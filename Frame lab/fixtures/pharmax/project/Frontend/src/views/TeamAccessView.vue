<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { usersService } from '@/services/users'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const toast = useToast()

const loading = ref(false)
const saving = ref(false)
const error = ref('')
const users = ref([])

function resolveViewFromPath(path) {
  if (path.startsWith('/users/activity')) return 'activity'
  if (path.startsWith('/users/tasks')) return 'tasks'
  return 'accounts'
}

function viewPath(view) {
  if (view === 'activity') return '/users/activity'
  if (view === 'tasks') return '/users/tasks'
  return '/users'
}

const activeView = ref(resolveViewFromPath(route.path))
const activityLogs = ref([])
const activityLoading = ref(false)
const activityError = ref('')
const taskLoading = ref(false)
const taskError = ref('')
const taskSaving = ref(false)
const teamTasks = ref([])
const selectedCredentialUser = ref(null)
const credentialsSaving = ref(false)

const createFormErrors = ref({
  username: '',
  email: '',
  password: '',
  pin: '',
})

const credentialsForm = ref({
  password: '',
  pin: '',
})

const credentialsErrors = ref({
  password: '',
  pin: '',
  general: '',
})

const search = ref('')
const roleFilter = ref('ALL')
const statusFilter = ref('ALL')
let filterDebounceTimer = null
let presencePollTimer = null

const createForm = ref({
  full_name: '',
  username: '',
  email: '',
  role: 'STAFF',
  password: '',
  pin: '',
})

const taskForm = ref({
  assignee_user_id: '',
  title: '',
  note: '',
})

const canManage = computed(() => auth.userRole === 'ADMIN')
const pendingTasks = computed(() => teamTasks.value.filter((task) => !task.is_done))
const completedTasks = computed(() => teamTasks.value.filter((task) => task.is_done))

function clearFilterDebounce() {
  if (filterDebounceTimer) {
    window.clearTimeout(filterDebounceTimer)
    filterDebounceTimer = null
  }
}

async function loadTasks() {
  if (!canManage.value) return

  taskLoading.value = true
  taskError.value = ''
  try {
    teamTasks.value = await usersService.listTasks({ limit: 120 })
  } catch (err) {
    taskError.value = err?.message || 'Could not load tasks right now.'
  } finally {
    taskLoading.value = false
  }
}

async function assignTask() {
  if (!canManage.value) return

  const assignee = String(taskForm.value.assignee_user_id || '').trim()
  const title = String(taskForm.value.title || '').trim()
  const note = String(taskForm.value.note || '').trim()

  if (!assignee || !title || !note) {
    toast.error('Please choose a teammate, add a task name, and write a note first.')
    return
  }

  taskSaving.value = true
  try {
    await usersService.assignTask({
      assignee_user_id: assignee,
      title,
      note,
    })
    taskForm.value = { assignee_user_id: '', title: '', note: '' }
    toast.success('Task sent successfully.')
    await loadTasks()
    await loadActivity()
  } catch (err) {
    toast.error(err?.message || 'Could not send task.')
  } finally {
    taskSaving.value = false
  }
}

async function toggleTaskDone(task) {
  if (!canManage.value) return
  try {
    await usersService.updateTaskStatus(task.id, !task.is_done)
    await loadTasks()
    await loadActivity()
  } catch (err) {
    toast.error(err?.message || 'Could not update this task right now.')
  }
}

