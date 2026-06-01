# Developer Workflows Agent Pack

Last Updated: 2026-04-08

This folder is the shared operating contract for implementation-focused assistant runs across:
- Claude Code
- Copilot CLI
- Codex
- Cascade
- Cursor

## Read Order (Mandatory)

1. `agents/developer-workflows/CENTRAL_CONTEXT.md`
2. `agents/developer-workflows/AGENT_WORKFLOWS.md`
3. `agents/developer-workflows/PROMPTS.md`
4. `docs/implementation.md` (run history and evidence)
5. `PROGRESS.md` (feature/phase status)
6. `docs/UI_MODERNIZATION_PLAN.md` (required for UI changes)
7. `/.github/skills/commit-message.md` (required when creating commits)

## Current Spec Anchors

- UX wording must remain plain-language for low computer-literacy users.
- UI wording must not sound like assistant/tool responses.
- UI direction is **Modern Clinical Green** with shared token/pattern consistency.
- Analytics/Reports are sidebar-only navigation surfaces (no in-page jump nav wrappers).
- `PROGRESS.md` is the feature/phase tracker all development assistants must reference.
- Reconciliation, lock-window, and notification behavior in `CENTRAL_CONTEXT.md` is mandatory unless the owner explicitly changes spec.
- Root-cause-first fix reporting is mandatory: Root cause -> Fix applied -> Prevention check.
- After every code change, run `cd Backend && uv run python scripts/smoke_test_workflows.py` (or update the script first if coverage is missing).

## Maintenance Rule

When product direction changes, update this folder first, then reflect execution evidence in `docs/implementation.md` and feature status in `PROGRESS.md`.
