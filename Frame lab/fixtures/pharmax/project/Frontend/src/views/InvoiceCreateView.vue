<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { invoicesService } from '../services/invoices'
import { productsService } from '../services/products'
import { useAuthStore } from '../stores/auth'
import { useSettingsStore } from '../stores/settings'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const auth = useAuthStore()
const settingsStore = useSettingsStore()
const toast = useToast()

const DRAFT_STORAGE_KEY = computed(() => `pharmax.invoice.drafts.${auth.user?.id || 'guest'}`)

// State
const products = ref([])
const productUnits = ref({})
const loading = ref(true)
const saving = ref(false)
const searchSectionRef = ref(null)
const searchInputRef = ref(null)
const DAILY_INVOICE_CUTOFF_HOUR = 22
const reconciliationStatus = ref(null)
let reconciliationStatusTimer = null

// Returned invoices (sent back by cashier for correction)
const RETURNED_NOTE_PREFIX = '[RETURNED_TO_SENDER]'
const returnedInvoices = ref([])

// Multi-invoice workspace
const invoiceTabs = ref([])
const activeTabIndex = ref(0)

function buildEmptyInvoiceTab(index = invoiceTabs.value.length + 1) {
  return {
    id: Date.now().toString(),
    name: `Invoice #${index}`,
    items: [],
    customerName: '',
    notes: '',
    invoiceDate: new Date().toISOString().slice(0, 10),
    searchQuery: '',
    showSearchResults: false,
    selectedProducts: new Set(),
  }
}

// Initialize with one invoice tab
function createNewInvoiceTab() {
  const newTab = buildEmptyInvoiceTab()
  invoiceTabs.value.push(newTab)
  activeTabIndex.value = invoiceTabs.value.length - 1
}

function serializeInvoiceTab(tab) {
  return {
    id: tab.id,
    name: tab.name,
    items: Array.isArray(tab.items) ? tab.items : [],
    customerName: tab.customerName || '',
    notes: tab.notes || '',
    invoiceDate: tab.invoiceDate || new Date().toISOString().slice(0, 10),
    searchQuery: tab.searchQuery || '',
    showSearchResults: false,
    selectedProducts: Array.from(tab.selectedProducts || []),
  }
}

function serializeDrafts() {
  return {
    activeTabIndex: activeTabIndex.value,
    invoiceTabs: invoiceTabs.value.map(serializeInvoiceTab),
  }
}

function saveDraftsToStorage() {
  if (!settingsStore.settings.workflow.invoice_draft_autosave) return
  if (typeof window === 'undefined') return

  const safePayload = serializeDrafts()
  window.localStorage.setItem(DRAFT_STORAGE_KEY.value, JSON.stringify(safePayload))
}

function restoreDraftsFromStorage() {
  if (typeof window === 'undefined') return false
  try {
    const raw = window.localStorage.getItem(DRAFT_STORAGE_KEY.value)
    if (!raw) return false
    const parsed = JSON.parse(raw)
    if (!parsed || !Array.isArray(parsed.invoiceTabs) || parsed.invoiceTabs.length === 0) return false

    invoiceTabs.value = parsed.invoiceTabs.map((tab, idx) => ({
      id: tab.id || `${Date.now()}-${idx}`,
      name: tab.name || `Invoice #${idx + 1}`,
      items: Array.isArray(tab.items) ? tab.items : [],
      customerName: tab.customerName || '',
      notes: tab.notes || '',
      invoiceDate: tab.invoiceDate || new Date().toISOString().slice(0, 10),
      searchQuery: tab.searchQuery || '',
      showSearchResults: false,
      selectedProducts: new Set(Array.isArray(tab.selectedProducts) ? tab.selectedProducts : []),
    }))

    const nextIndex = Number(parsed.activeTabIndex)
    activeTabIndex.value = Number.isInteger(nextIndex) && nextIndex >= 0 && nextIndex < invoiceTabs.value.length
      ? nextIndex
      : 0

    return true
  } catch {
    return false
  }
}

// Close invoice tab
function closeTab(index) {
  if (invoiceTabs.value.length === 1) {
    // Don't close the last tab, just clear it
    invoiceTabs.value[0] = buildEmptyInvoiceTab(1)
    return
  }
  
  invoiceTabs.value.splice(index, 1)
  if (activeTabIndex.value >= invoiceTabs.value.length) {
    activeTabIndex.value = invoiceTabs.value.length - 1
  }
}

// Current active invoice (computed)
const currentInvoice = computed(() => invoiceTabs.value[activeTabIndex.value])

