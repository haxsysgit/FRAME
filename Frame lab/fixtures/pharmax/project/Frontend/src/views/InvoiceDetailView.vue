<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { invoicesService } from '../services/invoices'

const route = useRoute()
const router = useRouter()

const invoice = ref(null)
const loading = ref(true)
const error = ref(null)

const lineItems = computed(() => invoice.value?.items || [])
const createdBy = computed(() => invoice.value?.user?.full_name || invoice.value?.user?.username || '—')

onMounted(async () => {
  await loadInvoice()
})

async function loadInvoice() {
  loading.value = true
  error.value = null
  try {
    const id = route.params.id
    invoice.value = await invoicesService.getById(id)
  } catch (err) {
    error.value = err.message || 'Failed to load invoice'
    console.error('Failed to load invoice:', err)
  } finally {
    loading.value = false
  }
}

function fmtDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function fmtCurrency(val) {
  return `₦${(val ?? 0).toLocaleString('en-NG', { minimumFractionDigits: 2 })}`
}

function statusClass(status) {
  const s = (status || '').toUpperCase()
  if (s === 'DRAFT') return 'draft'
  if (s === 'STAMPED' || s === 'FINALIZED') return 'finalized'
  if (s === 'DISPENSED') return 'dispensed'
  if (s === 'CANCELLED') return 'cancelled'
  return 'draft'
}

function goBack() {
  router.push('/invoices')
}

function printInvoice() {
  window.print()
}
</script>

<template>
  <section class="invoice-detail-page">
    <div v-if="loading" class="state-card loading-state">
      <div class="spinner"></div>
      <p>Loading invoice...</p>
    </div>

    <div v-else-if="error" class="state-card error-state">
      <span class="material-icons">error_outline</span>
      <h3>Failed to Load Invoice</h3>
      <p>{{ error }}</p>
      <button class="btn-secondary" @click="goBack">
        <span class="material-icons">arrow_back</span>
        Back to Invoices
      </button>
    </div>

    <div v-else-if="invoice" class="invoice-content">
      <header class="page-actions">
        <div class="page-title">
          <h2>Invoice Details</h2>
          <p>Review invoice information and print a customer copy when needed.</p>
        </div>
        <div class="actions-right">
          <button class="btn-secondary" @click="goBack">
            <span class="material-icons">arrow_back</span>
            Back to Invoices
          </button>
          <button class="btn-primary" @click="printInvoice">
            <span class="material-icons">print</span>
            Print
          </button>
        </div>
      </header>

      <article class="invoice-document">
        <header class="invoice-header">
          <div class="invoice-brand">
            <span class="material-icons">receipt_long</span>
            <div>
              <h3>Sales Invoice</h3>
              <p class="invoice-id">#{{ invoice.id.slice(0, 12) }}</p>
            </div>
          </div>
          <span class="status-badge" :class="statusClass(invoice.status)">
            {{ invoice.status }}
          </span>
        </header>

        <section class="invoice-meta-grid">
          <article class="meta-card">
            <span class="meta-label">Date Created</span>
            <span class="meta-value">{{ fmtDate(invoice.created_at) }}</span>
          </article>
          <article class="meta-card">
            <span class="meta-label">Payment Method</span>
            <span class="meta-value">{{ invoice.payment_method || 'Not set' }}</span>
          </article>
          <article class="meta-card">
            <span class="meta-label">Created By</span>
            <span class="meta-value">{{ createdBy }}</span>
          </article>
          <article v-if="invoice.finalized_at" class="meta-card">
            <span class="meta-label">Stamped</span>
            <span class="meta-value">{{ fmtDate(invoice.finalized_at) }}</span>
          </article>
        </section>

        <section class="invoice-items">
          <div class="section-header">
            <h4>Items</h4>
            <span>{{ lineItems.length }} {{ lineItems.length === 1 ? 'item' : 'items' }}</span>
          </div>

          <div v-if="lineItems.length === 0" class="empty-items">
            <span class="material-icons">inventory_2</span>
            <p>No items were added to this invoice.</p>
          </div>

          <div v-else class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Unit</th>
                  <th class="text-right">Quantity</th>
                  <th class="text-right">Unit Price</th>
                  <th class="text-right">Total</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in lineItems" :key="item.id">
                  <td>
                    <div class="item-name">{{ item.product?.name || 'Product' }}</div>
                    <div v-if="item.product?.brand_name" class="item-brand">{{ item.product.brand_name }}</div>
                  </td>
                  <td>{{ item.product_unit?.name || '—' }}</td>
                  <td class="text-right mono">{{ item.quantity }}</td>
                  <td class="text-right mono">{{ fmtCurrency(item.unit_price) }}</td>
                  <td class="text-right mono">{{ fmtCurrency(item.line_total) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <footer class="invoice-footer">
          <p class="footer-note">Thank you for your patronage</p>
          <div class="invoice-totals">
            <div class="totals-row">
              <span>Subtotal</span>
              <span class="mono">{{ fmtCurrency(invoice.total_amount) }}</span>
            </div>
            <div class="totals-row grand">
              <span>Total</span>
              <span class="mono">{{ fmtCurrency(invoice.total_amount) }}</span>
            </div>
          </div>
        </footer>
      </article>
    </div>
  </section>
</template>

<style scoped>
.invoice-detail-page {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.invoice-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.state-card {
  min-height: 360px;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
  color: var(--text-secondary);
  text-align: center;
  padding: var(--space-8);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-default);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state .material-icons {
  font-size: 44px;
  color: var(--error);
}

.page-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  background: var(--bg-card);
  box-shadow: var(--shadow-xs);
}

.page-title h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.page-title p {
  margin: var(--space-1) 0 0;
  font-size: 13px;
  color: var(--text-muted);
}

.actions-right {
  display: flex;
  gap: var(--space-3);
}

.btn-secondary,
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  height: 40px;
  padding: 0 var(--space-4);
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-secondary {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  color: var(--text-secondary);
}

.btn-secondary:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.btn-primary {
  background: var(--primary);
  border: 1px solid var(--primary);
  color: white;
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
}

.btn-secondary .material-icons,
.btn-primary .material-icons {
  font-size: 18px;
}

.invoice-document {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.invoice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--border-subtle);
  background: linear-gradient(180deg, var(--primary-bg) 0%, rgba(15, 159, 137, 0.03) 100%);
}

.invoice-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.invoice-brand .material-icons {
  font-size: 26px;
  color: var(--primary);
}

.invoice-brand h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.invoice-id {
  margin: 2px 0 0;
  font-family: var(--font-data);
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 0.03em;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.draft {
  background: var(--bg-recessed);
  color: var(--text-muted);
}

.status-badge.finalized {
  background: var(--primary-tint);
  color: var(--primary);
}

.status-badge.dispensed {
  background: var(--success-tint);
  color: var(--success);
}

.status-badge.cancelled {
  background: var(--error-tint);
  color: var(--error);
}

.invoice-meta-grid {
  padding: var(--space-4) var(--space-6) 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--space-3);
}

.meta-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-3);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--bg-elevated);
}

