<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const isTouchDevice = ref(false)

onMounted(() => {
  isTouchDevice.value = 'ontouchstart' in window || navigator.maxTouchPoints > 0 || window.innerWidth <= 1024
  activeTab.value = isTouchDevice.value ? 'pin' : 'admin'
})

const activeTab = ref('admin')
const identifier = ref('')
const password = ref('')
const showPassword = ref(false)
const rememberDevice = ref(false)
const pin = ref('')
const selectedStaff = ref('')

const staffList = [
  { id: 'cashier@pharmax.local', name: 'Cashier — F. Chidi' },
  { id: 'staff@pharmax.local', name: 'Staff — A. Kalu' },
  { id: 'admin@pharmax.local', name: 'Admin User' },
]

function handlePinKey(digit) {
  if (pin.value.length < 4) {
    pin.value += digit
  }
  if (pin.value.length === 4) {
    submitPin()
  }
}

function handlePinClear() {
  if (pin.value.length > 0) {
    pin.value = pin.value.slice(0, -1)
  }
}

async function submitPin() {
  if (!selectedStaff.value || pin.value.length < 4) return
  const ok = await auth.pinLogin(selectedStaff.value, pin.value)
  if (ok) {
    redirectByRole()
  } else {
    pin.value = ''
  }
}

async function handleAdminLogin() {
  if (!identifier.value || !password.value) return
  const ok = await auth.login(identifier.value, password.value)
  if (ok) {
    redirectByRole()
  }
}

function redirectByRole() {
  const role = auth.userRole
  if (role === 'CASHIER') router.push('/cashier')
  else if (role === 'STAFF') router.push('/invoices')
  else router.push('/dashboard')
}

function handlePinKeyboard(e) {
  if (auth.loading) return
  if (/^[0-9]$/.test(e.key)) {
    handlePinKey(e.key)
  } else if (e.key === 'Backspace') {
    handlePinClear()
  } else if (e.key === 'Enter' && pin.value.length === 4) {
    submitPin()
  }
}

function switchTab(tab) {
  activeTab.value = tab
  auth.error = null
  pin.value = ''
  identifier.value = ''
  password.value = ''
}
</script>

<template>
  <div class="login-page">
    <!-- Top Bar -->
    <header class="top-bar">
      <div class="top-left">
        <span class="logo">PHARMAX</span>
        <span class="divider" />
        <span class="store-name">Pharmax</span>
      </div>
      <div class="top-right">
        <span class="status-dot" />
        <span class="status-txt">System Online</span>
        <span class="secure-badge">
          <span class="material-icons lock-ico">lock</span>
          Secure Sign In
        </span>
      </div>
    </header>

    <!-- Center Area -->
    <section class="center-area">
      <div class="card-header">
        <h1>Welcome Back</h1>
        <p class="subtitle">Sign in to your pharmacy terminal</p>
      </div>

      <div class="login-card">
        <!-- Tab Bar -->
        <div class="tab-bar">
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'admin' }"
            @click="switchTab('admin')"
          >
            <span class="material-icons tab-ico">lock</span>
            Password
          </button>
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'pin' }"
            @click="switchTab('pin')"
          >
            <span class="material-icons tab-ico">dialpad</span>
            Quick PIN
          </button>
        </div>

        <!-- Error Message -->
        <div v-if="auth.error" class="error-msg">
          <span class="material-icons err-ico">error_outline</span>
          {{ auth.error }}
        </div>

        <!-- Staff PIN Tab -->
        <div v-if="activeTab === 'pin'" class="tab-content pin-content" @keydown="handlePinKeyboard" tabindex="0">
          <div class="field-group">
            <label class="field-label">STAFF MEMBER</label>
            <div class="select-wrap">
              <select v-model="selectedStaff" class="staff-select">
                <option value="" disabled>Select staff member</option>
                <option v-for="s in staffList" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
              <span class="material-icons select-chevron">expand_more</span>
            </div>
          </div>

          <label class="field-label">ENTER YOUR PIN</label>
          <p class="pin-hint">Type on keyboard or use the keypad below</p>

          <div class="pin-dots">
            <span v-for="i in 4" :key="i" class="dot" :class="{ filled: pin.length >= i }" />
          </div>

          <div class="keypad">
            <div v-for="row in [[1,2,3],[4,5,6],[7,8,9]]" :key="row[0]" class="key-row">
              <button
                v-for="d in row"
                :key="d"
                class="key-btn"
                :disabled="auth.loading"
                @click="handlePinKey(String(d))"
                tabindex="-1"
              >
                {{ d }}
              </button>
            </div>
            <div class="key-row">
              <button class="key-btn key-clear" :disabled="auth.loading" @click="handlePinClear" tabindex="-1">
                <span class="material-icons">backspace</span>
              </button>
              <button class="key-btn" :disabled="auth.loading" @click="handlePinKey('0')" tabindex="-1">0</button>
              <button class="key-btn key-enter" :disabled="auth.loading || pin.length < 4" @click="submitPin" tabindex="-1">
                <span class="material-icons">arrow_forward</span>
              </button>
            </div>
          </div>

          <button class="forgot-link" type="button">Forgot your PIN?</button>
        </div>

        <!-- Admin Login Tab -->
        <form v-if="activeTab === 'admin'" class="tab-content admin-content" @submit.prevent="handleAdminLogin">
          <div class="field-group">
            <label class="field-label">EMAIL OR USERNAME</label>
            <div class="input-wrap">
              <span class="material-icons input-ico">mail</span>
              <input
                v-model="identifier"
                type="text"
                placeholder="admin@pharmax.local"
                autocomplete="username"
              />
            </div>
          </div>

          <div class="field-group">
            <div class="label-row">
              <label class="field-label">PASSWORD</label>
              <button class="forgot-inline" type="button">Forgot password?</button>
            </div>
            <div class="input-wrap">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Enter password"
                autocomplete="current-password"
              />
              <button class="eye-btn" type="button" @click="showPassword = !showPassword">
                <span class="material-icons">{{ showPassword ? 'visibility' : 'visibility_off' }}</span>
              </button>
            </div>
          </div>

          <button class="sign-in-btn" type="submit" :disabled="auth.loading">
            <span class="material-icons btn-ico">login</span>
            {{ auth.loading ? 'Signing in…' : 'Sign In' }}
          </button>

          <label class="remember-row">
            <input v-model="rememberDevice" type="checkbox" class="checkbox" />
            <span class="remember-txt">Remember this device</span>
          </label>
        </form>
      </div>
    </section>

    <!-- Bottom Bar -->
    <footer class="bottom-bar">
      <div class="bot-left">
        <span class="terminal-info">Terminal 1 · Main Counter</span>
        <span class="divider-sm" />
        <span class="version">v0.1.0</span>
      </div>
      <div class="bot-right">
        <span class="material-icons help-ico">help_outline</span>
        <span class="help-txt">Need help? Contact IT</span>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  padding: 32px 40px;
  background:
    radial-gradient(900px 500px at 80% 10%, #ff5c0010 0%, transparent 60%),
    radial-gradient(700px 400px at 10% 90%, #ffffff06 0%, transparent 60%),
    var(--bg-canvas);
}

/* ---- Top Bar ---- */
.top-bar {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.top-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  font-family: var(--font-data);
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.24em;
  color: var(--accent);
}

.divider {
  width: 1px;
  height: 16px;
  background: var(--border-default);
}

.store-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-tertiary);
}

