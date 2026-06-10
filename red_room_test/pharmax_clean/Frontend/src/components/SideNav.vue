<script setup>
import { computed, nextTick, ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['navigate', 'toggle-sidebar'])
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const searchQuery = ref('')
const showSearch = ref(false)
const searchInputRef = ref(null)
const selectedResultIndex = ref(0)
const GROUP_KEYS = ['products', 'stockPages', 'invoices', 'analyticsPages', 'reportPages', 'teamAccess', 'settingsPages']
const COLLAPSED_GROUP_CLICK_DELAY_MS = 220

function buildClosedGroups() {
  return GROUP_KEYS.reduce((acc, key) => {
    acc[key] = false
    return acc
  }, {})
}

// Groups that are currently expanded
const openGroups = ref(buildClosedGroups())
let collapsedGroupClickTimer = null

// Keyboard shortcut for search
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown)
  if (collapsedGroupClickTimer) {
    clearTimeout(collapsedGroupClickTimer)
    collapsedGroupClickTimer = null
  }
})

function handleKeydown(e) {
  const key = e.key.toLowerCase()

  // Cmd+K or Ctrl+K to open search
  if ((e.metaKey || e.ctrlKey) && key === 'k') {
    e.preventDefault()
    openSearch()
    return
  }

  // Cmd+B or Ctrl+B to toggle sidebar rail
  if ((e.metaKey || e.ctrlKey) && key === 'b') {
    e.preventDefault()
    emit('toggle-sidebar')
    return
  }

  if (key === 'escape' && showSearch.value) {
    closeSearch()
  }
}

function openSearch() {
  showSearch.value = true
  nextTick(() => {
    searchInputRef.value?.focus()
  })
}

function closeSearch() {
  showSearch.value = false
  searchQuery.value = ''
  selectedResultIndex.value = 0
}

function toggleSearch() {
  if (showSearch.value) {
    closeSearch()
    return
  }

  openSearch()
}

function openGroupExclusively(key) {
  openGroups.value = GROUP_KEYS.reduce((acc, groupKey) => {
    acc[groupKey] = groupKey === key
    return acc
  }, {})
}

function toggleGroup(key) {
  const isCurrentlyOpen = Boolean(openGroups.value[key])
  if (isCurrentlyOpen) {
    openGroups.value = buildClosedGroups()
    return
  }

  openGroupExclusively(key)
}

function isGroupOpen(key) {
  return Boolean(openGroups.value[key])
}

function hasRole(item, role) {
  if (!role) return true
  return item.roles.includes(role)
}

function canAccessChild(child) {
  return hasRole(child, auth.userRole)
}

function handleGroupClick(item) {
  if (props.collapsed) {
    if (collapsedGroupClickTimer) {
      clearTimeout(collapsedGroupClickTimer)
    }
    collapsedGroupClickTimer = window.setTimeout(() => {
      const firstAccessibleChild = item.children.find(canAccessChild)
      if (firstAccessibleChild) {
        router.push(firstAccessibleChild.to)
        emit('navigate')
      }
      collapsedGroupClickTimer = null
    }, COLLAPSED_GROUP_CLICK_DELAY_MS)
    return
  }

  toggleGroup(item.group)
}

function handleCollapsedGroupDoubleClick(item, event) {
  if (!props.collapsed) {
    return
  }

  event.preventDefault()
  event.stopPropagation()

  if (collapsedGroupClickTimer) {
    clearTimeout(collapsedGroupClickTimer)
    collapsedGroupClickTimer = null
  }

  emit('toggle-sidebar')
  nextTick(() => {
    openGroupExclusively(item.group)
  })
}

