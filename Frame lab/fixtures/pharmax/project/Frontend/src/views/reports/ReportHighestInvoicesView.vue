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

const periodOptions = computed(() => {
  const monthLabel = new Date().toLocaleDateString(undefined, { month: 'long' })
  return [
    { key: 'yesterday', label: 'Yesterday', rangeDays: 1, asOfDate: isoDateDaysAgo(1) },
    { key: 'week', label: 'This Week', rangeDays: 7, asOfDate: null },
    { key: 'two-weeks', label: 'Last 2 Weeks', rangeDays: 14, asOfDate: null },
    { key: 'month', label: `Month of ${monthLabel}`, rangeDays: 30, asOfDate: null },
    { key: 'three-months', label: 'Last 3 Months', rangeDays: 90, asOfDate: null },
  ]
})

const activePeriod = computed(() => (
  periodOptions.value.find((period) => period.key === selectedPeriod.value) || periodOptions.value[3]
))

function toNumber(value) {
  const amount = Number(value)
  return Number.isFinite(amount) ? amount : 0
}

function getBillLabel(row, fallbackRank) {
  if (row.name) return row.name
  if (row.id) return row.id
  return `Bill ${fallbackRank}`
}

function getPaymentMethodLabel(row) {
  return row.payment_method || 'Not set'
}

const rows = computed(() => payload.value?.top_invoices ?? [])
const rankedRows = computed(() => (
  rows.value.map((row, index) => ({
    ...row,
    rank: index + 1,
    billLabel: getBillLabel(row, index + 1),
    paymentLabel: getPaymentMethodLabel(row),
    amountValue: toNumber(row.amount),
  }))
))
const invoiceCount = computed(() => rankedRows.value.length)
const largestBillAmount = computed(() => rankedRows.value[0]?.amountValue ?? 0)
const totalAmount = computed(() => (
  rankedRows.value.reduce((sum, row) => sum + row.amountValue, 0)
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
  const dataRows = [
    ['Rank', 'Bill', 'Payment Method', 'Amount'],
    ...rankedRows.value.map((row) => [row.rank, row.billLabel, row.paymentLabel, row.amountValue]),
  ]
  downloadCsv(`report-largest-customer-bills-${activePeriod.value.rangeDays}d.csv`, dataRows)
}

function printReport() {
  const reportRows = rankedRows.value.map((row) => [
    String(row.rank),
    row.billLabel,
    row.paymentLabel,
    formatCurrency(row.amountValue),
  ])

  printStructuredReport({
    title: 'Largest Customer Bills',
    subtitle: 'Review high-value bills first so follow-up is easier.',
    periodLabel: activePeriod.value.label,
    generatedBy: auth.user?.full_name || auth.user?.username,
    highlights: [
      { label: 'Bills Listed', value: invoiceCount.value.toLocaleString() },
      { label: 'Largest Bill', value: formatCurrency(largestBillAmount.value) },
      { label: 'Total Amount', value: formatCurrency(totalAmount.value) },
    ],
    tables: [
      {
        title: 'Ranked Bill List',
        columns: ['Rank', 'Bill', 'Payment Method', 'Amount'],
        rows: reportRows,
        emptyMessage: 'No customer bills found for this period.',
      },
    ],
  })
}

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    payload.value = await dashboardService.getAnalytics({
      rangeDays: activePeriod.value.rangeDays,
      asOfDate: activePeriod.value.asOfDate,
      includeContext: false,
      topN: 10,
      invoiceLimit: 20,
      staffLimit: 5,
    })
  } catch (err) {
    error.value = err?.message || 'Could not load the largest customer bills report.'
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
      <div class="title-wrap">
        <h2>Largest Customer Bills</h2>
        <p>Review high-value bills first, then continue down the list.</p>
      </div>

      <div class="report-actions">
        <label class="filter-field">
          <span>Time period</span>
          <select v-model="selectedPeriod" class="filter-select">
            <option v-for="option in periodOptions" :key="option.key" :value="option.key">{{ option.label }}</option>
          </select>
        </label>
        <button type="button" class="btn btn-primary" :disabled="loading" @click="exportCsv">Export CSV</button>
        <button type="button" class="btn btn-secondary" :disabled="loading" @click="printReport">Print</button>
      </div>
    </header>

    <p v-if="error" class="feedback feedback-error">{{ error }}</p>
    <p v-else-if="loading" class="feedback">Loading largest customer bills...</p>

    <template v-else>
      <section class="summary-grid">
        <article class="summary-card">
          <p class="summary-label">Bills listed</p>
          <p class="summary-value">{{ invoiceCount.toLocaleString() }}</p>
        </article>
        <article class="summary-card">
          <p class="summary-label">Largest bill amount</p>
          <p class="summary-value">{{ formatCurrency(largestBillAmount) }}</p>
        </article>
        <article class="summary-card">
          <p class="summary-label">Total amount in list</p>
          <p class="summary-value">{{ formatCurrency(totalAmount) }}</p>
        </article>
      </section>

      <article class="report-card">
        <header class="section-head">
          <h3>Ranked bill list</h3>
          <p>Start at rank 1 for the highest amount.</p>
        </header>
        <div class="table-wrap">
          <table class="report-table">
            <thead>
              <tr>
                <th class="rank">Rank</th>
                <th>Bill</th>
                <th>Payment Method</th>
                <th class="numeric">Amount</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in rankedRows" :key="row.id || `${row.billLabel}-${row.rank}`">
                <td class="rank">{{ row.rank }}</td>
                <td class="mono">{{ row.billLabel }}</td>
                <td>{{ row.paymentLabel }}</td>
                <td class="numeric">{{ formatCurrency(row.amountValue) }}</td>
              </tr>
            </tbody>
          </table>
          <p v-if="!rankedRows.length" class="empty">No customer bills found for this period.</p>
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

.title-wrap {
  display: grid;
  gap: 4px;
}

.title-wrap h2 {
  margin: 0;
  font-size: 24px;
}

.title-wrap p {
  margin: 0;
  color: var(--text-secondary);
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
  min-width: 620px;
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

.rank {
  width: 72px;
  text-align: center;
  font-family: var(--font-data);
}

.mono {
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
