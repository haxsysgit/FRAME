<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { dashboardService } from '@/services/dashboard'
import { VChart } from '@/lib/echarts'
import { useSettingsStore } from '@/stores/settings'
import { useCurrency } from '@/composables/useCurrency'

const loading = ref(false)
const error = ref('')
const payload = ref(null)
const rangeDays = ref(30)
const settingsStore = useSettingsStore()
const { format, formatCompact } = useCurrency()
const chartAnimationsEnabled = computed(() => !settingsStore.settings.accessibility.reduced_motion)

const rangeOptions = [
  { label: 'Last 7 Days', value: 7 },
  { label: 'Last 30 Days', value: 30 },
  { label: 'Last 90 Days', value: 90 },
]

const rows = computed(() => payload.value?.revenue_trend ?? [])
const kpis = computed(() => payload.value?.kpis ?? {})

function toNumber(value) {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

function fmtCurrency(value) {
  return format(value, { decimals: 0 })
}

function compactCurrency(value) {
  return formatCompact(value)
}

function formatDayLabel(value) {
  if (!value) return '—'
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return String(value)
  return parsed.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
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

function rowLabel(row) {
  return formatDayLabel(row?.bucket_label || row?.day || row?.bucket_key)
}

function rowAverageTicket(row) {
  const invoiceCount = toNumber(row?.invoice_count)
  if (invoiceCount <= 0) return 0
  return toNumber(row?.revenue) / invoiceCount
}

const peakDay = computed(() => {
  if (!rows.value.length) return null
  return rows.value.reduce((max, row) => (toNumber(row.revenue) > toNumber(max.revenue) ? row : max), rows.value[0])
})

const lowestDay = computed(() => {
  if (!rows.value.length) return null
  return rows.value.reduce((min, row) => (toNumber(row.revenue) < toNumber(min.revenue) ? row : min), rows.value[0])
})

const metricCards = computed(() => [
  {
    title: 'Total Revenue',
    value: fmtCurrency(kpis.value.total_revenue),
    helper: `${rows.value.length} day entries`,
  },
  {
    title: 'Paid Invoices',
    value: toNumber(kpis.value.paid_invoice_count).toLocaleString('en-NG'),
    helper: 'Completed sales only',
  },
  {
    title: 'Average Sale',
    value: fmtCurrency(kpis.value.average_ticket),
    helper: 'Average per paid invoice',
  },
  {
    title: 'Peak Day',
    value: peakDay.value ? rowLabel(peakDay.value) : '—',
    helper: peakDay.value ? fmtCurrency(peakDay.value.revenue) : 'No data yet',
  },
])

function rowTrend(index) {
  if (index === 0) return { label: 'Starting point', tone: 'neutral' }
  const current = toNumber(rows.value[index]?.revenue)
  const previous = toNumber(rows.value[index - 1]?.revenue)

  if (previous <= 0 && current > 0) return { label: 'Up', tone: 'up' }
  if (previous <= 0) return { label: 'Stable', tone: 'neutral' }

  const deltaPercent = ((current - previous) / previous) * 100
  if (deltaPercent >= 8) return { label: 'Up', tone: 'up' }
  if (deltaPercent <= -8) return { label: 'Needs review', tone: 'warn' }
  return { label: 'Stable', tone: 'stable' }
}

const actionMessage = computed(() => {
  if (rows.value.length < 2) return 'Not enough data yet. Keep recording invoices to see trends.'
  const recent = rows.value.slice(-3)
  if (recent.length >= 2) {
    const drops = recent.slice(1).filter((row, idx) => toNumber(row.revenue) < toNumber(recent[idx].revenue))
    if (drops.length >= 2) {
      return 'Revenue dropped in two consecutive periods. Check stock availability and queue speed.'
    }
  }
  return 'Revenue trend is stable. Keep using peak days to plan staffing and stock levels.'
})

const revenueChartOption = computed(() => ({
  animation: chartAnimationsEnabled.value,
  animationDuration: chartAnimationsEnabled.value ? 450 : 0,
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#0f172a',
    borderWidth: 0,
    textStyle: { color: '#f8fafc' },
    formatter: (params) => {
      const point = Array.isArray(params) ? params[0] : params
      if (!point) return ''
      const index = Number(point.dataIndex || 0)
      const row = rows.value[index]
      return `${rowLabel(row)}<br/>Revenue: ${fmtCurrency(point.data)}<br/>Invoices: ${toNumber(row?.invoice_count).toLocaleString('en-NG')}`
    },
  },
  grid: { top: 18, right: 16, bottom: 26, left: 56 },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: rows.value.map((row) => rowLabel(row)),
    axisLine: { lineStyle: { color: '#cfe2dc' } },
    axisLabel: { color: '#6d8b83' },
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#d9ebe5' } },
    axisLabel: { color: '#6d8b83', formatter: (value) => compactCurrency(value) },
  },
  series: [
    {
      type: 'line',
      smooth: true,
      showSymbol: false,
      lineStyle: { width: 2.6, color: '#0f9f89' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(15, 159, 137, 0.28)' },
            { offset: 1, color: 'rgba(15, 159, 137, 0.02)' },
          ],
        },
      },
      data: rows.value.map((row) => toNumber(row.revenue)),
    },
  ],
}))

