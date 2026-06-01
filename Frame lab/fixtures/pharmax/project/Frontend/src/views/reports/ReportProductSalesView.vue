<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { dashboardService } from '@/services/dashboard'
import { useAuthStore } from '@/stores/auth'
import { printStructuredReport } from '@/lib/reportPrint'
import { useCurrency } from '@/composables/useCurrency'

const loading = ref(false)
const error = ref('')
const payload = ref(null)
const selectedPeriod = ref('month')
const auth = useAuthStore()
const { formatSimple } = useCurrency()

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

const rows = computed(() => payload.value?.top_products ?? [])
const productCount = computed(() => rows.value.length)
const totalUnits = computed(() => (
  rows.value.reduce((sum, row) => sum + Number(row.quantity || 0), 0)
))
const totalRevenue = computed(() => (
  rows.value.reduce((sum, row) => sum + Number(row.revenue || 0), 0)
))

function formatCurrency(value) {
  return formatSimple(value, 0)
}

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
    ['Product', 'Units Sold', 'Revenue'],
    ...rows.value.map((row) => [row.product_name, Number(row.quantity || 0), Number(row.revenue || 0)]),
  ]
  downloadCsv(`report-product-sales-${activePeriod.rangeDays}d.csv`, dataRows)
}

function printReport() {
  const activePeriod = getActivePeriod()
  const reportRows = rows.value.map((row) => [
    row.product_name,
    Number(row.quantity || 0).toLocaleString(),
    formatCurrency(row.revenue),
  ])

  printStructuredReport({
    title: 'Best-Selling Products',
    subtitle: 'Products with highest quantity sold and revenue.',
    periodLabel: activePeriod.label,
    generatedBy: auth.user?.full_name || auth.user?.username,
    highlights: [
      { label: 'Products Listed', value: reportRows.length.toLocaleString() },
    ],
    tables: [
      {
        title: 'Product Sales Table',
        columns: ['Product', 'Units Sold', 'Revenue'],
        rows: reportRows,
        emptyMessage: 'No product sales data found.',
      },
    ],
  })
}

async function loadData() {
  const activePeriod = getActivePeriod()
  loading.value = true
  error.value = ''
  try {
    payload.value = await dashboardService.getAnalytics({
      rangeDays: activePeriod.rangeDays,
      asOfDate: activePeriod.asOfDate,
      includeContext: false,
      topN: 20,
      staffLimit: 5,
      invoiceLimit: 5,
    })
  } catch (err) {
    error.value = err?.message || 'Failed to load product sales report.'
  } finally {
    loading.value = false
  }
}

watch(selectedPeriod, loadData)
onMounted(loadData)
</script>

<template>
  <section class="report-page">
    <header class="report-header">
      <h2>Best-Selling Products</h2>

      <div class="report-actions">
        <label class="filter-field">
          <span>Time period</span>
          <select v-model="selectedPeriod" class="filter-select">
            <option v-for="option in getPeriodOptions()" :key="option.key" :value="option.key">{{ option.label }}</option>
          </select>
        </label>
        <button type="button" class="btn btn-primary" :disabled="loading" @click="exportCsv">Export CSV</button>
        <button type="button" class="btn btn-secondary" :disabled="loading" @click="printReport">Print</button>
      </div>
    </header>

    <p v-if="error" class="feedback feedback-error">{{ error }}</p>
    <p v-else-if="loading" class="feedback">Loading product sales report...</p>

    <template v-else>
      <section class="summary-grid">
        <article class="summary-card">
          <p class="summary-label">Products listed</p>
          <p class="summary-value">{{ productCount.toLocaleString() }}</p>
        </article>
        <article class="summary-card">
          <p class="summary-label">Total units sold</p>
          <p class="summary-value">{{ totalUnits.toLocaleString() }}</p>
        </article>
        <article class="summary-card">
          <p class="summary-label">Total revenue in list</p>
          <p class="summary-value">{{ formatCurrency(totalRevenue) }}</p>
        </article>
      </section>

      <article class="report-card">
        <header class="section-head">
          <h3>Product sales table</h3>
          <p>Use this table to prioritize reorder, promotions, and shelf space.</p>
        </header>
        <div class="table-wrap">
          <table class="report-table">
            <thead>
              <tr>
                <th>Product</th>
                <th class="numeric">Units sold</th>
                <th class="numeric">Revenue</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in rows" :key="row.product_id || row.product_name">
                <td>{{ row.product_name }}</td>
                <td class="numeric">{{ Number(row.quantity || 0).toLocaleString() }}</td>
                <td class="numeric">{{ formatCurrency(row.revenue) }}</td>
              </tr>
            </tbody>
          </table>
          <p v-if="!rows.length" class="empty">No product sales data found.</p>
        </div>
      </article>
    </template>
  </section>
