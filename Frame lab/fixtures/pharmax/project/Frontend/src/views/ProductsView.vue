<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useProductsStore } from '../stores/products'
import { productsService } from '../services/products'
import { useCurrency } from '@/composables/useCurrency'
import { useConfirm } from '@/composables/useConfirm'
import { useAuthStore } from '../stores/auth'

const store = useProductsStore()
const auth = useAuthStore()
const { formatSimple, symbol: currencySymbol } = useCurrency()
const { confirm } = useConfirm()

const canDelete = computed(() => auth.userRole === 'ADMIN')

const THERAPEUTIC_CATEGORIES = [
  'Analgesic', 'Anti-malarial', 'Antibiotic', 'Anti-fungal',
  'Anti-inflammatory', 'Anti-diarrhoeal', 'Antacid', 'Antihistamine',
  'Antihypertensive', 'Anti-diabetic', 'Cough & Cold', 'Vitamin & Supplement',
  'Skin Care', 'Eye/Ear/Nose', 'Gastrointestinal', 'Contraceptive', 'Other',
]
const BASE_UNITS = ['Pack', 'Strip', 'Tablet', 'Capsule', 'Bottle', 'Sachet', 'Tube', 'Vial', 'Ampoule', 'Unit']
const PAGE_SIZES = [30, 50, 100]

// Modal state
const showAddModal = ref(false)
const showEditModal = ref(false)
const saving = ref(false)
const modalError = ref(null)
const selectedProductIds = ref(new Set())
const selectedProductLookup = ref(new Map())
const showBulkEditModal = ref(false)
const bulkSaving = ref(false)
const bulkError = ref(null)
const bulkQueue = ref([])
const bulkQueueIndex = ref(0)
const bulkForm = ref({
  name: '',
  generic_name: '',
  brand_name: '',
  supplier_name: '',
  therapeutic_category: '',
  product_type: 'Medical',
  reorder_level: 0,
  dispense_without_prescription: true,
  status: 'Active',
})

const ROW_INTERACTIVE_SELECTOR = 'button, input, select, textarea, a, [role="button"], [role="link"], [contenteditable="true"]'

const emptyForm = () => ({
  name: '', generic_name: '', brand_name: '', supplier_name: '',
  therapeutic_category: '', product_type: 'Medical', base_unit: 'Pack',
  price_per_unit: '', multiplier_to_base: 1, initial_quantity: 0,
  reorder_level: 0, dispense_without_prescription: true, status: 'Active',
})

const selectedProducts = computed(() => (
  Array.from(selectedProductIds.value)
    .map((productId) => selectedProductLookup.value.get(productId))
    .filter(Boolean)
))

watch(
  () => store.items,
  (items) => {
    if (!selectedProductIds.value.size) return
    const nextLookup = new Map(selectedProductLookup.value)
    items.forEach((item) => {
      if (selectedProductIds.value.has(item.id)) {
        nextLookup.set(item.id, { ...item })
      }
    })
    selectedProductLookup.value = nextLookup
  },
  { immediate: true, deep: true },
)

const bulkCurrentProduct = computed(() => bulkQueue.value[bulkQueueIndex.value] ?? null)
const bulkHasNext = computed(() => bulkQueueIndex.value < bulkQueue.value.length - 1)
const bulkProgressLabel = computed(() => {
  if (!bulkQueue.value.length) return '0 / 0'
  return `${bulkQueueIndex.value + 1} / ${bulkQueue.value.length}`
})

function clearProductSelection() {
  selectedProductIds.value = new Set()
  selectedProductLookup.value = new Map()
}

function toggleProductSelection(productId, product = null) {
  const nextIds = new Set(selectedProductIds.value)
  const nextLookup = new Map(selectedProductLookup.value)
  if (nextIds.has(productId)) {
    nextIds.delete(productId)
    nextLookup.delete(productId)
  } else {
    nextIds.add(productId)
    const sourceProduct = product ?? store.items.find((item) => item.id === productId)
    if (sourceProduct) {
      nextLookup.set(productId, { ...sourceProduct })
    }
  }
  selectedProductIds.value = nextIds
  selectedProductLookup.value = nextLookup
}

function toggleSelectAllVisible() {
  const visibleProducts = store.filtered
  const visibleIds = visibleProducts.map((product) => product.id)
  if (!visibleIds.length) return

  const nextIds = new Set(selectedProductIds.value)
  const nextLookup = new Map(selectedProductLookup.value)
  const allSelected = visibleIds.every((id) => nextIds.has(id))
  if (allSelected) {
    visibleIds.forEach((id) => {
      nextIds.delete(id)
      nextLookup.delete(id)
    })
  } else {
    visibleProducts.forEach((product) => {
      nextIds.add(product.id)
      nextLookup.set(product.id, { ...product })
    })
  }
  selectedProductIds.value = nextIds
  selectedProductLookup.value = nextLookup
}

function shouldSkipRowSelection(event) {
  const target = event?.target
  return target instanceof Element && Boolean(target.closest(ROW_INTERACTIVE_SELECTOR))
}

function handleProductRowDoubleClick(event, product) {
  if (!product || shouldSkipRowSelection(event)) return
  toggleProductSelection(product.id, product)
}

function openBulkEditModal() {
  if (selectedProducts.value.length === 0) {
    bulkError.value = 'Select at least one product from the table first.'
    return
  }

  bulkQueue.value = selectedProducts.value.map((product) => ({ ...product }))
  bulkQueueIndex.value = 0
  hydrateBulkForm(bulkQueue.value[0])
  bulkError.value = null
  showBulkEditModal.value = true
}

function closeBulkEditModal() {
  showBulkEditModal.value = false
  bulkSaving.value = false
  bulkError.value = null
  bulkQueue.value = []
  bulkQueueIndex.value = 0
}

function hydrateBulkForm(product) {
  if (!product) return
  bulkForm.value = {
    name: product.name ?? '',
    generic_name: product.generic_name ?? '',
    brand_name: product.brand_name ?? '',
    supplier_name: product.supplier_name ?? '',
    therapeutic_category: product.therapeutic_category ?? '',
    product_type: product.product_type ?? 'Medical',
    reorder_level: Number.isFinite(Number(product.reorder_level)) ? Number(product.reorder_level) : 0,
    dispense_without_prescription: Boolean(product.dispense_without_prescription),
    status: product.status ?? 'Active',
  }
}

