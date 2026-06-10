import { ref } from 'vue'
import { defineStore } from 'pinia'
import { dashboardService } from '../services/dashboard'

export const useDashboardStore = defineStore('dashboard', () => {
  // Pre-aggregated metrics from backend
  const todayInvoiceCount = ref(0)
  const todayRevenue = ref(0)
  const activeProducts = ref(0)
  const outOfStockCount = ref(0)
  const lowStockItems = ref([])
  const creditOutstanding = ref(0)
  const recentInvoices = ref([])
  const totalInvoices = ref(0)
  const cancelledInvoiceCountToday = ref(0)
  const pendingUserApprovals = ref(0)
  const pendingStockAdjustments = ref(0)

  const loading = ref(false)
  const loaded = ref(false)
  const error = ref(null)

  async function load(force = false) {
    if (loaded.value && !force) return
    loading.value = true
    error.value = null
    try {
      const data = await dashboardService.getMetrics()
      todayInvoiceCount.value = data.today_invoice_count ?? 0
      todayRevenue.value = data.today_revenue ?? 0
      activeProducts.value = data.active_products ?? 0
      outOfStockCount.value = data.out_of_stock_count ?? 0
      lowStockItems.value = data.low_stock_items ?? []
      creditOutstanding.value = data.credit_outstanding ?? 0
      recentInvoices.value = data.recent_invoices ?? []
      totalInvoices.value = data.total_invoices ?? 0
      cancelledInvoiceCountToday.value = data.cancelled_invoice_count_today ?? 0
      pendingUserApprovals.value = data.pending_user_approvals ?? 0
      pendingStockAdjustments.value = data.pending_stock_adjustments ?? 0
      loaded.value = true
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    loaded,
    error,
    load,
    todayInvoiceCount,
    todayRevenue,
    activeProducts,
    outOfStockCount,
    lowStockItems,
    creditOutstanding,
    recentInvoices,
    totalInvoices,
    cancelledInvoiceCountToday,
    pendingUserApprovals,
    pendingStockAdjustments,
  }
})
