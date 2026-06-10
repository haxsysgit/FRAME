<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { invoicesService } from '../services/invoices'
import { useAuthStore } from '../stores/auth'
import { useToast } from '@/composables/useToast'
import { useCurrency } from '@/composables/useCurrency'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const toast = useToast()
const { formatSimple } = useCurrency()

// State
const invoices = ref([])
const loading = ref(true)
const totalCount = ref(0)

// Filters - Show only STAMPED invoices by default (paid/ready invoices)
const statusFilter = ref('STAMPED')
const dateFrom = ref('')
const dateTo = ref('')
const sortBy = ref('date_desc')
const searchQuery = ref('')

// Pagination
const currentPage = ref(1)
const pageSize = 20

function isStamped(status) {
  const normalized = String(status || '').toUpperCase()
  return normalized === 'STAMPED' || normalized === 'FINALIZED'
}

// Load invoices
async function loadInvoices() {
  loading.value = true
  try {
    const data = await invoicesService.list({
      status: statusFilter.value !== 'all' ? statusFilter.value : undefined,
      limit: pageSize,
      offset: (currentPage.value - 1) * pageSize,
    })
    invoices.value = Array.isArray(data) ? data : []
    totalCount.value = invoices.value.length
  } catch (err) {
    console.error('Failed to load invoices:', err)
    invoices.value = []
  } finally {
    loading.value = false
  }
}

const canDispense = computed(() => ['ADMIN', 'STAFF'].includes(auth.userRole))

onMounted(() => {
  const fromQuery = String(route.query.status || '').toUpperCase()
  if (['DRAFT', 'STAMPED', 'DISPENSED', 'CANCELLED', 'ALL'].includes(fromQuery)) {
    statusFilter.value = fromQuery === 'ALL' ? 'all' : fromQuery
  }
  loadInvoices()
})

watch([statusFilter, currentPage], loadInvoices)

// Filtered and sorted invoices
const displayInvoices = computed(() => {
  let result = [...invoices.value]
  
  // Enhanced smart search
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(inv => {
      // Search by invoice name/ID
      const matchesName = inv.name?.toLowerCase().includes(q)
      const matchesId = inv.id?.toLowerCase().includes(q)
      
      // Search by status
      const matchesStatus = inv.status?.toLowerCase().includes(q)
      
      // Search by payment method
      const matchesPayment = inv.payment_method?.toLowerCase().includes(q)
      
      // Search by amount (e.g., "1000", "$1000", "£1000", "₦1000")
      const amountStr = String(inv.total_amount || 0)
      const amountQuery = q.replace(/[^0-9.]/g, '')
      const matchesAmount = amountQuery ? amountStr.includes(amountQuery) : false
      
      // Search by date
      const dateStr = inv.created_at?.slice(0, 10) || ''
      const matchesDate = dateStr.includes(q)
      
      return matchesName || matchesId || matchesStatus || matchesPayment || matchesAmount || matchesDate
    })
  }
  
  // Date filter
  if (dateFrom.value) {
    result = result.filter(inv => inv.created_at?.slice(0, 10) >= dateFrom.value)
  }
  if (dateTo.value) {
    result = result.filter(inv => inv.created_at?.slice(0, 10) <= dateTo.value)
  }
  
  // Sort
  switch (sortBy.value) {
    case 'date_desc':
      result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      break
    case 'date_asc':
      result.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
      break
    case 'amount_desc':
      result.sort((a, b) => (b.total_amount || 0) - (a.total_amount || 0))
      break
    case 'amount_asc':
      result.sort((a, b) => (a.total_amount || 0) - (b.total_amount || 0))
      break
  }
  
  return result
})

// Stats
const stats = computed(() => {
  const all = invoices.value
  return {
    total: all.length,
    draft: all.filter(i => i.status === 'DRAFT').length,
    stamped: all.filter(i => isStamped(i.status)).length,
    dispensed: all.filter(i => i.status === 'DISPENSED').length,
    totalRevenue: all
      .filter(i => isStamped(i.status) || i.status === 'DISPENSED')
      .reduce((sum, i) => sum + (i.total_amount || 0), 0),
  }
})