function jumpToBulkQueue(index) {
  if (index < 0 || index >= bulkQueue.value.length) return
  bulkQueueIndex.value = index
  hydrateBulkForm(bulkQueue.value[index])
  bulkError.value = null
}

function skipBulkCurrent() {
  if (!bulkQueue.value.length) {
    closeBulkEditModal()
    return
  }

  if (bulkHasNext.value) {
    jumpToBulkQueue(bulkQueueIndex.value + 1)
    return
  }

  closeBulkEditModal()
}

async function saveBulkCurrent({ goNext = true } = {}) {
  if (!bulkCurrentProduct.value) {
    bulkError.value = 'No selected product in queue.'
    return
  }

  const payload = {
    name: String(bulkForm.value.name || '').trim(),
    generic_name: String(bulkForm.value.generic_name || '').trim() || null,
    brand_name: String(bulkForm.value.brand_name || '').trim() || null,
    supplier_name: String(bulkForm.value.supplier_name || '').trim() || null,
    therapeutic_category: bulkForm.value.therapeutic_category || null,
    product_type: bulkForm.value.product_type,
    reorder_level: parseInt(bulkForm.value.reorder_level, 10) || 0,
    dispense_without_prescription: Boolean(bulkForm.value.dispense_without_prescription),
    status: bulkForm.value.status,
  }

  bulkSaving.value = true
  bulkError.value = null
  try {
    const current = bulkCurrentProduct.value
    const updated = await store.updateProduct(current.id, payload)
    bulkQueue.value[bulkQueueIndex.value] = updated

    if (goNext && bulkHasNext.value) {
      jumpToBulkQueue(bulkQueueIndex.value + 1)
      return
    }

    if (!bulkHasNext.value) {
      clearProductSelection()
    }
    closeBulkEditModal()
  } catch (err) {
    bulkError.value = err?.message || 'Bulk update failed.'
  } finally {
    bulkSaving.value = false
  }
}

const form = ref(emptyForm())
const editingId = ref(null)
const extraUnits = ref([])

function addExtraUnit() {
  extraUnits.value.push({ name: 'Pack', quantity_in_base: 1, price_per_unit: '' })
}

function removeExtraUnit(index) {
  extraUnits.value.splice(index, 1)
}

// Filters reset to page 1 on change
let searchTimer = null
watch(() => store.filters.name, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => store.fetchProducts(1), 400)
})
watch(() => store.filters.therapeutic_category, () => store.fetchProducts(1))
watch(() => store.pageSize, () => store.fetchProducts(1))

onMounted(() => store.fetchProducts(1))

// Helpers
function basePrice(p) { return p.product_units?.[0]?.price_per_unit ?? null }
function fmtPrice(v) { return v != null ? formatSimple(v, 0) : '—' }
function fmtMarkup(v) { return v != null ? `${Number(v).toFixed(1)}%` : '—' }

function stockClass(qty, reorder) {
  if (qty === 0) return 'stock-zero'
  if (reorder > 0 && qty <= reorder) return 'stock-low'
  return 'stock-ok'
}

function parsePositiveInteger(value, label) {
  const parsed = Number.parseInt(String(value), 10)
  if (!Number.isFinite(parsed) || parsed < 1) {
    throw new Error(`${label} must be a whole number of at least 1.`)
  }
  return parsed
}

const inventoryMetrics = computed(() => {
  const rows = store.filtered
  const total = rows.length
  const outOfStock = rows.filter(p => p.quantity_on_hand === 0).length
  const lowStock = rows.filter(p => p.quantity_on_hand > 0 && p.reorder_level > 0 && p.quantity_on_hand <= p.reorder_level).length
  const active = rows.filter(p => p.status === 'Active').length
  return { total, outOfStock, lowStock, active }
})

// ── Add ───────────────────────────────────────────────────
function openAddModal() { form.value = emptyForm(); extraUnits.value = []; modalError.value = null; showAddModal.value = true }

async function submitAdd() {
  saving.value = true; modalError.value = null
  try {
    const baseUnit = form.value.base_unit
    const initialQuantity = Math.max(0, Number.parseInt(String(form.value.initial_quantity), 10) || 0)
    const reorderLevel = Math.max(0, Number.parseInt(String(form.value.reorder_level), 10) || 0)
    const created = await store.createProduct({
      name: form.value.name.trim(),
      generic_name: form.value.generic_name.trim() || null,
      brand_name: form.value.brand_name.trim() || null,
      supplier_name: form.value.supplier_name.trim() || null,
      therapeutic_category: form.value.therapeutic_category || null,
      product_type: form.value.product_type,
      base_unit: baseUnit,
      price_per_unit: parseFloat(form.value.price_per_unit),
      multiplier_to_base: parsePositiveInteger(form.value.multiplier_to_base, `Quantity in ${baseUnit}`),
      initial_quantity: initialQuantity,
      reorder_level: reorderLevel,
      dispense_without_prescription: form.value.dispense_without_prescription,
      status: form.value.status,
    })
    for (const eu of extraUnits.value) {
      const price = parseFloat(eu.price_per_unit)
      if (!Number.isFinite(price) || price <= 0) continue
      await productsService.addUnit(created.id, {
        name: eu.name,
        price_per_unit: price,
        multiplier_to_base: parsePositiveInteger(eu.quantity_in_base, `Quantity in ${baseUnit}`),
      })
    }
    if (extraUnits.value.length) await store.fetchProducts(store.currentPage)
    showAddModal.value = false
  } catch (err) { modalError.value = err.message }
  finally { saving.value = false }
}

// ── Edit ──────────────────────────────────────────────────
function openEditModal(p) {
  editingId.value = p.id
  form.value = {
    name: p.name, generic_name: p.generic_name || '', brand_name: p.brand_name || '',
    supplier_name: p.supplier_name || '', therapeutic_category: p.therapeutic_category || '',
    product_type: p.product_type, base_unit: p.base_unit || 'Pack',
    price_per_unit: '', multiplier_to_base: 1,
    initial_quantity: p.quantity_on_hand, reorder_level: p.reorder_level,
    dispense_without_prescription: p.dispense_without_prescription, status: p.status,
  }
  modalError.value = null; showEditModal.value = true
}