function statusBadgeClass(isActive) {
  return isActive ? 'active' : 'inactive'
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function currentStatusFilterValue() {
  if (statusFilter.value === 'ACTIVE') return true
  if (statusFilter.value === 'INACTIVE') return false
  return null
}

function resetCreateErrors() {
  createFormErrors.value = { username: '', email: '', password: '', pin: '' }
}

function validateCreateForm() {
  resetCreateErrors()
  const username = String(createForm.value.username || '').trim()
  const email = String(createForm.value.email || '').trim()
  const password = String(createForm.value.password || '')
  const pin = String(createForm.value.pin || '').trim()

  if (!username) createFormErrors.value.username = 'Username is required.'
  if (!email) createFormErrors.value.email = 'Email is required.'
  if (!password) createFormErrors.value.password = 'Password is required.'
  if (password && password.length < 8) createFormErrors.value.password = 'Password must be at least 8 characters.'
  if (pin && !/^\d{4,6}$/.test(pin)) createFormErrors.value.pin = 'PIN must be 4 to 6 digits.'

  return !Object.values(createFormErrors.value).some(Boolean)
}

async function loadUsers({ silent = false } = {}) {
  if (!canManage.value) return

  if (!silent) loading.value = true
  error.value = ''
  try {
    users.value = await usersService.list({
      search: search.value.trim() || null,
      role: roleFilter.value === 'ALL' ? null : roleFilter.value,
      isActive: currentStatusFilterValue(),
      limit: 300,
    })
  } catch (err) {
    error.value = err?.message || 'Could not load team accounts.'
  } finally {
    if (!silent) loading.value = false
  }
}

async function loadActivity() {
  if (!canManage.value) return

  activityLoading.value = true
  activityError.value = ''
  try {
    activityLogs.value = await usersService.listActivity({ limit: 80 })
  } catch (err) {
    activityError.value = err?.message || 'Could not load team activity.'
  } finally {
    activityLoading.value = false
  }
}

async function createUser() {
  if (!canManage.value) return
  if (!validateCreateForm()) {
    toast.error('Please fix the highlighted fields before creating account.')
    return
  }

  const cleanPin = String(createForm.value.pin || '').trim()

  saving.value = true
  try {
    await usersService.create({
      full_name: createForm.value.full_name || null,
      username: createForm.value.username.trim(),
      email: createForm.value.email.trim(),
      role: createForm.value.role,
      password: createForm.value.password,
      pin: cleanPin || null,
    })

    toast.success('Team account created successfully.')
    createForm.value = {
      full_name: '',
      username: '',
      email: '',
      role: 'STAFF',
      password: '',
      pin: '',
    }
    resetCreateErrors()
    await loadUsers()
    await loadActivity()
  } catch (err) {
    toast.error(err?.message || 'Could not create account.')
  } finally {
    saving.value = false
  }
}

async function toggleUserStatus(user) {
  if (!canManage.value) return
  const next = !user.is_active
  try {
    await usersService.updateStatus(user.id, next)
    user.is_active = next
    if (!next) user.last_logout_at = new Date().toISOString()
    toast.success(next ? 'User account activated.' : 'User account deactivated.')
    await loadActivity()
  } catch (err) {
    toast.error(err?.message || 'Could not update account status.')
  }
}

async function changeRole(user, event) {
  if (!canManage.value) return
  const nextRole = String(event.target.value || '').toUpperCase()
  if (!nextRole || nextRole === user.role) return

  try {
    const updated = await usersService.updateRole(user.id, nextRole)
    user.role = updated.role
    toast.success('User role updated.')
    await loadActivity()
  } catch (err) {
    event.target.value = user.role
    toast.error(err?.message || 'Could not update role.')
  }
}

function openCredentialEditor(user) {
  selectedCredentialUser.value = user
  credentialsForm.value = { password: '', pin: '' }
  credentialsErrors.value = { password: '', pin: '', general: '' }
}

function closeCredentialEditor() {
  selectedCredentialUser.value = null
  credentialsForm.value = { password: '', pin: '' }
  credentialsErrors.value = { password: '', pin: '', general: '' }
}

function validateCredentialForm() {
  credentialsErrors.value = { password: '', pin: '', general: '' }
  const password = String(credentialsForm.value.password || '')
  const pin = String(credentialsForm.value.pin || '').trim()

  if (!password && !pin) {
    credentialsErrors.value.general = 'Enter a new password and/or PIN before saving.'
    return false
  }
  if (password && password.trim().length < 8) {
    credentialsErrors.value.password = 'Password must be at least 8 characters.'
  }
  if (pin && !/^\d{4,6}$/.test(pin)) {
    credentialsErrors.value.pin = 'PIN must be 4 to 6 digits.'
  }

  return !Object.values(credentialsErrors.value).some(Boolean)
}

async function saveCredentials() {
  if (!selectedCredentialUser.value || !canManage.value) return
  if (!validateCredentialForm()) return

  credentialsSaving.value = true
  const user = selectedCredentialUser.value
  try {
    const password = String(credentialsForm.value.password || '').trim()
    const pin = String(credentialsForm.value.pin || '').trim()

    if (password) await usersService.resetPassword(user.id, password)
    if (pin) await usersService.resetPin(user.id, pin)

    toast.success('Credentials updated successfully.')
    await loadActivity()
    closeCredentialEditor()
  } catch (err) {
    credentialsErrors.value.general = err?.message || 'Could not update credentials.'
  } finally {
    credentialsSaving.value = false
  }
}

function relativeSeenLabel(user) {
  if (!user?.last_seen_at) return 'Never seen'
  const seenAt = new Date(user.last_seen_at).getTime()
  if (!Number.isFinite(seenAt)) return 'Unknown'
  const diffMs = Date.now() - seenAt
  if (diffMs < 60_000) return 'Seen just now'
  if (diffMs < 3_600_000) return `Seen ${Math.floor(diffMs / 60_000)} min ago`
  return `Seen ${Math.floor(diffMs / 3_600_000)}h ago`
}

function activityDetailsText(log) {
  if (!log?.details) return '—'
  if (typeof log.details === 'string') return log.details
  const pairs = Object.entries(log.details)
    .filter(([_, value]) => value !== null && value !== undefined && value !== '')
    .slice(0, 4)
    .map(([key, value]) => `${key}: ${value}`)

  return pairs.length ? pairs.join(' · ') : '—'
}

function activityDetailEntries(log) {
  if (!log?.details || typeof log.details !== 'object') return []
  return Object.entries(log.details)
    .filter(([_, value]) => value !== null && value !== undefined && value !== '')
    .slice(0, 6)
}

function actorLabel(log) {
  return log.actor_full_name || log.actor_username || 'Unknown user'
}

function setActiveView(view) {
  activeView.value = view
  const target = viewPath(view)
  if (route.path !== target) {
    router.push(target)
  }
}

watch([search, roleFilter, statusFilter], () => {
  clearFilterDebounce()
  filterDebounceTimer = window.setTimeout(() => {
    loadUsers()
  }, 220)
})

watch(
  () => route.path,
  (path) => {
    activeView.value = resolveViewFromPath(path)
  },
)

onMounted(loadUsers)
onMounted(loadActivity)
onMounted(loadTasks)
onMounted(() => {
  if (!canManage.value) return
  presencePollTimer = window.setInterval(() => {
    loadUsers({ silent: true })
  }, 45_000)
})

onBeforeUnmount(() => {
  clearFilterDebounce()
  if (presencePollTimer) {
    window.clearInterval(presencePollTimer)
    presencePollTimer = null
  }
})
</script>

<template>
  <section class="team-access" v-if="canManage">
    <header class="header panel-surface">
      <div class="header-copy">
        <h2>Team & Access</h2>
        <p>Manage accounts, review activity, and assign tasks from one simple workspace.</p>
      </div>
      <div class="header-controls">
        <label class="view-switch">
          <span>Choose view</span>
          <select :value="activeView" @change="setActiveView($event.target.value)">
            <option value="accounts">Accounts</option>
            <option value="activity">Activity Log</option>
            <option value="tasks">Tasks & Notes</option>
          </select>
        </label>
      </div>
    </header>

    <nav class="view-tabs panel-surface" aria-label="Team views">
      <button class="tab-btn" :class="{ active: activeView === 'accounts' }" @click="setActiveView('accounts')">Accounts</button>
      <button class="tab-btn" :class="{ active: activeView === 'activity' }" @click="setActiveView('activity')">Activity Log</button>
      <button class="tab-btn" :class="{ active: activeView === 'tasks' }" @click="setActiveView('tasks')">Tasks & Notes</button>
    </nav>

    <article class="panel create-panel" v-if="activeView === 'accounts'">
      <h3>Create Team Account</h3>
      <p class="hint">Add a team member and set their login details before they start work.</p>
      <div class="create-grid">
        <label>
          <span>Full Name</span>
          <input v-model="createForm.full_name" type="text" placeholder="e.g. Jane Okoro" />
        </label>
        <label :class="{ invalid: !!createFormErrors.username }">
          <span>Username</span>
          <input v-model="createForm.username" type="text" placeholder="e.g. jane.cashier" />
          <small v-if="createFormErrors.username" class="field-error">{{ createFormErrors.username }}</small>
        </label>
        <label :class="{ invalid: !!createFormErrors.email }">
          <span>Email</span>
          <input v-model="createForm.email" type="email" placeholder="e.g. jane@pharmax.local" />
          <small v-if="createFormErrors.email" class="field-error">{{ createFormErrors.email }}</small>
        </label>
        <label>
          <span>Role</span>
          <select v-model="createForm.role">
            <option value="STAFF">Staff</option>
            <option value="CASHIER">Cashier</option>
            <option value="ADMIN">Admin</option>
          </select>
        </label>
        <label :class="{ invalid: !!createFormErrors.password }">
          <span>Password</span>
          <input v-model="createForm.password" type="password" placeholder="At least 8 characters" />
          <small v-if="createFormErrors.password" class="field-error">{{ createFormErrors.password }}</small>
        </label>
        <label :class="{ invalid: !!createFormErrors.pin }">
          <span>PIN (optional)</span>
          <input v-model="createForm.pin" type="text" inputmode="numeric" placeholder="4 to 6 digits" />
          <small v-if="createFormErrors.pin" class="field-error">{{ createFormErrors.pin }}</small>
        </label>
      </div>
      <div class="create-actions">
        <button type="button" class="primary" :disabled="saving" @click="createUser">
          {{ saving ? 'Creating...' : 'Create Account' }}
        </button>
      </div>
    </article>

    <article class="panel" v-if="activeView === 'accounts'">
      <div class="panel-header">
        <div>
          <h3>Manage Team Accounts</h3>
          <p class="hint">Search, update roles, and manage account access.</p>
        </div>
      </div>
      <div class="filters">
        <label>
          <span>Search</span>
          <input v-model="search" type="text" placeholder="Find by name, username, or email" />
        </label>
        <label>
          <span>Role</span>
          <select v-model="roleFilter">
            <option value="ALL">All roles</option>
            <option value="ADMIN">Admin</option>
            <option value="CASHIER">Cashier</option>
            <option value="STAFF">Staff</option>
          </select>
        </label>
        <label>
          <span>Status</span>
          <select v-model="statusFilter">
            <option value="ALL">All accounts</option>
            <option value="ACTIVE">Active only</option>
            <option value="INACTIVE">Inactive only</option>
          </select>
        </label>
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <div class="table-wrap" v-else>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Username</th>
              <th>Role</th>
              <th>Status</th>
              <th>Presence</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!loading && users.length === 0">
              <td colspan="7" class="empty">No team account found for this filter.</td>
            </tr>
            <tr v-for="user in users" :key="user.id">
              <td>
                <strong>{{ user.full_name || '—' }}</strong>
                <div class="sub">{{ user.email }}</div>
              </td>
              <td class="mono">{{ user.username }}</td>
              <td>
                <select :value="user.role" @change="changeRole(user, $event)">
                  <option value="ADMIN">Admin</option>
                  <option value="CASHIER">Cashier</option>
                  <option value="STAFF">Staff</option>
                </select>
              </td>
              <td>
                <span class="status" :class="statusBadgeClass(user.is_active)">
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>
                <span class="status" :class="user.is_online ? 'online' : 'offline'">
                  {{ user.is_online ? 'Online' : 'Offline' }}
                </span>
                <div class="sub">{{ relativeSeenLabel(user) }}</div>
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td>
                <div class="actions">
                  <button type="button" @click="toggleUserStatus(user)">
                    {{ user.is_active ? 'Deactivate' : 'Activate' }}
                  </button>
                  <button type="button" @click="openCredentialEditor(user)">Edit Credentials</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </article>

    <article class="panel activity-panel" v-if="activeView === 'activity'">
      <div class="panel-header">
        <h3>Team Activity</h3>
        <button class="refresh-btn" type="button" :disabled="activityLoading" @click="loadActivity">
          {{ activityLoading ? 'Refreshing...' : 'Refresh Log' }}
        </button>
      </div>
      <p class="hint">Review role, status, and credential actions for accountability.</p>
      <p v-if="activityError" class="error">{{ activityError }}</p>

      <div class="activity-list" v-else>
        <article v-if="!activityLoading && activityLogs.length === 0" class="activity-item empty">
          No activity records yet.
        </article>
        <article v-for="log in activityLogs" :key="log.id" class="activity-item">
          <div class="activity-top">
            <div>
              <strong>{{ actorLabel(log) }}</strong>
              <div class="sub">{{ formatDate(log.created_at) }}</div>
            </div>
            <span class="status mono">{{ log.action }}</span>
          </div>
          <p class="sub">Target: <span class="mono">{{ (log.resource_id || '').slice(0, 8) || '—' }}</span></p>
          <ul class="detail-list" v-if="activityDetailEntries(log).length">
            <li v-for="entry in activityDetailEntries(log)" :key="entry[0]">
              <span class="mono">{{ entry[0] }}</span>
              <span>{{ entry[1] }}</span>
            </li>
          </ul>
          <p v-else class="sub">{{ activityDetailsText(log) }}</p>
        </article>
      </div>
    </article>

    <article class="panel tasks-panel" v-if="activeView === 'tasks'">
      <div class="panel-header">
        <div>
          <h3>Tasks & Notes</h3>
          <p class="hint">Keep work clear with simple tasks, plain-language notes, and easy status updates.</p>
        </div>
        <button class="refresh-btn" type="button" :disabled="taskLoading" @click="loadTasks">
          {{ taskLoading ? 'Refreshing...' : 'Refresh List' }}
        </button>
      </div>

      <div class="task-overview" aria-live="polite">
        <article class="task-overview-card">
          <span class="task-overview-label">Needs action</span>
          <strong>{{ pendingTasks.length }}</strong>
        </article>
        <article class="task-overview-card">
          <span class="task-overview-label">Completed</span>
          <strong>{{ completedTasks.length }}</strong>
        </article>
        <article class="task-overview-card">
          <span class="task-overview-label">Total tasks</span>
          <strong>{{ teamTasks.length }}</strong>
        </article>
      </div>

      <div class="tasks-layout">
        <section class="task-form-card">
          <h4>Assign a task</h4>
          <p class="hint">Choose a teammate, add a short task name, then write the note they should follow.</p>
          <div class="create-grid task-form-grid">
            <label>
              <span>Who should do this?</span>
              <select v-model="taskForm.assignee_user_id">
                <option value="">Choose teammate</option>
                <option v-for="user in users" :key="user.id" :value="user.id">
                  {{ user.full_name || user.username }} ({{ user.role }})
                </option>
              </select>
            </label>
            <label>
              <span>Task name</span>
              <input v-model="taskForm.title" type="text" placeholder="e.g. Check this week's supplier delivery" maxlength="120" />
            </label>
            <label class="task-note-field">
              <span>Note for teammate</span>
              <textarea
                v-model="taskForm.note"
                rows="4"
                placeholder="Write the next steps in simple words"
                maxlength="500"
              />
            </label>
          </div>
          <div class="create-actions">
            <button class="primary" type="button" :disabled="taskSaving" @click="assignTask">
              {{ taskSaving ? 'Sending...' : 'Send Task' }}
            </button>
          </div>
          <p v-if="taskError" class="error">{{ taskError }}</p>
        </section>

        <section class="task-groups">
          <article class="task-group">
            <div class="task-group-header">
              <h4>Needs Action</h4>
              <span class="status-count">{{ pendingTasks.length }}</span>
            </div>
            <p v-if="taskLoading" class="hint">Loading tasks...</p>
            <article v-else-if="pendingTasks.length === 0" class="activity-item empty">
              No tasks need action right now.
            </article>
            <article v-for="task in pendingTasks" :key="task.id" class="activity-item task-item">
              <div class="task-item-top">
                <div class="task-main">
                  <strong>{{ task.title }}</strong>
                  <p class="sub task-for">For {{ task.assignee_full_name || task.assignee_username || 'Unknown user' }}</p>
                </div>
                <span class="task-state task-state-open">Needs action</span>
              </div>
              <p class="task-note">{{ task.note }}</p>
              <div class="task-meta">
                <p class="sub">Assigned by {{ task.created_by_full_name || task.created_by_username || 'Unknown' }} • Updated {{ formatDate(task.updated_at) }}</p>
                <button class="task-toggle-btn" type="button" @click="toggleTaskDone(task)">Mark as done</button>
              </div>
            </article>
          </article>

          <article class="task-group">
            <div class="task-group-header">
              <h4>Completed</h4>
              <span class="status-count">{{ completedTasks.length }}</span>
            </div>
            <p v-if="taskLoading" class="hint">Loading tasks...</p>
            <article v-else-if="completedTasks.length === 0" class="activity-item empty">
              No completed tasks yet.
            </article>
            <article v-for="task in completedTasks" :key="task.id" class="activity-item task-item">
              <div class="task-item-top">
                <div class="task-main">
                  <strong>{{ task.title }}</strong>
                  <p class="sub task-for">For {{ task.assignee_full_name || task.assignee_username || 'Unknown user' }}</p>
                </div>
                <span class="task-state task-state-done">Completed</span>
              </div>
              <p class="task-note">{{ task.note }}</p>
              <div class="task-meta">
                <p class="sub">Assigned by {{ task.created_by_full_name || task.created_by_username || 'Unknown' }} • Updated {{ formatDate(task.updated_at) }}</p>
                <button class="task-toggle-btn" type="button" @click="toggleTaskDone(task)">Move back to open</button>
              </div>
            </article>
          </article>
        </section>
      </div>
    </article>
  </section>

  <section v-else class="panel blocked">
    <h2>Access restricted</h2>
    <p>Only admin accounts can manage team and access settings.</p>
  </section>

  <div v-if="selectedCredentialUser" class="modal-backdrop" @click.self="closeCredentialEditor">
    <article class="modal-card">
      <header>
        <h3>Update Credentials</h3>
        <p class="sub">{{ selectedCredentialUser.full_name || selectedCredentialUser.username }}</p>
      </header>

      <label :class="{ invalid: !!credentialsErrors.password }">
        <span>New Password (optional)</span>
        <input v-model="credentialsForm.password" type="password" placeholder="At least 8 characters" />
        <small v-if="credentialsErrors.password" class="field-error">{{ credentialsErrors.password }}</small>
      </label>

      <label :class="{ invalid: !!credentialsErrors.pin }">
        <span>New PIN (optional)</span>
        <input v-model="credentialsForm.pin" type="text" inputmode="numeric" placeholder="4 to 6 digits" />
        <small v-if="credentialsErrors.pin" class="field-error">{{ credentialsErrors.pin }}</small>
      </label>

      <p v-if="credentialsErrors.general" class="error">{{ credentialsErrors.general }}</p>

      <footer class="modal-actions">
        <button type="button" @click="closeCredentialEditor">Cancel</button>
        <button type="button" class="primary" :disabled="credentialsSaving" @click="saveCredentials">
          {{ credentialsSaving ? 'Saving...' : 'Save Changes' }}
        </button>
      </footer>
    </article>
  </div>
</template>

<style scoped>
.team-access {
  display: grid;
  gap: var(--space-4);
}

.panel-surface {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  padding: var(--space-4);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-3);
}

