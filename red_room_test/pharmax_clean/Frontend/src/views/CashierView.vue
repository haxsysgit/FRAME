<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { invoicesService } from '../services/invoices'
import { useSettingsStore } from '../stores/settings'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const router = useRouter()
const settingsStore = useSettingsStore()
const toast = useToast()

const QUEUE_POLL_INTERVAL_MS = 12000
const RETURNED_NOTE_PREFIX = '[RETURNED_TO_SENDER]'
let queuePollTimer = null

function normalizeQueueMode(value) {
  const mode = String(value || '').toUpperCase()
  return ['ALL', 'DRAFT'].includes(mode) ? mode : 'DRAFT'
}

function resolveDefaultPaymentMethod() {
  const method = String(settingsStore.defaultPaymentMethod || '').toUpperCase()
  return ['CASH', 'CARD', 'BANK_TRANSFER'].includes(method) ? method : 'CASH'
}

function pickupCode(invoiceId) {
  return String(invoiceId || '').replace(/-/g, '').slice(0, 8).toUpperCase()
}

function normalizePickupLookup(value) {
  return String(value || '').replace(/[^a-zA-Z0-9]/g, '').toLowerCase()
}

function findPickupCodeMatch(query) {
  const lookup = normalizePickupLookup(query)
  if (!lookup) return null
  return invoices.value.find((invoice) => normalizePickupLookup(pickupCode(invoice.id)) === lookup) || null
}

async function openInvoiceFromRoute(invoiceId) {
  if (!invoiceId || routeOpenHandled.value) return
  const target = invoices.value.find((invoice) => invoice.id === invoiceId)
  if (!target) return

  await selectInvoice(target)
  routeOpenHandled.value = true

  const nextQuery = { ...route.query }
  delete nextQuery.open
  delete nextQuery.source
  router.replace({ path: route.path, query: nextQuery })
}

async function openInvoiceFromPickupCode(code) {
  if (!code || routeOpenHandled.value) return
  const target = findPickupCodeMatch(code)
  if (!target) return

  await selectInvoice(target)
  routeOpenHandled.value = true

  const nextQuery = { ...route.query }
  delete nextQuery.code
  delete nextQuery.source
  router.replace({ path: route.path, query: nextQuery })
}

// ── Data ─────────────────────────────────────────────────
const invoices = ref([])
const loading = ref(true)
const error = ref(null)

// ── Selected invoice for payment ─────────────────────────
const selected = ref(null)
const selectedDetail = ref(null)
const paymentMethod = ref(resolveDefaultPaymentMethod())
const processing = ref(false)
const printingReceipt = ref(false)
const cancellingInvoiceId = ref(null)
const returningInvoiceId = ref(null)
const processError = ref(null)
const showReceipt = ref(false)
const advanceAfterPrint = ref(false)
const queueSearch = ref('')
const queueFilter = ref(normalizeQueueMode(settingsStore.cashierQueueMode))
const knownDraftInvoiceIds = ref(new Set())
const queuePrimed = ref(false)
const routeOpenHandled = ref(false)
let printAdvanceFallbackTimer = null
let onAfterPrintHandler = null

// ─────────────────────────────────────────────────────────
onMounted(async () => {
  queueFilter.value = normalizeQueueMode(settingsStore.cashierQueueMode)
  await loadInvoices()

  queuePollTimer = window.setInterval(() => {
    loadInvoices({ silent: true })
  }, QUEUE_POLL_INTERVAL_MS)
})

onBeforeUnmount(() => {
  if (queuePollTimer) {
    window.clearInterval(queuePollTimer)
    queuePollTimer = null
  }
  resetPrintAdvanceHooks()
})

function resetPrintAdvanceHooks() {
  if (printAdvanceFallbackTimer) {
    window.clearTimeout(printAdvanceFallbackTimer)
    printAdvanceFallbackTimer = null
  }
  if (onAfterPrintHandler) {
    window.removeEventListener('afterprint', onAfterPrintHandler)
    onAfterPrintHandler = null
  }
}

function isReturnedInvoice(invoice) {
  const note = String(invoice?.cashier_note || '').trim()
  return note.startsWith(RETURNED_NOTE_PREFIX)
}

function returnedReason(note) {
  const text = String(note || '').trim()
  if (!text.startsWith(RETURNED_NOTE_PREFIX)) return ''
  return text.slice(RETURNED_NOTE_PREFIX.length).trim()
}

