<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

// View state
const currentView = ref('landing') // 'landing', 'login', 'register', 'pin'

// Login form
const loginEmail = ref('')
const loginPassword = ref('')
const showLoginPassword = ref(false)

// Register form
const regFullName = ref('')
const regEmail = ref('')
const regUsername = ref('')
const regPassword = ref('')
const regConfirmPassword = ref('')
const regRole = ref('STAFF')
const showRegPassword = ref(false)

// PIN login
const selectedStaff = ref('')
const pin = ref('')
const staffList = [
  { id: 'cashier@pharmax.local', name: 'Cashier', role: 'CASHIER' },
  { id: 'staff@pharmax.local', name: 'Staff', role: 'STAFF' },
  { id: 'admin@pharmax.local', name: 'Admin', role: 'ADMIN' },
]

// Handlers
async function handleLogin() {
  if (!loginEmail.value || !loginPassword.value) return
  const ok = await auth.login(loginEmail.value, loginPassword.value)
  if (ok) redirectByRole()
}

async function handleRegister() {
  if (regPassword.value !== regConfirmPassword.value) {
    auth.error = 'Passwords do not match'
    return
  }
  // For now, show message - registration API would go here
  alert('Registration submitted. Please contact admin for account activation.')
  currentView.value = 'login'
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
  pin.value = ''
}
</script>

