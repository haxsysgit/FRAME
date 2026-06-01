<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useThemeStore } from '../stores/theme'
import { useSettingsStore } from '../stores/settings'
import { useAuthStore } from '../stores/auth'
import { useToast } from '@/composables/useToast'
import { useCurrency } from '@/composables/useCurrency'
import { invoicesService } from '@/services/invoices'
import { productsService } from '@/services/products'
import { usersService } from '@/services/users'
import { printThermalDocument, thermalEscape } from '@/lib/thermalPrint'

const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()
const settingsStore = useSettingsStore()
const authStore = useAuthStore()
const toast = useToast()
const { formatSimple } = useCurrency()

const saving = ref(false)
const lastSavedAt = ref('')
const isAdmin = computed(() => authStore.userRole === 'ADMIN')
const reconciliationStatus = ref(null)
const reconciliationSummary = ref(null)
const statusLoading = ref(false)
const lockActionLoading = ref(false)
const runActionLoading = ref(false)
const grantsLoading = ref(false)
const grantSaving = ref(false)
const stockGrantsLoading = ref(false)
const stockGrantSaving = ref(false)
const teamMembers = ref([])
const afterHoursGrants = ref([])
const stockBypassGrants = ref([])

const grantForm = reactive({
  user_id: '',
  duration_hours: 1,
  note: '',
})

const stockGrantForm = reactive({
  user_id: '',
  duration_minutes: 60,
  note: '',
})

