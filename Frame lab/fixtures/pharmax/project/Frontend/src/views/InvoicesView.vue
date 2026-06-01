<script setup>
import { ref, computed, onMounted } from 'vue'
import { invoicesService } from '../services/invoices'
import { productsService } from '../services/products'
import { useAuthStore } from '../stores/auth'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'

const auth = useAuthStore()
const toast = useToast()
const { confirm } = useConfirm()

// ── Pagination & data ─────────────────────────────────────
const PAGE_SIZE = 30
const currentPage = ref(1)
const hasMore = ref(false)
const invoices = ref([])
const loading = ref(true)
const error = ref(null)
const cancellingInvoiceId = ref(null)

// ── Filters ───────────────────────────────────────────────
const statusFilter = ref('')

// ── Create/Add Items modal ────────────────────────────────
const showCreate = ref(false)
const activeInvoice = ref(null) // invoice being built
const itemForm = ref({ product_id: '', product_unit_id: '', quantity: 1, unit_price: 0 })
const products = ref([])
const units = ref([])
const itemSaving = ref(false)
const itemError = ref(null)

// ── View Detail modal ─────────────────────────────────────
const showDetail = ref(false)
const detailInv = ref(null)
const detailLoading = ref(false)

// ─────────────────────────────────────────────────────────
onMounted(() => {
  loadPage(1)
  loadProducts()
})

