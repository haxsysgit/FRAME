<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { useCurrency } from '@/composables/useCurrency'
import { usersService } from '@/services/users'

const auth = useAuthStore()
const toast = useToast()
const { formatSimple } = useCurrency()

const loading = ref(false)
const error = ref('')
const logs = ref([])
const users = ref([])
const selectedLog = ref(null)
const showTechnicalDetails = ref(false)
const showRawJson = ref(false)

const filters = ref({
  search: '',
  action: '',
  resourceType: '',
  actorUserId: '',
  period: 'all',
  sort: 'desc',
  timePreset: '7d',
  fromLocal: '',
  toLocal: '',
  limit: 180,
})

const canSeeAllActors = computed(() => auth.userRole === 'ADMIN' || auth.userRole === 'CASHIER')
const isAdmin = computed(() => auth.userRole === 'ADMIN')

const availableActions = computed(() => {
  return [...new Set(logs.value.map((log) => String(log.action || '').trim()).filter(Boolean))].sort()
})

const availableResourceTypes = computed(() => {
  return [...new Set(logs.value.map((log) => String(log.resource_type || '').trim()).filter(Boolean))].sort()
})

const ACTION_LABELS = {
  CREATE: 'created',
  UPDATE: 'updated',
  DELETE: 'deleted',
  SOFT_DELETE: 'archived',
  RESTORE_PRODUCT: 'restored',
  LIST: 'viewed',
  UPDATE_NOTE: 'updated cashier note on',
  ADD_ITEM: 'added an item to',
  SEND_TO_CASHIER_QUEUE: 'sent to cashier queue',
  FINALIZE: 'stamped',
  DISPENSE: 'dispensed',
  CANCEL: 'cancelled',
  LOGIN: 'signed in',
  PIN_LOGIN: 'signed in with PIN',
  LOGOUT: 'signed out',
  REGISTER_REQUEST: 'requested account approval for',
  CREATE_MANAGED_USER: 'created account for',
  UPDATE_ROLE: 'changed role for',
  UPDATE_STATUS: 'changed account status for',
  RESET_PASSWORD: 'reset password for',
  RESET_PIN: 'reset PIN for',
  ASSIGN_TASK: 'assigned a task',
  TASK_STATUS: 'updated task progress',
  REQUEST_STOCK_ADJUSTMENT: 'requested stock adjustment for',
  ADJUST_STOCK: 'adjusted stock for',
  APPROVE_STOCK_ADJUSTMENT: 'approved stock adjustment for',
  REJECT_STOCK_ADJUSTMENT: 'rejected stock adjustment for',
}

// Plain-language resource type labels
const RESOURCE_LABELS = {
  INVOICE: 'invoice',
  INVOICE_ITEM: 'invoice item',
  PRODUCT: 'product',
  PRODUCT_UNIT: 'product unit',
  USER: 'user account',
  USER_TASK: 'team task',
  STOCK: 'stock record',
  STOCK_ADJUSTMENT: 'stock change request',
  SESSION: 'login session',
  SETTING: 'settings',
  SYSTEM: 'system',
}

// User-friendly filter labels
const ACTION_FILTER_LABELS = {
  CREATE: 'Created something',
  UPDATE: 'Updated something',
  DELETE: 'Deleted something',
  SOFT_DELETE: 'Archived something',
  LIST: 'Viewed records',
  UPDATE_NOTE: 'Updated cashier note',
  ADD_ITEM: 'Added invoice item',
  SEND_TO_CASHIER_QUEUE: 'Sent invoice to cashier queue',
  FINALIZE: 'Stamped invoice',
  DISPENSE: 'Dispensed invoice',
  CANCEL: 'Cancelled invoice',
  LOGIN: 'Signed in',
  PIN_LOGIN: 'Signed in with PIN',
  LOGOUT: 'Signed out',
  REGISTER_REQUEST: 'Requested account approval',
  CREATE_MANAGED_USER: 'Created staff account',
  UPDATE_ROLE: 'Changed user role',
  UPDATE_STATUS: 'Changed account status',
  RESET_PASSWORD: 'Reset password',
  RESET_PIN: 'Reset PIN',
  ASSIGN_TASK: 'Assigned task',
  TASK_STATUS: 'Updated task status',
  REQUEST_STOCK_ADJUSTMENT: 'Requested stock adjustment',
  ADJUST_STOCK: 'Adjusted stock',
  APPROVE_STOCK_ADJUSTMENT: 'Approved stock adjustment',
  REJECT_STOCK_ADJUSTMENT: 'Rejected stock adjustment',
}

