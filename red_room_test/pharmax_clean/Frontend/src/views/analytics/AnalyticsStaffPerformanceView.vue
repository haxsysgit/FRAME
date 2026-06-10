<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { dashboardService } from '@/services/dashboard'
import { useCurrency } from '@/composables/useCurrency'

const loading = ref(false)
const error = ref('')
const payload = ref(null)
const rangeDays = ref(30)
const { format } = useCurrency()

const staffRows = computed(() => payload.value?.top_staff ?? [])
const invoiceRows = computed(() => payload.value?.top_invoices ?? [])

function toNumber(value) {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

function fmtCurrency(value) {
  return format(value, { decimals: 0 })
}

const topPerformer = computed(() => (
  [...staffRows.value].sort((a, b) => toNumber(b.revenue) - toNumber(a.revenue))[0] || null
))

const totalInvoices = computed(() => (
  staffRows.value.reduce((sum, row) => sum + toNumber(row.invoice_count), 0)
))

const totalRevenue = computed(() => (
  staffRows.value.reduce((sum, row) => sum + toNumber(row.revenue), 0)
))

const summaryCards = computed(() => [
  {
    title: 'Team Members Listed',
    value: staffRows.value.length.toLocaleString('en-NG'),
    helper: 'Staff with recorded invoices in range',
  },
  {
    title: 'Total Team Invoices',
    value: totalInvoices.value.toLocaleString('en-NG'),
    helper: 'Combined invoice count from listed staff',
  },
  {
    title: 'Total Team Revenue',
    value: fmtCurrency(totalRevenue.value),
    helper: 'Revenue contributed by listed staff',
  },
  {
    title: 'Top Performer',
    value: topPerformer.value?.name || '—',
    helper: topPerformer.value ? fmtCurrency(topPerformer.value.revenue) : 'No staff data yet',
  },
])

const coachingMessage = computed(() => {
  if (!staffRows.value.length) return 'No staff performance data yet. Keep logging sales to see coaching tips.'
  if (staffRows.value.length === 1) return 'Only one staff member has sales in this range. Add more data for team comparison.'

  const averageRevenue = totalRevenue.value / staffRows.value.length
  if (topPerformer.value && toNumber(topPerformer.value.revenue) > averageRevenue * 1.7) {
    return `Top performer is far ahead. Ask ${topPerformer.value.name} to share winning sales steps with the team.`
  }
  return 'Results are close across the team. Keep weekly check-ins focused on patient service and clear add-on suggestions.'
})

const invoiceInsight = computed(() => {
  const highest = invoiceRows.value[0]
  if (!highest) return 'No large invoices in this period yet.'
  return `Largest invoice: ${highest.name || highest.id} (${fmtCurrency(highest.amount)}).`
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
  const dataRows = [
    ['Section', 'Name', 'Invoices', 'Revenue'],
    ...staffRows.value.map((row) => ['Staff Performance', row.name, toNumber(row.invoice_count), toNumber(row.revenue)]),
    [],
    ['Section', 'Invoice', 'Payment Method', 'Amount'],
    ...invoiceRows.value.map((row) => [
      'Highest Invoices',
      row.name || row.id,
      row.payment_method || '—',
      toNumber(row.amount),
    ]),
  ]
  downloadCsv(`analytics-staff-performance-${rangeDays.value}d.csv`, dataRows)
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
      staffLimit: 10,
      invoiceLimit: 10,
    })
  } catch (err) {
    error.value = err?.message || 'Could not load staff performance right now.'
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
      <h2>Staff Performance</h2>

      <div class="analytics-actions">
        <label class="filter-field">
          <span>Time range</span>
          <select v-model="rangeDays" class="filter-select">
            <option :value="7">Last 7 Days</option>
            <option :value="30">Last 30 Days</option>
            <option :value="90">Last 90 Days</option>
          </select>
        </label>
        <button type="button" class="btn btn-secondary" :disabled="loading" @click="loadData">Refresh</button>
        <button type="button" class="btn btn-primary" :disabled="loading" @click="exportCsv">Export CSV</button>
        <button type="button" class="btn btn-ghost" :disabled="loading" @click="printReport">Print</button>
      </div>
    </header>

    <p v-if="error" class="feedback feedback-error">{{ error }}</p>
    <p v-else-if="loading" class="feedback">Loading staff performance...</p>

    <template v-else>
      <section class="kpi-grid">
        <article v-for="card in summaryCards" :key="card.title" class="kpi-card">
          <p class="kpi-label">{{ card.title }}</p>
          <p class="kpi-value">{{ card.value }}</p>
          <p class="kpi-helper">{{ card.helper }}</p>
        </article>
      </section>

      <section class="analytics-grid">
        <article class="analytics-card">
          <header class="section-head">
            <h3>Staff Comparison Table</h3>
            <p>Use this table to see each staff member's invoice count and sales value.</p>
          </header>

          <div class="table-wrap">
            <table class="analytics-table">
              <thead>
                <tr>
                  <th>Staff Name</th>
                  <th class="numeric">Invoices</th>
                  <th class="numeric">Revenue</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in staffRows" :key="row.staff_id || row.name">
                  <td>{{ row.name }}</td>
                  <td class="numeric">{{ toNumber(row.invoice_count).toLocaleString('en-NG') }}</td>
                  <td class="numeric">{{ fmtCurrency(row.revenue) }}</td>
                </tr>
              </tbody>
            </table>
            <p v-if="!staffRows.length" class="empty">No staff sales found for this time range.</p>
          </div>
        </article>

        <article class="analytics-card">
          <header class="section-head">
            <h3>Coaching Insights</h3>
            <p>Quick notes for team follow-up.</p>
          </header>

          <div class="insight-list">
            <div class="insight tone-success">
              <strong>Top Performer</strong>
              <span>
                {{ topPerformer ? `${topPerformer.name} with ${fmtCurrency(topPerformer.revenue)} revenue.` : 'No top performer yet.' }}
              </span>
            </div>
            <div class="insight tone-info">
              <strong>Largest Invoice</strong>
              <span>{{ invoiceInsight }}</span>
            </div>
            <div class="insight tone-warning">
              <strong>Next Step</strong>
              <span>{{ coachingMessage }}</span>
            </div>
          </div>
        </article>
      </section>

      <article class="analytics-card">
        <header class="section-head">
          <h3>Largest Invoices</h3>
          <p>Use this table to spot big sales that can raise one person's totals.</p>
        </header>

        <div class="table-wrap">
          <table class="analytics-table">
            <thead>
              <tr>
                <th>Invoice</th>
                <th>Payment</th>
                <th class="numeric">Amount</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in invoiceRows" :key="row.id">
                <td>{{ row.name || row.id }}</td>
                <td>{{ row.payment_method || '—' }}</td>
                <td class="numeric">{{ fmtCurrency(row.amount) }}</td>
              </tr>
            </tbody>
          </table>
          <p v-if="!invoiceRows.length" class="empty">No large invoice records found for this time range.</p>
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
  padding: var(--space-4);
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: var(--space-3);
  flex-wrap: wrap;
  background: linear-gradient(145deg, var(--bg-card), var(--bg-muted));
}