// Aliases for backward compatibility
const invoiceItems = computed({
  get: () => currentInvoice.value?.items || [],
  set: (val) => { if (currentInvoice.value) currentInvoice.value.items = val }
})
const customerName = computed({
  get: () => currentInvoice.value?.customerName || '',
  set: (val) => { if (currentInvoice.value) currentInvoice.value.customerName = val }
})
const notes = computed({
  get: () => currentInvoice.value?.notes || '',
  set: (val) => { if (currentInvoice.value) currentInvoice.value.notes = val }
})
const invoiceDate = computed({
  get: () => currentInvoice.value?.invoiceDate || new Date().toISOString().slice(0, 10),
  set: (val) => { if (currentInvoice.value) currentInvoice.value.invoiceDate = val }
})
const searchQuery = computed({
  get: () => currentInvoice.value?.searchQuery || '',
  set: (val) => { if (currentInvoice.value) currentInvoice.value.searchQuery = val }
})
const showSearchResults = computed({
  get: () => currentInvoice.value?.showSearchResults || false,
  set: (val) => { if (currentInvoice.value) currentInvoice.value.showSearchResults = val }
})
const selectedProducts = computed({
  get: () => currentInvoice.value?.selectedProducts || new Set(),
  set: (val) => { if (currentInvoice.value) currentInvoice.value.selectedProducts = val }
})
const canEditUnitPrice = computed(() => auth.user?.role === 'ADMIN')

function isAfterInvoiceCutoff() {
  return new Date().getHours() >= DAILY_INVOICE_CUTOFF_HOUR
}

function formatStatusTime(value) {
  if (!value) return '10:00 PM'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '10:00 PM'
  return date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
}

async function loadReconciliationStatus() {
  try {
    reconciliationStatus.value = await invoicesService.getReconciliationStatus()
  } catch {
    reconciliationStatus.value = null
  }
}

async function loadReturnedInvoices() {
  try {
    const allDrafts = await invoicesService.list({ status: 'DRAFT', limit: 50 })
    const myId = auth.user?.id
    returnedInvoices.value = (allDrafts || []).filter(inv => {
      const isReturned = inv.cashier_note?.startsWith(RETURNED_NOTE_PREFIX)
      const isMine = inv.user_id === myId || inv.sold_by_id === myId
      return isReturned && isMine
    })
  } catch (err) {
    console.error('Failed to load returned invoices:', err)
    returnedInvoices.value = []
  }
}

// Load a returned invoice into the workspace for editing
async function loadReturnedInvoice(invoice) {
  try {
    // Fetch full invoice with items
    const full = await invoicesService.get(invoice.id)
    if (!full || !full.items?.length) {
      toast.error('Could not load invoice items')
      return
    }
    
    // Extract return reason from cashier_note
    const returnReason = (full.cashier_note || '').replace(RETURNED_NOTE_PREFIX, '').trim()
    
    // Build items array matching our workspace format
    const items = []
    for (const item of full.items) {
      const units = await loadUnits(item.product?.id)
      items.push({
        product_id: item.product?.id,
        product_name: item.product?.name || 'Unknown',
        product_brand: '',
        quantity: item.quantity,
        unit_id: item.product_unit?.id || null,
        unit_name: item.product_unit?.name || 'Unit',
        price: item.unit_price,
        units: units,
        stock: 0,
      })
    }
    
    // Create new tab with the returned invoice data
    const newTab = {
      id: invoice.id,
      name: `RETURNED`,
      items,
      customerName: full.customer_name || '',
      notes: returnReason ? `Returned: ${returnReason}` : '',
      invoiceDate: full.invoice_date?.slice(0, 10) || new Date().toISOString().slice(0, 10),
      searchQuery: '',
      showSearchResults: false,
      selectedProducts: new Set(),
      isReturned: true,
      originalInvoiceId: invoice.id,
    }
    
    invoiceTabs.value.push(newTab)
    activeTabIndex.value = invoiceTabs.value.length - 1
    
    // Remove from returned list
    returnedInvoices.value = returnedInvoices.value.filter(inv => inv.id !== invoice.id)
    
    toast.success('Invoice loaded for editing')
  } catch (err) {
    console.error('Failed to load returned invoice:', err)
    toast.error('Failed to load invoice')
  }
}

const invoiceCreationBlocked = computed(() => {
  if (canEditUnitPrice.value) return false
  if (reconciliationStatus.value) {
    return !Boolean(reconciliationStatus.value.can_process_invoices_now)
  }
  return isAfterInvoiceCutoff()
})

const afterHoursWarning = computed(() => {
  if (!invoiceCreationBlocked.value) {
    if (
      reconciliationStatus.value?.has_after_hours_permission &&
      reconciliationStatus.value?.permission_expires_at
    ) {
      return `Temporary after-hours access is active until ${formatStatusTime(reconciliationStatus.value.permission_expires_at)}.`
    }
    return ''
  }

  const lockTime = formatStatusTime(reconciliationStatus.value?.lock_start_at)
  return `Invoice creation is closed after ${lockTime} for cashier and staff users. Ask an admin to grant temporary access.`
})

