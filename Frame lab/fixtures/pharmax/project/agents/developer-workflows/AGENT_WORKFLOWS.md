# Agent Workflows (Claude Code / Copilot CLI / Codex / Cascade / Cursor)

Last Updated: 2026-04-08

---

## 1) Why this file exists

This file standardizes execution behavior across assistants so context and quality remain stable when switching tools.

Use with:
- `agents/developer-workflows/CENTRAL_CONTEXT.md`
- `docs/implementation.md`
- `PROGRESS.md`
- `docs/UI_MODERNIZATION_PLAN.md` (UI tasks)
- `/.github/skills/commit-message.md` (when creating commits)

---

## 2) Universal Run Loop (Same for all tools)

1. Read `CENTRAL_CONTEXT.md` and confirm active product constraints.
2. Read `docs/implementation.md` for latest run history.
3. Read `PROGRESS.md` for current feature state.
4. Read `docs/UI_MODERNIZATION_PLAN.md` if touching UI.
5. Pick scoped task (or user-priority override).
6. If SQL todos are available, set task `in_progress` before coding.
7. Ask concise clarifying questions only if ambiguity changes behavior.
8. Implement focused changes only.
9. Run required validations.
   - Mandatory after every code change: `cd Backend && uv run python scripts/smoke_test_workflows.py`
   - If coverage is missing for a changed workflow, update that script and run it again in the same pass.
10. Update tracker docs (`docs/implementation.md`, and `PROGRESS.md` if feature status changed).
11. Update todo status to `done` or `blocked`.
12. If committing, apply `/.github/skills/commit-message.md` rules.
13. Provide concise handoff summary.

---

## 3) Persona Library

### A) Builder Persona
**Use when:** implementing features/fixes

> Focus on minimal, safe edits that preserve RBAC, reconciliation policies, and beginner-friendly UX clarity. Avoid unrelated refactors.

### B) QA Persona
**Use when:** validating stability/regressions

> Validate with build/compile/tests/manual route checks for touched scope only. Report reproducible findings with severity and exact repro steps.

### C) Handoff Persona
**Use when:** closing a run

> Write concise run notes, update trackers accurately, and name the exact next start point.

---

## 4) Clarifying Question Framework

Ask when uncertainty can change output behavior.

Format:
1. What is ambiguous
2. Why it changes implementation
3. Default assumption if no answer
4. Direct question

---

## 5) Validation Matrix

- **Any code touched** -> `cd Backend && uv run python scripts/smoke_test_workflows.py`
- **Frontend touched** -> `cd Frontend && npm run build`
- **Backend touched** -> `python3 -m py_compile <changed_python_files>`
- **Tests available for touched area** -> run them
- **Critical workflow changes** -> if smoke script misses coverage, extend script and rerun it

Record results in `docs/implementation.md`.

---

## 6) Non-Regression Checklist (Current Spec)

Before ending, confirm no accidental regressions in:
- Plain-language UI wording for low computer-literacy users
- Modern Clinical Green shared visual patterns
- No assistant-style/command-style copy in customer-facing UI text
- Analytics/Reports remain sidebar-only (no in-page jump nav or redundant intro wrappers)
- Reconciliation/lock-window and after-hours permission behavior
- Notification behavior (dismiss-only startup low-stock popup)
- Activity log readability + technical drill-down affordances
- Products/Units bulk-selection ergonomics (double-click row select, selected-row highlight, search-safe selection persistence)
- Sidebar first-load collapsed behavior and collapsed-mode double-click group expansion

---

## 7) Handoff Template (Copy/Paste)

Run Summary:
- Task IDs:
- Root cause(s):
- Fix applied:
- Prevention check:
- Files changed:
- Validation:
  - Build:
  - Compile:
  - Tests/Manual QA:
- Blockers/Questions:
- Next recommended start:
