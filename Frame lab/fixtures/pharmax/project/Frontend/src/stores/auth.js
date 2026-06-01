import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { api } from '../services/api'

const TOKEN_KEY = 'pharmax.token'
const PRESENCE_HEARTBEAT_MS = 60_000

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || null)
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || null)
  let heartbeatTimer = null

  const userInitials = computed(() => {
    if (!user.value) return '??'
    if (user.value.full_name) {
      return user.value.full_name
        .split(' ')
        .map((w) => w[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    }
    return user.value.username.slice(0, 2).toUpperCase()
  })

  function stopPresenceHeartbeat() {
    if (heartbeatTimer) {
      window.clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  async function sendPresenceHeartbeat() {
    if (!token.value) return
    try {
      await api.post('/auth/presence/heartbeat', {}, { silent: true })
    } catch (_) {
      // best-effort keepalive
    }
  }

  function startPresenceHeartbeat() {
    if (!token.value) return
    stopPresenceHeartbeat()
    sendPresenceHeartbeat()
    heartbeatTimer = window.setInterval(sendPresenceHeartbeat, PRESENCE_HEARTBEAT_MS)
  }

  function setToken(newToken) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem(TOKEN_KEY, newToken)
    } else {
      localStorage.removeItem(TOKEN_KEY)
    }
  }

  async function login(identifier, password) {
    loading.value = true
    error.value = null
    try {
      const data = await api.post('/auth/login', { identifier, password })
      setToken(data.access_token)
      const profile = await fetchUser()
      if (!profile) {
        setToken(null)
        user.value = null
        error.value = 'Signed in, but profile could not be loaded. Please try again.'
        return false
      }
      return true
    } catch (err) {
      error.value = err.message || 'Login failed'
      setToken(null)
      user.value = null
      return false
    } finally {
      loading.value = false
    }
  }

  async function register(payload) {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/auth/register', payload)
      return response
    } catch (err) {
      error.value = err.message || 'Registration failed'
      return null
    } finally {
      loading.value = false
    }
  }

  async function pinLogin(identifier, pin) {
    loading.value = true
    error.value = null
    try {
      const data = await api.post('/auth/pin-login', { identifier, pin })
      setToken(data.access_token)
      const profile = await fetchUser()
      if (!profile) {
        setToken(null)
        user.value = null
        error.value = 'Signed in, but profile could not be loaded. Please try again.'
        return false
      }
      return true
    } catch (err) {
      error.value = err.message || 'Invalid PIN'
      setToken(null)
      user.value = null
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    if (!token.value) return null
    try {
      user.value = await api.get('/auth/me')
      startPresenceHeartbeat()
      return user.value
    } catch (_) {
      stopPresenceHeartbeat()
      setToken(null)
      user.value = null
      return null
    }
  }

  async function logout() {
    stopPresenceHeartbeat()
    if (token.value) {
      try {
        await api.post('/auth/logout', {}, { silent: true })
      } catch (_) {
        // best-effort logout marker
      }
    }
    setToken(null)
    user.value = null
  }

  return {
    token,
    user,
    loading,
    error,
    isAuthenticated,
    userRole,
    userInitials,
    login,
    register,
    pinLogin,
    fetchUser,
    logout,
    sendPresenceHeartbeat,
  }
})
