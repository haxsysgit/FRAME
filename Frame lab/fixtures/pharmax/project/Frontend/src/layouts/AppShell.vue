<script setup>
import { computed, ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SideNav from '../components/SideNav.vue'
import { useThemeStore } from '../stores/theme'
import { useAuthStore } from '../stores/auth'
import { useDashboardStore } from '../stores/dashboard'
import { useSettingsStore } from '../stores/settings'

const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()
const auth = useAuthStore()
const dash = useDashboardStore()
const settingsStore = useSettingsStore()
const mobileNavOpen = ref(false)
const profileOpen = ref(false)
const notificationsOpen = ref(false)
const priorityPopupVisible = ref(false)
const priorityPopupShown = ref(false)
const profileDropdownRef = ref(null)
const notificationsDropdownRef = ref(null)
const SIDEBAR_PREF_KEY = 'pharmax.sidebar.collapsed'
const sidebarCollapsed = ref(readSidebarCollapsedPreference())
const dismissedNotificationIds = ref(new Set())
const lockCountdownVisible = ref(false)
const lockCountdownSeconds = ref(0)
const loginPopupCheckedThisSession = ref(false)
const DAILY_LOCK_HOUR = 22
const DISMISSED_NOTIFICATION_KEY_PREFIX = 'pharmax.notifications.dismissed.v1'
const PRIORITY_POPUP_KEY_PREFIX = 'pharmax.notifications.priority-popup.v1'
let metricsRefreshTimer = null
let inactivityTimer = null
let lockCountdownTimer = null

function readSidebarCollapsedPreference() {
  if (typeof window === 'undefined') {
    return true
  }
  const saved = window.localStorage.getItem(SIDEBAR_PREF_KEY)
  if (saved === null) {
    return true
  }
  return saved === '1'
}

function notificationScopeKey() {
  return String(auth.user?.id || auth.user?.username || 'guest')
}

function localDateKey(value = new Date()) {
  const year = value.getFullYear()
  const month = String(value.getMonth() + 1).padStart(2, '0')
  const day = String(value.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function dismissedNotificationStorageKey() {
  return `${DISMISSED_NOTIFICATION_KEY_PREFIX}.${notificationScopeKey()}`
}

function readDismissedNotificationIds() {
  if (typeof window === 'undefined') return new Set()
  try {
    const raw = window.localStorage.getItem(dismissedNotificationStorageKey())
    if (!raw) return new Set()
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return new Set()
    return new Set(parsed.map((id) => String(id)))
  } catch {
    return new Set()
  }
}

function persistDismissedNotificationIds(next) {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(dismissedNotificationStorageKey(), JSON.stringify(Array.from(next)))
}

function priorityPopupStorageKey(scope, now = new Date()) {
  return `${PRIORITY_POPUP_KEY_PREFIX}.${scope}.${notificationScopeKey()}.${localDateKey(now)}`
}

function hasShownPriorityPopup(scope, now = new Date()) {
  if (typeof window === 'undefined') return false
  return window.localStorage.getItem(priorityPopupStorageKey(scope, now)) === '1'
}

function markPriorityPopupShown(scope, now = new Date()) {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(priorityPopupStorageKey(scope, now), '1')
}

function clearInactivityTimer() {
  if (inactivityTimer) {
    clearTimeout(inactivityTimer)
    inactivityTimer = null
  }
}

function clearLockCountdownTimer() {
  if (lockCountdownTimer) {
    clearInterval(lockCountdownTimer)
    lockCountdownTimer = null
  }
}

function tryShowDailyLockPriorityPopup(now = new Date()) {
  if (now.getHours() < DAILY_LOCK_HOUR) return
  if (!Boolean(settingsStore.settings.notifications?.priority_popup_on_login)) return
  if (priorityNotifications.value.length === 0) return
  if (hasShownPriorityPopup('lock', now)) return
  markPriorityPopupShown('lock', now)
  priorityPopupVisible.value = true
  priorityPopupShown.value = true
}

function updateLockCountdownState() {
  const role = String(auth.userRole || '').toUpperCase()
  const isOperationalUser = role === 'CASHIER' || role === 'STAFF'
  if (!isOperationalUser) {
    lockCountdownVisible.value = false
    lockCountdownSeconds.value = 0
    return
  }

  const now = new Date()
  const lockAt = new Date(now)
  lockAt.setHours(DAILY_LOCK_HOUR, 0, 0, 0)
  const diffSeconds = Math.floor((lockAt.getTime() - now.getTime()) / 1000)

  tryShowDailyLockPriorityPopup(now)

  if (diffSeconds > 0 && diffSeconds <= 300) {
    lockCountdownVisible.value = true
    lockCountdownSeconds.value = diffSeconds
    return
  }

  if (diffSeconds <= 0 && diffSeconds > -300) {
    lockCountdownVisible.value = true
    lockCountdownSeconds.value = 0
    return
  }

  lockCountdownVisible.value = false
  lockCountdownSeconds.value = 0
}

function scheduleAutoLock() {
  clearInactivityTimer()

  const safety = settingsStore.settings.safety
  if (!safety.auto_lock) return

  const timeoutMs = Number(safety.session_timeout_minutes || 0) * 60 * 1000
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) return

  inactivityTimer = window.setTimeout(async () => {
    await auth.logout()
    router.replace('/login')
  }, timeoutMs)
}

onMounted(() => {
  dismissedNotificationIds.value = readDismissedNotificationIds()
  sidebarCollapsed.value = readSidebarCollapsedPreference()
  dash.load(true)
  metricsRefreshTimer = window.setInterval(() => {
    dash.load(true)
  }, 45_000)

  document.addEventListener('click', handleClickOutside)
  ;['mousemove', 'keydown', 'click', 'touchstart', 'scroll'].forEach((eventName) => {
    window.addEventListener(eventName, scheduleAutoLock, { passive: true })
  })

  scheduleAutoLock()
  updateLockCountdownState()
  lockCountdownTimer = window.setInterval(() => {
    updateLockCountdownState()
  }, 1_000)
})

onBeforeUnmount(() => {
  if (metricsRefreshTimer) {
    clearInterval(metricsRefreshTimer)
    metricsRefreshTimer = null
  }
  document.removeEventListener('click', handleClickOutside)
  ;['mousemove', 'keydown', 'click', 'touchstart', 'scroll'].forEach((eventName) => {
    window.removeEventListener(eventName, scheduleAutoLock)
  })
  clearInactivityTimer()
  clearLockCountdownTimer()
})

watch(
  () => [
    settingsStore.settings.safety.auto_lock,
    settingsStore.settings.safety.session_timeout_minutes,
  ],
  () => {
    scheduleAutoLock()
  },
)

watch(
  () => auth.user?.id,
  () => {
    dismissedNotificationIds.value = readDismissedNotificationIds()
    loginPopupCheckedThisSession.value = false
  },
)

function handleClickOutside(event) {
  if (profileDropdownRef.value && !profileDropdownRef.value.contains(event.target)) {
    profileOpen.value = false
  }
  if (notificationsDropdownRef.value && !notificationsDropdownRef.value.contains(event.target)) {
    notificationsOpen.value = false
  }
}

const notifications = computed(() => {
  const cfg = settingsStore.settings.notifications || {}
  const items = []

  if (auth.userRole === 'ADMIN' && cfg.include_new_user_approvals && Number(dash.pendingUserApprovals || 0) > 0) {
    items.push({
      id: 'pending-user-approvals',
      title: `${dash.pendingUserApprovals} user approval request${dash.pendingUserApprovals > 1 ? 's' : ''}`,
      subtitle: 'Review pending account approvals in Team & Access.',
      route: '/users',
      type: 'warning',
      priority: true,
    })
  }

  if (auth.userRole === 'ADMIN' && Number(dash.pendingStockAdjustments || 0) > 0) {
    items.push({
      id: 'pending-stock-adjustments',
      title: `${dash.pendingStockAdjustments} stock adjustment request${dash.pendingStockAdjustments > 1 ? 's' : ''}`,
      subtitle: 'Review pending stock changes awaiting approval.',
      route: '/stock',
      type: 'warning',
      priority: true,
    })
  }

  if (cfg.include_out_of_stock && Number(dash.outOfStockCount || 0) > 0) {
    items.push({
      id: 'out-of-stock',
      title: `${dash.outOfStockCount} product${dash.outOfStockCount > 1 ? 's are' : ' is'} out of stock`,
      subtitle: 'Open Stock Management → Out-of-Stock Items to prioritize restock.',
      route: '/stock/out-of-stock',
      type: 'error',
      priority: true,
    })
  }

  if (cfg.include_low_stock) {
    const lowStock = Array.isArray(dash.lowStockItems) ? dash.lowStockItems.slice(0, 3) : []
    lowStock.forEach((item) => {
      items.push({
        id: `low-stock-${item.id}`,
        title: `${item.name || 'Product'} is low on stock`,
        subtitle: `Only ${item.quantity_on_hand ?? 0} left`,
        route: '/stock/low-stock',
        type: 'warning',
        priority: true,
      })
    })
  }

  if (cfg.include_invoice_cancellations && Number(dash.cancelledInvoiceCountToday || 0) > 0) {
    items.push({
      id: 'cancelled-invoices-today',
      title: `${dash.cancelledInvoiceCountToday} invoice cancellation${dash.cancelledInvoiceCountToday > 1 ? 's' : ''} today`,
      subtitle: 'Review cancellation reasons and trends.',
      route: '/invoices',
      type: 'warning',
      priority: true,
    })
  }

  const recentInvoices = Array.isArray(dash.recentInvoices) ? dash.recentInvoices.slice(0, 4) : []
  recentInvoices.forEach((invoice) => {
    items.push({
      id: `invoice-${invoice.id}`,
      title: `Invoice #${String(invoice.id || '').slice(0, 8)} created`,
      subtitle: `${invoice.status || 'DRAFT'} • ₦${Number(invoice.total_amount || 0).toLocaleString('en-NG')}`,
      route: '/invoices',
      type: 'info',
      priority: false,
    })
  })

  return items
    .filter((item) => !dismissedNotificationIds.value.has(item.id))
    .slice(0, 12)
})

const priorityNotifications = computed(() => notifications.value.filter((item) => item.priority))

const notificationCount = computed(() => notifications.value.length)

const lockCountdownLabel = computed(() => {
  if (lockCountdownSeconds.value <= 0) {
    return 'Sales are now locked for cashier and staff. Ask an admin for temporary after-hours access if you must continue.'
  }

  const minutes = Math.floor(lockCountdownSeconds.value / 60)
  const seconds = lockCountdownSeconds.value % 60
  return `Sales will lock in ${minutes}m ${String(seconds).padStart(2, '0')}s. Please finish and stamp active invoices now.`
})

function dismissNotification(notificationId) {
  const next = new Set(dismissedNotificationIds.value)
  next.add(notificationId)
  dismissedNotificationIds.value = next
  persistDismissedNotificationIds(next)

  if (priorityPopupVisible.value && priorityNotifications.value.length === 0) {
    priorityPopupVisible.value = false
  }
  if (notificationsOpen.value && notifications.value.length === 0) {
    notificationsOpen.value = false
  }
}

function openPriorityCenter() {
  priorityPopupVisible.value = false
  notificationsOpen.value = true
  profileOpen.value = false
}

function closePriorityPopup() {
  priorityPopupVisible.value = false
}

function toggleNotifications() {
  notificationsOpen.value = !notificationsOpen.value
  if (notificationsOpen.value) {
    profileOpen.value = false
  }
}

function openNotification(item) {
  dismissNotification(item.id)
  priorityPopupVisible.value = false
  notificationsOpen.value = false
  const route = item?.route || '/dashboard'
  router.push(route)
}

function fmtRevenue(n) {
  const value = Number(n)
  const safe = Number.isFinite(value) ? value : 0
  if (safe >= 1_000_000) return `₦${(safe / 1_000_000).toFixed(2)}M`
  if (safe >= 1_000) return `₦${(safe / 1_000).toFixed(1)}K`
  return `₦${safe.toLocaleString('en-NG', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
}

function toggleProfile() {
  notificationsOpen.value = false
  profileOpen.value = !profileOpen.value
}

async function handleLogout() {
  await auth.logout()
  router.replace('/login')
}

const pageTitle = computed(() => route.meta?.label ?? 'Pharmax')
const showShellHeader = computed(() => route.meta?.showShellHeader !== false)

// Breadcrumb generation
const breadcrumbs = computed(() => {
  const crumbs = [{ label: 'Home', to: '/dashboard' }]
  const path = route.path

  if (path.startsWith('/products/units')) {
    crumbs.push({ label: 'Products', to: '/products' })
    crumbs.push({ label: 'Units & Pricing', to: null })
  } else if (path.startsWith('/products')) {
    crumbs.push({ label: 'Products', to: null })
  } else if (path === '/stock') {
    crumbs.push({ label: 'Stock Management', to: null })
  } else if (path.startsWith('/stock/out-of-stock')) {
    crumbs.push({ label: 'Stock Management', to: '/stock' })
    crumbs.push({ label: 'Out-of-Stock Items', to: null })
  } else if (path.startsWith('/stock/low-stock')) {
    crumbs.push({ label: 'Stock Management', to: '/stock' })
    crumbs.push({ label: 'Low Stock Watchlist', to: null })
  } else if (path !== '/dashboard' && route.meta?.label) {
    crumbs.push({ label: route.meta.label, to: null })
  }

  return crumbs
})

function openMobileNav() {
  mobileNavOpen.value = true
}

function closeMobileNav() {
  mobileNavOpen.value = false
}

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
  localStorage.setItem(SIDEBAR_PREF_KEY, sidebarCollapsed.value ? '1' : '0')
}

function openSettings() {
  profileOpen.value = false
  router.push('/settings')
}

watch(
  () => route.fullPath,
  () => {
    notificationsOpen.value = false
    profileOpen.value = false
    priorityPopupVisible.value = false
  },
)

watch(
  () => [
    Boolean(settingsStore.settings.notifications?.priority_popup_on_login),
    Boolean(dash.loaded),
    priorityNotifications.value.map((item) => item.id).join('|'),
  ],
  ([enabled, loaded]) => {
    if (!enabled || !loaded || loginPopupCheckedThisSession.value) return
    loginPopupCheckedThisSession.value = true
    if (hasShownPriorityPopup('login')) return
    markPriorityPopupShown('login')
    if (priorityNotifications.value.length === 0) return
    priorityPopupVisible.value = true
    priorityPopupShown.value = true
  },
  { immediate: true },
)
</script>

<template>
  <div class="shell" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <aside class="sidebar-container" :class="{ 'is-open': mobileNavOpen, 'collapsed': sidebarCollapsed }">
      <SideNav :collapsed="sidebarCollapsed" @navigate="closeMobileNav" @toggle-sidebar="toggleSidebar" />
    </aside>

    <button
      v-if="mobileNavOpen"
      type="button"
      class="backdrop"
      aria-label="Close sidebar"
      @click="closeMobileNav"
    />

    <section class="main-area">
      <header class="topbar">
        <div class="topbar-left">
          <button type="button" class="menu-toggle mobile-only" aria-label="Open sidebar" @click="openMobileNav">
            <span class="material-icons">menu</span>
          </button>
          
          <button type="button" class="sidebar-toggle desktop-only" aria-label="Toggle sidebar" @click="toggleSidebar" title="Toggle sidebar">
            <span class="material-icons">{{ sidebarCollapsed ? 'menu_open' : 'menu' }}</span>
          </button>

          <!-- Breadcrumbs -->
          <nav class="breadcrumbs" aria-label="Breadcrumb">
            <template v-for="(crumb, idx) in breadcrumbs" :key="idx">
              <RouterLink v-if="crumb.to" :to="crumb.to" class="crumb-link">
                {{ crumb.label }}
              </RouterLink>
              <span v-else class="crumb-current">{{ crumb.label }}</span>
              <span v-if="idx < breadcrumbs.length - 1" class="crumb-sep">/</span>
            </template>
          </nav>
        </div>

        <div class="topbar-right">
          <!-- Page title (shown on mobile) -->
          <h1 class="page-title-mobile">{{ pageTitle }}</h1>

          <!-- Actions -->
          <div class="topbar-actions">
            <div class="notifications" ref="notificationsDropdownRef">
              <button
                type="button"
                class="action-btn notification-btn"
                title="Notifications"
                aria-label="Notifications"
                :aria-expanded="notificationsOpen ? 'true' : 'false'"
                aria-controls="topbar-notifications-menu"
                @click="toggleNotifications"
              >
                <span class="material-icons">notifications_none</span>
                <span v-if="notificationCount > 0" class="notification-badge">{{ notificationCount }}</span>
              </button>
              <div
                v-if="notificationsOpen"
                id="topbar-notifications-menu"
                class="notifications-menu"
                aria-label="Notifications"
              >
                <header class="notifications-head">
                  <h3>Notifications</h3>
                  <span>{{ notificationCount }}</span>
                </header>
                <div v-if="notificationCount === 0" class="notifications-empty">No new alerts</div>
                <article
                  v-for="item in notifications"
                  :key="item.id"
                  class="notification-item"
                  :class="[item.type, { priority: item.priority }]"
                >
                  <button type="button" class="notification-open-btn" @click="openNotification(item)">
                    <div class="notification-copy">
                      <strong>{{ item.title }}</strong>
                      <span>{{ item.subtitle }}</span>
                    </div>
                  </button>
                  <button type="button" class="notification-dismiss" @click="dismissNotification(item.id)">Remove</button>
                </article>
              </div>
            </div>
            
            <!-- Daily revenue stat -->
            <div class="revenue-stat">
              <span class="material-icons">trending_up</span>
              <span class="revenue-text">Today: {{ dash.loading ? '—' : fmtRevenue(dash.todayRevenue) }}</span>
            </div>

            <!-- Profile dropdown -->
            <div class="profile-dropdown" ref="profileDropdownRef">
              <button
                type="button"
                class="profile-btn"
                aria-label="Open profile menu"
                :aria-expanded="profileOpen ? 'true' : 'false'"
                aria-controls="topbar-profile-menu"
                @click="toggleProfile"
              >
                <div class="profile-avatar">{{ auth.userInitials }}</div>
                <span class="material-icons chevron">expand_more</span>
              </button>
              
              <div v-if="profileOpen" id="topbar-profile-menu" class="profile-menu">
                <div class="profile-info">
                  <p class="profile-name">{{ auth.user?.full_name || auth.user?.username }}</p>
                  <p class="profile-role">{{ auth.userRole }}</p>
                </div>
                <div class="profile-actions">
                  <button class="profile-action" @click="openSettings">
                    <span class="material-icons">person</span>
                    Settings
                  </button>
                  <button class="profile-action" @click="themeStore.toggleTheme()">
                    <span class="material-icons">{{ themeStore.isDark ? 'light_mode' : 'dark_mode' }}</span>
                    {{ themeStore.isDark ? 'Light Mode' : 'Dark Mode' }}
                  </button>
                  <button class="profile-action logout" @click="handleLogout">
                    <span class="material-icons">logout</span>
                    Sign Out
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Page header -->
      <div v-if="showShellHeader" class="page-header">
        <div class="page-header-content">
          <h1 class="page-title">{{ pageTitle }}</h1>
        </div>
      </div>

      <main class="content-area">
        <RouterView />
      </main>
    </section>

    <div v-if="lockCountdownVisible" class="lock-warning-popup" role="status" aria-live="polite">
      <span class="material-icons">schedule</span>
      <p>{{ lockCountdownLabel }}</p>
    </div>

    <div v-if="priorityPopupVisible" class="priority-popup-backdrop" @click.self="closePriorityPopup">
      <article class="priority-popup">
        <header>
          <h3>Attention Needed</h3>
          <p>Review these items before you start. You can dismiss them or check notifications for details.</p>
        </header>

        <ul>
          <li v-for="item in priorityNotifications" :key="item.id" class="priority-alert-item">
            <div class="priority-alert-content">
              <strong>{{ item.title }}</strong>
              <span>{{ item.subtitle }}</span>
            </div>
            <button type="button" class="priority-dismiss-btn" @click="dismissNotification(item.id)" title="Remove forever">
              <span class="material-icons">close</span>
            </button>
          </li>
        </ul>

        <footer>
          <button type="button" class="btn-popup ghost" @click="closePriorityPopup">Got It</button>
          <button type="button" class="btn-popup primary" @click="openPriorityCenter">View All Notifications</button>
        </footer>
      </article>
    </div>
  </div>
</template>

<style scoped>
/* ═══════════════════════════════════════════════════════════════════════════
   PHARMAX APP SHELL — Green Medical Theme
   Clean, professional healthcare interface
   ═══════════════════════════════════════════════════════════════════════════ */

.shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  transition: grid-template-columns 0.3s ease;
  background: transparent;
}

.shell.sidebar-collapsed {
  grid-template-columns: 72px minmax(0, 1fr);
}

.sidebar-container {
  border-right: 1px solid var(--border-subtle);
  background: linear-gradient(180deg, var(--bg-sidebar) 0%, var(--bg-card) 100%);
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
  transition: all 0.3s ease;
  box-shadow: inset -1px 0 0 var(--border-subtle);
}

.sidebar-container.collapsed {
  width: 72px;
}

.main-area {
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: var(--bg-canvas);
}

/* ─── Top Bar ──────────────────────────────────────────────────────────────── */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-card);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 10;
  box-shadow: var(--shadow-xs);
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.menu-toggle,
.sidebar-toggle {
  width: 40px;
  height: 40px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  align-items: center;
  justify-content: center;
  display: none;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.menu-toggle:hover,
.sidebar-toggle:hover {
  background: var(--bg-hover);
  color: var(--primary);
  border-color: var(--primary);
}

.menu-toggle .material-icons,
.sidebar-toggle .material-icons {
  font-size: 20px;
}

.sidebar-toggle.desktop-only {
  display: flex;
}

.mobile-only {
  display: none;
}

/* ─── Breadcrumbs ──────────────────────────────────────────────────────────── */
.breadcrumbs {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 13px;
}

.crumb-link {
  color: var(--text-muted);
  transition: color var(--transition-fast);
}

.crumb-link:hover {
  color: var(--text-primary);
}

.crumb-sep {
  color: var(--text-disabled);
  font-size: 12px;
}

.crumb-current {
  color: var(--text-primary);
  font-weight: 500;
}

/* ─── Revenue Stat (Figma Style) ────────────────────────────────────────────── */
.revenue-stat {
  display: none;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: var(--radius-md);
  background: var(--success-bg);
  border: 1px solid var(--success-tint);
}

@media (min-width: 1024px) {
  .revenue-stat {
    display: flex;
  }
}

.revenue-stat .material-icons {
  font-size: 16px;
  color: var(--success);
}

.revenue-text {
  font-size: 12px;
  font-weight: 600;
  color: var(--success);
}

/* ─── Top Bar Actions ──────────────────────────────────────────────────────── */
.topbar-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.action-btn {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  background: var(--bg-card);
  color: var(--text-secondary);
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
  box-shadow: var(--shadow-xs);
}

.action-btn:hover {
  background: var(--bg-hover);
  color: var(--primary);
  border-color: var(--primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.action-btn .material-icons {
  font-size: 18px;
}

.notification-btn {
  position: relative;
}

.notifications {
  position: relative;
}

.notifications-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: min(380px, 82vw);
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  z-index: 100;
  overflow: hidden;
}

.notifications-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-subtle);
}

.notifications-head h3 {
  margin: 0;
  font-size: 13px;
}

.notifications-head span {
  font-size: 11px;
  color: var(--text-muted);
}

.notifications-empty {
  padding: 14px 12px;
  font-size: 12px;
  color: var(--text-muted);
}

.notification-item {
  width: 100%;
  border-bottom: 1px solid var(--border-subtle);
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.notification-item:last-child {
  border-bottom: 0;
}

.notification-item:hover {
  background: var(--bg-hover);
}

.notification-item:focus-within {
  background: var(--bg-hover);
}

.notification-item.priority {
  border-left: 3px solid var(--warning);
}

.notification-item.error {
  border-left: 3px solid var(--error);
}

.notification-item.info {
  border-left: 3px solid var(--info);
}

.notification-copy {
  display: grid;
  gap: 3px;
  text-align: left;
}

.notification-open-btn {
  flex: 1;
  border: 0;
  background: transparent;
  color: inherit;
  min-height: 40px;
  padding: 10px 0 10px 12px;
  text-align: inherit;
  cursor: pointer;
  display: block;
}

.notification-copy strong {
  font-size: 12px;
  color: var(--text-primary);
}

.notification-copy span {
  font-size: 11px;
  color: var(--text-muted);
}

.notification-dismiss {
  border: 1px solid var(--border-default);
  border-radius: 999px;
  background: transparent;
  color: var(--text-secondary);
  min-height: 36px;
  margin: 0 12px 0 0;
  padding: 0 10px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
}

.notification-dismiss:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--error);
  color: white;
  font-size: 10px;
  font-weight: 600;
  display: grid;
  place-items: center;
  border: 2px solid var(--bg-card);
}

/* ─── Profile Dropdown (Figma Style) ────────────────────────────────────────── */
.profile-dropdown {
  position: relative;
}

.profile-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 40px;
  padding: 4px 6px;
  border: 1px solid transparent;
  background: var(--bg-card);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast);
  box-shadow: var(--shadow-xs);
}

.profile-btn:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
  box-shadow: var(--shadow-sm);
}

.profile-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  display: grid;
  place-items: center;
  font-size: 12px;
  font-weight: 600;
}

.profile-btn .chevron {
  font-size: 18px;
  color: var(--text-muted);
}

.profile-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 220px;
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  z-index: 50;
  overflow: hidden;
}

.profile-info {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-subtle);
}

.profile-name {
  margin: 0;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.profile-role {
  margin: 2px 0 0;
  font-size: 11px;
  color: var(--text-muted);
}

.profile-actions {
  padding: 4px;
}

.profile-action {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border: none;
  background: transparent;
  text-align: left;
  font-size: 13px;
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.profile-action:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.profile-action.logout {
  color: var(--error);
}

.profile-action.logout:hover {
  background: var(--error-bg);
}

.profile-action .material-icons {
  font-size: 18px;
}

.page-title-mobile {
  display: none;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

/* ─── Page Header ──────────────────────────────────────────────────────────── */
.page-header {
  padding: var(--space-4) var(--space-4) var(--space-2);
}

.page-header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
  padding: var(--space-3) var(--space-4);
}

.page-title {
  margin: 0;
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

/* ─── Content Area ─────────────────────────────────────────────────────────── */
.content-area {
  flex: 1;
  padding: 0 var(--space-4) var(--space-4);
  min-height: 0;
}

/* ─── Backdrop ─────────────────────────────────────────────────────────────── */
.backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  border: 0;
  padding: 0;
  z-index: 20;
  backdrop-filter: blur(2px);
}

.lock-warning-popup {
  position: fixed;
  top: 76px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 88;
  width: min(680px, calc(100vw - 24px));
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--warning);
  background: var(--warning-bg);
  color: var(--text-primary);
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(8px);
}

.lock-warning-popup .material-icons {
  font-size: 18px;
  color: var(--warning);
  margin-top: 1px;
}

.lock-warning-popup p {
  margin: 0;
  font-size: 13px;
  line-height: 1.35;
}

.priority-popup-backdrop {
  position: fixed;
  inset: 0;
  background: var(--overlay-bg);
  z-index: 90;
  display: grid;
  place-items: center;
  padding: 20px;
}

.priority-popup {
  width: min(520px, 100%);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  box-shadow: var(--shadow-xl);
  padding: 18px;
  display: grid;
  gap: 12px;
}

.priority-popup header h3 {
  margin: 0;
  font-size: 18px;
}

.priority-popup header p {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--text-muted);
}

.priority-popup ul {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
}

.priority-alert-item {
  width: 100%;
  border: 1px solid var(--warning-tint);
  border-radius: var(--radius-md);
  background: var(--warning-bg);
  text-align: left;
  padding: 10px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.priority-alert-content {
  display: grid;
  gap: 4px;
  flex: 1;
  min-width: 0;
}

.priority-alert-item strong {
  font-size: 13px;
  color: var(--text-primary);
}

.priority-alert-item span {
  font-size: 11px;
  color: var(--text-secondary);
}

.priority-dismiss-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  background: var(--bg-elevated);
  color: var(--text-muted);
  cursor: pointer;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  transition: all var(--transition-fast);
}

.priority-dismiss-btn .material-icons {
  font-size: 16px;
}

.priority-dismiss-btn:hover {
  background: var(--error-bg);
  border-color: var(--error);
  color: var(--error);
}

.priority-popup footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.btn-popup {
  min-height: 40px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
  padding: 0 12px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
}

.btn-popup.primary {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
  box-shadow: var(--shadow-sm);
}

/* ─── Responsive ───────────────────────────────────────────────────────────── */
@media (max-width: 1024px) {
  .shell {
    grid-template-columns: 1fr;
  }

  .sidebar-container {
    position: fixed;
    z-index: 24;
    top: 0;
    left: 0;
    bottom: 0;
    width: 280px;
    transform: translateX(-102%);
    transition: transform 200ms ease;
    box-shadow: var(--shadow-lg);
  }

  .sidebar-container.is-open {
    transform: translateX(0);
  }

  .menu-toggle {
    display: inline-flex;
  }

  .breadcrumbs {
    display: none;
  }

  .page-title-mobile {
    display: block;
  }

  .page-header {
    padding: var(--space-3) var(--space-3) var(--space-2);
  }

  .page-header-content {
    padding: var(--space-2) var(--space-3);
  }

  .page-title {
    font-size: 20px;
  }

  .content-area {
    padding: 0 var(--space-3) var(--space-3);
  }

  .topbar {
    padding: var(--space-2) var(--space-3);
  }
}
</style>
