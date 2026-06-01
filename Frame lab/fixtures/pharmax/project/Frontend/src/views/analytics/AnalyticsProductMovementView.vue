<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { dashboardService } from '@/services/dashboard'
import { VChart } from '@/lib/echarts'
import { useSettingsStore } from '@/stores/settings'
import { useCurrency } from '@/composables/useCurrency'

const loading = ref(false)
const error = ref('')
const payload = ref(null)
const stockSnapshot = ref({ out_of_stock_count: 0, low_stock_items: [] })
const rangeDays = ref(30)
const settingsStore = useSettingsStore()
const { format, formatCompact } = useCurrency()
const chartAnimationsEnabled = computed(() => !settingsStore.settings.accessibility.reduced_motion)

const rangeOptions = [
  { label: 'Last 7 Days', value: 7 },
  { label: 'Last 30 Days', value: 30 },
  { label: 'Last 90 Days', value: 90 },
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
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return String(value)
  return parsed.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

const rows = computed(() => payload.value?.top_products ?? [])
const revenueTrend = computed(() => payload.value?.revenue_trend ?? [])
const movementRows = computed(() => rows.value.slice(0, 8))

const outOfStockCount = computed(() => toNumber(stockSnapshot.value?.out_of_stock_count))
const lowStockItems = computed(() => (
  Array.isArray(stockSnapshot.value?.low_stock_items) ? stockSnapshot.value.low_stock_items : []
))
const lowStockOnlyCount = computed(() => (
  lowStockItems.value.filter((item) => toNumber(item.quantity_on_hand) > 0).length
))

const outOfStockPreview = computed(() => (
  lowStockItems.value
    .filter((item) => toNumber(item.quantity_on_hand) <= 0)
    .slice(0, 2)
    .map((item) => item.name)
    .join(', ')
))

const lowStockPreview = computed(() => (
  lowStockItems.value
    .filter((item) => toNumber(item.quantity_on_hand) > 0)
    .slice(0, 2)
    .map((item) => item.name)
    .join(', ')
))

const topSeller = computed(() => rows.value[0] ?? null)
const slowMover = computed(() => {
  const positiveRows = rows.value.filter((row) => toNumber(row.quantity) > 0)
  if (!positiveRows.length) return null
  return [...positiveRows].sort((a, b) => toNumber(a.quantity) - toNumber(b.quantity))[0]
})

const quantityStats = computed(() => {
  const quantities = movementRows.value
    .map((row) => toNumber(row.quantity))
    .filter((quantity) => quantity > 0)

  if (!quantities.length) return { fastCutoff: 0, slowCutoff: 0 }

  const max = Math.max(...quantities)
  return {
    fastCutoff: max * 0.65,
    slowCutoff: max * 0.25,
  }
})

function movementTrend(row) {
  const quantity = toNumber(row?.quantity)
  if (quantity <= 0) return { label: 'No sales', tone: 'neutral' }
  if (quantity >= quantityStats.value.fastCutoff) return { label: 'Fast', tone: 'fast' }
  if (quantity <= quantityStats.value.slowCutoff) return { label: 'Slow', tone: 'slow' }
  return { label: 'Stable', tone: 'stable' }
}

const tableRows = computed(() => movementRows.value.map((row) => ({ ...row, trend: movementTrend(row) })))

const summaryCards = computed(() => [
  {
    title: 'Top Selling Product',
    value: topSeller.value?.product_name || '—',
    helper: topSeller.value ? `${toNumber(topSeller.value.quantity).toLocaleString('en-NG')} units sold` : 'No sales yet',
    helperTone: 'success',
  },
  {
    title: 'Slow Mover',
    value: slowMover.value?.product_name || '—',
    helper: slowMover.value ? `${toNumber(slowMover.value.quantity).toLocaleString('en-NG')} units sold` : 'No movement data yet',
    helperTone: 'muted',
  },
  {
    title: 'Low Stock Items',
    value: lowStockOnlyCount.value.toLocaleString('en-NG'),
    helper: lowStockOnlyCount.value > 0 ? 'Needs reorder soon' : 'Stock level looks healthy',
    helperTone: lowStockOnlyCount.value > 0 ? 'warning' : 'success',
  },
  {
    title: 'Out-of-Stock Items',
    value: outOfStockCount.value.toLocaleString('en-NG'),
    helper: outOfStockCount.value > 0 ? 'Urgent action required' : 'No stock-out right now',
    helperTone: outOfStockCount.value > 0 ? 'danger' : 'success',
  },
])

const stockActionMessage = computed(() => {
  if (outOfStockCount.value > 0) {
    return 'Move urgent restock items first and check substitutes for walk-in patients.'
  }
  if (lowStockOnlyCount.value > 0) {
    return 'Prepare reorder before weekend demand to avoid unexpected stock-outs.'
  }
  if (slowMover.value?.product_name) {
    return `Stock risk is low. Consider promoting ${slowMover.value.product_name} to improve turnover.`
  }
  return 'Stock risk is low. Keep monitoring product movement daily.'
})

const timelineOption = computed(() => ({
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
      const row = revenueTrend.value[Number(point.dataIndex || 0)]
      return `${formatDayLabel(row?.day)}<br/>Sales value: ${fmtCurrency(point.data)}<br/>Invoices: ${toNumber(row?.invoice_count).toLocaleString('en-NG')}`
    },
  },
  grid: { top: 18, right: 16, bottom: 26, left: 56 },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: revenueTrend.value.map((row) => formatDayLabel(row.day)),
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
            { offset: 0, color: 'rgba(15, 159, 137, 0.26)' },
            { offset: 1, color: 'rgba(15, 159, 137, 0.02)' },
          ],
        },
      },
      data: revenueTrend.value.map((row) => toNumber(row.revenue)),
    },
  ],
}))

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
    ['Section', 'Metric', 'Value'],
    ['Summary', 'Top Selling Product', topSeller.value?.product_name || '—'],
    ['Summary', 'Slow Mover', slowMover.value?.product_name || '—'],
    ['Stock Risk', 'Out-of-Stock Items', outOfStockCount.value],
    ['Stock Risk', 'Low Stock Items', lowStockOnlyCount.value],
    [],
    ['Top Products by Movement', 'Product', 'Units Sold', 'Revenue', 'Trend'],
    ...tableRows.value.map((row) => [
      'Top Products by Movement',
      row.product_name,
      toNumber(row.quantity),
      toNumber(row.revenue),
      row.trend.label,
    ]),
  ]
  downloadCsv(`analytics-product-insights-${rangeDays.value}d.csv`, dataRows)
}

