<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useDashboardStore } from '../stores/dashboard'
import { dashboardService } from '../services/dashboard'
import { VChart } from '../lib/echarts'
import { useSettingsStore } from '../stores/settings'
import { useCurrency } from '../composables/useCurrency'

const dash = useDashboardStore()
const settingsStore = useSettingsStore()
const { format: fmtCurrency, formatCompact, symbol: currencySymbol } = useCurrency()

const analytics = ref(null)
const chartsLoading = ref(false)
const chartsError = ref('')
const chartRange = ref(30)
const lastUpdatedAt = ref(null)

const rangeOptions = [
  { label: '7 days', value: 7 },
  { label: '30 days', value: 30 },
  { label: '90 days', value: 90 },
  { label: '180 days', value: 180 },
]

const quickActions = [
  { label: 'Create invoice', to: '/invoices/create' },
  { label: 'Open invoices', to: '/invoices' },
  { label: 'Check stock', to: '/stock' },
]

const statusColors = {
  DRAFT: '#94a3b8',
  STAMPED: '#2563eb',
  DISPENSED: '#22c55e',
  CANCELLED: '#ef4444',
}

const paymentColors = {
  CASH: '#2563eb',
  CARD: '#14b8a6',
  BANK_TRANSFER: '#8b5cf6',
  CREDIT: '#f59e0b',
  TRANSFER: '#8b5cf6',
  UNKNOWN: '#94a3b8',
}