// Format helpers
function fmt(n) {
  return formatSimple(n, 2)
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function statusClass(status) {
  const s = (status || '').toUpperCase()
  if (s === 'DISPENSED') return 'dispensed'
  if (s === 'STAMPED' || s === 'FINALIZED') return 'finalized'
  if (s === 'CANCELLED') return 'cancelled'
  return 'draft'
}

// Actions
function viewInvoice(inv) {
  router.push(`/invoices/${inv.id}`)
}

function createInvoice() {
  router.push('/invoices/create')
}

async function markDispensed(inv) {
  if (!canDispense.value) return
  try {
    await invoicesService.dispense(inv.id)
    toast.success('Invoice marked as dispensed.')
    await loadInvoices()
  } catch (err) {
    toast.error(`Could not mark as dispensed. ${err.message}`)
  }
}

// Role checks
const canCreate = computed(() => ['ADMIN', 'STAFF'].includes(auth.userRole))
</script>

<template>
  <div class="invoice-list">
    <!-- Header with actions -->
    <header class="list-header">
      <div class="header-left">
        <span class="count-badge">{{ stats.total }} invoices</span>
      </div>
      <div class="header-right">
        <button v-if="canCreate" class="btn-primary" @click="createInvoice">
          <span class="material-icons">add</span>
          New Invoice
        </button>
      </div>
    </header>

    <article class="status-guide">
      <strong>Status guide:</strong>
      <span><strong>Draft</strong> = awaiting payment.</span>
      <span><strong>Stamped</strong> = paid and ready to hand over.</span>
      <span><strong>Dispensed</strong> = goods already released to customer.</span>
    </article>

    <!-- Stats Cards -->
    <div class="stats-row">
      <div class="stat-card">
        <span class="stat-value">{{ stats.draft }}</span>
        <span class="stat-label">Drafts</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ stats.stamped }}</span>
        <span class="stat-label">Awaiting Dispense</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ stats.dispensed }}</span>
        <span class="stat-label">Completed</span>
      </div>
      <div class="stat-card highlight">
        <span class="stat-value">{{ fmt(stats.totalRevenue) }}</span>
        <span class="stat-label">Total Revenue</span>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="filter-group">
        <div class="search-input">
          <span class="material-icons">search</span>
          <input v-model="searchQuery" type="text" placeholder="Search invoices..." />
        </div>
      </div>

      <div class="filter-group">
        <label>Status</label>
        <select v-model="statusFilter">
          <option value="all">All Status</option>
          <option value="DRAFT">Draft</option>
          <option value="STAMPED">Stamped</option>
          <option value="DISPENSED">Dispensed</option>
          <option value="CANCELLED">Cancelled</option>
        </select>
      </div>

      <div class="filter-group">
        <label>From</label>
        <input v-model="dateFrom" type="date" />
      </div>

      <div class="filter-group">
        <label>To</label>
        <input v-model="dateTo" type="date" />
      </div>

      <div class="filter-group">
        <label>Sort by</label>
        <select v-model="sortBy">
          <option value="date_desc">Newest First</option>
          <option value="date_asc">Oldest First</option>
          <option value="amount_desc">Highest Amount</option>
          <option value="amount_asc">Lowest Amount</option>
        </select>
      </div>
    </div>

    <!-- Invoice Table -->
    <div class="table-container">
      <div v-if="loading" class="loading-state">
        <span class="material-icons spin">refresh</span>
        Loading invoices...
      </div>

      <table v-else-if="displayInvoices.length > 0">
        <thead>
          <tr>
            <th>Invoice</th>
            <th>Date</th>
            <th>Items</th>
            <th>Amount</th>
            <th>Payment</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="inv in displayInvoices" :key="inv.id" @click="viewInvoice(inv)">
            <td class="col-id">
              <span class="invoice-id">{{ inv.name || inv.id?.slice(0, 8) }}</span>
              <span class="invoice-staff">{{ inv.sold_by_id?.slice(0, 6) || '—' }}</span>
            </td>
            <td class="col-date">{{ formatDate(inv.created_at) }}</td>
            <td class="col-items">{{ inv.items?.length || 0 }} items</td>
            <td class="col-amount mono">{{ fmt(inv.total_amount) }}</td>
            <td class="col-payment">{{ inv.payment_method || '—' }}</td>
            <td class="col-status">
              <span class="status-badge" :class="statusClass(inv.status)">
                {{ inv.status }}
              </span>
            </td>
            <td class="col-actions">
              <button class="action-btn" title="View details" @click.stop="viewInvoice(inv)">
                <span class="material-icons">visibility</span>
              </button>
              <button
                v-if="canDispense && (inv.status === 'STAMPED' || inv.status === 'FINALIZED')"
                class="action-btn success"
                title="Mark as dispensed"
                @click.stop="markDispensed(inv)"
              >
                <span class="material-icons">inventory</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else class="empty-state">
        <span class="material-icons">receipt_long</span>
        <p>No invoices found</p>
        <p class="hint">Try adjusting your filters or create a new invoice</p>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="displayInvoices.length > 0" class="pagination">
      <button :disabled="currentPage === 1" @click="currentPage--">
        <span class="material-icons">chevron_left</span>
      </button>
      <span class="page-info">Page {{ currentPage }}</span>
      <button :disabled="displayInvoices.length < pageSize" @click="currentPage++">
        <span class="material-icons">chevron_right</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
/* ═══════════════════════════════════════════════════════════════════════════
   INVOICE LIST VIEW — Clean, filterable invoice list
   ═══════════════════════════════════════════════════════════════════════════ */

