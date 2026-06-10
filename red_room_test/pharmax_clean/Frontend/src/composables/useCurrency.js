import { computed } from 'vue'
import { useSettingsStore } from '@/stores/settings'

const CURRENCY_CONFIG = {
  NGN: { symbol: '₦', locale: 'en-NG', code: 'NGN' },
  USD: { symbol: '$', locale: 'en-US', code: 'USD' },
  GBP: { symbol: '£', locale: 'en-GB', code: 'GBP' },
}

export function useCurrency() {
  const settingsStore = useSettingsStore()

  const currencyCode = computed(() => settingsStore.settings.pharmacy?.currency || 'NGN')
  const config = computed(() => CURRENCY_CONFIG[currencyCode.value] || CURRENCY_CONFIG.NGN)
  const symbol = computed(() => config.value.symbol)
  const locale = computed(() => config.value.locale)

  function format(value, options = {}) {
    const n = Number(value)
    if (!Number.isFinite(n)) return `${symbol.value}0`

    const { decimals = 2, compact = false } = options

    if (compact) {
      if (n >= 1_000_000) return `${symbol.value}${(n / 1_000_000).toFixed(1)}M`
      if (n >= 1_000) return `${symbol.value}${(n / 1_000).toFixed(1)}K`
    }

    return n.toLocaleString(locale.value, {
      style: 'currency',
      currency: currencyCode.value,
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    })
  }

  function formatCompact(value) {
    return format(value, { compact: true, decimals: 0 })
  }

  function formatSimple(value, decimals = 2) {
    const n = Number(value)
    if (!Number.isFinite(n)) return `${symbol.value}0`
    return `${symbol.value}${n.toLocaleString(locale.value, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}`
  }

  return {
    currencyCode,
    symbol,
    locale,
    format,
    formatCompact,
    formatSimple,
  }
}