// Navigation structure with role-specific customization
const navSections = [
  {
    section: 'main',
    items: [
      { to: '/dashboard', icon: 'space_dashboard', label: 'Dashboard', roles: ['ADMIN', 'CASHIER', 'STAFF'] },
      {
        group: 'invoices',
        icon: 'receipt_long',
        label: 'Invoices',
        roles: ['ADMIN', 'CASHIER', 'STAFF'],
        children: [
          { to: '/invoices/create', icon: 'add_circle', label: 'Create Invoice', roles: ['ADMIN', 'STAFF', 'CASHIER'] },
          { to: '/invoices', icon: 'list_alt', label: 'Invoices List', roles: ['ADMIN', 'CASHIER', 'STAFF'], exact: true },
          { to: '/cashier', icon: 'payments', label: 'Invoice Queue', roles: ['ADMIN', 'CASHIER'] },
        ],
      },
    ],
  },
  {
    section: 'Inventory',
    items: [
      {
        group: 'products',
        icon: 'inventory_2',
        label: 'Products',
        roles: ['ADMIN', 'CASHIER', 'STAFF'],
        children: [
          { to: '/products', icon: 'list_alt', label: 'Master List', roles: ['ADMIN', 'CASHIER', 'STAFF'], exact: true },
          { to: '/products/units', icon: 'grid_view', label: 'Units & Pricing', roles: ['ADMIN', 'CASHIER', 'STAFF'] },
        ],
      },
      {
        group: 'stockPages',
        icon: 'warehouse',
        label: 'Stock Management',
        roles: ['ADMIN', 'CASHIER', 'STAFF'],
        children: [
          { to: '/stock', icon: 'tune', label: 'Stock Adjustments', roles: ['ADMIN', 'CASHIER', 'STAFF'], exact: true },
          { to: '/stock/out-of-stock', icon: 'remove_shopping_cart', label: 'Out-of-Stock Items', roles: ['ADMIN', 'CASHIER', 'STAFF'] },
          { to: '/stock/low-stock', icon: 'inventory', label: 'Low Stock Watchlist', roles: ['ADMIN', 'CASHIER', 'STAFF'] },
        ],
      },
    ],
  },
  {
    section: 'Reports',
    items: [
      {
        group: 'analyticsPages',
        icon: 'insights',
        label: 'Analytics',
        roles: ['ADMIN'],
        children: [
          { to: '/analytics/revenue-trend', icon: 'trending_up', label: 'Revenue Trend', roles: ['ADMIN'] },
          { to: '/analytics/product-movement', icon: 'moving', label: 'Product Insights', roles: ['ADMIN'] },
          { to: '/analytics/staff-performance', icon: 'groups', label: 'Staff Performance', roles: ['ADMIN'] },
          { to: '/analytics/payment-insights', icon: 'payments', label: 'Payment Insights', roles: ['ADMIN'] },
        ],
      },
      {
        group: 'reportPages',
        icon: 'description',
        label: 'Reports',
        roles: ['ADMIN', 'CASHIER'],
        children: [
          { to: '/reports/end-of-day', icon: 'today', label: 'End of Day Report', roles: ['ADMIN', 'CASHIER'] },
          { to: '/reports/highest-invoices', icon: 'emoji_events', label: 'Largest Customer Bills', roles: ['ADMIN', 'CASHIER'] },
          { to: '/reports/product-sales', icon: 'leaderboard', label: 'Best-Selling Products', roles: ['ADMIN', 'CASHIER'] },
          { to: '/reports/expiring-drugs', icon: 'warning', label: 'Expiry Watch (Manual)', roles: ['ADMIN', 'CASHIER'] },
        ],
      },
      { to: '/activity-logs', icon: 'history', label: 'Activity Logs', roles: ['ADMIN', 'CASHIER', 'STAFF'] },
    ],
  },
  {
    section: 'Settings',
    items: [
      {
        group: 'teamAccess',
        icon: 'people',
        label: 'Team & Access',
        roles: ['ADMIN'],
        children: [
          { to: '/users', icon: 'badge', label: 'Accounts', roles: ['ADMIN'], exact: true },
          { to: '/users/activity', icon: 'history', label: 'Activity', roles: ['ADMIN'] },
          { to: '/users/tasks', icon: 'task_alt', label: 'Tasks & Notes', roles: ['ADMIN'] },
        ],
      },
      {
        group: 'settingsPages',
        icon: 'tune',
        label: 'Settings',
        roles: ['ADMIN', 'CASHIER', 'STAFF'],
        children: [
          { to: '/settings/profile', icon: 'badge', label: 'Profile & Account', roles: ['ADMIN', 'CASHIER', 'STAFF'] },
          { to: '/settings/pharmacy', icon: 'local_hospital', label: 'Pharmacy Preferences', roles: ['ADMIN'] },
          { to: '/settings/workflow', icon: 'swap_horiz', label: 'Workflow Defaults', roles: ['ADMIN'] },
          { to: '/settings/notifications', icon: 'notifications_active', label: 'Priority Notifications', roles: ['ADMIN', 'CASHIER', 'STAFF'] },
          { to: '/settings/accessibility', icon: 'accessibility_new', label: 'Accessibility Options', roles: ['ADMIN', 'CASHIER', 'STAFF'] },
          { to: '/settings/safety', icon: 'verified_user', label: 'Safety Controls', roles: ['ADMIN', 'CASHIER', 'STAFF'] },
        ],
      },
    ],
  },
]