function toNumber(value) {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

function fmt(n) {
  return formatCompact(n)
}

function compactCurrency(n) {
  return formatCompact(n)
}

function formatDayLabel(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return String(value)
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

function toTitleLabel(value, fallback = '—') {
  if (value === null || value === undefined || value === '') return fallback
  return String(value)
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, (m) => m.toUpperCase())
}

function countLabel(count, noun) {
  const value = toNumber(count)
  return `${value.toLocaleString()} ${noun}${value === 1 ? '' : 's'}`
}

function paymentMethodLabel(method) {
  return toTitleLabel(method, 'Not set')
}

function statusText(status) {
  return toTitleLabel(status, 'Unknown')
}

function stockAlertLevel(item) {
  const qty = toNumber(item?.quantity_on_hand)
  const reorder = toNumber(item?.reorder_level)
  if (qty <= 0) return 'critical'
  if (reorder > 0 && qty <= reorder * 0.5) return 'warning'
  return 'watch'
}

function stockAlertLabel(item) {
  const level = stockAlertLevel(item)
  if (level === 'critical') return 'Out of stock'
  if (level === 'warning') return 'Critical low'
  return 'Low stock'
}

function signalToneClass(tone) {
  if (tone === 'error') return 'signal-pill--error'
  if (tone === 'warning') return 'signal-pill--warning'
  if (tone === 'info') return 'signal-pill--info'
  return 'signal-pill--neutral'
}

function statusClass(status) {
  const s = String(status ?? '').toLowerCase()
  if (s === 'dispensed') return 'dispensed'
  if (s === 'stamped' || s === 'finalized') return 'finalized'
  if (s === 'draft') return 'draft'
  if (s === 'cancelled') return 'cancelled'
  if (s === 'credit') return 'credit'
  return 'draft'
}

const todayLabel = computed(() => new Date().toLocaleDateString(undefined, {
  weekday: 'long',
  month: 'short',
  day: 'numeric',
  year: 'numeric',
}))

const lastUpdatedLabel = computed(() => {
  if (!lastUpdatedAt.value) return 'Waiting for first refresh'
  return lastUpdatedAt.value.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
})

const isRefreshing = computed(() => dash.loading || chartsLoading.value)
const activeRangeLabel = computed(() => rangeOptions.find((o) => o.value === chartRange.value)?.label ?? '30 days')
const chartAnimationsEnabled = computed(() => !settingsStore.settings.accessibility.reduced_motion)
const lowStockThreshold = computed(() => {
  const raw = Number(settingsStore.settings.workflow?.low_stock_alert_threshold)
  if (!Number.isFinite(raw)) return 10
  return Math.max(1, Math.round(raw))
})

const kpis = computed(() => analytics.value?.kpis ?? {})
const revenueTrend = computed(() => analytics.value?.revenue_trend ?? [])
const statusMix = computed(() => analytics.value?.status_mix ?? [])
const paymentMix = computed(() => analytics.value?.payment_mix ?? [])
const attentionSignals = computed(() => {
  const signals = []
  const outOfStock = toNumber(dash.outOfStockCount)
  const lowStock = Array.isArray(dash.lowStockItems)
    ? dash.lowStockItems.filter((item) => toNumber(item?.quantity_on_hand) <= lowStockThreshold.value).length
    : 0
  const pendingStock = toNumber(dash.pendingStockAdjustments)
  const pendingUsers = toNumber(dash.pendingUserApprovals)
  const cancelledToday = toNumber(dash.cancelledInvoiceCountToday)
  const outstandingCredit = toNumber(dash.creditOutstanding)

  if (outOfStock > 0) {
    signals.push({ key: 'out-of-stock', label: 'Out of stock', value: countLabel(outOfStock, 'item'), tone: 'error' })
  }
  if (lowStock > 0) {
    signals.push({ key: 'low-stock', label: 'Running low', value: countLabel(lowStock, 'item'), tone: 'warning' })
  }
  if (outstandingCredit > 0) {
    signals.push({ key: 'credit', label: 'Outstanding credit', value: fmt(outstandingCredit), tone: 'warning' })
  }
  if (pendingStock > 0) {
    signals.push({ key: 'pending-stock', label: 'Stock approvals', value: countLabel(pendingStock, 'request'), tone: 'info' })
  }
  if (pendingUsers > 0) {
    signals.push({ key: 'pending-users', label: 'User approvals', value: countLabel(pendingUsers, 'request'), tone: 'info' })
  }
  if (cancelledToday > 0) {
    signals.push({ key: 'cancelled', label: 'Cancelled invoices', value: countLabel(cancelledToday, 'invoice'), tone: 'error' })
  }

  return signals
})

const statusMixRows = computed(() => statusMix.value.map((row) => ({
  ...row,
  label: String(row.status || '').slice(0, 1) + String(row.status || '').slice(1).toLowerCase(),
  color: statusColors[row.status] || statusColors.DRAFT,
})))

const paymentMixRows = computed(() => paymentMix.value.map((row) => ({
  ...row,
  color: paymentColors[row.method] || paymentColors.UNKNOWN,
})))

const peakDay = computed(() => {
  if (!revenueTrend.value.length) return null
  return revenueTrend.value.reduce((max, row) => (toNumber(row.revenue) > toNumber(max.revenue) ? row : max), revenueTrend.value[0])
})

const revenueChartOption = computed(() => ({
  animation: chartAnimationsEnabled.value,
  animationDuration: chartAnimationsEnabled.value ? 450 : 0,
  animationDurationUpdate: chartAnimationsEnabled.value ? 250 : 0,
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#0f172a',
    borderWidth: 0,
    textStyle: { color: '#f8fafc' },
    formatter: (params) => {
      const point = Array.isArray(params) ? params[0] : params
      if (!point) return ''
      return `${formatDayLabel(point.axisValue)}<br/>Revenue: ${fmt(point.data)}`
    },
  },
  grid: { top: 24, right: 18, bottom: 24, left: 56 },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: revenueTrend.value.map((row) => row.day),
    axisLine: { lineStyle: { color: '#dbe5ea' } },
    axisLabel: {
      color: '#94a3b8',
      formatter: (value) => formatDayLabel(value),
    },
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#e2e8f0' } },
    axisLabel: { color: '#94a3b8', formatter: (value) => compactCurrency(value) },
  },
  series: [
    {
      type: 'line',
      smooth: true,
      showSymbol: false,
      lineStyle: { width: 2.5, color: '#10b981' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(16,185,129,0.35)' },
            { offset: 1, color: 'rgba(16,185,129,0.02)' },
          ],
        },
      },
      data: revenueTrend.value.map((row) => toNumber(row.revenue)),
      emphasis: { focus: 'series' },
    },
  ],
}))

