<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useToast } from '../composables/useToast'

const router = useRouter()
const auth = useAuthStore()
const toast = useToast()

// View state: 'landing', 'login', 'register', 'pin'
const currentView = ref('landing')

// Login form
const loginEmail = ref('')
const loginPassword = ref('')
const showLoginPassword = ref(false)

// Register form
const regFullName = ref('')
const regEmail = ref('')
const regUsername = ref('')
const regRole = ref('STAFF')
const regPassword = ref('')
const regConfirmPassword = ref('')
const showRegPassword = ref(false)
const loginTouched = ref(false)
const registerTouched = ref(false)

// PIN login
const selectedStaff = ref('')
const pin = ref('')
const staffList = [
  { id: 'cashier@pharmax.local', name: 'Cashier', role: 'CASHIER' },
  { id: 'staff@pharmax.local', name: 'Staff', role: 'STAFF' },
  { id: 'admin@pharmax.local', name: 'Admin', role: 'ADMIN' },
]

const loginIdentifierError = computed(() => {
  if (!loginTouched.value) return ''
  if (!loginEmail.value.trim()) return 'Enter your email or username.'
  return ''
})

const loginPasswordError = computed(() => {
  if (!loginTouched.value) return ''
  if (!loginPassword.value) return 'Enter your password.'
  if (loginPassword.value.length < 8) return 'Password must be at least 8 characters.'
  return ''
})

const registerEmailError = computed(() => {
  if (!registerTouched.value) return ''
  if (!regEmail.value.trim()) return 'Email is required.'
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(regEmail.value.trim())) return 'Enter a valid email address.'
  return ''
})

const registerUsernameError = computed(() => {
  if (!registerTouched.value) return ''
  if (!regUsername.value.trim()) return 'Username is required.'
  if (regUsername.value.trim().length < 3) return 'Username must be at least 3 characters.'
  return ''
})

const passwordChecks = computed(() => [
  {
    key: 'length',
    label: 'At least 8 characters',
    passed: regPassword.value.length >= 8,
  },
  {
    key: 'upper',
    label: 'At least 1 uppercase letter',
    passed: /[A-Z]/.test(regPassword.value),
  },
  {
    key: 'lower',
    label: 'At least 1 lowercase letter',
    passed: /[a-z]/.test(regPassword.value),
  },
  {
    key: 'digit',
    label: 'At least 1 number',
    passed: /\d/.test(regPassword.value),
  },
])

const isPasswordValid = computed(() => passwordChecks.value.every((rule) => rule.passed))

const registerPasswordError = computed(() => {
  if (!registerTouched.value) return ''
  if (!regPassword.value) return 'Password is required.'
  if (!isPasswordValid.value) return 'Password does not meet the minimum requirements.'
  return ''
})

const registerConfirmError = computed(() => {
  if (!registerTouched.value && !regConfirmPassword.value) return ''
  if (!regConfirmPassword.value) return 'Confirm your password.'
  if (regPassword.value !== regConfirmPassword.value) return 'Passwords do not match.'
  return ''
})

const showPasswordChecklist = computed(() => registerTouched.value || regPassword.value.length > 0)

const canSubmitLogin = computed(() => loginEmail.value.trim().length > 0 && loginPassword.value.length >= 8)
const canSubmitRegister = computed(() => {
  return (
    !!regEmail.value.trim()
    && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(regEmail.value.trim())
    && regUsername.value.trim().length >= 3
    && isPasswordValid.value
    && !!regConfirmPassword.value
    && regPassword.value === regConfirmPassword.value
  )
})

// Handlers
async function handleLogin() {
  loginTouched.value = true
  if (!canSubmitLogin.value) {
    auth.error = loginIdentifierError.value || loginPasswordError.value
    return
  }
  const ok = await auth.login(loginEmail.value, loginPassword.value)
  if (ok) redirectByRole()
}

async function handleRegister() {
  registerTouched.value = true

  if (!canSubmitRegister.value) {
    auth.error =
      registerEmailError.value
      || registerUsernameError.value
      || registerPasswordError.value
      || registerConfirmError.value
    return
  }

  const response = await auth.register({
    full_name: regFullName.value || null,
    email: regEmail.value,
    username: regUsername.value,
    password: regPassword.value,
    role: regRole.value,
  })

  if (!response) return

  toast.success(response.message || 'Request sent to admin. Your account will be activated after approval.')
  currentView.value = 'login'
  clearRegisterForm()
}