async function loadPage(page) {
  loading.value = true
  error.value = null
  try {
    const data = await invoicesService.list({
      status: statusFilter.value || null,
      limit: PAGE_SIZE,
      offset: (page - 1) * PAGE_SIZE,
    })
    invoices.value = data
    currentPage.value = page
    hasMore.value = data.length === PAGE_SIZE
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function loadProducts() {
  try {
    products.value = await productsService.list({ limit: 1000 })
  } catch (_) {
    products.value = []
  }
}

function onFilterChange() {
  loadPage(1)
}

function pageStart() { return (currentPage.value - 1) * PAGE_SIZE + 1 }
function pageEnd()   { return pageStart() + invoices.value.length - 1 }

// ── Create invoice ────────────────────────────────────────
async function openCreate() {
  itemError.value = null
  try {
    const inv = await invoicesService.create()
    activeInvoice.value = inv
    itemForm.value = { product_id: '', product_unit_id: '', quantity: 1, unit_price: 0 }
    units.value = []
    showCreate.value = true
  } catch (err) {
    toast.error(`Could not start a new invoice. Please try again. (${err.message})`)
  }
}

async function onProductChange() {
  const pid = itemForm.value.product_id
  if (!pid) { units.value = []; itemForm.value.product_unit_id = ''; return }
  try {
    units.value = await productsService.getUnits(pid)
    if (units.value.length > 0) {
      itemForm.value.product_unit_id = units.value[0].id
      itemForm.value.unit_price = units.value[0].price_per_unit
    }
  } catch (_) {
    units.value = []
  }
}

function onUnitChange() {
  const unit = units.value.find(u => u.id === itemForm.value.product_unit_id)
  if (unit) itemForm.value.unit_price = unit.price_per_unit
}

async function addItem() {
  if (!itemForm.value.product_id || !itemForm.value.product_unit_id || itemForm.value.quantity < 1) {
    itemError.value = 'Please select product, unit, and quantity.'
    return
  }
  itemSaving.value = true
  itemError.value = null
  try {
    const updated = await invoicesService.addItem(activeInvoice.value.id, {
      product_id: itemForm.value.product_id,
      product_unit_id: itemForm.value.product_unit_id,
      quantity: itemForm.value.quantity,
      unit_price: itemForm.value.unit_price,
    })
    activeInvoice.value = updated
    itemForm.value = { product_id: '', product_unit_id: '', quantity: 1, unit_price: 0 }
    units.value = []
  } catch (err) {
    itemError.value = err.message
  } finally {
    itemSaving.value = false
  }
}

function finishInvoice() {
  if (!activeInvoice.value.items || activeInvoice.value.items.length === 0) {
    toast.warning('Add at least one product before sending this invoice.')
    return
  }
  showCreate.value = false
  loadPage(currentPage.value)
  activeInvoice.value = null
  toast.success('Invoice saved. You can continue from the list or send it to cashier.')
}

// ── View detail ───────────────────────────────────────────
async function openDetail(inv) {
  detailInv.value = null
  detailLoading.value = true
  showDetail.value = true
  try {
    detailInv.value = await invoicesService.get(inv.id)
  } catch (_) {
    detailInv.value = null
  } finally {
    detailLoading.value = false
  }
}

// ── Status helpers ────────────────────────────────────────
function statusClass(status) {
  const s = String(status || '').toUpperCase()
  if (s === 'DRAFT') return 'draft'
  if (s === 'STAMPED' || s === 'FINALIZED') return 'finalized'
  if (s === 'DISPENSED') return 'dispensed'
  if (s === 'CANCELLED') return 'cancelled'
  return ''
}

function fmtDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function fmtCurrency(val) {
  return new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP' }).format(val ?? 0)
}

// ── Role checks ───────────────────────────────────────────
const canCreate = computed(() => ['ADMIN', 'STAFF', 'CASHIER'].includes(auth.userRole))
const canDispense = computed(() => ['ADMIN', 'STAFF'].includes(auth.userRole))

function canCancelInvoice(inv) {
  const status = String(inv?.status || '').toUpperCase()
  if (auth.userRole === 'STAFF') return status === 'DRAFT'
  return ['ADMIN', 'CASHIER'].includes(auth.userRole) && ['DRAFT', 'STAMPED', 'FINALIZED'].includes(status)
}

// ── Cancel invoice ────────────────────────────────────────
async function cancelInvoice(inv) {
  if (!inv?.id) return
  if (cancellingInvoiceId.value === inv.id) return
  
  const confirmed = await confirm({
    title: 'Cancel Invoice',
    message: `Cancel invoice ${inv.id.slice(0, 8)}? Stock will be restored.`,
    confirmText: 'Cancel Invoice',
    confirmStyle: 'danger',
  })
  if (!confirmed) return
  
  cancellingInvoiceId.value = inv.id
  try {
    await invoicesService.cancel(inv.id, null)
    await loadPage(currentPage.value)
    if (detailInv.value?.id === inv.id) {
      detailInv.value = { ...detailInv.value, status: 'CANCELLED' }
    }
    toast.success('Invoice cancelled and stock was restored.')
  } catch (err) {
    toast.error(`Could not cancel invoice. ${err.message}`)
  } finally {
    cancellingInvoiceId.value = null
  }
}

// ── Dispense invoice ─────────────────────────────────────
async function dispenseInvoice(inv) {
  try {
    await invoicesService.dispense(inv.id)
    loadPage(currentPage.value)
    toast.success('Invoice marked as dispensed.')
  } catch (err) {
    toast.error(`Could not mark as dispensed. ${err.message}`)
  }
}
</script>

<template>
  <section class="invoices-page">

    <!-- Toolbar -->
    <div class="toolbar">
      <div class="filters">
        <select v-model="statusFilter" class="filter-select" @change="onFilterChange">
          <option value="">All Statuses</option>
          <option value="DRAFT">Draft</option>
          <option value="STAMPED">Stamped</option>
          <option value="DISPENSED">Dispensed</option>
          <option value="CANCELLED">Cancelled</option>
        </select>
      </div>
      <button v-if="canCreate" class="btn-primary" @click="openCreate">
        <span class="material-icons">add</span>
        Create Invoice
      </button>
    </div>

    <!-- Loading / error -->
    <p v-if="loading" class="state-msg">Loading invoices…</p>
    <p v-else-if="error" class="state-msg err">{{ error }}</p>

    <!-- Table -->
    <div v-else class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Invoice ID</th>
            <th>Items</th>
            <th class="right">Total</th>
            <th>Payment</th>
            <th>Status</th>
            <th class="center">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="invoices.length === 0">
            <td colspan="7" class="empty">No invoices found.</td>
          </tr>
          <tr v-for="inv in invoices" :key="inv.id">
            <td class="mono sm muted">{{ fmtDate(inv.created_at) }}</td>
            <td class="mono sm muted">{{ inv.id.slice(0, 8) }}</td>
            <td class="center">{{ inv.items?.length ?? 0 }}</td>
            <td class="right mono">{{ fmtCurrency(inv.total_amount) }}</td>
            <td class="sm">
              <span v-if="inv.payment_method" class="payment-badge">{{ inv.payment_method }}</span>
              <span v-else class="muted">—</span>
            </td>
            <td>
              <span class="status-badge" :class="statusClass(inv.status)">{{ inv.status }}</span>
            </td>
            <td class="center actions">
              <button class="icon-btn" title="View detail" @click="openDetail(inv)">
                <span class="material-icons">visibility</span>
              </button>
              <button
                v-if="canDispense && (inv.status === 'STAMPED' || inv.status === 'FINALIZED')"
                class="icon-btn success"
                title="Dispense goods"
                @click="dispenseInvoice(inv)"
              >
                <span class="material-icons">inventory</span>
              </button>
              <button
                v-if="canCancelInvoice(inv)"
                class="icon-btn danger"
                title="Cancel invoice"
                :disabled="cancellingInvoiceId === inv.id"
                @click="cancelInvoice(inv)"
              >
                <span class="material-icons">{{ cancellingInvoiceId === inv.id ? 'hourglass_empty' : 'cancel' }}</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="!loading && !error" class="pagination-bar">
      <span class="page-info">Invoices {{ pageStart() }}–{{ pageEnd() }}{{ hasMore ? '+' : '' }}</span>
      <div class="page-controls">
        <button class="page-btn" :disabled="currentPage === 1 || loading" @click="loadPage(currentPage - 1)">
          <span class="material-icons">chevron_left</span>
        </button>
        <span class="page-num">{{ currentPage }}</span>
        <button class="page-btn" :disabled="!hasMore || loading" @click="loadPage(currentPage + 1)">
          <span class="material-icons">chevron_right</span>
        </button>
      </div>
    </div>

    <!-- ── Create Invoice Modal ── -->
    <Teleport to="body">
      <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false; activeInvoice = null">
        <div class="modal create-modal">
          <div class="modal-head">
            <div>
              <h3>New Invoice</h3>
              <p class="modal-sub">ID: {{ activeInvoice?.id?.slice(0, 8) }}</p>
            </div>
            <button class="icon-btn" @click="showCreate = false; activeInvoice = null">
              <span class="material-icons">close</span>
            </button>
          </div>
          <div class="modal-body">

            <!-- Current items list -->
            <div v-if="activeInvoice?.items?.length" class="items-list">
              <h4 class="items-head">Added Items</h4>
              <div v-for="(item, idx) in activeInvoice.items" :key="item.id" class="item-row">
                <span class="item-idx">{{ idx + 1 }}</span>
                <div class="item-info">
                  <span class="item-name">{{ item.product?.name }}</span>
                  <span class="item-meta">{{ item.quantity }} × {{ item.product_unit?.name }} @ {{ fmtCurrency(item.unit_price) }}</span>
                </div>
                <span class="item-total">{{ fmtCurrency(item.line_total) }}</span>
              </div>
              <div class="items-total">
                <span>Total</span>
                <span class="total-val">{{ fmtCurrency(activeInvoice.total_amount) }}</span>
              </div>
            </div>

            <p v-else class="empty-items">No items added yet.</p>

            <hr class="divider" />

            <!-- Add item form -->
            <h4 class="form-head">Add Item</h4>

            <div class="form-row">
              <label class="form-label">Product</label>
              <select v-model="itemForm.product_id" class="form-input" @change="onProductChange">
                <option value="">Select product…</option>
                <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
              </select>
            </div>

            <div class="form-row">
              <label class="form-label">Unit</label>
              <select v-model="itemForm.product_unit_id" class="form-input" :disabled="!units.length" @change="onUnitChange">
                <option value="">Select unit…</option>
                <option v-for="u in units" :key="u.id" :value="u.id">
                  {{ u.name }} — {{ fmtCurrency(u.price_per_unit) }}
                </option>
              </select>
            </div>

            <div class="form-row-split">
              <div class="form-row">
                <label class="form-label">Quantity</label>
                <input v-model.number="itemForm.quantity" type="number" min="1" class="form-input" />
              </div>
              <div class="form-row">
                <label class="form-label">Unit Price</label>
                <input v-model.number="itemForm.unit_price" type="number" step="0.01" class="form-input" />
              </div>
            </div>

            <p v-if="itemError" class="modal-error">{{ itemError }}</p>

            <button class="btn-outline full-width" :disabled="itemSaving" @click="addItem">
              <span v-if="itemSaving" class="material-icons spin">sync</span>
              <span v-else class="material-icons">add</span>
              {{ itemSaving ? 'Adding…' : 'Add to Invoice' }}
            </button>

            <div class="modal-footer">
              <button type="button" class="btn-outline" @click="showCreate = false; activeInvoice = null">Cancel</button>
              <button class="btn-primary" @click="finishInvoice">
                <span class="material-icons">check</span>
                Finish Invoice
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ── Detail Modal ── -->
    <Teleport to="body">
      <div v-if="showDetail" class="modal-overlay" @click.self="showDetail = false">
        <div class="modal detail-modal">
          <div class="modal-head">
            <div>
              <h3>Invoice Detail</h3>
              <p class="modal-sub">{{ detailInv?.id?.slice(0, 12) }}</p>
            </div>
            <button class="icon-btn" @click="showDetail = false">
              <span class="material-icons">close</span>
            </button>
          </div>
          <div class="modal-body">
            <p v-if="detailLoading" class="state-msg">Loading…</p>
            <template v-else-if="detailInv">

              <!-- Info grid -->
              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">Status</span>
                  <span class="status-badge" :class="statusClass(detailInv.status)">{{ detailInv.status }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Created</span>
                  <span class="info-val">{{ fmtDate(detailInv.created_at) }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Payment</span>
                  <span v-if="detailInv.payment_method" class="payment-badge">{{ detailInv.payment_method }}</span>
                  <span v-else class="info-val muted">—</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Stamped</span>
                  <span class="info-val">{{ fmtDate(detailInv.finalized_at) }}</span>
                </div>
              </div>

              <!-- Items table -->
              <h4 class="detail-head">Line Items</h4>
              <table class="detail-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Product</th>
                    <th>Unit</th>
                    <th class="right">Qty</th>
                    <th class="right">Price</th>
                    <th class="right">Total</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, idx) in detailInv.items" :key="item.id">
                    <td class="mono sm muted">{{ idx + 1 }}</td>
                    <td>{{ item.product?.name }}</td>
                    <td class="sm muted">{{ item.product_unit?.name }}</td>
                    <td class="right mono">{{ item.quantity }}</td>
                    <td class="right mono sm">{{ fmtCurrency(item.unit_price) }}</td>
                    <td class="right mono">{{ fmtCurrency(item.line_total) }}</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td colspan="5" class="right bold">Total</td>
                    <td class="right mono bold">{{ fmtCurrency(detailInv.total_amount) }}</td>
                  </tr>
                </tfoot>
              </table>

            </template>
            <div class="modal-footer">
              <button class="btn-outline" @click="showDetail = false">Close</button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

  </section>
</template>

<style scoped>
.invoices-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

/* ── Toolbar ─────────────────────────────────────────────── */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-select {
  height: 38px;
  padding: 0 32px 0 12px;
  border-radius: 8px;
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-primary);
  font-size: 13px;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23666' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  outline: none;
}

.filter-select:focus { border-color: var(--accent); }

/* ── State msgs ──────────────────────────────────────────── */
.state-msg { font-size: 13px; color: var(--text-muted); margin: 0; }
.state-msg.err { color: var(--error); }

/* ── Table ───────────────────────────────────────────────── */
.table-wrap {
  flex: 1;
  overflow: auto;
  border-radius: 10px;
  border: 1px solid var(--border-subtle);
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

thead { background: var(--bg-elevated); position: sticky; top: 0; z-index: 1; }

th {
  padding: 10px 12px;
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-subtle);
  white-space: nowrap;
}

td {
  padding: 9px 12px;
  border-bottom: 1px solid var(--border-subtle);
  vertical-align: middle;
}

tr:last-child td { border-bottom: none; }
tr:hover td { background: var(--bg-elevated); }

.center { text-align: center; }
.right  { text-align: right; }
.mono   { font-family: var(--font-data); }
.muted  { color: var(--text-muted); }
.sm     { font-size: 12px; }
.bold   { font-weight: 600; }
.empty  { text-align: center; color: var(--text-muted); padding: 32px; }

/* ── Badges ──────────────────────────────────────────────── */
.status-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 12px;
  text-transform: uppercase;
}

.status-badge.draft      { background: rgba(107,114,128,.12); color: #6b7280; }
.status-badge.finalized  { background: rgba(59,130,246,.12);  color: #3b82f6; }
.status-badge.dispensed  { background: rgba(34,197,94,.12);   color: #22c55e; }
.status-badge.cancelled  { background: rgba(239,68,68,.12);   color: var(--error); }

.payment-badge {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 7px;
  border-radius: 10px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  text-transform: uppercase;
}

/* ── Buttons ─────────────────────────────────────────────── */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 38px;
  padding: 0 16px;
  border-radius: 8px;
  border: 0;
  background: var(--accent);
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-outline {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 38px;
  padding: 0 16px;
  border-radius: 8px;
  border: 1px solid var(--border-default);
  background: transparent;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
}

.btn-outline:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline.full-width { width: 100%; justify-content: center; }

.icon-btn {
  width: 30px; height: 30px;
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

.icon-btn .material-icons { font-size: 15px; }
.icon-btn:hover { background: var(--bg-card); }
.icon-btn.success { color: #22c55e; border-color: #22c55e; }
.icon-btn.danger { color: var(--error); border-color: var(--error); }

.actions { display: flex; gap: 4px; justify-content: center; }

/* ── Pagination ──────────────────────────────────────────── */
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 0;
  gap: 10px;
  flex-wrap: wrap;
}

.page-info { font-size: 12px; color: var(--text-muted); font-family: var(--font-data); }

.page-controls { display: flex; align-items: center; gap: 8px; }

.page-num {
  font-size: 13px;
  font-family: var(--font-data);
  color: var(--text-secondary);
  min-width: 20px;
  text-align: center;
}

.page-btn {
  width: 32px; height: 32px;
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

.page-btn:disabled  { opacity: 0.35; cursor: not-allowed; }
.page-btn .material-icons { font-size: 18px; }

/* ── Modal shared ────────────────────────────────────────── */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,.45);
  display: flex; align-items: center; justify-content: center;
  z-index: 100; padding: 16px;
}

.modal {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 14px;
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.create-modal { max-width: 580px; }
.detail-modal { max-width: 640px; }

.modal-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 18px 20px 14px;
  border-bottom: 1px solid var(--border-subtle);
  gap: 12px;
}

.modal-head h3 { margin: 0; font-size: 15px; font-weight: 600; }
.modal-sub { margin: 2px 0 0; font-size: 12px; color: var(--text-muted); font-family: var(--font-data); }

.modal-body {
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* ── Items list ──────────────────────────────────────────── */
.items-list {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.items-head {
  margin: 0 0 6px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
}

.item-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  background: var(--bg-card);
  border-radius: 8px;
}

.item-idx {
  width: 22px; height: 22px;
  border-radius: 50%;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  flex-shrink: 0;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.item-name { font-size: 13px; font-weight: 500; }
.item-meta { font-size: 11px; color: var(--text-muted); }

.item-total {
  font-family: var(--font-data);
  font-weight: 600;
  font-size: 14px;
}

.items-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 8px 2px;
  border-top: 1px solid var(--border-subtle);
  margin-top: 4px;
  font-size: 13px;
  font-weight: 600;
}

.total-val {
  font-family: var(--font-data);
  font-size: 16px;
  color: var(--accent);
}

.empty-items {
  font-size: 13px;
  color: var(--text-muted);
  text-align: center;
  padding: 16px;
  margin: 0;
  background: var(--bg-elevated);
  border-radius: 8px;
}

/* ── Form ────────────────────────────────────────────────── */
.divider {
  border: none;
  border-top: 1px solid var(--border-subtle);
  margin: 8px 0;
}

.form-head {
  margin: 0 0 4px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
}

.form-row { display: flex; flex-direction: column; gap: 6px; }
.form-row-split { display: flex; gap: 10px; }
.form-row-split .form-row { flex: 1; }

.form-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}

.form-input {
  height: 38px;
  padding: 0 12px;
  border-radius: 8px;
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
}

.form-input:focus { border-color: var(--accent); }
.form-input:disabled { opacity: 0.5; cursor: not-allowed; }

select.form-input {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23666' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 32px;
}

.modal-error {
  font-size: 12px;
  color: var(--error);
  margin: 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 6px;
}

/* ── Detail modal ────────────────────────────────────────── */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
}

.info-val {
  font-size: 13px;
  color: var(--text-primary);
}

.detail-head {
  margin: 8px 0 4px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
}

.detail-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.detail-table th {
  padding: 8px 10px;
  text-align: left;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-subtle);
}

.detail-table td {
  padding: 8px 10px;
  border-bottom: 1px solid var(--border-subtle);
}

.detail-table tfoot td {
  padding: 10px 10px 4px;
  border-top: 2px solid var(--border-default);
  border-bottom: none;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

.spin { animation: spin 0.8s linear infinite; display: inline-block; }
</style>
