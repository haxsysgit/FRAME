<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { dashboardService } from '../services/dashboard'
import { VChart } from '../lib/echarts'
import { useSettingsStore } from '../stores/settings'
import { useCurrency } from '../composables/useCurrency'

const rangeDays = ref(30)
const loading = ref(false)
const error = ref('')
const payload = ref(null)
const settingsStore = useSettingsStore()
const { format, formatCompact } = useCurrency()
const chartAnimationsEnabled = computed(() => !settingsStore.settings.accessibility.reduced_motion)

const rangeOptions = [
  { label: 'Last 7 Days', value: 7 },
  { label: 'Last 30 Days', value: 30 },
  { label: 'Last 90 Days', value: 90 },
  { label: 'Last 180 Days', value: 180 },
]

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
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return String(value)
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

const kpis = computed(() => payload.value?.kpis ?? {})
const revenueTrend = computed(() => payload.value?.revenue_trend ?? [])
const statusMix = computed(() => payload.value?.status_mix ?? [])
const paymentMix = computed(() => payload.value?.payment_mix ?? [])
const topProducts = computed(() => payload.value?.top_products ?? [])
const topStaffRows = computed(() => payload.value?.top_staff ?? [])
const topInvoices = computed(() => payload.value?.top_invoices ?? [])

const overviewCards = computed(() => [
  {
    title: 'Total Revenue',
    value: fmtCurrency(kpis.value.total_revenue),
    helper: `${rangeDays.value}-day window`,
  },
  {
    title: 'Paid Invoices',
    value: toNumber(kpis.value.paid_invoice_count).toLocaleString('en-NG'),
    helper: 'Completed and paid invoices',
  },
  {
    title: 'Average Ticket',
    value: fmtCurrency(kpis.value.average_ticket),
    helper: 'Average value per paid invoice',
  },
  {
    title: 'Total Invoices (Range)',
    value: toNumber(kpis.value.invoice_count).toLocaleString('en-NG'),
    helper: 'All statuses in selected range',
  },
])

const statusColorMap = {
  DRAFT: '#7a9991',
  STAMPED: '#0f9f89',
  DISPENSED: '#16a34a',
  CANCELLED: '#dc2626',
}

const statusMixRows = computed(() => statusMix.value.map((row) => ({
  ...row,
  label: String(row.status || '').slice(0, 1) + String(row.status || '').slice(1).toLowerCase(),
  color: statusColorMap[row.status] || '#6d8b83',
})))

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
      return `${formatDayLabel(point.axisValue)}<br/>Revenue: ${fmtCurrency(point.data)}`
    },
  },
  grid: { top: 18, right: 16, bottom: 26, left: 56 },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: revenueTrend.value.map((row) => row.day),
    axisLine: { lineStyle: { color: '#cfe2dc' } },
    axisLabel: { color: '#6d8b83', formatter: (value) => formatDayLabel(value) },
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
            { offset: 0, color: 'rgba(15, 159, 137, 0.30)' },
            { offset: 1, color: 'rgba(15, 159, 137, 0.02)' },
          ],
        },
      },
      data: revenueTrend.value.map((row) => toNumber(row.revenue)),
      emphasis: { focus: 'series' },
    },
  ],
}))

const statusChartOption = computed(() => ({
  animation: chartAnimationsEnabled.value,
  animationDuration: chartAnimationsEnabled.value ? 420 : 0,
  tooltip: {
    trigger: 'item',
    backgroundColor: '#0f172a',
    borderWidth: 0,
    textStyle: { color: '#f8fafc' },
    formatter: ({ name, value, percent }) => `${name}: ${value} (${percent}%)`,
  },
  title: {
    text: String(kpis.value.invoice_count ?? 0),
    subtext: 'Invoices',
    left: 'center',
    top: '39%',
    textStyle: { fontSize: 20, fontWeight: 700, color: '#10211d' },
    subtextStyle: { color: '#6d8b83', fontSize: 11 },
  },
  series: [
    {
      type: 'pie',
      radius: ['58%', '80%'],
      center: ['50%', '50%'],
      label: { show: false },
      data: statusMixRows.value
        .filter((row) => toNumber(row.count) > 0)
        .map((row) => ({
          name: row.label,
          value: toNumber(row.count),
          itemStyle: { color: row.color },
        })),
      emphasis: {
        scale: true,
        itemStyle: {
          shadowBlur: 14,
          shadowOffsetX: 0,
          shadowColor: 'rgba(10, 24, 21, 0.25)',
        },
      },
    },
  ],
}))

