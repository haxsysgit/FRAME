# Pharmax Development Progress Tracker

## Current Status: Final Stabilization Sweep Active (Backend-first pass complete)
**Last Updated**: April 6, 2026

---

## Final Stabilization Sweep (Backend-first) — April 6, 2026

### Completed in this pass
- [x] Backend core hardening updates completed:
  - CORS now respects configured `CORS_ORIGINS` in app bootstrap.
  - Auth dependency cleanup removed unreachable token-exception handling.
  - Security module import/format cleanup and clearer token-expiry handling comments.
  - Admin auth flow no longer performs duplicate commit in login and now uses narrowed DB exception handling.
- [x] Backend service-layer hardening completed:
  - `InvoiceService.update_cashier_note` fixed to avoid nested commit inside transaction context.
  - `UserService` login/PIN auth paths hardened against commit/audit failures and stale object crashes.
  - User registration and managed-user creation now commit once per flow to reduce partial-write risk.
  - User task sorting fixed to keep open tasks first while preserving recency order.
  - Product restore flow now validates target state and uses consistent audit action naming (`RESTORE_PRODUCT`).
  - Product/unit parsing tightened for safer numeric conversion behavior.
- [x] Backend route-layer consistency updates completed:
  - Staff invoice access guard added so staff can only open/update invoices they created.
  - Invoice list pagination now validates `limit`/`offset` bounds.
  - Product route numeric pagination params now validated with query bounds.
  - Error re-raise paths normalized to preserve HTTP exception causes.
- [x] Backend model/schema contract alignment completed:
  - Product unit multiplier contract standardized to **whole numbers** (schema + service alignment with DB integer column).
  - Removed stale/unused invoice request placeholder schema (`DispenseInvoiceRequest`).
- [x] Frontend stabilization updates completed:
  - Startup priority popup "View All Notifications" flow fixed (no longer immediately closes due outside-click race).
  - Auth form focus-outline issue reduced on active sign-in/register fields.
  - Product and Unit forms now submit whole-number multipliers to match backend data contract.
  - Unit multiplier inputs normalized to integer steps (`min=1`, `step=1`) across inline/add/bulk edit paths.
  - Cashier receipt printing moved to a compact thermal/POS slip format (80mm target) with clearer print output.
  - Receipt details now include the serving staff/cashier name.
  - Daily reconciliation summary now computes and returns payment-channel totals (Cash, POS/Card, Transfer) and paid invoice count.
  - Running daily reconciliation in Settings now auto-opens a receipt-like reconciliation print slip and keeps a manual reprint button.

### Validation snapshot
- [x] Backend compile check passed: `cd Backend && uv run python -m compileall -q app`
- [x] Frontend production build passed: `cd Frontend && npm run build`
- [~] `pytest` execution unavailable in current backend uv environment (`pytest` not installed in `.venv`).

---

## Work Order (Sequential)
1. ✅ **Login & Registration** - COMPLETED
2. ⏳ **UX Improvements** - IN PROGRESS (QA Reopened)
3. ⏳ **Invoice System** - IN PROGRESS
4. ⏳ **Products Management** - IN PROGRESS
5. ⏳ Analytics
6. ⏳ Reports
7. ✅ Settings (core complete; hardening follow-up pending)

## Ranked Implementation Priorities (Remaining Work)
1. [ ] **Deployment, observability, and backup readiness** (Section 10)
   - Finish production deploy checklist/scripts, backup+restore drill, health monitoring, and demo reset mode.
   - [x] SQLite-dev/PostgreSQL-prod backend runtime split completed (env-driven DB URL + psycopg driver + docs/env updates).
   - [x] SQLite-era UUID schema hacks removed in models/services (`String(36)` UUID IDs replaced with portable UUID types) with PostgreSQL UUID conversion migration added.
   - [x] Backend now autoloads `Backend/.env`, so local PostgreSQL `PHARMAX_ENV`/`DATABASE_URL` settings are applied reliably at startup.
   - [x] Fixed PostgreSQL startup crash from duplicate `ix_stock_adjustments_product_id` metadata declaration.
   - [x] Enum-safe migration refactor completed (duplicate enum type creation eliminated across historical migrations).
   - [x] Fresh-schema PostgreSQL migration validation completed with `uv run alembic upgrade head` (clean schema pass).