.invoice-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* ─── Header ───────────────────────────────────────────────────────────────── */
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
  padding: var(--space-4) var(--space-5);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.header-left h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.count-badge {
  font-size: 12px;
  color: var(--text-muted);
  background: var(--bg-recessed);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  height: 40px;
  padding: 0 var(--space-4);
  background: var(--primary);
  border: none;
  border-radius: var(--radius-lg);
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background var(--transition-fast), transform var(--transition-fast), box-shadow var(--transition-fast);
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-primary .material-icons {
  font-size: 18px;
}

/* ─── Stats ────────────────────────────────────────────────────────────────── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-3);
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  box-shadow: var(--shadow-xs);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast), border-color var(--transition-fast);
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
  opacity: 0.8;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--primary);
}

.stat-card.highlight {
  background: var(--primary-bg);
  border-color: var(--primary);
}

.stat-value {
  font-family: var(--font-data);
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.stat-card.highlight .stat-value {
  color: var(--primary);
}

.stat-label {
  font-size: 12px;
  color: var(--text-muted);
}

.status-guide {
  border: 1px dashed var(--border-default);
  border-radius: var(--radius-lg);
  background: var(--bg-recessed);
  padding: 10px 12px;
  font-size: 12px;
  color: var(--text-secondary);
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

/* ─── Filters ──────────────────────────────────────────────────────────────── */
.filters-bar {
  display: grid;
  grid-template-columns: 2fr repeat(4, 1fr);
  gap: var(--space-3);
  align-items: end;
  padding: var(--space-4);
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xs);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.filter-group label {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
}

.filter-group input,
.filter-group select {
  height: 36px;
  padding: 0 var(--space-3);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  font-size: 13px;
  color: var(--text-primary);
}

.search-input {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  height: 36px;
  padding: 0 var(--space-3);
  background: var(--bg-recessed);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  min-width: 240px;
}

.search-input .material-icons {
  font-size: 18px;
  color: var(--text-muted);
}

.search-input input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 13px;
  color: var(--text-primary);
  outline: none;
  height: 100%;
  padding: 0;
}

/* ─── Table ────────────────────────────────────────────────────────────────── */
.table-container {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xs);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  padding: var(--space-3) var(--space-4);
  background: var(--table-header-bg);
  border-bottom: 1px solid var(--border-subtle);
}

td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
  font-size: 13px;
}

tbody tr {
  cursor: pointer;
  transition: background var(--transition-fast);
}

tbody tr:hover {
  background: var(--bg-hover);
}

tbody tr:last-child td {
  border-bottom: none;
}

.col-id {
  min-width: 120px;
}

.invoice-id {
  display: block;
  font-family: var(--font-data);
  font-weight: 500;
  color: var(--text-primary);
}

.invoice-staff {
  display: block;
  font-size: 11px;
  color: var(--text-muted);
}

.col-date {
  color: var(--text-secondary);
}

.col-items {
  color: var(--text-muted);
}

.col-amount {
  font-weight: 600;
  color: var(--text-primary);
}

.col-payment {
  color: var(--text-muted);
  text-transform: capitalize;
}

.mono {
  font-family: var(--font-data);
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.draft {
  background: var(--bg-recessed);
  color: var(--text-muted);
}

.status-badge.finalized {
  background: var(--primary-tint);
  color: var(--primary);
}

.status-badge.dispensed {
  background: var(--success-tint);
  color: var(--success);
}

.status-badge.cancelled {
  background: var(--error-tint);
  color: var(--error);
}

.action-btn {
  width: 32px;
  height: 32px;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  color: var(--text-muted);
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--border-default);
  transform: translateY(-1px);
  box-shadow: var(--shadow-xs);
}

.action-btn.success {
  color: var(--success);
  border-color: var(--success);
}

.action-btn.success:hover {
  background: var(--success-bg);
}

.action-btn .material-icons {
  font-size: 16px;
}

/* ─── Loading / Empty ──────────────────────────────────────────────────────── */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  color: var(--text-muted);
}

.loading-state .material-icons,
.empty-state .material-icons {
  font-size: 48px;
  margin-bottom: var(--space-3);
  opacity: 0.4;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.empty-state p {
  margin: 0;
}

.empty-state .hint {
  font-size: 12px;
  margin-top: var(--space-1);
}

/* ─── Pagination ───────────────────────────────────────────────────────────── */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
}

.pagination button {
  width: 36px;
  height: 36px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  display: grid;
  place-items: center;
}

.pagination button:hover:not(:disabled) {
  background: var(--bg-hover);
}

.pagination button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  font-size: 13px;
  color: var(--text-muted);
}

/* ─── Responsive ───────────────────────────────────────────────────────────── */
@media (max-width: 1024px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .filters-bar {
    flex-direction: column;
  }

  .search-input {
    min-width: 100%;
  }
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>