const RESOURCE_FILTER_LABELS = {
  INVOICE: 'Sales & Invoices',
  PRODUCT: 'Products',
  PRODUCT_UNIT: 'Product Units',
  USER: 'User Accounts',
  USER_TASK: 'Team Tasks',
  STOCK: 'Stock Records',
  STOCK_ADJUSTMENT: 'Stock Changes',
  SESSION: 'Login Sessions',
  SETTING: 'Settings',
}

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  
  const isToday = date.toDateString() === today.toDateString()
  const isYesterday = date.toDateString() === yesterday.toDateString()
  
  const timeStr = date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
  
  if (isToday) return `Today at ${timeStr}`
  if (isYesterday) return `Yesterday at ${timeStr}`
  
  return date.toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined,
  }) + ` at ${timeStr}`
}

function humanizeCode(value) {
  const text = String(value || '')
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()

  if (!text) return ''
  return text.toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase())
}

function normalizeAction(action) {
  return String(action || '').trim().toUpperCase().replace(/\s+/g, '_')
}

function normalizeResource(resourceType) {
  return String(resourceType || '').trim().toUpperCase()
}

function actionPhrase(action) {
  const normalized = normalizeAction(action)
  return ACTION_LABELS[normalized] || humanizeCode(normalized).toLowerCase()
}

function friendlyActionLabel(action) {
  const phrase = actionPhrase(action)
  return phrase ? phrase.charAt(0).toUpperCase() + phrase.slice(1) : 'Did something'
}

function friendlyResourceLabel(resourceType) {
  const normalized = normalizeResource(resourceType)
  return RESOURCE_LABELS[normalized] || humanizeCode(normalized).toLowerCase() || 'item'
}

function actionFilterLabel(action) {
  const normalized = normalizeAction(action)
  return ACTION_FILTER_LABELS[normalized] || friendlyActionLabel(normalized)
}

function resourceFilterLabel(resourceType) {
  const normalized = normalizeResource(resourceType)
  return RESOURCE_FILTER_LABELS[normalized] || humanizeCode(normalized)
}

function formatPaymentMethod(value) {
  return humanizeCode(value || 'unknown')
}

function shortId(value) {
  const text = String(value || '')
  if (!text) return null
  return text.slice(0, 8)
}

