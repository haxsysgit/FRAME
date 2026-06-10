<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { dashboardService } from '../services/dashboard'
import { useAuthStore } from '@/stores/auth'
import { printStructuredReport } from '@/lib/reportPrint'
import { useCurrency } from '@/composables/useCurrency'

const { formatSimple } = useCurrency()

function isoLocalDate(value = new Date()) {
  const date = new Date(value)
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset())
  return date.toISOString().slice(0, 10)
}

const dateLabelFormatter = new Intl.DateTimeFormat(undefined, {
  weekday: 'short',
  month: 'short',
  day: 'numeric',
  year: 'numeric',
})

const dateTimeFormatter = new Intl.DateTimeFormat(undefined, {
  month: 'short',
  day: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
})

const todayDate = isoLocalDate()
const selectedDate = ref(todayDate)
const loading = ref(false)
const error = ref('')
const payload = ref(null)
const auth = useAuthStore()

function toNumber(value) {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

function fmtCurrency(value) {
  return formatSimple(value, 0)
}

function fmtDateLabel(value) {
  if (!value) return '—'
  const date = new Date(`${value}T00:00:00`)
  if (Number.isNaN(date.getTime())) return value
  return dateLabelFormatter.format(date)
}

function fmtDateTime(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return dateTimeFormatter.format(date)
}

function csvValue(value) {
  const text = String(value ?? '')
  if (text.includes('"') || text.includes(',') || text.includes('\n')) {
    return `"${text.replace(/"/g, '""')}"`
  }
  return text
}

function downloadCsv(filename, rows) {
  const csv = rows.map((row) => row.map(csvValue).join(',')).join('\n')
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

const reportKpis = computed(() => payload.value?.kpis ?? {
  paid_revenue: 0,
  cancelled_value: 0,
  credit_outstanding: 0,
  low_stock_items_count: 0,
})

const invoiceSummary = computed(() => payload.value?.invoice_summary ?? {
  DRAFT: 0,
  STAMPED: 0,
  DISPENSED: 0,
  CANCELLED: 0,
})

const invoiceStatusRows = computed(() => [
  {
    label: 'Draft',
    value: toNumber(invoiceSummary.value.DRAFT),
    action: 'Finish draft invoices',
    route: '/invoices',
  },
  {
    label: 'Stamped',
    value: toNumber(invoiceSummary.value.STAMPED),
    action: 'Review cashier queue',
    route: '/cashier',
  },
  {
    label: 'Dispensed',
    value: toNumber(invoiceSummary.value.DISPENSED),
    action: 'Open invoice history',
    route: '/invoices',
  },
  {
    label: 'Cancelled',
    value: toNumber(invoiceSummary.value.CANCELLED),
    action: 'Review cancellations',
    route: '/invoices',
  },
])

const totalInvoices = computed(() => (
  invoiceStatusRows.value.reduce((sum, row) => sum + row.value, 0)
))

const lowStockReport = computed(() => (payload.value?.low_stock_items ?? []).slice(0, 10))
const creditInvoices = computed(() => payload.value?.credit_invoices ?? [])
const creditInvoiceCount = computed(() => creditInvoices.value.length)
const reportDate = computed(() => payload.value?.as_of_date || selectedDate.value)
const reportDateLabel = computed(() => fmtDateLabel(reportDate.value))

function exportCsv() {
  if (!payload.value) return

  const rows = [
    ['Section', 'Metric', 'Value'],
    ['KPI', 'Paid Revenue', toNumber(reportKpis.value.paid_revenue)],
    ['KPI', 'Credit Outstanding', toNumber(reportKpis.value.credit_outstanding)],
    ['KPI', 'Cancelled Value', toNumber(reportKpis.value.cancelled_value)],
    ['KPI', 'Low Stock Items Count', toNumber(reportKpis.value.low_stock_items_count)],
    ['KPI', 'Credit Invoices Count', toNumber(creditInvoiceCount.value)],
    [],
    ['Invoice Summary', 'Status', 'Count'],
    ['Invoice Summary', 'DRAFT', toNumber(invoiceSummary.value.DRAFT)],
    ['Invoice Summary', 'STAMPED', toNumber(invoiceSummary.value.STAMPED)],
    ['Invoice Summary', 'DISPENSED', toNumber(invoiceSummary.value.DISPENSED)],
    ['Invoice Summary', 'CANCELLED', toNumber(invoiceSummary.value.CANCELLED)],
    [],
    ['Low Stock', 'Product', 'On Hand', 'Reorder Level'],
    ...lowStockReport.value.map((item) => ['Low Stock', item.name, toNumber(item.quantity_on_hand), toNumber(item.reorder_level)]),
    [],
    ['Credit Invoices', 'Invoice', 'Status', 'Payment Method', 'Amount', 'Created'],
    ...creditInvoices.value.map((inv) => [
      'Credit Invoices',
      inv.name || inv.id,
      inv.status,
      inv.payment_method || 'CREDIT',
      toNumber(inv.total_amount),
      fmtDateTime(inv.created_at),
    ]),
  ]

  downloadCsv(`end-of-day-${reportDate.value}.csv`, rows)
}

function printReport() {
  if (!payload.value) return

  const invoiceRows = invoiceStatusRows.value.map((row) => [
    row.label,
    row.value.toLocaleString(),
  ])

  const lowStockRows = lowStockReport.value.map((item) => [
    item.name,
    Number(item.quantity_on_hand || 0).toLocaleString(),
    Number(item.reorder_level || 0).toLocaleString(),
  ])

  const creditRows = creditInvoices.value.map((inv) => [
    inv.name || inv.id,
    inv.status || 'UNKNOWN',
    inv.payment_method || 'CREDIT',
    fmtCurrency(inv.total_amount),
    fmtDateTime(inv.created_at),
  ])

  printStructuredReport({
    title: 'End of Day Report',
    subtitle: 'Daily closing summary for handover and follow-up.',
    reportDateLabel: reportDateLabel.value,
    generatedBy: auth.user?.full_name || auth.user?.username,
    highlights: [
      { label: 'Total Invoices', value: totalInvoices.value.toLocaleString() },
      { label: 'Money Collected', value: fmtCurrency(reportKpis.value.paid_revenue) },
      { label: 'Credit Outstanding', value: fmtCurrency(reportKpis.value.credit_outstanding) },
      { label: 'Cancelled Value', value: fmtCurrency(reportKpis.value.cancelled_value) },
      { label: 'Low Stock Items', value: Number(reportKpis.value.low_stock_items_count || 0).toLocaleString() },
      { label: 'Credit Invoices', value: creditInvoiceCount.value.toLocaleString() },
    ],
    tables: [
      {
        title: 'Invoice Status Summary',
        columns: ['Status', 'Count'],
        rows: invoiceRows,
      },
      {
        title: 'Low Stock Alerts',
        columns: ['Product', 'On Hand', 'Reorder'],
        rows: lowStockRows,
        emptyMessage: 'No low-stock items currently.',
      },
      {
        title: 'Credit Invoices to Follow Up',
        columns: ['Invoice', 'Status', 'Payment', 'Amount', 'Created'],
        rows: creditRows,
        emptyMessage: 'No recent credit invoices.',
      },
    ],
  })
}

async function loadReportData() {
  loading.value = true
  error.value = ''

  try {
    payload.value = await dashboardService.getEndOfDay({ rangeDays: 1, asOfDate: selectedDate.value })
  } catch (err) {
    error.value = err?.message || 'Failed to load end-of-day report data.'
  } finally {
    loading.value = false
  }
}

function setTodayDate() {
  if (selectedDate.value === todayDate) {
    loadReportData()
    return
  }
  selectedDate.value = todayDate
}

watch(selectedDate, loadReportData)
onMounted(loadReportData)
</script>

<template>
  <section class="report-page">
    <header class="report-header">
      <div class="header-copy">
        <h1>End of Day Report</h1>
        <p>Showing {{ reportDateLabel }}. Use this page to close the shift quickly.</p>
      </div>

      <div class="report-actions">
        <label class="filter-field" for="report-date">
          <span>Report date</span>
          <div class="date-control">
            <input id="report-date" v-model="selectedDate" class="date-input" type="date" :max="todayDate" />
            <button type="button" class="btn btn-light" :disabled="loading || selectedDate === todayDate" @click="setTodayDate">
              Today
            </button>
          </div>
        </label>

        <div class="action-buttons">
          <button
            type="button"
            class="btn btn-primary"
            :disabled="loading || !payload"
            @click="exportCsv"
          >
            Export CSV
          </button>
          <button
            type="button"
            class="btn btn-secondary"
            :disabled="loading || !payload"
            @click="printReport"
          >
            Print
          </button>
          <button type="button" class="btn" :disabled="loading" @click="loadReportData">Refresh</button>
        </div>
      </div>
    </header>

    <p v-if="error" class="feedback feedback-error">{{ error }}</p>
    <p v-else-if="loading" class="feedback">Loading end-of-day report...</p>

    <template v-else>
      <section class="kpi-grid">
        <article class="kpi-card">
          <p class="kpi-label">Total invoices</p>
          <p class="kpi-value">{{ totalInvoices.toLocaleString() }}</p>
        </article>
        <article class="kpi-card">
          <p class="kpi-label">Money collected</p>
          <p class="kpi-value">{{ fmtCurrency(reportKpis.paid_revenue) }}</p>
        </article>
        <article class="kpi-card">
          <p class="kpi-label">Credit to collect</p>
          <p class="kpi-value">{{ fmtCurrency(reportKpis.credit_outstanding) }}</p>
        </article>
        <article class="kpi-card">
          <p class="kpi-label">Cancelled value</p>
          <p class="kpi-value">{{ fmtCurrency(reportKpis.cancelled_value) }}</p>
        </article>
        <article class="kpi-card">
          <p class="kpi-label">Low-stock products</p>
          <p class="kpi-value">{{ toNumber(reportKpis.low_stock_items_count).toLocaleString() }}</p>
        </article>
        <article class="kpi-card">
          <p class="kpi-label">Credit invoices</p>
          <p class="kpi-value">{{ creditInvoiceCount.toLocaleString() }}</p>
        </article>
      </section>

      <nav class="ops-nav" aria-label="End-of-day quick actions">
        <RouterLink to="/invoices" class="ops-link primary">Review invoices</RouterLink>
        <RouterLink to="/cashier" class="ops-link">Open cashier queue</RouterLink>
        <RouterLink to="/stock" class="ops-link">Open stock adjustments</RouterLink>
        <RouterLink to="/stock/low-stock" class="ops-link">Low-stock watchlist</RouterLink>
      </nav>

      <section class="content-grid">
        <article class="report-card">
          <header class="section-head">
            <div>
              <h2>Invoice summary</h2>
              <p>See what still needs action before close.</p>
            </div>
            <RouterLink to="/invoices" class="section-link">Open invoices</RouterLink>
          </header>
          <div class="table-wrap">
            <table class="report-table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th class="numeric">Count</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="status in invoiceStatusRows" :key="status.label">
                  <td>{{ status.label }}</td>
                  <td class="numeric">{{ status.value.toLocaleString() }}</td>
                  <td>
                    <RouterLink v-if="status.value > 0" :to="status.route" class="table-link">{{ status.action }}</RouterLink>
                    <span v-else class="muted">No action</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article class="report-card">
          <header class="section-head">
            <div>
              <h2>Low stock to restock</h2>
              <p>Restock these items before the next shift.</p>
            </div>
            <RouterLink to="/stock/low-stock" class="section-link">Open watchlist</RouterLink>
          </header>
          <div class="table-wrap">
            <table v-if="lowStockReport.length" class="report-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th class="numeric">On hand</th>
                  <th class="numeric">Reorder level</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in lowStockReport" :key="item.id">
                  <td>{{ item.name }}</td>
                  <td class="numeric">{{ toNumber(item.quantity_on_hand).toLocaleString() }}</td>
                  <td class="numeric">{{ toNumber(item.reorder_level).toLocaleString() }}</td>
                  <td>
                    <RouterLink to="/stock" class="table-link">Adjust stock</RouterLink>
                  </td>
                </tr>
              </tbody>
            </table>
            <p v-else class="empty">No low-stock items currently.</p>
          </div>
        </article>
      </section>

      <article class="report-card">
        <header class="section-head">
          <div>
            <h2>Credit follow-up list</h2>
            <p>Follow up before the next shift starts.</p>
          </div>
          <RouterLink to="/cashier" class="section-link">Open cashier queue</RouterLink>
        </header>
        <div class="table-wrap">
          <table v-if="creditInvoices.length" class="report-table">
            <thead>
              <tr>
                <th>Invoice</th>
                <th>Status</th>
                <th>Payment</th>
                <th class="numeric">Amount</th>
                <th>Created</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="inv in creditInvoices" :key="inv.id">
                <td class="mono">{{ inv.name || inv.id.slice(0, 8) }}</td>
                <td>{{ inv.status || 'Unknown' }}</td>
                <td>{{ inv.payment_method || 'CREDIT' }}</td>
                <td class="numeric">{{ fmtCurrency(inv.total_amount) }}</td>
                <td class="mono">{{ fmtDateTime(inv.created_at) }}</td>
                <td>
                  <RouterLink :to="`/invoices/${inv.id}`" class="table-link">Open</RouterLink>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-else class="empty">No recent credit invoices.</p>
        </div>
      </article>
    </template>
  </section>
</template>

<style scoped>
.report-page {
  display: grid;
  gap: var(--space-3);
}

.report-header {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
  padding: var(--space-2) var(--space-3);
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.header-copy {
  display: grid;
  gap: 3px;
}

.header-copy h1 {
  margin: 0;
  font-size: clamp(18px, 1.7vw, 24px);
  line-height: 1.2;
}

.header-copy p {
  margin: 0;
  font-size: 12px;
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
  gap: 4px;
  min-width: 240px;
}

.filter-field span {
  font-size: 12px;
  color: var(--text-muted);
}

.date-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-input {
  min-height: 40px;
  padding: 0 10px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-primary);
  min-width: 0;
  flex: 1;
}

.action-buttons {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.btn {
  min-height: 40px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
  background: var(--bg-card);
  color: var(--text-primary);
  padding: 0 12px;
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

.btn-light {
  background: var(--bg-elevated);
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
  gap: var(--space-2);
  grid-template-columns: repeat(auto-fit, minmax(165px, 1fr));
}

.kpi-card {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
  padding: var(--space-2) var(--space-3);
  display: grid;
  gap: 4px;
}

.kpi-label {
  margin: 0;
  color: var(--text-muted);
  font-size: 11px;
}

.kpi-value {
  margin: 0;
  font-size: clamp(18px, 1.9vw, 24px);
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-data);
  word-break: break-word;
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
  padding: 0 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  font-size: 12px;
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

.content-grid {
  display: grid;
  gap: var(--space-3);
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.report-card {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-2);
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.section-head h2 {
  margin: 0;
  font-size: 17px;
}

.section-head p {
  margin: 3px 0 0;
  color: var(--text-secondary);
  font-size: 12px;
}

.section-link,
.table-link {
  color: var(--primary);
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
}

.section-link:hover,
.table-link:hover {
  text-decoration: underline;
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
  padding: 9px 12px;
  border-bottom: 1px solid var(--table-border);
  text-align: left;
  vertical-align: middle;
}

.report-table th {
  background: var(--table-header-bg);
  color: var(--text-secondary);
  font-size: 11px;
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

.mono {
  font-family: var(--font-data);
}

.muted {
  color: var(--text-muted);
  font-size: 12px;
}

.empty {
  margin: 0;
  color: var(--text-muted);
  padding: 12px;
}

@media (max-width: 1080px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .report-header {
    align-items: stretch;
  }

  .report-actions,
  .filter-field,
  .date-control,
  .action-buttons {
    width: 100%;
  }

  .date-input {
    width: 100%;
  }

  .action-buttons .btn {
    flex: 1 1 120px;
  }
}

@media print {
  .report-actions,
  .ops-nav,
  .section-link,
  .table-link {
    display: none;
  }

  .report-header,
  .report-card,
  .kpi-card {
    box-shadow: none;
  }

  .report-table tbody tr:nth-child(even) {
    background: transparent;
  }
}
</style>