// Load products on mount
onMounted(async () => {
  document.addEventListener('pointerdown', handleDocumentPointerDown)
  document.addEventListener('keydown', handleGlobalShortcut)
  await loadReconciliationStatus()
  await loadReturnedInvoices()
  reconciliationStatusTimer = window.setInterval(() => {
    loadReconciliationStatus()
  }, 60_000)

  // Restore invoice drafts or initialize a new tab
  if (!restoreDraftsFromStorage()) {
    createNewInvoiceTab()
  }

  try {
    const allProducts = await productsService.listAll({
      batchSize: 500,
      maxRecords: 5000,
      offset: 0,
    })
    products.value = Array.isArray(allProducts) ? allProducts : []
  } catch (err) {
    console.error('Failed to load full product list:', err)
    try {
      const fallbackProducts = await productsService.list({ limit: 500, offset: 0 })
      products.value = Array.isArray(fallbackProducts) ? fallbackProducts : []
    } catch (fallbackErr) {
      console.error('Fallback product load also failed:', fallbackErr)
      products.value = []
      toast.error('Could not load products for invoice search. Please refresh.')
    }
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  saveDraftsToStorage()
  document.removeEventListener('pointerdown', handleDocumentPointerDown)
  document.removeEventListener('keydown', handleGlobalShortcut)
  if (reconciliationStatusTimer) {
    window.clearInterval(reconciliationStatusTimer)
    reconciliationStatusTimer = null
  }
})

watch(
  [invoiceTabs, activeTabIndex],
  () => {
    saveDraftsToStorage()
  },
  { deep: true },
)

watch(
  () => settingsStore.settings.workflow.invoice_draft_autosave,
  (enabled) => {
    if (enabled) {
      saveDraftsToStorage()
      return
    }
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem(DRAFT_STORAGE_KEY.value)
    }
  },
)

function handleDocumentPointerDown(event) {
  if (!searchSectionRef.value) return
  if (!searchSectionRef.value.contains(event.target)) {
    showSearchResults.value = false
    selectedProducts.value = new Set()
  }
}

function handleGlobalShortcut(event) {
  if (event.key === 'F2') {
    event.preventDefault()
    focusSearchInput()
  }
  // Ctrl+Enter or Cmd+Enter to send to cashier
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    event.preventDefault()
    sendToCashier()
  }
}

function focusSearchInput() {
  showSearchResults.value = true
  nextTick(() => searchInputRef.value?.focus())
}

// Filter products by search
const filteredProducts = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return []
  const tokens = query.split(/\s+/).filter(Boolean)
  return products.value
    .filter((p) => {
      const haystack = [
        p.name || '',
        p.brand_name || '',
        p.sku || '',
        p.generic_name || '',
      ]
        .join(' ')
        .toLowerCase()
      return tokens.every((token) => haystack.includes(token))
    })
    .filter(p => p.quantity_on_hand > 0)
    .slice(0, settingsStore.settings.workflow.quick_add_max_results || 10)
})

function handleSearchKeydown(event) {
  if (event.key === 'Enter' && filteredProducts.value.length > 0) {
    event.preventDefault()
    addProduct(filteredProducts.value[0])
  }
}

// Get units for a product
async function loadUnits(productId) {
  if (productUnits.value[productId]) return productUnits.value[productId]
  try {
    const units = await productsService.getUnits(productId)
    productUnits.value[productId] = units
    return units
  } catch {
    return []
  }
}

// Toggle product selection for multi-add
function toggleProductSelection(productId) {
  if (selectedProducts.value.has(productId)) {
    selectedProducts.value.delete(productId)
  } else {
    selectedProducts.value.add(productId)
  }
}

// Add single product to invoice
async function addProduct(product, closeDropdown = true) {
  const units = await loadUnits(product.id)
  const defaultUnit = units.find(u => u.is_default) || units[0]
  
  // Check if already in list - if so, increase quantity
  const existing = invoiceItems.value.find(i => i.product_id === product.id)
  if (existing) {
    existing.quantity += 1
    // Close dropdown when selecting existing product
    if (closeDropdown) {
      searchQuery.value = ''
      showSearchResults.value = false
    }
    return
  }

  // Get price from unit (price_per_unit) or fallback to product selling_price
  const unitPrice = defaultUnit?.price_per_unit || product.selling_price || 0

  invoiceItems.value.push({
    product_id: product.id,
    product_name: product.name,
    product_brand: product.brand_name,
    quantity: 1,
    unit_id: defaultUnit?.id || null,
    unit_name: defaultUnit?.name || 'Unit',
    price: unitPrice,
    units: units,
    stock: product.quantity_on_hand,
  })
  
  // Close dropdown after adding
  if (closeDropdown) {
    searchQuery.value = ''
    showSearchResults.value = false
  }
}

// Add all selected products at once
async function addSelectedProducts() {
  for (const productId of selectedProducts.value) {
    const product = products.value.find(p => p.id === productId)
    if (product) {
      await addProduct(product, false)
    }
  }
  selectedProducts.value.clear()
  searchQuery.value = ''
  showSearchResults.value = false
}

// Update item quantity
function updateQuantity(item, delta) {
  item.quantity = Math.max(1, item.quantity + delta)
}

// Change unit for item
function changeUnit(item, unitId) {
  const unit = item.units.find(u => u.id === unitId)
  if (unit) {
    item.unit_id = unit.id
    item.unit_name = unit.name
    item.price = unit.price_per_unit
  }
}

// Remove item
function removeItem(index) {
  invoiceItems.value.splice(index, 1)
}

// Calculate totals
const subtotal = computed(() => 
  invoiceItems.value.reduce((sum, item) => sum + (item.price * item.quantity), 0)
)

const itemCount = computed(() => invoiceItems.value.length)

// Format currency
function fmt(n) {
  return `₦${n.toLocaleString('en-NG', { minimumFractionDigits: 2 })}`
}