function formatDetailValue(value) {
  if (value === null || value === undefined || value === '') return null
  if (typeof value === 'boolean') return value ? 'Yes' : 'No'
  if (typeof value === 'number') return Number(value).toLocaleString('en-NG')
  if (Array.isArray(value)) {
    return value
      .map((entry) => formatDetailValue(entry) || String(entry))
      .filter(Boolean)
      .join(', ')
  }
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

function detailHighlights(log) {
  const details = log?.details && typeof log.details === 'object' ? log.details : {}
  const highlights = []

  if (log?.resource_id) highlights.push({ label: 'Ref', value: shortId(log.resource_id) })
  if (details.invoice_id) highlights.push({ label: 'Invoice', value: shortId(details.invoice_id) })
  if (details.total_amount !== undefined) {
    highlights.push({ label: 'Amount', value: formatSimple(details.total_amount, 0) })
  }
  if (details.payment_method) highlights.push({ label: 'Payment', value: formatPaymentMethod(details.payment_method) })
  if (details.items_count !== undefined) highlights.push({ label: 'Items', value: String(details.items_count) })
  if (details.quantity !== undefined) highlights.push({ label: 'Quantity', value: String(details.quantity) })
  if (details.unit_price !== undefined) {
    highlights.push({ label: 'Unit Price', value: formatSimple(details.unit_price, 0) })
  }
  if (details.change_qty !== undefined) {
    const change = Number(details.change_qty || 0)
    highlights.push({ label: 'Stock Change', value: `${change > 0 ? '+' : ''}${change.toLocaleString('en-NG')}` })
  }
  if (details.old_quantity !== undefined && details.new_quantity !== undefined) {
    highlights.push({
      label: 'Stock Level',
      value: `${Number(details.old_quantity || 0).toLocaleString('en-NG')} → ${Number(details.new_quantity || 0).toLocaleString('en-NG')}`,
    })
  }
  if (details.name || details.product_name) highlights.push({ label: 'Product', value: details.name || details.product_name })
  if (details.sku) highlights.push({ label: 'SKU', value: details.sku })
  if (details.created_user || details.target_user || details.username || details.full_name) {
    highlights.push({ label: 'User', value: details.created_user || details.target_user || details.full_name || details.username })
  }
  if (details.from && details.to) highlights.push({ label: 'Role', value: `${details.from} → ${details.to}` })
  if (details.is_active !== undefined) highlights.push({ label: 'Active', value: details.is_active ? 'Yes' : 'No' })
  if (details.title) highlights.push({ label: 'Task', value: details.title })
  if (details.is_done !== undefined) highlights.push({ label: 'Task Status', value: details.is_done ? 'Done' : 'Pending' })
  if (details.reason) highlights.push({ label: 'Reason', value: details.reason })
  if (details.status) highlights.push({ label: 'Status', value: humanizeCode(details.status) })
  if (details.review_status) highlights.push({ label: 'Review', value: humanizeCode(details.review_status) })
  if (details.results_count !== undefined) highlights.push({ label: 'Results', value: String(details.results_count) })

  const seen = new Set()
  return highlights.filter((item) => {
    const key = `${item.label}:${item.value}`
    if (!item.value || seen.has(key)) return false
    seen.add(key)
    return true
  })
}

function technicalDetailsEntries(log) {
  const details = log?.details && typeof log.details === 'object' ? log.details : {}
  return Object.entries(details)
    .filter(([_, value]) => value !== null && value !== undefined && value !== '')
    .map(([key, value]) => ({
      key,
      label: humanizeCode(key),
      value: formatDetailValue(value) ?? '—',
    }))
}

function friendlyActivitySummary(log) {
  const actor = log?.actor_full_name || log?.actor_username || 'Someone'
  const action = actionPhrase(log?.action)
  const resource = friendlyResourceLabel(log?.resource_type)
  const details = log?.details || {}

  let summary = `${actor} ${action} ${resource}`

  if (details.name || details.product_name || details.title || details.created_user || details.target_user) {
    summary += `: ${details.name || details.product_name || details.title || details.created_user || details.target_user}`
  }
  if (details.total_amount !== undefined) {
    summary += ` worth ${formatSimple(details.total_amount, 0)}`
  }
  if (details.change_qty !== undefined) {
    const change = Number(details.change_qty || 0)
    summary += ` (${change > 0 ? '+' : ''}${change.toLocaleString('en-NG')} units)`
  }

  return summary
}

function friendlyDetailsSummary(log) {
  const highlights = detailHighlights(log).slice(0, 2)
  if (!highlights.length) return null
  return highlights.map((entry) => `${entry.label}: ${entry.value}`).join(' • ')
}

function actorLabel(log) {
  return log?.actor_full_name || log?.actor_username || 'System'
}

function toIsoOrNull(localValue) {
  if (!localValue) return null
  const date = new Date(localValue)
  return Number.isFinite(date.getTime()) ? date.toISOString() : null
}

function resolveTimeWindow() {
  const now = new Date()
  const preset = filters.value.timePreset

  if (preset === 'custom') {
    return {
      fromAt: toIsoOrNull(filters.value.fromLocal),
      toAt: toIsoOrNull(filters.value.toLocal),
    }
  }

  if (preset === '24h') {
    const from = new Date(now.getTime() - 24 * 60 * 60 * 1000)
    return { fromAt: from.toISOString(), toAt: now.toISOString() }
  }

  if (preset === '7d') {
    const from = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    return { fromAt: from.toISOString(), toAt: now.toISOString() }
  }

  if (preset === '30d') {
    const from = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
    return { fromAt: from.toISOString(), toAt: now.toISOString() }
  }

  const dayStart = new Date(now)
  dayStart.setHours(0, 0, 0, 0)
  return { fromAt: dayStart.toISOString(), toAt: now.toISOString() }
}

function resetSelectedIfMissing(nextLogs) {
  if (!selectedLog.value) return
  const exists = nextLogs.some((log) => log.id === selectedLog.value.id)
  if (!exists) selectedLog.value = null
}

async function loadUsersForFilter() {
  if (!canSeeAllActors.value) return
  try {
    users.value = await usersService.list({ limit: 300 })
  } catch {
    users.value = []
  }
}

async function loadActivityLogs() {
  loading.value = true
  error.value = ''
  try {
    const { fromAt, toAt } = resolveTimeWindow()
    const result = await usersService.listSystemActivity({
      limit: filters.value.limit,
      action: filters.value.action || null,
      resourceType: filters.value.resourceType || null,
      actorUserId: canSeeAllActors.value ? (filters.value.actorUserId || null) : null,
      search: filters.value.search.trim() || null,
      fromAt,
      toAt,
      period: filters.value.period,
      sort: filters.value.sort,
    })

    logs.value = Array.isArray(result) ? result : []
    resetSelectedIfMissing(logs.value)
  } catch (err) {
    logs.value = []
    error.value = err?.message || 'Could not load recent activity. Please try again.'
  } finally {
    loading.value = false
  }
}

function inspectLog(log) {
  selectedLog.value = log
  showRawJson.value = false
}

function closeInspector() {
  selectedLog.value = null
  showRawJson.value = false
}

async function copySelectedJson() {
  if (!selectedLog.value) return
  try {
    await navigator.clipboard.writeText(JSON.stringify(selectedLog.value, null, 2))
    toast.success('Raw JSON copied.')
  } catch {
    toast.error('Could not copy. Please try again.')
  }
}

watch(showTechnicalDetails, (enabled) => {
  if (!enabled) showRawJson.value = false
})

watch(
  () => [
    filters.value.action,
    filters.value.resourceType,
    filters.value.actorUserId,
    filters.value.period,
    filters.value.sort,
    filters.value.timePreset,
    filters.value.limit,
    filters.value.fromLocal,
    filters.value.toLocal,
  ],
  () => {
    loadActivityLogs()
  },
)

let searchDebounce = null
watch(
  () => filters.value.search,
  () => {
    if (searchDebounce) window.clearTimeout(searchDebounce)
    searchDebounce = window.setTimeout(() => {
      loadActivityLogs()
    }, 240)
  },
)

onMounted(async () => {
  await loadUsersForFilter()
  await loadActivityLogs()
})
</script>

<template>
  <section class="activity-page">
    <header class="page-head">
      <div>
        <h2>Recent Activity</h2>
        <p>See what's been happening in the pharmacy — sales, stock changes, and more.</p>
      </div>
      <button class="refresh-btn" :disabled="loading" @click="loadActivityLogs">
        {{ loading ? 'Loading…' : 'Refresh' }}
      </button>
    </header>

    <article class="panel filters">
      <div class="filters-head">
        <h3>Filter activity</h3>
        <p>Use simple labels to narrow results, then open an item for full details.</p>
      </div>

      <div class="filters-grid">
        <label class="filter-search">
          <span>Search</span>
          <input v-model="filters.search" type="text" placeholder="Type to find activity…" />
        </label>

        <label>
          <span>Show</span>
          <select v-model="filters.sort">
            <option value="desc">Latest first</option>
            <option value="asc">Oldest first</option>
          </select>
        </label>

        <label>
          <span>Time of Day</span>
          <select v-model="filters.period">
            <option value="all">Any time</option>
            <option value="morning">Morning (5am – 12pm)</option>
            <option value="afternoon">Afternoon (12pm – 5pm)</option>
            <option value="evening">Evening (5pm – 9pm)</option>
            <option value="night">Night (9pm – 5am)</option>
          </select>
        </label>

        <label>
          <span>Date Range</span>
          <select v-model="filters.timePreset">
            <option value="today">Today only</option>
            <option value="24h">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="custom">Custom dates</option>
          </select>
        </label>

        <label>
          <span>Activity Type</span>
          <select v-model="filters.action">
            <option value="">All activities</option>
            <option v-for="action in availableActions" :key="action" :value="action">
              {{ actionFilterLabel(action) }}
            </option>
          </select>
        </label>

        <label>
          <span>Category</span>
          <select v-model="filters.resourceType">
            <option value="">All categories</option>
            <option v-for="resource in availableResourceTypes" :key="resource" :value="resource">
              {{ resourceFilterLabel(resource) }}
            </option>
          </select>
        </label>

        <label v-if="canSeeAllActors">
          <span>Team Member</span>
          <select v-model="filters.actorUserId">
            <option value="">Anyone</option>
            <option v-for="u in users" :key="u.id" :value="u.id">{{ u.full_name || u.username }}</option>
          </select>
        </label>

        <label>
          <span>Show up to</span>
          <select v-model.number="filters.limit">
            <option :value="60">60 activities</option>
            <option :value="120">120 activities</option>
            <option :value="180">180 activities</option>
            <option :value="300">300 activities</option>
          </select>
        </label>

        <template v-if="filters.timePreset === 'custom'">
          <label>
            <span>From</span>
            <input v-model="filters.fromLocal" type="datetime-local" />
          </label>
          <label>
            <span>To</span>
            <input v-model="filters.toLocal" type="datetime-local" />
          </label>
        </template>
      </div>
    </article>

    <p v-if="error" class="error">{{ error }}</p>

    <div class="content-grid">
      <article class="panel activity-list-wrap">
        <header class="list-head">
          <div>
            <h3>Activity Timeline</h3>
            <p>
              {{ logs.length }} {{ logs.length === 1 ? 'entry' : 'entries' }}
              {{ filters.sort === 'desc' ? 'shown newest first' : 'shown oldest first' }}
            </p>
          </div>
        </header>

        <p v-if="loading" class="state">Looking up recent activity…</p>
        <p v-else-if="logs.length === 0" class="state">No activity matches your search. Try changing the filters above.</p>

        <div v-else class="activity-list">
          <button
            v-for="log in logs"
            :key="log.id"
            type="button"
            class="activity-item"
            :class="{ active: selectedLog?.id === log.id }"
            @click="inspectLog(log)"
          >
            <div class="activity-item-top">
              <span class="activity-action">{{ friendlyActionLabel(log.action) }}</span>
              <span class="activity-time">{{ formatDate(log.created_at) }}</span>
            </div>

            <strong class="activity-headline">{{ friendlyActivitySummary(log) }}</strong>
            <p v-if="friendlyDetailsSummary(log)" class="activity-extra">{{ friendlyDetailsSummary(log) }}</p>

            <div class="activity-context">
              <span class="context-pill">{{ friendlyResourceLabel(log.resource_type) }}</span>
              <span class="context-pill">{{ actorLabel(log) }}</span>
            </div>

            <div v-if="detailHighlights(log).length" class="activity-highlights">
              <span
                v-for="item in detailHighlights(log).slice(0, 2)"
                :key="`${log.id}-${item.label}`"
                class="activity-chip"
              >
                <span class="chip-label">{{ item.label }}</span>
                <span class="chip-value">{{ item.value }}</span>
              </span>
            </div>
          </button>
        </div>
      </article>

      <article class="panel inspector" v-if="selectedLog">
        <header class="inspector-head">
          <div>
            <h3>Activity Details</h3>
            <p>Quick summary first, with deeper context underneath.</p>
          </div>
          <div class="inspector-actions">
            <button type="button" @click="closeInspector">Close</button>
          </div>
        </header>

        <div class="detail-summary">
          <p class="detail-kicker">What happened</p>
          <p class="detail-headline">{{ friendlyActivitySummary(selectedLog) }}</p>
          <p class="detail-time">{{ formatDate(selectedLog.created_at) }}</p>
        </div>

        <dl class="meta-grid">
          <div>
            <dt>Who</dt>
            <dd>{{ actorLabel(selectedLog) }}</dd>
          </div>
          <div>
            <dt>What</dt>
            <dd>{{ friendlyActionLabel(selectedLog.action) }} {{ friendlyResourceLabel(selectedLog.resource_type) }}</dd>
          </div>
          <div>
            <dt>When</dt>
            <dd>{{ formatDate(selectedLog.created_at) }}</dd>
          </div>
          <div v-if="selectedLog.resource_id">
            <dt>Reference</dt>
            <dd>{{ shortId(selectedLog.resource_id) }}</dd>
          </div>
        </dl>

        <div v-if="selectedLog.details?.reason" class="detail-reason">
          <strong>Reason given:</strong>
          <p>{{ selectedLog.details.reason }}</p>
        </div>

        <div v-if="detailHighlights(selectedLog).length" class="detail-highlights">
          <h4>Key details</h4>
          <div class="detail-chips">
            <span
              v-for="item in detailHighlights(selectedLog)"
              :key="`${selectedLog.id}-${item.label}`"
              class="detail-chip"
            >
              <span class="chip-label">{{ item.label }}</span>
              <span class="chip-value">{{ item.value }}</span>
            </span>
          </div>
        </div>

        <div v-if="isAdmin" class="technical-toggle">
          <div>
            <p>Need technical audit fields?</p>
            <span>Use this for admin troubleshooting, exact keys, and JSON drill-down.</span>
          </div>
          <button type="button" @click="showTechnicalDetails = !showTechnicalDetails">
            {{ showTechnicalDetails ? 'Hide Technical Details' : 'Show Technical Details' }}
          </button>
        </div>

        <div v-if="showTechnicalDetails && isAdmin" class="payload">
          <div class="payload-header">
            <div>
              <p>Technical details (admin review)</p>
              <span>Original saved payload fields.</span>
            </div>
            <button type="button" class="copy-btn" @click="showRawJson = !showRawJson">
              {{ showRawJson ? 'Hide Raw JSON' : 'Show Raw JSON' }}
            </button>
          </div>

          <dl v-if="technicalDetailsEntries(selectedLog).length" class="tech-grid">
            <div v-for="entry in technicalDetailsEntries(selectedLog)" :key="entry.key">
              <dt>{{ entry.label }}</dt>
              <dd>{{ entry.value }}</dd>
            </div>
          </dl>
          <p v-else class="tech-empty">No extra technical details were saved for this activity.</p>

          <div v-if="showRawJson" class="raw-json-block">
            <div class="payload-header raw-json-head">
              <div>
                <p>Raw JSON</p>
                <span>Copy this block for deeper debugging.</span>
              </div>
              <button type="button" class="copy-btn" @click="copySelectedJson">Copy JSON</button>
            </div>
            <pre>{{ JSON.stringify(selectedLog, null, 2) }}</pre>
          </div>
        </div>
      </article>

      <article class="panel inspector empty" v-else>
        <span class="material-icons empty-icon">touch_app</span>
        <h3>Tap an activity to see more</h3>
        <p>Select any item from the list to view its details.</p>
      </article>
    </div>
  </section>
</template>

<style scoped>
.activity-page { display: grid; gap: 14px; }
.page-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.page-head h2 { margin: 0; }
.page-head p { margin: 4px 0 0; color: var(--text-muted); font-size: 14px; }

.panel {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  padding: var(--space-3);
}

.filters {
  display: grid;
  gap: 12px;
}

.filters-head h3 {
  margin: 0;
  font-size: 15px;
}

.filters-head p {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--text-muted);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
}

