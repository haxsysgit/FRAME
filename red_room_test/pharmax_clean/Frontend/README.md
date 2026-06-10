# Pharmax Frontend (Vue + Vite)

## Environment (single file)

Frontend now uses one canonical env file:

- `Frontend/.env`

Current local defaults:

- `VITE_API_URL=http://localhost:8000`
- `VITE_API_TIMEOUT_MS=20000`

Deterministic behavior:

- Local `npm run dev` / `npm run build` reads from `Frontend/.env`
- Render build uses service env vars from `render.yaml` / Render dashboard
- Render env vars override file values at build time

## Render frontend env vars

Set these in the Render static site service:

- `VITE_API_URL=https://pharmax-api.onrender.com`
- `VITE_API_TIMEOUT_MS=20000`