const filteredSections = computed(() => {
  const role = auth.userRole

  return navSections
    .map(section => ({
      ...section,
      items: section.items
        .filter(item => hasRole(item, role))
        .map(item => {
          if (!item.group) return item
          return {
            ...item,
            children: item.children.filter(canAccessChild),
          }
        })
        .filter(item => !item.group || item.children.length > 0),
    }))
    .filter(section => section.items.length > 0)
})

function isGroupActive(group) {
  return group.children.some(c => route.path === c.to || route.path.startsWith(c.to + '/'))
}

function isChildActive(child) {
  if (child.exact) {
    return route.path === child.to
  }
  return route.path === child.to || route.path.startsWith(child.to + '/')
}

async function handleLogout() {
  await auth.logout()
  router.replace('/login')
}

// Search through all nav items
const searchResults = computed(() => {
  if (!searchQuery.value.trim()) return []
  
  const query = searchQuery.value.toLowerCase()
  const results = []
  
  filteredSections.value.forEach(section => {
    section.items.forEach(item => {
      if (item.group) {
        item.children.filter(canAccessChild).forEach(child => {
          if (
            child.label.toLowerCase().includes(query) ||
            item.label.toLowerCase().includes(query) ||
            section.section.toLowerCase().includes(query)
          ) {
            results.push({
              ...child,
              section: section.section,
              parent: item.label
            })
          }
        })
      } else if (item.label.toLowerCase().includes(query)) {
        results.push({ ...item, section: section.section })
      }
    })
  })
  
  return results.slice(0, 8)
})

watch(searchQuery, () => {
  selectedResultIndex.value = 0
})

watch(
  () => route.path,
  () => {
    const allGroups = navSections
      .flatMap((section) => section.items)
      .filter((item) => Boolean(item.group))

    const activeGroup = allGroups.find((item) => isGroupActive(item))
    if (!activeGroup) {
      openGroups.value = buildClosedGroups()
      return
    }

    openGroupExclusively(activeGroup.group)
  },
  { immediate: true },
)

watch(
  () => props.collapsed,
  (collapsed) => {
    if (collapsed) {
      openGroups.value = buildClosedGroups()
    }
  },
)

function handleSearchKeydown(e) {
  if (!searchResults.value.length) {
    if (e.key === 'Escape') closeSearch()
    return
  }

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    selectedResultIndex.value = (selectedResultIndex.value + 1) % searchResults.value.length
    return
  }

  if (e.key === 'ArrowUp') {
    e.preventDefault()
    selectedResultIndex.value = (selectedResultIndex.value - 1 + searchResults.value.length) % searchResults.value.length
    return
  }

  if (e.key === 'Enter') {
    e.preventDefault()
    const selected = searchResults.value[selectedResultIndex.value]
    if (selected) navigateToResult(selected.to)
    return
  }

  if (e.key === 'Escape') {
    e.preventDefault()
    closeSearch()
  }
}

function navigateToResult(path) {
  router.push(path)
  closeSearch()
  emit('navigate')
}
</script>

