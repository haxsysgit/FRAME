import { api } from './api'

export const invoicesService = {
  list({ status = null, limit = 50, offset = 0 } = {}) {
    const params = new URLSearchParams()
    const normalizedStatus = String(status || '').toUpperCase()
    if (normalizedStatus) {
      params.append('status', normalizedStatus === 'STAMPED' ? 'FINALIZED' : normalizedStatus)
    }
    params.append('limit', limit)
    params.append('offset', offset)
    return api.get(`/invoices/all?${params}`)
  },

  get(id) {
    return api.get(`/invoices/${id}`)
  },

  getById(id) {
    return api.get(`/invoices/${id}`)
  },

  create(payload = {}) {
    return api.post('/invoices/', payload)
  },

  addItem(invoiceId, item) {
    return api.post(`/invoices/${invoiceId}/items`, item)
  },

  finalize(invoiceId, paymentMethod) {
    return api.post(`/invoices/${invoiceId}/finalize`, { payment_method: paymentMethod })
  },

  dispense(invoiceId) {
    return api.post(`/invoices/${invoiceId}/dispense`)
  },

  cancel(invoiceId, reason = null) {
    return api.post(`/invoices/${invoiceId}/cancel`, { reason })
  },

  updateCashierNote(invoiceId, cashierNote = '') {
    return api.patch(`/invoices/${invoiceId}/cashier-note`, { cashier_note: cashierNote || null })
  },

  getReconciliationStatus() {
    return api.get('/invoices/reconciliation/status')
  },

  lockDay(note = '') {
    return api.post('/invoices/reconciliation/lock-day', { note: note || null })
  },

  runReconciliation(note = '') {
    return api.post('/invoices/reconciliation/run', { note: note || null })
  },

  listAfterHoursGrants({ activeOnly = true } = {}) {
    const params = new URLSearchParams()
    params.set('active_only', String(Boolean(activeOnly)))
    return api.get(`/invoices/reconciliation/after-hours-grants?${params.toString()}`)
  },

  grantAfterHoursAccess({ userId, durationHours = 1, note = '' }) {
    return api.post('/invoices/reconciliation/after-hours-grants', {
      user_id: userId,
      duration_hours: Number(durationHours),
      note: note || null,
    })
  },

  revokeAfterHoursAccess(grantId, reason = '') {
    return api.post(`/invoices/reconciliation/after-hours-grants/${grantId}/revoke`, {
      reason: reason || null,
    })
  },

  returnToSender(invoiceId, note = '') {
    return api.post(`/invoices/${invoiceId}/return`, { note: note || null })
  },

  printReceipt(invoiceId) {
    return api.post(`/invoices/${invoiceId}/print-receipt`)
  },
}