// Create invoice and send to cashier
async function sendToCashier() {
  await loadReconciliationStatus()

  if (invoiceCreationBlocked.value) {
    toast.error(afterHoursWarning.value)
    return
  }

  if (invoiceItems.value.length === 0) {
    toast.warning('Add at least one item to the invoice.')
    return
  }

  const sentTabId = currentInvoice.value?.id
  const isReturned = currentInvoice.value?.isReturned
  const originalId = currentInvoice.value?.originalInvoiceId
  
  saving.value = true
  try {
    let invoice
    
    if (isReturned && originalId) {
      // Returned invoice: just clear the RETURNED marker to put it back in queue
      await invoicesService.updateCashierNote(originalId, '')
      invoice = { id: originalId }
      toast.success('Invoice sent back to cashier queue.')
    } else {
      // New invoice: create and add items
      const cashierNote = String(notes.value || '').trim()
      invoice = await invoicesService.create({ cashier_note: cashierNote || null })
      
      for (const item of invoiceItems.value) {
        await invoicesService.addItem(invoice.id, {
          product_id: item.product_id,
          quantity: item.quantity,
          product_unit_id: item.unit_id,
          unit_price: item.price,
        })
      }
      
      const pickupCode = invoice.id.slice(0, 8).toUpperCase()
      toast.success(`Invoice sent to cashier queue. Pickup code: ${pickupCode}`)
    }
    
    clearSentInvoiceDraft(sentTabId)

    if (auth.user?.role === 'ADMIN' || auth.user?.role === 'CASHIER') {
      router.push({
        path: '/cashier',
        query: {
          open: invoice.id,
          source: 'invoice-create',
        },
      })
    } else {
      router.push('/invoices')
    }
  } catch (err) {
    console.error('Invoice creation error:', err)
    let errorMsg = 'Unknown error'
    if (typeof err === 'string') {
      errorMsg = err
    } else if (err?.message) {
      errorMsg = err.message
    } else if (err?.body?.detail) {
      errorMsg = err.body.detail
    } else if (err?.detail) {
      errorMsg = err.detail
    }
    if (errorMsg.toLowerCase().includes('after-hours') || errorMsg.toLowerCase().includes('daily sales are closed')) {
      await loadReconciliationStatus()
    }
    toast.error('Failed to create invoice: ' + errorMsg)
  } finally {
    saving.value = false
  }
}

// Update price directly
function updatePrice(item, newPrice) {
  if (!canEditUnitPrice.value) return
  item.price = Math.max(0, parseFloat(newPrice) || 0)
}

function clearSentInvoiceDraft(sentTabId) {
  if (invoiceTabs.value.length <= 1) {
    invoiceTabs.value = [buildEmptyInvoiceTab(1)]
    activeTabIndex.value = 0
    return
  }

  const sentTabIndex = invoiceTabs.value.findIndex((tab) => tab.id === sentTabId)
  const indexToRemove = sentTabIndex >= 0 ? sentTabIndex : activeTabIndex.value

  invoiceTabs.value.splice(indexToRemove, 1)

  if (invoiceTabs.value.length === 0) {
    invoiceTabs.value = [buildEmptyInvoiceTab(1)]
    activeTabIndex.value = 0
    return
  }

  if (activeTabIndex.value >= invoiceTabs.value.length) {
    activeTabIndex.value = invoiceTabs.value.length - 1
  }
}

// Cancel and go back
function cancel() {
  router.push('/invoices')
}
</script>

