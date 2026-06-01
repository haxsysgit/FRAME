# Prompt Templates (Developer Workflow Bootstrap)

Last Updated: 2026-04-08

---

## 1) Universal Bootstrap (any assistant)

Use this at the start of development runs:

```text
Read and follow these files in order:
1) agents/developer-workflows/CENTRAL_CONTEXT.md
2) agents/developer-workflows/AGENT_WORKFLOWS.md
3) docs/implementation.md
4) PROGRESS.md
5) docs/UI_MODERNIZATION_PLAN.md (if UI is touched)
6) /.github/skills/commit-message.md (if a commit is requested)

Task for this run: <TASK_ID or scope>

Operating rules:
- Use Builder Persona unless I specify otherwise.
- Work step-by-step and show a concise reasoning summary.
- Ask clarifying questions when ambiguity can change implementation.
- Keep edits minimal and preserve RBAC + beginner-friendly UX wording.
- Use plain language for all UI text (users are computer-illiterate).
- For each fix, report: Root cause -> Fix applied -> Prevention check.
- After every code change, run `cd Backend && uv run python scripts/smoke_test_workflows.py`.
- If changed behavior is not covered by the smoke script, update the script and rerun it before ending.
- If committing, follow /.github/skills/commit-message.md and avoid conventional-commit prefixes.
- Run validations before ending and report PASS/FAIL.
- Update docs/implementation.md before finishing.
- If SQL todos are available, update status: pending -> in_progress -> done/blocked.
```

---

## 2) Tool-Specific Start Prompts

### A) Claude Code

```text
Use agents/developer-workflows/CENTRAL_CONTEXT.md, docs/implementation.md, and PROGRESS.md as source of truth.
Persona: Builder Agent.
Current task: <TASK_ID>.
Before coding, list assumptions in 2-4 bullets.
If requirements are ambiguous, ask me targeted questions first.
After edits, run validation and produce run handoff format.
```

### B) Copilot CLI

```text
Follow agents/developer-workflows/CENTRAL_CONTEXT.md + docs/implementation.md + PROGRESS.md.
Persona: Builder Agent.
Implement <TASK_ID> with small scoped changes.
Use step-by-step reasoning summary.
Ask concise clarifying questions if needed before risky choices.
Run checks and update implementation tracker before ending.
```

### C) Codex

```text
Project context is in agents/developer-workflows/CENTRAL_CONTEXT.md.
Run logs in docs/implementation.md. Feature status in PROGRESS.md.
Persona: Builder Agent.
Task: <TASK_ID>.
Priorities: preserve RBAC, plain UX language (computer-illiterate users), minimal diffs.
Report: files changed, validations, blockers, next task.
```

### D) Cascade

```text
Initialize from agents/developer-workflows/CENTRAL_CONTEXT.md, docs/implementation.md, and PROGRESS.md.
Persona: Builder Agent (switch to QA Agent only when validating).
Execute <TASK_ID> in small steps.
Ask questions on ambiguity before implementation.
End by updating run log and suggesting next start point.
```

### E) Cursor

```text
Load agents/developer-workflows/CENTRAL_CONTEXT.md, docs/implementation.md, and PROGRESS.md first.
Use Builder Persona for this run.
Task scope: <TASK_ID>.
Show concise step-by-step execution summary.
If uncertainty affects outcome, ask me before proceeding.
Validate and update tracker before completion.
```

---

## 3) Persona Switch Prompt Snippets

### Switch to QA Persona
```text
Switch to QA Agent now. Validate only: build/compile/tests/manual route checks for touched areas. Return reproducible issues with severity and steps.
```

### Switch to Handoff Persona
```text
Switch to Handoff Agent now. Produce run summary in the project handoff template and include next recommended task ID.
```

---

## 4) Clarification Prompt You Can Force

Use this whenever you want the assistant to ask first:

```text
Before implementation, ask me up to 3 clarifying questions that could materially change your approach. Then continue with default assumptions if I do not respond.
```
