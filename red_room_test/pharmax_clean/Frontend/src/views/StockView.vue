<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { productsService } from '../services/products'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()

// ── Pagination & data ─────────────────────────────────────
const PAGE_SIZE = 30
const currentPage = ref(1)
const hasMore = ref(false)
const products = ref([])
const loading = ref(true)
const error = ref(null)
const isAdmin = computed(() => auth.userRole === 'ADMIN')

// ── Search ────────────────────────────────────────────────
const search = ref('')
const searchDebounce = ref(null)

// ── Adjust modal ──────────────────────────────────────────
const showAdjust = ref(false)
const adjTarget = ref(null)    // product being adjusted
const adjForm = ref({ change_qty: '', reason: 'MANUAL_ADJUSTMENT', reference: '', note: '' })
const adjSaving = ref(false)
const adjError = ref(null)
const adjInfo = ref(null)

// ── History modal ─────────────────────────────────────────
const showHistory = ref(false)
const histTarget = ref(null)
const histRows = ref([])
const histLoading = ref(false)

// ── Pending approvals (admin) ─────────────────────────────
const pendingRows = ref([])
const pendingLoading = ref(false)
const pendingError = ref(null)
const pendingActionId = ref(null)
const pendingActionError = ref(null)
const pendingActionInfo = ref(null)

// ─────────────────────────────────────────────────────────
onMounted(async () => {
  await loadPage(1)
  if (isAdmin.value) {
    await loadPendingAdjustments()
  }
})

watch(isAdmin, (next) => {
  if (next && pendingRows.value.length === 0) {
    loadPendingAdjustments()
  }
})