<template>
  <div class="create-invoice">
    <!-- Header -->
    <header class="page-actions">
      <button class="btn-secondary" @click="cancel">
        <span class="material-icons">arrow_back</span>
        Back to Invoices
      </button>
      <button class="btn-primary btn-focus-search" @click="focusSearchInput">
        <span class="material-icons">search</span>
        Quick Add (F2)
      </button>
    </header>

    <!-- Returned Invoices Alert -->
    <div v-if="returnedInvoices.length > 0" class="returned-alert">
      <span class="material-icons alert-icon">undo</span>
      <div class="returned-content">
        <strong>{{ returnedInvoices.length }} invoice{{ returnedInvoices.length > 1 ? 's' : '' }} sent back</strong>
        <div class="returned-list">
          <div v-for="inv in returnedInvoices" :key="inv.id" class="returned-item">
            <span class="returned-info">
              {{ inv.cashier_note?.replace('[RETURNED_TO_SENDER]', '').trim() || 'Needs correction' }}
            </span>
            <button class="btn-load-returned" @click="loadReturnedInvoice(inv)">
              Load &amp; Edit
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Invoice Tabs -->
    <div class="invoice-tabs">
      <div class="tabs-list">
        <button
          v-for="(tab, index) in invoiceTabs"
          :key="tab.id"
          class="tab-item"
          :class="{ active: index === activeTabIndex, returned: tab.isReturned }"
          @click="activeTabIndex = index"
        >
          <span v-if="tab.isReturned" class="tab-returned-badge">RETURNED</span>
          <span class="tab-name">{{ tab.isReturned ? 'Edit Invoice' : `Invoice #${index + 1}` }}</span>
          <span v-if="tab.items.length > 0 && invoiceTabs.length > 1" class="tab-count">{{ tab.items.length }}</span>
          <button 
            v-if="invoiceTabs.length > 1"
            class="tab-close"
            @click.stop="closeTab(index)"
            title="Close tab"
          >
            <span class="material-icons">close</span>
          </button>
        </button>
        <button class="tab-new" @click="createNewInvoiceTab" title="New Invoice">
          <span class="material-icons">add</span>
          New Invoice
        </button>
      </div>
    </div>

    <!-- Invoice Form -->
    <div class="invoice-form">
      <section class="invoice-document" :class="{ compact: invoiceItems.length <= 3 }">
        <!-- Invoice Header -->
        <div class="invoice-header">
          <div class="invoice-brand">
            <span class="material-icons">local_pharmacy</span>
            <div>
              <h3>Pharmax</h3>
              <p>Sales Invoice</p>
            </div>
          </div>
          <div class="invoice-meta">
            <div class="meta-field">
              <label>Date</label>
              <input type="date" v-model="invoiceDate" />
            </div>
            <div class="meta-field">
              <label>Staff</label>
              <input type="text" :value="auth.user?.full_name || auth.user?.username" readonly />
            </div>
            <div class="meta-field">
              <label>Customer (Optional)</label>
              <input type="text" v-model="customerName" placeholder="Walk-in" />
            </div>
            <div class="meta-field notes-field">
              <label>Message for Cashier</label>
              <textarea v-model="notes" rows="2" placeholder="Add handling instruction, insurance note, or pickup hint"></textarea>
            </div>
          </div>
        </div>

        <!-- Product Search -->
        <div ref="searchSectionRef" class="search-section">
          <div class="search-box">
            <span class="material-icons">search</span>
            <input 
              ref="searchInputRef"
              v-model="searchQuery"
              type="text"
              placeholder="Search products by name, brand, or SKU... (F2)"
              @focus="showSearchResults = true"
              @keydown="handleSearchKeydown"
            />
          </div>
          
          <!-- Search Results Dropdown -->
          <div v-if="showSearchResults && filteredProducts.length > 0" class="search-results">
            <div class="search-results-header">
              <span>{{ filteredProducts.length }} products found</span>
              <button 
                v-if="selectedProducts.size > 0" 
                class="btn-add-selected"
                @click="addSelectedProducts"
              >
                Add Selected ({{ selectedProducts.size }})
              </button>
            </div>
            <div class="search-results-list">
              <div
                v-for="product in filteredProducts"
                :key="product.id"
                class="search-result-item"
                :class="{ selected: selectedProducts.has(product.id) }"
              >
                <label class="result-checkbox">
                  <input 
                    type="checkbox"
                    :checked="selectedProducts.has(product.id)"
                    @change="toggleProductSelection(product.id)"
                    @click.stop
                  />
                  <span class="checkbox-custom"></span>
                </label>
                <button class="result-content" @click="addProduct(product)">
                  <div class="result-main">
                    <span class="result-name">{{ product.name }}</span>
                    <span v-if="product.brand_name" class="result-brand">{{ product.brand_name }}</span>
                  </div>
                  <div class="result-meta">
                    <span class="result-price">{{ fmt(product.selling_price || 0) }}</span>
                    <span class="result-stock">{{ product.quantity_on_hand }} in stock</span>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Items Table -->
        <div class="invoice-items" :class="{ dense: invoiceItems.length > 4 }">
            <table v-if="invoiceItems.length > 0">
              <thead>
                <tr>
                  <th class="col-product">Product</th>
                  <th class="col-unit">Unit</th>
                  <th class="col-qty">Qty</th>
                  <th class="col-price">Price</th>
                  <th class="col-total">Total</th>
                  <th class="col-action"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, idx) in invoiceItems" :key="item.product_id">
                  <td class="col-product">
                    <span class="item-name">{{ item.product_name }}</span>
                    <span class="item-brand">{{ item.product_brand }}</span>
                  </td>
                  <td class="col-unit">
                    <select 
                      :value="item.unit_id" 
                      @change="changeUnit(item, $event.target.value)"
                    >
                      <option v-for="u in item.units" :key="u.id" :value="u.id">
                        {{ u.name }}
                      </option>
                    </select>
                  </td>
                  <td class="col-qty">
                    <div class="qty-control">
                      <button @click="updateQuantity(item, -1)">−</button>
                      <input 
                        type="number" 
                        :value="item.quantity"
                        @input="updateQuantity(item, Number($event.target.value) - item.quantity)"
                        @blur="item.quantity < 1 ? updateQuantity(item, 1 - item.quantity) : null"
                        min="1"
                        step="1"
                        class="qty-input"
                      />
                      <button @click="updateQuantity(item, 1)">+</button>
                    </div>
                  </td>
                  <td class="col-price">
                    <input 
                      type="number" 
                      :value="item.price" 
                      @input="updatePrice(item, $event.target.value)"
                      :readonly="!canEditUnitPrice"
                      :disabled="!canEditUnitPrice"
                      min="0"
                      step="10"
                      class="price-input"
                    />
                  </td>
                  <td class="col-total mono">{{ fmt(item.price * item.quantity) }}</td>
                  <td class="col-action">
                    <button class="remove-btn" @click="removeItem(idx)">
                      <span class="material-icons">close</span>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>

            <div v-else class="empty-invoice">
              <span class="material-icons">receipt_long</span>
              <p>No items added yet</p>
              <p class="hint">Search and click products to add them</p>
            </div>
          </div>

        <!-- Invoice Footer / Totals -->
        <div class="invoice-footer">
          <div class="checkout-panel">
            <p v-if="afterHoursWarning" class="after-hours-warning">
              {{ afterHoursWarning }}
            </p>

            <div class="totals-section">
              <div class="total-row">
                <span>Subtotal ({{ itemCount }} items)</span>
                <span class="mono">{{ fmt(subtotal) }}</span>
              </div>
              <div class="total-row grand">
                <span>Total</span>
                <span class="mono">{{ fmt(subtotal) }}</span>
              </div>
            </div>

            <button 
              class="btn-checkout" 
              :disabled="saving || invoiceItems.length === 0 || invoiceCreationBlocked" 
              @click="sendToCashier"
              title="Send invoice to cashier queue (Ctrl+Enter)"
            >
              <span class="material-icons">{{ saving ? 'hourglass_empty' : 'send' }}</span>
              {{ saving ? 'Sending...' : 'Send to Cashier' }}
              <span class="shortcut-hint">Ctrl+Enter</span>
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
/* ═══════════════════════════════════════════════════════════════════════════
   INVOICE CREATE VIEW — Clean, professional invoice builder
   ═══════════════════════════════════════════════════════════════════════════ */

