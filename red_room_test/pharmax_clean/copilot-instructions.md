# Copilot Instructions (Pharmax Final Project)

## 0) Purpose
This file is the single operating contract for AI assistance in this repository across:
- Copilot CLI
- Claude Code
- Codex
- Cascade
- Cursor

Follow these rules for **all sessions**.

---

## 1) Canonical Context Files

### Development
- `agents/developer-workflows/CENTRAL_CONTEXT.md`
- `agents/developer-workflows/AGENT_WORKFLOWS.md`
- `agents/developer-workflows/PROMPTS.md`

### Report Writing
- `agents/report-writing/CENTRAL_CONTEXT.md`
- `agents/report-writing/REPORT_OUTLINE.md`
- `agents/report-writing/HANDBOOK_ALIGNMENT.md`
- `agents/report-writing/PROMPTS.md`
- `agents/report-writing/EVIDENCE_LOG_TEMPLATE.md`

### Trackers
- `PROGRESS.md` — Master feature and phase tracker (update when features complete)
- `docs/UI_MODERNIZATION_PLAN.md` — Canonical UI modernization blueprint (theme, visual rules, rollout)

### Commit Message Skill
- `/.github/skills/commit-message.md` — Canonical commit-message writing rules for all assistants

---

## 2) UX Philosophy (Critical)

PharmaX is designed for **computer-illiterate users**. Most operators have limited technical experience.

Hard rules:
- Use plain, everyday language — avoid technical jargon
- Labels should be action-oriented and clear (e.g., "Add Product" not "Create Entity")
- Error messages must explain what happened AND what to do next
- Avoid abbreviations unless universally understood
- When in doubt, write as if explaining to someone who rarely uses computers
- Test all wording by asking: "Would my grandmother understand this?"

Visual system rule:
- Use and preserve the **Modern Clinical Green** design direction documented in `docs/UI_MODERNIZATION_PLAN.md`.
- New UI work must follow shared token/pattern consistency (cards, forms, tables, buttons, states) instead of introducing one-off styles.

Current interaction/copy rules:
- Analytics and Reports use **sidebar-only navigation**; do not reintroduce in-page jump dropdowns, quick-link cards, or extra intro wrappers.
- Avoid command-style or assistant-style UI wording (for example, explanatory phrases that sound like tool output).
- Keep page tops compact: avoid stacked duplicate title + subtitle + helper-tip blocks when one clear title is enough.
- Preserve high-friction workflow improvements:
  - product/unit bulk selection supports row double-click selection with clear selected-row highlighting,
  - selected rows should persist during search/filter refinements,
  - Units & Pricing step controls use increments of 10 for price/multiplier editing.

Examples:
- ✅ "Sales & Invoices" — ❌ "Invoice Resource Type"
- ✅ "Something went wrong. Please try again." — ❌ "NetworkError: fetch failed"
- ✅ "Who did it" — ❌ "Actor"
- ✅ "What changed" — ❌ "Resource Type"

---

## 3) Mandatory Start Sequence (Every Session)

1. Identify task type: `development` or `report-writing`.
2. Read the relevant central context file(s) above.
3. Read `docs/implementation.md` for run history.
4. Read `PROGRESS.md` for feature status.
5. Read `docs/UI_MODERNIZATION_PLAN.md` for visual system alignment when touching UI.
6. Confirm current task ID / chapter target.
7. Ask clarifying questions before implementation/drafting if anything is ambiguous.

Do not proceed on major assumptions.

Commit rule:
- Before any `git commit`, read and follow `/.github/skills/commit-message.md`.

---

## 4) Clarifying Questions Rule (Mandatory)

If requirements are unclear, ask questions first.

Minimum triggers for questions:
- conflicting instructions,
- missing evidence/data,
- unclear scope boundaries,
- uncertain rubric/handbook alignment.

Use concise questions and wait for answers before high-impact changes.

---

## 5) Persona-Driven Workflow

Always declare and follow one persona per pass:

### A) Development personas
- **Planner**: scope and acceptance criteria
- **Builder**: implement minimal safe changes
- **QA/Reviewer**: validate build/tests/RBAC/UX clarity
- **Handoff**: summarize changes and next steps

### B) Report-writing personas
- **Report Supervisor**: structure and academic coherence
- **Methodology Validator**: “what was done” accuracy
- **Evidence Auditor**: traceability to artifacts
- **Human Voice Coach**: natural student voice polish
- **Compliance Guard**: handbook + supervisor alignment

---

## 6) Reasoning Style Contract

Do not output hidden internal reasoning.
Provide concise, explicit step summaries:
1. Plan
2. Action
3. Validation
4. Result
5. Next step / blocker

---

## 7) Report Structure Rules (Supervisor-Mandated)

Use this exact chapter order:

1. Introduction  
2. Literature Review  
3. Requirements  
4. Design  
5. Implementation  
6. Evaluation  
7. Conclusion and Future Work

Hard constraints:
- Consistent numbering
- No duplicated sections
- Clear system purpose early in Chapter 1
- Include Literature Review as full chapter
- Prefer past tense (“what I did”) over future tense
- Mark missing proof as `[EVIDENCE NEEDED]`

## 7.1) Report Length and Depth Requirement

The final report should target approximately 18,500 words.

Guidelines:
- This is a flexible target (acceptable range: ~17,000–20,000 words).
- Word count must emerge naturally from depth, not forced expansion.
- Do not add filler, repetition, or generic academic phrasing to meet length.

Depth should come from:
- explaining decisions and reasoning,
- describing implementation details clearly,
- discussing trade-offs and alternatives,
- reflecting on challenges and how they were resolved.