2. [ ] **Final QA sign-off for core daily workflow** (Final UX wave, Sections 2 and 4)
   - Close browser/device sweep, role-based invoice walkthrough, and all reopened QA-pending UX items.
3. [ ] **Dashboard/Analytics/Reports QA closeout** (Sections 3, 6, 7)
   - Complete desktop/mobile visual QA and figma-reference styling verification.
4. [ ] **Reporting & compliance pack implementation** (Section 12)
   - Deliver printable period summaries, role-based export presets, reconciliation/credit bundles, and audit timeline views.
5. [ ] **Products workspace final refinements** (Section 5)
   - Finish advanced UI refinements after bulk-edit QA sign-off.
6. [ ] **Settings backend persistence hardening** (Section 8 follow-up)
   - Implement per-user settings persistence and admin policy endpoints.
7. [ ] **Post-launch medium roadmap** (Sections 13–18)
   - Speed target validation, daily automation, offline sync hardening, debtor/transfer accountability.
8. [ ] **Post-launch low roadmap** (Sections 19–21)
   - Smart assist features, safe AI assist, and team collaboration layer.

---

## UI MODERNIZATION PROGRAM (NEW)

- Direction confirmed: **Modern Clinical Green** (premium refresh, same PharmaX identity)
- Delivery mode: **Phased rollout**
- Canonical UI blueprint added: `docs/UI_MODERNIZATION_PLAN.md`

### Completed in current pass
- [x] Global token and semantic visual refresh in `Frontend/src/style.css`
- [x] Shared UI pattern consistency pass (cards/forms/filters/tables/states/badges/modals)
- [x] App shell and sidebar modernization (`Frontend/src/layouts/AppShell.vue`, `Frontend/src/components/SideNav.vue`)
- [x] Auth + dashboard modernization (`Frontend/src/views/AuthView.vue`, `Frontend/src/views/DashboardView.vue`)
- [x] Invoice + cashier modernization including invoice details (`Frontend/src/views/InvoiceCreateView.vue`, `Frontend/src/views/InvoiceListView.vue`, `Frontend/src/views/CashierView.vue`, `Frontend/src/views/InvoiceDetailView.vue`)
- [x] Inventory modernization (`Frontend/src/views/ProductsView.vue`, `Frontend/src/views/ProductUnitsView.vue`, `Frontend/src/views/StockView.vue`, `Frontend/src/views/reports/ReportStockOutView.vue`, `Frontend/src/views/reports/ReportStockSummaryView.vue`)
- [x] Analytics modernization (`Frontend/src/views/AnalyticsView.vue` and all analytics child pages)
- [x] Reports modernization (`Frontend/src/views/ReportsView.vue` and all report child pages)
- [x] Team & Access + Settings modernization (`Frontend/src/views/TeamAccessView.vue`, `Frontend/src/views/SettingsView.vue`)
- [x] Activity logs modernization (`Frontend/src/views/ActivityLogsView.vue`)

### Program records updated
- [x] `docs/UI_MODERNIZATION_PLAN.md` created
- [x] `copilot-instructions.md` linked to UI modernization contract
- [x] `agents/developer-workflows/CENTRAL_CONTEXT.md` linked to UI modernization contract
- [x] `docs/implementation.md` updated with modernization run evidence

### Remaining in program
- [x] Responsive + accessibility hardening sweep (`ui-responsive-a11y-hardening`)

### Final UX polish wave (April 5, 2026)
- [x] Analytics + Reports switched to **sidebar-only navigation** (removed in-page jump wrappers/quick links)
- [x] Report/analytics top sections compacted to remove repeated title/description clutter
- [x] Removed assistant-style phrasing from analytics/report user-facing copy
- [x] Products + Units now support row double-click bulk selection with stronger selected-row highlight
- [x] Selection persistence fixed during search/filter in bulk edit flows
- [x] Units & Pricing controls refined (price keeps operational step sizing; multiplier now whole-number only for data-contract safety)
- [x] Sidebar defaults to collapsed on first load
- [x] Collapsed grouped sidebar supports double-click expansion behavior
- [x] Global shell/page spacing tightened to reduce wasted whitespace
- [x] Responsive + accessibility hardening sweep completed (focus visibility, touch targets, reduced-motion/chart behavior, contrast token alignment)
- [~] Final browser/device QA sweep pending before deployment freeze