.create-invoice {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  min-height: 0;
}

/* ─── Page Actions ─────────────────────────────────────────────────────────── */
.page-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--space-2);
  margin-bottom: var(--space-4);
  gap: var(--space-4);
}

/* ─── Returned Invoices Alert ─────────────────────────────────────────────── */
.returned-alert {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-3);
}

.returned-alert .alert-icon {
  font-size: 24px;
  color: var(--warning, #f59e0b);
  align-self: flex-start;
  margin-top: 2px;
}

.returned-content {
  flex: 1;
}

.returned-content strong {
  display: block;
  color: var(--text-primary);
  font-size: 14px;
  margin-bottom: var(--space-2);
}

.returned-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.returned-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  background: rgba(255, 255, 255, 0.5);
  border-radius: var(--radius-sm);
}

.returned-info {
  font-size: 13px;
  color: var(--text-secondary);
}

.btn-load-returned {
  padding: 6px 12px;
  border: none;
  background: var(--warning, #f59e0b);
  color: white;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-load-returned:hover {
  background: #d97706;
}

/* ─── Invoice Tabs ─────────────────────────────────────────────────────────── */
.invoice-tabs {
  margin-bottom: var(--space-3);
}

.tabs-list {
  display: flex;
  gap: var(--space-2);
  border-bottom: 1px solid var(--border-default);
  overflow-x: auto;
  scrollbar-width: thin;
  padding-bottom: var(--space-1);
}

.tab-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border: none;
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.tab-item:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.tab-item.active {
  color: var(--primary);
  border-color: rgba(15, 159, 137, 0.3);
  background: linear-gradient(90deg, var(--primary-bg) 0%, var(--primary-tint) 100%);
  box-shadow: var(--shadow-xs);
}

.tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: var(--radius-full);
  background: var(--primary);
  color: white;
  font-size: 11px;
  font-weight: 600;
}

.tab-item.returned {
  border-color: rgba(245, 158, 11, 0.4);
  background: rgba(245, 158, 11, 0.1);
}

.tab-item.returned.active {
  background: rgba(245, 158, 11, 0.15);
  border-color: rgba(245, 158, 11, 0.5);
}

.tab-returned-badge {
  display: inline-block;
  padding: 2px 6px;
  background: var(--warning, #f59e0b);
  color: white;
  font-size: 10px;
  font-weight: 600;
  border-radius: var(--radius-sm);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tab-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  padding: 0;
}

.tab-close:hover {
  background: var(--error-bg);
  color: var(--error);
}

.tab-close .material-icons {
  font-size: 16px;
}

.tab-new {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border: 1px dashed var(--border-strong);
  background: transparent;
  border-radius: var(--radius-md);
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-left: var(--space-2);
  margin-bottom: var(--space-2);
}

.tab-new:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: var(--primary-bg);
}

.tab-new .material-icons {
  font-size: 18px;
}

.btn-secondary, .btn-primary {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  height: 40px;
  padding: 0 var(--space-4);
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-secondary {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  color: var(--text-secondary);
}

.btn-secondary:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.btn-primary {
  background: var(--primary);
  border: 1px solid var(--primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary .material-icons,
.btn-primary .material-icons {
  font-size: 18px;
}

/* ─── Invoice Form ─────────────────────────────────────────────────────────── */
.invoice-form {
  flex: 1;
  min-height: min(620px, calc(100vh - 230px));
}

.invoice-document {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  display: flex;
  flex-direction: column;
  min-height: 0;
  height: 100%;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.invoice-document.compact {
  height: auto;
}

.invoice-document.compact .invoice-header {
  padding: var(--space-4) var(--space-6);
}

.invoice-document.compact .search-section {
  padding-top: var(--space-2);
  padding-bottom: var(--space-2);
}

/* ─── Invoice Header ───────────────────────────────────────────────────────── */
.invoice-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--space-5) var(--space-6);
  background: linear-gradient(145deg, #0f9f89 0%, #0b8572 54%, #08685b 100%);
  color: white;
  box-shadow: inset 0 -1px 0 rgba(255,255,255,0.14);
}

.invoice-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.invoice-brand .material-icons {
  font-size: 32px;
}

.invoice-brand h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
}

.invoice-brand p {
  margin: 2px 0 0;
  font-size: 12px;
  opacity: 0.9;
}

.invoice-meta {
  display: flex;
  gap: var(--space-4);
}

.meta-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-field label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  opacity: 0.8;
}

.meta-field input {
  height: 32px;
  padding: 0 var(--space-2);
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: var(--radius-sm);
  background: rgba(255,255,255,0.1);
  color: white;
  font-size: 13px;
  font-weight: 500;
}

.meta-field input:read-only {
  background: rgba(255,255,255,0.05);
  cursor: not-allowed;
}

.meta-field input::placeholder {
  color: rgba(255,255,255,0.6);
}

.meta-field textarea {
  min-height: 56px;
  padding: 8px var(--space-2);
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: var(--radius-sm);
  background: rgba(255,255,255,0.1);
  color: white;
  font-size: 12px;
  resize: vertical;
}

.meta-field textarea::placeholder {
  color: rgba(255,255,255,0.6);
}

.notes-field {
  min-width: 260px;
}

/* ─── Search Section ───────────────────────────────────────────────────────── */
.search-section {
  padding: var(--space-3) var(--space-6);
  position: relative;
  background: linear-gradient(180deg, rgba(15, 159, 137, 0.05) 0%, transparent 100%);
}

.search-box {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  height: 48px;
  padding: 0 var(--space-4);
  background: var(--primary-bg);
  border: 1px solid rgba(15, 159, 137, 0.42);
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-xs);
}

.search-box:focus-within {
  background: var(--bg-elevated);
  border-color: var(--primary-hover);
  box-shadow: 0 0 0 3px var(--primary-tint);
}

.search-box .material-icons {
  color: var(--primary);
  font-size: 22px;
}

.search-box input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 15px;
  color: var(--text-primary);
  outline: none;
}