function clearRegisterForm() {
  regFullName.value = ''
  regEmail.value = ''
  regUsername.value = ''
  regRole.value = 'STAFF'
  regPassword.value = ''
  regConfirmPassword.value = ''
  registerTouched.value = false
}

function handlePinKey(digit) {
  if (pin.value.length < 4) pin.value += digit
  if (pin.value.length === 4) submitPin()
}

function handlePinClear() {
  if (pin.value.length > 0) pin.value = pin.value.slice(0, -1)
}

async function submitPin() {
  if (!selectedStaff.value || pin.value.length < 4) return
  const ok = await auth.pinLogin(selectedStaff.value, pin.value)
  if (ok) redirectByRole()
  else pin.value = ''
}

function redirectByRole() {
  const role = auth.userRole
  if (role === 'CASHIER') router.push('/cashier')
  else if (role === 'STAFF') router.push('/invoices/create')
  else router.push('/dashboard')
}

function switchView(view) {
  currentView.value = view
  auth.error = null
  loginTouched.value = false
  registerTouched.value = false
  pin.value = ''
}
</script>

<template>
  <div class="auth-page">
    <!-- Landing View - Full Screen Split -->
    <div v-if="currentView === 'landing'" class="landing-split">
      <!-- Left Side - Branding -->
      <div class="landing-brand">
        <div class="brand-content">
          <div class="landing-logo">
            <span class="material-icons">local_pharmacy</span>
          </div>
          <h1 class="landing-title">Pharmax</h1>
          <p class="landing-tagline">Pharmacy Management System</p>
          
          <div class="feature-list">
            <div class="feature-item">
              <span class="material-icons">inventory_2</span>
              <span>Inventory Management</span>
            </div>
            <div class="feature-item">
              <span class="material-icons">point_of_sale</span>
              <span>Sales & Invoicing</span>
            </div>
            <div class="feature-item">
              <span class="material-icons">analytics</span>
              <span>Reports & Analytics</span>
            </div>
            <div class="feature-item">
              <span class="material-icons">groups</span>
              <span>Multi-User Access</span>
            </div>
          </div>

        </div>
      </div>

      <!-- Right Side - Form -->
      <div class="landing-form-side">
        <div class="form-container">
          <h2>Welcome Back</h2>
          <p class="form-subtitle">Access your pharmacy management system</p>

          <div class="landing-buttons">
            <button class="landing-btn primary" @click="switchView('login')">
              <span class="material-icons">login</span>
              Sign In with Email
            </button>
            
            <div class="divider">
              <span>or</span>
            </div>
            
            <button class="landing-btn ghost" @click="switchView('pin')">
              <span class="material-icons">dialpad</span>
              Quick PIN Login
            </button>
          </div>

          <p class="register-hint">
            New users can request access. Admin approval is required before first login.
          </p>
        </div>
      </div>

      <!-- Footer -->
      <footer class="landing-footer-bar">
        <div class="footer-content">
          <div class="footer-block footer-brand">
            <div class="footer-brand-head">
              <h4>Pharmax</h4>
              <span class="footer-chip">Internal Ops</span>
            </div>
            <p class="footer-copy">Internal pharmacy operations suite.</p>
            <p class="footer-meta">© 2026 Pharmax. Internal Use Only.</p>
          </div>
          <div class="footer-block footer-support">
            <h4>Support</h4>
            <p class="footer-label">Direct channels</p>
            <a href="mailto:pentacker@gmail.com" class="footer-link">
              <span class="material-icons">email</span>
              pentacker@gmail.com
            </a>
            <a href="https://www.linkedin.com/in/arinze-elenasulu-b011a1249" target="_blank" rel="noreferrer" class="footer-link">
              <span class="material-icons">link</span>
              LinkedIn
            </a>
          </div>

          <div class="footer-block footer-access">
            <h4>Access</h4>
            <ul class="footer-list">
              <li><span class="material-icons">check_circle</span>Admin, Cashier, and Staff portals</li>
              <li><span class="material-icons">lock</span>Private deployment</li>
            </ul>
          </div>
        </div>
      </footer>
    </div>

    <!-- Auth Card (Login/Register/PIN) -->
    <div v-else class="auth-card">
      <!-- Back to Landing -->
      <button v-if="currentView !== 'pin'" class="back-link" @click="switchView('landing')">
        <span class="material-icons">arrow_back</span>
        Back
      </button>

      <!-- Logo & Title -->
      <div class="auth-header">
        <div class="logo">
          <span class="material-icons">local_pharmacy</span>
        </div>
        <h1>Pharmax</h1>
        <p class="subtitle">Pharmacy Management System</p>
      </div>

      <!-- Tab Navigation -->
      <div class="auth-tabs" v-if="currentView !== 'pin'">
        <button 
          :class="['tab', { active: currentView === 'login' }]" 
          @click="switchView('login')"
        >
          Sign In
        </button>
        <button 
          :class="['tab', { active: currentView === 'register' }]" 
          @click="switchView('register')"
        >
          Register
        </button>
      </div>

      <!-- Error Alert -->
      <div v-if="auth.error" class="error-alert">
        <span class="material-icons">error</span>
        {{ auth.error }}
      </div>

      <!-- Login Form -->
      <form v-if="currentView === 'login'" class="auth-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Email or Username</label>
          <div class="input-wrapper" :class="{ invalid: !!loginIdentifierError }">
            <span class="material-icons">person</span>
            <input 
              v-model="loginEmail" 
              type="text" 
              placeholder="Enter email or username"
              autocomplete="username"
            />
          </div>
          <p v-if="loginIdentifierError" class="field-error">{{ loginIdentifierError }}</p>
        </div>

        <div class="form-group">
          <label>Password</label>
          <div class="input-wrapper" :class="{ invalid: !!loginPasswordError }">
            <span class="material-icons">lock</span>
            <input 
              v-model="loginPassword" 
              :type="showLoginPassword ? 'text' : 'password'" 
              placeholder="Enter password"
              autocomplete="current-password"
            />
            <button type="button" class="toggle-btn" @click="showLoginPassword = !showLoginPassword">
              <span class="material-icons">{{ showLoginPassword ? 'visibility_off' : 'visibility' }}</span>
            </button>
          </div>
          <p v-if="loginPasswordError" class="field-error">{{ loginPasswordError }}</p>
        </div>

        <button type="submit" class="submit-btn" :disabled="auth.loading || !canSubmitLogin">
          {{ auth.loading ? 'Signing in...' : 'Sign In' }}
        </button>

        <div class="divider">
          <span>or</span>
        </div>

        <button type="button" class="pin-btn" @click="switchView('pin')">
          <span class="material-icons">dialpad</span>
          Sign in with PIN
        </button>
      </form>

      <!-- Register Form -->
      <form v-else-if="currentView === 'register'" class="auth-form" @submit.prevent="handleRegister">
        <div class="form-group">
          <label>Full Name</label>
          <div class="input-wrapper">
            <span class="material-icons">badge</span>
            <input 
              v-model="regFullName" 
              type="text" 
              placeholder="Enter your full name"
              autocomplete="off"
            />
          </div>
        </div>

        <div class="form-group">
          <label>Email</label>
          <div class="input-wrapper" :class="{ invalid: !!registerEmailError }">
            <span class="material-icons">email</span>
            <input 
              v-model="regEmail" 
              type="email" 
              placeholder="Enter your email"
              autocomplete="off"
            />
          </div>
          <p v-if="registerEmailError" class="field-error">{{ registerEmailError }}</p>
        </div>

        <div class="form-group">
          <label>Username</label>
          <div class="input-wrapper" :class="{ invalid: !!registerUsernameError }">
            <span class="material-icons">person</span>
            <input 
              v-model="regUsername" 
              type="text" 
              placeholder="Choose a username"
              autocomplete="off"
            />
          </div>
          <p v-if="registerUsernameError" class="field-error">{{ registerUsernameError }}</p>
        </div>

        <div class="form-group">
          <label>Role</label>
          <div class="input-wrapper select-wrapper">
            <span class="material-icons">badge</span>
            <select v-model="regRole">
              <option value="STAFF">Staff</option>
              <option value="CASHIER">Cashier</option>
            </select>
            <span class="material-icons chevron">expand_more</span>
          </div>
        </div>

        <div class="form-group">
          <label>Password</label>
          <div class="input-wrapper" :class="{ invalid: !!registerPasswordError }">
            <span class="material-icons">lock</span>
            <input 
              v-model="regPassword" 
              :type="showRegPassword ? 'text' : 'password'" 
              placeholder="Create password"
              autocomplete="new-password"
            />
            <button type="button" class="toggle-btn" @click="showRegPassword = !showRegPassword">
              <span class="material-icons">{{ showRegPassword ? 'visibility_off' : 'visibility' }}</span>
            </button>
          </div>
          <p v-if="registerPasswordError" class="field-error">{{ registerPasswordError }}</p>

          <ul v-if="showPasswordChecklist" class="password-rules">
            <li
              v-for="rule in passwordChecks"
              :key="rule.key"
              :class="{ passed: rule.passed }"
            >
              <span class="material-icons">{{ rule.passed ? 'check_circle' : 'radio_button_unchecked' }}</span>
              <span>{{ rule.label }}</span>
            </li>
          </ul>
        </div>

        <div class="form-group">
          <label>Confirm Password</label>
          <div class="input-wrapper" :class="{ invalid: !!registerConfirmError }">
            <span class="material-icons">lock</span>
            <input 
              v-model="regConfirmPassword" 
              type="password" 
              placeholder="Confirm password"
              autocomplete="new-password"
            />
          </div>
          <p v-if="registerConfirmError" class="field-error">{{ registerConfirmError }}</p>
        </div>

        <button type="submit" class="submit-btn" :disabled="auth.loading || !canSubmitRegister">
          {{ auth.loading ? 'Sending...' : 'Send Approval Request' }}
        </button>
      </form>

      <!-- PIN Login -->
      <div v-else-if="currentView === 'pin'" class="pin-view">
        <button class="back-link" @click="switchView('login')">
          <span class="material-icons">arrow_back</span>
          Back to login
        </button>

        <div class="form-group">
          <label>Select User</label>
          <div class="input-wrapper select-wrapper">
            <span class="material-icons">person</span>
            <select v-model="selectedStaff">
              <option value="" disabled>Choose your account</option>
              <option v-for="s in staffList" :key="s.id" :value="s.id">
                {{ s.name }} ({{ s.role }})
              </option>
            </select>
            <span class="material-icons chevron">expand_more</span>
          </div>
        </div>

        <div class="pin-section">
          <label>Enter PIN</label>
          <div class="pin-dots">
            <span v-for="i in 4" :key="i" :class="['dot', { filled: pin.length >= i }]"></span>
          </div>

          <div class="keypad">
            <button v-for="n in [1,2,3,4,5,6,7,8,9]" :key="n" type="button" class="key" @click="handlePinKey(String(n))">
              {{ n }}
            </button>
            <button type="button" class="key key-fn" @click="handlePinClear">
              <span class="material-icons">backspace</span>
            </button>
            <button type="button" class="key" @click="handlePinKey('0')">0</button>
            <button type="button" class="key key-fn key-enter" :disabled="pin.length < 4" @click="submitPin">
              <span class="material-icons">check</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(1100px circle at 8% -10%, rgba(15, 159, 137, 0.32), transparent 48%),
    radial-gradient(900px circle at 100% -20%, rgba(37, 99, 235, 0.2), transparent 46%),
    var(--bg-canvas);
  padding: 20px;
}

