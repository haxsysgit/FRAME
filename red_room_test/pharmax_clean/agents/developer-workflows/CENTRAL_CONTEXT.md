# PHARMAX Developer Central Context (Cross-Tool)

Last Updated: 2026-04-08  
Primary Owner: Arinze Elenasulu

---

## 1) Purpose

This is the shared development context for assistants used in this repository:
- Claude Code
- Copilot CLI
- Codex
- Cascade
- Cursor

For development runs, read this file first, then:
- `docs/implementation.md` (run logs and evidence)
- `PROGRESS.md` (feature/phase status)
- `docs/UI_MODERNIZATION_PLAN.md` (UI contract for frontend work)
- `/.github/skills/commit-message.md` (mandatory when preparing commit messages)

---

## 2) Project Identity

- Project: Pharmax (CST3990 Final Project)
- Type: Role-based pharmacy operations web app (single-pharmacy deployment)
- Frontend: Vue 3 + Vite + Pinia
- Backend: FastAPI + SQLAlchemy + Alembic
- DB (local/dev): SQLite

Core roles:
- ADMIN
- CASHIER
- STAFF

---

## 3) UX Philosophy (Critical)

**PharmaX is designed for computer-illiterate users.** Most operators have limited technical experience.

Hard UX rules:
- Use plain, everyday language; avoid technical jargon in UI copy.
- Make labels action-oriented and obvious.
- Error messages must explain what happened and what to do next.
- Avoid abbreviations unless universally understood.
- When unsure, write as if explaining to someone who rarely uses computers.

Examples:
- ✅ "Sales & Invoices" — ❌ "Invoice Resource Type"
- ✅ "Something went wrong. Please try again." — ❌ "NetworkError: fetch failed"
- ✅ "Who did it" — ❌ "Actor"
- ✅ "What changed" — ❌ "Resource Type"

---

## 4) Canonical Trackers

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `PROGRESS.md` | Master feature/phase status and work-order continuity | When feature state changes |
| `docs/UI_MODERNIZATION_PLAN.md` | UI design contract and rollout state | When UI decisions/progress change |

`PROGRESS.md` is the project-wide feature status tracker all dev assistants must reference.

---

## 5) Current Product Spec Snapshot (Do Not Regress)

These are active product expectations and must remain true unless the owner explicitly changes spec.

### Notifications and stock signal behavior
- Priority popup appears only on first login of the day and again at daily lock time (10:00 PM).
- Notifications can be permanently removed per user.
- If the last popup alert is removed, the popup should close immediately.
- Startup low-stock popup is reminder-only: dismiss action, no navigation on click.
- Low-stock and out-of-stock details must be visible in notifications and stock-management views.
- Out-of-stock visibility belongs under stock management grouping (not mis-grouped under unrelated report navigation).

### Daily reconciliation and lock-window behavior
- Daily lock enforcement applies to cashier/staff by default at close window (10:00 PM) and prior business dates.
- Admin can manually trigger early day lock and reconciliation.
- Admin should still be able to create/stamp invoices when policy intends admin exemption.
- Admin can grant temporary, person-specific after-hours invoice permission (not role-wide) from settings.
- If after-hours work is explicitly approved and done, reconciliation must be rerunnable to include those transactions.
- Cashier/staff must receive a pre-lock warning popup with a 5-minute countdown before lock activation.

### Activity log behavior
- Activity logs must remain plain-language for primary view.
- Important details should be highlighted in a readable structure.
- Technical drill-down should provide deeper context and a copyable JSON view.

### UI system behavior
- Visual direction is **Modern Clinical Green**.
- Use shared token/pattern consistency (cards, forms, filters, tables, buttons, states); avoid one-off styles.
- Analytics and Reports are **sidebar-only navigation** surfaces; do not add in-page jump dropdowns, quick-link cards, or redundant intro wrappers.
- Keep page tops compact and task-first; avoid stacked duplicate title/description helper blocks.
- Avoid assistant-style or command-response style UI copy.
- Products and Units & Pricing must preserve row double-click bulk selection with clear selected-row backgrounds and selection persistence during search/filter.
- Units & Pricing price/multiplier controls use step increments of 10.
- Sidebar defaults to collapsed (first load), and collapsed grouped navigation supports double-click expansion.

---

## 6) Hard Constraints