const statusDonutOption = computed(() => ({
  animation: chartAnimationsEnabled.value,
  animationDuration: chartAnimationsEnabled.value ? 400 : 0,
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
    textStyle: { fontSize: 18, fontWeight: 700, color: '#0f172a' },
    subtextStyle: { color: '#94a3b8', fontSize: 10 },
  },
  series: [
    {
      type: 'pie',
      radius: ['55%', '78%'],
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
          shadowColor: 'rgba(15,23,42,0.25)',
        },
      },
    },
  ],
}))

const paymentBarOption = computed(() => ({
  animation: chartAnimationsEnabled.value,
  animationDuration: chartAnimationsEnabled.value ? 400 : 0,
  tooltip: {
    trigger: 'item',
    backgroundColor: '#0f172a',
    borderWidth: 0,
    textStyle: { color: '#f8fafc' },
    formatter: ({ data }) => `${data.method}<br/>Revenue: ${fmt(data.value)}<br/>Invoices: ${data.invoice_count}`,
  },
  grid: { top: 8, right: 14, bottom: 6, left: 76 },
  xAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#e2e8f0' } },
    axisLabel: { color: '#94a3b8', formatter: (value) => compactCurrency(value) },
  },
  yAxis: {
    type: 'category',
    data: paymentMixRows.value.map((row) => row.method),
    axisLabel: { color: '#64748b' },
    axisTick: { show: false },
    axisLine: { show: false },
  },
  series: [
    {
      type: 'bar',
      data: paymentMixRows.value.map((row) => ({
        value: toNumber(row.revenue),
        method: row.method,
        invoice_count: row.invoice_count,
        itemStyle: {
          color: row.color,
          borderRadius: [6, 6, 6, 6],
        },
      })),
      barWidth: 18,
      label: {
        show: true,
        position: 'right',
        color: '#64748b',
        fontSize: 11,
        formatter: ({ data }) => `${compactCurrency(data.value)}`,
      },
      emphasis: { focus: 'series' },
    },
  ],
}))

async function loadChartData() {
  chartsLoading.value = true
  chartsError.value = ''

  try {
    analytics.value = await dashboardService.getAnalytics({ rangeDays: chartRange.value })
  } catch (err) {
    chartsError.value = err?.message || 'Could not load analytics charts.'
  } finally {
    chartsLoading.value = false
  }
}

async function refreshAll() {
  await Promise.all([
    dash.load(true),
    loadChartData(),
  ])
  lastUpdatedAt.value = new Date()
}

watch(chartRange, () => {
  loadChartData()
})

onMounted(() => {
  refreshAll()
})
</script>