function printReport() {
  window.print()
}

async function loadData() {
  loading.value = true
  error.value = ''

  try {
    const [analytics, metrics] = await Promise.all([
      dashboardService.getAnalytics({
        rangeDays: rangeDays.value,
        includeContext: false,
        topN: 20,
        staffLimit: 5,
        invoiceLimit: 5,
      }),
      dashboardService.getMetrics(),
    ])
    payload.value = analytics
    stockSnapshot.value = {
      out_of_stock_count: toNumber(metrics?.out_of_stock_count),
      low_stock_items: Array.isArray(metrics?.low_stock_items) ? metrics.low_stock_items : [],
    }
  } catch (err) {
    error.value = err?.message || 'Could not load product insights right now.'
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
      <h2>Product Insights</h2>

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
    <p v-else-if="loading" class="feedback">Loading product insights...</p>

    <template v-else>
      <section class="kpi-grid">
        <article v-for="card in summaryCards" :key="card.title" class="kpi-card">
          <p class="kpi-label">{{ card.title }}</p>
          <p class="kpi-value">{{ card.value }}</p>
          <p class="kpi-helper" :class="`helper-${card.helperTone}`">{{ card.helper }}</p>
        </article>
      </section>

      <section class="analytics-grid">
        <article class="analytics-card">
          <header class="section-head">
            <h3>Top Products by Movement</h3>
            <p>Shows high-demand products and current movement pace.</p>
          </header>

          <div class="table-wrap">
            <table class="analytics-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th class="numeric">Units Sold</th>
                  <th class="numeric">Revenue</th>
                  <th>Trend</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in tableRows" :key="row.product_id || row.product_name">
                  <td>{{ row.product_name }}</td>
                  <td class="numeric">{{ toNumber(row.quantity).toLocaleString('en-NG') }}</td>
                  <td class="numeric">{{ fmtCurrency(row.revenue) }}</td>
                  <td>
                    <span class="trend-pill" :class="`trend-${row.trend.tone}`">{{ row.trend.label }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
            <p v-if="tableRows.length === 0" class="empty">No product movement data for this period.</p>
          </div>
        </article>

        <article class="analytics-card">
          <header class="section-head">
            <h3>Stock Risk Watch</h3>
            <p>Stock pressure signals for reorder planning.</p>
          </header>

          <div class="insight-list">
            <div class="insight tone-danger">
              <strong>Out-of-Stock: {{ outOfStockCount.toLocaleString('en-NG') }} items</strong>
              <span>{{ outOfStockCount > 0 ? (outOfStockPreview || 'Immediate restock required') : 'No out-of-stock items right now' }}</span>
            </div>

            <div class="insight tone-warning">
              <strong>Low Stock: {{ lowStockOnlyCount.toLocaleString('en-NG') }} items</strong>
              <span>{{ lowStockOnlyCount > 0 ? (lowStockPreview || 'Reorder before weekend') : 'No low-stock pressure right now' }}</span>
            </div>

            <div class="insight tone-info">
              <strong>Next Step</strong>
              <span>{{ stockActionMessage }}</span>
            </div>
          </div>
        </article>
      </section>

      <article class="analytics-card">
        <header class="section-head">
          <h3>Movement Timeline</h3>
          <p>Daily movement summary to support stock and staffing plans.</p>
        </header>

        <div v-if="revenueTrend.length" class="chart-wrap">
          <VChart class="chart" :option="timelineOption" autoresize />
        </div>
        <p v-else class="empty">No daily movement timeline available yet.</p>
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
}

.helper-success {
  color: var(--success);
}

.helper-warning {
  color: var(--warning);
}

.helper-danger {
  color: var(--error);
}

.helper-muted {
  color: var(--text-muted);
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

.trend-pill {
  border-radius: var(--radius-full);
  padding: 2px 9px;
  font-size: 11px;
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
}

.trend-fast {
  color: var(--success);
  border-color: var(--success-tint);
  background: var(--success-bg);
}

.trend-stable {
  color: var(--primary);
  border-color: var(--primary-tint);
  background: var(--primary-bg);
}

.trend-slow {
  color: var(--warning);
  border-color: var(--warning-tint);
  background: var(--warning-bg);
}

.trend-neutral {
  color: var(--text-secondary);
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

.tone-danger {
  background: var(--error-bg);
  border-color: var(--error-tint);
}

.tone-warning {
  background: var(--warning-bg);
  border-color: var(--warning-tint);
}

.tone-info {
  background: var(--primary-bg);
  border-color: var(--primary-tint);
}

.chart-wrap {
  border: 1px solid var(--table-border);
  border-radius: var(--radius-md);
  background: var(--bg-recessed);
  padding: 8px;
}

.chart {
  width: 100%;
  height: 220px;
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