function formatDateTime(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleString([], {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function formatTimeOnly(value) {
  if (!value) return '10:00 PM'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '10:00 PM'
  return date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
}

function formatMoney(value) {
  return formatSimple(value, 0)
}

function printReconciliationSlip(summary, printWindowRef = null) {
  if (!summary) return false

  const generatedAt = formatDateTime(summary.generated_at)
  const cashTotal = Number(summary.cash_total ?? 0)
  const cardTotal = Number(summary.card_total ?? 0)
  const transferTotal = Number(summary.bank_transfer_total ?? 0)
  const paidRevenue = Number(summary.paid_revenue ?? 0)
  const paidCount = Number(summary.paid_invoice_count ?? (
    Number(summary.stamped_count ?? 0) + Number(summary.dispensed_count ?? 0)
  ))
  const printedBy = authStore.user?.full_name || authStore.user?.username || 'Admin'

  const bodyHtml = `
    <section class="center">
      <p class="title">Daily Reconciliation</p>
      <p class="muted">${thermalEscape(settingsStore.settings.pharmacy?.pharmacy_name || 'Pharmax Pharmacy')}</p>
      <p class="muted">Business date: ${thermalEscape(summary.for_date || '—')}</p>
      <p class="muted">Generated: ${thermalEscape(generatedAt)}</p>
      <p class="muted">Printed by: ${thermalEscape(printedBy)}</p>
    </section>

    <div class="divider"></div>

    <div class="line"><span>Cash total</span><span class="mono">${thermalEscape(formatMoney(cashTotal))}</span></div>
    <div class="line"><span>POS/Card total</span><span class="mono">${thermalEscape(formatMoney(cardTotal))}</span></div>
    <div class="line"><span>Transfer total</span><span class="mono">${thermalEscape(formatMoney(transferTotal))}</span></div>
    <div class="line grand"><span>Revenue</span><span class="mono">${thermalEscape(formatMoney(paidRevenue))}</span></div>

    <div class="divider"></div>

    <div class="line"><span>Paid invoices</span><span class="mono">${thermalEscape(paidCount)}</span></div>
    <div class="line"><span>Draft</span><span class="mono">${thermalEscape(summary.draft_count ?? 0)}</span></div>
    <div class="line"><span>Stamped</span><span class="mono">${thermalEscape(summary.stamped_count ?? 0)}</span></div>
    <div class="line"><span>Dispensed</span><span class="mono">${thermalEscape(summary.dispensed_count ?? 0)}</span></div>
    <div class="line"><span>Cancelled</span><span class="mono">${thermalEscape(summary.cancelled_count ?? 0)}</span></div>
  `

  return printThermalDocument({
    title: '',
    bodyHtml,
    printWindow: printWindowRef,
  })
}

function cloneSettings(value) {
  return JSON.parse(JSON.stringify(value || {}))
}

const draft = reactive(cloneSettings(settingsStore.settings))

const sectionOptions = [
  {
    value: 'profile',
    title: 'Profile & Account',
    help: 'Manage account identity details for this device.',
  },
  {
    value: 'pharmacy',
    title: 'Pharmacy Preferences',
    help: 'Control receipts, wording, and print defaults.',
  },
  {
    value: 'workflow',
    title: 'Workflow Defaults',
    help: 'Set queue and payment defaults for faster cashier flow.',
  },
  {
    value: 'accessibility',
    title: 'Accessibility Options',
    help: 'Improve readability and reduce visual strain.',
  },
  {
    value: 'notifications',
    title: 'Priority Notifications',
    help: 'Control which alerts should be treated as high priority popups.',
  },
  {
    value: 'safety',
    title: 'Safety Controls',
    help: 'Reduce accidental actions and improve session safety.',
  },
]

const basicSectionKeys = new Set(['profile', 'notifications', 'accessibility', 'safety'])
const visibleSections = computed(() => {
  if (authStore.userRole === 'ADMIN') return sectionOptions
  return sectionOptions.filter((section) => basicSectionKeys.has(section.value))
})

const currentSection = computed({
  get: () => {
    const section = String(route.params.section || 'profile')
    return visibleSections.value.some((item) => item.value === section)
      ? section
      : visibleSections.value[0]?.value || 'profile'
  },
  set: (next) => {
    if (!next || next === currentSection.value) return
    router.push(`/settings/${next}`)
  },
})

const activeSection = computed(() => (
  visibleSections.value.find((item) => item.value === currentSection.value) || visibleSections.value[0]
))

const fontScaleOptions = [
  { value: 'normal', label: 'Normal text size (recommended)' },
  { value: 'large', label: 'Large text size' },
  { value: 'extra-large', label: 'Extra large text size' },
]

const queueModeOptions = [
  { value: 'ALL', label: 'Show all queue items' },
  { value: 'DRAFT', label: 'Show only pending queue items' },
]

const paymentMethodOptions = [
  { value: 'CASH', label: 'Cash' },
  { value: 'CARD', label: 'POS/Card' },
  { value: 'BANK_TRANSFER', label: 'Bank Transfer' },
]

const stampButtonPreview = computed(() => (
  draft.accessibility.simplified_labels ? 'Stamp Invoice' : 'Finalize Invoice'
))

const lockPreview = computed(() => {
  if (!draft.safety.auto_lock) return 'Auto-lock disabled'
  return `Auto-lock after ${draft.safety.session_timeout_minutes} minute(s) of inactivity`
})

function applyFromStore() {
  const next = cloneSettings(settingsStore.settings)
  Object.assign(draft.profile, next.profile)
  Object.assign(draft.pharmacy, next.pharmacy)
  Object.assign(draft.workflow, next.workflow)
  Object.assign(draft.accessibility, next.accessibility)
  Object.assign(draft.notifications, next.notifications)
  Object.assign(draft.safety, next.safety)
}

function saveSettings() {
  saving.value = true
  try {
    settingsStore.replaceAll(draft)
    lastSavedAt.value = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    toast.success('Settings saved on this device.')
  } finally {
    saving.value = false
  }
}

function resetToDefault() {
  settingsStore.resetDefaults()
  applyFromStore()
  lastSavedAt.value = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  toast.info('Settings reset to recommended defaults.')
}

function discardChanges() {
  applyFromStore()
  toast.info('Unsaved changes were discarded.')
}

function goToSection(section) {
  currentSection.value = section
}

async function loadReconciliationStatus() {
  if (!isAdmin.value) return
  statusLoading.value = true
  try {
    reconciliationStatus.value = await invoicesService.getReconciliationStatus()
  } catch (err) {
    reconciliationStatus.value = null
    toast.error(err?.message || 'Could not load reconciliation status.')
  } finally {
    statusLoading.value = false
  }
}

async function loadAfterHoursGrants() {
  if (!isAdmin.value) return
  grantsLoading.value = true
  try {
    afterHoursGrants.value = await invoicesService.listAfterHoursGrants({ activeOnly: true })
  } catch (err) {
    afterHoursGrants.value = []
    toast.error(err?.message || 'Could not load after-hours permissions.')
  } finally {
    grantsLoading.value = false
  }
}

async function loadStockBypassGrants() {
  if (!isAdmin.value) return
  stockGrantsLoading.value = true
  try {
    stockBypassGrants.value = await productsService.listStockApprovalBypassGrants({ activeOnly: true })
  } catch (err) {
    stockBypassGrants.value = []
    toast.error(err?.message || 'Could not load temporary stock permissions.')
  } finally {
    stockGrantsLoading.value = false
  }
}

async function loadTeamMembers() {
  if (!isAdmin.value) return
  try {
    const users = await usersService.list({ limit: 300 })
    teamMembers.value = users.filter((user) => ['CASHIER', 'STAFF'].includes(String(user.role || '').toUpperCase()))
    if (!grantForm.user_id && teamMembers.value.length > 0) {
      grantForm.user_id = teamMembers.value[0].id
    }
    if (!stockGrantForm.user_id && teamMembers.value.length > 0) {
      stockGrantForm.user_id = teamMembers.value[0].id
    }
  } catch (err) {
    teamMembers.value = []
    toast.error(err?.message || 'Could not load team members.')
  }
}

async function loadAdminSafetyData() {
  await Promise.all([
    loadReconciliationStatus(),
    loadAfterHoursGrants(),
    loadStockBypassGrants(),
    loadTeamMembers(),
  ])
}

async function lockDayNow() {
  lockActionLoading.value = true
  try {
    reconciliationStatus.value = await invoicesService.lockDay()
    toast.success('Sales are now locked for cashier and staff.')
  } catch (err) {
    toast.error(err?.message || 'Could not lock sales for the day.')
  } finally {
    lockActionLoading.value = false
  }
}

async function runReconciliationNow() {
  runActionLoading.value = true
  let printWindowRef = null
  if (typeof window !== 'undefined') {
    printWindowRef = window.open('', '_blank', 'noopener,noreferrer,width=420,height=760')
  }

  try {
    reconciliationSummary.value = await invoicesService.runReconciliation()
    const printed = printReconciliationSlip(reconciliationSummary.value, printWindowRef)
    if (!printed && printWindowRef && !printWindowRef.closed) {
      printWindowRef.close()
    }
    toast.success('Daily reconciliation completed.')
    if (!printed) {
      toast.info('Reconciliation completed. Allow pop-ups to print the summary slip automatically.')
    }
    await loadReconciliationStatus()
  } catch (err) {
    if (printWindowRef && !printWindowRef.closed) {
      printWindowRef.close()
    }
    toast.error(err?.message || 'Could not run daily reconciliation.')
  } finally {
    runActionLoading.value = false
  }
}

async function grantAfterHoursAccess() {
  if (!grantForm.user_id) {
    toast.warning('Choose a staff or cashier account first.')
    return
  }

  grantSaving.value = true
  try {
    await invoicesService.grantAfterHoursAccess({
      userId: grantForm.user_id,
      durationHours: grantForm.duration_hours,
      note: grantForm.note,
    })
    grantForm.note = ''
    toast.success('Temporary after-hours access granted.')
    await Promise.all([loadAfterHoursGrants(), loadReconciliationStatus()])
  } catch (err) {
    toast.error(err?.message || 'Could not grant after-hours access.')
  } finally {
    grantSaving.value = false
  }
}

async function revokeAfterHoursAccess(grant) {
  try {
    await invoicesService.revokeAfterHoursAccess(grant.grant_id)
    toast.info('After-hours access revoked.')
    await Promise.all([loadAfterHoursGrants(), loadReconciliationStatus()])
  } catch (err) {
    toast.error(err?.message || 'Could not revoke access.')
  }
}

async function grantStockApprovalBypass() {
  if (!stockGrantForm.user_id) {
    toast.warning('Choose a staff or cashier account first.')
    return
  }

  stockGrantSaving.value = true
  try {
    await productsService.grantStockApprovalBypass({
      userId: stockGrantForm.user_id,
      durationMinutes: stockGrantForm.duration_minutes,
      note: stockGrantForm.note,
    })
    stockGrantForm.note = ''
    toast.success('Temporary stock auto-approval granted.')
    await loadStockBypassGrants()
  } catch (err) {
    toast.error(err?.message || 'Could not grant temporary stock permission.')
  } finally {
    stockGrantSaving.value = false
  }
}

async function revokeStockApprovalBypass(grant) {
  try {
    await productsService.revokeStockApprovalBypass(grant.grant_id)
    toast.info('Temporary stock permission revoked.')
    await loadStockBypassGrants()
  } catch (err) {
    toast.error(err?.message || 'Could not revoke temporary stock permission.')
  }
}

const lockStatusText = computed(() => {
  if (!reconciliationStatus.value) return 'Status unavailable'
  if (reconciliationStatus.value.is_locked_for_staff) {
    return `Locked for cashier/staff since ${formatTimeOnly(reconciliationStatus.value.lock_start_at)}`
  }
  return `Open until ${formatTimeOnly(reconciliationStatus.value.lock_start_at)}`
})

watch(
  () => currentSection.value,
  (section) => {
    if (section === 'safety' && isAdmin.value) {
      loadAdminSafetyData()
    }
  },
)

onMounted(() => {
  if (isAdmin.value) {
    loadAdminSafetyData()
  }
})
</script>

<template>
  <section class="settings-page">
    <header class="settings-header panel-shell">
      <div>
        <p class="eyebrow">Settings</p>
        <h1>Settings made simple</h1>
        <p class="subtitle">Pick a section, update the fields, then click <strong>Save Settings</strong>.</p>
      </div>
      <div class="header-summary">
        <p class="summary-label">You are editing</p>
        <p class="summary-title">{{ activeSection.title }}</p>
        <p class="summary-help">{{ activeSection.help }}</p>
      </div>
    </header>

    <div class="settings-toolbar panel-shell">
      <label class="picker">
        <span>Settings section</span>
        <select v-model="currentSection">
          <option v-for="section in visibleSections" :key="section.value" :value="section.value">
            {{ section.title }}
          </option>
        </select>
      </label>
      <div class="header-actions">
        <button class="btn btn-ghost" @click="discardChanges">Discard</button>
        <button class="btn btn-danger" @click="resetToDefault">Reset Defaults</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveSettings">
          {{ saving ? 'Saving…' : 'Save Settings' }}
        </button>
      </div>
    </div>

    <p class="saved-note" v-if="lastSavedAt">Last saved at {{ lastSavedAt }}</p>

    <div class="settings-layout">
      <aside class="section-nav-panel">
        <p class="nav-heading">Sections</p>
        <p class="helper">Open one section at a time for focused changes.</p>
        <div class="section-nav-list">
          <button
            v-for="section in visibleSections"
            :key="section.value"
            type="button"
            class="section-nav-btn"
            :class="{ active: currentSection === section.value }"
            @click="goToSection(section.value)"
          >
            <span>{{ section.title }}</span>
            <small>{{ section.help }}</small>
          </button>
        </div>
      </aside>

      <div class="settings-grid">
      <article v-if="currentSection === 'profile'" class="panel">
        <h2>Profile and account</h2>
        <p class="helper">Use this section to show who is currently using this device.</p>

        <label class="field">
          <span>Display Name</span>
          <input v-model="draft.profile.display_name" type="text" placeholder="Example: Main Cashier" />
        </label>

        <label class="field">
          <span>Phone Number</span>
          <input v-model="draft.profile.phone" type="tel" placeholder="Example: +234..." />
        </label>

        <div class="info-box">
          <p><strong>Logged in account:</strong> {{ authStore.user?.username || 'Unknown' }}</p>
          <p>
            Need a password or PIN change? Ask an admin to open Team & Access and use Edit Credentials.
          </p>
        </div>
      </article>

      <article v-if="currentSection === 'pharmacy'" class="panel">
        <h2>Pharmacy preferences</h2>
        <p class="helper">Choose how receipts look and what default wording appears.</p>

        <label class="field">
          <span>Pharmacy Name</span>
          <input v-model="draft.pharmacy.pharmacy_name" type="text" />
        </label>

        <label class="field">
          <span>Receipt Footer Message</span>
          <textarea
            v-model="draft.pharmacy.receipt_footer"
            rows="3"
            placeholder="Thank you for choosing us."
          />
        </label>

        <div class="field-row">
          <label class="field">
            <span>Currency</span>
            <select v-model="draft.pharmacy.currency">
              <option value="NGN">NGN (₦)</option>
              <option value="USD">USD ($)</option>
              <option value="GBP">GBP (£)</option>
            </select>
          </label>

          <label class="field">
            <span>Invoice Paid Label</span>
            <input v-model="draft.pharmacy.invoice_stamp_label" type="text" />
          </label>
        </div>

        <label class="toggle">
          <input v-model="draft.pharmacy.include_tax_in_receipt" type="checkbox" />
          <span>Show tax line on receipts</span>
        </label>

        <label class="toggle">
          <input v-model="draft.pharmacy.print_receipt_after_stamp" type="checkbox" />
          <span>Print receipt automatically after stamping</span>
        </label>
      </article>

      <article v-if="currentSection === 'workflow'" class="panel">
        <h2>Workflow defaults</h2>
        <p class="helper">Set starting values so cashiers can move faster with fewer edits.</p>

        <label class="field">
          <span>Default Payment Method</span>
          <select v-model="draft.workflow.default_payment_method">
            <option v-for="option in paymentMethodOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>

        <label class="field">
          <span>Default Cashier Queue View</span>
          <select v-model="draft.workflow.cashier_queue_mode">
            <option v-for="option in queueModeOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>

        <label class="field">
          <span>Low Stock Alert Threshold</span>
          <input v-model.number="draft.workflow.low_stock_alert_threshold" type="number" min="1" max="500" />
        </label>

        <label class="field">
          <span>Quick Add Search Results Limit</span>
          <input v-model.number="draft.workflow.quick_add_max_results" type="number" min="5" max="25" />
        </label>

        <label class="toggle">
          <input v-model="draft.workflow.invoice_draft_autosave" type="checkbox" />
          <span>Keep invoice drafts after leaving the create page</span>
        </label>
      </article>

      <article v-if="currentSection === 'notifications'" class="panel">
        <h2>Priority notifications</h2>
        <p class="helper">Choose which alerts should pop up right away.</p>

        <label class="toggle">
          <input v-model="draft.notifications.priority_popup_on_login" type="checkbox" />
          <span>Show priority popup at login/session start</span>
        </label>

        <label class="toggle">
          <input v-model="draft.notifications.include_new_user_approvals" type="checkbox" />
          <span>New user approval requests</span>
        </label>

        <label class="toggle">
          <input v-model="draft.notifications.include_out_of_stock" type="checkbox" />
          <span>Out-of-stock inventory alerts</span>
        </label>

        <label class="toggle">
          <input v-model="draft.notifications.include_low_stock" type="checkbox" />
          <span>Low-stock warnings</span>
        </label>

        <label class="toggle">
          <input v-model="draft.notifications.include_invoice_cancellations" type="checkbox" />
          <span>Invoice cancellation alerts</span>
        </label>
      </article>

      <article v-if="currentSection === 'accessibility'" class="panel">
        <h2>Accessibility options</h2>
        <p class="helper">Make text and controls easier to read and use.</p>

        <label class="field">
          <span>Text Size</span>
          <select v-model="draft.accessibility.font_scale">
            <option v-for="option in fontScaleOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>

        <label class="toggle">
          <input v-model="draft.accessibility.high_contrast" type="checkbox" />
          <span>Use high-contrast colors</span>
        </label>

        <label class="toggle">
          <input v-model="draft.accessibility.reduced_motion" type="checkbox" />
          <span>Reduce animations and motion</span>
        </label>

        <label class="toggle">
          <input v-model="draft.accessibility.simplified_labels" type="checkbox" />
          <span>Use simple button wording</span>
        </label>

        <label class="toggle">
          <input v-model="draft.accessibility.large_touch_targets" type="checkbox" />
          <span>Make buttons and fields easier to tap</span>
        </label>

        <label class="toggle">
          <input v-model="draft.accessibility.focus_highlight" type="checkbox" />
          <span>Show a clear highlight on the field you are typing in</span>
        </label>

        <div class="info-box">
          <p><strong>Preview action label:</strong> {{ stampButtonPreview }}</p>
          <button class="btn btn-ghost small" type="button" @click="themeStore.toggleTheme()">
            Preview {{ themeStore.isDark ? 'Light' : 'Dark' }} Theme
          </button>
        </div>
      </article>

      <article v-if="currentSection === 'safety'" class="panel">
        <h2>Safety controls</h2>
        <p class="helper">Protect shared devices and reduce accidental actions.</p>

        <div class="field-row">
          <label class="toggle">
            <input v-model="draft.safety.auto_lock" type="checkbox" />
            <span>Enable auto-lock on inactivity</span>
          </label>

          <label class="field compact">
            <span>Auto-lock after (minutes)</span>
            <input
              v-model.number="draft.safety.session_timeout_minutes"
              type="number"
              min="1"
              max="240"
              :disabled="!draft.safety.auto_lock"
            />
          </label>
        </div>

        <label class="toggle">
          <input v-model="draft.safety.confirm_before_cancel_invoice" type="checkbox" />
          <span>Ask for confirmation before cancelling invoice</span>
        </label>

        <label class="toggle">
          <input v-model="draft.safety.require_dispense_confirmation" type="checkbox" />
          <span>Always ask before marking invoice as dispensed</span>
        </label>

        <p class="lock-preview">{{ lockPreview }}</p>

        <div v-if="isAdmin" class="admin-safety-tools">
          <section class="admin-tool">
            <header>
              <h3>Daily reconciliation</h3>
              <p>Use this if you need to lock sales now or rerun reconciliation.</p>
            </header>

            <div class="status-strip">
              <span>{{ statusLoading ? 'Checking status…' : lockStatusText }}</span>
              <span
                v-if="reconciliationStatus?.reconciliation_needs_rerun"
                class="status-pill warning"
              >
                Reconciliation needed again
              </span>
            </div>

            <div class="tool-actions">
              <button class="btn btn-danger" :disabled="lockActionLoading" @click="lockDayNow">
                {{ lockActionLoading ? 'Locking…' : 'Lock for Today Now' }}
              </button>
              <button class="btn btn-primary" :disabled="runActionLoading" @click="runReconciliationNow">
                {{ runActionLoading ? 'Running…' : 'Run Daily Reconciliation' }}
              </button>
            </div>

            <div v-if="reconciliationSummary" class="info-box">
              <p><strong>Last run:</strong> {{ formatDateTime(reconciliationSummary.generated_at) }}</p>
              <p><strong>Paid revenue:</strong> {{ formatMoney(reconciliationSummary.paid_revenue) }}</p>
              <p><strong>Paid invoices:</strong> {{ reconciliationSummary.paid_invoice_count }}</p>
              <p>
                <strong>Collections:</strong>
                Cash {{ formatMoney(reconciliationSummary.cash_total) }},
                POS {{ formatMoney(reconciliationSummary.card_total) }},
                Transfer {{ formatMoney(reconciliationSummary.bank_transfer_total) }}
              </p>
              <p>
                <strong>Counts:</strong>
                Draft {{ reconciliationSummary.draft_count }},
                Stamped {{ reconciliationSummary.stamped_count }},
                Dispensed {{ reconciliationSummary.dispensed_count }},
                Cancelled {{ reconciliationSummary.cancelled_count }}
              </p>
              <div class="tool-actions" style="margin-top: 8px;">
                <button class="btn btn-ghost" type="button" @click="printReconciliationSlip(reconciliationSummary)">
                  Print Reconciliation Slip
                </button>
              </div>
            </div>
          </section>

          <section class="admin-tool">
            <header>
              <h3>Temporary after-hours access</h3>
              <p>Give one cashier or staff member short-term access after closing.</p>
            </header>

            <div class="field-row">
              <label class="field">
                <span>Team member</span>
                <select v-model="grantForm.user_id">
                  <option value="" disabled>Select account</option>
                  <option v-for="user in teamMembers" :key="user.id" :value="user.id">
                    {{ user.full_name || user.username }} ({{ user.role }})
                  </option>
                </select>
              </label>

              <label class="field compact">
                <span>Access duration (hours)</span>
                <input v-model.number="grantForm.duration_hours" type="number" min="1" max="12" />
              </label>
            </div>

            <label class="field">
              <span>Reason (optional)</span>
              <input v-model="grantForm.note" type="text" placeholder="Example: Late customer pickup approved by admin." />
            </label>

            <div class="tool-actions">
              <button class="btn btn-primary" :disabled="grantSaving" @click="grantAfterHoursAccess">
                {{ grantSaving ? 'Granting…' : 'Grant Temporary Access' }}
              </button>
            </div>

            <div class="grant-list">
              <p v-if="grantsLoading" class="lock-preview">Loading active grants…</p>
              <p v-else-if="afterHoursGrants.length === 0" class="lock-preview">No active after-hours grants.</p>

              <article v-for="grant in afterHoursGrants" :key="grant.grant_id" class="grant-item">
                <div>
                  <strong>{{ grant.full_name || grant.username }}</strong>
                  <p>Expires: {{ formatDateTime(grant.expires_at) }}</p>
                  <p v-if="grant.note">Reason: {{ grant.note }}</p>
                </div>
                <button class="btn btn-ghost" type="button" @click="revokeAfterHoursAccess(grant)">
                  Revoke
                </button>
              </article>
            </div>
          </section>

          <section class="admin-tool">
            <header>
              <h3>Temporary stock auto-approval</h3>
              <p>Allow one cashier or staff member to adjust stock without waiting for admin review.</p>
            </header>

            <div class="field-row">
              <label class="field">
                <span>Team member</span>
                <select v-model="stockGrantForm.user_id">
                  <option value="" disabled>Select account</option>
                  <option v-for="user in teamMembers" :key="user.id" :value="user.id">
                    {{ user.full_name || user.username }} ({{ user.role }})
                  </option>
                </select>
              </label>

              <label class="field compact">
                <span>Access duration (minutes)</span>
                <input v-model.number="stockGrantForm.duration_minutes" type="number" min="5" max="720" />
              </label>
            </div>

            <label class="field">
              <span>Reason (optional)</span>
              <input
                v-model="stockGrantForm.note"
                type="text"
                placeholder="Example: Emergency supplier return stock count."
              />
            </label>

            <div class="tool-actions">
              <button class="btn btn-primary" :disabled="stockGrantSaving" @click="grantStockApprovalBypass">
                {{ stockGrantSaving ? 'Granting…' : 'Grant Temporary Stock Access' }}
              </button>
            </div>

            <div class="grant-list">
              <p v-if="stockGrantsLoading" class="lock-preview">Loading active stock permissions…</p>
              <p v-else-if="stockBypassGrants.length === 0" class="lock-preview">
                No active temporary stock permissions.
              </p>

              <article v-for="grant in stockBypassGrants" :key="grant.grant_id" class="grant-item">
                <div>
                  <strong>{{ grant.full_name || grant.username }}</strong>
                  <p>Expires: {{ formatDateTime(grant.expires_at) }}</p>
                  <p v-if="grant.note">Reason: {{ grant.note }}</p>
                </div>
                <button class="btn btn-ghost" type="button" @click="revokeStockApprovalBypass(grant)">
                  Revoke
                </button>
              </article>
            </div>
          </section>
        </div>
      </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.settings-page {
  display: grid;
  gap: var(--space-4);
}

.panel-shell {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  padding: var(--space-4);
}

.settings-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(240px, 320px);
  gap: var(--space-4);
  align-items: start;
}

.eyebrow {
  margin: 0;
  font-size: 11px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-muted);
}

h1 {
  margin: 4px 0 0;
  font-size: 24px;
}

.subtitle {
  margin: var(--space-2) 0 0;
  color: var(--text-secondary);
  max-width: 640px;
}

.header-summary {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  padding: var(--space-3);
  display: grid;
  gap: 6px;
}

.summary-label {
  margin: 0;
  font-size: 11px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.summary-title {
  margin: 0;
  font-weight: 600;
  color: var(--text-primary);
}

.summary-help {
  margin: 0;
  color: var(--text-secondary);
  font-size: 12px;
  line-height: 1.4;
}

.settings-toolbar {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-end;
  gap: var(--space-3);
}

.header-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: var(--space-2);
}

.picker {
  display: grid;
  gap: 4px;
  min-width: 260px;
}

.picker span {
  font-size: 12px;
  color: var(--text-muted);
}

.picker select {
  height: 36px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  color: var(--text-primary);
  padding: 0 12px;
}

.saved-note {
  margin: 0;
  font-size: 12px;
  color: var(--text-muted);
}

.settings-layout {
  display: grid;
  grid-template-columns: minmax(250px, 300px) minmax(0, 1fr);
  gap: var(--space-3);
  align-items: start;
}

.section-nav-panel {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-2);
}