async function submitEdit() {
  saving.value = true; modalError.value = null
  try {
    await store.updateProduct(editingId.value, {
      name: form.value.name.trim(),
      generic_name: form.value.generic_name.trim() || null,
      brand_name: form.value.brand_name.trim() || null,
      supplier_name: form.value.supplier_name.trim() || null,
      therapeutic_category: form.value.therapeutic_category || null,
      product_type: form.value.product_type,
      reorder_level: parseInt(form.value.reorder_level, 10),
      dispense_without_prescription: form.value.dispense_without_prescription,
      status: form.value.status,
    })
    showEditModal.value = false
  } catch (err) { modalError.value = err.message }
  finally { saving.value = false }
}

// ── Delete ────────────────────────────────────────────────
async function deleteProduct(id) {
  const confirmed = await confirm({
    title: 'Delete Product',
    message: 'Remove this product? This cannot be undone.',
    confirmText: 'Delete',
    confirmStyle: 'danger',
  })
  if (!confirmed) return
  try { await store.removeProduct(id) } catch (err) { alert(err.message) }
}

// ── CSV Import ────────────────────────────────────────────
const showImportModal = ref(false)
const importFile = ref(null)
const importSkipDuplicates = ref(true)
const importing = ref(false)
const importResult = ref(null)
const importError = ref(null)

function openImportModal() {
  importFile.value = null
  importResult.value = null
  importError.value = null
  showImportModal.value = true
}

function onFileChange(e) {
  importFile.value = e.target.files[0] ?? null
}

function downloadTemplate() {
  const cols = [
    'PRODUCT NAME', 'BRAND NAME', 'SUPPLIER', 'GENERIC NAME',
    'STOCK THRESHOLD', 'BARCODE', 'MARKUP', 'STOCK',
    'TYPE', 'DISPENSE WITHOUT PRESCRIPTION', 'ITEM RETURN POLICY', 'STATUS',
  ]
  const ex = [
    'Amoxicillin 500mg Cap', 'Amoxil', 'ABC Pharma', 'Amoxicillin',
    '10', '', '20', '0', 'Medical', 'Yes', 'No Returns', 'Active',
  ]
  const csv = [cols.join(','), ex.join(',')].join('\n')
  const a = document.createElement('a')
  a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }))
  a.download = 'pharmax_product_template.csv'
  a.click()
}

async function submitImport() {
  if (!importFile.value) return
  importing.value = true
  importError.value = null
  importResult.value = null
  try {
    importResult.value = await productsService.importCsv(importFile.value, importSkipDuplicates.value)
    await store.fetchProducts(1)
  } catch (err) {
    importError.value = err.message
  } finally {
    importing.value = false
  }
}
</script>