---

## 1. LOGIN & REGISTRATION ✅

### Completed:
- [x] Full-screen split landing page (left: teal branding, right: auth buttons)
- [x] Removed redundant "Request Access" button - now just "Sign In" and "Quick PIN"
- [x] Proper footer with black background and contact info (email, LinkedIn)
- [x] Login/Register tabs with back button to landing
- [x] PIN login with clean keypad interface
- [x] Registration form - autocomplete disabled, single-column layout
- [x] Mobile responsive design

### Files Changed:
- `Frontend/src/views/AuthView.vue` - Complete redesign
- `Frontend/src/router/index.js` - Updated to use AuthView

### Note:
Pharmax is PERSONAL SOFTWARE for ONE pharmacy only. Not a SaaS product.

---

## 2. UX IMPROVEMENTS ⏳

### Completed:
- [x] **Toast Notification System** - Modern non-blocking toasts replace alert()
  - Files: `Frontend/src/composables/useToast.js`, `Frontend/src/components/ToastNotification.vue`
  - Added to `App.vue` for global access
  - Success, error, warning, info types with animations

- [x] **Profile Dropdown Fix** - Closes on outside click
  - File: `Frontend/src/layouts/AppShell.vue`
  - Added click outside detection with event listeners

- [x] **Collapsible Navbar**
  - Files: `Frontend/src/layouts/AppShell.vue`, `Frontend/src/components/SideNav.vue`
  - Toggle button in header
  - Smooth width transitions (260px ↔ 72px)
  - Page content adjusts automatically

- [x] **Navbar Search (Cmd+K)**
  - File: `Frontend/src/components/SideNav.vue`
  - Command palette style modal
  - Searches all nav items by name, section, parent
  - Keyboard shortcut: ⌘K / Ctrl+K
  - Beautiful animations and results display

- [x] **Navbar Hover Effects**
  - Enhanced hover states with color transitions
  - Active route highlighting with teal accent
  - Icon color changes on interaction

- [x] **Smart Search - Invoice List**
  - File: `Frontend/src/views/InvoiceListView.vue`
  - Search by: name, ID, status, payment method, amount, date
  - Example: typing "1000" finds invoices with ₦1000
  - Example: typing "cash" finds all cash payments

- [x] **Invoice List Alignment**
  - File: `Frontend/src/views/InvoiceListView.vue`
  - Fixed filters bar - grid layout for proper alignment
  - Search bar takes 2fr, other filters take 1fr each

- [x] **Stock Adjustment Search**
  - File: `Frontend/src/views/StockView.vue`
  - Added debounced search (300ms)
  - Searches by product name, brand, generic, SKU

### Reopened / QA Pending:
- [~] **Invoice Queue Layout Density (Implemented, QA Pending)**
  - File: `Frontend/src/views/CashierView.vue`
  - Reduced compact invoice dead space for small item counts
  - Kept totals + stamp actions anchored in bottom-right footer cluster

- [~] **Invoice Create Checkout Alignment (Implemented, QA Pending)**
  - File: `Frontend/src/views/InvoiceCreateView.vue`
  - Added compact mode for low item count invoices
  - Preserved bottom-right totals + "Send to Cashier" alignment with reduced vertical gaps

- [~] **Landing Footer Polish (Implemented, QA Pending)**
  - File: `Frontend/src/views/AuthView.vue`
  - Improved footer hierarchy, support labeling, and access list presentation

- [~] **Design Mirror Rebuild in `pharmax.pen` (Implemented, Review Pending)**
  - File: `pharmax.pen`
  - Cleared legacy canvas and rebuilt key screens to mirror current UI structure
  - Included updated Landing, App Dashboard, Invoice Create, Cashier, and Products screens

- [~] **Global Nav UX Upgrade (Implemented, QA Pending)**
  - Files: `Frontend/src/components/SideNav.vue`, `Frontend/src/layouts/AppShell.vue`
  - Upgraded command palette responsiveness (instant focus, keyboard navigation)
  - Improved sidebar collapse/toggle quality with compact rail behavior
  - Added sidebar collapsed-state persistence for better continuity