<template>
  <section class="dashboard">
    <header class="dashboard-head">
      <div class="head-row">
        <p class="head-date">{{ todayLabel }}</p>
        <p class="head-updated">Last refresh: <strong>{{ lastUpdatedLabel }}</strong></p>
      </div>
      <div class="head-actions">
        <div class="range-switch">
          <button
            v-for="option in rangeOptions"
            :key="option.value"
            type="button"
            class="range-switch-btn"
            :class="{ active: chartRange === option.value }"
            @click="chartRange = option.value"
          >
            {{ option.label }}
          </button>
        </div>
        <button type="button" class="ghost-button" :disabled="isRefreshing" @click="refreshAll">
          {{ isRefreshing ? 'Refreshing…' : 'Refresh data' }}
        </button>
      </div>
    </header>

    <p v-if="dash.error" class="error-banner phx-state phx-state--error">{{ dash.error }}</p>
    <p v-if="chartsError" class="error-banner phx-state phx-state--error">{{ chartsError }}</p>

    <nav class="quick-actions phx-panel" aria-label="Quick actions">
      <p class="quick-actions-label">Quick actions</p>
      <div class="quick-actions-list">
        <RouterLink
          v-for="action in quickActions"
          :key="action.to"
          :to="action.to"
          class="quick-action-link"
        >
          {{ action.label }}
        </RouterLink>
      </div>
    </nav>

    <section class="attention-strip phx-panel">
      <div class="attention-head">
        <h2>Attention needed</h2>
        <p class="panel-sub">Items to follow up today.</p>
      </div>
      <p v-if="dash.loading" class="muted">Checking operational alerts…</p>
      <ul v-else-if="attentionSignals.length" class="signal-list">
        <li
          v-for="signal in attentionSignals"
          :key="signal.key"
          class="signal-pill"
          :class="signalToneClass(signal.tone)"
        >
          <span>{{ signal.label }}</span>
          <strong>{{ signal.value }}</strong>
        </li>
      </ul>
      <p v-else class="signal-ok phx-state phx-state--success">No urgent issues right now.</p>
    </section>

    <div class="metrics-grid">
      <article class="metric-card">
        <p class="metric-label">Sales collected today</p>
        <p class="metric-value">{{ dash.loading ? '…' : fmt(dash.todayRevenue) }}</p>
        <p class="metric-change" :class="dash.todayInvoiceCount > 0 ? 'positive' : ''">
          {{ dash.loading ? '' : dash.todayInvoiceCount > 0 ? countLabel(dash.todayInvoiceCount, 'paid invoice') : 'No paid invoice yet today' }}
        </p>
      </article>
      <article class="metric-card">
        <p class="metric-label">Products in catalog</p>
        <p class="metric-value">{{ dash.loading ? '…' : dash.activeProducts.toLocaleString() }}</p>
        <p
          class="metric-change"
          :class="dash.lowStockItems.length > 0 || dash.outOfStockCount > 0 ? 'negative' : 'positive'"
        >
          {{
            dash.loading
              ? ''
              : dash.outOfStockCount > 0
                ? `${countLabel(dash.outOfStockCount, 'item')} out of stock`
                : dash.lowStockItems.length > 0
                  ? `${countLabel(dash.lowStockItems.length, 'item')} running low`
                  : 'Stock levels are stable'
          }}
        </p>
      </article>
      <article class="metric-card">
        <p class="metric-label">Invoices raised today</p>
        <p class="metric-value">{{ dash.loading ? '…' : dash.todayInvoiceCount }}</p>
        <p class="metric-change positive">{{ dash.loading ? '' : `${countLabel(dash.totalInvoices, 'invoice')} total` }}</p>
      </article>
      <article class="metric-card">
        <p class="metric-label">Outstanding credit</p>
        <p class="metric-value">{{ dash.loading ? '…' : fmt(dash.creditOutstanding) }}</p>
        <p class="metric-change" :class="dash.creditOutstanding > 0 ? 'negative' : 'positive'">
          {{ dash.creditOutstanding > 0 ? 'Follow up unpaid balances' : 'No unpaid balances' }}
        </p>
      </article>
    </div>

    <div class="charts-grid">
      <article class="panel chart-panel trend-panel">
        <div class="panel-head compact">
          <div>
            <h2>Sales trend</h2>
            <p class="panel-sub">Paid sales over the last {{ activeRangeLabel }}</p>
          </div>
          <p class="panel-kpi">Best day {{ peakDay ? compactCurrency(peakDay.revenue) : compactCurrency(0) }}</p>
        </div>

        <div v-if="chartsLoading" class="loading-skeleton" aria-hidden="true" />
        <v-chart
          v-else-if="revenueTrend.length"
          class="trend-chart"
          :option="revenueChartOption"
          autoresize
        />
        <p v-else class="muted">No paid revenue data in selected range.</p>

        <div class="trend-foot">
          <p class="muted" v-if="peakDay">Best day: <strong>{{ formatDayLabel(peakDay.day) }}</strong> ({{ fmt(peakDay.revenue) }})</p>
          <p class="muted">Average paid sale: <strong>{{ fmt(kpis.average_ticket) }}</strong></p>
        </div>
      </article>

      <article class="panel chart-panel">
        <div class="panel-head compact">
          <div>
            <h2>Sales breakdown</h2>
            <p class="panel-sub">Invoice status and payment mix</p>
          </div>
        </div>

        <div v-if="chartsLoading" class="loading-skeleton loading-skeleton--mix" aria-hidden="true" />
        <div v-else class="mix-layout">
          <div class="status-ring-block">
            <v-chart
              class="status-chart"
              :option="statusDonutOption"
              autoresize
            />

            <ul class="status-legend">
              <li v-for="row in statusMixRows" :key="row.status">
                <span class="dot" :style="{ background: row.color }" />
                <span>{{ row.label }}</span>
                <strong>{{ row.count }}</strong>
              </li>
            </ul>
          </div>

          <div class="payment-block">
            <p class="panel-sub">Revenue by payment method</p>
            <v-chart
              v-if="paymentMixRows.length"
              class="payment-chart"
              :option="paymentBarOption"
              autoresize
            />
            <p v-else class="muted">No paid invoices in selected range.</p>
          </div>
        </div>
      </article>
    </div>

    <div class="split-grid">
      <article class="panel">
        <div class="panel-head">
          <h2>Recent Invoices</h2>
          <RouterLink to="/invoices" class="panel-action">Open invoices</RouterLink>
        </div>
        <div v-if="dash.loading" class="loading-row phx-state phx-state--empty">Loading…</div>
        <table v-else>
          <thead>
            <tr>
              <th>Invoice</th>
              <th>Staff ID</th>
              <th>Amount</th>
              <th>Payment type</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="dash.recentInvoices.length === 0">
              <td colspan="5" class="empty phx-empty-cell">No invoices recorded yet.</td>
            </tr>
            <tr v-for="inv in dash.recentInvoices" :key="inv.id">
              <td class="mono inv-id">{{ inv.name ?? inv.id.slice(0, 8) }}</td>
              <td class="muted">{{ inv.sold_by_id?.slice(0, 8) ?? 'Not set' }}</td>
              <td class="mono">{{ inv.total_amount != null ? fmt(inv.total_amount) : '—' }}</td>
              <td class="muted">{{ paymentMethodLabel(inv.payment_method) }}</td>
              <td><span class="status" :class="statusClass(inv.status)">{{ statusText(inv.status) }}</span></td>
            </tr>
          </tbody>
        </table>
      </article>

      <article class="panel">
        <div class="panel-head">
          <h2>Low Stock Alerts</h2>
          <RouterLink to="/stock" class="panel-action">Manage stock</RouterLink>
        </div>
        <div v-if="dash.loading" class="loading-row phx-state phx-state--empty">Loading…</div>
        <ul v-else-if="dash.lowStockItems.length > 0" class="alerts">
          <li v-for="item in dash.lowStockItems.slice(0, 6)" :key="item.id">
            <div>
              <p class="alert-name">{{ item.name }}</p>
              <p class="alert-detail">Reorder at {{ item.reorder_level }} • Current {{ item.quantity_on_hand }}</p>
            </div>
            <div class="alert-side">
              <p class="alert-state" :class="`alert-state--${stockAlertLevel(item)}`">{{ stockAlertLabel(item) }}</p>
              <p class="mono alert-qty">{{ item.quantity_on_hand }} in stock</p>
            </div>
          </li>
        </ul>
        <p v-else class="all-clear phx-state phx-state--success">Stock levels are within reorder targets.</p>
      </article>
    </div>

  </section>