.header h2 { margin: 0; }

.header p {
  margin: 6px 0 0;
  color: var(--text-secondary);
}

.header-controls {
  display: flex;
  align-items: flex-start;
}

.view-switch {
  display: grid;
  gap: 4px;
  min-width: 220px;
}

.view-switch span {
  font-size: 12px;
  color: var(--text-muted);
}

.view-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tab-btn {
  min-height: 40px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  padding: 0 12px;
  cursor: pointer;
}

.tab-btn.active {
  border-color: var(--primary);
  background: var(--primary-bg);
  color: var(--primary);
}

.panel {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  padding: var(--space-4);
  display: grid;
  gap: var(--space-3);
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-3);
}

.panel-header h3 { margin: 0; }
.create-panel h3 { margin: 0; }

.create-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

label { display: grid; gap: 6px; }
label span { font-size: 12px; color: var(--text-muted); }

label.invalid input,
label.invalid select {
  border-color: var(--error);
}

.field-error {
  color: var(--error);
  font-size: 12px;
}

input,
select,
textarea {
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  color: var(--text-primary);
  padding: 0 10px;
  min-height: 40px;
}

textarea {
  padding: 10px;
  resize: vertical;
  line-height: 1.4;
}

.create-actions { display: flex; justify-content: flex-end; }

