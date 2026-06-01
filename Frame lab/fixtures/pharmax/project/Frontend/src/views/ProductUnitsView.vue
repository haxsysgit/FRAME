<script setup>
import { ref, computed, onMounted } from 'vue'
import { productsService } from '../services/products'
import { useCurrency } from '@/composables/useCurrency'

const rows = ref([])          // flat list: { product, unit }
const { formatSimple, symbol: currencySymbol } = useCurrency()
const ROW_INTERACTIVE_SELECTOR = 'button, input, select, textarea, a, [role="button"], [role="link"], [contenteditable="true"]'

const selectedUnitRows = computed(() => (
  rows.value.filter((row) => row.unit && selectedUnitIds.value.has(row.unit.id))
))

function isUnitSelected(unitId) {
  return selectedUnitIds.value.has(unitId)
}

function toggleUnitSelection(unitId) {
  if (!unitId) return
  const next = new Set(selectedUnitIds.value)
  if (next.has(unitId)) {
    next.delete(unitId)
  } else {
    next.add(unitId)
  }
  selectedUnitIds.value = next
}

function toggleSelectAllVisible() {
  const visibleIds = filtered.value
    .filter((row) => row.unit)
    .map((row) => row.unit.id)
  if (!visibleIds.length) return

  const next = new Set(selectedUnitIds.value)
  const allSelected = visibleIds.every((id) => next.has(id))
  if (allSelected) {
    visibleIds.forEach((id) => next.delete(id))
  } else {
    visibleIds.forEach((id) => next.add(id))
  }
  selectedUnitIds.value = next
}

function shouldSkipRowSelection(event) {
  const target = event?.target
  return target instanceof Element && Boolean(target.closest(ROW_INTERACTIVE_SELECTOR))
}

function handleUnitRowDoubleClick(event, row) {
  if (!row?.unit || shouldSkipRowSelection(event)) return
  toggleUnitSelection(row.unit.id)
}

function openBulkEditModal() {
  if (selectedUnitRows.value.length === 0) {
    bulkError.value = 'Select at least one unit row to edit in bulk.'
    return
  }

  bulkError.value = null
  bulkForm.value = { price_per_unit: '', quantity_in_base: '' }
  showBulkEditModal.value = true
}

async function submitBulkEdit() {
  if (selectedUnitRows.value.length === 0) {
    bulkError.value = 'No selected rows.'
    return
  }

  const hasPrice = String(bulkForm.value.price_per_unit || '').trim() !== ''
  const hasMultiplier = String(bulkForm.value.quantity_in_base || '').trim() !== ''
  if (!hasPrice && !hasMultiplier) {
    bulkError.value = 'Enter at least one value to update.'
    return
  }

  bulkSaving.value = true
  bulkError.value = null

  try {
    const payload = {}
    if (hasPrice) payload.price_per_unit = parseFloat(bulkForm.value.price_per_unit)
    if (hasMultiplier) {
      payload.multiplier_to_base = parsePositiveInteger(
        bulkForm.value.quantity_in_base,
        'Quantity in base unit',
      )
    }

    const updates = selectedUnitRows.value.map((row) => (
      productsService.updateUnit(row.product.id, row.unit.id, payload)
    ))
    const results = await Promise.all(updates)

    results.forEach((updatedUnit) => {
      const row = rows.value.find((r) => r.unit?.id === updatedUnit.id)
      if (row) row.unit = updatedUnit
    })

    showBulkEditModal.value = false
    selectedUnitIds.value = new Set()
  } catch (err) {
    bulkError.value = err.message || 'Bulk update failed.'
  } finally {
    bulkSaving.value = false
  }
}
const loading = ref(true)
const error = ref(null)
const search = ref('')
const saving = ref(null)      // unit id being saved
const saveError = ref(null)

// Pagination
const PAGE_SIZE = 100
const currentPage = ref(1)
const hasMore = ref(false)

// edit state: { unitId -> { price, multiplier } }
const edits = ref({})