.filter-search {
  grid-column: 1 / -1;
}

label { display: grid; gap: 6px; }
label span { font-size: 12px; color: var(--text-muted); font-weight: 500; }

input, select {
  min-height: 40px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  color: var(--text-primary);
  padding: 0 12px;
  font-size: 14px;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
  gap: 12px;
}

.activity-list-wrap {
  display: grid;
  gap: 12px;
  max-height: 72vh;
  overflow: auto;
  align-content: start;
}

.list-head h3 {
  margin: 0;
  font-size: 15px;
}

.list-head p {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--text-muted);
}

.activity-list {
  display: grid;
  gap: 10px;
}

.activity-item {
  position: relative;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  padding: 12px 14px 12px 18px;
  text-align: left;
  cursor: pointer;
  display: grid;
  gap: 8px;
  transition: border-color 0.15s, background 0.15s;
}

.activity-item::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 12px;
  bottom: 12px;
  width: 3px;
  border-radius: 999px;
  background: var(--border-subtle);
}

.activity-item:hover { 
  border-color: var(--border-default);
  background: var(--bg-hover);
}

.activity-item.active { 
  border-color: var(--primary); 
  background: var(--primary-bg);
}

.activity-item.active::before {
  background: var(--primary);
}

.activity-item-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.activity-action {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}