<template>
  <div class="sidebar" :class="{ 'is-collapsed': collapsed }">
    <!-- Brand -->
    <div class="brand">
      <div class="brand-icon">
        <span class="material-icons">local_pharmacy</span>
      </div>
      <div class="brand-text">
        <span class="brand-name">Pharmax</span>
        <span class="brand-env">Pharmacy</span>
      </div>
    </div>

    <!-- Search trigger (command palette style) -->
    <button
      type="button"
      class="search-trigger"
      :title="collapsed ? 'Search navigation' : ''"
      :aria-expanded="showSearch ? 'true' : 'false'"
      aria-haspopup="dialog"
      aria-controls="sidebar-search-dialog"
      @click="toggleSearch"
    >
      <span class="material-icons">search</span>
      <span v-if="!collapsed" class="search-text">Search pages, tasks, modules...</span>
      <kbd v-if="!collapsed" class="search-kbd">⌘K</kbd>
    </button>

    <!-- Search Modal -->
    <Teleport to="body">
      <div v-show="showSearch" class="search-modal-backdrop" @click="closeSearch">
        <div
          id="sidebar-search-dialog"
          class="search-modal"
          role="dialog"
          aria-modal="true"
          aria-label="Search navigation"
          @click.stop
        >
          <div class="search-input-wrapper">
            <span class="material-icons">search</span>
            <input 
              ref="searchInputRef"
              v-model="searchQuery"
              type="text" 
              class="search-input"
              placeholder="Search navigation, reports, inventory..."
              @keydown="handleSearchKeydown"
            />
          </div>

          <div v-if="searchQuery.trim() && searchResults.length > 0" class="search-results-panel">
            <button
              v-for="(result, index) in searchResults"
              :key="result.to"
              type="button"
              class="search-result"
              :class="{ 'is-selected': index === selectedResultIndex }"
              @mouseenter="selectedResultIndex = index"
              @click="navigateToResult(result.to)"
            >
              <span class="material-icons">{{ result.icon }}</span>
              <div class="result-info">
                <span class="result-label">{{ result.label }}</span>
                <span class="result-path">{{ result.parent ? `${result.parent} › ` : '' }}{{ result.section }}</span>
              </div>
            </button>
          </div>

          <div v-else-if="searchQuery.trim()" class="search-empty">
            <span class="material-icons">search_off</span>
            <p>No results found</p>
          </div>

          <div v-else class="search-hint">
            <span class="material-icons">tips_and_updates</span>
            <p>Try: <strong>invoice</strong>, <strong>stock</strong>, <strong>dashboard</strong>, <strong>team</strong></p>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Navigation -->
    <nav class="nav">
      <template v-for="section in filteredSections" :key="section.section">
        <div v-if="section.section !== 'main'" class="nav-section-label">
          {{ section.section }}
        </div>

        <template v-for="item in section.items" :key="item.group ?? item.to">
          <!-- Group header (collapsible) -->
          <button
            v-if="item.group"
            type="button"
            class="nav-item"
            :class="{ active: isGroupActive(item), expanded: isGroupOpen(item.group) }"
            :title="collapsed ? item.label : ''"
            :aria-expanded="isGroupOpen(item.group) ? 'true' : 'false'"
            :aria-controls="collapsed ? undefined : `sidenav-group-${item.group}`"
            @click="handleGroupClick(item)"
            @dblclick="handleCollapsedGroupDoubleClick(item, $event)"
          >
            <span class="material-icons nav-icon">{{ item.icon }}</span>
            <span v-if="!collapsed" class="nav-label">{{ item.label }}</span>
            <span v-if="!collapsed" class="material-icons nav-chevron">expand_more</span>
          </button>

          <!-- Group children -->
          <div
            v-if="!collapsed && item.group && isGroupOpen(item.group)"
            :id="`sidenav-group-${item.group}`"
            class="nav-children"
          >
            <RouterLink
              v-for="child in item.children"
              :key="child.to"
              :to="child.to"
              class="nav-item nav-item--child"
              :class="{ active: isChildActive(child) }"
              @click="emit('navigate')"
            >
              <span class="nav-label">{{ child.label }}</span>
            </RouterLink>
          </div>

          <!-- Regular item -->
          <RouterLink
            v-else-if="!item.group"
            :to="item.to"
            class="nav-item"
            :title="collapsed ? item.label : ''"
            active-class="active"
            @click="emit('navigate')"
          >
            <span class="material-icons nav-icon">{{ item.icon }}</span>
            <span v-if="!collapsed" class="nav-label">{{ item.label }}</span>
            <span v-if="!collapsed && item.badge" class="nav-badge" :class="item.badge">{{ item.badge }}</span>
          </RouterLink>
        </template>
      </template>
    </nav>

    <!-- User block -->
    <div class="user-block" :class="{ compact: collapsed }">
      <div class="user-info">
        <div class="avatar">{{ auth.userInitials }}</div>
        <div v-if="!collapsed" class="user-meta">
          <span class="user-name">{{ auth.user?.full_name || auth.user?.username || 'User' }}</span>
          <span class="user-role">{{ auth.userRole || 'Guest' }}</span>
        </div>
      </div>
      <button type="button" class="logout-btn" :title="collapsed ? 'Sign out' : 'Sign out'" @click="handleLogout">
        <span class="material-icons">logout</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
