<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { dashboardService } from '@/services/dashboard'
import { useAuthStore } from '@/stores/auth'
import { printStructuredReport } from '@/lib/reportPrint'

const loading = ref(false)
const error = ref('')
const payload = ref(null)
const selectedPeriod = ref('month')
const auth = useAuthStore()

function isoDateDaysAgo(daysAgo) {
  const day = new Date()
  day.setDate(day.getDate() - daysAgo)
  return day.toISOString().slice(0, 10)
}

function getPeriodOptions() {
  const monthLabel = new Date().toLocaleDateString(undefined, { month: 'long' })
  return [
    { key: 'yesterday', label: 'Yesterday', rangeDays: 1, asOfDate: isoDateDaysAgo(1) },
    { key: 'week', label: 'This Week', rangeDays: 7, asOfDate: null },
    { key: 'two-weeks', label: 'Last 2 Weeks', rangeDays: 14, asOfDate: null },
    { key: 'month', label: `Month of ${monthLabel}`, rangeDays: 30, asOfDate: null },
    { key: 'three-months', label: 'Last 3 Months', rangeDays: 90, asOfDate: null },
  ]
}

function getActivePeriod() {
  return getPeriodOptions().find((period) => period.key === selectedPeriod.value) || getPeriodOptions()[3]
}

const stockOutRows = computed(() => {
  return payload.value?.out_of_stock_items ?? []
})
const lowStockWatchCount = computed(() => {
  const rows = payload.value?.low_stock_items ?? []
  return rows.filter((row) => Number(row.quantity_on_hand || 0) > 0).length
})

function csvValue(value) {
  const text = String(value ?? '')
  if (text.includes('"') || text.includes(',') || text.includes('\n')) {
    return `"${text.replace(/"/g, '""')}"`
  }
  return text
}

function downloadCsv(filename, dataRows) {
  const csv = dataRows.map((row) => row.map(csvValue).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

function exportCsv() {
  const activePeriod = getActivePeriod()
  const dataRows = [
    ['Product', 'On Hand', 'Reorder Level'],
    ...stockOutRows.value.map((row) => [row.name, Number(row.quantity_on_hand || 0), Number(row.reorder_level || 0)]),
  ]
  downloadCsv(`report-stock-out-${activePeriod.rangeDays}d.csv`, dataRows)
}

function printReport() {
  const activePeriod = getActivePeriod()
  const rows = stockOutRows.value.map((row) => [
    row.name,
    Number(row.quantity_on_hand || 0).toLocaleString(),
    Number(row.reorder_level || 0).toLocaleString(),
  ])

  printStructuredReport({
    title: 'Out-of-Stock Items',
    subtitle: 'Products listed here currently have zero quantity.',
    periodLabel: activePeriod.label,
    generatedBy: auth.user?.full_name || auth.user?.username,
    highlights: [
      { label: 'Stock-out Count', value: rows.length.toLocaleString() },
    ],
    tables: [
      {
        title: 'Out-of-Stock Table',
        columns: ['Product', 'On Hand', 'Reorder Level'],
        rows,
        emptyMessage: 'No stock-out products found in this period.',
      },
    ],
  })
}

async function loadData() {
  const activePeriod = getActivePeriod()
  loading.value = true
  error.value = ''
  try {
    payload.value = await dashboardService.getReports({
      rangeDays: activePeriod.rangeDays,
      asOfDate: activePeriod.asOfDate,
    })
  } catch (err) {
    error.value = err?.message || 'Failed to load stock out report.'
  } finally {
    loading.value = false
  }
}

watch(selectedPeriod, loadData)
onMounted(loadData)
</script>

<template>
  <section class="report-page">
    <header class="hero-card">
      <div class="hero-copy">
        <p class="eyebrow">Stock Management</p>
        <h2>Out-of-Stock Items</h2>
        <p>Restock zero-quantity products first.</p>
      </div>
      <div class="actions">
        <select v-model="selectedPeriod" class="control-select">
          <option v-for="option in getPeriodOptions()" :key="option.key" :value="option.key">{{ option.label }}</option>
        </select>
        <button type="button" class="btn-outline" @click="exportCsv" :disabled="loading">Export CSV</button>
        <button type="button" class="btn-primary" @click="printReport" :disabled="loading">Print</button>
      </div>
    </header>

    <div class="summary-grid">
      <article class="summary-card alert">
        <p class="summary-label">Out now</p>
        <p class="summary-value">{{ stockOutRows.length.toLocaleString() }}</p>
      </article>
      <article class="summary-card">
        <p class="summary-label">Low but available</p>
        <p class="summary-value">{{ lowStockWatchCount.toLocaleString() }}</p>
      </article>
    </div>

    <nav class="ops-nav" aria-label="Stock operations shortcuts">
      <RouterLink to="/stock" class="ops-link primary">Open Stock Adjustments</RouterLink>
      <RouterLink to="/stock/low-stock" class="ops-link">Open Low Stock Watchlist</RouterLink>
    </nav>

    <p v-if="error" class="state-msg error">{{ error }}</p>
    <p v-else-if="loading" class="state-msg">Loading out-of-stock report...</p>

    <div v-else class="table-surface">
      <table class="report-table">
        <thead>
          <tr>
            <th>Product</th>
            <th class="num">On Hand</th>
            <th class="num">Reorder Level</th>
            <th class="center">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in stockOutRows" :key="row.product_id || row.name">
            <td>{{ row.name }}</td>
            <td class="num">{{ Number(row.quantity_on_hand || 0).toLocaleString() }}</td>
            <td class="num">{{ Number(row.reorder_level || 0).toLocaleString() }}</td>
            <td class="center">
              <span class="status-pill danger">Out of stock</span>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="!stockOutRows.length" class="state-msg">No out-of-stock products were found for this period.</p>
    </div>
  </section>
</template>

<style scoped>
.report-page {
  display: grid;
  gap: var(--space-4);
}

.hero-card {
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

.hero-copy {
  display: grid;
  gap: var(--space-1);
}

.eyebrow {
  margin: 0;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-tertiary);
}

.hero-copy h2 {
  margin: 0;
  font-size: 24px;
}

.hero-copy p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 13px;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
}

.control-select,
.btn-outline,
.btn-primary {
  height: 40px;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 500;
}

.control-select {
  border: 1px solid var(--border-default);
  padding: 0 12px;
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.btn-outline,
.btn-primary {
  padding: 0 14px;
  cursor: pointer;
}

.btn-outline {
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-secondary);
}

.btn-outline:hover:not(:disabled) {
  background: var(--bg-hover);
}

.btn-primary {
  border: 0;
  background: var(--primary);
  color: var(--text-inverse);
  box-shadow: var(--shadow-xs);
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-outline:disabled,
.btn-primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-3);
}