.activity-headline {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  line-height: 1.4;
}

.activity-time {
  font-size: 12px;
  color: var(--text-muted);
}

.activity-extra {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
}

.activity-context {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.context-pill {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  border: 1px solid var(--border-default);
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 11px;
  padding: 2px 8px;
}

.activity-highlights {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.activity-chip {
  display: grid;
  gap: 2px;
  min-width: 120px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  background: var(--bg-card);
  padding: 6px 8px;
}

.inspector { display: grid; gap: 14px; align-content: start; }
.inspector-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; flex-wrap: wrap; }
.inspector-head h3 { margin: 0; font-size: 16px; }

.inspector-head p {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--text-muted);
}

.inspector-actions { display: flex; gap: 8px; }
.inspector-actions button,
.refresh-btn,
.technical-toggle button {
  min-height: 40px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  color: var(--text-primary);
  padding: 0 12px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
}

.inspector-actions button:hover,
.refresh-btn:hover,
.technical-toggle button:hover {
  background: var(--bg-hover);
}

.detail-summary {
  padding: 14px;
  border-radius: var(--radius-md);
  background: var(--primary-bg);
  border: 1px solid var(--primary-tint);
}

.detail-kicker {
  margin: 0 0 6px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  font-weight: 600;
}

.detail-headline {
  margin: 0;
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
  line-height: 1.4;
}

