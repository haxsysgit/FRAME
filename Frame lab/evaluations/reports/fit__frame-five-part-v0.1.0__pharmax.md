# Fit report: frame-five-part-v0.1.0 / pharmax

Fixture: `/home/hax/FRAME/Frame lab/fixtures/pharmax/project`
Output: `/home/hax/FRAME/Frame lab/evaluations/fits/frame-five-part-v0.1.0/pharmax`
Schema version: `0.1.0`
Checked: `2026-06-01T21:53:45Z`

## What was fitted

Wrote the adjusted FRAME five-file representation:

- `facts.yaml` -- current project truth, project profile, source-truth ranking, architecture, workflow facts, and structural quirks.
- `rules.yaml` -- project instruction blueprint and command inventory only.
- `acts.yaml` -- checked fitting activity/handoff only; not baseline project representation.
- `map.yaml` -- repository context map for frontend/backend/docs/data/generated boundaries.
- `expect.yaml` -- correctness contract with `verify` entries using `command_ref` into `rules.commands`.

## Project shape found

Pharmax is a medium-sized full-stack pharmacy operations app:

- Backend: FastAPI, SQLAlchemy, Alembic, uv, JWT/PIN auth, SQLAdmin, receipt/printing support, SQLite default with production PostgreSQL support.
- Frontend: Vue 3, Pinia, Vue Router, Vite/Rolldown Vite, Vuestic UI, ECharts.
- Core workflows: role-based access, product catalog/units/pricing, stock adjustments, invoice create/add/finalize/dispense/cancel/return, cashier desk, reconciliation/after-hours access, dashboard/reports/analytics, activity logs.
- Verification surfaces: backend no-server workflow smoke script, server-backed invoice/RBAC scripts, frontend build/preview commands, migrations, seed/import scripts.

## Schema-intent coverage

- `facts.project_profile` summarizes app family, system role, and medium complexity.
- `facts.structural_quirks` captures import namespace surprise, STAFF/SALES drift, DB/docs drift, generated artifact noise, and missing render.yaml claim.
- `facts.source_truth` ranks runtime source and executable scripts above docs and generated artifacts.
- `rules.commands` is a command inventory without duplicating expectation prose.
- `expect.verify` uses `command_ref` for runnable commands and `null` only for review-only checks.
- `acts.yaml` records only inspected/written/validated activity and handoff state.

## Friction found

1. Backend import namespace surprise: source imports `example_projects.pharmax.Backend...` while the fixture path is `Frame lab/fixtures/pharmax/project`. Backend commands may need the prepared package namespace/PYTHONPATH to run outside this fixture harness.
2. Role naming drift: README/current app intent uses `STAFF`, while an older RBAC script uses `SALES` in registrations and expectations.
3. Documentation drift: README/code indicate SQLite default with production PostgreSQL support; PROJECT_BRIEF lists PostgreSQL and Streamlit analytics as if canonical.
4. Generated/state noise is committed in fixture: `Frontend/node_modules`, `Frontend/dist`, `Backend/.venv`, `__pycache__`, `.pytest_cache`, `.env`, and `Backend/app/_db/pharmax.db` can swamp mapping/search.
5. README mentions root `render.yaml`, but it was not present in the inspected fixture file listing.
6. Frontend has no declared lint/test command; build is the only package-level static verification command.

## Validation note

The fit was written against `/home/hax/FRAME/schemas/*.schema.yaml` for FRAME `0.1.0`; a follow-up schema validation pass was run after writing and schema issues were corrected.