.top-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--success);
}

.status-txt {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
}

.secure-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
}

.lock-ico {
  font-size: 12px;
}

/* ---- Center Area ---- */
.center-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.card-header {
  text-align: center;
}

h1 {
  margin: 0;
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.subtitle {
  margin: 8px 0 0;
  font-size: 14px;
  color: var(--text-muted);
}

/* ---- Login Card ---- */
.login-card {
  width: 420px;
  border-radius: 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  overflow: hidden;
}

.tab-bar {
  display: flex;
  background: var(--bg-recessed);
  padding: 6px 6px 0;
  gap: 0;
}

.tab-btn {
  flex: 1;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: none;
  background: transparent;
  border-radius: 10px 10px 0 0;
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
  cursor: pointer;
  transition: background 120ms ease, color 120ms ease;
}

.tab-btn:focus,
.tab-btn:focus-visible {
  outline: none;
  box-shadow: none;
}

.tab-btn.active {
  background: var(--bg-card);
  color: var(--text-primary);
  font-weight: 600;
}

.tab-btn.active .tab-ico {
  color: var(--accent);
}

.tab-ico {
  font-size: 16px;
  color: var(--text-muted);
}

.error-msg {
  margin: 16px 20px 0;
  padding: 10px 14px;
  border-radius: 8px;
  background: #ef444418;
  border: 1px solid #ef444440;
  color: var(--error);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.err-ico {
  font-size: 16px;
}

/* ---- Tab Content ---- */
.tab-content {
  padding: 24px 28px;
}

/* ---- Shared Field Styles ---- */
.field-group {
  margin-bottom: 20px;
}

.field-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.label-row .field-label {
  margin-bottom: 0;
}

/* ---- Staff PIN Tab ---- */
.select-wrap {
  position: relative;
}

.staff-select {
  width: 100%;
  height: 48px;
  border-radius: 10px;
  border: 1px solid var(--border-default);
  background: var(--bg-recessed);
  color: var(--text-primary);
  font-family: var(--font-ui);
  font-size: 14px;
  padding: 0 40px 0 16px;
  appearance: none;
  cursor: pointer;
  transition: border-color 120ms ease;
}

.staff-select:focus,
.staff-select:focus-visible {
  outline: none;
  box-shadow: none;
  border-color: var(--accent);
}

.select-chevron {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 18px;
  color: var(--text-muted);
  pointer-events: none;
}

.pin-content:focus {
  outline: none;
}

.pin-hint {
  margin: 2px 0 0;
  font-size: 11px;
  color: var(--text-disabled);
  text-align: center;
}

.pin-dots {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin: 16px 0 20px;
}

.dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid var(--border-default);
  transition: background 100ms ease, border-color 100ms ease;
}

.dot.filled {
  background: var(--accent);
  border-color: var(--accent);
}

.keypad {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.key-row {
  display: flex;
  gap: 8px;
}

.key-btn {
  flex: 1;
  height: 56px;
  border-radius: 10px;
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-primary);
  font-family: var(--font-data);
  font-size: 22px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 80ms ease, transform 80ms ease;
}

.key-btn:focus,
.key-btn:focus-visible {
  outline: none;
  box-shadow: none;
}

.key-btn:active {
  background: var(--border-default);
  transform: scale(0.97);
}

.key-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.key-clear {
  background: var(--bg-recessed);
}

.key-clear .material-icons {
  font-size: 20px;
  color: var(--text-tertiary);
}

.key-enter {
  background: var(--accent);
  border-color: var(--accent);
}

.key-enter .material-icons {
  font-size: 20px;
  color: #fff;
}

.key-enter:disabled {
  opacity: 0.5;
}

.forgot-link {
  display: block;
  width: 100%;
  text-align: center;
  margin-top: 16px;
  background: none;
  border: none;
  color: var(--accent);
  font-family: var(--font-ui);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
}

/* ---- Admin Login Tab ---- */
.input-wrap {
  display: flex;
  align-items: center;
  height: 48px;
  border-radius: 10px;
  border: 1px solid var(--border-default);
  background: var(--bg-recessed);
  padding: 0 16px;
  gap: 10px;
  transition: border-color 120ms ease;
}

.input-wrap:focus-within {
  border-color: var(--accent);
}

.input-ico {
  font-size: 16px;
  color: var(--text-disabled);
}

.input-wrap input {
  flex: 1;
  height: 100%;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-family: var(--font-ui);
  font-size: 14px;
  outline: none;
}

/* Disable global focus-visible outline on wrapped inputs */
.input-wrap input:focus-visible {
  outline: none;
  box-shadow: none;
}

/* Fix browser autofill styling */
.input-wrap input:-webkit-autofill,
.input-wrap input:-webkit-autofill:hover,
.input-wrap input:-webkit-autofill:focus,
.input-wrap input:-webkit-autofill:active {
  -webkit-box-shadow: 0 0 0 30px var(--bg-recessed) inset !important;
  -webkit-text-fill-color: var(--text-primary) !important;
  transition: background-color 5000s ease-in-out 0s;
}

.input-wrap input::placeholder {
  color: var(--text-disabled);
}

.eye-btn {
  background: none;
  border: none;
  padding: 0;
  color: var(--text-disabled);
  cursor: pointer;
  display: flex;
}

.eye-btn:focus,
.eye-btn:focus-visible {
  outline: none;
  box-shadow: none;
}

.eye-btn .material-icons {
  font-size: 18px;
}

.forgot-inline {
  background: none;
  border: none;
  padding: 0;
  font-family: var(--font-ui);
  font-size: 11px;
  font-weight: 500;
  color: var(--accent);
  cursor: pointer;
}

.forgot-inline:focus,
.forgot-inline:focus-visible {
  outline: none;
  box-shadow: none;
}

.sign-in-btn {
  width: 100%;
  height: 48px;
  border-radius: 10px;
  border: none;
  background: var(--accent);
  color: #ffffff;
  font-family: var(--font-ui);
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: opacity 120ms ease;
}

.sign-in-btn:focus,
.sign-in-btn:focus-visible {
  outline: none;
  box-shadow: none;
}

.sign-in-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-ico {
  font-size: 16px;
}

.remember-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
  cursor: pointer;
}

.checkbox {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  accent-color: var(--accent);
}

.remember-txt {
  font-size: 12px;
  color: var(--text-muted);
}

/* ---- Bottom Bar ---- */
.bottom-bar {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bot-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.terminal-info,
.version {
  font-family: var(--font-data);
  font-size: 11px;
  color: var(--text-disabled);
}

.divider-sm {
  width: 1px;
  height: 12px;
  background: var(--border-default);
}

.bot-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.help-ico {
  font-size: 14px;
  color: var(--text-disabled);
}

.help-txt {
  font-size: 11px;
  color: var(--text-disabled);
}

/* ---- Responsive ---- */
@media (max-width: 520px) {
  .login-page {
    padding: 20px 16px;
  }

  .login-card {
    width: 100%;
  }

  .top-bar {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .secure-badge {
    display: none;
  }

  h1 {
    font-size: 24px;
  }

  .key-btn {
    height: 50px;
    font-size: 20px;
  }
}
</style>
