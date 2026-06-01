import { api } from './api'

export const dashboardService = {
  getMetrics() {
    return api.get('/dashboard/metrics')
  },

  getAnalytics({
    rangeDays = 30,
    trendGranularity = 'day',
    topN = 10,
    staffLimit = 5,
    invoiceLimit = 5,
    includeContext = true,
    soldById = null,
    asOfDate = null,
  } = {}) {
    const params = new URLSearchParams()
    params.set('range_days', String(rangeDays))
    params.set('trend_granularity', String(trendGranularity))
    params.set('top_n', String(topN))
    params.set('staff_limit', String(staffLimit))
    params.set('invoice_limit', String(invoiceLimit))
    params.set('include_context', String(Boolean(includeContext)))
    if (soldById) params.set('sold_by_id', String(soldById))
    if (asOfDate) params.set('as_of_date', String(asOfDate))
    return api.get(`/dashboard/analytics?${params.toString()}`)
  },

  getReports({ rangeDays = 30, soldById = null, asOfDate = null } = {}) {
    const params = new URLSearchParams()
    params.set('range_days', String(rangeDays))
    if (soldById) params.set('sold_by_id', String(soldById))
    if (asOfDate) params.set('as_of_date', String(asOfDate))
    return api.get(`/dashboard/reports?${params.toString()}`)
  },

  getEndOfDay({ rangeDays = 30, soldById = null, asOfDate = null } = {}) {
    const params = new URLSearchParams()
    params.set('range_days', String(rangeDays))
    if (soldById) params.set('sold_by_id', String(soldById))
    if (asOfDate) params.set('as_of_date', String(asOfDate))
    return api.get(`/dashboard/eod?${params.toString()}`)
  },
}