.analytics-header h2 {
  margin: 0;
  font-size: 24px;
}

.analytics-actions {
  display: flex;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.filter-field {
  display: grid;
  gap: 6px;
  min-width: 180px;
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
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.kpi-card {
  padding: var(--space-3);
  display: grid;
  gap: 6px;
}

.kpi-label {
  margin: 0;
  font-size: 12px;
  color: var(--text-muted);
}

.kpi-value {
  margin: 0;
  font-size: clamp(21px, 2vw, 28px);
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
  grid-template-columns: minmax(0, 1.55fr) minmax(0, 0.95fr);
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

.table-wrap {
  overflow: auto;
  border: 1px solid var(--table-border);
  border-radius: var(--radius-md);
  background: var(--bg-card);
}

.analytics-table {
  width: 100%;
  min-width: 520px;
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

.insight-list {
  display: grid;
  gap: 10px;
}

.insight {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  display: grid;
  gap: 4px;
}

.insight strong {
  font-size: 14px;
}

.insight span {
  font-size: 12px;
  color: var(--text-secondary);
}

.tone-success {
  background: var(--success-bg);
  border-color: var(--success-tint);
}

.tone-info {
  background: var(--primary-bg);
  border-color: var(--primary-tint);
}

.tone-warning {
  background: var(--warning-bg);
  border-color: var(--warning-tint);
}

.empty {
  margin: 0;
  color: var(--text-muted);
  padding: 12px;
}

@media (max-width: 1200px) {
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
}
</style>