.search-box input::placeholder {
  color: var(--text-muted);
}

/* ─── Search Results Dropdown ──────────────────────────────────────────────── */
.search-results {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  max-height: 450px;
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  z-index: 100;
  overflow: hidden;
}

.search-results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  background: var(--bg-elevated);
  border-bottom: 1px solid var(--border-default);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}

.btn-add-selected {
  padding: 6px 12px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--primary);
  color: white;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.btn-add-selected:hover {
  background: var(--primary-hover);
}

.search-results-list {
  max-height: 370px;
  overflow-y: auto;
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
  transition: background var(--transition-fast);
}

.search-result-item:last-child {
  border-bottom: none;
}

.search-result-item.selected {
  background: var(--primary-bg);
}

.search-result-item:hover {
  background: var(--bg-hover);
}

.result-checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
  position: relative;
}

.result-checkbox input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.checkbox-custom {
  width: 18px;
  height: 18px;
  border: 2px solid var(--border-default);
  border-radius: var(--radius-sm);
  background: var(--bg-elevated);
  display: grid;
  place-items: center;
  transition: all var(--transition-fast);
}

.result-checkbox input:checked + .checkbox-custom {
  background: var(--primary);
  border-color: var(--primary);
}

.result-checkbox input:checked + .checkbox-custom::after {
  content: '✓';
  color: white;
  font-size: 12px;
  font-weight: 700;
}

.result-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: none;
  background: transparent;
  text-align: left;
  cursor: pointer;
  padding: 0;
}

.result-main {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.result-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.result-brand {
  font-size: 12px;
  color: var(--text-muted);
}

.result-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.result-price {
  font-family: var(--font-data);
  font-size: 14px;
  font-weight: 600;
  color: var(--primary);
}

.result-stock {
  font-size: 11px;
  color: var(--text-muted);
}

.product-stock {
  font-size: 11px;
  color: var(--text-muted);
}

.product-stock.warning {
  color: var(--warning);
}

.loading-state {
  padding: var(--space-8);
  text-align: center;
  color: var(--text-muted);
}

/* ─── Invoice Items Table ──────────────────────────────────────────────────── */
.invoice-items {
  flex: 1;
  padding: 0;
  overflow-y: auto;
  min-height: 220px;
}

.invoice-document.compact .invoice-items {
  flex: 0 0 auto;
  min-height: 120px;
  max-height: 280px;
}

.invoice-items.dense th {
  padding: var(--space-2) var(--space-3);
}

.invoice-items.dense td {
  padding: var(--space-2) var(--space-3);
}

.invoice-items table {
  width: 100%;
  border-collapse: collapse;
}

.invoice-items thead {
  background: var(--table-header-bg);
  position: sticky;
  top: 0;
  z-index: 1;
}

.invoice-items th {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-default);
}

.invoice-items td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
  vertical-align: middle;
}

.invoice-items tr:last-child td {
  border-bottom: none;
}

.invoice-items tbody tr:hover td {
  background: var(--table-row-hover);
}

.col-product { min-width: 200px; }
.col-unit { width: 140px; }
.col-qty { width: 120px; }
.col-price { width: 120px; text-align: right; }
.col-total { width: 120px; text-align: right; }
.col-action { width: 60px; text-align: center; }