/* ═══════════════════════════════════════════════════════════════════════════
   PHARMAX SIDEBAR — Green Medical Theme
   Clean, professional healthcare interface
   ═══════════════════════════════════════════════════════════════════════════ */

.sidebar {
  height: 100%;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  background:
    radial-gradient(700px circle at -10% -20%, rgba(15, 159, 137, 0.14), transparent 48%),
    var(--bg-sidebar);
}

.sidebar.is-collapsed {
  padding: var(--space-4) var(--space-2);
  align-items: center;
}

/* ─── Brand ────────────────────────────────────────────────────────────────── */
.brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-2) var(--space-3);
  border-bottom: 1px dashed var(--border-subtle);
}

.sidebar.is-collapsed .brand {
  justify-content: center;
  width: 100%;
  padding: 0;
}

.sidebar.is-collapsed .brand-text {
  display: none;
}

.brand-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  display: grid;
  place-items: center;
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
}

.brand-icon .material-icons {
  font-size: 18px;
  color: #fff;
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.brand-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.brand-env {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* ─── Search Trigger ───────────────────────────────────────────────────────── */
.search-trigger {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-height: 40px;
  padding: 0 var(--space-3);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-default);
  background: var(--bg-card);
  color: var(--text-muted);
  font-size: 13px;
  cursor: pointer;
  transition: border-color var(--transition-fast), background var(--transition-fast), box-shadow var(--transition-fast), transform var(--transition-fast);
  box-shadow: var(--shadow-xs);
}

.sidebar.is-collapsed .search-trigger {
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
}

.search-trigger:hover {
  border-color: var(--primary);
  background: var(--bg-elevated);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.search-trigger .material-icons {
  font-size: 16px;
}

.search-text {
  flex: 1;
  text-align: left;
}

.search-kbd {
  font-family: var(--font-ui);
  font-size: 11px;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  background: var(--kbd-bg);
  color: var(--text-tertiary);
  border: none;
}

/* ─── Navigation ───────────────────────────────────────────────────────────── */
.nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow-y: auto;
}

.sidebar.is-collapsed .nav {
  align-items: center;
  width: 100%;
}

.nav-section-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  padding: var(--space-4) var(--space-3) var(--space-2);
  margin-top: var(--space-2);
}

.nav-section-label:first-child {
  margin-top: 0;
}