<template>
  <div class="landing-page">
    <!-- Landing View -->
    <div v-if="currentView === 'landing'" class="landing-content">
      <!-- Hero Section -->
      <header class="hero">
        <nav class="nav-bar">
          <div class="brand">
            <div class="brand-icon">
              <span class="material-icons">local_pharmacy</span>
            </div>
            <span class="brand-name">Pharmax</span>
          </div>
          <div class="nav-actions">
            <button class="nav-btn ghost" @click="switchView('login')">Sign In</button>
            <button class="nav-btn primary" @click="switchView('register')">Get Started</button>
          </div>
        </nav>

        <div class="hero-content">
          <div class="hero-text">
            <h1>Modern Pharmacy<br/>Management System</h1>
            <p class="hero-subtitle">
              Streamline your pharmacy operations with intelligent inventory tracking, 
              seamless billing, and real-time analytics. Built for modern pharmacies.
            </p>
            <div class="hero-actions">
              <button class="hero-btn primary" @click="switchView('register')">
                <span class="material-icons">rocket_launch</span>
                Start Free Trial
              </button>
              <button class="hero-btn secondary" @click="switchView('login')">
                <span class="material-icons">login</span>
                Sign In
              </button>
            </div>
          </div>
          <div class="hero-visual">
            <div class="dashboard-preview">
              <div class="preview-header">
                <div class="preview-dots">
                  <span></span><span></span><span></span>
                </div>
                <span class="preview-title">Dashboard</span>
              </div>
              <div class="preview-content">
                <div class="preview-stat">
                  <span class="stat-value">₦847,250</span>
                  <span class="stat-label">Today's Revenue</span>
                </div>
                <div class="preview-chart">
                  <div class="chart-bar" style="height: 40%"></div>
                  <div class="chart-bar" style="height: 65%"></div>
                  <div class="chart-bar" style="height: 45%"></div>
                  <div class="chart-bar" style="height: 80%"></div>
                  <div class="chart-bar" style="height: 55%"></div>
                  <div class="chart-bar active" style="height: 90%"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Features Section -->
      <section class="features">
        <h2>Everything You Need</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon blue">
              <span class="material-icons">inventory_2</span>
            </div>
            <h3>Smart Inventory</h3>
            <p>Track stock levels, set reorder points, and manage multiple suppliers effortlessly.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon green">
              <span class="material-icons">point_of_sale</span>
            </div>
            <h3>Quick Billing</h3>
            <p>Process sales in seconds with barcode scanning and flexible payment options.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon purple">
              <span class="material-icons">analytics</span>
            </div>
            <h3>Real-time Analytics</h3>
            <p>Get insights into sales trends, popular products, and business performance.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon orange">
              <span class="material-icons">people</span>
            </div>
            <h3>Multi-user Access</h3>
            <p>Role-based permissions for admins, cashiers, and staff members.</p>
          </div>
        </div>
      </section>

      <!-- Footer -->
      <footer class="landing-footer">
        <div class="footer-content">
          <div class="footer-brand">
            <span class="material-icons">local_pharmacy</span>
            <span>Pharmax</span>
          </div>
          <p>© 2026 Pharmax. Modern pharmacy management.</p>
        </div>
      </footer>
    </div>

    <!-- Login View -->
    <div v-else-if="currentView === 'login'" class="auth-view">
      <div class="auth-container">
        <button class="back-btn" @click="switchView('landing')">
          <span class="material-icons">arrow_back</span>
          Back
        </button>

        <div class="auth-header">
          <div class="auth-logo">
            <span class="material-icons">local_pharmacy</span>
          </div>
          <h1>Welcome Back</h1>
          <p>Sign in to your Pharmax account</p>
        </div>

        <div v-if="auth.error" class="error-alert">
          <span class="material-icons">error</span>
          {{ auth.error }}
        </div>

        <form class="auth-form" @submit.prevent="handleLogin">
          <div class="form-group">
            <label>Email or Username</label>
            <div class="input-field">
              <span class="material-icons">person</span>
              <input 
                v-model="loginEmail" 
                type="text" 
                placeholder="Enter your email or username"
                autocomplete="username"
              />
            </div>
          </div>

          <div class="form-group">
            <label>Password</label>
            <div class="input-field">
              <span class="material-icons">lock</span>
              <input 
                v-model="loginPassword" 
                :type="showLoginPassword ? 'text' : 'password'" 
                placeholder="Enter your password"
                autocomplete="current-password"
              />
              <button type="button" class="toggle-pass" @click="showLoginPassword = !showLoginPassword">
                <span class="material-icons">{{ showLoginPassword ? 'visibility_off' : 'visibility' }}</span>
              </button>
            </div>
          </div>

          <button type="submit" class="submit-btn" :disabled="auth.loading">
            {{ auth.loading ? 'Signing in...' : 'Sign In' }}
          </button>
        </form>

        <div class="auth-divider">
          <span>or</span>
        </div>

        <button class="pin-login-btn" @click="switchView('pin')">
          <span class="material-icons">dialpad</span>
          Sign in with PIN
        </button>

        <p class="auth-switch">
          Don't have an account? 
          <button @click="switchView('register')">Create Account</button>
        </p>
      </div>
    </div>

    <!-- Register View -->
    <div v-else-if="currentView === 'register'" class="auth-view">
      <div class="auth-container">
        <button class="back-btn" @click="switchView('landing')">
          <span class="material-icons">arrow_back</span>
          Back
        </button>

        <div class="auth-header">
          <div class="auth-logo">
            <span class="material-icons">local_pharmacy</span>
          </div>
          <h1>Create Account</h1>
          <p>Join Pharmax and streamline your pharmacy</p>
        </div>

        <div v-if="auth.error" class="error-alert">
          <span class="material-icons">error</span>
          {{ auth.error }}
        </div>

        <form class="auth-form" @submit.prevent="handleRegister">
          <div class="form-group">
            <label>Full Name</label>
            <div class="input-field">
              <span class="material-icons">badge</span>
              <input v-model="regFullName" type="text" placeholder="Enter your full name" />
            </div>
          </div>

          <div class="form-group">
            <label>Email</label>
            <div class="input-field">
              <span class="material-icons">email</span>
              <input v-model="regEmail" type="email" placeholder="Enter your email" />
            </div>
          </div>

          <div class="form-group">
            <label>Username</label>
            <div class="input-field">
              <span class="material-icons">person</span>
              <input v-model="regUsername" type="text" placeholder="Choose a username" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Password</label>
              <div class="input-field">
                <span class="material-icons">lock</span>
                <input 
                  v-model="regPassword" 
                  :type="showRegPassword ? 'text' : 'password'" 
                  placeholder="Create password" 
                />
              </div>
            </div>
            <div class="form-group">
              <label>Confirm Password</label>
              <div class="input-field">
                <span class="material-icons">lock</span>
                <input 
                  v-model="regConfirmPassword" 
                  type="password" 
                  placeholder="Confirm password" 
                />
              </div>
            </div>
          </div>

          <button type="submit" class="submit-btn" :disabled="auth.loading">
            {{ auth.loading ? 'Creating...' : 'Create Account' }}
          </button>
        </form>

        <p class="auth-switch">
          Already have an account? 
          <button @click="switchView('login')">Sign In</button>
        </p>
      </div>
    </div>

    <!-- PIN Login View -->
    <div v-else-if="currentView === 'pin'" class="auth-view">
      <div class="auth-container pin-container">
        <button class="back-btn" @click="switchView('login')">
          <span class="material-icons">arrow_back</span>
          Back
        </button>

        <div class="auth-header">
          <div class="auth-logo">
            <span class="material-icons">dialpad</span>
          </div>
          <h1>PIN Login</h1>
          <p>Quick access for staff members</p>
        </div>

        <div v-if="auth.error" class="error-alert">
          <span class="material-icons">error</span>
          {{ auth.error }}
        </div>

        <div class="form-group">
          <label>Select User</label>
          <div class="input-field select-field">
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
            <button v-for="n in [1,2,3,4,5,6,7,8,9]" :key="n" class="key" @click="handlePinKey(String(n))">
              {{ n }}
            </button>
            <button class="key key-clear" @click="handlePinClear">
              <span class="material-icons">backspace</span>
            </button>
            <button class="key" @click="handlePinKey('0')">0</button>
            <button class="key key-enter" :disabled="pin.length < 4" @click="submitPin">
              <span class="material-icons">check</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ===== Base Styles ===== */