.item-name {
  display: block;
  font-weight: 500;
  color: var(--text-primary);
}

.item-brand {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.col-unit select {
  width: 100%;
  height: 32px;
  padding: 0 var(--space-2);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  background: var(--bg-elevated);
  color: var(--text-primary);
  font-size: 13px;
  cursor: pointer;
}

.price-input {
  width: 100%;
  height: 32px;
  padding: 0 var(--space-2);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  background: var(--bg-elevated);
  color: var(--text-primary);
  font-family: var(--font-data);
  font-size: 13px;
  text-align: right;
  transition: all var(--transition-fast);
}

.price-input:focus {
  outline: none;
  border-color: var(--primary);
  background: var(--bg-card);
}

.price-input::-webkit-inner-spin-button,
.price-input::-webkit-outer-spin-button {
  opacity: 1;
}

.price-input:disabled {
  opacity: 0.8;
  cursor: not-allowed;
  background: var(--bg-muted);
  color: var(--text-secondary);
}

.qty-control {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.qty-control button {
  width: 28px;
  height: 28px;
  border: none;
  background: var(--bg-recessed);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
}

.qty-control button:hover {
  background: var(--bg-hover);
}

.qty-control span {
  width: 36px;
  text-align: center;
  font-size: 14px;
  font-weight: 500;
}

.qty-control .qty-input {
  width: 50px;
  text-align: center;
  font-size: 14px;
  font-weight: 500;
  border: none;
  background: var(--bg-default);
  padding: 4px 2px;
  -moz-appearance: textfield;
}

.qty-control .qty-input::-webkit-outer-spin-button,
.qty-control .qty-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.invoice-items.dense .qty-control button {
  width: 24px;
  height: 24px;
}

.invoice-items.dense .qty-control span {
  width: 30px;
  font-size: 13px;
}

.mono {
  font-family: var(--font-data);
}

.remove-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: var(--radius-sm);
  display: grid;
  place-items: center;
}

.remove-btn:hover {
  background: var(--error-bg);
  color: var(--error);
}

.remove-btn .material-icons {
  font-size: 16px;
}

.empty-invoice {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
  color: var(--text-muted);
}

.empty-invoice .material-icons {
  font-size: 48px;
  margin-bottom: var(--space-3);
  opacity: 0.4;
}

.empty-invoice p {
  margin: 0;
  font-size: 14px;
}

.empty-invoice .hint {
  font-size: 12px;
  margin-top: var(--space-1);
}

.invoice-document.compact .empty-invoice {
  padding: var(--space-5);
}

.invoice-document.compact .total-row.grand {
  font-size: 18px;
  padding-top: var(--space-2);
}

/* ─── Invoice Footer - Checkout Style ──────────────────────────────────────── */
.invoice-footer {
  border-top: 2px solid var(--border-subtle);
  padding: var(--space-4) var(--space-5);
  background: var(--bg-recessed);
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  display: flex;
  justify-content: flex-end;
  align-items: flex-end;
  gap: var(--space-6);
}

.invoice-document.compact .invoice-footer {
  padding: var(--space-3) var(--space-5);
}

.checkout-panel {
  width: min(380px, 100%);
  margin-left: auto;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: var(--space-4);
}

.after-hours-warning {
  margin: 0;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--warning);
  background: var(--warning-bg);
  color: var(--warning);
  font-size: 12px;
  line-height: 1.4;
}

.invoice-document.compact .checkout-panel {
  gap: var(--space-3);
}

.totals-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  width: 100%;
}

.total-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: var(--text-secondary);
  padding: var(--space-2) 0;
}

.invoice-document.compact .total-row {
  font-size: 13px;
  padding: 4px 0;
}

.total-row.grand {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  padding-top: var(--space-3);
  border-top: 2px solid var(--border-default);
  margin-top: var(--space-1);
}

.btn-checkout {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: 14px var(--space-6);
  background: var(--primary);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-normal);
  box-shadow: 0 4px 12px var(--primary-tint);
  width: 100%;
  justify-content: center;
}

.invoice-document.compact .btn-checkout {
  padding: 12px var(--space-5);
}

.btn-checkout:hover:not(:disabled) {
  background: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px var(--primary-tint);
}

.btn-checkout:active:not(:disabled) {
  transform: translateY(0);
}

.btn-checkout:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-checkout .material-icons {
  font-size: 20px;
}

.shortcut-hint {
  margin-left: 8px;
  padding: 2px 6px;
  font-size: 11px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  opacity: 0.8;
}

/* ─── Responsive ───────────────────────────────────────────────────────────── */
@media (max-width: 1024px) {
  .invoice-items {
    min-height: 180px;
  }

  .invoice-footer {
    padding: var(--space-4);
  }

  .checkout-panel {
    width: 100%;
  }

  .shortcut-hint {
    display: none;
  }
}

@media (max-width: 768px) {
  .page-actions {
    flex-wrap: wrap;
  }

  .btn-secondary,
  .btn-primary {
    width: 100%;
    justify-content: center;
  }

  .invoice-header {
    flex-direction: column;
    gap: var(--space-4);
  }

  .invoice-meta {
    width: 100%;
    display: grid;
    grid-template-columns: 1fr;
    gap: var(--space-3);
  }
}
</style>
