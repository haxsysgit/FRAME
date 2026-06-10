import { api, API_BASE_URL } from './api'
import { beginRequestLoading, endRequestLoading } from './globalLoading'

export const productsService = {
  list(params = {}) {
    const qs = new URLSearchParams()
    qs.set('limit', String(params.limit ?? 50))
    qs.set('offset', String(params.offset ?? 0))
    if (params.name) qs.set('name', params.name)
    if (params.generic_name) qs.set('generic_name', params.generic_name)
    if (params.therapeutic_category) qs.set('therapeutic_category', params.therapeutic_category)
    return api.get(`/products/?${qs.toString()}`)
  },

  async listAll(params = {}) {
    const batchSize = Math.min(500, Math.max(1, Number(params.batchSize ?? 500)))
    const maxRecords = Math.max(batchSize, Number(params.maxRecords ?? 10000))
    const seedOffset = Math.max(0, Number(params.offset ?? 0))
    const seen = new Set()
    const rows = []

    let offset = seedOffset
    while (rows.length < maxRecords) {
      const pageLimit = Math.min(batchSize, maxRecords - rows.length)
      const page = await this.list({ ...params, limit: pageLimit, offset })
      if (!Array.isArray(page) || page.length === 0) break

      page.forEach((item) => {
        if (!item?.id || seen.has(item.id)) return
        seen.add(item.id)
        rows.push(item)
      })

      if (page.length < pageLimit) break
      offset += page.length
    }

    return rows
  },

  get(id) {
    return api.get(`/products/${id}`)
  },

  create(payload) {
    return api.post('/products/', payload)
  },

  update(id, payload) {
    return api.patch(`/products/${id}`, payload)
  },

  remove(id) {
    return api.delete(`/products/${id}`)
  },

  adjustStock(productId, payload) {
    return api.post(`/products/${productId}/adjust-stock`, payload)
  },

  listAdjustments(productId, limit = 30) {
    return api.get(`/products/${productId}/adjustments?limit=${limit}`)
  },

  listPendingAdjustments(limit = 100) {
    return api.get(`/products/stock-adjustments/pending?limit=${limit}`)
  },

  listStockApprovalBypassGrants({ activeOnly = true } = {}) {
    const params = new URLSearchParams()
    params.set('active_only', String(Boolean(activeOnly)))
    return api.get(`/products/stock-adjustments/approval-bypass-grants?${params.toString()}`)
  },

  grantStockApprovalBypass({ userId, durationMinutes = 60, note = '' }) {
    return api.post('/products/stock-adjustments/approval-bypass-grants', {
      user_id: userId,
      duration_minutes: Number(durationMinutes),
      note: note || null,
    })
  },

  revokeStockApprovalBypass(grantId, reason = '') {
    return api.post(`/products/stock-adjustments/approval-bypass-grants/${grantId}/revoke`, {
      reason: reason || null,
    })
  },

  reviewAdjustment(productId, adjustmentId, payload) {
    return api.post(`/products/${productId}/adjustments/${adjustmentId}/review`, payload)
  },

  // Bulk import
  importCsv(file, skipDuplicates = true) {
    const form = new FormData()
    form.append('file', file)
    const token = localStorage.getItem('pharmax.token')
    const loadingLabel = `POST /products/import?skip_duplicates=${skipDuplicates}`
    beginRequestLoading(loadingLabel)
    return fetch(
      `${API_BASE_URL}/products/import?skip_duplicates=${skipDuplicates}`,
      { method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: form },
    )
      .then(async (r) => {
        const data = await r.json()
        if (!r.ok) throw new Error(data.detail ?? 'Import failed')
        return data
      })
      .finally(() => {
        endRequestLoading(loadingLabel)
      })
  },

  // Units
  listUnits(productId) {
    return api.get(`/products/${productId}/units`)
  },

  getUnits(productId) {
    return api.get(`/products/${productId}/units`)
  },

  addUnit(productId, payload) {
    return api.post(`/products/${productId}/units`, payload)
  },

  updateUnit(productId, unitId, payload) {
    return api.patch(`/products/${productId}/units/${unitId}`, payload)
  },
}