.primary,
.refresh-btn,
.actions button {
  min-height: 40px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  color: var(--text-primary);
  padding: 0 12px;
  cursor: pointer;
}

.primary {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
}

.filters {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 10px;
}

.error { margin: 0; color: var(--error); }
.table-wrap { overflow: auto; }

.table-wrap table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: 10px; border-bottom: 1px solid var(--border-subtle); vertical-align: middle; }

.sub { font-size: 12px; color: var(--text-muted); margin-top: 3px; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }

.status {
  display: inline-flex;
  border-radius: 999px;
  font-size: 12px;
  padding: 4px 10px;
  border: 1px solid transparent;
}

.status.active { background: var(--success-bg); border-color: var(--success-tint); color: var(--success); }
.status.inactive { background: var(--error-bg); border-color: var(--error-tint); color: var(--error); }
.status.online { background: var(--success-bg); border-color: var(--success-tint); color: var(--success); }
.status.offline { background: var(--bg-muted); border-color: var(--border-default); color: var(--text-secondary); }

.actions { display: flex; flex-wrap: wrap; gap: 8px; }
.empty { color: var(--text-muted); text-align: center; }

.hint {
  margin: 0;
  color: var(--text-muted);
  font-size: 13px;
}

.activity-list {
  display: grid;
  gap: 10px;
}