</template>

<style scoped>
.report-page {
  display: grid;
  gap: var(--space-4);
}

.report-header,
.report-card,
.summary-card {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
}

.report-header {
  padding: var(--space-4);
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.report-header h2 {
  margin: 0;
  font-size: 24px;
}

.report-actions {
  display: flex;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.filter-field {
  display: grid;
  gap: 6px;
  min-width: 210px;
}

.filter-field span {
  font-size: 12px;
  color: var(--text-muted);
}

.filter-select {
  min-height: 40px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 0 12px;
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.btn {
  min-height: 40px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
  background: var(--bg-card);
  color: var(--text-primary);
  padding: 0 14px;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary {
  background: var(--primary);
  border-color: var(--primary);
  color: var(--text-inverse);
}

.btn-secondary {
  border-color: var(--primary);
  color: var(--primary);
  background: var(--primary-bg);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.feedback {
  margin: 0;
  padding: 10px 12px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-recessed);
  color: var(--text-secondary);
}

.feedback-error {
  border-color: var(--error);
  background: var(--error-bg);
  color: var(--error);
}

.summary-grid {
  display: grid;
  gap: var(--space-3);
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.summary-card {
  padding: var(--space-3);
  display: grid;
  gap: 6px;
}

.summary-label {
  margin: 0;
  font-size: 12px;
  color: var(--text-muted);
}

.summary-value {
  margin: 0;
  font-family: var(--font-data);
  font-size: clamp(20px, 2vw, 28px);
  font-weight: 700;
}

.report-card {
  padding: var(--space-4);
  display: grid;
  gap: var(--space-3);
}

.section-head h3 {
  margin: 0;
  font-size: 18px;
}

.section-head p {
  margin: 4px 0 0;
  color: var(--text-secondary);
  font-size: 13px;
}

.table-wrap {
  overflow: auto;
  border: 1px solid var(--table-border);
  border-radius: var(--radius-md);
  background: var(--bg-card);
}

.report-table {
  width: 100%;
  min-width: 520px;
  border-collapse: collapse;
}

.report-table th,
.report-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--table-border);
  text-align: left;
}

.report-table th {
  background: var(--table-header-bg);
  color: var(--text-secondary);
  font-size: 12px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.report-table tbody tr:nth-child(even) {
  background: var(--bg-muted);
}

.report-table tbody tr:last-child td {
  border-bottom: 0;
}

.numeric {
  text-align: right !important;
  font-family: var(--font-data);
}

.empty {
  margin: 0;
  color: var(--text-muted);
  padding: 12px;
}

@media (max-width: 760px) {
  .report-header {
    align-items: stretch;
  }

  .report-actions,
  .filter-field {
    width: 100%;
  }
}

@media print {
  .report-actions {
    display: none;
  }

  .report-header,
  .report-card,
  .summary-card {
    box-shadow: none;
  }

  .report-table tbody tr:nth-child(even) {
    background: transparent;
  }
}
</style>