/* Landing View - Full Screen Split */
.landing-split {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: minmax(0, 1fr) auto;
}

.landing-brand {
  grid-column: 1;
  grid-row: 1;
  background: linear-gradient(145deg, #0c8f7b 0%, #0a7665 52%, #0b5f53 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
  overflow: hidden;
}

.landing-brand::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.16) 0%, transparent 62%);
  animation: pulse 15s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.3; }
}

.brand-content {
  text-align: center;
  position: relative;
  z-index: 1;
}

.landing-logo {
  width: 100px;
  height: 100px;
  margin: 0 auto 24px;
  background: rgba(255, 255, 255, 0.18);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.38);
  box-shadow: 0 18px 30px rgba(3, 30, 25, 0.25);
}

.landing-logo .material-icons {
  font-size: 48px;
  color: white;
}

.landing-title {
  font-size: 48px;
  font-weight: 800;
  color: white;
  margin: 0 0 8px;
  letter-spacing: -1.2px;
  text-shadow: 0 10px 22px rgba(0, 0, 0, 0.18);
}

.landing-tagline {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.85);
  margin: 0 0 48px;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  text-align: left;
  max-width: 280px;
  margin: 0 auto;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 14px;
  color: rgba(255, 255, 255, 0.95);
  font-size: 15px;
  font-weight: 500;
}