.meta-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.meta-value {
  font-size: 13px;
  color: var(--text-primary);
}

.invoice-items {
  padding: var(--space-4) var(--space-6);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}

.section-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.section-header span {
  font-size: 12px;
  color: var(--text-muted);
}

.table-wrap {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.invoice-items table {
  width: 100%;
  border-collapse: collapse;
}

.invoice-items th {
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: var(--space-3) var(--space-4);
  background: var(--table-header-bg);
  border-bottom: 1px solid var(--border-subtle);
}

.invoice-items td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
  vertical-align: top;
}

.invoice-items tbody tr:hover td {
  background: var(--table-row-hover);
}

.invoice-items tr:last-child td {
  border-bottom: none;
}

.item-name {
  font-weight: 500;
  color: var(--text-primary);
}

.item-brand {
  margin-top: 2px;
  font-size: 12px;
  color: var(--text-muted);
}

.text-right {
  text-align: right;
}

.mono {
  font-family: var(--font-data);
}

.empty-items {
  border: 1px dashed var(--border-default);
  border-radius: var(--radius-lg);
  background: var(--bg-recessed);
  color: var(--text-muted);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-8);
  text-align: center;
}

.empty-items .material-icons {
  font-size: 30px;
  opacity: 0.55;
}

.empty-items p {
  margin: 0;
}

.invoice-footer {
  border-top: 1px solid var(--border-subtle);
  background: var(--bg-recessed);
  padding: var(--space-4) var(--space-6);
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.footer-note {
  margin: 0;
  font-size: 13px;
  color: var(--text-muted);
}

.invoice-totals {
  min-width: 260px;
  max-width: 320px;
  margin-left: auto;
  width: 100%;
}

.totals-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-1) 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.totals-row.grand {
  margin-top: var(--space-2);
  padding-top: var(--space-2);
  border-top: 2px solid var(--border-default);
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.totals-row.grand .mono {
  color: var(--primary);
}

@media (max-width: 900px) {
  .page-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .actions-right {
    width: 100%;
    flex-wrap: wrap;
  }

  .invoice-header,
  .invoice-items,
  .invoice-footer,
  .invoice-meta-grid {
    padding-left: var(--space-4);
    padding-right: var(--space-4);
  }

  .invoice-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .invoice-totals {
    min-width: 100%;
    max-width: none;
  }
}

@media print {
  .page-actions {
    display: none;
  }

  .invoice-detail-page {
    background: white;
    padding: 0;
  }

  .invoice-document {
    border: none;
    box-shadow: none;
  }

  .invoice-meta-grid,
  .invoice-items,
  .invoice-footer,
  .invoice-header {
    padding-left: 0;
    padding-right: 0;
  }
}
</style>