.sidebar.is-collapsed .nav-section-label {
  display: none;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-height: 40px;
  padding: 0 var(--space-3);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  border: none;
  background: transparent;
  cursor: pointer;
  width: 100%;
  text-align: left;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.sidebar.is-collapsed .nav-item {
  width: 40px;
  height: 40px;
  padding: 0;
  justify-content: center;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  transform: translateX(2px);
}

.nav-item.active {
  background: linear-gradient(90deg, var(--primary-tint) 0%, var(--primary-bg) 100%);
  color: var(--text-primary);
  box-shadow: var(--shadow-xs);
  border: 1px solid rgba(15, 159, 137, 0.24);
}

.nav-item.active .nav-icon {
  color: var(--primary);
}

.nav-icon {
  font-size: 18px;
  color: var(--text-tertiary);
  flex-shrink: 0;
  transition: color var(--transition-fast);
}

.nav-item:hover .nav-icon {
  color: var(--text-secondary);
}

.nav-label {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar.is-collapsed .nav-label,
.sidebar.is-collapsed .nav-chevron,
.sidebar.is-collapsed .nav-badge {
  display: none;
}

.nav-chevron {
  font-size: 18px !important;
  color: var(--text-muted);
  transition: transform var(--transition-fast);
  margin-left: auto;
}

.nav-item.expanded .nav-chevron {
  transform: rotate(180deg);
}

/* Nav children (nested items) */
.nav-children {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding-left: var(--space-6);
  margin-bottom: var(--space-1);
}

.nav-item--child {
  min-height: 40px;
  font-size: 13px;
  color: var(--text-tertiary);
  padding-left: var(--space-4);
  border-left: 1px solid var(--border-subtle);
  border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
}

.nav-item--child:hover {
  color: var(--text-primary);
  border-left-color: var(--text-muted);
}

.nav-item--child.active {
  color: var(--primary);
  border-left-color: var(--primary);
  background: var(--primary-bg);
}

/* Nav badges */
.nav-badge {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  letter-spacing: 0.02em;
}

.nav-badge.new {
  background: var(--success-tint);
  color: var(--success);
}

.nav-badge.beta {
  background: var(--info-tint);
  color: var(--info);
}

/* ─── User Block ───────────────────────────────────────────────────────────── */
.user-block {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3);
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  box-shadow: var(--shadow-xs);
}

.user-block.compact {
  flex-direction: column;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-2);
  width: 100%;
}

.user-block.compact .user-info {
  justify-content: center;
}

.user-block.compact .logout-btn {
  background: var(--bg-recessed);
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 0;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  font-size: 12px;
  font-family: var(--font-data);
  font-weight: 600;
  color: #fff;
  flex-shrink: 0;
  box-shadow: var(--shadow-xs);
}

.user-meta {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: capitalize;
}

.logout-btn {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  border: none;
  background: transparent;
  color: var(--text-muted);
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: color var(--transition-fast), background var(--transition-fast);
}

.logout-btn:hover {
  color: var(--error);
  background: var(--error-tint);
}

.logout-btn .material-icons {
  font-size: 16px;
}

/* ─── Search Modal ─────────────────────────────────────────────────────────── */
.search-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.58);
  backdrop-filter: blur(1px);
  z-index: 9999;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 10vh;
  animation: fadeIn 0.12s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.search-modal {
  width: 90%;
  max-width: 600px;
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-default);
  box-shadow: var(--shadow-xl);
  overflow: hidden;
  animation: slideDown 0.14s ease;
}

@keyframes slideDown {
  from { 
    opacity: 0;
    transform: translateY(-20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
}

.search-input-wrapper .material-icons {
  font-size: 24px;
  color: var(--text-muted);
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 16px;
  color: var(--text-primary);
  outline: none;
}

.search-input:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
  box-shadow: 0 0 0 3px var(--primary-tint);
  border-radius: var(--radius-sm);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-results-panel {
  max-height: 400px;
  overflow-y: auto;
}

.search-result {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border: none;
  background: transparent;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: background var(--transition-fast);
  border-bottom: 1px solid var(--border-subtle);
}

.search-result:last-child {
  border-bottom: none;
}

.search-result:hover {
  background: var(--bg-hover);
}

.search-result.is-selected {
  background: linear-gradient(90deg, var(--primary-bg) 0%, var(--primary-tint) 100%);
}

.search-result .material-icons {
  font-size: 20px;
  color: var(--text-tertiary);
}

.result-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.result-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.result-path {
  font-size: 12px;
  color: var(--text-muted);
}

.search-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-8) var(--space-4);
  color: var(--text-muted);
}

.search-empty .material-icons {
  font-size: 48px;
  opacity: 0.3;
}

.search-empty p {
  margin: 0;
  font-size: 14px;
}

.search-hint {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4);
  color: var(--text-muted);
  font-size: 13px;
}

.search-hint .material-icons {
  font-size: 18px;
  color: var(--primary);
}
</style>