.landing-page {
  min-height: 100vh;
  background: var(--bg-canvas);
  color: var(--text-primary);
}

/* ===== Landing View ===== */
.landing-content {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Navigation */
.nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 60px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--primary), var(--primary-hover));
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-icon .material-icons {
  color: white;
  font-size: 22px;
}

.brand-name {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

.nav-actions {
  display: flex;
  gap: 12px;
}

.nav-btn {
  padding: 10px 24px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-btn.ghost {
  background: transparent;
  border: 1px solid var(--border-default);
  color: var(--text-primary);
}

.nav-btn.ghost:hover {
  background: var(--bg-hover);
}

.nav-btn.primary {
  background: var(--primary);
  border: none;
  color: white;
}

.nav-btn.primary:hover {
  background: var(--primary-hover);
}

/* Hero */
.hero {
  padding: 0 60px 80px;
  max-width: 1400px;
  margin: 0 auto;
}

.hero-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
  align-items: center;
  padding-top: 60px;
}

.hero-text h1 {
  font-size: 52px;
  font-weight: 800;
  line-height: 1.1;
  margin: 0 0 24px;
  background: linear-gradient(135deg, var(--text-primary), var(--primary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 18px;
  line-height: 1.7;
  color: var(--text-secondary);
  margin: 0 0 40px;
  max-width: 500px;
}

.hero-actions {
  display: flex;
  gap: 16px;
}

.hero-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.hero-btn.primary {
  background: var(--primary);
  border: none;
  color: white;
}

.hero-btn.primary:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.hero-btn.secondary {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  color: var(--text-primary);
}

.hero-btn.secondary:hover {
  background: var(--bg-hover);
}

/* Dashboard Preview */
.hero-visual {
  display: flex;
  justify-content: center;
}

.dashboard-preview {
  width: 100%;
  max-width: 480px;
  background: var(--bg-card);
  border-radius: 16px;
  border: 1px solid var(--border-default);
  overflow: hidden;
  box-shadow: 0 20px 60px -20px rgba(0,0,0,0.3);
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: var(--bg-elevated);
  border-bottom: 1px solid var(--border-subtle);
}

.preview-dots {
  display: flex;
  gap: 6px;
}

.preview-dots span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--border-default);
}

.preview-dots span:first-child { background: #ff5f57; }
.preview-dots span:nth-child(2) { background: #febc2e; }
.preview-dots span:last-child { background: #28c840; }

.preview-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
}

.preview-content {
  padding: 32px;
}

.preview-stat {
  text-align: center;
  margin-bottom: 32px;
}

.stat-value {
  display: block;
  font-size: 36px;
  font-weight: 700;
  color: var(--primary);
}

.stat-label {
  font-size: 14px;
  color: var(--text-muted);
}

.preview-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  height: 100px;
  gap: 12px;
}

.chart-bar {
  flex: 1;
  background: var(--bg-elevated);
  border-radius: 6px;
  transition: all 0.3s ease;
}

.chart-bar.active {
  background: var(--primary);
}

/* Features */
.features {
  padding: 80px 60px;
  max-width: 1400px;
  margin: 0 auto;
}

.features h2 {
  text-align: center;
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 60px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.feature-card {
  padding: 32px;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  transition: all 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px -12px rgba(0,0,0,0.2);
}

.feature-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.feature-icon.blue { background: #3b82f620; }
.feature-icon.blue .material-icons { color: #3b82f6; }
.feature-icon.green { background: #10b98120; }
.feature-icon.green .material-icons { color: #10b981; }
.feature-icon.purple { background: #8b5cf620; }
.feature-icon.purple .material-icons { color: #8b5cf6; }
.feature-icon.orange { background: #f9731620; }
.feature-icon.orange .material-icons { color: #f97316; }

.feature-icon .material-icons {
  font-size: 28px;
}

.feature-card h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 12px;
}

.feature-card p {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-secondary);
  margin: 0;
}

/* Footer */
.landing-footer {
  padding: 40px 60px;
  border-top: 1px solid var(--border-subtle);
  margin-top: auto;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.footer-brand .material-icons {
  color: var(--primary);
}

.footer-content p {
  color: var(--text-muted);
  font-size: 14px;
  margin: 0;
}

/* ===== Auth Views ===== */
.auth-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: 
    radial-gradient(circle at 20% 20%, var(--primary-bg) 0%, transparent 50%),
    var(--bg-canvas);
}

.auth-container {
  width: 100%;
  max-width: 440px;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 20px;
  padding: 40px;
}

.pin-container {
  max-width: 380px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 14px;
  cursor: pointer;
  margin-bottom: 24px;
  padding: 0;
}

.back-btn:hover {
  color: var(--text-primary);
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-logo {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, var(--primary), var(--primary-hover));
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-logo .material-icons {
  font-size: 32px;
  color: white;
}

.auth-header h1 {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px;
}

.auth-header p {
  color: var(--text-muted);
  font-size: 15px;
  margin: 0;
}

.error-alert {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  background: var(--error-bg);
  border: 1px solid var(--error);
  border-radius: 10px;
  color: var(--error);
  font-size: 14px;
  margin-bottom: 24px;
}

.error-alert .material-icons {
  font-size: 20px;
}

/* Form Styles */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.input-field {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 52px;
  padding: 0 16px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: 12px;
  transition: all 0.2s ease;
}

.input-field:focus-within {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-bg);
}

.input-field .material-icons {
  color: var(--text-muted);
  font-size: 20px;
}

.input-field input,
.input-field select {
  flex: 1;
  height: 100%;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 15px;
  outline: none;
}

.input-field input::placeholder {
  color: var(--text-disabled);
}

.select-field {
  position: relative;
}

.select-field select {
  appearance: none;
  cursor: pointer;
}

.select-field .chevron {
  position: absolute;
  right: 16px;
  pointer-events: none;
}

.toggle-pass {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  color: var(--text-muted);
  display: flex;
}

.toggle-pass:hover {
  color: var(--text-primary);
}

.submit-btn {
  height: 52px;
  background: var(--primary);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.submit-btn:hover:not(:disabled) {
  background: var(--primary-hover);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-divider {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 24px 0;
  color: var(--text-muted);
  font-size: 13px;
}

.auth-divider::before,
.auth-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border-default);
}

.pin-login-btn {
  width: 100%;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pin-login-btn:hover {
  background: var(--bg-hover);
}

.auth-switch {
  text-align: center;
  margin-top: 24px;
  color: var(--text-muted);
  font-size: 14px;
}

.auth-switch button {
  background: none;
  border: none;
  color: var(--primary);
  font-weight: 600;
  cursor: pointer;
}

.auth-switch button:hover {
  text-decoration: underline;
}

/* PIN Section */
.pin-section {
  margin-top: 24px;
}

.pin-section label {
  display: block;
  text-align: center;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.pin-dots {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 24px;
}

.dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid var(--border-default);
  transition: all 0.15s ease;
}

.dot.filled {
  background: var(--primary);
  border-color: var(--primary);
}

.keypad {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.key {
  height: 60px;
  border-radius: 12px;
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-primary);
  font-size: 24px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.1s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.key:active {
  transform: scale(0.95);
  background: var(--bg-hover);
}

.key-clear {
  background: var(--bg-recessed);
}

.key-clear .material-icons {
  font-size: 22px;
  color: var(--text-muted);
}

.key-enter {
  background: var(--primary);
  border-color: var(--primary);
}

.key-enter .material-icons {
  color: white;
  font-size: 24px;
}

.key-enter:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ===== Responsive ===== */
@media (max-width: 1024px) {
  .hero-content {
    grid-template-columns: 1fr;
    gap: 60px;
  }

  .hero-visual {
    order: -1;
  }

  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .nav-bar, .hero, .features, .landing-footer {
    padding-left: 24px;
    padding-right: 24px;
  }

  .hero-text h1 {
    font-size: 36px;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .footer-content {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
}
</style>