Chapter expectations (approximate guidance, not strict limits):
- Introduction: concise (1,000–1,500 words)
- Literature Review: detailed and critical (3,000–4,000 words)
- Requirements: clear and structured (2,000–2,500 words)
- Design: detailed system reasoning (3,000–3,500 words)
- Implementation: highly detailed (4,000–5,000 words)
- Evaluation: critical analysis (2,500–3,000 words)
- Conclusion: concise and reflective (800–1,200 words)

Rules:
- Avoid shallow summaries of complex features.
- Avoid listing without explanation.
- Expand by explaining "why" and "how", not repeating "what".

If content is insufficient:
- Mark gaps with `[EVIDENCE NEEDED]` instead of fabricating details.
---

## 8) Human-Authorship Rules (Important)

Do not attempt AI-detection evasion.
Instead:
- keep authentic student voice,
- ground claims in project evidence,
- include decisions, trade-offs, and limitations,
- keep wording clear and natural, not formulaic.

## 8.1) Conversational Academic Tone (Supervisor-Aligned)

The report must read as a natural, professional conversation between the student and the supervisor/reader.

Tone guidelines:
- Write as if explaining decisions and work to a supervisor in person.
- Avoid exam-style responses or rigid Q&A phrasing.
- Maintain clarity and professionalism, but keep language natural and fluid.
- Use smooth transitions between ideas instead of abrupt, disconnected statements.
- Explain reasoning, not just outcomes (e.g., why a decision was made, not only what was done).
- Avoid overly formal or robotic phrasing.
- Prefer past tense for implementation ("I implemented...", "I designed...")
- Allow present tense when explaining system behavior ("The system handles...", "This ensures...")

Style constraints:
- No bullet-dumping in core chapters unless necessary (prefer paragraphs).
- Avoid generic filler phrases (e.g., "This section will discuss...").
- Prefer grounded statements tied to actual implementation.
- Keep sentences varied in structure and length.

Litmus test:
The writing should feel like:
"I’m walking my supervisor through what I built and why it makes sense."

Not like:
"I am answering an academic question for marks."
---

## 9) Development Quality Gates

For development tasks, run relevant checks:

- Frontend build:
  - `cd Frontend && npm run build`
- Backend dependency/runtime tooling:
  - Use `uv` commands (`uv sync`, `uv run ...`) for backend setup and execution.
  - Do not use `pip`-based install/run flows unless explicitly requested for a special case.
- Backend workflow smoke test (**mandatory after every code change**):
  - Run: `cd Backend && uv run python scripts/smoke_test_workflows.py`
  - If a new/changed workflow is not covered, update `scripts/smoke_test_workflows.py` first, then run it in the same pass.
  - Do not close a task until this script passes.
- Backend syntax check for touched files:
  - `python3 -m py_compile <changed_files>`

If tests exist for touched area, run them.
Report pass/fail clearly.

---

## 10) End-of-Run Requirements (Mandatory)

Before ending any run:
1. Update `docs/implementation.md` with:
   - what was completed,
   - files changed,
   - validation results,
   - next recommended start point.
2. Provide a concise handoff summary.

No run is complete without tracker update.

---

## 11) Output Format Preference

Keep responses:
- concise,
- actionable,
- file-path specific,
- aligned to current task only.

When editing files, provide precise patch-ready content.

---

## 12) Safe Development Practices (CRITICAL)

These rules exist to prevent breaking working functionality when making changes.

### A) Incremental Change Rule
- **One feature/fix at a time**: Do not combine multiple unrelated changes in a single session.
- **Test after each change**: After modifying ANY file, verify the application still works:
  - Frontend: Run `cd Frontend && npm run build`
  - Backend: Run `cd Backend && uv run python -c "from app.main import app"`
- **Commit working changes before moving to next task**.

### B) Never Edit Without Understanding
- Before modifying a file, read and understand its current logic.
- Do not modify complex business logic (reconciliation, permissions, invoicing) without tracing through the full flow.
- If you don't understand why code exists, ASK before changing it.

### C) Protected Files (High-Risk)
These files contain complex interconnected logic. Extra care required:
- `Backend/app/api/routes/invoices_route.py` — Reconciliation, after-hours permissions, complex queries
- `Backend/app/core/dependencies.py` — Auth and permission guards
- `Frontend/src/layouts/AppShell.vue` — Notifications, navigation, global state
- `Frontend/src/views/CashierView.vue` — Cashier workflow, receipt printing

For these files:
1. Read the entire file before making changes
2. Understand all functions that depend on your changes
3. Test thoroughly after modification
4. Prefer small surgical changes over rewrites

### D) Revert Protocol
If a change breaks existing functionality:
1. **Stop immediately** — do not attempt multiple fixes that may compound the problem.
2. Use `git checkout -- <file>` to revert to last working state.
3. Report what was reverted and why.
4. Re-approach with smaller, safer changes.

### E) Print/Browser API Caution
Browser print functionality is fragile. Before changing print logic:
- Test the existing implementation first
- Use `window.open` + `window.print()` pattern (proven to work)
- Avoid iframe-based printing (browser compatibility issues)
- Always test print dialog actually opens

### F) Database Migration Safety
- Never add enum values without migration scripts
- Test SQLAlchemy queries with `.unique()` when using eager loads
- Verify imports before committing config changes

### G) Root-Cause-First Fix Protocol (Mandatory)
For every bug fix, always identify and report the **actual root cause** before (or with) the code change.

Required per-fix output:
1. **Root cause** — exact file/function and why the bug happened.
2. **Fix applied** — what changed and why it solves that root cause.
3. **Prevention check** — what guard/validation confirms the issue should not repeat.

Do not report only symptom-level changes. Every fix must include a clear cause-and-resolution explanation.