const paymentChartOption = computed(() => ({
  animation: chartAnimationsEnabled.value,
  animationDuration: chartAnimationsEnabled.value ? 420 : 0,
  tooltip: {
    trigger: 'item',
    backgroundColor: '#0f172a',
    borderWidth: 0,
    textStyle: { color: '#f8fafc' },
    formatter: ({ data }) => `${data.method}<br/>Revenue: ${fmtCurrency(data.value)}<br/>Invoices: ${data.invoice_count}`,
  },
  grid: { top: 10, right: 10, bottom: 4, left: 82 },
  xAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#d9ebe5' } },
    axisLabel: { color: '#6d8b83', formatter: (value) => compactCurrency(value) },
  },
  yAxis: {
    type: 'category',
    data: paymentMix.value.map((row) => row.method),
    axisLabel: { color: '#4f7068' },
    axisTick: { show: false },
    axisLine: { show: false },
  },
  series: [
    {
      type: 'bar',
      data: paymentMix.value.map((row) => ({
        value: toNumber(row.revenue),
        method: row.method,
        invoice_count: row.invoice_count,
        itemStyle: {
          color: '#0f9f89',
          borderRadius: [6, 6, 6, 6],
        },
      })),
      barWidth: 16,
      label: {
        show: true,
        position: 'right',
        color: '#4f7068',
        fontSize: 11,
        formatter: ({ data }) => compactCurrency(data.value),
      },
    },
  ],
}))

const topProductsBarOption = computed(() => ({
  animation: chartAnimationsEnabled.value,
  animationDuration: chartAnimationsEnabled.value ? 350 : 0,
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    backgroundColor: '#0f172a',
    borderWidth: 0,
    textStyle: { color: '#f8fafc' },
    formatter: (params) => {
      const point = Array.isArray(params) ? params[0] : params
      if (!point) return ''
      return `${point.name}<br/>Units: ${point.value}`
    },
  },
  grid: { top: 10, right: 8, bottom: 52, left: 28 },
  xAxis: {
    type: 'category',
    data: topProducts.value.slice(0, 6).map((row) => row.product_name),
    axisLabel: {
      color: '#6d8b83',
      interval: 0,
      rotate: 24,
      formatter: (value) => String(value).slice(0, 12),
    },
    axisLine: { lineStyle: { color: '#cfe2dc' } },
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#d9ebe5' } },
    axisLabel: { color: '#6d8b83' },
  },
  series: [
    {
      type: 'bar',
      barWidth: 22,
      data: topProducts.value.slice(0, 6).map((row) => toNumber(row.quantity)),
      itemStyle: { color: '#18bfa3', borderRadius: [6, 6, 0, 0] },
      emphasis: { focus: 'series' },
    },
  ],
}))

