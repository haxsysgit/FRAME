# Pharmax — Pharmacy Operations Platform

**Live App:** https://pharmax-0ez1.onrender.com
**API Base:** https://pharmax-api.onrender.com

Pharmax is a role-based pharmacy management system for day-to-day operations: inventory control, invoice workflow, cashier processing, reporting, team access, and auditable activity tracking.

---

## What this project is for

Pharmax is designed to replace manual pharmacy workflows with a fast, traceable, and structured digital process.

It supports three operational roles:

- **ADMIN**: configuration, user/access control, inventory governance, reporting
- **CASHIER**: payment handling, cashier queue, invoice completion
- **STAFF**: invoice creation and operational stock/inventory tasks

---

## Core capabilities

- JWT + PIN login flows
- Public registration request flow with **admin approval**
- Product master list and unit/price management
- Stock adjustment tracking with audit history
- Invoice lifecycle (draft, finalized/stamped, dispensed, cancelled)
- Team & access management (accounts, tasks, activity)
- Global Activity Logs with:
  - row click inspection
  - payload viewer
  - sort order
  - date range filtering
  - period-of-day filtering (morning/afternoon/evening/night)

---

## Tech stack

### Backend
- FastAPI
- SQLAlchemy
- Alembic
- SQLite (default)

### Frontend
- Vue 3
- Pinia
- Vue Router
- Vite

### Deployment
- Render (Blueprint-compatible via `render.yaml`)

---

## Repository layout

```text
Backend/      FastAPI app, models, services, routes, migrations, scripts
Frontend/     Vue application, views, components, stores, services
docs/         Implementation and project documentation
render.yaml   Render blueprint for backend + frontend
```

---

## Local setup

## 1) Backend

```bash
cd Backend
uv sync
cp .env.example .env
uv run fastapi dev main.py
```

Backend runs on `http://127.0.0.1:8000` by default.

## 2) Frontend

```bash
cd Frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173` by default.

---

## Environment notes

### Backend (`Backend/.env`)
Set at least:

- `PHARMAX_SECRET_KEY`
- `PHARMAX_ADMIN_PASSWORD`
- `PHARMAX_CASHIER_PASSWORD`
- `PHARMAX_STAFF_PASSWORD`
- `PHARMAX_CORS_ORIGINS`

### Frontend (`Frontend/.env`)
Set at least:

- `VITE_API_URL`
- `VITE_API_TIMEOUT_MS`

Render deterministic behavior:

- Keep local defaults in `Frontend/.env`
- Set `VITE_API_URL` and `VITE_API_TIMEOUT_MS` in Render service env vars
- Render env vars override `Frontend/.env` at build time

---

## Deployment (Render)

This repo includes a root `render.yaml` that defines:

- Python web service (`Backend`)
- Static frontend service (`Frontend/dist`) with SPA rewrites

Use Render Blueprint deploy and provide required secret env vars in Render dashboard.

---

## Important operational notes

- New public registrations are created as **inactive** and require admin activation.
- If login appears to hang, frontend now enforces request timeout and surfaces an actionable error.
- Keep production secrets only in environment variables (never commit `.env`).
- Ensure backend CORS includes the exact deployed frontend origin.

---

## License / Usage

Internal academic and operational project for Pharmax pharmacy workflows.
