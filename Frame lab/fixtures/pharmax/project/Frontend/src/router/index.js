import { createRouter, createWebHistory } from 'vue-router'
import AppShell from '../layouts/AppShell.vue'
import DashboardView from '../views/DashboardView.vue'
import AuthView from '../views/AuthView.vue'
import PlaceholderView from '../views/PlaceholderView.vue'
import ProductsView from '../views/ProductsView.vue'
import ProductUnitsView from '../views/ProductUnitsView.vue'
import StockView from '../views/StockView.vue'
import InvoiceListView from '../views/InvoiceListView.vue'
import InvoiceCreateView from '../views/InvoiceCreateView.vue'
import CashierView from '../views/CashierView.vue'
import ReportsView from '../views/ReportsView.vue'
import SettingsView from '../views/SettingsView.vue'
import TeamAccessView from '../views/TeamAccessView.vue'
import ActivityLogsView from '../views/ActivityLogsView.vue'
import AnalyticsHubView from '../views/analytics/AnalyticsHubView.vue'
import AnalyticsRevenueTrendView from '../views/analytics/AnalyticsRevenueTrendView.vue'
import AnalyticsProductMovementView from '../views/analytics/AnalyticsProductMovementView.vue'
import AnalyticsStaffPerformanceView from '../views/analytics/AnalyticsStaffPerformanceView.vue'
import AnalyticsPaymentInsightsView from '../views/analytics/AnalyticsPaymentInsightsView.vue'
import ReportsHubView from '../views/reports/ReportsHubView.vue'
import ReportStockOutView from '../views/reports/ReportStockOutView.vue'
import ReportStockSummaryView from '../views/reports/ReportStockSummaryView.vue'
import ReportHighestInvoicesView from '../views/reports/ReportHighestInvoicesView.vue'
import ReportProductSalesView from '../views/reports/ReportProductSalesView.vue'
import ReportExpiringDrugsView from '../views/reports/ReportExpiringDrugsView.vue'
import { beginRouteLoading, endRouteLoading } from '../services/globalLoading'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: AuthView,
    meta: {
      label: 'Welcome',
      subtitle: 'Pharmax - Modern Pharmacy Management',
      public: true,
    },
  },
  {
    path: '/',
    component: AppShell,
    children: [
      {
        path: '',
        redirect: () => {
          const token = localStorage.getItem('pharmax.token')
          if (!token) return '/login'
          return '/dashboard'
        },
      },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: DashboardView,
        meta: {
          label: 'Dashboard',
          subtitle: 'Business overview and live operational status.',
          roles: ['ADMIN', 'CASHIER', 'STAFF'],
        },
      },
      {
        path: 'products',
        name: 'products',
        component: ProductsView,
        meta: {
          label: 'Products',
          subtitle: 'Master catalog — search, filter and manage all products.',
          roles: ['ADMIN', 'CASHIER', 'STAFF'],
        },
      },
      {
        path: 'products/units',
        name: 'products-units',
        component: ProductUnitsView,
        meta: {
          label: 'Units & Pricing',
          subtitle: 'View and edit unit prices and multipliers per product.',
          roles: ['ADMIN', 'CASHIER', 'STAFF'],
        },
      },
      {
        path: 'stock',
        name: 'stock',
        component: StockView,
        meta: {
          label: 'Stock Management',
          subtitle: 'Adjust quantities and review audit trail history.',
          roles: ['ADMIN', 'CASHIER', 'STAFF'],
        },
      },
      {
        path: 'stock/out-of-stock',
        name: 'stock-out',
        component: ReportStockOutView,
        meta: {
          label: 'Out-of-Stock Items',
          subtitle: 'Zero-quantity products to restock first.',
          showShellHeader: false,
          roles: ['ADMIN', 'CASHIER', 'STAFF'],
        },
      },
      {
        path: 'stock/low-stock',
        name: 'stock-low-watch',
        component: ReportStockSummaryView,
        meta: {
          label: 'Low Stock Watchlist',
          subtitle: 'Low-quantity products to reorder before stock-outs.',
          showShellHeader: false,
          roles: ['ADMIN', 'CASHIER', 'STAFF'],
        },
      },
      {
        path: 'invoices',
        name: 'invoices',
        component: InvoiceListView,
        meta: {
          label: 'Invoices',
          subtitle: 'View and manage all sales invoices.',
          roles: ['ADMIN', 'CASHIER', 'STAFF'],
        },
      },
      {
        path: 'invoices/create',
        name: 'invoices-create',
        component: InvoiceCreateView,
        meta: {
          label: 'Create Invoice',
          subtitle: 'Build a new sales invoice.',
          roles: ['ADMIN', 'STAFF', 'CASHIER'],
          showShellHeader: false,
        },
      },
      {
        path: 'invoices/:id',
        name: 'invoice-detail',
        component: () => import('../views/InvoiceDetailView.vue'),
        meta: {
          label: 'Invoice Details',
          subtitle: 'View invoice details.',
          showShellHeader: false,
          roles: ['ADMIN', 'CASHIER', 'STAFF'],
        },
      },
      {
        path: 'cashier',
        name: 'cashier',
        component: CashierView,
        meta: {
          label: 'Cashier Desk',
          subtitle: 'Handle payment confirmation and reconciliation.',
          roles: ['ADMIN', 'CASHIER'],
        },
      },
      {
        path: 'ai-query',
        name: 'ai-query',
        component: PlaceholderView,
        meta: {
          label: 'AI Query',
          subtitle: 'Ask business questions and inspect generated SQL.',
          roles: ['ADMIN'],
        },
      },
      {
        path: 'analytics',
        component: AnalyticsHubView,
        meta: {
          label: 'Analytics',
          subtitle: 'Track revenue, products, staff, and payments.',
          showShellHeader: false,
          roles: ['ADMIN'],
        },
        children: [
          {
            path: '',
            redirect: { name: 'analytics-revenue-trend' },
          },
          {
            path: 'revenue-trend',
            name: 'analytics-revenue-trend',
            component: AnalyticsRevenueTrendView,
            meta: {
              label: 'Revenue Trend',
              subtitle: 'Track paid revenue and invoice trends.',
              roles: ['ADMIN'],
            },
          },
          {
            path: 'product-movement',
            name: 'analytics-product-movement',
            component: AnalyticsProductMovementView,
            meta: {
              label: 'Product Insights',
              subtitle: 'See fast movers, slow movers, and stock risk.',
              roles: ['ADMIN'],
            },
          },
          {
            path: 'staff-performance',
            name: 'analytics-staff-performance',
            component: AnalyticsStaffPerformanceView,
            meta: {
              label: 'Staff Performance',
              subtitle: 'See each staff member\'s invoice count and sales value.',
              roles: ['ADMIN'],
            },
          },
          {
            path: 'payment-insights',
            name: 'analytics-payment-insights',
            component: AnalyticsPaymentInsightsView,
            meta: {
              label: 'Payment Insights',
              subtitle: 'Review payment methods and invoice status mix.',
              roles: ['ADMIN'],
            },
          },
        ],
      },
      {
        path: 'reports',
        component: ReportsHubView,
        meta: {
          label: 'Reports',
          subtitle: 'Open daily and sales reports in simple views.',
          showShellHeader: false,
          roles: ['ADMIN', 'CASHIER'],
        },
        children: [
          {
            path: '',
            redirect: { name: 'report-end-of-day' },
          },
          {
            path: 'end-of-day',
            name: 'report-end-of-day',
            component: ReportsView,
            meta: {
              label: 'End of Day Report',
              subtitle: 'Daily closing summary for handover and reconciliation.',
              roles: ['ADMIN', 'CASHIER'],
            },
          },
          {
            path: 'highest-invoices',
            name: 'report-highest-invoices',
            component: ReportHighestInvoicesView,
            meta: {
              label: 'Largest Customer Bills',
              subtitle: 'Highest-value invoices in the selected period.',
              roles: ['ADMIN', 'CASHIER'],
            },
          },
          {
            path: 'product-sales',
            name: 'report-product-sales',
            component: ReportProductSalesView,
            meta: {
              label: 'Best-Selling Products',
              subtitle: 'Products with the most units sold and sales value.',
              roles: ['ADMIN', 'CASHIER'],
            },
          },
          {
            path: 'expiring-drugs',
            name: 'report-expiring-drugs',
            component: ReportExpiringDrugsView,
            meta: {
              label: 'Expiry Watch',
              subtitle: 'Manual mode until backend batch-expiry data and endpoint are ready.',
              roles: ['ADMIN', 'CASHIER'],
            },
          },
        ],
      },
      {
        path: 'reconciliation',
        redirect: '/analytics',
      },
      {
        path: 'credit-ledger',
        redirect: '/reports',
      },
      {
        path: 'activity-logs',
        name: 'activity-logs',
        component: ActivityLogsView,
        meta: {
          label: 'Activity Logs',
          subtitle: 'Review chronological actions across the system.',
          roles: ['ADMIN', 'CASHIER', 'STAFF'],
        },
      },
      {
        path: 'users',
        name: 'users',
        component: TeamAccessView,
        meta: {
          label: 'Team & Access',
          subtitle: 'Create staff/cashier accounts, reset credentials, and control roles.',
          roles: ['ADMIN'],
        },
      },
      {
        path: 'users/activity',
        name: 'users-activity',
        component: TeamAccessView,
        meta: {
          label: 'Team Activity',
          subtitle: 'Review role, access, and credential activity in one timeline.',
          roles: ['ADMIN'],
        },
      },
      {
        path: 'users/tasks',
        name: 'users-tasks',
        component: TeamAccessView,
        meta: {
          label: 'Team Tasks',
          subtitle: 'Assign team tasks and track completion.',
          roles: ['ADMIN'],
        },
      },
      {
        path: 'settings',
        redirect: '/settings/profile',
      },
      {
        path: 'settings/:section(profile|pharmacy|workflow|notifications|accessibility|safety)',
        name: 'settings-section',
        component: SettingsView,
        meta: {
          label: 'Settings',
          subtitle: 'Tune app preferences and environment options by section.',
          roles: ['ADMIN', 'CASHIER', 'STAFF'],
        },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

function landingRoute(role) {
  if (role === 'CASHIER') return '/cashier'
  if (role === 'STAFF') return '/invoices'
  return '/dashboard'
}

let activeRouteLoadingLabel = 'Route navigation'

router.beforeEach(async (to) => {
  const { useAuthStore } = await import('../stores/auth')
  const auth = useAuthStore()

  // If we have a token but no user loaded yet (page reload), restore session
  if (auth.token && !auth.user) {
    await auth.fetchUser()
  }

  // Public routes (login) — redirect by role if already logged in
  if (to.meta?.public && auth.isAuthenticated) {
    return landingRoute(auth.userRole)
  }

  // Protected routes — redirect to login if not authenticated
  if (!to.meta?.public && !auth.isAuthenticated) {
    return '/login'
  }

  // Role-based access — redirect if user lacks permission for this route
  const allowedRoles = to.meta?.roles
  if (allowedRoles && auth.isAuthenticated && !allowedRoles.includes(auth.userRole)) {
    return landingRoute(auth.userRole)
  }
})

router.beforeResolve((to) => {
  activeRouteLoadingLabel = `Route ${to.fullPath || to.path || 'navigation'}`
  beginRouteLoading(activeRouteLoadingLabel)
})

router.afterEach((to) => {
  endRouteLoading(activeRouteLoadingLabel)
  activeRouteLoadingLabel = 'Route navigation'
  const label = to.meta?.label ? `${to.meta.label} | ` : ''
  document.title = `${label}Pharmax`
})

router.onError(() => {
  endRouteLoading(activeRouteLoadingLabel)
  activeRouteLoadingLabel = 'Route navigation'
})

export default router