- [~] **Landing Footer Full-Width Layout (Implemented, QA Pending)**
  - File: `Frontend/src/views/AuthView.vue`
  - Footer now spans the entire landing width and aligns in a proper bottom bar layout
  - Improved footer spacing, hierarchy, and support-link presentation

- [~] **Phase 2 — Cashier & Invoice Density Pass (Implemented, QA Pending)**
  - Files: `Frontend/src/views/CashierView.vue`, `Frontend/src/views/InvoiceCreateView.vue`
  - Cashier queue now has search + status filters for faster picking under load
  - Invoice details/payment panel spacing tightened for low-item invoices and bottom-right action focus
  - Invoice create search now supports immediate focus (F2), enter-to-add, and outside-click close behavior

- [~] **Phase 2 — Inventory Workspace Surface (Implemented, QA Pending)**
  - File: `Frontend/src/views/ProductsView.vue`
  - Added visible product metrics band (total, active, low stock, out-of-stock)
  - Improved at-a-glance inventory signal before table scanning

### Files Changed:
- `Frontend/src/composables/useToast.js` - NEW
- `Frontend/src/components/ToastNotification.vue` - NEW
- `Frontend/src/App.vue` - Added ToastNotification
- `Frontend/src/layouts/AppShell.vue` - Profile fix, collapsible sidebar
- `Frontend/src/components/SideNav.vue` - Search modal, hover effects
- `Frontend/src/views/InvoiceCreateView.vue` - Checkout layout revised (QA pending)
- `Frontend/src/views/CashierView.vue` - Invoice queue/payment footer compaction pass
- `Frontend/src/views/AuthView.vue` - Landing footer structure redesign pass
- `Frontend/src/views/InvoiceListView.vue` - Smart search, alignment
- `Frontend/src/views/StockView.vue` - Debounced search
- `pharmax.pen` - Rebuilt UI mirror screens from current application

## 3. DASHBOARD
- [x] Metrics endpoint functional - `/dashboard/metrics`
- Note: Metrics show 0 until invoices are created (expected behavior)
- [~] Figma-inspired chart analytics pass implemented
  - Added interactive range switch (7D / 30D / 90D / All) and refresh control
  - Added richer visual chart widgets: revenue trend (line/area), status mix ring, payment distribution bars
  - Migrated chart rendering to `vue-echarts + echarts` for interactive tooltip/hover behavior
  - Preserved operational tables (recent invoices + low stock) and responsive behavior
  - Pending: browser visual QA against figma-reference styling details
- [x] Topbar "Today" metric reliability fix
  - Backend status normalization now handles enum values correctly for paid revenue
  - App shell now force-refreshes dashboard metrics periodically to avoid stale 0-value display

---

## 4. INVOICE SYSTEM ⏳

### Fixed Issues:
- [x] Field mapping: `unit_id` → `product_unit_id` in frontend
- [x] Added `unit_price` to invoice item submission
- [x] STAFF navigation: now goes to /invoices instead of /cashier
- [x] Products API now returns `selling_price` field
- [x] Fixed error handling: properly extracts error message from different formats
- [x] Fixed productsService.list() call - was passing wrong params
- [x] Added getUnits() method to products service
- [x] Fixed unit price field: `price_per_unit` (not `selling_price`)
- [x] Fixed unit name field: `name` (not `unit_name`)
- [x] Fixed brand field: `brand_name` (not `brand`)
- [x] Fixed default unit check: `is_default` (not `is_base`)

### Remaining Issues:
- [~] Test complete workflow with real data (Automated pass, manual UI pass pending)
  - Automated smoke verification passed across ADMIN/STAFF/CASHIER lifecycle
  - Verified create/add (ADMIN/STAFF), finalize/cancel (CASHIER), and role restrictions
  - Manual visual UI role-by-role walkthrough still pending in browser

### Files Changed:
- `Frontend/src/views/InvoiceCreateView.vue` - Multiple field name fixes
- `Frontend/src/services/products.js` - Added getUnits() method
- `Backend/app/api/routes/products_route.py` - Added selling_price to responses
- `Backend/app/schemas/product_schema.py` - Added selling_price field

---