</template>

<style scoped>
.dashboard {
  display: grid;
  gap: var(--space-4);
}

.dashboard-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-2) 0;
  margin-bottom: var(--space-3);
}

.head-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.head-date {
  margin: 0;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.head-updated {
  margin: 0;
  color: var(--text-muted);
  font-size: 12px;
}

.head-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.range-switch {
  display: inline-flex;
  gap: 4px;
  border-radius: 999px;
  padding: 4px;
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
  box-shadow: var(--shadow-xs);
}

.range-switch-btn {
  border: none;
  background: transparent;
  color: var(--text-muted);
  min-height: 40px;
  min-width: 68px;
  padding: 0 12px;
  border-radius: 999px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
}

.range-switch-btn.active {
  background: var(--primary);
  color: var(--text-inverse);
  box-shadow: var(--shadow-xs);
}

.ghost-button,
.panel-action {
  min-height: 40px;
  padding: 0 var(--space-3);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.ghost-button:hover,
.panel-action:hover {
  background: var(--bg-hover);
  border-color: var(--primary);
  color: var(--primary);
}

.ghost-button:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.error-banner {
  margin: 0;
  padding: 10px 12px;
  border: 1px solid var(--error-tint);
  border-radius: var(--radius-md);
  background: var(--error-bg);
  color: var(--error);
  font-size: 13px;
}

.quick-actions {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
  padding: var(--space-3) var(--space-4);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}

.quick-actions-label {
  margin: 0;
  color: var(--text-tertiary);
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.quick-actions-list {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.quick-action-link {
  display: inline-flex;
  align-items: center;
  min-height: 40px;
  padding: 0 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
  transition: all var(--transition-fast);
}

.quick-action-link:hover {
  background: var(--bg-hover);
  border-color: var(--primary);
  color: var(--primary);
}

.attention-strip {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
  padding: var(--space-3) var(--space-4);
  display: grid;
  gap: var(--space-2);
}

.attention-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: var(--space-3);
}

.signal-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.signal-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 999px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  padding: 4px 10px;
  font-size: 12px;
}

.signal-pill--error {
  color: var(--error);
  border-color: var(--error-tint);
  background: var(--error-bg);
}

.signal-pill--warning {
  color: var(--warning);
  border-color: var(--warning-tint);
  background: var(--warning-bg);
}

.signal-pill--info {
  color: var(--info);
  border-color: var(--info-tint);
  background: var(--info-bg);
}

.signal-pill--neutral {
  color: var(--text-secondary);
}

.signal-ok {
  margin: 0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--space-4);
}

.metric-card {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background:
    linear-gradient(180deg, rgba(255,255,255,0.45) 0%, rgba(255,255,255,0) 52%),
    var(--bg-card);
  padding: var(--space-4);
  box-shadow: var(--shadow-xs);
  transition: box-shadow var(--transition-fast), border-color var(--transition-fast), transform var(--transition-fast);
  position: relative;
  overflow: hidden;
}

.metric-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--primary);
  transform: translateY(-2px);
}