.nav-heading {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.section-nav-list {
  display: grid;
  gap: 8px;
}

.section-nav-btn {
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  text-align: left;
  padding: 10px 12px;
  cursor: pointer;
  display: grid;
  gap: 4px;
}

.section-nav-btn span {
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 600;
}

.section-nav-btn small {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.35;
}

.section-nav-btn.active {
  border-color: var(--primary);
  background: var(--primary-bg);
}

.section-nav-btn.active span {
  color: var(--primary);
}

.settings-grid {
  display: grid;
  gap: var(--space-3);
  grid-template-columns: minmax(0, 1fr);
  min-width: 0;
}

.panel {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  padding: var(--space-4);
  display: grid;
  gap: var(--space-3);
}

.panel.full-width {
  grid-column: 1 / -1;
}

h2 {
  margin: 0;
  font-size: 16px;
}

.helper {
  margin: 0;
  color: var(--text-secondary);
  font-size: 13px;
}

.field {
  display: grid;
  gap: 6px;
}

.field > span {
  font-size: 12px;
  color: var(--text-muted);
}

.field input,
.field select,
.field textarea {
  width: 100%;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  color: var(--text-primary);
  min-height: 38px;
  padding: 0 12px;
}

.field textarea {
  padding: 10px 12px;
  resize: vertical;
}

.field-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
}