.detail-time {
  margin: 6px 0 0;
  font-size: 13px;
  color: var(--text-muted);
}

.meta-grid {
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 10px;
}

.meta-grid > div {
  padding: 10px 12px;
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
}

.meta-grid dt { 
  font-size: 11px; 
  color: var(--text-muted); 
  text-transform: uppercase; 
  letter-spacing: 0.04em;
  font-weight: 600;
  margin-bottom: 4px;
}

.meta-grid dd { 
  margin: 0; 
  font-size: 14px; 
  color: var(--text-primary);
}

.detail-reason {
  padding: 12px;
  border-radius: var(--radius-md);
  background: var(--warning-bg);
  border: 1px solid var(--warning-tint);
}

.detail-reason strong {
  font-size: 12px;
  color: var(--warning);
  display: block;
  margin-bottom: 4px;
}

.detail-reason p {
  margin: 0;
  font-size: 14px;
  color: var(--text-primary);
}

.detail-highlights {
  display: grid;
  gap: 8px;
}

.detail-highlights h4 {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.detail-chips {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px;
}

.detail-chip {
  display: grid;
  gap: 2px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  color: var(--text-primary);
  padding: 6px 10px;
}

.chip-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  font-weight: 600;
}

.chip-value {
  font-size: 12px;
  color: var(--text-primary);
  font-weight: 500;
  word-break: break-word;
}