.summary-card {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
  padding: var(--space-4);
}

.summary-card.alert {
  border-color: var(--error-tint);
  background: var(--error-bg);
}

.summary-label {
  margin: 0;
  font-size: 12px;
  color: var(--text-tertiary);
}

.summary-value {
  margin: var(--space-1) 0 0;
  font-size: 24px;
  font-family: var(--font-data);
  color: var(--text-primary);
}

.summary-card.alert .summary-value {
  color: var(--error);
}

.ops-nav {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.ops-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
}

.ops-link.primary {
  border-color: transparent;
  background: var(--primary);
  color: var(--text-inverse);
}

.ops-link:hover {
  background: var(--bg-hover);
}

.ops-link.primary:hover {
  background: var(--primary-hover);
}

.state-msg {
  margin: 0;
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-muted);
  color: var(--text-secondary);
}

.state-msg.error {
  border-color: var(--error-tint);
  background: var(--error-bg);
  color: var(--error);
}

.table-surface {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
  overflow: auto;
}

.report-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  min-width: 560px;
}

.report-table th,
.report-table td {
  padding: 11px 14px;
  border-bottom: 1px solid var(--border-subtle);
  text-align: left;
  vertical-align: middle;
}

.report-table th {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  background: var(--table-header-bg);
}

.report-table tbody tr:nth-child(even) td {
  background: var(--bg-muted);
}

.report-table tbody tr:hover td {
  background: var(--table-row-hover);
}

.report-table tbody tr:last-child td {
  border-bottom: none;
}

.num {
  text-align: right !important;
  font-family: var(--font-data);
}

.center {
  text-align: center !important;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 3px 9px;
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 600;
  border: 1px solid transparent;
}

.status-pill.danger {
  color: var(--error);
  background: var(--error-bg);
  border-color: var(--error-tint);
}

@media (max-width: 760px) {
  .hero-card {
    padding: var(--space-4);
  }

  .actions {
    width: 100%;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