.metric-card::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
  opacity: 0.85;
}

.metric-label {
  margin: 0;
  color: var(--text-tertiary);
  font-size: 13px;
  font-weight: 500;
}

.metric-value {
  margin: var(--space-2) 0 0;
  font-family: var(--font-data);
  font-size: clamp(24px, 2vw, 32px);
  font-weight: 600;
  line-height: 1.1;
  letter-spacing: -0.03em;
  color: var(--text-primary);
}

.metric-change {
  margin: var(--space-2) 0 0;
  font-size: 12px;
  font-weight: 500;
}

.metric-change.positive {
  color: var(--success);
}

.metric-change.negative {
  color: var(--error);
}

.charts-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr);
  gap: var(--space-4);
}

.split-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) minmax(0, 1fr);
  gap: var(--space-4);
}

.panel {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  padding: var(--space-5);
  box-shadow: var(--shadow-xs);
  min-width: 0;
}

.chart-panel {
  padding: var(--space-4);
  overflow: hidden;
  min-width: 0;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px dashed var(--border-subtle);
}

.panel-head.compact {
  margin-bottom: var(--space-3);
}

h2 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.panel-sub {
  margin: 4px 0 0;
  color: var(--text-muted);
  font-size: 12px;
}

.panel-kpi {
  margin: 0;
  font-size: 12px;
  color: var(--success);
  font-weight: 600;
}

.trend-chart {
  width: 100%;
  height: 278px;
}