.activity-item {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  padding: 10px;
  display: grid;
  gap: 6px;
}

.activity-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}

.detail-list {
  margin: 0;
  padding-left: 18px;
  display: grid;
  gap: 3px;
}

.detail-list li {
  display: flex;
  gap: 8px;
  font-size: 12px;
}

.tasks-layout {
  display: grid;
  grid-template-columns: minmax(300px, 360px) minmax(0, 1fr);
  gap: var(--space-4);
  align-items: start;
}

.task-overview {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.task-overview-card {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  padding: 10px 12px;
  display: grid;
  gap: 2px;
}

.task-overview-label {
  font-size: 12px;
  color: var(--text-muted);
}

.task-overview-card strong {
  font-size: 18px;
  line-height: 1.2;
}

.task-form-card {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-3);
}

.task-form-card h4 {
  margin: 0;
  font-size: 15px;
}

.task-form-grid {
  grid-template-columns: minmax(0, 1fr);
}

.task-note-field {
  grid-column: 1 / -1;
}

.task-groups {
  display: grid;
  gap: var(--space-4);
}

.task-group {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  padding: var(--space-4);
  display: grid;
  gap: var(--space-3);
}

.task-group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.task-group-header h4 {
  margin: 0;
  font-size: 15px;
}

.status-count {
  border-radius: 999px;
  background: var(--bg-recessed);
  border: 1px solid var(--border-default);
  font-size: 12px;
  padding: 2px 10px;
  color: var(--text-secondary);
}