async function loadPage(page) {
  loading.value = true
  error.value = null
  try {
    const params = {
      limit: PAGE_SIZE,
      offset: (page - 1) * PAGE_SIZE,
    }
    
    // Smart search - name, brand, generic, SKU
    if (search.value.trim()) {
      params.name = search.value.trim()
    }
    
    const data = await productsService.list(params)
    products.value = data
    currentPage.value = page
    hasMore.value = data.length === PAGE_SIZE
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function onSearch() {
  clearTimeout(searchDebounce.value)
  searchDebounce.value = setTimeout(() => loadPage(1), 300)
}

function pageStart() { return (currentPage.value - 1) * PAGE_SIZE + 1 }
function pageEnd()   { return pageStart() + products.value.length - 1 }

// ── Stock level helpers ───────────────────────────────────
function stockClass(p) {
  if (p.quantity_on_hand === 0) return 'stock-zero'
  if (p.reorder_level > 0 && p.quantity_on_hand <= p.reorder_level) return 'stock-low'
  return 'stock-ok'
}

function stockLabel(p) {
  if (p.quantity_on_hand === 0) return 'Out of stock'
  if (p.reorder_level > 0 && p.quantity_on_hand <= p.reorder_level) return 'Low stock'
  return 'In stock'
}

// ── Summary bar counts ────────────────────────────────────
const outOfStock = computed(() => products.value.filter(p => p.quantity_on_hand === 0).length)
const lowStock   = computed(() => products.value.filter(p =>
  p.quantity_on_hand > 0 && p.reorder_level > 0 && p.quantity_on_hand <= p.reorder_level
).length)

// ── Adjust stock ──────────────────────────────────────────
function openAdjust(product) {
  adjTarget.value = product
  adjForm.value = { change_qty: '', reason: 'MANUAL_ADJUSTMENT', reference: '', note: '' }
  adjError.value = null
  adjInfo.value = null
  showAdjust.value = true
}

async function submitAdjust() {
  const qty = parseInt(adjForm.value.change_qty)
  if (!qty || qty === 0) { adjError.value = 'Enter a non-zero quantity.'; return }
  adjSaving.value = true
  adjError.value = null
  try {
    const result = await productsService.adjustStock(adjTarget.value.id, {
      change_qty: qty,
      reason: adjForm.value.reason,
      reference: adjForm.value.reference || null,
      note: adjForm.value.note || null,
    })
    // Update the product in-place so the table refreshes without a full reload
    const idx = products.value.findIndex(p => p.id === adjTarget.value.id)
    if (idx !== -1) products.value[idx] = result.product
    adjInfo.value = result.adjustment?.status === 'PENDING'
      ? 'Adjustment request submitted. Waiting for admin approval.'
      : 'Stock updated successfully.'
    showAdjust.value = false
    if (isAdmin.value) {
      await loadPendingAdjustments()
    }
  } catch (err) {
    adjError.value = err.message
  } finally {
    adjSaving.value = false
  }
}

// ── Adjustment history ────────────────────────────────────
async function openHistory(product) {
  histTarget.value = product
  histRows.value = []
  histLoading.value = true
  showHistory.value = true
  try {
    histRows.value = await productsService.listAdjustments(product.id, 30)
  } catch (_) {
    histRows.value = []
  } finally {
    histLoading.value = false
  }
}

async function loadPendingAdjustments() {
  pendingLoading.value = true
  pendingError.value = null
  try {
    pendingRows.value = await productsService.listPendingAdjustments(100)
  } catch (err) {
    pendingError.value = err.message
  } finally {
    pendingLoading.value = false
  }
}

function pendingProduct(row) {
  const product = products.value.find((p) => p.id === row.product_id)
  if (!product) return `Product ${row.product_id.slice(0, 8)}…`
  return `${product.name} (${product.sku})`
}

async function reviewPending(row, approve) {
  const actionText = approve ? 'approve' : 'reject'
  const note = window.prompt(`Optional note to ${actionText} this request:`, '')
  if (note === null) return

  pendingActionId.value = row.id
  pendingActionError.value = null
  pendingActionInfo.value = null

  try {
    const result = await productsService.reviewAdjustment(row.product_id, row.id, {
      approve,
      note: note.trim() || null,
    })

    pendingRows.value = pendingRows.value.filter((r) => r.id !== row.id)
    const idx = products.value.findIndex((p) => p.id === result.product.id)
    if (idx !== -1) products.value[idx] = result.product

    pendingActionInfo.value = approve
      ? 'Adjustment approved and stock updated.'
      : 'Adjustment rejected.'
  } catch (err) {
    pendingActionError.value = err.message
  } finally {
    pendingActionId.value = null
  }
}

function fmtDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

// ── Bulk restock ─────────────────────────────────────────
const selected = ref(new Set())
const showBulk = ref(false)
const bulkRows = ref([])
const bulkSaving = ref(false)
const bulkError = ref(null)
const bulkProgress = ref(0)
const bulkInfo = ref(null)

const allSelected = computed(() =>
  products.value.length > 0 && products.value.every(p => selected.value.has(p.id))
)

function toggleSelectAll() {
  if (allSelected.value) {
    selected.value = new Set()
  } else {
    selected.value = new Set(products.value.map(p => p.id))
  }
}

function toggleSelect(id) {
  const next = new Set(selected.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  selected.value = next
}

function openBulkRestock() {
  const selectedProducts = products.value.filter(p => selected.value.has(p.id))
  bulkRows.value = selectedProducts.map(p => ({
    id: p.id,
    name: p.name,
    sku: p.sku,
    current: p.quantity_on_hand,
    reorder: p.reorder_level,
    add_qty: '',
    reference: '',
  }))
  bulkError.value = null
  bulkProgress.value = 0
  bulkInfo.value = null
  showBulk.value = true
}

function bulkFillToReorder() {
  bulkRows.value.forEach(row => {
    if (row.reorder > 0 && row.current < row.reorder) {
      row.add_qty = String(row.reorder - row.current)
    }
  })
}

async function submitBulkRestock() {
  const validRows = bulkRows.value.filter(r => {
    const qty = parseInt(r.add_qty)
    return qty && qty > 0
  })
  if (validRows.length === 0) {
    bulkError.value = 'Enter a restock quantity for at least one product.'
    return
  }

  bulkSaving.value = true
  bulkError.value = null
  bulkProgress.value = 0
  let successCount = 0
  let failCount = 0

  for (const row of validRows) {
    try {
      const result = await productsService.adjustStock(row.id, {
        change_qty: parseInt(row.add_qty),
        reason: 'RESTOCK',
        reference: row.reference || null,
        note: `Bulk restock — ${validRows.length} products`,
      })
      const idx = products.value.findIndex(p => p.id === row.id)
      if (idx !== -1) products.value[idx] = result.product
      successCount++
    } catch {
      failCount++
    }
    bulkProgress.value = Math.round(((successCount + failCount) / validRows.length) * 100)
  }

  bulkSaving.value = false
  if (failCount === 0) {
    showBulk.value = false
    selected.value = new Set()
    bulkInfo.value = `Restocked ${successCount} product${successCount !== 1 ? 's' : ''} successfully.`
  } else {
    bulkError.value = `${successCount} succeeded, ${failCount} failed. Check stock levels and try again.`
  }
}
</script>

<template>
  <section class="stock-page">
    <!-- Toolbar -->
    <div class="toolbar phx-filter-bar">
      <div class="search-wrap">
        <span class="material-icons search-icon">search</span>
        <input
          v-model="search"
          class="search-input"
          placeholder="Search products by name or SKU…"
          @keydown.enter="onSearch"
          @input="search === '' && loadPage(1)"
        />
        <button v-if="search" class="clear-btn" @click="search = ''; loadPage(1)">
          <span class="material-icons">close</span>
        </button>
      </div>
      <div class="summary-chips">
        <span class="chip chip-zero">
          <span class="material-icons">remove_circle_outline</span>
          {{ outOfStock }} out of stock
        </span>
        <span class="chip chip-low">
          <span class="material-icons">warning_amber</span>
          {{ lowStock }} low stock
        </span>
      </div>

      <button
        v-if="selected.size > 0"
        class="btn-primary bulk-restock-btn"
        @click="openBulkRestock"
      >
        <span class="material-icons">inventory_2</span>
        Bulk Restock ({{ selected.size }})
      </button>
    </div>

    <p v-if="adjInfo" class="state-msg ok phx-state phx-state--success">{{ adjInfo }}</p>
    <p v-if="bulkInfo" class="state-msg ok phx-state phx-state--success">{{ bulkInfo }}</p>

    <div v-if="isAdmin" class="pending-panel phx-panel">
      <div class="pending-head">
        <h3>Pending Stock Adjustment Requests</h3>
        <button class="btn-outline" :disabled="pendingLoading" @click="loadPendingAdjustments">
          <span v-if="pendingLoading" class="material-icons spin">sync</span>
          Refresh
        </button>
      </div>

      <p v-if="pendingError" class="state-msg err phx-state phx-state--error">{{ pendingError }}</p>
      <p v-if="pendingActionError" class="state-msg err phx-state phx-state--error">{{ pendingActionError }}</p>
      <p v-if="pendingActionInfo" class="state-msg ok phx-state phx-state--success">{{ pendingActionInfo }}</p>
      <p v-if="pendingLoading" class="state-msg phx-state phx-state--empty">Loading pending requests…</p>
      <p v-else-if="pendingRows.length === 0" class="state-msg phx-state phx-state--empty">No pending approvals.</p>

      <div v-else class="pending-table-wrap phx-table-wrap">
        <table class="pending-table">
          <thead>
            <tr>
              <th>Requested</th>
              <th>Product</th>
              <th class="center">Change</th>
              <th>Reason</th>
              <th>Reference</th>
              <th class="center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in pendingRows" :key="row.id">
              <td class="mono sm">{{ fmtDate(row.created_at) }}</td>
              <td class="sm">{{ pendingProduct(row) }}</td>
              <td class="center">
                <span class="change-badge" :class="row.change_qty >= 0 ? 'pos' : 'neg'">
                  {{ row.change_qty >= 0 ? '+' : '' }}{{ row.change_qty }}
                </span>
              </td>
              <td class="sm muted">{{ row.reason.replaceAll('_', ' ') }}</td>
              <td class="sm muted mono">{{ row.reference ?? '—' }}</td>
              <td class="center pending-actions">
                <button class="btn-primary btn-sm" :disabled="pendingActionId === row.id" @click="reviewPending(row, true)">
                  Approve
                </button>
                <button class="btn-danger btn-sm" :disabled="pendingActionId === row.id" @click="reviewPending(row, false)">
                  Reject
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Loading / error -->
    <p v-if="loading" class="state-msg phx-state phx-state--empty">Loading…</p>
    <p v-else-if="error" class="state-msg err phx-state phx-state--error">{{ error }}</p>

    <!-- Table -->
    <div v-else class="table-wrap phx-table-wrap">
      <table>
        <thead>
          <tr>
            <th class="center chk-col">
              <input type="checkbox" :checked="allSelected" @change="toggleSelectAll" title="Select all" />
            </th>
            <th>SKU</th>
            <th>Product Name</th>
            <th>Supplier</th>
            <th>Type</th>
            <th class="center">On Hand</th>
            <th class="center">Reorder</th>
            <th>Status</th>
            <th class="center">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="products.length === 0">
            <td colspan="9" class="empty phx-empty-cell">No products found.</td>
          </tr>
            <tr
              v-for="p in products"
              :key="p.id"
              :class="['stock-row', stockClass(p), { 'row-warn': p.quantity_on_hand <= p.reorder_level && p.reorder_level > 0, 'row-selected': selected.has(p.id) }]"
            >
            <td class="center chk-col">
              <input type="checkbox" :checked="selected.has(p.id)" @change="toggleSelect(p.id)" />
            </td>
            <td class="mono muted">{{ p.sku }}</td>
            <td class="name-cell">{{ p.name }}</td>
            <td class="muted sm">{{ p.supplier_name ?? '—' }}</td>
            <td>
              <span class="type-badge phx-badge" :class="p.product_type === 'Medical' ? 'medical' : 'nonmedical'">
                {{ p.product_type }}
              </span>
            </td>
            <td class="center">
              <span class="qty-badge" :class="stockClass(p)">{{ p.quantity_on_hand }}</span>
            </td>
            <td class="center mono muted sm">{{ p.reorder_level || '—' }}</td>
            <td>
               <span class="stock-status phx-badge" :class="stockClass(p)">{{ stockLabel(p) }}</span>
            </td>
            <td class="center actions">
              <button class="icon-btn accent" title="Adjust stock" @click="openAdjust(p)">
                <span class="material-icons">tune</span>
              </button>
              <button class="icon-btn" title="View history" @click="openHistory(p)">
                <span class="material-icons">history</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="!loading && !error" class="pagination-bar">
      <span class="page-info">Products {{ pageStart() }}–{{ pageEnd() }}{{ hasMore ? '+' : '' }}</span>
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

    <!-- ── Adjust Stock Modal ── -->
    <Teleport to="body">
      <div v-if="showAdjust" class="modal-overlay phx-modal-overlay" @click.self="showAdjust = false">
        <div class="modal phx-modal">
          <div class="modal-head">
            <div>
              <h3>Adjust Stock</h3>
              <p class="modal-sub">{{ adjTarget?.name }}</p>
            </div>
            <button class="icon-btn" @click="showAdjust = false">
              <span class="material-icons">close</span>
            </button>
          </div>
          <div class="modal-body">

            <!-- Current stock display -->
            <div class="current-stock">
              <span class="cs-label">Current stock</span>
              <span class="cs-qty" :class="stockClass(adjTarget)">{{ adjTarget?.quantity_on_hand }}</span>
            </div>

            <!-- Qty input with +/- quick buttons -->
            <div class="form-row">
              <label class="form-label">Change Quantity <span class="hint">(use negative to remove stock)</span></label>
              <div class="qty-input-row">
                <button type="button" class="qty-step" @click="adjForm.change_qty = String(Number(adjForm.change_qty || 0) - 1)">−</button>
                <input
                  v-model="adjForm.change_qty"
                  type="number"
                  class="form-input qty-input"
                  placeholder="e.g. +50 or -10"
                />
                <button type="button" class="qty-step" @click="adjForm.change_qty = String(Number(adjForm.change_qty || 0) + 1)">+</button>
              </div>
              <p v-if="adjForm.change_qty && !isNaN(Number(adjForm.change_qty))" class="qty-preview">
                New total:
                <strong :class="(adjTarget?.quantity_on_hand ?? 0) + Number(adjForm.change_qty) < 0 ? 'err-text' : 'ok-text'">
                  {{ (adjTarget?.quantity_on_hand ?? 0) + Number(adjForm.change_qty) }}
                </strong>
              </p>
            </div>

            <div class="form-row">
              <label class="form-label">Reference <span class="hint">(optional — e.g. delivery note no.)</span></label>
              <input v-model="adjForm.reference" type="text" class="form-input" placeholder="DN-20240219" />
            </div>

            <div class="form-row">
              <label class="form-label">Note <span class="hint">(optional)</span></label>
              <input v-model="adjForm.note" type="text" class="form-input" placeholder="Damaged units removed…" />
            </div>

            <p v-if="adjError" class="modal-error">{{ adjError }}</p>
            <p v-if="!isAdmin" class="state-msg phx-state phx-state--warning">
              This adjustment will be submitted as a request and needs admin approval.
            </p>

            <div class="modal-footer">
              <button type="button" class="btn-outline" @click="showAdjust = false">Cancel</button>
              <button class="btn-primary" :disabled="adjSaving" @click="submitAdjust">
                <span v-if="adjSaving" class="material-icons spin">sync</span>
                {{ adjSaving ? 'Saving…' : (isAdmin ? 'Apply Adjustment' : 'Submit Request') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ── History Modal ── -->
    <Teleport to="body">
      <div v-if="showHistory" class="modal-overlay phx-modal-overlay" @click.self="showHistory = false">
        <div class="modal phx-modal history-modal">
          <div class="modal-head">
            <div>
              <h3>Adjustment History</h3>
              <p class="modal-sub">{{ histTarget?.name }} · {{ histTarget?.sku }}</p>
            </div>
            <button class="icon-btn" @click="showHistory = false">
              <span class="material-icons">close</span>
            </button>
          </div>
          <div class="modal-body">
            <p v-if="histLoading" class="state-msg phx-state phx-state--empty">Loading…</p>
            <p v-else-if="histRows.length === 0" class="empty-hist">No adjustments recorded yet.</p>
            <table v-else class="hist-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th class="center">Change</th>
                  <th>Status</th>
                  <th>Reason</th>
                  <th>Reference</th>
                  <th>Note</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="h in histRows" :key="h.id">
                  <td class="mono sm">{{ fmtDate(h.created_at) }}</td>
                  <td class="center">
                    <span class="change-badge" :class="h.change_qty >= 0 ? 'pos' : 'neg'">
                      {{ h.change_qty >= 0 ? '+' : '' }}{{ h.change_qty }}
                    </span>
                  </td>
                  <td>
                    <span class="approval-badge" :class="`status-${String(h.status || '').toLowerCase()}`">
                      {{ (h.status ?? 'APPROVED').replaceAll('_', ' ') }}
                    </span>
                  </td>
                  <td class="sm muted">{{ h.reason.replace('_', ' ') }}</td>
                  <td class="sm muted mono">{{ h.reference ?? '—' }}</td>
                  <td class="sm muted">{{ h.note ?? '—' }}</td>
                </tr>
              </tbody>
            </table>
            <div class="modal-footer">
              <button class="btn-outline" @click="showHistory = false">Close</button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ── Bulk Restock Modal ── -->
    <Teleport to="body">
      <div v-if="showBulk" class="modal-overlay phx-modal-overlay" @click.self="showBulk = false">
        <div class="modal phx-modal bulk-modal">
          <div class="modal-head">
            <div>
              <h3>Bulk Restock</h3>
              <p class="modal-sub">{{ bulkRows.length }} product{{ bulkRows.length !== 1 ? 's' : '' }} selected</p>
            </div>
            <button class="icon-btn" @click="showBulk = false">
              <span class="material-icons">close</span>
            </button>
          </div>
          <div class="modal-body">
            <div class="bulk-actions-row">
              <button type="button" class="btn-outline btn-sm" @click="bulkFillToReorder" title="Auto-fill quantities to reach reorder level">
                <span class="material-icons" style="font-size:14px">auto_fix_high</span>
                Fill to reorder level
              </button>
            </div>

            <div class="bulk-table-wrap">
              <table class="bulk-table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th class="center">On Hand</th>
                    <th class="center">Reorder</th>
                    <th class="center">Add Qty</th>
                    <th>Reference</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in bulkRows" :key="row.id" :class="{ 'row-warn': row.current < row.reorder && row.reorder > 0 }">
                    <td class="name-cell">
                      <span>{{ row.name }}</span>
                      <span class="mono muted sm">{{ row.sku }}</span>
                    </td>
                    <td class="center">
                      <span class="qty-badge" :class="row.current === 0 ? 'stock-zero' : row.current <= row.reorder && row.reorder > 0 ? 'stock-low' : 'stock-ok'">
                        {{ row.current }}
                      </span>
                    </td>
                    <td class="center mono muted">{{ row.reorder || '—' }}</td>
                    <td class="center">
                      <input
                        v-model="row.add_qty"
                        type="number"
                        min="0"
                        class="form-input bulk-qty-input"
                        placeholder="0"
                      />
                    </td>
                    <td>
                      <input
                        v-model="row.reference"
                        type="text"
                        class="form-input bulk-ref-input"
                        placeholder="DN-…"
                      />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div v-if="bulkSaving" class="bulk-progress">
              <div class="bulk-progress-bar">
                <div class="bulk-progress-fill" :style="{ width: bulkProgress + '%' }" />
              </div>
              <span class="sm muted">{{ bulkProgress }}%</span>
            </div>

            <p v-if="bulkError" class="modal-error">{{ bulkError }}</p>

            <div class="modal-footer">
              <button type="button" class="btn-outline" @click="showBulk = false">Cancel</button>
              <button class="btn-primary" :disabled="bulkSaving" @click="submitBulkRestock">
                <span v-if="bulkSaving" class="material-icons spin">sync</span>
                {{ bulkSaving ? 'Restocking…' : 'Apply Restock' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

  </section>
</template>

<style scoped>
.stock-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

/* ── Toolbar ─────────────────────────────────────────────── */
.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.search-wrap {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 200px;
  max-width: 360px;
}

.search-icon {
  position: absolute;
  left: 10px;
  font-size: 18px;
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  height: 38px;
  padding: 0 34px 0 36px;
  border-radius: 8px;
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
}

.search-input:focus { border-color: var(--accent); }

.clear-btn {
  position: absolute;
  right: 6px;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 2px;
}

.clear-btn .material-icons { font-size: 16px; }

.summary-chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 20px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-elevated);
}

.chip .material-icons { font-size: 14px; }
.chip-zero { color: var(--error); border-color: var(--error); }
.chip-low  { color: var(--warning); border-color: var(--warning); }

/* ── State msgs ──────────────────────────────────────────── */
.state-msg { font-size: 13px; color: var(--text-muted); margin: 0; }
.state-msg.err { color: var(--error); }
.state-msg.ok { color: var(--success); }

/* ── Pending approvals panel ─────────────────────────────── */
.pending-panel {
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  background: var(--bg-elevated);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pending-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.pending-head h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.pending-table-wrap {
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  overflow: auto;
  background: var(--bg-card);
}

.pending-table { width: 100%; border-collapse: collapse; }
.pending-actions { display: inline-flex; gap: 8px; }

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

.row-warn td { background: var(--warning-bg); }
.row-warn:hover td { background: var(--warning-tint); }

.center { text-align: center; }
.mono   { font-family: var(--font-data); }
.muted  { color: var(--text-muted); }
.sm     { font-size: 12px; }
.name-cell { font-weight: 500; max-width: 280px; }
.empty  { text-align: center; color: var(--text-muted); padding: 32px; }

/* ── Badges ──────────────────────────────────────────────── */
.qty-badge {
  display: inline-block;
  font-family: var(--font-data);
  font-weight: 600;
  font-size: 14px;
  min-width: 36px;
  text-align: center;
}

.qty-badge.stock-ok   { color: var(--success); }
.qty-badge.stock-low  { color: var(--warning); }
.qty-badge.stock-zero { color: var(--error); }

.stock-status {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
}

.stock-status.stock-ok   { background: var(--success-bg); color: var(--success); }
.stock-status.stock-low  { background: var(--warning-bg); color: var(--warning); }
.stock-status.stock-zero { background: var(--error-bg); color: var(--error); }

.type-badge {
  font-size: 11px;
  padding: 2px 7px;
  border-radius: 10px;
  font-weight: 500;
}

.type-badge.medical    { background: var(--info-bg); color: var(--info); }
.type-badge.nonmedical { background: var(--bg-elevated);   color: var(--text-muted); border: 1px solid var(--border-subtle); }

/* ── Action buttons ──────────────────────────────────────── */
.actions { display: flex; gap: 4px; justify-content: center; }

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
.icon-btn.accent { color: var(--accent); border-color: var(--accent); }
.icon-btn:hover  { background: var(--bg-card); }

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
  background: var(--overlay-bg);
  display: flex; align-items: center; justify-content: center;
  z-index: 100; padding: 16px;
}

.modal {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 14px;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-modal { max-width: 620px; }

.modal-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 18px 20px 14px;
  border-bottom: 1px solid var(--border-subtle);
  gap: 12px;
}

.modal-head h3 { margin: 0; font-size: 15px; font-weight: 600; }
.modal-sub { margin: 2px 0 0; font-size: 12px; color: var(--text-muted); }

.modal-body {
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-row { display: flex; flex-direction: column; gap: 6px; }

.form-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.hint { font-weight: 400; text-transform: none; letter-spacing: 0; color: var(--text-muted); }

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

/* ── Current stock display ───────────────────────────────── */
.current-stock {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
}

.cs-label { font-size: 12px; color: var(--text-muted); }

.cs-qty {
  font-family: var(--font-data);
  font-size: 28px;
  font-weight: 700;
}

.cs-qty.stock-ok   { color: var(--success); }
.cs-qty.stock-low  { color: var(--warning); }
.cs-qty.stock-zero { color: var(--error); }

/* ── Qty input row ───────────────────────────────────────── */
.qty-input-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.qty-step {
  width: 36px; height: 38px;
  border-radius: 8px;
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-primary);
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.qty-step:hover { border-color: var(--accent); color: var(--accent); }

.qty-input { flex: 1; text-align: center; font-family: var(--font-data); font-size: 16px; }

.qty-preview {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0;
}

.ok-text  { color: var(--success); }
.err-text { color: var(--error); }

/* ── History table ───────────────────────────────────────── */
.hist-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.hist-table th {
  padding: 8px 10px;
  text-align: left;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-subtle);
}

.hist-table td {
  padding: 8px 10px;
  border-bottom: 1px solid var(--border-subtle);
  vertical-align: middle;
}

.hist-table tr:last-child td { border-bottom: none; }

.change-badge {
  font-family: var(--font-data);
  font-weight: 700;
  font-size: 13px;
  padding: 2px 8px;
  border-radius: 10px;
}

.change-badge.pos { background: var(--success-bg); color: var(--success); }
.change-badge.neg { background: var(--error-bg);  color: var(--error); }

.approval-badge {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  border-radius: 999px;
  padding: 2px 8px;
  border: 1px solid transparent;
}

.approval-badge.status-pending {
  color: var(--warning);
  background: var(--warning-bg);
  border-color: var(--warning-tint);
}

.approval-badge.status-approved {
  color: var(--success);
  background: var(--success-bg);
  border-color: var(--success-tint);
}

.approval-badge.status-rejected {
  color: var(--error);
  background: var(--error-bg);
  border-color: var(--error-tint);
}

.empty-hist { font-size: 13px; color: var(--text-muted); text-align: center; margin: 16px 0; }

/* ── Modal footer ────────────────────────────────────────── */
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
}

.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-danger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 38px;
  padding: 0 16px;
  border-radius: 8px;
  border: 1px solid var(--error-tint);
  background: var(--error-bg);
  color: var(--error);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.btn-sm {
  height: 30px;
  padding: 0 12px;
  font-size: 12px;
}

.btn-danger:disabled,
.btn-primary.btn-sm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.stock-page {
  gap: var(--space-4);
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
  max-width: 340px;
  font-size: 13px;
  color: var(--text-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-recessed);
  padding: var(--space-3);
}

.toolbar {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
  padding: var(--space-4);
  gap: var(--space-3);
}

.search-input {
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
}

.clear-btn {
  border-radius: var(--radius-full);
}

.clear-btn:hover {
  background: var(--bg-hover);
}

.summary-chips {
  margin-left: auto;
}

.chip {
  padding: 5px 12px;
  border-radius: var(--radius-full);
  background: var(--bg-recessed);
}

.chip-zero {
  color: var(--error);
  background: var(--error-bg);
  border-color: var(--error-tint);
}

.chip-low {
  color: var(--warning);
  background: var(--warning-bg);
  border-color: var(--warning-tint);
}

.pending-panel {
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
  padding: var(--space-4);
}

.pending-head h3 {
  font-size: 16px;
}

.pending-table-wrap {
  border-radius: var(--radius-lg);
}

.table-wrap {
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
}

thead {
  background: var(--table-header-bg);
}

th {
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

.stock-row.stock-low td:first-child {
  box-shadow: inset 3px 0 0 var(--warning);
}

.stock-row.stock-zero td:first-child {
  box-shadow: inset 3px 0 0 var(--error);
}

.qty-badge {
  border-radius: var(--radius-full);
  border: 1px solid transparent;
  min-width: 44px;
  padding: 4px 10px;
}

.qty-badge.stock-ok {
  background: var(--success-bg);
  border-color: var(--success-tint);
}

.qty-badge.stock-low {
  background: var(--warning-bg);
  border-color: var(--warning-tint);
}

.qty-badge.stock-zero {
  background: var(--error-bg);
  border-color: var(--error-tint);
}

.stock-status {
  border: 1px solid transparent;
  border-radius: var(--radius-full);
  padding: 3px 9px;
}

.stock-status.stock-ok {
  border-color: var(--success-tint);
}

.stock-status.stock-low {
  border-color: var(--warning-tint);
}

.stock-status.stock-zero {
  border-color: var(--error-tint);
}

.icon-btn {
  border-radius: var(--radius-md);
  background: var(--bg-card);
}

.icon-btn:hover {
  background: var(--bg-hover);
  border-color: var(--border-strong);
}

.pagination-bar {
  padding-top: var(--space-2);
}

.page-btn {
  border-radius: var(--radius-md);
}

.modal-overlay {
  background: var(--overlay-bg);
}

.modal {
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
}

.modal-head {
  padding: var(--space-5) var(--space-5) var(--space-4);
}

.modal-body {
  padding: var(--space-5);
}

.form-input,
.qty-step,
.btn-primary,
.btn-outline,
.btn-danger {
  border-radius: var(--radius-md);
}

.btn-primary {
  background: var(--primary);
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-outline:hover:not(:disabled) {
  background: var(--bg-hover);
}

@media (max-width: 980px) {
  .page-hero {
    padding: var(--space-4);
  }

  .hero-tip {
    max-width: none;
    width: 100%;
  }

  .toolbar {
    align-items: stretch;
  }

  .search-wrap {
    max-width: none;
  }

  .summary-chips {
    margin-left: 0;
  }
}

/* ── Checkbox column ────────────────────────────────────── */
.chk-col { width: 40px; }
.chk-col input[type="checkbox"] { cursor: pointer; width: 16px; height: 16px; accent-color: var(--primary); }

.row-selected td { background: var(--primary-tint) !important; }

/* ── Bulk restock button ───────────────────────────────── */
.bulk-restock-btn {
  white-space: nowrap;
}

.bulk-restock-btn .material-icons { font-size: 16px; }

/* ── Bulk modal ────────────────────────────────────────── */
.bulk-modal { max-width: 720px; }

.bulk-actions-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.bulk-table-wrap {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: auto;
  max-height: 400px;
}

.bulk-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.bulk-table th {
  padding: 8px 10px;
  text-align: left;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-subtle);
  background: var(--table-header-bg);
  position: sticky;
  top: 0;
  z-index: 1;
}

.bulk-table td {
  padding: 8px 10px;
  border-bottom: 1px solid var(--border-subtle);
  vertical-align: middle;
}

.bulk-table .name-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-width: 220px;
}

.bulk-qty-input {
  width: 80px;
  text-align: center;
  font-family: var(--font-data);
  font-size: 14px;
  font-weight: 600;
}

.bulk-ref-input {
  width: 120px;
  font-size: 12px;
}

.bulk-progress {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bulk-progress-bar {
  flex: 1;
  height: 6px;
  background: var(--bg-recessed);
  border-radius: 999px;
  overflow: hidden;
}

.bulk-progress-fill {
  height: 100%;
  background: var(--primary);
  border-radius: 999px;
  transition: width 0.3s ease;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

.spin { animation: spin 0.8s linear infinite; display: inline-block; }
</style>