.feature-item .material-icons {
  font-size: 24px;
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.18);
  padding: 8px;
  border-radius: 10px;
}

/* Right Side - Form */
.landing-form-side {
  grid-column: 2;
  grid-row: 1;
  background:
    radial-gradient(600px circle at 100% 0%, rgba(15, 159, 137, 0.1), transparent 42%),
    var(--bg-canvas);
  display: flex;
  flex-direction: column;
  position: relative;
}

.form-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 100%;
  max-width: 420px;
  padding: 40px;
  margin: 0 auto;
}

.form-container h2 {
  font-size: 34px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px;
}

.form-subtitle {
  font-size: 15px;
  color: var(--text-secondary);
  margin: 0 0 40px;
}

.landing-buttons {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.landing-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px 24px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.landing-btn .material-icons {
  font-size: 20px;
}

.landing-btn.primary {
  background: var(--primary);
  color: white;
  box-shadow: var(--shadow-sm);
}

.landing-btn.primary:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.landing-btn.secondary {
  background: var(--bg-card);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
}

.landing-btn.secondary:hover {
  background: var(--bg-hover);
  border-color: var(--primary);
}

.landing-btn.ghost {
  background: transparent;
  color: var(--text-secondary);
  padding: 12px 24px;
}

.landing-btn.ghost:hover {
  color: var(--primary);
  background: var(--primary-tint);
}

.register-hint {
  margin-top: 24px;
  font-size: 13px;
  color: var(--text-tertiary);
  text-align: center;
}

/* Footer */
.landing-footer-bar {
  grid-column: 1 / -1;
  grid-row: 2;
  width: 100%;
  background: linear-gradient(180deg, #0a1714 0%, #07110f 100%);
  color: rgba(255, 255, 255, 0.78);
  padding: 24px 48px;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
}

.footer-content {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr;
  align-items: start;
  width: 100%;
  max-width: 1240px;
  margin: 0 auto;
  gap: 32px;
}

.footer-block h4 {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.58);
  margin: 0 0 10px;
  text-transform: uppercase;
  letter-spacing: 0.07em;
}

.footer-brand-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.footer-brand-head h4 {
  margin: 0;
}

.footer-chip {
  display: inline-flex;
  align-items: center;
  padding: 3px 8px;
  border: 1px solid rgba(45, 212, 191, 0.4);
  border-radius: 999px;
  font-size: 10px;
  color: rgba(153, 246, 228, 0.9);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.footer-copy {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.84);
  margin: 0 0 6px;
}

.footer-meta {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.58);
  margin: 0 0 4px;
}