async function loadInvoices({ silent = false } = {}) {
  if (!silent) loading.value = true
  error.value = null
  try {
    const drafts = await invoicesService.list({ status: 'DRAFT', limit: 100 })
    const visibleDrafts = Array.isArray(drafts) ? drafts : []

    invoices.value = [...visibleDrafts].sort(
      (a, b) => new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime(),
    )

    const routeOpenInvoiceId = String(route.query.open || '')
    const routePickupCode = String(route.query.code || '')
    const incomingDrafts = visibleDrafts.filter(
      (inv) => !isReturnedInvoice(inv) && !knownDraftInvoiceIds.value.has(inv.id),
    )
    const notifyDrafts = incomingDrafts.filter((inv) => inv.id !== routeOpenInvoiceId)

    if (queuePrimed.value && notifyDrafts.length > 0) {
      if (notifyDrafts.length === 1) {
        const inv = notifyDrafts[0]
        toast.info(`New invoice in queue: #${inv.id.slice(0, 8)} (Code ${pickupCode(inv.id)})`)
      } else {
        toast.info(`${notifyDrafts.length} new invoices are waiting in cashier queue.`)
      }
    }

    knownDraftInvoiceIds.value = new Set(
      visibleDrafts.filter((inv) => !isReturnedInvoice(inv)).map((inv) => inv.id),
    )
    if (!queuePrimed.value) queuePrimed.value = true

    if (routeOpenInvoiceId) {
      await openInvoiceFromRoute(routeOpenInvoiceId)
    } else if (routePickupCode) {
      await openInvoiceFromPickupCode(routePickupCode)
    }

    if (selected.value && !showReceipt.value) {
      const visibleInvoiceIds = new Set(invoices.value.filter(shouldDisplayInQueue).map(i => i.id))
      if (!visibleInvoiceIds.has(selected.value.id)) clearSelection()
    }

    if (!selected.value && !showReceipt.value && nonReturnedDraftInvoices.value.length > 0) {
      await selectInvoice(nonReturnedDraftInvoices.value[0])
    }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// ── Computed ─────────────────────────────────────────────
function isCreditInvoice(invoice) {
  const paymentMethod = String(invoice.payment_method || '').toUpperCase()
  const label = String(invoice.name || '').toLowerCase()
  const total = Number(invoice.total_amount ?? 0)
  return paymentMethod.includes('CREDIT') || label.includes('credit') || total < 0
}

function shouldDisplayInQueue(invoice) {
  const status = String(invoice?.status || '').toUpperCase()
  if (status === 'DRAFT') return true
  if (isCreditInvoice(invoice)) return true
  const total = Number(invoice.total_amount ?? 0)
  return Number.isFinite(total) && total > 0
}

const queueVisibleInvoices = computed(() => invoices.value.filter(shouldDisplayInQueue))
const draftInvoices = computed(() => queueVisibleInvoices.value.filter(i => i.status === 'DRAFT'))
const nonReturnedDraftInvoices = computed(() =>
  draftInvoices.value.filter((invoice) => !isReturnedInvoice(invoice)),
)
const returnedDraftInvoices = computed(() =>
  draftInvoices.value.filter((invoice) => isReturnedInvoice(invoice)),
)
const stampedInvoices = computed(() => queueVisibleInvoices.value.filter((i) => {
  const status = String(i.status || '').toUpperCase()
  return status === 'STAMPED' || status === 'FINALIZED'
}))

function matchesQueueQuery(invoice) {
  const query = queueSearch.value.trim().toLowerCase()
  if (!query) return true
  const code = pickupCode(invoice.id).toLowerCase()
  const sender = String(invoice.sold_by_name || invoice.name || '').toLowerCase()

  return (
    invoice.id?.toLowerCase().includes(query) ||
    code.includes(query) ||
    sender.includes(query) ||
    invoice.payment_method?.toLowerCase().includes(query) ||
    String(invoice.total_amount ?? '').includes(query)
  )
}

const filteredDraftInvoices = computed(() => {
  if (queueFilter.value !== 'ALL' && queueFilter.value !== 'DRAFT') return []
  return nonReturnedDraftInvoices.value.filter(matchesQueueQuery)
})

const filteredReturnedInvoices = computed(() => {
  if (queueFilter.value !== 'ALL' && queueFilter.value !== 'DRAFT') return []
  return returnedDraftInvoices.value.filter(matchesQueueQuery)
})

const canCancelSelected = computed(() => {
  const status = String(selected.value?.status || '').toUpperCase()
  return status === 'DRAFT' || status === 'STAMPED' || status === 'FINALIZED'
})

const isCompactInvoice = computed(() => (selectedDetail.value?.items?.length || 0) <= 3)

function toAmount(value) {
  const amount = Number(value)
  return Number.isFinite(amount) ? amount : 0
}

const selectedReceiptSubtotal = computed(() => {
  const items = selectedDetail.value?.items || []
  return items.reduce((sum, item) => {
    const lineTotal = toAmount(item?.line_total)
    if (lineTotal > 0) return sum + lineTotal
    return sum + (toAmount(item?.quantity) * toAmount(item?.unit_price))
  }, 0)
})

const selectedReceiptTotal = computed(() => toAmount(selectedDetail.value?.total_amount))

const selectedReceiptDiscount = computed(() =>
  Math.max(selectedReceiptSubtotal.value - selectedReceiptTotal.value, 0),
)

const selectedReceiptCredit = computed(() => {
  const payment = String(selectedDetail.value?.payment_method || paymentMethod.value || '').toUpperCase()
  if (payment.includes('CREDIT')) return Math.max(selectedReceiptTotal.value, 0)
  return Math.max(selectedReceiptTotal.value - selectedReceiptSubtotal.value, 0)
})

watch(queueSearch, async (value) => {
  const match = findPickupCodeMatch(value)
  if (!match) return
  if (selected.value?.id === match.id) return
  await selectInvoice(match)
})

// ── Select invoice and load details ──────────────────────
async function selectInvoice(inv) {
  selected.value = inv
  selectedDetail.value = null
  paymentMethod.value = resolveDefaultPaymentMethod()
  processError.value = null
  
  try {
    selectedDetail.value = await invoicesService.get(inv.id)
  } catch (err) {
    console.error('Failed to load invoice details:', err)
  }
}

function clearSelection() {
  selected.value = null
  selectedDetail.value = null
  processError.value = null
}

async function moveToNextInvoiceInQueue({ excludeId = null } = {}) {
  const nextInvoice = draftInvoices.value.find((inv) => inv.id !== excludeId) || null
  if (!nextInvoice) {
    clearSelection()
    return
  }

  await selectInvoice(nextInvoice)
}

// ── Process and Print ────────────────────────────────────
async function finalizeSelected({ autoPrint = false } = {}) {
  if (!selected.value) return false

  const processingInvoiceId = selected.value.id

  processing.value = true
  processError.value = null

  try {
    await invoicesService.finalize(processingInvoiceId, paymentMethod.value)
    const finalizedDetail = await invoicesService.get(processingInvoiceId)
    await loadInvoices()

    if (autoPrint) {
      selectedDetail.value = finalizedDetail
      showReceipt.value = true
      advanceAfterPrint.value = true
      await nextTick()
      await printReceipt()
    } else {
      showReceipt.value = false
      selectedDetail.value = null
      await moveToNextInvoiceInQueue({ excludeId: processingInvoiceId })
    }

    return true
  } catch (err) {
    processError.value = err.message
    return false
  } finally {
    processing.value = false
  }
}

// ── Stamp only ───────────────────────────────────────────
async function stampInvoice() {
  await finalizeSelected({ autoPrint: settingsStore.shouldAutoPrintAfterStamp })
}

// ── Stamp and Print ───────────────────────────────────────
async function stampAndPrintInvoice() {
  await finalizeSelected({ autoPrint: true })
}

// ── Print receipt ─────────────────────────────────────────
async function printReceipt() {
  if (!selectedDetail.value?.id || printingReceipt.value) return false

  printingReceipt.value = true
  processError.value = null

  try {
    const result = await invoicesService.printReceipt(selectedDetail.value.id)
    if (!result?.success) {
      throw new Error(result?.error || 'Printer is not available right now.')
    }

    toast.success('Receipt sent to printer.')

    if (advanceAfterPrint.value) {
      await closeReceipt({ autoAdvance: true })
    }
    return true
  } catch (err) {
    const message = err?.message || 'Print failed. Please check printer connection and try again.'
    advanceAfterPrint.value = false
    processError.value = message
    toast.error(message)
    return false
  } finally {
    printingReceipt.value = false
  }
}

// ── Close receipt modal ───────────────────────────────────
async function closeReceipt({ autoAdvance = false } = {}) {
  resetPrintAdvanceHooks()
  showReceipt.value = false
  selectedDetail.value = null
  processError.value = null

  if (autoAdvance || advanceAfterPrint.value) {
    advanceAfterPrint.value = false
    await moveToNextInvoiceInQueue()
    return
  }

  clearSelection()
}

// ── Cancel invoice ───────────────────────────────────────
async function cancelInvoice(inv) {
  if (!inv?.id) {
    toast.error('No invoice selected')
    return
  }
  try {
    await invoicesService.cancel(inv.id, null)
    toast.success('Invoice cancelled!')
    await loadInvoices()
    await moveToNextInvoiceInQueue({ excludeId: inv.id })
  } catch (err) {
    console.error('cancelInvoice error:', err)
    toast.error('Cancel failed: ' + (err.message || String(err)))
  }
}

// ── Return invoice to sender ─────────────────────────────
async function returnInvoice(inv) {
  if (!inv?.id) {
    toast.error('No invoice selected')
    return
  }
  try {
    await invoicesService.returnToSender(inv.id)
    toast.success('Invoice returned to sender!')
    await loadInvoices()
    await moveToNextInvoiceInQueue({ excludeId: inv.id })
  } catch (err) {
    console.error('returnInvoice error:', err)
    toast.error('Return failed: ' + (err.message || String(err)))
  }
}

// ── Helpers ──────────────────────────────────────────────
function fmtDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function fmtCurrency(val) {
  const amount = toAmount(val)
  return `₦${amount.toLocaleString('en-NG', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function statusClass(status) {
  const s = (status || '').toUpperCase()
  if (s === 'DRAFT') return 'draft'
  if (s === 'STAMPED' || s === 'FINALIZED') return 'finalized'
  if (s === 'DISPENSED') return 'dispensed'
  if (s === 'CANCELLED') return 'cancelled'
  return 'draft'
}

function openDispenseWorkspace() {
  router.push('/invoices')
}
</script>

<template>
  <section class="cashier-page">
    <!-- Left: Queue Panel -->
    <aside class="queue-panel">
      <div class="queue-header">
        <div>
          <h2>Invoice Queue</h2>
          <p class="queue-subtext">Fast-payment desk for pending invoices only.</p>
        </div>
        <button class="refresh-btn" @click="loadInvoices" :disabled="loading">
          <span class="material-icons" :class="{ spin: loading }">refresh</span>
        </button>
      </div>

      <div class="queue-tools">
        <div class="queue-search">
          <span class="material-icons">search</span>
          <input
            v-model="queueSearch"
            type="text"
            placeholder="Search by invoice ID, pickup code, amount, payment..."
          />
        </div>
        <div class="queue-filter-tabs">
          <button class="filter-tab" :class="{ active: queueFilter === 'ALL' }" @click="queueFilter = 'ALL'">All Pending</button>
          <button class="filter-tab" :class="{ active: queueFilter === 'DRAFT' }" @click="queueFilter = 'DRAFT'">Pending</button>
        </div>
      </div>

      <div v-if="loading" class="queue-loading">Loading invoices...</div>
      <div v-else-if="error" class="queue-error">{{ error }}</div>

      <div v-else class="queue-list">
        <!-- Draft invoices -->
        <div class="queue-section">
          <div class="section-header">
            <span class="section-dot draft"></span>
            <span class="section-title">Awaiting Payment</span>
            <span class="section-count">{{ filteredDraftInvoices.length }}</span>
          </div>
          <div v-if="filteredDraftInvoices.length === 0" class="queue-empty">No pending invoices</div>
          <button
            v-for="inv in filteredDraftInvoices"
            :key="inv.id"
            class="queue-item"
            :class="{ active: selected?.id === inv.id }"
            @click="selectInvoice(inv)"
          >
            <div class="qi-main">
              <span class="qi-id">#{{ inv.id.slice(0, 8) }}</span>
              <span class="qi-amount">{{ fmtCurrency(inv.total_amount) }}</span>
            </div>
            <div class="qi-meta">
              <span>{{ inv.items?.length ?? 0 }} items</span>
              <span class="qi-code">Code {{ pickupCode(inv.id) }}</span>
              <span>{{ fmtDate(inv.created_at) }}</span>
            </div>
            <p class="qi-from">From {{ inv.sold_by_name || inv.name || 'Unknown staff' }}</p>
            <p v-if="inv.cashier_note" class="qi-note">Cashier note: {{ inv.cashier_note }}</p>
          </button>
        </div>

        <div class="queue-section">
          <div class="section-header">
            <span class="section-dot returned"></span>
            <span class="section-title">Sent Back for Correction</span>
            <span class="section-count">{{ filteredReturnedInvoices.length }}</span>
          </div>
          <div v-if="filteredReturnedInvoices.length === 0" class="queue-empty">No sent-back invoices</div>
          <button
            v-for="inv in filteredReturnedInvoices"
            :key="`${inv.id}-returned`"
            class="queue-item"
            :class="{ active: selected?.id === inv.id }"
            @click="selectInvoice(inv)"
          >
            <div class="qi-main">
              <span class="qi-id">#{{ inv.id.slice(0, 8) }}</span>
              <span class="qi-amount">{{ fmtCurrency(inv.total_amount) }}</span>
            </div>
            <div class="qi-meta">
              <span>{{ inv.items?.length ?? 0 }} items</span>
              <span class="qi-code">Code {{ pickupCode(inv.id) }}</span>
              <span>{{ fmtDate(inv.created_at) }}</span>
            </div>
            <p class="qi-from">From {{ inv.sold_by_name || inv.name || 'Unknown staff' }}</p>
            <p class="qi-note">Correction note: {{ returnedReason(inv.cashier_note) || 'Needs correction' }}</p>
          </button>
        </div>

        <div class="queue-note">
          <p>Once an invoice is stamped, it leaves this queue to prevent clutter.</p>
          <button type="button" class="filter-tab" @click="openDispenseWorkspace">Open Invoices List for Dispense</button>
        </div>
      </div>
    </aside>

    <!-- Right: Digital Invoice View -->
    <main class="invoice-view">
      <template v-if="selected">
        <!-- Invoice Document -->
        <div class="invoice-document" :class="{ compact: isCompactInvoice }">
          <!-- Invoice Header -->
          <header class="inv-header">
            <div class="inv-brand">
              <span class="material-icons brand-icon">local_pharmacy</span>
              <div class="brand-info">
                <h1>Pharmax</h1>
                <p>Sales Invoice</p>
              </div>
            </div>
            <div class="inv-meta">
              <div class="meta-row">
                <span class="meta-label">Invoice #</span>
                <span class="meta-value mono">{{ selected.id.slice(0, 12) }}</span>
              </div>
              <div class="meta-row">
                <span class="meta-label">Date</span>
                <span class="meta-value">{{ fmtDate(selected.created_at) }}</span>
              </div>
              <div class="meta-row">
                <span class="meta-label">Pickup Code</span>
                <span class="meta-value mono">{{ pickupCode(selected.id) }}</span>
              </div>
              <div class="meta-row">
                <span class="meta-label">Status</span>
                <span class="status-tag" :class="statusClass(selected.status)">{{ selected.status }}</span>
              </div>
            </div>
          </header>

          <section v-if="selected.status === 'DRAFT' && selected.cashier_note" class="cashier-note-banner">
            <span class="material-icons">campaign</span>
            <div>
              <strong>Cashier Instruction</strong>
              <p>{{ selected.cashier_note }}</p>
            </div>
          </section>

          <!-- Invoice Items -->
          <section class="inv-items">
            <table v-if="selectedDetail?.items?.length">
              <thead>
                <tr>
                  <th class="col-num">#</th>
                  <th class="col-product">Product</th>
                  <th class="col-unit">Unit</th>
                  <th class="col-qty">Qty</th>
                  <th class="col-price">Price</th>
                  <th class="col-total">Total</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, idx) in selectedDetail.items" :key="item.id">
                  <td class="col-num">{{ idx + 1 }}</td>
                  <td class="col-product">
                    <span class="product-name">{{ item.product?.name || 'Product' }}</span>
                    <span class="product-brand">{{ item.product?.brand_name || '' }}</span>
                  </td>
                  <td class="col-unit">{{ item.product_unit?.name || 'Unit' }}</td>
                  <td class="col-qty mono">{{ item.quantity }}</td>
                  <td class="col-price mono">{{ fmtCurrency(item.unit_price) }}</td>
                  <td class="col-total mono">{{ fmtCurrency(item.line_total) }}</td>
                </tr>
              </tbody>
            </table>
            <div v-else class="items-loading">Loading items...</div>
          </section>

          <!-- Invoice Footer with Totals -->
          <footer class="inv-footer" :class="{ compact: isCompactInvoice }">
            <div class="footer-left">
              <button
                type="button"
                class="btn-cancel"
                @click.prevent.stop="cancelInvoice(selected)"
              >
                <span class="material-icons">close</span>
                Cancel Invoice
              </button>
              <button
                v-if="selected?.status === 'DRAFT' && !selected?.cashier_note?.startsWith('[RETURNED_TO_SENDER]')"
                type="button"
                class="btn-return"
                @click.prevent.stop="returnInvoice(selected)"
              >
                <span class="material-icons">undo</span>
                Send Back
              </button>
            </div>
            <div class="footer-right">
              <div class="totals-box">
                <div class="total-row">
                  <span>Subtotal</span>
                  <span class="mono">{{ fmtCurrency(selected.total_amount) }}</span>
                </div>
                <div class="total-row grand">
                  <span>Total Due</span>
                  <span class="mono">{{ fmtCurrency(selected.total_amount) }}</span>
                </div>
              </div>

              <div v-if="selected.status === 'DRAFT'" class="payment-action-inline">
                <h3>Confirm Payment</h3>

                <div class="payment-methods">
                  <button
                    class="pay-method"
                    :class="{ active: paymentMethod === 'CASH' }"
                    @click="paymentMethod = 'CASH'"
                  >
                    <span class="material-icons">payments</span>
                    <span>Cash</span>
                  </button>
                  <button
                    class="pay-method"
                    :class="{ active: paymentMethod === 'CARD' }"
                    @click="paymentMethod = 'CARD'"
                  >
                    <span class="material-icons">credit_card</span>
                    <span>POS</span>
                  </button>
                  <button
                    class="pay-method"
                    :class="{ active: paymentMethod === 'BANK_TRANSFER' }"
                    @click="paymentMethod = 'BANK_TRANSFER'"
                  >
                    <span class="material-icons">account_balance</span>
                    <span>Transfer</span>
                  </button>
                </div>

                <p v-if="processError" class="payment-error">{{ processError }}</p>

                <div class="payment-buttons">
                  <button class="btn-confirm btn-process" :disabled="processing" @click="stampInvoice">
                    <span class="material-icons">{{ processing ? 'hourglass_empty' : 'approval' }}</span>
                    {{ processing ? 'Stamping...' : 'Stamp' }}
                  </button>
                  <button class="btn-confirm btn-finalize" :disabled="processing" @click="stampAndPrintInvoice">
                    <span class="material-icons">{{ processing ? 'hourglass_empty' : 'print' }}</span>
                    {{ processing ? 'Stamping...' : 'Stamp & Print' }}
                  </button>
                </div>
              </div>

              <div v-else class="payment-done-inline">
                <span class="material-icons">check_circle</span>
                <p>Payment confirmed via <strong>{{ selected.payment_method }}</strong></p>
              </div>
            </div>
          </footer>
        </div>
      </template>

      <!-- Empty state -->
      <div v-else class="empty-view">
        <span class="material-icons">point_of_sale</span>
        <h3>Select an Invoice</h3>
        <p>Choose an invoice from the queue to view details and process payment</p>
      </div>
    </main>

    <!-- Receipt Modal -->
    <div v-if="showReceipt && selectedDetail" class="receipt-modal" @click="closeReceipt">
      <div class="receipt-content" @click.stop>
        <button class="receipt-close" @click="closeReceipt">
          <span class="material-icons">close</span>
        </button>
        
        <div class="receipt">
          <!-- Receipt Header -->
          <div class="receipt-header">
            <span class="material-icons receipt-logo">local_pharmacy</span>
            <h2>Pharmax</h2>
            <p>Pharmacy Management System</p>
            <p class="receipt-date">{{ fmtDate(selectedDetail.created_at) }}</p>
          </div>

          <!-- Receipt Details -->
          <div class="receipt-section">
            <div class="receipt-row">
              <span>Sold By</span>
              <span class="receipt-meta-value">{{ selectedDetail.sold_by_name || '—' }}</span>
            </div>
            <div class="receipt-row">
              <span>Payment Method</span>
              <span class="receipt-meta-value">{{ selectedDetail.payment_method || paymentMethod }}</span>
            </div>
            <div class="receipt-row">
              <span>Invoice #</span>
              <span class="mono receipt-meta-value">{{ selectedDetail.id.slice(0, 12) }}</span>
            </div>
          </div>

          <!-- Receipt Items -->
          <div class="receipt-items">
            <table>
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Qty</th>
                  <th>Price</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in selectedDetail.items" :key="item.id">
                  <td>
                    <div class="receipt-item-name">{{ item.product?.name }}</div>
                    <div class="receipt-item-unit">{{ item.product_unit?.name }}</div>
                  </td>
                  <td class="mono">{{ item.quantity }}</td>
                  <td class="mono">{{ fmtCurrency(item.unit_price) }}</td>
                  <td class="mono">{{ fmtCurrency(item.line_total) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Receipt Total -->
          <div class="receipt-total">
            <div class="receipt-row">
              <span>Subtotal</span>
              <span class="mono">{{ fmtCurrency(selectedReceiptSubtotal) }}</span>
            </div>
            <div class="receipt-row">
              <span>Discount</span>
              <span class="mono">{{ fmtCurrency(selectedReceiptDiscount) }}</span>
            </div>
            <div class="receipt-row">
              <span>Credit</span>
              <span class="mono">{{ fmtCurrency(selectedReceiptCredit) }}</span>
            </div>
            <div class="receipt-row grand">
              <span>TOTAL</span>
              <span class="mono">{{ fmtCurrency(selectedReceiptTotal) }}</span>
            </div>
          </div>

          <!-- Receipt Footer -->
          <div class="receipt-footer">
            <p>Thank you for your patronage!</p>
            <p class="receipt-tagline">Your health is our priority</p>
          </div>
        </div>

        <!-- Print Button -->
        <div class="receipt-actions">
          <button class="btn-print" :disabled="printingReceipt" @click="printReceipt">
            <span class="material-icons">print</span>
            {{ printingReceipt ? 'Printing...' : 'Print Receipt' }}
          </button>
          <button class="btn-done" @click="closeReceipt">
            Done
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.cashier-page {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: var(--space-4);
  height: 100%;
  min-height: 0;
}

@media (max-width: 1000px) {
  .cashier-page {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }
}

/* ── Queue Panel ──────────────────────────────────────────── */
.queue-panel {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-xs);
}

.queue-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px dashed var(--border-subtle);
  background: var(--bg-elevated);
}

.queue-header h2 {
  margin: 0 0 2px;
  font-size: 15px;
  font-weight: 600;
}

.queue-subtext {
  margin: 0;
  font-size: 11px;
  color: var(--text-muted);
}

.queue-tools {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-subtle);
  display: grid;
  gap: 8px;
  background: var(--bg-card);
}

.queue-search {
  height: 34px;
  border: 1px solid var(--border-default);
  border-radius: 10px;
  background: var(--bg-elevated);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 10px;
}

.queue-search .material-icons {
  font-size: 16px;
  color: var(--text-muted);
}

.queue-search input {
  border: none;
  background: transparent;
  outline: none;
  width: 100%;
  color: var(--text-primary);
  font-size: 11px;
}

.queue-filter-tabs {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 6px;
}

.filter-tab {
  height: 30px;
  border: 1px solid var(--border-default);
  border-radius: 10px;
  background: var(--bg-elevated);
  color: var(--text-secondary);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  cursor: pointer;
}

.filter-tab.active {
  border-color: var(--primary);
  background: linear-gradient(90deg, var(--primary-bg) 0%, var(--primary-tint) 100%);
  color: var(--primary);
}

.refresh-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
}

.refresh-btn:hover { background: var(--bg-card); }
.refresh-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.refresh-btn .material-icons { font-size: 18px; }

.queue-loading,
.queue-error {
  padding: 24px;
  text-align: center;
  color: var(--text-muted);
  font-size: 14px;
}

.queue-error { color: var(--error); }

.queue-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* ── Queue Section ────────────────────────────────────────── */
.queue-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 4px;
}

.section-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.section-dot.draft { background: #f59e0b; }
.section-dot.finalized { background: #22c55e; }
.section-dot.returned { background: #f97316; }

.section-title {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
}

.section-count {
  margin-left: auto;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  background: var(--bg-elevated);
  border-radius: 10px;
  color: var(--text-secondary);
}

.queue-empty {
  font-size: 12px;
  color: var(--text-muted);
  text-align: center;
  padding: 16px;
  background: var(--bg-elevated);
  border-radius: 8px;
}

/* ── Queue Item ───────────────────────────────────────────── */
.queue-item {
  width: 100%;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: 10px 12px;
  cursor: pointer;
  text-align: left;
  transition: border-color 0.15s, background 0.15s, transform 0.1s, box-shadow 0.15s;
}

.queue-item:hover {
  border-color: var(--primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.queue-item.active {
  border-color: var(--primary);
  background: linear-gradient(90deg, var(--primary-bg) 0%, var(--primary-tint) 100%);
}

.queue-item.paid {
  border-color: rgba(34, 197, 94, 0.3);
  background: rgba(34, 197, 94, 0.05);
}

.qi-note {
  margin: 8px 0 0;
  font-size: 12px;
  font-weight: 600;
  color: var(--warning);
  background: var(--warning-bg);
  border: 1px solid var(--warning-tint);
  border-radius: 8px;
  padding: 6px 8px;
}

.qi-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.qi-id {
  font-family: var(--font-data);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.qi-amount {
  font-family: var(--font-data);
  font-size: 14px;
  font-weight: 700;
  color: var(--primary);
}

.qi-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(34, 197, 94, 0.15);
  color: #16a34a;
  text-transform: uppercase;
}

.qi-meta {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-muted);
}

.qi-code {
  font-family: var(--font-data);
  font-weight: 600;
}

.qi-from {
  margin: 4px 0 0;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
}

.qi-amount-small {
  font-family: var(--font-data);
  font-weight: 500;
}

.queue-note {
  border: 1px dashed var(--border-default);
  border-radius: 10px;
  padding: 10px;
  display: grid;
  gap: 8px;
  background: var(--bg-recessed);
}

.queue-note p {
  margin: 0;
  font-size: 12px;
  color: var(--text-muted);
}

/* ── Invoice View Panel ───────────────────────────────────── */
.invoice-view {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 0;
}

/* ── Invoice Document ─────────────────────────────────────── */
.invoice-document {
  flex: 1;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.invoice-document.compact {
  flex: 0 0 auto;
}

.invoice-document.compact .inv-items {
  flex: 0 0 auto;
  min-height: 120px;
  max-height: 260px;
}

.inv-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 18px 22px;
  background: linear-gradient(145deg, #0f9f89 0%, #0b8572 54%, #08685b 100%);
  color: white;
}

.inv-brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-icon {
  font-size: 34px;
  opacity: 0.9;
}

.brand-info h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
}

.brand-info p {
  margin: 4px 0 0;
  font-size: 13px;
  opacity: 0.85;
}

.inv-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
}

.meta-label {
  opacity: 0.7;
}

.meta-value {
  font-weight: 500;
}

.meta-value.mono {
  font-family: var(--font-data);
  letter-spacing: 0.02em;
}

.cashier-note-banner {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 18px;
  border-top: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
  background: rgba(245, 158, 11, 0.12);
}

.cashier-note-banner .material-icons {
  font-size: 20px;
  color: #f59e0b;
  margin-top: 2px;
}

.cashier-note-banner strong {
  display: block;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #fbbf24;
}

.cashier-note-banner p {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.45;
}

.status-tag {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 6px;
  text-transform: uppercase;
}

.status-tag.draft {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.status-tag.finalized {
  background: #22c55e;
  color: white;
}

.status-tag.dispensed {
  background: #3b82f6;
  color: white;
}

.status-tag.cancelled {
  background: #ef4444;
  color: white;
}

/* ── Invoice Items Table ──────────────────────────────────── */
.inv-items {
  flex: 1;
  padding: 0;
  overflow-y: auto;
  min-height: 200px;
}

.inv-items table {
  width: 100%;
  border-collapse: collapse;
}

.inv-items thead {
  position: sticky;
  top: 0;
  background: var(--table-header-bg);
  z-index: 1;
}

.inv-items th {
  padding: 10px 12px;
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-subtle);
}

.inv-items td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-subtle);
  vertical-align: middle;
}

.inv-items tr:last-child td {
  border-bottom: none;
}

.inv-items tbody tr:hover td {
  background: var(--table-row-hover);
}

.col-num { width: 50px; text-align: center; }
.col-product { min-width: 200px; }
.col-unit { width: 100px; }
.col-qty { width: 70px; text-align: center; }
.col-price { width: 120px; text-align: right; }
.col-total { width: 120px; text-align: right; }

.inv-items th.col-num,
.inv-items td.col-num { text-align: center; }
.inv-items th.col-qty,
.inv-items td.col-qty { text-align: center; }
.inv-items th.col-price,
.inv-items td.col-price { text-align: right; }
.inv-items th.col-total,
.inv-items td.col-total { text-align: right; }

.product-name {
  display: block;
  font-weight: 500;
  color: var(--text-primary);
}

.product-brand {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.items-loading {
  padding: 40px;
  text-align: center;
  color: var(--text-muted);
}

.mono {
  font-family: var(--font-data);
}

/* ── Invoice Footer ───────────────────────────────────────── */
.inv-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  padding: 14px 18px;
  background: var(--bg-recessed);
  border-top: 1px solid var(--border-subtle);
  gap: 14px;
}

.inv-footer.compact {
  padding: 12px 16px;
  align-items: flex-start;
}

.btn-cancel {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border-radius: 8px;
  border: 1px solid var(--error);
  background: transparent;
  color: var(--error);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-cancel:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.1);
}

.btn-cancel:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-cancel .material-icons {
  font-size: 16px;
}

.btn-return {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border-radius: 8px;
  border: 1px solid var(--warning, #f59e0b);
  background: transparent;
  color: var(--warning, #f59e0b);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-return:hover:not(:disabled) {
  background: rgba(245, 158, 11, 0.1);
}

.btn-return:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-return .material-icons {
  font-size: 16px;
}

.footer-left {
  display: flex;
  gap: 8px;
  position: relative;
  z-index: 2;
  flex-shrink: 0;
}

.footer-right {
  flex: 1 1 360px;
  min-width: 280px;
  max-width: 500px;
  margin-left: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.inv-footer.compact .footer-right {
  gap: 8px;
}

.totals-box {
  min-width: 220px;
  margin-left: auto;
  width: 100%;
  max-width: 300px;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.total-row.grand {
  padding-top: 8px;
  margin-top: 6px;
  border-top: 2px solid var(--border-default);
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
}

.total-row.grand .mono {
  color: var(--primary);
}

/* ── Inline Payment Action Panel ───────────────────────────── */
.payment-action-inline {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 12px;
  box-shadow: var(--shadow-xs);
}

.inv-footer.compact .payment-action-inline {
  padding: 10px;
}

.payment-action-inline h3 {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 600;
}

.payment-methods {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.pay-method {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 8px 6px;
  border-radius: 10px;
  border: 2px solid var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}

.pay-method .material-icons {
  font-size: 18px;
}

.pay-method:hover {
  border-color: var(--text-muted);
}

.pay-method.active {
  border-color: var(--primary);
  background: linear-gradient(90deg, var(--primary-bg) 0%, var(--primary-tint) 100%);
  color: var(--primary);
}

.payment-error {
  margin: 0 0 12px;
  padding: 10px 14px;
  border-radius: 10px;
  background: var(--error-bg);
  color: var(--error);
  font-size: 13px;
}

.payment-buttons {
  display: flex;
  gap: 8px;
}

.btn-confirm {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 10px;
  border: none;
  color: white;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.1s, box-shadow 0.15s;
}

.btn-process {
  background: var(--primary);
}

.btn-finalize {
  background: var(--secondary);
}

.btn-confirm:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.btn-confirm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ── Receipt Modal ─────────────────────────────────────────── */
.receipt-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: grid;
  place-items: center;
  z-index: 1000;
  padding: 20px;
}

.receipt-content {
  background: var(--bg-card);
  border-radius: 16px;
  max-width: 480px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.receipt-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.1);
  color: var(--text-secondary);
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: all 0.15s;
  z-index: 1;
}

.receipt-close:hover {
  background: rgba(0, 0, 0, 0.2);
  color: var(--text-primary);
}

.receipt {
  padding: 40px 32px 24px;
}

.receipt-header {
  text-align: center;
  padding-bottom: 20px;
  border-bottom: 2px dashed var(--border-default);
  margin-bottom: 20px;
  position: relative;
}

.receipt-logo {
  font-size: 48px;
  color: var(--primary);
  margin-bottom: 8px;
}

.receipt-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.receipt-header p {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--text-muted);
}

.receipt-date {
  margin-top: 12px !important;
  font-family: var(--font-data);
  font-size: 12px !important;
}

.receipt-section {
  padding: 16px 0;
  border-bottom: 1px dashed var(--border-default);
  margin-bottom: 16px;
}

.receipt-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 6px 0;
  font-size: 13px;
}

.receipt-meta-value {
  max-width: 62%;
  text-align: right;
  color: var(--text-primary);
  font-weight: 500;
  overflow-wrap: anywhere;
}

.receipt-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  background: var(--success-bg);
  color: var(--success);
  font-weight: 600;
  font-size: 11px;
  text-transform: uppercase;
}

.receipt-items {
  margin-bottom: 16px;
}

.receipt-items table {
  width: 100%;
  border-collapse: collapse;
}

.receipt-items th {
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  padding: 8px 4px;
  border-bottom: 1px solid var(--border-default);
}

.receipt-items td {
  padding: 10px 4px;
  font-size: 13px;
  border-bottom: 1px dashed var(--border-subtle);
}

.receipt-items tr:last-child td {
  border-bottom: none;
}

.receipt-item-name {
  font-weight: 500;
  color: var(--text-primary);
}

.receipt-item-unit {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.receipt-total {
  padding: 16px 0;
  border-top: 2px solid var(--border-default);
}

.receipt-row.grand {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  padding: 8px 0;
}

.receipt-row.grand .mono {
  color: var(--primary);
  font-size: 20px;
}

.receipt-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 2px dashed var(--border-default);
  margin-top: 20px;
}

.receipt-footer p {
  margin: 4px 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.receipt-tagline {
  font-style: italic;
  color: var(--primary) !important;
  font-weight: 500;
}

.receipt-actions {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--border-subtle);
}

.btn-print,
.btn-done {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 44px;
  border-radius: 10px;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-print {
  background: var(--primary);
  color: white;
}

.btn-print:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-print:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-done {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
}

.btn-done:hover {
  background: var(--bg-hover);
}

@media print {
  .receipt-modal {
    background: white;
  }
  
  .receipt-close,
  .receipt-actions {
    display: none;
  }
  
  .receipt-content {
    max-width: 100%;
    box-shadow: none;
  }
}

.btn-confirm .material-icons {
  font-size: 20px;
}

/* ── Inline Payment Done ──────────────────────────────────── */
.payment-done-inline {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  align-self: flex-end;
  padding: 10px 12px;
  border-radius: 8px;
  background: rgba(34, 197, 94, 0.08);
  border: 1px solid rgba(34, 197, 94, 0.25);
  color: #15803d;
}

.payment-done-inline .material-icons {
  font-size: 18px;
}

.payment-done-inline p {
  margin: 0;
  font-size: 13px;
}

@media (max-width: 1000px) {
  .queue-tools {
    grid-template-columns: 1fr;
  }

  .invoice-document.compact .inv-items,
  .inv-items {
    min-height: 160px;
    max-height: none;
  }

  .inv-footer,
  .inv-footer.compact {
    flex-direction: column;
    align-items: stretch;
  }

  .footer-right,
  .totals-box {
    width: 100%;
    max-width: 100%;
  }
}

/* ── Empty State ──────────────────────────────────────────── */
.empty-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: 60px 40px;
  text-align: center;
}

.empty-view .material-icons {
  font-size: 64px;
  color: var(--text-muted);
  opacity: 0.4;
}

.empty-view h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-view p {
  margin: 0;
  font-size: 14px;
  color: var(--text-muted);
  max-width: 280px;
}

/* ── Animations ───────────────────────────────────────────── */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spin {
  animation: spin 0.8s linear infinite;
  display: inline-block;
}
</style>