.task-item {
  background: var(--bg-card);
  padding: 12px;
  gap: 10px;
}

.task-item-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  flex-wrap: wrap;
}

.task-main {
  min-width: 0;
}

.task-main strong {
  display: block;
}

.task-for {
  margin: 6px 0 0;
}

.task-state {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  border: 1px solid transparent;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 600;
}

.task-state-open {
  background: var(--primary-bg);
  border-color: var(--primary);
  color: var(--primary);
}

.task-state-done {
  background: var(--success-bg);
  border-color: var(--success-tint);
  color: var(--success);
}

.task-note {
  margin: 0;
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  background: var(--bg-recessed);
  border-radius: var(--radius-md);
  padding: 8px 10px;
}

.task-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.task-meta .sub {
  margin: 0;
}

.task-toggle-btn {
  min-height: 40px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  color: var(--text-primary);
  padding: 0 14px;
  cursor: pointer;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(16, 24, 40, 0.48);
  display: grid;
  place-items: center;
  z-index: 40;
  padding: 20px;
}

.modal-card {
  width: min(560px, 100%);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  padding: 18px;
  display: grid;
  gap: 12px;
  box-shadow: var(--shadow-lg);
}

.modal-card h3 {
  margin: 0;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.modal-actions button {
  min-height: 40px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  color: var(--text-primary);
  padding: 0 12px;
  cursor: pointer;
}

.blocked h2 { margin: 0; }
.blocked p { margin: 0; color: var(--text-secondary); }

@media (max-width: 1100px) {
  .tasks-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .filters { grid-template-columns: 1fr; }
  .header { flex-direction: column; align-items: flex-start; }
  .header-controls { width: 100%; }
  .view-switch {
    width: 100%;
    min-width: 0;
  }
  .task-overview { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .task-meta {
    flex-direction: column;
    align-items: stretch;
  }
  .task-toggle-btn {
    width: 100%;
  }
}

@media (max-width: 640px) {
  .task-overview {
    grid-template-columns: 1fr;
  }
}
</style>