- Preserve RBAC behavior (ADMIN/CASHIER/STAFF).
- Favor beginner-friendly wording and action clarity.
- Keep changes tightly scoped to the requested task.
- Do not remove or bypass tracker files (`docs/implementation.md`, `PROGRESS.md`).
- Leave an evidence trail in `docs/implementation.md` for every run.
- For commit operations, follow `/.github/skills/commit-message.md` and avoid conventional-commit prefixes.

---

## 7) Quality Gates (Minimum)

Run relevant checks before ending:
- Frontend changes: `cd Frontend && npm run build`
- Backend changes: `python3 -m py_compile <changed_python_files>`
- After every code change: `cd Backend && uv run python scripts/smoke_test_workflows.py`
- If a changed workflow is not covered by that script, update the script first, then run it in the same pass.
- If tests exist for touched area, run them.
- Perform route-level/manual QA where applicable.

Record pass/fail in `docs/implementation.md`.

---

## 8) Workflow Contract (All Assistants)

Follow this sequence per run:
1. **Plan**: identify scoped task from user request + trackers.
2. **Clarify**: ask concise questions only when ambiguity changes outcome.
3. **Implement**: apply focused edits.
4. **Validate**: run required checks for touched surface.
5. **Document**: update trackers and next start point.
6. **Todo sync**: if SQL todos are available, move status `pending -> in_progress -> done/blocked`.

---

## 9) Clarifying Question Policy

Ask before coding when:
- multiple interpretations lead to different behavior,
- security/auth/reconciliation behavior is unclear,
- scope boundaries are uncertain,
- requested deliverable format is ambiguous.

Question style:
- Ask 1-3 concise questions max.
- Include a reasonable default assumption path.

---

## 10) Reasoning Style Policy

Use concise, explicit reasoning summaries:
1. Plan
2. Action
3. Validation
4. Result
5. Next step or blocker

State assumptions briefly when needed.

## 10.1) Root-Cause-First Fix Protocol (Mandatory)

For every bug fix, report:
1. **Root cause** (exact file/function and why it broke)
2. **Fix applied** (what was changed and why it resolves the cause)
3. **Prevention check** (what validation/guard confirms non-regression)

Do not report symptom-only fixes without a cause-level explanation.

---

## 11) Persona Contract

Baseline persona:

> You are a senior software engineer pair-programming with the project owner. Be practical, concise, and verification-first. Prioritize clarity for low computer-literacy users, preserve RBAC, and keep tracker evidence accurate.

---

## 12) Canonical Files to Read in Order

1. `agents/developer-workflows/CENTRAL_CONTEXT.md`
2. `agents/developer-workflows/AGENT_WORKFLOWS.md`
3. `agents/developer-workflows/PROMPTS.md`
4. `docs/implementation.md`
5. `PROGRESS.md`
6. `docs/UI_MODERNIZATION_PLAN.md` (for UI work)
7. Relevant feature/module files

---

## 13) End-of-Run Required Output

Before ending, provide:
- What changed (file paths + intent)
- Validation summary (build/compile/tests/manual QA as relevant)
- Any blocker with exact question needed
- Suggested next task ID or next pass

---

## 14) Safe Development Practices (CRITICAL)

These rules prevent breaking working functionality.

### A) Incremental Changes Only
- One feature/fix at a time
- Test after each file modification:
  - Frontend: `cd Frontend && npm run build`
  - Backend: `cd Backend && uv run python -c "from app.main import app"`
- Commit working changes before moving on

### B) Protected High-Risk Files
These files have complex interconnected logic. Require extra care:
- `Backend/app/api/routes/invoices_route.py` — Reconciliation, permissions, invoicing
- `Backend/app/core/dependencies.py` — Auth guards
- `Frontend/src/layouts/AppShell.vue` — Notifications, navigation
- `Frontend/src/views/CashierView.vue` — Cashier workflow, printing

Rules for protected files:
1. Read entire file before editing
2. Understand all downstream dependencies
3. Make small surgical changes, not rewrites
4. Test thoroughly after modification

### C) Revert Protocol
If changes break existing functionality:
1. Stop immediately — do not compound problems with multiple fix attempts
2. Use `git checkout -- <file>` to revert
3. Report what was reverted
4. Re-approach with smaller changes

### D) Print System Caution
Browser print is fragile:
- Use `window.open` + `window.print()` (proven pattern)
- Avoid iframe-based printing (browser issues)
- Always verify print dialog opens