async function loadAnalytics() {
  loading.value = true
  error.value = ''

  try {
    payload.value = await dashboardService.getAnalytics({ rangeDays: rangeDays.value })
  } catch (err) {
    error.value = err?.message || 'Unable to load analytics right now.'
  } finally {
    loading.value = false
  }
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

function exportAnalyticsCsv() {
  if (!payload.value) return

  const rows = [
    ['Section', 'Metric', 'Value'],
    ['KPI', 'Revenue', toNumber(kpis.value.total_revenue)],
    ['KPI', 'Paid Invoices', toNumber(kpis.value.paid_invoice_count)],
    ['KPI', 'Average Ticket', toNumber(kpis.value.average_ticket)],
    ['KPI', 'Total Invoices (Range)', toNumber(kpis.value.invoice_count)],
    [],
    ['Status Mix', 'Status', 'Count', 'Percent'],
    ...statusMixRows.value.map((row) => ['Status Mix', row.status, toNumber(row.count), toNumber(row.percent)]),
    [],
    ['Payment Mix', 'Method', 'Revenue', 'Invoices', 'Percent'],
    ...paymentMix.value.map((row) => [
      'Payment Mix',
      row.method,
      toNumber(row.revenue),
      toNumber(row.invoice_count),
      toNumber(row.percent),
    ]),
    [],
    ['Top Products', 'Product', 'Units', 'Revenue'],
    ...topProducts.value.map((row) => ['Top Products', row.product_name, toNumber(row.quantity), toNumber(row.revenue)]),
    [],
    ['Top Staff', 'Staff', 'Invoices', 'Revenue'],
    ...topStaffRows.value.map((row) => ['Top Staff', row.name, toNumber(row.invoice_count), toNumber(row.revenue)]),
    [],
    ['Top Invoices', 'Invoice', 'Payment', 'Amount'],
    ...topInvoices.value.map((row) => ['Top Invoices', row.name || row.id, row.payment_method || '—', toNumber(row.amount)]),
  ]

  const stamp = new Date().toISOString().slice(0, 10)
  downloadCsv(`analytics-${rangeDays.value}d-${stamp}.csv`, rows)
}

function printAnalytics() {
  window.print()
}

watch(rangeDays, () => {
  loadAnalytics()
})

onMounted(loadAnalytics)
</script>

<template>
  <section class="analytics-page">
    <header class="analytics-header">
      <h2>Analytics Overview</h2>

      <div class="analytics-actions">
        <label class="filter-field">
          <span>Time range</span>
          <select v-model="rangeDays" class="filter-select">
            <option v-for="option in rangeOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>
        <button type="button" class="btn btn-secondary" :disabled="loading" @click="loadAnalytics">Refresh</button>
        <button type="button" class="btn btn-primary" :disabled="loading || !payload" @click="exportAnalyticsCsv">Export CSV</button>
        <button type="button" class="btn btn-ghost" :disabled="loading || !payload" @click="printAnalytics">Print</button>
      </div>
    </header>

    <p v-if="error" class="feedback feedback-error">{{ error }}</p>

    <div v-if="loading && !payload" class="analytics-skeleton" aria-hidden="true">
      <div class="kpi-grid">
        <article v-for="n in 4" :key="`sk-card-${n}`" class="kpi-card skeleton-block" />
      </div>
      <div class="insight-grid">
        <article v-for="n in 4" :key="`sk-insight-${n}`" class="analytics-card skeleton-block" />
      </div>
      <div class="analytics-grid">
        <article class="analytics-card skeleton-block skeleton-chart" />
        <article class="analytics-card skeleton-block skeleton-chart" />
      </div>
      <article class="analytics-card skeleton-block skeleton-table" />
      <div class="analytics-grid">
        <article class="analytics-card skeleton-block skeleton-table" />
        <article class="analytics-card skeleton-block skeleton-table" />
      </div>
    </div>

    <template v-if="payload">
      <section class="kpi-grid">
        <article v-for="card in overviewCards" :key="card.title" class="kpi-card">
          <p class="kpi-label">{{ card.title }}</p>
          <p class="kpi-value">{{ card.value }}</p>
          <p class="kpi-helper">{{ card.helper }}</p>
        </article>
      </section>

      <section class="insight-grid">
        <article class="analytics-card insight-card tone-success">
          <h3>Best Selling Product</h3>
          <p class="insight-main">{{ kpis.best_selling_product?.product_name || '—' }}</p>
          <p class="muted">{{ kpis.best_selling_product?.quantity ?? 0 }} units • {{ fmtCurrency(kpis.best_selling_product?.revenue) }}</p>
        </article>

        <article class="analytics-card insight-card tone-info">
          <h3>Highest Invoice</h3>
          <p class="insight-main">{{ compactCurrency(kpis.highest_invoice?.amount) }}</p>
          <p class="muted">{{ kpis.highest_invoice?.name || kpis.highest_invoice?.id?.slice(0, 8) || '—' }}</p>
        </article>

        <article class="analytics-card insight-card tone-success-soft">
          <h3>Top Staff Seller</h3>
          <p class="insight-main">{{ kpis.top_staff?.name || '—' }}</p>
          <p class="muted">{{ kpis.top_staff?.invoice_count ?? 0 }} invoices • {{ fmtCurrency(kpis.top_staff?.revenue) }}</p>
        </article>

        <article class="analytics-card insight-card tone-muted">
          <h3>Most Common Product</h3>
          <p class="insight-main">{{ kpis.most_common_product_today?.product_name || '—' }}</p>
          <p class="muted">Today: {{ kpis.most_common_product_today?.quantity ?? 0 }} • Week: {{ kpis.most_common_product_week?.product_name || '—' }}</p>
        </article>
      </section>

      <section class="analytics-grid">
        <article class="analytics-card">
          <header class="section-head">
            <h3>Revenue Trend</h3>
            <p>Daily revenue movement for the selected time range.</p>
          </header>
          <div class="chart-wrap">
            <VChart class="trend-chart" :option="revenueChartOption" autoresize v-if="revenueTrend.length" />
            <p v-else class="empty">No trend data in selected range.</p>
          </div>
        </article>

        <article class="analytics-card">
          <header class="section-head">
            <h3>Status and Payment Mix</h3>
            <p>View invoice statuses and payment method contribution together.</p>
          </header>

          <div class="status-wrap">
            <VChart class="status-chart" :option="statusChartOption" autoresize />

            <ul class="status-legend">
              <li v-for="item in statusMixRows" :key="item.status">
                <span class="dot" :style="{ background: item.color }" />
                <span>{{ item.label }}</span>
                <strong>{{ item.count }}</strong>
              </li>
            </ul>
          </div>

          <div class="chart-wrap compact">
            <VChart v-if="paymentMix.length" class="payment-chart" :option="paymentChartOption" autoresize />
            <p v-else class="empty">No paid invoices in this range.</p>
          </div>
        </article>
      </section>

      <article class="analytics-card">
        <header class="section-head">
          <h3>Top Selling Products</h3>
          <p>Use this panel to prioritize stock replenishment and shelf planning.</p>
        </header>

        <div class="chart-wrap" v-if="topProducts.length">
          <VChart class="products-chart" :option="topProductsBarOption" autoresize />
        </div>

        <div class="table-wrap" v-if="topProducts.length">
          <table class="analytics-table">
            <thead>
              <tr>
                <th>Product</th>
                <th class="numeric">Units</th>
                <th class="numeric">Revenue</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in topProducts" :key="row.product_id">
                <td>{{ row.product_name }}</td>
                <td class="numeric mono">{{ row.quantity }}</td>
                <td class="numeric mono">{{ fmtCurrency(row.revenue) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="empty">No top product data available.</p>
      </article>

      <section class="analytics-grid">
        <article class="analytics-card">
          <header class="section-head">
            <h3>Top Staff Performance</h3>
            <p>Staff rankings by invoice count and revenue contribution.</p>
          </header>

          <div class="table-wrap" v-if="topStaffRows.length">
            <table class="analytics-table">
              <thead>
                <tr>
                  <th>Staff</th>
                  <th class="numeric">Invoices</th>
                  <th class="numeric">Revenue</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in topStaffRows" :key="row.user_id">
                  <td>{{ row.name }}</td>
                  <td class="numeric mono">{{ row.invoice_count }}</td>
                  <td class="numeric mono">{{ fmtCurrency(row.revenue) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="empty">No staff performance data available.</p>
        </article>

        <article class="analytics-card">
          <header class="section-head">
            <h3>Highest Value Invoices</h3>
            <p>Large transactions that can affect trend interpretation.</p>
          </header>

          <div class="table-wrap" v-if="topInvoices.length">
            <table class="analytics-table">
              <thead>
                <tr>
                  <th>Invoice</th>
                  <th>Method</th>
                  <th class="numeric">Amount</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in topInvoices" :key="row.id">
                  <td class="mono">{{ row.name || row.id.slice(0, 8) }}</td>
                  <td>{{ row.payment_method || '—' }}</td>
                  <td class="numeric mono">{{ fmtCurrency(row.amount) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="empty">No high-value invoice data available.</p>
        </article>
      </section>
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
  min-width: 190px;
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

.insight-grid {
  display: grid;
  gap: var(--space-3);
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
}

.analytics-card {
  padding: var(--space-4);
  display: grid;
  gap: var(--space-3);
}

.insight-card h3 {
  margin: 0;
  font-size: 15px;
}

.insight-main {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
}

.tone-success {
  background: var(--success-bg);
  border-color: var(--success-tint);
}

.tone-info {
  background: var(--primary-bg);
  border-color: var(--primary-tint);
}

.tone-success-soft {
  background: rgba(22, 163, 74, 0.06);
  border-color: rgba(22, 163, 74, 0.2);
}

.tone-muted {
  background: var(--bg-muted);
}

.analytics-grid {
  display: grid;
  gap: var(--space-3);
  grid-template-columns: repeat(2, minmax(0, 1fr));
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

.chart-wrap.compact {
  padding-bottom: 4px;
}

.trend-chart {
  width: 100%;
  height: 260px;
}

.status-wrap {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 12px;
  align-items: center;
}

.status-chart {
  width: 156px;
  height: 156px;
}

.status-legend {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 6px;
}

.status-legend li {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 8px;
  align-items: center;
  font-size: 12px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: var(--radius-full);
  display: inline-block;
}

.payment-chart {
  width: 100%;
  height: 210px;
}

.products-chart {
  width: 100%;
  height: 230px;
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

.mono {
  font-family: var(--font-data);
}

.muted {
  margin: 0;
  color: var(--text-secondary);
  font-size: 13px;
}

.empty {
  margin: 0;
  color: var(--text-muted);
  padding: 12px;
}

.analytics-skeleton {
  display: grid;
  gap: var(--space-3);
}

.skeleton-block {
  border-color: transparent;
  background: linear-gradient(90deg, var(--bg-elevated) 25%, var(--bg-card) 37%, var(--bg-elevated) 63%);
  background-size: 400% 100%;
  animation: analytics-shimmer 1.2s linear infinite;
}

.kpi-grid .skeleton-block {
  min-height: 100px;
}

.insight-grid .skeleton-block {
  min-height: 120px;
}

.skeleton-chart {
  min-height: 300px;
}

.skeleton-table {
  min-height: 220px;
}

@keyframes analytics-shimmer {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: 0 0;
  }
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

  .status-wrap {
    grid-template-columns: 1fr;
    justify-items: center;
  }
}
</style>
