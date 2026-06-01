import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'

const STORAGE_KEY = 'pharmax.settings.v1'

const DEFAULT_SETTINGS = {
  profile: {
    display_name: '',
    phone: '',
  },
  pharmacy: {
    pharmacy_name: 'Pharmax Pharmacy',
    receipt_footer: 'Thank you for choosing us. Get well soon.',
    currency: 'NGN',
    include_tax_in_receipt: false,
    invoice_stamp_label: 'STAMPED',
    print_receipt_after_stamp: false,
  },
  workflow: {
    default_payment_method: 'CASH',
    cashier_queue_mode: 'DRAFT',
    low_stock_alert_threshold: 10,
    invoice_draft_autosave: true,
    quick_add_max_results: 10,
  },
  accessibility: {
    font_scale: 'normal',
    high_contrast: false,
    reduced_motion: false,
    simplified_labels: true,
    large_touch_targets: false,
    focus_highlight: true,
  },
  safety: {
    auto_lock: true,
    session_timeout_minutes: 20,
    confirm_before_cancel_invoice: true,
    require_dispense_confirmation: true,
  },
  notifications: {
    priority_popup_on_login: true,
    include_out_of_stock: true,
    include_low_stock: true,
    include_invoice_cancellations: true,
    include_new_user_approvals: true,
  },
}

function clone(value) {
  return JSON.parse(JSON.stringify(value))
}

function normalizeSettings(raw) {
  const settings = {
    profile: { ...DEFAULT_SETTINGS.profile, ...(raw?.profile || {}) },
    pharmacy: { ...DEFAULT_SETTINGS.pharmacy, ...(raw?.pharmacy || {}) },
    workflow: { ...DEFAULT_SETTINGS.workflow, ...(raw?.workflow || {}) },
    accessibility: { ...DEFAULT_SETTINGS.accessibility, ...(raw?.accessibility || {}) },
    safety: { ...DEFAULT_SETTINGS.safety, ...(raw?.safety || {}) },
    notifications: { ...DEFAULT_SETTINGS.notifications, ...(raw?.notifications || {}) },
  }

  if (!['NGN', 'USD', 'GBP'].includes(settings.pharmacy.currency)) {
    settings.pharmacy.currency = DEFAULT_SETTINGS.pharmacy.currency
  }

  if (!['CASH', 'CARD', 'BANK_TRANSFER'].includes(settings.workflow.default_payment_method)) {
    settings.workflow.default_payment_method = DEFAULT_SETTINGS.workflow.default_payment_method
  }

  if (!['ALL', 'DRAFT'].includes(settings.workflow.cashier_queue_mode)) {
    settings.workflow.cashier_queue_mode = DEFAULT_SETTINGS.workflow.cashier_queue_mode
  }

  const quickAddMaxResults = Number(settings.workflow.quick_add_max_results)
  settings.workflow.quick_add_max_results = Number.isFinite(quickAddMaxResults)
    ? Math.min(25, Math.max(5, Math.round(quickAddMaxResults)))
    : DEFAULT_SETTINGS.workflow.quick_add_max_results

  settings.workflow.invoice_draft_autosave = Boolean(settings.workflow.invoice_draft_autosave)

  const lowStock = Number(settings.workflow.low_stock_alert_threshold)
  settings.workflow.low_stock_alert_threshold = Number.isFinite(lowStock)
    ? Math.min(500, Math.max(1, Math.round(lowStock)))
    : DEFAULT_SETTINGS.workflow.low_stock_alert_threshold

  if (!['normal', 'large', 'extra-large'].includes(settings.accessibility.font_scale)) {
    settings.accessibility.font_scale = DEFAULT_SETTINGS.accessibility.font_scale
  }

  settings.accessibility.large_touch_targets = Boolean(settings.accessibility.large_touch_targets)
  settings.accessibility.focus_highlight = Boolean(settings.accessibility.focus_highlight)

  const timeout = Number(settings.safety.session_timeout_minutes)
  settings.safety.session_timeout_minutes = Number.isFinite(timeout)
    ? Math.min(240, Math.max(1, Math.round(timeout)))
    : DEFAULT_SETTINGS.safety.session_timeout_minutes
  settings.safety.require_dispense_confirmation = Boolean(settings.safety.require_dispense_confirmation)

  settings.notifications.priority_popup_on_login = Boolean(settings.notifications.priority_popup_on_login)
  settings.notifications.include_out_of_stock = Boolean(settings.notifications.include_out_of_stock)
  settings.notifications.include_low_stock = Boolean(settings.notifications.include_low_stock)
  settings.notifications.include_invoice_cancellations = Boolean(settings.notifications.include_invoice_cancellations)
  settings.notifications.include_new_user_approvals = Boolean(settings.notifications.include_new_user_approvals)

  return settings
}

function loadSettings() {
  if (typeof window === 'undefined') return clone(DEFAULT_SETTINGS)

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return clone(DEFAULT_SETTINGS)
    return normalizeSettings(JSON.parse(raw))
  } catch {
    return clone(DEFAULT_SETTINGS)
  }
}

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref(loadSettings())

  function applyAccessibility() {
    if (typeof document === 'undefined') return

    const root = document.documentElement
    root.setAttribute('data-font-scale', settings.value.accessibility.font_scale)
    root.setAttribute('data-contrast', settings.value.accessibility.high_contrast ? 'high' : 'normal')
    root.setAttribute('data-motion', settings.value.accessibility.reduced_motion ? 'reduce' : 'normal')
    root.setAttribute('data-touch-targets', settings.value.accessibility.large_touch_targets ? 'large' : 'normal')
    root.setAttribute('data-focus-highlight', settings.value.accessibility.focus_highlight ? 'on' : 'off')
  }

  function replaceAll(next) {
    settings.value = normalizeSettings(next)
  }

  function updateSection(section, patch) {
    settings.value = normalizeSettings({
      ...settings.value,
      [section]: {
        ...(settings.value[section] || {}),
        ...(patch || {}),
      },
    })
  }

  function resetDefaults() {
    settings.value = clone(DEFAULT_SETTINGS)
  }

  watch(
    settings,
    (value) => {
      applyAccessibility()
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(value))
      }
    },
    { deep: true, immediate: true },
  )

  const defaultPaymentMethod = computed(() => settings.value.workflow.default_payment_method)
  const cashierQueueMode = computed(() => settings.value.workflow.cashier_queue_mode)
  const shouldAutoPrintAfterStamp = computed(() => settings.value.pharmacy.print_receipt_after_stamp)

  return {
    settings,
    defaultPaymentMethod,
    cashierQueueMode,
    shouldAutoPrintAfterStamp,
    applyAccessibility,
    replaceAll,
    updateSection,
    resetDefaults,
    defaultSettings: clone(DEFAULT_SETTINGS),
  }
})
