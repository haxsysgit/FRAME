import { computed, ref } from 'vue'

const activeRequests = ref(0)
const activeRouteChanges = ref(0)
const progress = ref(0)
const visible = ref(false)
const activityByLabel = ref({})

let progressTimer = null
let revealTimer = null
let hideTimer = null

const totalActive = computed(() => activeRequests.value + activeRouteChanges.value)

function clearTimers() {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
  if (revealTimer) {
    clearTimeout(revealTimer)
    revealTimer = null
  }
  if (hideTimer) {
    clearTimeout(hideTimer)
    hideTimer = null
  }
}

function updateActivityLabel(label, delta) {
  const key = String(label || 'Background activity')
  const next = (activityByLabel.value[key] || 0) + delta
  if (next > 0) {
    activityByLabel.value[key] = next
    return
  }
  delete activityByLabel.value[key]
}

function titleCase(text) {
  return String(text || '')
    .split(' ')
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

function toFriendlyLabel(label) {
  const raw = String(label || '').trim()
  if (!raw) return 'Updating data'

  if (raw.toLowerCase().startsWith('route ')) {
    return 'Opening page'
  }

  const requestMatch = raw.match(/^(GET|POST|PATCH|PUT|DELETE)\s+(.+)$/i)
  if (!requestMatch) {
    return titleCase(raw.replace(/[_-]+/g, ' '))
  }

  const [, , pathWithQuery] = requestMatch
  const cleanPath = String(pathWithQuery || '').split('?')[0]
  const parts = cleanPath
    .split('/')
    .filter(Boolean)
    .map((part) => (part.length > 36 ? 'record' : part.replace(/[-_]+/g, ' ')))

  if (!parts.length) return 'Loading data'

  const lastPart = parts[parts.length - 1]
  return `Loading ${titleCase(lastPart)}`
}

function startProgress() {
  clearTimers()

  progress.value = 14

  revealTimer = window.setTimeout(() => {
    visible.value = true
  }, 110)

  progressTimer = window.setInterval(() => {
    if (progress.value >= 92) return
    const gap = 92 - progress.value
    progress.value = Math.min(92, progress.value + Math.max(1.2, gap * 0.15))
  }, 160)
}

function finishProgress() {
  clearTimers()

  progress.value = 100
  visible.value = true

  hideTimer = window.setTimeout(() => {
    visible.value = false
    progress.value = 0
    activityByLabel.value = {}
  }, 260)
}

function resetLoadingState() {
  clearTimers()
  activeRequests.value = 0
  activeRouteChanges.value = 0
  progress.value = 0
  visible.value = false
  activityByLabel.value = {}
}

function beginActivity(counterRef, label) {
  const wasIdle = totalActive.value === 0
  counterRef.value += 1
  updateActivityLabel(label, 1)
  if (wasIdle) {
    startProgress()
  }
}

function endActivity(counterRef, label) {
  counterRef.value = Math.max(0, counterRef.value - 1)
  updateActivityLabel(label, -1)
  if (totalActive.value === 0) {
    finishProgress()
  }
}

export function beginRequestLoading(label) {
  beginActivity(activeRequests, label)
}

export function endRequestLoading(label) {
  endActivity(activeRequests, label)
}

export function beginRouteLoading(label = 'Route navigation') {
  beginActivity(activeRouteChanges, label)
}

export function endRouteLoading(label = 'Route navigation') {
  endActivity(activeRouteChanges, label)
}

const resourcesInFlight = computed(() => Object.entries(activityByLabel.value)
  .filter(([, count]) => count > 0)
  .sort((a, b) => b[1] - a[1])
  .map(([label, count]) => ({ label: toFriendlyLabel(label), count })))

export const globalLoading = {
  activeRequests,
  activeRouteChanges,
  progress,
  visible,
  resourcesInFlight,
  totalActive,
  resetLoadingState,
}