## 5. PRODUCTS MANAGEMENT ⏳
- [x] Search functionality active (name, brand, generic)
- [x] Pagination and filtering working
- [~] Bulk edit workflow redesigned to queue-based one-by-one editing (implemented, QA pending)
  - Product bulk edit now opens a queue modal and lets users edit selected products one-by-one using the same fields as single-product edit.
  - Bulk button now highlights with accent background when selections exist.
- [ ] Advanced UI refinements pending

---

## 6. ANALYTICS
- [~] Advanced analytics implementation in progress
  - New backend endpoint: `GET /dashboard/analytics` with role-aware scope and query contract controls
    - `range_days`, `trend_granularity` (day/week/month), `top_n`, `staff_limit`, `invoice_limit`, `include_context`, optional `sold_by_id`
  - Status wording alignment in analytics payloads: `FINALIZED` displayed as `STAMPED`
  - KPI insights added: best selling product, highest invoice, top staff seller, most common product (today/week)
  - Added contextual KPI deltas (current range vs previous range) for better benchmark awareness
  - Added richer analytics visuals with interactive `vue-echarts` charts (trend, status mix, payment mix, top products)
  - Added top tables: products, staff performance, highest-value invoices
  - Added export + print actions (CSV export and browser print from Analytics view)
  - Dedicated analytics child pages active:
    - Analytics Overview
    - Revenue Trend Analysis
    - Product Insights
    - Staff Performance Analysis
    - Payment Insights
  - Navigation pattern now finalized as **sidebar-only** with compact page headers (no in-page jump wrappers)
  - Per-page export CSV + print actions remain available on analytics child pages
  - Revenue Trend page fully redesigned (new KPI cards, trend chart, quick insights, daily breakdown)
  - Product Insights page fully redesigned (fast/slow mover table, stock risk watch, movement timeline, plain-language action hints)
  - Analytics labels updated from "Product Movement Analysis" to "Product Insights" for easier understanding
  - Pending: browser visual QA on desktop + mobile breakpoints

---

## 7. REPORTS
- [~] Initial reports screen implemented
  - New `Reports` route and role access (ADMIN/CASHIER)
  - Added backend endpoint: `GET /dashboard/reports?range_days=`
  - Reports view now display-only (frontend no longer computes KPIs from bulk invoice list)
  - Invoice status summary, low-stock report, credit invoice section now served from backend payload
  - Status wording aligned to `STAMPED` in frontend report summaries and backend report payload
  - Added print/export workflow (CSV export and browser print from Reports view)
  - Dedicated report pages active:
    - Reports Overview
    - Stock Out Report
    - Stock Report
    - Highest Invoice Report
    - Product Sales Report
    - Expiring Drugs Report (placeholder pending backend expiry field)
  - Navigation pattern now finalized as **sidebar-only** with compact page headers (no in-page jump wrappers)
  - Per-page export CSV + print actions remain available on report child pages (except expiry placeholder)
  - Pending: browser visual QA on desktop + mobile breakpoints

---

## 8. SETTINGS
- [x] Settings phase completed (figma-inspired + beginner-friendly)
  - Profile & Account: name, phone, avatar, password/PIN update with plain-language help text
  - Pharmacy Preferences: receipt footer, currency, tax toggle, invoice wording, print defaults
  - Workflow Defaults: default payment method, queue behavior, low-stock alert thresholds
  - Accessibility Options: font-size preset, high contrast mode, reduced motion, simplified labels
  - Safety Controls: session timeout, auto-lock, role-based approval toggles (where applicable)
  - Implemented in app: route-based settings sections (`/settings/profile|pharmacy|workflow|accessibility|safety`) with section dropdown + quick section switcher
  - Side navigation now exposes Settings as a dropdown group with one-click links to each settings section
  - Persisted local device settings store, cashier defaults integration, and app-level accessibility + auto-lock hooks
  - Remaining hardening (backend per-user persistence + admin policy endpoints) tracked under operations/security phases

---

## 9. OPERATIONS HARDENING
- [x] Security + process integrity (phase completed)
  - [x] Stock adjustment approval workflow (non-admin requests require admin approval)
  - [x] Invoice void/cancel reason hardening + audit review panel
    - Cancel reason now required in cashier/invoices UI and enforced in backend cancel endpoint body schema
    - Cancellation reason is persisted in audit log details for traceability
  - [x] Queue safety hardening for walk-ins: pickup-code-first lookup and auto-open flow for newly sent invoices
  - [x] Daily reconciliation lock (prevent post-close transaction edits after 10:00 PM or prior business dates)
  - [x] Stronger role policy test matrix (ADMIN/CASHIER/STAFF)
    - Added dedicated route-policy smoke matrix script: `Backend/tests/test_role_policy_matrix.py`

