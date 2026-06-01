<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { dashboardService } from '@/services/dashboard'
import { useCurrency } from '@/composables/useCurrency'

const loading = ref(false)
const error = ref('')
const payload = ref(null)
const rangeDays = ref(30)
const { format } = useCurrency()

const rangeOptions = [
  { label: 'Last 7 Days', value: 7 },
  { label: 'Last 30 Days', value: 30 },
  { label: 'Last 90 Days', value: 90 },
]

const PAID_STATUS_KEYS = ['PAID', 'STAMPED', 'FINALIZED', 'DISPENSED', 'COMPLETED', 'SETTLED']
const WATCH_STATUS_KEYS = ['DRAFT', 'PENDING', 'PROCESSING', 'PARTIAL']

const paymentRows = computed(() => payload.value?.payment_mix ?? [])
const statusRows = computed(() => payload.value?.status_mix ?? [])

function toNumber(value) {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

function fmtCurrency(value) {
  return format(value, { decimals: 0 })
}

function fmtCount(value) {
  return toNumber(value).toLocaleString('en-NG')
}

function normalizeStatus(value) {
  return String(value || '').trim().toUpperCase()
}

function isPaidStatus(value) {
  return PAID_STATUS_KEYS.includes(normalizeStatus(value))
}

function formatPaymentMethod(value) {
  const text = String(value || '').trim()
  if (!text || text.toUpperCase() === 'UNKNOWN') return 'Not recorded'
  return text
    .replace(/[_-]+/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function formatStatus(value) {
  const normalized = normalizeStatus(value)
  if (!normalized) return '—'
  if (normalized === 'FINALIZED') return 'Stamped'
  return normalized
    .replace(/[_-]+/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

const totalPaymentRevenue = computed(() => (
  paymentRows.value.reduce((sum, row) => sum + toNumber(row.revenue), 0)
))

const totalPaymentInvoices = computed(() => (
  paymentRows.value.reduce((sum, row) => sum + toNumber(row.invoice_count), 0)
))

const paymentMethodRows = computed(() => (
  [...paymentRows.value].sort((a, b) => toNumber(b.revenue) - toNumber(a.revenue))
))

const statusTableRows = computed(() => (
  [...statusRows.value].sort((a, b) => toNumber(b.count) - toNumber(a.count))
))

const leadingMethod = computed(() => {
  if (!paymentMethodRows.value.length) return null
  return paymentMethodRows.value[0]
})

const totalStatusInvoices = computed(() => (
  statusRows.value.reduce((sum, row) => sum + toNumber(row.count), 0)
))

const paidInvoices = computed(() => (
  statusRows.value.reduce((sum, row) => (
    sum + (isPaidStatus(row.status) ? toNumber(row.count) : 0)
  ), 0)
))

const paidPercent = computed(() => (
  totalStatusInvoices.value > 0
    ? (paidInvoices.value / totalStatusInvoices.value) * 100
    : 0
))

const followUpInvoices = computed(() => (
  Math.max(0, totalStatusInvoices.value - paidInvoices.value)
))

const followUpPercent = computed(() => (
  totalStatusInvoices.value > 0
    ? (followUpInvoices.value / totalStatusInvoices.value) * 100
    : 0
))

const kpiCards = computed(() => [
  {
    title: 'Money Collected',
    value: fmtCurrency(totalPaymentRevenue.value),
    helper: `${fmtCount(totalPaymentInvoices.value)} paid invoice${totalPaymentInvoices.value === 1 ? '' : 's'}`,
  },
  {
    title: 'Most Used Method',
    value: leadingMethod.value ? formatPaymentMethod(leadingMethod.value.method) : 'No data yet',
    helper: leadingMethod.value
      ? `${toNumber(leadingMethod.value.percent).toFixed(1)}% of collected money`
      : 'Add payment records to view this trend',
  },
  {
    title: 'Paid Invoices',
    value: fmtCount(paidInvoices.value),
    helper: totalStatusInvoices.value
      ? `${paidPercent.value.toFixed(1)}% of status records`
      : 'Status tracking not available yet',
  },
  {
    title: 'Needs Follow-up',
    value: fmtCount(followUpInvoices.value),
    helper: totalStatusInvoices.value
      ? `${followUpPercent.value.toFixed(1)}% are still open`
      : 'No open invoice status data yet',
  },
])

const workflowActions = computed(() => {
  const actions = []

  if (!paymentMethodRows.value.length) {
    actions.push({
      title: 'Capture payment method at checkout',
      note: 'Log each payment as cash, card, or transfer so this view stays useful.',
    })
  } else if (leadingMethod.value && toNumber(leadingMethod.value.percent) >= 65) {
    actions.push({
      title: `Keep ${formatPaymentMethod(leadingMethod.value.method)} channel stable`,
      note: 'Most collections use this method. Confirm uptime and speed before rush hours.',
    })
  } else {
    actions.push({
      title: 'Keep all payment options visible',
      note: 'Patients are using multiple methods. Clear checkout prompts will reduce delays.',
    })
  }

  if (followUpInvoices.value > 0) {
    actions.push({
      title: 'Follow up open invoices today',
      note: `${fmtCount(followUpInvoices.value)} invoices are not paid yet. Assign calls before day end.`,
    })
  } else {
    actions.push({
      title: 'Maintain current reconciliation routine',
      note: 'All tracked invoices are marked paid. Continue daily close checks.',
    })
  }

  const cancelledRow = statusRows.value.find((row) => normalizeStatus(row.status) === 'CANCELLED')
  if (toNumber(cancelledRow?.percent) >= 10) {
    actions.push({
      title: 'Review cancellation reasons',
      note: `${toNumber(cancelledRow.percent).toFixed(1)}% cancelled suggests checkout friction or stock issues.`,
    })
  } else {
    actions.push({
      title: 'Watch pending and cancelled counts',
      note: 'A quick daily review helps prevent payment backlog.',
    })
  }

  return actions
})

function clampPercent(value) {
  return Math.min(100, Math.max(0, toNumber(value)))
}

function statusTone(status) {
  const normalized = normalizeStatus(status)
  if (isPaidStatus(normalized)) return 'ok'
  if (WATCH_STATUS_KEYS.includes(normalized)) return 'watch'
  return 'alert'
}

function statusFlag(status) {
  const tone = statusTone(status)
  if (tone === 'ok') return 'On track'
  if (tone === 'watch') return 'Watch'
  return 'Act now'
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
    ['Group', 'Label', 'Revenue', 'Invoices', 'Count', 'Share Percent'],
    ...paymentMethodRows.value.map((row) => [
      'Payment Method',
      formatPaymentMethod(row.method),
      toNumber(row.revenue),
      toNumber(row.invoice_count),
      '',
      toNumber(row.percent),
    ]),
    [],
    ['Group', 'Label', 'Revenue', 'Invoices', 'Count', 'Share Percent'],
    ...statusTableRows.value.map((row) => [
      'Invoice Status',
      formatStatus(row.status),
      '',
      '',
      toNumber(row.count),
      toNumber(row.percent),
    ]),
  ]

  downloadCsv(`analytics-payment-insights-${rangeDays.value}d.csv`, dataRows)
}

function printReport() {
  window.print()
}

async function loadData() {
  loading.value = true
  error.value = ''

  try {
    payload.value = await dashboardService.getAnalytics({
      rangeDays: rangeDays.value,
      includeContext: false,
      topN: 10,
      staffLimit: 5,
      invoiceLimit: 5,
    })
  } catch (err) {
    error.value = err?.message || 'Failed to load payment insights.'
  } finally {
    loading.value = false
  }
}

watch(rangeDays, loadData)
onMounted(loadData)
</script>

<template>
  <section class="analytics-page">
    <header class="analytics-header">
      <h2>Payment Insights</h2>

      <div class="analytics-actions">
        <label class="filter-field">
          <span>Time range</span>
          <select v-model="rangeDays" class="filter-select">
            <option v-for="option in rangeOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
          </select>
        </label>
        <button type="button" class="btn btn-secondary" :disabled="loading" @click="loadData">Refresh</button>
        <button type="button" class="btn btn-primary" :disabled="loading" @click="exportCsv">Export CSV</button>
        <button type="button" class="btn btn-ghost" :disabled="loading" @click="printReport">Print</button>
      </div>
    </header>

    <p v-if="error" class="feedback feedback-error">{{ error }}</p>
    <p v-else-if="loading" class="feedback">Loading payment insights...</p>

    <template v-else>
      <section class="kpi-grid">
        <article v-for="card in kpiCards" :key="card.title" class="kpi-card">
          <p class="kpi-label">{{ card.title }}</p>
          <p class="kpi-value">{{ card.value }}</p>
          <p class="kpi-helper">{{ card.helper }}</p>
        </article>
      </section>

      <section class="analytics-grid">
        <article class="analytics-card">
          <header class="section-head">
            <h3>How patients paid</h3>
            <p>Compare collected money and invoice volume by payment method.</p>
          </header>

          <div v-if="paymentMethodRows.length" class="method-list">
            <div v-for="row in paymentMethodRows" :key="row.method" class="method-row">
              <div class="method-head">
                <p class="method-name">{{ formatPaymentMethod(row.method) }}</p>
                <p class="method-summary">
                  {{ fmtCurrency(row.revenue) }}
                  <span>•</span>
                  {{ fmtCount(row.invoice_count) }} invoices
                </p>
              </div>
              <div class="share-track" role="presentation">
                <span class="share-fill" :style="{ width: `${clampPercent(row.percent)}%` }" />
              </div>
              <p class="share-caption">{{ toNumber(row.percent).toFixed(1) }}% of collected money</p>
            </div>
          </div>
          <p v-else class="empty">No payment activity found for the selected period.</p>
        </article>

        <article class="analytics-card action-card">
          <header class="section-head">
            <h3>Daily follow-up checklist</h3>
            <p>Simple steps for reconciliation and follow-up calls.</p>
          </header>

          <ol class="action-list">
            <li v-for="item in workflowActions" :key="item.title" class="action-item">
              <p class="action-title">{{ item.title }}</p>
              <p class="action-note">{{ item.note }}</p>
            </li>
          </ol>
        </article>
      </section>

      <article class="analytics-card status-card">
        <header class="section-head">
          <h3>Invoice status table</h3>
          <p>Track what is paid, pending, and cancelled so follow-up stays clear.</p>
        </header>

        <div class="table-wrap">
          <table class="analytics-table">
            <thead>
              <tr>
                <th>Status</th>
                <th class="numeric">Invoices</th>
                <th class="numeric">Share</th>
                <th>Follow-up</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in statusTableRows" :key="row.status">
                <td>{{ formatStatus(row.status) }}</td>
                <td class="numeric">{{ fmtCount(row.count) }}</td>
                <td class="numeric">{{ toNumber(row.percent).toFixed(1) }}%</td>
                <td>
                  <span class="status-pill" :class="`status-pill-${statusTone(row.status)}`">{{ statusFlag(row.status) }}</span>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-if="!statusTableRows.length" class="empty">No invoice status data found for the selected period.</p>
        </div>
      </article>
    </template>
  </section>
</template>

<style scoped>
.analytics-page {
  display: grid;
  gap: var(--space-4);
}

.analytics-header,
.kpi-card,
.analytics-card {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
}

.analytics-header {
  padding: var(--space-3) var(--space-4);
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: var(--space-3);
  flex-wrap: wrap;
  border-color: var(--border-subtle);
  background: linear-gradient(150deg, var(--bg-card) 0%, var(--bg-muted) 100%);
}

.analytics-header h2 {
  margin: 0;
  font-size: 22px;
}

.analytics-actions {
  display: flex;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.filter-field {
  display: grid;
  gap: 4px;
  min-width: 170px;
}

.filter-field span {
  font-size: 12px;
  color: var(--text-muted);
}

.filter-select,
.btn {
  min-height: 40px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
  background: var(--bg-card);
  color: var(--text-primary);
  padding: 0 12px;
}

.btn {
  font-weight: 600;
  cursor: pointer;
}

.btn-primary {
  background: var(--primary);
  border-color: var(--primary);
  color: var(--text-inverse);
}

.btn-secondary {
  background: var(--primary-bg);
  border-color: var(--primary);
  color: var(--primary);
}

.btn-ghost {
  background: var(--bg-card);
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

.kpi-grid {
  display: grid;
  gap: var(--space-3);
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

.kpi-card {
  padding: var(--space-3);
  display: grid;
  gap: 6px;
  border-left: 3px solid var(--primary);
  background: var(--bg-card);
}

.kpi-label {
  margin: 0;
  font-size: 12px;
  color: var(--text-muted);
}

.kpi-value {
  margin: 0;
  font-size: clamp(20px, 2vw, 27px);
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.kpi-helper {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
}

.analytics-grid {
  display: grid;
  gap: var(--space-3);
  grid-template-columns: minmax(0, 1.45fr) minmax(0, 0.95fr);
}

.analytics-card {
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

.method-list {
  display: grid;
  gap: 12px;
}

.method-row {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  padding: 10px 12px;
  display: grid;
  gap: 8px;
}

.method-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.method-name,
.method-summary,
.share-caption,
.action-title,
.action-note {
  margin: 0;
}

.method-name {
  font-weight: 600;
}

.method-summary {
  font-size: 12px;
  color: var(--text-secondary);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.share-track {
  height: 8px;
  border-radius: 999px;
  background: var(--bg-muted);
  overflow: hidden;
}

.share-fill {
  display: block;
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
}

.share-caption {
  font-size: 12px;
  color: var(--text-secondary);
}

.action-card {
  align-content: start;
}

.action-list {
  margin: 0;
  padding-left: 18px;
  display: grid;
  gap: 12px;
}

.action-item {
  display: grid;
  gap: 4px;
}

.action-title {
  font-size: 14px;
  font-weight: 600;
}

.action-note {
  font-size: 12px;
  color: var(--text-secondary);
}

.table-wrap {
  overflow: auto;
  border: 1px solid var(--table-border);
  border-radius: var(--radius-md);
  background: var(--bg-card);
}

.analytics-table {
  width: 100%;
  min-width: 560px;
  border-collapse: collapse;
}

.analytics-table th,
.analytics-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--table-border);
  text-align: left;
}

.analytics-table th {
  background: var(--table-header-bg);
  color: var(--text-secondary);
  font-size: 12px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.analytics-table tbody tr:nth-child(even) {
  background: var(--bg-muted);
}

.analytics-table tbody tr:last-child td {
  border-bottom: 0;
}

.numeric {
  text-align: right !important;
  font-family: var(--font-data);
}

.status-pill {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.status-pill-ok {
  background: var(--success-bg);
  color: var(--success);
}

.status-pill-watch {
  background: var(--warning-bg);
  color: var(--warning);
}

.status-pill-alert {
  background: var(--error-bg);
  color: var(--error);
}

.empty {
  margin: 0;
  color: var(--text-muted);
  padding: 12px;
}

@media (max-width: 1150px) {
  .analytics-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .analytics-header {
    align-items: stretch;
  }

  .analytics-actions,
  .filter-field {
    width: 100%;
  }

  .btn,
  .filter-select {
    width: 100%;
  }

  .method-head {
    flex-direction: column;
  }
}
</style>
