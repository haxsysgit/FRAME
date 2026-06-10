# UI Modernization Plan (Modern Clinical Green)

Last Updated: 2026-04-05

## 1) Visual Direction

PharmaX uses a **Modern Clinical Green** theme:
- Keep the pharmacy identity (green-led interface)
- Increase polish with cleaner depth, better hierarchy, softer surfaces
- Improve readability and confidence for non-technical users

### Core Palette
- Primary: `#0F9F89`
- Primary Hover: `#0B8572`
- Secondary: `#21BA78`
- Canvas (Light): `#F4F8F7`
- Card (Light): `#FFFFFF`
- Canvas (Dark): `#0D1715`
- Card (Dark): `#162724`

## 2) UX Rules (Non-Negotiable)

1. Language must stay plain and action-focused.
2. Avoid assistant-style or command-response style wording in any user-facing UI copy.
3. Analytics and Reports must use sidebar-only navigation (no in-page jump wrappers/quick-link cards).
4. Keep page tops compact; avoid repeated title/description stacks that waste space.
5. Products and Units must preserve row double-click bulk selection with clear selected-row highlighting and search-safe selection persistence.
6. Units & Pricing numeric controls use step increments of 10 for multiplier/price editing.
7. Sidebar defaults to collapsed on first load; collapsed grouped navigation supports double-click expansion.
8. Keep spacing dense enough for daily operations while preserving readability.
9. Primary actions must be visually obvious and consistent.
10. Tables/forms must be easy to scan quickly.
11. States (error/success/warning/loading/empty) must be clear without technical wording.
12. Keep RBAC behavior unchanged while modernizing visuals.

## 3) Design System Upgrades

- Token refresh in `Frontend/src/style.css` (colors, borders, text hierarchy, shadows, semantic states)
- Surface consistency using shared visual patterns:
  - cards/panels
  - form controls
  - filter bars
  - tables
  - action buttons
  - badges and pills

## 4) Rollout Plan

1. Foundation (tokens + shared patterns)
2. App shell (`AppShell`, `SideNav`, top bar, notifications)
3. Page groups:
   - Auth
   - Dashboard
   - Invoices + Cashier
   - Inventory
   - Analytics
   - Reports
   - Team & Access + Settings
   - Activity Logs
4. Responsive/accessibility hardening
5. Documentation and tracker finalization

## 5) Progress Notes

- Foundation token refresh: **completed**
- Shared UI pattern consistency pass: **completed**
- Shell modernization: **completed**
- Auth + dashboard modernization: **completed**
- Invoice + cashier modernization (including invoice detail): **completed**
- Inventory modernization: **completed**
- Analytics modernization: **completed**
- Reports modernization: **completed**
- Team & Access + Settings modernization: **completed**
- Activity logs modernization: **completed**
- Final UX polish wave (header/nav trim, selection ergonomics, sidebar behavior, copy cleanup, spacing density): **completed**
- Responsive/accessibility hardening: **pending final sweep**

## 6) Record Files To Keep In Sync

- `docs/UI_MODERNIZATION_PLAN.md` (this file)
- `copilot-instructions.md`
- `agents/developer-workflows/CENTRAL_CONTEXT.md`
- `PROGRESS.md`
- `docs/implementation.md`