.toggle {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--text-secondary);
}

.toggle input {
  width: 16px;
  height: 16px;
}

.info-box {
  border: 1px dashed var(--border-default);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  background: var(--bg-recessed);
  font-size: 12px;
  color: var(--text-secondary);
  display: grid;
  gap: 8px;
}

.info-box p {
  margin: 0;
}

.lock-preview {
  margin: 0;
  font-size: 12px;
  color: var(--text-muted);
}

.admin-safety-tools {
  display: grid;
  gap: var(--space-3);
}

.admin-tool {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 12px;
  background: var(--bg-recessed);
  display: grid;
  gap: 10px;
}

.admin-tool h3 {
  margin: 0;
  font-size: 14px;
}

.admin-tool header p {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--text-muted);
}

.status-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  flex-wrap: wrap;
  font-size: 12px;
  color: var(--text-secondary);
}

.status-pill {
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 11px;
  border: 1px solid var(--border-default);
}

.status-pill.warning {
  border-color: var(--warning);
  color: var(--warning);
  background: var(--warning-bg);
}

.tool-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.grant-list {
  display: grid;
  gap: 8px;
}

.grant-item {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  padding: 10px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.grant-item p {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--text-secondary);
}

.btn {
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  height: 36px;
  padding: 0 14px;
  cursor: pointer;
}

.btn.small {
  height: 30px;
  font-size: 12px;
}

.btn-primary {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.btn-danger {
  color: var(--error);
  border-color: var(--error);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 1024px) {
  .field-row {
    grid-template-columns: 1fr;
  }

  .settings-header {
    grid-template-columns: 1fr;
  }

  .settings-toolbar {
    align-items: stretch;
  }

  .picker {
    width: 100%;
  }

  .settings-layout {
    grid-template-columns: 1fr;
  }
}
</style>
