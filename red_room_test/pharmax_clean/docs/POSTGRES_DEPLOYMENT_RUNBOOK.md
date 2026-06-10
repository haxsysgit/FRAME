# Pharmax PostgreSQL Deployment Runbook (Priority 1 and 2)

This is the recommended step-by-step path to:
1. move Pharmax from SQLite to PostgreSQL, and
2. finish final backend/frontend deployment readiness and sign-off QA.

This runbook is optimized for your current stack and hosting model (**Render**).

---

## 0) Deployment strategy (recommended)

Use this architecture:
- **Render Web Service** for Backend (`Backend`)
- **Render Static Site** for Frontend (`Frontend`)
- **Render Managed PostgreSQL** for production DB

Why this is best here:
- Your repo already has `render.yaml`.
- Managed PostgreSQL gives backups, connection URL, and easier operations.
- Keeps backend/frontend split clean and scalable.

---

## 1) Pre-migration safety checklist

Do this before changing DB:

1. Freeze active edits in a branch.
2. Back up current SQLite DB file:
   - `Backend/app/_db/pharmax.db`
3. Export critical tables (users, products, invoices) to CSV/SQL.
4. Confirm current migration head:
   - `cd Backend && alembic current`
5. Confirm app builds and starts on current branch.

---

## 2) Backend code changes required for PostgreSQL

These are the exact production-readiness changes to apply first.

## 2.1 Add PostgreSQL driver dependency

In `Backend/pyproject.toml`, add:
- `psycopg[binary]` (or `psycopg2-binary`; psycopg is preferred).

Then install/sync dependencies.

## 2.2 Make DB URL environment-driven

Update `Backend/app/core/config.py` so `DATABASE_URL` is:

1. `PHARMAX_DATABASE_URL` if set
2. otherwise fallback to SQLite for local dev

Target behavior:
- local dev works without extra setup
- production uses Postgres by env only (no code edits per environment)

## 2.3 Make SQLAlchemy engine DB-aware

In `Backend/app/db/session.py`:

- Apply SQLite-only `connect_args={"check_same_thread": False}` **only** when URL starts with `sqlite`.
- For PostgreSQL, create engine without SQLite connect args.
- Keep `pool_pre_ping=True` for reliability.

## 2.4 Keep Alembic URL source aligned

`Backend/alembic/env.py` already reads `DATABASE_URL`. Keep this pattern.

For deploys, always run:
- `alembic upgrade head`

before app traffic is served.

## 2.5 CORS hardening for production

In `Backend/app/main.py`, stop using wildcard CORS in production.

Use `CORS_ORIGINS` from config so only your deployed frontend domain is allowed.

---

## 3) Render configuration (best-practice setup)

## 3.1 Add PostgreSQL service in Render

Create managed PostgreSQL in Render and copy the internal connection URL.

Use env var:
- `PHARMAX_DATABASE_URL=<postgres-url>`

## 3.2 Backend service env vars (required)

Set on Render backend service:
- `PHARMAX_DATABASE_URL`
- `PHARMAX_SECRET_KEY`
- `PHARMAX_ADMIN_PASSWORD`
- `PHARMAX_CASHIER_PASSWORD`
- `PHARMAX_STAFF_PASSWORD`
- `PHARMAX_CASHIER_PIN`
- `PHARMAX_STAFF_PIN`
- `PHARMAX_JWT_ALGORITHM=HS256`
- `PHARMAX_ACCESS_TOKEN_EXPIRE_MINUTES=30`
- `PHARMAX_CORS_ORIGINS=<your-frontend-domain>`

## 3.3 Frontend env vars (required)

Set on Render frontend service:
- `VITE_API_URL=https://<your-backend-domain>`
- `VITE_API_TIMEOUT_MS=20000`

## 3.4 Migrations on deploy

Best pattern:
1. Build backend
2. Run `alembic upgrade head`
3. Start app

If using Render release command support, place Alembic migration there.

---

## 4) Data migration plan (SQLite -> PostgreSQL)

Choose one:

## Option A (clean production start, fastest)

1. Deploy with PostgreSQL.
2. Run migrations (`alembic upgrade head`).
3. Seed required users/products from approved source.
4. Go live without historical SQLite import.

Use when historical data is not required.

## Option B (preserve existing historical data)

1. Freeze writes on old system.
2. Migrate schema to PostgreSQL via Alembic.
3. Import data table-by-table (users -> products -> units -> invoices -> invoice_items -> logs).
4. Verify row counts and totals before cutover.

Use when old invoices/stock history must remain.

---

## 5) Priority 1 final deployment hardening checklist

Complete this before public cutover:

1. Health checks
   - Backend `/` responds 200.
   - Frontend loads and calls API successfully.
2. Secrets
   - No default passwords or placeholder secret key.
3. Backups
   - Confirm Render PostgreSQL backup policy.
   - Test one restore on staging (or dry-run procedure).
4. Observability
   - Capture backend logs and error traces.
   - Confirm failed API requests are visible in logs.
5. Performance sanity
   - Test invoice create -> cashier queue path under realistic load.

---

## 6) Priority 2 QA sign-off checklist (frontend + backend)

Run role-based QA in production-like environment:

1. **ADMIN**
   - create/edit products and units
   - view stock out/low stock pages
   - run reports and print/export
2. **CASHIER**
   - open cashier queue
   - stamp/finalize allowed invoices
   - verify lock-window rules
3. **STAFF**
   - create invoices
   - restricted actions behave correctly
4. **Cross-surface consistency**
   - Dashboard out-of-stock count matches out-of-stock queue
   - notifications point to correct stock surfaces
5. **UI checks**
   - mobile/tablet/desktop layout
   - focus states, touch targets, reduced motion behavior

Sign off only when all pass.

---

## 7) Cutover sequence (recommended)

1. Deploy backend with PostgreSQL env vars.
2. Run migrations (`alembic upgrade head`).
3. Verify backend health endpoint.
4. Deploy frontend with correct `VITE_API_URL`.
5. Run smoke tests (admin/cashier/staff core workflow).
6. Monitor logs for first live transactions.

---

## 8) Rollback plan

If deployment fails:

1. Re-point frontend `VITE_API_URL` to last stable backend.
2. Restore previous backend release on Render.
3. If needed, restore PostgreSQL from latest snapshot.
4. Keep incident notes and fix forward on staging branch.

---

## 9) What to implement first (execution order)

Use this exact order:

1. DB config + engine portability changes (Section 2.2, 2.3)
2. Add PostgreSQL driver (Section 2.1)
3. CORS production hardening (Section 2.5)
4. Render env + migration pipeline (Section 3)
5. Data migration option selection (Section 4)
6. Priority 1 hardening checks (Section 5)
7. Priority 2 QA sign-off (Section 6)