---

## 10. DEPLOYMENT, OBSERVABILITY & DEMO READINESS
### PRIORITY: HIGH
- [ ] Production and presentation readiness
  - Deployment runbook prepared: `docs/POSTGRES_DEPLOYMENT_RUNBOOK.md` (PostgreSQL migration + deployment + QA sign-off)
  - Deployment scripts + environment checklist
  - Automated backups and restore test run
  - Error monitoring + health dashboard
  - Demo script mode for stable walkthroughs (clean sample data reset)

---

## 11. ACCESSIBILITY & ADOPTION
### PRIORITY: HIGH
- [x] Improve usability for low computer-literacy users (phase completed)
  - [x] Plain-language copy pass across key day-to-day actions
    - Invoice and cashier action feedback now uses direct guidance-style wording instead of technical/system wording.
    - After-hours invoice restriction now shows a clear human-readable warning: cashier/staff must ask an admin after 10:00 PM.
  - [x] Team & Access workspace delivered for practical admin operations
    - Admin `/users` workspace supports account creation, role/status updates, password/PIN reset, and task tracking.
    - Team activity timeline (`/users/activity`) and task page (`/users/tasks`) are route-synced for simpler navigation.
    - Presence status (online/offline + last seen) added to reduce handoff confusion.
  - [x] Navigation simplification pass completed
    - Removed redundant Reports Center entry from side nav.
    - Added Priority Notifications under Settings navigation for quick discovery.
    - Settings visibility now follows role and context: cashier/staff can access basic sections without admin-only clutter.
  - [x] Error and recovery messaging hardened
    - Registration pending-approval flow now returns explicit action-focused messages.
    - Invoice create/cancel/dispense failures now surface actionable next steps instead of silent/ambiguous failure.
  - [x] Touch-first and readability polish applied on active operational screens
    - Dark-mode contrast fixes shipped on Team & Access and Stock views.
    - Priority alerts and cashier notes are now visually prominent and easier to process quickly.
  - [x] Report printing usability upgraded for layman operators
    - Report print actions now produce structured printable documents with title, report period/date, printed-by user, and clear tables.
    - Removed screenshot-style output for report printing to support real-world handover and audit review.

---

## 12. REPORTING & COMPLIANCE PACK
### PRIORITY: HIGH
- [~] Professional reporting package for operations + academic demo (phase started)
  - Kickoff started: phase marked active and queued for implementation after current QA pass.
  - Printable daily/weekly/monthly summary templates
  - Export presets (CSV/PDF-ready layouts) per role
  - Reconciliation and credit outstanding report bundles
  - Audit-friendly transaction timeline views
  - Future phase: enforce daily sales closure by 10:00 PM and auto-generate/send End of Day reports after close

---

## 13. FUTURE PHASE — SPEED-RUN SALES WORKFLOW (<=15s)
### PRIORITY: MEDIUM
- [ ] Benchmark and enforce a **<=15s** default sales path for repeat/common purchases
  - Keyboard-only flow: search -> add -> qty -> send to cashier
  - Top-items memory cache + instant recall
  - Barcode-first fast add path
  - Real-time flow timer instrumentation (capture p50/p90 checkout speed)

## 14. FUTURE PHASE — DAILY AUTOMATION ENGINE
### PRIORITY: MEDIUM
- [ ] Midnight close automation and scheduled operational jobs
  - Auto-generate End-of-Day summary bundle (cash/transfer/POS split)
  - Auto-export archival package (CSV/PDF where applicable)
  - Auto-backup DB snapshots with retention policy and restore checks

## 15. FUTURE PHASE — OFFLINE RESILIENCE + SYNC
### PRIORITY: MEDIUM
- [ ] Harden local-offline behavior for unstable connectivity windows
  - Local draft queue with deterministic replay
  - Conflict-safe one-way/optional mirror sync strategy
  - Recovery dashboard for failed sync/print/export jobs