<template>
  <section class="products-page">
    <!-- Header actions -->
    <div class="page-actions phx-filter-bar">
      <div class="filters">
        <div class="search-wrap">
          <span class="material-icons search-icon">search</span>
          <input
            v-model="store.filters.name"
            class="search-input"
            type="text"
            placeholder="Search by name, brand or generic…"
          />
        </div>
        <select v-model="store.filters.therapeutic_category" class="filter-select">
          <option value="">All Categories</option>
          <option v-for="cat in THERAPEUTIC_CATEGORIES" :key="cat" :value="cat">{{ cat }}</option>
        </select>
        <select v-model="store.filters.product_type" class="filter-select">
          <option value="">All Types</option>
          <option value="Medical">Medical</option>
          <option value="Non-medical">Non-medical</option>
        </select>
      </div>
      <div class="action-btns">
        <button
          class="btn-outline btn-bulk"
          :class="{ 'btn-bulk-active': selectedProducts.length > 0 }"
          @click="openBulkEditModal"
        >
          Bulk Edit ({{ selectedProducts.length }})
        </button>
        <button class="btn-outline" @click="openImportModal">
          <span class="material-icons">upload_file</span>
          Import CSV
        </button>
        <button class="btn-outline btn-soon" title="Excel import — coming soon" disabled>
          <span class="material-icons">table_view</span>
          Excel
        </button>
        <button class="btn-outline btn-soon" title="PDF import — coming soon" disabled>
          <span class="material-icons">picture_as_pdf</span>
          PDF
        </button>
        <button class="btn-primary" @click="openAddModal">
          <span class="material-icons">add</span>
          Add Product
        </button>
      </div>
    </div>

    <article class="price-guidance">
      <strong>Quick note:</strong>
      Update selling prices in <em>Units &amp; Pricing</em>. Use this page to manage names, suppliers, categories, and stock rules.
    </article>

    <div class="inventory-overview">
      <article class="metric-card">
        <span class="metric-label">Visible Products</span>
        <strong class="metric-value">{{ inventoryMetrics.total.toLocaleString() }}</strong>
      </article>
      <article class="metric-card success">
        <span class="metric-label">Active</span>
        <strong class="metric-value">{{ inventoryMetrics.active.toLocaleString() }}</strong>
      </article>
      <article class="metric-card warning">
        <span class="metric-label">Low Stock</span>
        <strong class="metric-value">{{ inventoryMetrics.lowStock.toLocaleString() }}</strong>
      </article>
      <article class="metric-card danger">
        <span class="metric-label">Out of Stock</span>
        <strong class="metric-value">{{ inventoryMetrics.outOfStock.toLocaleString() }}</strong>
      </article>
    </div>

    <!-- Loading / error -->
    <p v-if="store.loading" class="state-msg phx-state phx-state--empty">Loading products…</p>
    <p v-else-if="store.error" class="state-msg error phx-state phx-state--error">{{ store.error }}</p>

    <!-- Table -->
    <div v-else class="table-wrap phx-table-wrap">
      <table>
        <thead>
          <tr>
            <th class="center">
              <input
                type="checkbox"
                :checked="store.filtered.length > 0 && store.filtered.every((p) => selectedProductIds.has(p.id))"
                @change="toggleSelectAllVisible"
                aria-label="Select all visible products"
              />
            </th>
            <th>SKU</th>
            <th>Product Name</th>
            <th>Brand</th>
            <th>Generic Name</th>
            <th>Supplier</th>
            <th>Category</th>
            <th>Type</th>
            <th>Base Unit</th>
             <th class="num">Markup %</th>
             <th class="num">Price</th>
             <th class="num">Stock</th>
             <th class="num">Reorder</th>
             <th class="center">No Prescription</th>
             <th>Status</th>
             <th></th>
           </tr>
         </thead>
         <tbody>
          <tr v-if="store.filtered.length === 0">
            <td colspan="16" class="empty-row phx-empty-cell">No products found.</td>
          </tr>
          <tr
            v-for="p in store.filtered"
            :key="p.id"
            :class="[
              'product-row',
              stockClass(p.quantity_on_hand, p.reorder_level),
              { 'row-selected': selectedProductIds.has(p.id) },
            ]"
            @dblclick="handleProductRowDoubleClick($event, p)"
          >
            <td class="center">
              <input
                type="checkbox"
                :checked="selectedProductIds.has(p.id)"
                @change="toggleProductSelection(p.id, p)"
              />
            </td>
            <td class="mono sku">{{ p.sku }}</td>
            <td class="name-cell">{{ p.name }}</td>
            <td class="muted-sm">{{ p.brand_name || '—' }}</td>
            <td class="generic">{{ p.generic_name || '—' }}</td>
            <td class="muted-sm">{{ p.supplier_name || '—' }}</td>
            <td>
              <span v-if="p.therapeutic_category" class="cat-pill phx-badge">{{ p.therapeutic_category }}</span>
              <span v-else class="muted">—</span>
            </td>
            <td>
              <span class="type-pill phx-badge" :class="p.product_type === 'Medical' ? 'medical' : 'nonmedical'">
                {{ p.product_type }}
              </span>
            </td>
            <td class="muted-sm mono">{{ p.base_unit ?? '—' }}</td>
            <td class="num muted-sm mono">{{ fmtMarkup(p.markup_percent) }}</td>
            <td class="num mono">{{ fmtPrice(basePrice(p)) }}</td>
            <td class="num stock-cell">
              <span class="stock-pill mono" :class="stockClass(p.quantity_on_hand, p.reorder_level)">
                {{ p.quantity_on_hand }}
              </span>
            </td>
            <td class="num muted-sm mono">{{ p.reorder_level }}</td>
            <td class="center">
              <span class="material-icons otc-icon" :class="p.dispense_without_prescription ? 'otc-yes' : 'otc-no'">
                {{ p.dispense_without_prescription ? 'check_circle' : 'cancel' }}
              </span>
            </td>
            <td>
              <span
                class="status-pill phx-badge"
                :class="[
                  p.status.toLowerCase(),
                  p.status === 'Active' ? 'phx-badge--success' : p.status === 'Deleted' ? 'phx-badge--error' : 'phx-badge--muted',
                ]"
              >
                {{ p.status }}
              </span>
            </td>
            <td class="actions">
              <button class="icon-btn" title="Edit" @click="openEditModal(p)">
                <span class="material-icons">edit</span>
              </button>
              <button v-if="canDelete" class="icon-btn danger" title="Delete" @click="deleteProduct(p.id)">
                <span class="material-icons">delete</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination bar -->
    <div class="pagination-bar">
      <span class="page-info">
        Showing {{ store.pageStart }}–{{ store.pageEnd }} &nbsp;·&nbsp;
        Page {{ store.currentPage }}{{ store.hasMore ? '+' : '' }}
      </span>
      <div class="page-controls">
        <label class="per-page-label">
          Per page
          <select v-model="store.pageSize" class="per-page-select">
            <option v-for="s in PAGE_SIZES" :key="s" :value="s">{{ s }}</option>
          </select>
        </label>
        <button class="page-btn" :disabled="store.currentPage === 1 || store.loading" @click="store.goToPage(store.currentPage - 1)">
          <span class="material-icons">chevron_left</span>
        </button>
        <button class="page-btn" :disabled="!store.hasMore || store.loading" @click="store.goToPage(store.currentPage + 1)">
          <span class="material-icons">chevron_right</span>
        </button>
      </div>
    </div>

    <!-- Import CSV Modal -->
    <Teleport to="body">
      <div v-if="showImportModal" class="modal-overlay phx-modal-overlay" @click.self="showImportModal = false">
        <div class="modal phx-modal import-modal">
          <div class="modal-head">
            <h3>Import Products from CSV</h3>
            <button class="icon-btn" @click="showImportModal = false">
              <span class="material-icons">close</span>
            </button>
          </div>

          <div class="modal-body import-body">
            <!-- Instructions -->
            <div class="import-info">
              <p>Upload a CSV file with product data. The importer accepts these column names (case-insensitive):</p>
              <p class="col-list">PRODUCT NAME · BRAND NAME · SUPPLIER · GENERIC NAME · STOCK THRESHOLD · BARCODE · MARKUP · STOCK · TYPE · DISPENSE WITHOUT PRESCRIPTION · ITEM RETURN POLICY · STATUS</p>
              <button class="link-btn" @click="downloadTemplate">Download template CSV</button>
            </div>

            <!-- File picker -->
            <label class="file-field">
              <span class="material-icons">attach_file</span>
              <span>{{ importFile ? importFile.name : 'Choose .csv file…' }}</span>
              <input type="file" accept=".csv" class="hidden-input" @change="onFileChange" />
            </label>

            <!-- Options -->
            <label class="checkbox-field">
              <input v-model="importSkipDuplicates" type="checkbox" />
              <span>Skip products with the same name already in the database</span>
            </label>

            <!-- Error -->
            <p v-if="importError" class="modal-error">{{ importError }}</p>

            <!-- Results -->
            <div v-if="importResult" class="import-result">
              <div class="result-stats">
                <div class="stat">
                  <span class="stat-num created">{{ importResult.created }}</span>
                  <span class="stat-label">Created</span>
                </div>
                <div class="stat">
                  <span class="stat-num skipped">{{ importResult.skipped }}</span>
                  <span class="stat-label">Skipped</span>
                </div>
                <div class="stat">
                  <span class="stat-num errored">{{ importResult.errors.length }}</span>
                  <span class="stat-label">Errors</span>
                </div>
                <div class="stat">
                  <span class="stat-num total">{{ importResult.total }}</span>
                  <span class="stat-label">Total rows</span>
                </div>
              </div>
              <div v-if="importResult.errors.length > 0" class="error-list">
                <p class="error-list-title">Row errors (first {{ Math.min(importResult.errors.length, 10) }}):</p>
                <ul>
                  <li v-for="e in importResult.errors.slice(0, 10)" :key="e.row">
                    Row {{ e.row }} — <strong>{{ e.name }}</strong>: {{ e.reason }}
                  </li>
                </ul>
              </div>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-outline" @click="showImportModal = false">Close</button>
              <button
                class="btn-primary"
                :disabled="!importFile || importing"
                @click="submitImport"
              >
                <span v-if="importing" class="material-icons spin">sync</span>
                {{ importing ? 'Importing…' : 'Import' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Add Product Modal -->
    <Teleport to="body">
      <div v-if="showAddModal" class="modal-overlay phx-modal-overlay" @click.self="showAddModal = false">
        <div class="modal phx-modal">
          <div class="modal-head">
            <h3>Add Product</h3>
            <button class="icon-btn" @click="showAddModal = false">
              <span class="material-icons">close</span>
            </button>
          </div>

          <form class="modal-body" @submit.prevent="submitAdd">
            <div class="form-grid">
              <label class="field span2">
                <span>Product Name *</span>
                <input v-model="form.name" type="text" required placeholder="e.g. Amoxicillin 500mg Capsules" />
              </label>
              <label class="field">
                <span>Generic Name</span>
                <input v-model="form.generic_name" type="text" placeholder="e.g. Amoxicillin" />
              </label>
              <label class="field">
                <span>Brand Name</span>
                <input v-model="form.brand_name" type="text" placeholder="e.g. Amoxil" />
              </label>
              <label class="field">
                <span>Supplier</span>
                <input v-model="form.supplier_name" type="text" placeholder="Supplier name" />
              </label>
              <label class="field">
                <span>Therapeutic Category</span>
                <select v-model="form.therapeutic_category">
                  <option value="">— None —</option>
                  <option v-for="cat in THERAPEUTIC_CATEGORIES" :key="cat" :value="cat">{{ cat }}</option>
                </select>
              </label>
              <label class="field">
                <span>Product Type *</span>
                <select v-model="form.product_type" required>
                  <option value="Medical">Medical</option>
                  <option value="Non-medical">Non-medical</option>
                </select>
              </label>
              <label class="field">
                <span>Base Unit *</span>
                <select v-model="form.base_unit" required>
                  <option v-for="u in BASE_UNITS" :key="u" :value="u">{{ u }}</option>
                </select>
              </label>
              <label class="field">
                <span>Price per {{ form.base_unit }} ({{ currencySymbol }}) *</span>
                <input v-model="form.price_per_unit" type="number" min="0" step="100" required placeholder="0" />
              </label>
              <label class="field">
                <span class="label-with-tip">
                  Quantity in {{ form.base_unit }}
                  <span class="material-icons tooltip-icon" title="How many base units are contained in this unit">info</span>
                </span>
                <input v-model="form.multiplier_to_base" type="number" min="1" step="1" placeholder="1" />
              </label>
              <label class="field">
                <span>Initial Stock Qty</span>
                <input v-model="form.initial_quantity" type="number" min="0" placeholder="0" />
              </label>
              <label class="field">
                <span class="label-with-tip">
                  Reorder Level
                  <span class="material-icons tooltip-icon" title="Minimum stock before restocking (based on base unit)">info</span>
                </span>
                <input v-model="form.reorder_level" type="number" min="0" placeholder="0" />
              </label>
              <label class="field checkbox-field span2">
                <input v-model="form.dispense_without_prescription" type="checkbox" />
                <span>Dispense without prescription (OTC)</span>
              </label>
            </div>

            <div class="extra-units-section">
              <div class="extra-units-header">
                <span class="extra-units-title">Additional Units</span>
                <button type="button" class="btn-outline btn-sm" @click="addExtraUnit">
                  <span class="material-icons">add</span> Add Unit
                </button>
              </div>
              <div v-for="(eu, idx) in extraUnits" :key="idx" class="extra-unit-row">
                <label class="field">
                  <span>Unit Name *</span>
                  <select v-model="eu.name" required>
                    <option v-for="u in BASE_UNITS" :key="u" :value="u">{{ u }}</option>
                  </select>
                </label>
                <label class="field">
                  <span class="label-with-tip">
                    Qty in {{ form.base_unit }}
                    <span class="material-icons tooltip-icon" title="How many base units are contained in this unit">info</span>
                  </span>
                  <input v-model="eu.quantity_in_base" type="number" min="1" step="1" placeholder="1" />
                </label>
                <label class="field">
                  <span>Price ({{ currencySymbol }}) *</span>
                  <input v-model="eu.price_per_unit" type="number" min="0" step="100" required placeholder="0" />
                </label>
                <button type="button" class="icon-btn danger extra-unit-remove" title="Remove" @click="removeExtraUnit(idx)">
                  <span class="material-icons">close</span>
                </button>
              </div>
            </div>

            <p v-if="modalError" class="modal-error">{{ modalError }}</p>

            <div class="modal-footer">
              <button type="button" class="btn-outline" @click="showAddModal = false">Cancel</button>
              <button type="submit" class="btn-primary" :disabled="saving">
                {{ saving ? 'Saving…' : 'Add Product' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Edit Product Modal -->
    <Teleport to="body">
      <div v-if="showEditModal" class="modal-overlay phx-modal-overlay" @click.self="showEditModal = false">
        <div class="modal phx-modal">
          <div class="modal-head">
            <h3>Edit Product</h3>
            <button class="icon-btn" @click="showEditModal = false">
              <span class="material-icons">close</span>
            </button>
          </div>

          <form class="modal-body" @submit.prevent="submitEdit">
            <div class="form-grid">
              <label class="field span2">
                <span>Product Name *</span>
                <input v-model="form.name" type="text" required />
              </label>
              <label class="field">
                <span>Generic Name</span>
                <input v-model="form.generic_name" type="text" />
              </label>
              <label class="field">
                <span>Brand Name</span>
                <input v-model="form.brand_name" type="text" />
              </label>
              <label class="field">
                <span>Supplier</span>
                <input v-model="form.supplier_name" type="text" />
              </label>
              <label class="field">
                <span>Therapeutic Category</span>
                <select v-model="form.therapeutic_category">
                  <option value="">— None —</option>
                  <option v-for="cat in THERAPEUTIC_CATEGORIES" :key="cat" :value="cat">{{ cat }}</option>
                </select>
              </label>
              <label class="field">
                <span>Product Type</span>
                <select v-model="form.product_type">
                  <option value="Medical">Medical</option>
                  <option value="Non-medical">Non-medical</option>
                </select>
              </label>
              <label class="field">
                <span class="label-with-tip">
                  Reorder Level
                  <span class="material-icons tooltip-icon" title="Minimum stock before restocking (based on base unit)">info</span>
                </span>
                <input v-model="form.reorder_level" type="number" min="0" />
              </label>
              <label class="field">
                <span>Status</span>
                <select v-model="form.status">
                  <option value="Active">Active</option>
                  <option value="Inactive">Inactive</option>
                </select>
              </label>
              <label class="field checkbox-field span2">
                <input v-model="form.dispense_without_prescription" type="checkbox" />
                <span>Dispense without prescription (OTC)</span>
              </label>
            </div>

            <p v-if="modalError" class="modal-error">{{ modalError }}</p>

            <div class="modal-footer">
              <button type="button" class="btn-outline" @click="showEditModal = false">Cancel</button>
              <button type="submit" class="btn-primary" :disabled="saving">
                {{ saving ? 'Saving…' : 'Save Changes' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Bulk Edit Products Modal -->
    <Teleport to="body">
      <div v-if="showBulkEditModal" class="modal-overlay phx-modal-overlay" @click.self="closeBulkEditModal">
        <div class="modal phx-modal">
          <div class="modal-head">
            <h3>Bulk Edit Queue ({{ bulkProgressLabel }})</h3>
            <button class="icon-btn" @click="closeBulkEditModal">
              <span class="material-icons">close</span>
            </button>
          </div>

          <form class="modal-body" @submit.prevent="saveBulkCurrent({ goNext: true })">
            <div v-if="bulkCurrentProduct" class="bulk-queue-meta">
              <p>
                Editing: <strong>{{ bulkCurrentProduct.name }}</strong>
                <span class="bulk-queue-sku">SKU {{ bulkCurrentProduct.sku }}</span>
              </p>
            </div>

            <div class="bulk-queue-strip" v-if="bulkQueue.length">
              <button
                v-for="(product, index) in bulkQueue"
                :key="product.id"
                type="button"
                class="queue-chip"
                :class="{ active: index === bulkQueueIndex }"
                @click="jumpToBulkQueue(index)"
              >
                {{ index + 1 }}. {{ product.name }}
              </button>
            </div>

            <div class="form-grid">
              <label class="field span2">
                <span>Product Name *</span>
                <input v-model="bulkForm.name" type="text" required />
              </label>
              <label class="field">
                <span>Generic Name</span>
                <input v-model="bulkForm.generic_name" type="text" />
              </label>
              <label class="field">
                <span>Brand Name</span>
                <input v-model="bulkForm.brand_name" type="text" />
              </label>
              <label class="field">
                <span>Supplier</span>
                <input v-model="bulkForm.supplier_name" type="text" />
              </label>
              <label class="field">
                <span>Therapeutic Category</span>
                <select v-model="bulkForm.therapeutic_category">
                  <option value="">— None —</option>
                  <option v-for="cat in THERAPEUTIC_CATEGORIES" :key="cat" :value="cat">{{ cat }}</option>
                </select>
              </label>
              <label class="field">
                <span>Product Type</span>
                <select v-model="bulkForm.product_type">
                  <option value="Medical">Medical</option>
                  <option value="Non-medical">Non-medical</option>
                </select>
              </label>
              <label class="field">
                <span>Reorder Level</span>
                <input v-model="bulkForm.reorder_level" type="number" min="0" />
              </label>
              <label class="field span2">
                <span>OTC Dispense Policy</span>
                <select v-model="bulkForm.dispense_without_prescription">
                  <option :value="true">Allow OTC dispense</option>
                  <option :value="false">Prescription required</option>
                </select>
              </label>
              <label class="field">
                <span>Status</span>
                <select v-model="bulkForm.status">
                  <option value="Active">Active</option>
                  <option value="Inactive">Inactive</option>
                </select>
              </label>
            </div>
            <p v-if="bulkError" class="modal-error">{{ bulkError }}</p>

            <div class="modal-footer">
              <button type="button" class="btn-outline" @click="closeBulkEditModal">Cancel</button>
              <button type="button" class="btn-outline" :disabled="bulkSaving" @click="skipBulkCurrent">
                {{ bulkHasNext ? 'Skip Product' : 'Skip & Close' }}
              </button>
              <button type="submit" class="btn-primary" :disabled="bulkSaving || !bulkCurrentProduct">
                {{ bulkSaving ? 'Saving…' : (bulkHasNext ? 'Save & Next' : 'Save & Finish') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

  </section>
</template>

<style scoped>
.products-page {
  display: grid;
  gap: 18px;
}

.inventory-overview {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.price-guidance {
  border: 1px dashed var(--border-default);
  border-radius: 10px;
  background: var(--bg-recessed);
  padding: 10px 12px;
  font-size: 12px;
  color: var(--text-secondary);
}

.metric-card {
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  background: var(--bg-card);
  padding: 10px 12px;
  display: grid;
  gap: 4px;
}

.metric-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  font-weight: 600;
}

.metric-value {
  font-family: var(--font-data);
  font-size: 20px;
  line-height: 1.1;
  color: var(--text-primary);
}

.metric-card.success .metric-value {
  color: var(--success);
}

.metric-card.warning .metric-value {
  color: var(--warning);
}

.metric-card.danger .metric-value {
  color: var(--error);
}

/* ── Header / filters ─────────────────────────────── */
.page-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.search-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 10px;
  font-size: 18px;
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  height: 38px;
  padding: 0 12px 0 36px;
  border-radius: 8px;
  border: 1px solid var(--border-default);
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 13px;
  width: 280px;
  outline: none;
}

.search-input:focus {
  border-color: var(--accent);
}

.search-input:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  box-shadow: 0 0 0 3px var(--primary-tint);
}

.filter-select {
  height: 38px;
  padding: 0 12px;
  border-radius: 8px;
  border: 1px solid var(--border-default);
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  outline: none;
}

.filter-select:focus {
  border-color: var(--accent);
}

.filter-select:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  box-shadow: 0 0 0 3px var(--primary-tint);
}

.action-btns {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-soon {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 38px;
  padding: 0 16px;
  border-radius: 8px;
  border: 0;
  background: var(--accent);
  color: var(--text-inverse);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-outline {
  height: 38px;
  padding: 0 16px;
  border-radius: 8px;
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
}

.btn-bulk {
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.btn-bulk-active {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--text-inverse);
  box-shadow: 0 6px 14px color-mix(in oklab, var(--accent) 35%, transparent);
}

.btn-bulk-active:hover {
  filter: brightness(0.98);
}

/* ── State messages ───────────────────────────────── */
.state-msg {
  margin: 0;
  font-size: 13px;
  color: var(--text-muted);
  padding: 32px 0;
  text-align: center;
}

.state-msg.error {
  color: var(--error);
}

/* ── Table ────────────────────────────────────────── */
.table-wrap {
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  background: var(--bg-card);
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1400px;
}

thead tr {
  border-bottom: 1px solid var(--border-subtle);
}

th {
  text-align: left;
  font-size: 11px;
  color: var(--text-muted);
  padding: 10px 14px;
  font-weight: 600;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

th.num {
  text-align: right;
}

td {
  padding: 12px 14px;
  border-top: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  font-size: 13px;
  vertical-align: middle;
}

td.num {
  text-align: right;
}

.mono {
  font-family: var(--font-data);
}

.sku {
  color: var(--text-primary);
  font-size: 12px;
  font-weight: 500;
}

.name-cell {
  color: var(--text-primary);
  font-weight: 500;
  max-width: 240px;
}

.generic {
  color: var(--accent);
  font-size: 12px;
}

.muted {
  color: var(--text-muted);
}

.muted-sm {
  color: var(--text-muted);
  font-size: 12px;
}

.center {
  text-align: center;
}

th.center {
  text-align: center;
}

.otc-icon {
  font-size: 16px;
}

.otc-yes { color: var(--success); }
.otc-no  { color: var(--text-muted); }

.empty-row {
  text-align: center;
  color: var(--text-muted);
  padding: 40px;
  border-top: none;
}

/* Stock colors */
.stock-ok { color: var(--success); }
.stock-low { color: var(--accent); }
.stock-zero { color: var(--error); }

/* Pills */
.cat-pill {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  background: var(--accent-tint);
  color: var(--accent);
  white-space: nowrap;
}

.type-pill {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  white-space: nowrap;
}

.type-pill.medical {
  background: var(--info-bg);
  color: var(--info);
}

.type-pill.nonmedical {
  background: var(--bg-elevated);
  color: var(--text-muted);
}

.status-pill {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
}

.status-pill.active {
  background: var(--success-bg);
  color: var(--success);
}

.status-pill.inactive {
  background: var(--bg-elevated);
  color: var(--text-muted);
}

.status-pill.deleted {
  background: var(--error-bg);
  color: var(--error);
}

/* Actions */
.actions {
  display: flex;
  gap: 4px;
  justify-content: flex-end;
  white-space: nowrap;
}

.icon-btn {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
}

.icon-btn .material-icons {
  font-size: 16px;
}

.icon-btn.danger {
  color: var(--error);
  border-color: var(--error-tint);
}

.icon-btn.danger:hover {
  background: var(--error-bg);
}

/* ── Modal ────────────────────────────────────────── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--overlay-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 16px;
}

.modal {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 14px;
  width: 100%;
  max-width: 620px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px;
  border-bottom: 1px solid var(--border-subtle);
}

.modal-head h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.modal-body {
  padding: 20px 24px;
  overflow-y: auto;
  flex: 1;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12px;
  color: var(--text-muted);
}

.field.span2 {
  grid-column: span 2;
}

.field input,
.field select {
  min-height: 40px;
  padding: 0 12px;
  border-radius: 8px;
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
}

.field input:focus,
.field select:focus {
  border-color: var(--accent);
}

.field input:focus-visible,
.field select:focus-visible,
.per-page-select:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  box-shadow: 0 0 0 3px var(--primary-tint);
}

.checkbox-field {
  flex-direction: row;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
}

.checkbox-field input[type='checkbox'] {
  width: 16px;
  height: 16px;
  accent-color: var(--accent);
}

.modal-error {
  margin: 12px 0 0;
  font-size: 12px;
  color: var(--error);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.bulk-queue-meta {
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  background: var(--bg-elevated);
  padding: 8px 10px;
  margin-bottom: 10px;
}

.bulk-queue-meta p {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
}

.bulk-queue-sku {
  margin-left: 8px;
  font-family: var(--font-data);
  color: var(--text-muted);
}

.bulk-queue-strip {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding-bottom: 6px;
  margin-bottom: 12px;
}

.queue-chip {
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  border-radius: 999px;
  padding: 5px 10px;
  font-size: 12px;
  white-space: nowrap;
  cursor: pointer;
}

.queue-chip.active {
  border-color: var(--accent);
  background: var(--accent-tint);
  color: var(--accent);
}

/* ── Import modal ─────────────────────────── */
.import-modal { max-width: 560px; }

.import-body { display: grid; gap: 16px; }

.import-info {
  padding: 12px;
  border-radius: 8px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  font-size: 12px;
  color: var(--text-muted);
  display: grid;
  gap: 6px;
}

.col-list {
  margin: 0;
  color: var(--accent);
  font-family: var(--font-data);
  font-size: 11px;
  line-height: 1.7;
}

.link-btn {
  background: none;
  border: none;
  color: var(--accent);
  font-size: 12px;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.file-field {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 44px;
  padding: 0 14px;
  border-radius: 8px;
  border: 1px dashed var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
}

.file-field:hover { border-color: var(--accent); }
.file-field .material-icons { font-size: 18px; color: var(--text-muted); }
.hidden-input { display: none; }

.import-result {
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
  overflow: hidden;
}

.result-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  background: var(--bg-elevated);
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 14px 8px;
  gap: 4px;
  border-right: 1px solid var(--border-subtle);
}

.stat:last-child { border-right: none; }

.stat-num {
  font-family: var(--font-data);
  font-size: 24px;
  font-weight: 600;
}

.stat-num.created  { color: var(--success); }
.stat-num.skipped  { color: var(--text-muted); }
.stat-num.errored  { color: var(--error); }
.stat-num.total    { color: var(--text-primary); }

.stat-label { font-size: 11px; color: var(--text-muted); }

.error-list {
  padding: 12px 16px;
  border-top: 1px solid var(--border-subtle);
}

.error-list-title {
  margin: 0 0 8px;
  font-size: 12px;
  color: var(--error);
  font-weight: 600;
}

.error-list ul {
  margin: 0;
  padding: 0 0 0 16px;
  display: grid;
  gap: 4px;
}

.error-list li { font-size: 12px; color: var(--text-muted); }
.error-list strong { color: var(--text-secondary); }

@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

.spin { animation: spin 0.8s linear infinite; display: inline-block; }

/* ── Pagination ────────────────────────────────── */
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 4px 0;
  flex-wrap: wrap;
  gap: 10px;
}

.page-info {
  font-size: 12px;
  color: var(--text-muted);
  font-family: var(--font-data);
}

.page-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.per-page-label {
  font-size: 12px;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 6px;
}

.per-page-select {
  min-height: 40px;
  padding: 0 8px;
  border-radius: 6px;
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  outline: none;
}

.page-btn {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
}

.page-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.page-btn .material-icons {
  font-size: 18px;
}

.page-hero {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
  padding: var(--space-5);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.eyebrow {
  margin: 0;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  font-weight: 600;
}

.page-hero h1 {
  margin: 6px 0 0;
  font-size: 24px;
  line-height: 1.2;
}

.hero-copy {
  margin: var(--space-2) 0 0;
  color: var(--text-secondary);
}

.hero-tip {
  margin: 0;
  max-width: 320px;
  font-size: 13px;
  color: var(--text-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-recessed);
  padding: var(--space-3);
}

.page-actions {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
  padding: var(--space-4);
}

.filters {
  flex: 1;
  min-width: 260px;
}

.search-input,
.filter-select {
  height: 40px;
  border-radius: var(--radius-md);
  border-color: var(--border-default);
  background: var(--bg-elevated);
}

.search-input {
  width: min(340px, 100%);
}

.action-btns {
  margin-left: auto;
}

.btn-primary,
.btn-outline {
  height: 40px;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 500;
}

.btn-primary {
  background: var(--primary);
  box-shadow: var(--shadow-xs);
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-outline {
  background: var(--bg-elevated);
  border-color: var(--border-default);
}

.btn-outline:hover:not(:disabled) {
  background: var(--bg-hover);
}

.btn-bulk-active {
  background: var(--primary);
  border-color: var(--primary);
  color: var(--text-inverse);
  box-shadow: var(--shadow-xs);
}

.price-guidance {
  border-radius: var(--radius-lg);
  border-color: var(--border-default);
  padding: var(--space-3) var(--space-4);
  color: var(--text-secondary);
}

.inventory-overview {
  gap: var(--space-3);
}

.metric-card {
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  box-shadow: var(--shadow-xs);
}

.metric-card.success .metric-value {
  color: var(--success);
}

.metric-card.warning .metric-value {
  color: var(--warning);
}

.table-wrap {
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xs);
}

table {
  min-width: 1320px;
}

th {
  background: var(--table-header-bg);
  position: sticky;
  top: 0;
  z-index: 1;
}

tbody tr:nth-child(even) td {
  background: var(--bg-muted);
}

tbody tr:hover td {
  background: var(--table-row-hover);
}

.product-row.row-selected td {
  background: color-mix(in oklab, var(--primary) 16%, var(--bg-card));
}

.product-row.row-selected:hover td {
  background: color-mix(in oklab, var(--primary) 22%, var(--bg-card));
}

.product-row.stock-low td:first-child {
  box-shadow: inset 3px 0 0 var(--warning);
}

.product-row.stock-zero td:first-child {
  box-shadow: inset 3px 0 0 var(--error);
}

.stock-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 42px;
  padding: 3px 9px;
  border-radius: var(--radius-full);
  border: 1px solid transparent;
  font-size: 12px;
}

.stock-pill.stock-ok {
  color: var(--success);
  background: var(--success-bg);
  border-color: var(--success-tint);
}

.stock-pill.stock-low {
  color: var(--warning);
  background: var(--warning-bg);
  border-color: var(--warning-tint);
}

.stock-pill.stock-zero {
  color: var(--error);
  background: var(--error-bg);
  border-color: var(--error-tint);
}

.cat-pill,
.type-pill,
.status-pill {
  border-radius: var(--radius-full);
  padding: 3px 9px;
}

.type-pill.medical {
  background: var(--info-bg);
  color: var(--info);
}

.type-pill.nonmedical {
  background: var(--bg-recessed);
  color: var(--text-tertiary);
}

.status-pill.active {
  background: var(--success-bg);
  color: var(--success);
}

.status-pill.inactive {
  background: var(--bg-recessed);
  color: var(--text-muted);
}

.icon-btn {
  border-radius: var(--radius-md);
  background: var(--bg-card);
}

.icon-btn:hover {
  background: var(--bg-hover);
  border-color: var(--border-strong);
}

.modal-overlay {
  background: var(--overlay-bg);
}

.modal {
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
}

.modal-head {
  padding: var(--space-5) var(--space-6) var(--space-4);
}

.modal-body {
  padding: var(--space-5) var(--space-6);
}

.field input,
.field select {
  border-radius: var(--radius-md);
  border-color: var(--border-default);
}

.pagination-bar {
  padding-top: var(--space-2);
}

.per-page-select,
.page-btn {
  border-radius: var(--radius-md);
}

@media (max-width: 960px) {
  .page-hero {
    padding: var(--space-4);
  }

  .filters {
    width: 100%;
  }

  .search-input {
    width: 100%;
  }

  .action-btns {
    margin-left: 0;
    width: 100%;
    flex-wrap: wrap;
  }

  .table-wrap table {
    min-width: 1160px;
  }
}

/* ── Tooltip icon ─────────────────────────────── */
.label-with-tip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.tooltip-icon {
  font-size: 14px;
  color: var(--text-muted);
  cursor: help;
  opacity: 0.7;
}

.tooltip-icon:hover {
  opacity: 1;
  color: var(--accent);
}

/* ── Extra units section ────────────────────────── */
.extra-units-section {
  margin-top: 18px;
  border-top: 1px dashed var(--border-default);
  padding-top: 14px;
}

.extra-units-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.extra-units-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.btn-sm {
  height: 32px;
  padding: 0 10px;
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.btn-sm .material-icons {
  font-size: 16px;
}

.extra-unit-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr auto;
  gap: 10px;
  align-items: end;
  margin-bottom: 10px;
}

.extra-unit-remove {
  width: 36px;
  height: 36px;
  margin-bottom: 2px;
}

@media (max-width: 640px) {
  .inventory-overview {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .field.span2 {
    grid-column: span 1;
  }

  .search-input {
    width: 100%;
  }

  .extra-unit-row {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
