# FRAME required signals from the working seven

This is the extraction from repeated pressure across the seven comparison fixtures.

Goal:
- define what FRAME must prove it can capture
- keep it grounded in repeated project-structure signals
- avoid stuffing in memory/context-style fields just because they sound complete

This is not the final schema.
This is the test surface FRAME has to earn.

---

## ELI5 version

Think of this as the minimum set of truths that keeps showing up no matter what kind of repo we inspect.

Not feature details.
Not every file.
Not all project history.

Just the recurring stuff that helps another dev or agent quickly get:
- what this thing is
- how it is built
- where the important surfaces live
- what rules/boundaries matter
- how to run/check it
- what weird project-specific quirks could trip you up

---

## The repeated signals across all seven

### 1) project identity
FRAME must capture:
- what the project is
- what role it plays
- what kind of software shape it belongs to

Why this keeps repeating:
- every fixture has a clear identity that changes how you should reason about the repo
- `organize` is not `terragrunt`
- `python-sdk` is not `pharmax`
- `twenty` is not `httpie`

Good signal examples:
- tiny file-organization CLI
- protocol SDK
- pharmacy operations platform
- infra tooling CLI
- large CRM monorepo

What to avoid:
- long feature catalogs
- abstract labels that hide what the project actually is

---

### 2) primary stack and runtime/tooling surface
FRAME must capture:
- primary languages/frameworks
- major runtime/tooling assumptions that shape contribution or operation

Why this keeps repeating:
- stack changes how agents navigate, run, edit, and verify work
- some repos are simple stdlib Python
- others require uv, Playwright, Docker, Nx, Go toolchains, DB services, or infra tooling

Good signal examples:
- Python stdlib only
- FastAPI + Vue split app
- Go + Terraform/OpenTofu ecosystem
- TypeScript + Nx workspace

What to avoid:
- exhaustive dependency dumps
- every package unless it changes project behavior materially

---

### 3) repo shape
FRAME must capture:
- the overall structural shape of the repo
- the main organizational split that explains how the project is built

Why this keeps repeating:
- repo shape is one of the strongest cross-fixture signals
- tiny single script, medium package repo, split full-stack app, clean SDK tree, infra fixture forest, workspace monorepo

Good signal examples:
- single-script repo
- Python package repo with tests/docs/Docker
- split backend/frontend app
- src/tests/examples/docs/scripts SDK
- `internal/pkg/test/docs` tooling repo
- `packages/` workspace monorepo

What to avoid:
- deep file-by-file explanation
- turning every folder into a mini ontology

---

### 4) major surfaces and boundaries
FRAME must capture:
- the important working surfaces
- the meaningful boundaries between them

Why this keeps repeating:
- agents make bad edits when they miss boundaries
- `Backend/` vs `Frontend/`
- source tree vs tests
- plugin surfaces
- workspace packages
- fixture forests vs production code

Good signal examples:
- CLI entrypoint vs internal modules
- backend vs frontend
- public API vs internal implementation
- workspace package boundaries
- test fixtures as core surface, not “misc examples”

What to avoid:
- representing boundaries so vaguely that they stop being useful
- over-decomposing small repos that barely have boundaries

---

### 5) structural rules and contributor/runtime constraints
FRAME must capture:
- the real rules that shape safe work in the repo
- the important operating assumptions or contribution discipline

Why this keeps repeating:
- these rules change behavior more than descriptive prose does
- use `uv`, not `pip`
- install Playwright before real runs
- npm blocked, Yarn pinned
- CI/test matrix is part of the project shape
- filesystem mutation risk matters

Good signal examples:
- pinned toolchain rules
- environment assumptions
- contributor discipline
- hard project boundaries
- run/setup prerequisites

What to avoid:
- mixing stable project rules with task-specific instructions
- turning one-off advice into permanent project law

---

### 6) key paths and source-of-truth anchors
FRAME must capture:
- where the important truths live
- which files/folders are the main anchor points for understanding or changing the repo

Why this keeps repeating:
- every fixture had a small set of paths that mattered disproportionately
- agents need retrieval anchors, not whole-repo narration

Good signal examples:
- `organize.py`
- `Backend/` and `Frontend/`
- `pyproject.toml`
- `setup.cfg`
- `src/`, `tests/`, `packages/`
- rule docs like `AGENTS.md` or `CLAUDE.md`

What to avoid:
- giant path inventories
- listing paths without saying why they matter

---

### 7) run / verify surface
FRAME must capture:
- how the project is actually run or checked at a basic level
- what counts as the normal verification path

Why this keeps repeating:
- run/verify truth is part of project structure, not just task execution trivia
- some repos use simple CLI help runs
- some use pytest/ruff/pyright
- some use backend/frontend commands
- some rely on big make/go test/Nx flows

Good signal examples:
- `python3 organize.py --help`
- `uv run --frozen pytest`
- `make test`
- `npx nx test ...`

What to avoid:
- copying every command variant
- storing fragile command noise that goes stale fast

---

### 8) recurring structural quirks and drift hazards
FRAME must capture:
- the weird but important truths likely to mislead future agents/devs

Why this keeps repeating:
- these are exactly the sharp edges that a clean project paraphrase should preserve
- README/script-name mismatch in `organize`
- fixture-adapted imports in `autopahe`
- `render.yaml` mismatch/noise in `pharmax`
- stable-v1 vs in-progress-v2 split in `python-sdk`
- tooling/convention guardrails in `twenty`

Good signal examples:
- doc/code drift
- fixture-specific structural adaptation
- explicit blocked workflows
- checked-in repo noise that changes how the project should be interpreted

What to avoid:
- turning every minor oddity into a top-level core field
- losing the quirks completely and pretending the repo is cleaner than it is

---

## The compact “FRAME must earn these” list

Across the seven, FRAME should prove it can capture:

1. project identity
2. primary stack
3. repo shape
4. major surfaces
5. important boundaries
6. structural rules / operating constraints
7. key source-of-truth paths
8. basic run / verify surface
9. recurring structural quirks / drift hazards

If FRAME cannot capture those cleanly, it is not ready.

If FRAME captures those but needs lots of extra baggage, it is also not ready.

---

## What probably should NOT be core FRAME pressure right now

These did not show up as the most portable repeated needs across the seven:
- full feature breakdowns
- per-file descriptions
- chat/session memory
- broad “context” buckets
- large activity/history logs
- exhaustive dependency inventories
- detailed workflow-state modeling for every app unless it repeatedly proves portable

That stuff can still exist somewhere.
It just has not earned core-schema status from this seven-fixture pass.

---

## Translation into evaluation questions

When we fit FRAME against a repo, we should ask:

1. Can it say what the project is without becoming a brochure?
2. Can it represent the repo shape without file-by-file sludge?
3. Can it preserve the real boundaries that stop bad edits?
4. Can it point to the right source-of-truth paths?
5. Can it capture meaningful rules/constraints without mixing in task chatter?
6. Can it preserve the true run/verify surface?
7. Can it note important quirks/drift hazards without inventing a giant new category system?
8. Can it do all that with low repetition?

That is the real test surface.
Not whether the schema can technically hold more text.

---

## Strong early takeaway

The seven are already pushing toward a pretty clear idea:

FRAME should mostly be a structured project paraphrase.

Meaning:
- ordered
- grounded
- navigable
- constraint-aware
- lean

Not a second memory system.
Not an activity dump.
Not a feature encyclopedia.

(So yeah, the repos are basically telling us to stop being greedy.)