.footer-label {
  margin: 0 0 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.footer-link {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  margin-bottom: 6px;
  transition: color 0.2s;
}

.footer-link:hover {
  color: var(--primary-light);
}

.footer-link .material-icons {
  font-size: 16px;
}

.footer-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.68);
}

.footer-list .material-icons {
  font-size: 15px;
  color: rgba(45, 212, 191, 0.9);
}

/* Mobile responsive */
@media (max-width: 800px) {
  .landing-split {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr auto;
  }

  .landing-brand {
    grid-column: 1;
    grid-row: 1;
  }

  .landing-form-side {
    grid-column: 1;
    grid-row: 2;
  }

  .landing-footer-bar {
    grid-column: 1;
    grid-row: 3;
  }
  
  .landing-brand {
    padding: 48px 24px;
  }
  
  .landing-title {
    font-size: 36px;
  }
  
  .feature-list {
    display: none;
  }
  
  .brand-footer {
    display: none;
  }
  
  .landing-form-side {
    padding: 0;
  }
  
  .form-container {
    padding: 32px 24px;
  }
  
  .landing-footer-bar {
    padding: 20px 24px;
  }
  
  .footer-content {
    grid-template-columns: 1fr;
    gap: 18px;
  }
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background: var(--bg-card);
  border-radius: 20px;
  border: 1px solid var(--border-default);
  padding: 40px 32px;
  box-shadow: var(--shadow-xl);
  backdrop-filter: blur(10px);
}