## 16. FUTURE PHASE — CREDIT/DEBTOR OPERATIONS
### PRIORITY: MEDIUM
- [ ] Full debtor workflow from invoice to settlement
  - Debtor profile + aging buckets + partial repayments
  - Reminder engine priority chain: WhatsApp -> SMS -> Email
  - Action log for every reminder, retry, and settlement update

## 17. FUTURE PHASE — SALES REP + TRANSFER ACCOUNTABILITY
### PRIORITY: MEDIUM
- [ ] Add dedicated rep and handoff accounting workflows
  - Sales rep credit withdrawals/returns
  - Transfer logs between sales desk and cashier desk
  - Reconciliation report linking invoice/payment/transfer timelines

## 18. LEGACY BLUEPRINT EXTRACTION (from `phase1.txt` + `PHASES.txt`)
### PRIORITY: MEDIUM

### What is already implemented (mapped to early blueprint)
- [x] Role-based users and auth (ADMIN/CASHIER/STAFF)
- [x] Product + inventory management with stock adjustment trail
- [x] Invoice lifecycle with cashier-side payment confirmation flow
- [x] Core reports/analytics foundation with export + print actions
- [x] Local-first architecture (LAN-friendly deployment model)

### Partially implemented / needs hardening
- [~] Speed-first invoicing workflow exists, but hard performance target still pending validation
  - Required target from original intent: complete common sale path in **15 seconds or less**
- [~] Receipt flow exists, but printer automation hardening (ESC/POS service reliability) remains
- [~] Daily summary/reporting exists, but full midnight automation pipeline is pending
- [~] Offline-first behavior exists at local-hosted level, but robust draft-sync/queue semantics still pending

### Not implemented yet (from early blueprint)
- [ ] Debtor/credit lifecycle (aging, partial repayment tracking, reminder orchestration)
- [ ] Sales rep partner ledger (withdrawals/returns/credit accountability)
- [ ] Transfer-log workflow between sales/cashier as first-class reportable object
- [ ] AI-assisted suggestions/substitutes with human verification UX
- [ ] Cloud mirror sync and formal backup retention automation

---

## 19. SMART ASSIST FEATURES (FINAL-YEAR INNOVATION)
### PRIORITY: LOW
- [~] Practical innovation without adding user complexity (phase started)
  - Kickoff started: phase marked active with implementation sequencing prepared behind reporting/compliance deliverables.
  - Natural-language insights panel ("What sold most this week?")
  - Slow/fast moving stock suggestions from transaction trends
  - Early anomaly hints (spikes, unusual cancellations, unusual stock drains)
  - Safe recommendation UX: suggestions only, no silent auto-actions

## 20. FUTURE PHASE — SAFE AI ASSIST
### PRIORITY: LOW
- [ ] Introduce AI as assistive (non-autonomous) layer
  - Substitution suggestions from explicit mappings + usage trends
  - Optional prescription OCR intake (human confirmation required)
  - No silent auto-actions on billing, stock, or clinical choices

## 21. FUTURE PHASE — TEAM COLLABORATION & SOCIAL LAYER
### PRIORITY: LOW
- [ ] Add low-friction internal collaboration once operations core is stable
  - Presence-aware handoff view (who is online, busy, or recently active)
  - Lightweight team notes on invoices/tasks (internal-only)
  - Mentions + assignment queue for cashier/sales coordination
  - Strict auditability and role controls for all collaboration actions

---

## Database Status
- 3,000 products seeded with real prices
- 5,347 pricing units (each product has 1-3 units)
- Users: admin, cashier, staff

## Credentials

Demo credentials existed in the source project notes but are intentionally redacted in this FRAME fixture snapshot.
Use environment variables or local-only seed data when exercising the fixture.

---

## Recent Session Summary (March 7, 2026 PM)

### Major Improvements:
1. **Landing Page Redesign** - Full-screen split layout, proper footer with contacts
2. **Toast System** - Replaced all alert() calls with beautiful toasts
3. **UX Fixes** - Profile dropdown, collapsible navbar, checkout-style invoice
4. **Search Enhancements** - Smart search in invoices, products, stock
5. **Visual Polish** - Hover effects, transitions, proper alignment

### Next Priority:
- Complete invoice workflow testing
- Apply figma-reference styling patterns (fonts, tables, spacing)
- Analytics & Reports sections
