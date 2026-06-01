import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'

const STORAGE_KEY = 'pharmax.theme'

function detectInitialTheme() {
  if (typeof window === 'undefined') {
    return 'light'
  }

  const saved = window.localStorage.getItem(STORAGE_KEY)
  if (saved === 'dark' || saved === 'light') {
    return saved
  }

  // Default to light theme for Green Medical design
  return 'light'
}

export const useThemeStore = defineStore('theme', () => {
  const theme = ref(detectInitialTheme())
  const isDark = computed(() => theme.value === 'dark')

  function applyTheme() {
    if (typeof document === 'undefined') {
      return
    }
    document.documentElement.setAttribute('data-theme', theme.value)
  }

  function setTheme(nextTheme) {
    if (nextTheme !== 'dark' && nextTheme !== 'light') {
      return
    }
    theme.value = nextTheme
  }

  function toggleTheme() {
    theme.value = isDark.value ? 'light' : 'dark'
  }

  watch(
    theme,
    (value) => {
      applyTheme()
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(STORAGE_KEY, value)
      }
    },
    { immediate: true },
  )

  return {
    theme,
    isDark,
    applyTheme,
    setTheme,
    toggleTheme,
  }
})