.trend-foot {
  margin-top: var(--space-3);
  display: flex;
  justify-content: space-between;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.mix-layout {
  display: grid;
  gap: var(--space-4);
  min-width: 0;
  overflow: hidden;
}

.status-ring-block {
  display: grid;
  grid-template-columns: 130px minmax(0, 1fr);
  align-items: center;
  gap: var(--space-3);
  min-width: 0;
}

.status-chart {
  width: 130px;
  height: 130px;
}

.status-legend {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
}

.status-legend li {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  display: inline-block;
}

.payment-block {
  min-width: 0;
  overflow: hidden;
}

.payment-chart {
  width: 100%;
  height: 180px;
  min-width: 0;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  text-align: left;
  font-size: 11px;
  color: var(--text-muted);
  padding: 10px 8px;
  font-weight: 600;
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-muted);
}

td {
  padding: 12px 8px;
  border-top: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  font-size: 13px;
}

tbody tr:hover td {
  background: var(--bg-hover);
}

.mono {
  font-family: var(--font-data);
}

.status {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  height: 22px;
  padding: 0 10px;
  font-size: 11px;
}

.status.dispensed {
  color: var(--success);
  background: var(--success-bg);
}

.status.finalized {
  color: var(--primary);
  background: var(--primary-tint);
}

.status.draft {
  color: var(--text-muted);
  background: var(--bg-elevated);
}

.status.cancelled {
  color: var(--error);
  background: var(--error-bg);
}

.status.credit {
  color: var(--warning);
  background: var(--warning-bg);
}

.alerts {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
}

.alerts li {
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  background: var(--bg-elevated);
  padding: 10px 12px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.alert-side {
  display: grid;
  justify-items: end;
  align-content: center;
  gap: 4px;
}

.alert-name {
  margin: 0;
  font-size: 13px;
}

.alert-detail {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--text-muted);
}

.alert-state {
  margin: 0;
  font-size: 11px;
  font-weight: 600;
  border-radius: 999px;
  padding: 2px 8px;
}

.alert-state--critical {
  color: var(--error);
  background: var(--error-bg);
}

.alert-state--warning {
  color: var(--warning);
  background: var(--warning-bg);
}

.alert-state--watch {
  color: var(--info);
  background: var(--info-bg);
}

.alert-qty {
  color: var(--warning);
  font-weight: 600;
  font-size: 13px;
  margin: 0;
}

.loading-row {
  padding: 24px;
  text-align: center;
  font-size: 13px;
  color: var(--text-muted);
}

.loading-skeleton {
  height: 220px;
  border-radius: 12px;
  background: linear-gradient(90deg, var(--bg-elevated) 25%, var(--bg-card) 37%, var(--bg-elevated) 63%);
  background-size: 400% 100%;
  animation: loading-shimmer 1.2s linear infinite;
}

.loading-skeleton--mix {
  height: 280px;
}

@keyframes loading-shimmer {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: 0 0;
  }
}

.empty {
  text-align: center;
  color: var(--text-muted);
  padding: 24px;
  border-top: none;
}

.all-clear {
  padding: 24px;
  text-align: center;
  font-size: 13px;
  color: var(--success);
  margin: 0;
}

.inv-id {
  color: var(--text-primary);
  font-size: 12px;
}

.muted {
  color: var(--text-muted);
  font-size: 12px;
  margin: 0;
}

@media (max-width: 1240px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }

  .split-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1160px) {
  .metrics-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .dashboard-head {
    flex-direction: column;
    align-items: stretch;
  }

  .quick-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .attention-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .head-actions {
    justify-content: space-between;
  }

  .status-ring-block {
    grid-template-columns: 1fr;
    justify-items: center;
  }

  .trend-foot {
    flex-direction: column;
  }

  .alerts li {
    flex-direction: column;
    align-items: flex-start;
  }

  .alert-side {
    justify-items: start;
  }
}

@media (max-width: 640px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .range-switch {
    width: 100%;
    justify-content: space-between;
  }

  .range-switch-btn {
    flex: 1 1 auto;
  }

  .head-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