const BASE_UNITS = ['Pack', 'Strip', 'Tablet', 'Capsule', 'Bottle', 'Sachet', 'Tube', 'Vial', 'Ampoule', 'Unit']

// Add-unit modal
const showAddModal = ref(false)
const addTarget = ref(null)   // product being operated on
const addForm = ref({ name: 'Pack', price_per_unit: '', quantity_in_base: 1 })
const addSaving = ref(false)
const addError = ref(null)
const selectedUnitIds = ref(new Set())
const showBulkEditModal = ref(false)
const bulkForm = ref({
  price_per_unit: '',
  quantity_in_base: '',
})
const bulkSaving = ref(false)
const bulkError = ref(null)

onMounted(() => loadPage(1))

async function loadPage(page) {
  loading.value = true
  error.value = null
  edits.value = {}
  selectedUnitIds.value = new Set()
  try {
    const products = await productsService.list({
      limit: PAGE_SIZE,
      offset: (page - 1) * PAGE_SIZE,
    })
    const flat = []
    for (const p of products) {
      if (p.product_units && p.product_units.length > 0) {
        for (const u of p.product_units) flat.push({ product: p, unit: u })
      } else {
        flat.push({ product: p, unit: null })
      }
    }
    rows.value = flat
    currentPage.value = page
    hasMore.value = products.length === PAGE_SIZE
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const filtered = computed(() => {
  if (!search.value.trim()) return rows.value
  const q = search.value.toLowerCase()
  return rows.value.filter(
    (r) =>
      r.product.name.toLowerCase().includes(q) ||
      r.product.sku.toLowerCase().includes(q) ||
      (r.product.generic_name ?? '').toLowerCase().includes(q),
  )
})

function pageStart() { return (currentPage.value - 1) * PAGE_SIZE + 1 }
function pageEnd()   { return pageStart() + rows.value.length - 1 }

function stockClass(qty, reorder) {
  if (qty === 0) return 'stock-zero'
  if (reorder > 0 && qty <= reorder) return 'stock-low'
  return 'stock-ok'
}

function formatUnitPrice(value) {
  return formatSimple(value, 0)
}

function parsePositiveInteger(value, label) {
  const parsed = Number.parseInt(String(value), 10)
  if (!Number.isFinite(parsed) || parsed < 1) {
    throw new Error(`${label} must be a whole number of at least 1.`)
  }
  return parsed
}

// ── Inline edit ──────────────────────────────────────────
function startEdit(unit) {
  edits.value[unit.id] = {
    price: unit.price_per_unit,
    multiplier: unit.multiplier_to_base,
  }
}

function cancelEdit(unitId) {
  delete edits.value[unitId]
}

async function saveEdit(productId, unitId, baseUnit) {
  const e = edits.value[unitId]
  if (!e) return
  saving.value = unitId
  saveError.value = null
  try {
    const updated = await productsService.updateUnit(productId, unitId, {
      price_per_unit: parseFloat(e.price),
      multiplier_to_base: parsePositiveInteger(e.multiplier, `Quantity in ${baseUnit || 'base unit'}`),
    })
    // Update in-place
    const row = rows.value.find((r) => r.unit?.id === unitId)
    if (row) row.unit = updated
    delete edits.value[unitId]
  } catch (err) {
    saveError.value = err.message
  } finally {
    saving.value = null
  }
}

// ── Add unit modal ────────────────────────────────────────
function openAddUnit(product) {
  addTarget.value = product
  addForm.value = { name: 'Pack', price_per_unit: '', quantity_in_base: 1 }
  addError.value = null
  showAddModal.value = true
}

async function submitAddUnit() {
  addSaving.value = true
  addError.value = null
  try {
    const baseUnit = addTarget.value?.base_unit || 'base unit'
    const unit = await productsService.addUnit(addTarget.value.id, {
      name: addForm.value.name,
      price_per_unit: parseFloat(addForm.value.price_per_unit),
      multiplier_to_base: parsePositiveInteger(addForm.value.quantity_in_base, `Quantity in ${baseUnit}`),
    })
    rows.value.push({ product: addTarget.value, unit })
    showAddModal.value = false
  } catch (err) {
    addError.value = err.message
  } finally {
    addSaving.value = false
  }
}
</script>

<template>
  <section class="units-page">
    <!-- Toolbar -->
    <div class="toolbar phx-filter-bar">
      <div class="search-wrap">
        <span class="material-icons search-icon">search</span>
        <input v-model="search" class="search-input" type="text" placeholder="Search product name, SKU or generic…" />
      </div>
      <button class="btn-bulk" :class="{ 'btn-bulk-active': selectedUnitRows.length > 0 }" type="button" @click="openBulkEditModal">
        Bulk Edit ({{ selectedUnitRows.length }})
      </button>
      <span class="hint">{{ filtered.length.toLocaleString() }} rows shown</span>
    </div>

    <p v-if="loading" class="state-msg phx-state phx-state--empty">Loading units…</p>
    <p v-else-if="error" class="state-msg error phx-state phx-state--error">{{ error }}</p>

    <div v-else class="table-wrap phx-table-wrap">
      <table>
        <thead>
          <tr>
            <th class="center">
              <input
                type="checkbox"
                :checked="filtered.filter((r) => r.unit).length > 0 && filtered.filter((r) => r.unit).every((r) => isUnitSelected(r.unit.id))"
                @change="toggleSelectAllVisible"
                aria-label="Select all visible units"
              />
            </th>
            <th>SKU</th>
            <th>Product Name</th>
            <th>Generic Name</th>
            <th>Unit Name</th>
            <th class="num">Price ({{ currencySymbol }})</th>
            <th class="num">Qty in Base</th>
            <th class="num">Stock</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filtered.length === 0">
            <td colspan="9" class="empty-row phx-empty-cell">No units found.</td>
          </tr>

          <template v-for="r in filtered" :key="(r.unit?.id ?? r.product.id)">
            <tr
              :class="[
                'unit-row',
                stockClass(r.product.quantity_on_hand, r.product.reorder_level),
                {
                  editing: edits[r.unit?.id],
                  'row-selected': r.unit && isUnitSelected(r.unit.id),
                },
              ]"
              @dblclick="handleUnitRowDoubleClick($event, r)"
            >
              <td class="center">
                <input
                  v-if="r.unit"
                  type="checkbox"
                  :checked="isUnitSelected(r.unit.id)"
                  @change="toggleUnitSelection(r.unit.id)"
                />
              </td>
              <td class="mono sku">{{ r.product.sku }}</td>
              <td class="name-cell">{{ r.product.name }}</td>
              <td class="generic">{{ r.product.generic_name || '—' }}</td>

              <!-- No unit row -->
              <template v-if="!r.unit">
                <td colspan="4" class="muted no-unit">No unit set up yet</td>
                <td class="actions">
                  <button class="icon-btn" title="Add unit" @click="openAddUnit(r.product)">
                    <span class="material-icons">add</span>
                  </button>
                </td>
              </template>

              <!-- Unit row — view mode -->
              <template v-else-if="!edits[r.unit.id]">
                <td class="unit-name">
                  <span class="unit-badge phx-badge">{{ r.unit.name }}</span>
                </td>
                <td class="num mono">{{ formatUnitPrice(r.unit.price_per_unit) }}</td>
                <td class="num mono muted">× {{ r.unit.multiplier_to_base }} {{ r.product.base_unit }}</td>
                <td class="num mono">
                  <span class="stock-pill" :class="stockClass(r.product.quantity_on_hand, r.product.reorder_level)">
                    {{ r.product.quantity_on_hand }}
                  </span>
                </td>
                <td class="actions">
                  <button class="icon-btn" title="Edit price" @click="startEdit(r.unit)">
                    <span class="material-icons">edit</span>
                  </button>
                  <button class="icon-btn" title="Add another unit" @click="openAddUnit(r.product)">
                    <span class="material-icons">add</span>
                  </button>
                </td>
              </template>

              <!-- Unit row — edit mode -->
              <template v-else>
                <td class="unit-name">
                  <span class="unit-badge phx-badge">{{ r.unit.name }}</span>
                </td>
                <td class="num">
                  <input
                    v-model="edits[r.unit.id].price"
                    class="inline-input"
                    type="number"
                    min="0"
                    step="100"
                  />
                </td>
                <td class="num">
                  <input
                    v-model="edits[r.unit.id].multiplier"
                    class="inline-input"
                    type="number"
                    min="1"
                    step="1"
                    :title="'Quantity in ' + (r.product.base_unit || 'base unit')"
                  />
                </td>
                <td class="num mono">
                  <span class="stock-pill" :class="stockClass(r.product.quantity_on_hand, r.product.reorder_level)">
                    {{ r.product.quantity_on_hand }}
                  </span>
                </td>
                <td class="actions">
                  <button
                    class="icon-btn accent"
                    title="Save"
                    :disabled="saving === r.unit.id"
                    @click="saveEdit(r.product.id, r.unit.id, r.product.base_unit)"
                  >
                    <span class="material-icons">{{ saving === r.unit.id ? 'hourglass_empty' : 'check' }}</span>
                  </button>
                  <button class="icon-btn" title="Cancel" @click="cancelEdit(r.unit.id)">
                    <span class="material-icons">close</span>
                  </button>
                </td>
              </template>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Pagination bar -->
    <div class="pagination-bar">
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

    <p v-if="saveError" class="save-error">{{ saveError }}</p>

    <!-- Add Unit Modal -->
    <Teleport to="body">
      <div v-if="showAddModal" class="modal-overlay phx-modal-overlay" @click.self="showAddModal = false">
        <div class="modal phx-modal">
          <div class="modal-head">
            <h3>Add Unit — {{ addTarget?.name }}</h3>
            <button class="icon-btn" @click="showAddModal = false">
              <span class="material-icons">close</span>
            </button>
          </div>
          <form class="modal-body" @submit.prevent="submitAddUnit">
            <div class="form-grid">
              <label class="field">
                <span>Unit Name *</span>
                <select v-model="addForm.name" required>
                  <option v-for="u in BASE_UNITS" :key="u" :value="u">{{ u }}</option>
                </select>
              </label>
              <label class="field">
                <span>Price per Unit ({{ currencySymbol }}) *</span>
                <input v-model="addForm.price_per_unit" type="number" min="0" step="100" required placeholder="0" />
              </label>
              <label class="field">
                <span class="label-with-tip">
                  Quantity in {{ addTarget?.base_unit || 'Base Unit' }}
                  <span class="material-icons tooltip-icon" title="How many base units are contained in this unit">info</span>
                </span>
                <input v-model="addForm.quantity_in_base" type="number" min="1" step="1" placeholder="1" />
              </label>
            </div>
            <p v-if="addError" class="modal-error">{{ addError }}</p>
            <div class="modal-footer">
              <button type="button" class="btn-outline" @click="showAddModal = false">Cancel</button>
              <button type="submit" class="btn-primary" :disabled="addSaving">
                {{ addSaving ? 'Adding…' : 'Add Unit' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Bulk Edit Modal -->
    <Teleport to="body">
      <div v-if="showBulkEditModal" class="modal-overlay phx-modal-overlay" @click.self="showBulkEditModal = false">
        <div class="modal phx-modal">
          <div class="modal-head">
            <h3>Bulk Edit Units ({{ selectedUnitRows.length }})</h3>
            <button class="icon-btn" @click="showBulkEditModal = false">
              <span class="material-icons">close</span>
            </button>
          </div>
          <form class="modal-body" @submit.prevent="submitBulkEdit">
            <div class="form-grid">
              <label class="field">
                <span>New Price per Unit ({{ currencySymbol }})</span>
                <input v-model="bulkForm.price_per_unit" type="number" min="0" step="100" placeholder="Leave blank to keep" />
              </label>
              <label class="field">
                <span class="label-with-tip">
                  Quantity in Base Unit
                  <span class="material-icons tooltip-icon" title="How many base units are contained in this unit">info</span>
                </span>
                <input v-model="bulkForm.quantity_in_base" type="number" min="1" step="1" placeholder="Leave blank to keep" />
              </label>
            </div>
            <p v-if="bulkError" class="modal-error">{{ bulkError }}</p>
            <div class="modal-footer">
              <button type="button" class="btn-outline" @click="showBulkEditModal = false">Cancel</button>
              <button type="submit" class="btn-primary" :disabled="bulkSaving">
                {{ bulkSaving ? 'Updating…' : 'Apply Changes' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

  </section>
</template>

<style scoped>
.units-page { display: grid; gap: 16px; }

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-bulk {
  height: 36px;
  padding: 0 12px;
  border: 1px solid var(--border-default);
  border-radius: 8px;
  background: var(--bg-elevated);
  color: var(--text-secondary);
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.btn-bulk-active {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--text-inverse);
}

.search-wrap { position: relative; display: flex; align-items: center; }

.search-icon {
  position: absolute; left: 10px; font-size: 18px;
  color: var(--text-muted); pointer-events: none;
}

.search-input {
  height: 38px; padding: 0 12px 0 36px;
  border-radius: 8px; border: 1px solid var(--border-default);
  background: var(--bg-card); color: var(--text-primary);
  font-size: 13px; width: 320px; outline: none;
}
.search-input:focus { border-color: var(--accent); }

.search-input:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  box-shadow: 0 0 0 3px var(--primary-tint);
}

.hint { font-size: 12px; color: var(--text-muted); font-family: var(--font-data); }

.state-msg { margin: 0; font-size: 13px; color: var(--text-muted); padding: 32px 0; text-align: center; }
.state-msg.error { color: var(--error); }

.table-wrap {
  border: 1px solid var(--border-subtle);
  border-radius: 12px; background: var(--bg-card); overflow-x: auto;
}

table { width: 100%; border-collapse: collapse; min-width: 860px; }
thead tr { border-bottom: 1px solid var(--border-subtle); }

th {
  text-align: left; font-size: 11px; color: var(--text-muted);
  padding: 10px 14px; font-weight: 600; letter-spacing: 0.04em; white-space: nowrap;
}
th.num { text-align: right; }

td {
  padding: 11px 14px; border-top: 1px solid var(--border-subtle);
  color: var(--text-secondary); font-size: 13px; vertical-align: middle;
}
td.num { text-align: right; }

tr.editing td { background: var(--bg-elevated); }

.mono { font-family: var(--font-data); }
.sku { color: var(--text-primary); font-size: 12px; font-weight: 500; }
.name-cell { color: var(--text-primary); font-weight: 500; max-width: 220px; }
.generic { color: var(--accent); font-size: 12px; }
.muted { color: var(--text-muted); }

.no-unit { color: var(--text-muted); font-size: 12px; font-style: italic; }

.unit-badge {
  display: inline-block; padding: 2px 8px; border-radius: 999px;
  font-size: 11px; background: var(--bg-elevated);
  color: var(--text-secondary); border: 1px solid var(--border-default);
}

.inline-input {
  width: 90px; min-height: 34px; padding: 0 8px; border-radius: 6px;
  border: 1px solid var(--accent); background: var(--bg-recessed);
  color: var(--text-primary); font-size: 12px; font-family: var(--font-data); outline: none;
}

.stock-ok { color: var(--success); }
.stock-low { color: var(--accent); }
.stock-zero { color: var(--error); }

.empty-row { text-align: center; color: var(--text-muted); padding: 40px; border-top: none; }

.actions { display: flex; gap: 4px; justify-content: flex-end; white-space: nowrap; }

.icon-btn {
  width: 40px; height: 40px; border-radius: 6px;
  border: 1px solid var(--border-default); background: var(--bg-elevated);
  color: var(--text-secondary); display: inline-flex;
  align-items: center; justify-content: center; cursor: pointer; padding: 0;
}
.icon-btn .material-icons { font-size: 15px; }
.icon-btn.accent { color: var(--accent); border-color: var(--accent); }
.icon-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.save-error { font-size: 12px; color: var(--error); margin: 0; }

.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 4px 0;
  gap: 10px;
  flex-wrap: wrap;
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

.page-num {
  font-size: 13px;
  font-family: var(--font-data);
  color: var(--text-secondary);
  min-width: 20px;
  text-align: center;
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

.page-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.page-btn .material-icons { font-size: 18px; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: var(--overlay-bg);
  display: flex; align-items: center; justify-content: center; z-index: 100; padding: 16px;
}
.modal {
  background: var(--bg-card); border: 1px solid var(--border-subtle);
  border-radius: 14px; width: 100%; max-width: 480px;
  display: flex; flex-direction: column; overflow: hidden;
}
.modal-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 18px 22px 14px; border-bottom: 1px solid var(--border-subtle);
}
.modal-head h3 { margin: 0; font-size: 15px; font-weight: 600; }
.modal-body { padding: 18px 22px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.field {
  display: flex; flex-direction: column; gap: 6px;
  font-size: 12px; color: var(--text-muted);
}
.field input, .field select {
  min-height: 40px; padding: 0 12px; border-radius: 8px;
  border: 1px solid var(--border-default); background: var(--bg-elevated);
  color: var(--text-primary); font-size: 13px; outline: none;
}
.field input:focus, .field select:focus { border-color: var(--accent); }

.inline-input:focus-visible,
.field input:focus-visible,
.field select:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  box-shadow: 0 0 0 3px var(--primary-tint);
}
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

.modal-error { font-size: 12px; color: var(--error); margin: 10px 0 0; }
.modal-footer { display: flex; justify-content: flex-end; gap: 10px; margin-top: 18px; }
.btn-primary {
  display: inline-flex; align-items: center; gap: 6px;
  height: 36px; padding: 0 16px; border-radius: 8px; border: 0;
  background: var(--accent); color: var(--text-inverse); font-size: 13px; font-weight: 500; cursor: pointer;
}
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-outline {
  height: 36px; padding: 0 16px; border-radius: 8px;
  border: 1px solid var(--border-default); background: var(--bg-elevated);
  color: var(--text-secondary); font-size: 13px; cursor: pointer;
}

.units-page {
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
  max-width: 320px;
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
  width: min(360px, 100%);
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
}

.btn-bulk {
  height: 40px;
  border-radius: var(--radius-md);
  font-weight: 500;
  border-color: var(--border-default);
  background: var(--bg-elevated);
}

.btn-bulk:hover:not(:disabled) {
  background: var(--bg-hover);
}

.btn-bulk-active {
  background: var(--primary);
  border-color: var(--primary);
  color: var(--text-inverse);
  box-shadow: var(--shadow-xs);
}

.hint {
  margin-left: auto;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-default);
  background: var(--bg-recessed);
}

.table-wrap {
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
}

table {
  min-width: 900px;
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

.unit-row.row-selected td {
  background: color-mix(in oklab, var(--primary) 16%, var(--bg-card));
}

.unit-row.row-selected:hover td {
  background: color-mix(in oklab, var(--primary) 22%, var(--bg-card));
}

.unit-row.stock-low td:first-child {
  box-shadow: inset 3px 0 0 var(--warning);
}

.unit-row.stock-zero td:first-child {
  box-shadow: inset 3px 0 0 var(--error);
}

.stock-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 42px;
  padding: 3px 8px;
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

.icon-btn {
  border-radius: var(--radius-md);
  background: var(--bg-card);
}

.icon-btn:hover:not(:disabled) {
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
  padding: var(--space-5) var(--space-6) var(--space-4);
}

.modal-body {
  padding: var(--space-5) var(--space-6);
}

.field input,
.field select {
  border-radius: var(--radius-md);
}

.btn-primary,
.btn-outline {
  height: 40px;
  border-radius: var(--radius-md);
  font-weight: 500;
}

.btn-primary {
  background: var(--primary);
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-outline:hover {
  background: var(--bg-hover);
}

@media (max-width: 900px) {
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
    width: 100%;
  }

  .search-input {
    width: 100%;
  }

  .hint {
    margin-left: 0;
    align-self: flex-start;
  }
}
</style>