.technical-toggle {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 12px;
  border: 1px dashed var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
}

.technical-toggle p {
  margin: 0;
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 600;
}

.technical-toggle span {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-muted);
}

.payload {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.payload-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--bg-elevated);
  border-bottom: 1px solid var(--border-subtle);
}

.payload-header p { 
  margin: 0; 
  font-size: 12px; 
  color: var(--text-muted);
  font-weight: 500;
}

.payload-header span {
  display: block;
  margin-top: 2px;
  font-size: 11px;
  color: var(--text-muted);
}

.copy-btn {
  min-height: 36px;
  padding: 0 10px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}

.copy-btn:hover {
  background: var(--bg-hover);
}

.tech-grid {
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 8px;
  padding: 10px 12px;
}

.tech-grid > div {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 8px 10px;
  background: var(--bg-card);
}

.tech-grid dt {
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.tech-grid dd {
  margin: 0;
  font-size: 12px;
  color: var(--text-primary);
  word-break: break-word;
}

.tech-empty {
  margin: 0;
  padding: 12px;
  color: var(--text-muted);
  font-size: 12px;
}

.raw-json-block {
  border-top: 1px solid var(--border-subtle);
}

.raw-json-head {
  border-top: 1px solid var(--border-subtle);
}

.payload pre {
  margin: 0;
  background: var(--bg-recessed);
  padding: 12px;
  max-height: 36vh;
  overflow: auto;
  font-size: 12px;
  color: var(--text-secondary);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}

.state { margin: 0; color: var(--text-muted); font-size: 14px; padding: 20px 0; text-align: center; }
.error { margin: 0; color: var(--error); font-size: 14px; }

.inspector.empty { 
  place-items: center; 
  text-align: center; 
  align-content: center; 
  min-height: 240px;
  padding: 32px;
}

.empty-icon {
  font-size: 48px;
  color: var(--text-muted);
  opacity: 0.5;
  margin-bottom: 12px;
}

.inspector.empty h3 {
  font-size: 15px;
  font-weight: 500;
}

.inspector.empty p { 
  margin: 6px 0 0; 
  color: var(--text-muted);
  font-size: 13px;
}

@media (max-width: 980px) {
  .content-grid { grid-template-columns: 1fr; }
  .filters-grid { grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }
}

@media (max-width: 720px) {
  .activity-item-top {
    align-items: flex-start;
    flex-direction: column;
    gap: 4px;
  }

  .technical-toggle {
    flex-direction: column;
  }

  .meta-grid {
    grid-template-columns: 1fr;
  }
}
</style>