function exportCsv() {
  const dataRows = [
    ['Date', 'Revenue', 'Paid Invoices', 'Average Sale', 'Trend'],
    ...rows.value.map((row, index) => [
      rowLabel(row),
      toNumber(row.revenue),
      toNumber(row.invoice_count),
      Math.round(rowAverageTicket(row)),
      rowTrend(index).label,
    ]),
  ]
  downloadCsv(`analytics-revenue-trend-${rangeDays.value}d.csv`, dataRows)
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
      includeContext: true,
      topN: 10,
      staffLimit: 5,
      invoiceLimit: 5,
    })
  } catch (err) {
    error.value = err?.message || 'Could not load revenue trend data.'
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
      <h2>Revenue Trend</h2>

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
    <p v-else-if="loading" class="feedback">Loading revenue trend...</p>

    <template v-else>
      <section class="kpi-grid">
        <article v-for="card in metricCards" :key="card.title" class="kpi-card">
          <p class="kpi-label">{{ card.title }}</p>
          <p class="kpi-value">{{ card.value }}</p>
          <p class="kpi-helper">{{ card.helper }}</p>
        </article>
      </section>

      <section class="analytics-grid">
        <article class="analytics-card chart-panel">
          <header class="section-head">
            <h3>Revenue Over Time</h3>
            <p>Daily paid revenue for the selected period.</p>
          </header>
          <div class="chart-wrap">
            <VChart class="chart" :option="revenueChartOption" autoresize />
          </div>
        </article>

        <article class="analytics-card insights-panel">
          <header class="section-head">
            <h3>Highlights</h3>
            <p>Use these notes for daily handover decisions.</p>
          </header>

          <div class="insight-list">
            <div class="insight tone-success">
              <strong>Best Day: {{ peakDay ? rowLabel(peakDay) : '—' }}</strong>
              <span>{{ peakDay ? fmtCurrency(peakDay.revenue) : 'No data yet' }}</span>
            </div>
            <div class="insight tone-info">
              <strong>Lowest Day: {{ lowestDay ? rowLabel(lowestDay) : '—' }}</strong>
              <span>{{ lowestDay ? fmtCurrency(lowestDay.revenue) : 'No data yet' }}</span>
            </div>
            <div class="insight tone-warning">
              <strong>Next Step</strong>
              <span>{{ actionMessage }}</span>
            </div>
          </div>
        </article>
      </section>

      <article class="analytics-card">
        <header class="section-head">
          <h3>Daily Breakdown</h3>
          <p>Use this table to review unusual days and explain trend changes to your team.</p>
        </header>

        <div class="table-wrap">
          <table class="analytics-table">
            <thead>
              <tr>
                <th>Date</th>
                <th class="numeric">Revenue</th>
                <th class="numeric">Invoices</th>
                <th class="numeric">Average Sale</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in rows" :key="row.day || row.bucket_key || index">
                <td>{{ rowLabel(row) }}</td>
                <td class="numeric">{{ fmtCurrency(row.revenue) }}</td>
                <td class="numeric">{{ toNumber(row.invoice_count).toLocaleString('en-NG') }}</td>
                <td class="numeric">{{ fmtCurrency(rowAverageTicket(row)) }}</td>
                <td>
                  <span class="trend-pill" :class="`trend-${rowTrend(index).tone}`">{{ rowTrend(index).label }}</span>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-if="rows.length === 0" class="empty">No revenue trend data available for this period.</p>
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
  font-size: clamp(22px, 2.2vw, 30px);
  font-family: var(--font-data);
  font-weight: 700;
  color: var(--text-primary);
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

.chart-wrap {
  border: 1px solid var(--table-border);
  border-radius: var(--radius-md);
  background: var(--bg-recessed);
  padding: 8px;
}

.chart {
  width: 100%;
  height: 320px;
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

.table-wrap {
  overflow: auto;
  border: 1px solid var(--table-border);
  border-radius: var(--radius-md);
  background: var(--bg-card);
}

.analytics-table {
  width: 100%;
  min-width: 640px;
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

.trend-pill {
  border-radius: var(--radius-full);
  padding: 2px 9px;
  font-size: 11px;
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
}

.trend-up {
  color: var(--success);
  border-color: var(--success-tint);
  background: var(--success-bg);
}

.trend-warn {
  color: var(--warning);
  border-color: var(--warning-tint);
  background: var(--warning-bg);
}

.trend-stable {
  color: var(--primary);
  border-color: var(--primary-tint);
  background: var(--primary-bg);
}

.trend-neutral {
  color: var(--text-secondary);
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

  .analytics-table {
    min-width: 560px;
  }
}
</style>