/* Header */
.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, var(--primary), var(--primary-hover));
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo .material-icons {
  font-size: 32px;
  color: white;
}

.auth-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 4px;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0;
}

/* Tabs */
.auth-tabs {
  display: flex;
  gap: 4px;
  background: var(--bg-recessed);
  padding: 4px;
  border-radius: 10px;
  margin-bottom: 24px;
}

.tab {
  flex: 1;
  padding: 10px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab.active {
  background: var(--primary);
  color: white;
}

.tab:hover:not(.active) {
  color: var(--text-primary);
}

/* Error */
.error-alert {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: var(--error-bg);
  border: 1px solid var(--error-tint);
  border-radius: 8px;
  color: var(--error);
  font-size: 13px;
  margin-bottom: 20px;
}

.error-alert .material-icons {
  font-size: 18px;
}

/* Form */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: 10px;
  padding: 0 12px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-wrapper:focus-within {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-tint);
}

.input-wrapper.invalid {
  border-color: rgba(239, 68, 68, 0.6);
  box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.12);
}

.input-wrapper .material-icons {
  font-size: 20px;
  color: var(--text-muted);
}

.input-wrapper input,
.input-wrapper select {
  flex: 1;
  padding: 12px 0;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
}

.input-wrapper input:focus-visible,
.input-wrapper select:focus-visible {
  outline: none;
  box-shadow: none;
}

.input-wrapper input::placeholder {
  color: var(--text-muted);
}

.select-wrapper {
  position: relative;
}

.select-wrapper select {
  appearance: none;
  cursor: pointer;
  padding-right: 24px;
}

.select-wrapper .chevron {
  position: absolute;
  right: 12px;
  pointer-events: none;
}

.toggle-btn {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: var(--text-muted);
  display: flex;
}

.toggle-btn:hover {
  color: var(--text-secondary);
}

.field-error {
  margin: 0;
  font-size: 12px;
  color: #f87171;
}

.password-rules {
  margin: 8px 0 0;
  padding: 10px 12px;
  list-style: none;
  border: 1px solid var(--border-default);
  border-radius: 10px;
  background: var(--bg-recessed);
  display: grid;
  gap: 6px;
}

.password-rules li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
}

.password-rules .material-icons {
  font-size: 16px;
}

.password-rules li.passed {
  color: #34d399;
}

/* Submit Button */
.submit-btn {
  padding: 14px;
  background: var(--primary);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  margin-top: 8px;
  box-shadow: var(--shadow-sm);
}

.submit-btn:hover:not(:disabled) {
  background: var(--primary-hover);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Divider */
.divider {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 8px 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border-default);
}

.divider span {
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
}

/* PIN Button */
.pin-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: var(--primary-tint);
  border: 1px solid var(--primary);
  border-radius: 10px;
  color: var(--primary);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: var(--shadow-xs);
}

.pin-btn:hover {
  background: var(--primary);
  color: white;
}

/* PIN View */
.pin-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.back-link {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  padding: 0;
  margin-bottom: 8px;
}

.back-link:hover {
  color: var(--primary);
}

.back-link .material-icons {
  font-size: 18px;
}

.pin-section {
  text-align: center;
}

.pin-section label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.pin-dots {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
}

.dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--bg-recessed);
  border: 2px solid var(--border-default);
  transition: all 0.2s;
}

.dot.filled {
  background: var(--primary);
  border-color: var(--primary);
}

.keypad {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  max-width: 240px;
  margin: 0 auto;
}

.key {
  height: 56px;
  border: none;
  border-radius: 14px;
  background: var(--bg-elevated);
  color: var(--text-primary);
  font-size: 20px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.key:hover {
  background: var(--bg-hover);
  box-shadow: var(--shadow-xs);
}

.key:active {
  transform: scale(0.95);
}

.key-fn {
  background: var(--bg-recessed);
}

.key-fn .material-icons {
  font-size: 22px;
}

.key-enter {
  background: var(--primary);
  color: white;
}

.key-enter:hover {
  background: var(--primary-hover);
}

.key-enter:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
