# Schema adjustment: FRAME schema 0.1.0 round 2

Date: 2026-06-01
Candidate: `frame-five-part` / FRAME schema `0.1.0`

Inputs used:
- `Frame lab/evaluations/reports/scoring-synthesis__frame-five-part-v0.1.0__round2.md`
- `Frame lab/evaluations/scorecards/frame-five-part-v0.1.0/scorecard__frame-five-part-v0.1.0__organize.toml`
- `Frame lab/evaluations/scorecards/frame-five-part-v0.1.0/scorecard__frame-five-part-v0.1.0__autopahe.toml`
- `Frame lab/evaluations/scorecards/frame-five-part-v0.1.0/scorecard__frame-five-part-v0.1.0__pharmax.toml`
- all 15 refit files under `Frame lab/evaluations/fits/frame-five-part-v0.1.0/`

Changed files:
- `schemas/frame.schema.yaml`
- `schemas/facts.schema.yaml`

Validation performed:
- JSON Schema Draft 2020-12 meta-validation passed for every file in `schemas/*.schema.yaml`
- all 15 refit files still validate against the adjusted schemas
- all 3 scorecards parse as TOML

## Why a second adjustment was earned

The refit/score round showed the first adjustment helped:
- `project_profile` reduced scale confusion
- `source_truth` handled authority conflicts
- `structural_quirks` captured known hazards
- `rules.commands` plus `expect.verify.command_ref` reduced command duplication

But two repeated pressures stayed visible.

## Adjustment 1 — add `frame.representation_scope`

Added optional `representation_scope` to the shared FRAME header.

Allowed values:
- `baseline_project`
- `execution_record`
- `handoff`
- `mixed`
- `null`

Reason:
`acts` repeatedly failed as baseline project representation.
It was useful as provenance/work-history, but weak as durable project context.

This field lets a FRAME file say what kind of context it is without changing file roles or deleting Acts.

Expected Haxaml use:
- load `baseline_project` files first for normal repo understanding
- treat `execution_record` / `handoff` files as session history or task-state context
- avoid wasting baseline context budget on Acts when no current task needs action history

Anti-overfit note:
This is not an Acts-specific hack. Any FRAME file can declare scope if a future representation is mixed or handoff-shaped.

## Adjustment 2 — add shared `policy_entry`

Added `$defs.policy_entry` to `schemas/frame.schema.yaml`.

Purpose:
Represent durable project policies, workflows, lifecycle constraints, role rules, safety constraints, data-integrity rules, and environment policies in a portable way.

Core fields:
- `id`
- `summary`
- `kind`
- optional `applies_to`
- optional `source_refs`
- optional `expect_refs`
- optional `links`
- optional `evidence`

Allowed `kind` values:
- `role_policy`
- `workflow_policy`
- `lifecycle_constraint`
- `safety_constraint`
- `data_integrity`
- `environment_policy`
- `other`

Reason:
`pharmax` exposed repeated workflow/policy truth across Facts, Rules, Map, and Expect:
- role policy
- invoice lifecycle
- stock/inventory integrity
- auth/RBAC boundaries

The schema needed a small reusable way to define that durable truth once, then let other files reference it.

Anti-overfit note:
This does not add pharmacy fields, invoice fields, browser fields, or full domain modeling.
It adds a general small policy shape that also works for CLIs, web apps, SDKs, infra repos, and AI systems.

## Adjustment 3 — add `facts.policies`

Added optional `facts.policies` array referencing `$defs.policy_entry`.

Reason:
Facts should hold durable current project truth.
Policies/workflows/lifecycle constraints are project truth when they describe how the system must behave.

Rules can still contain instructions.
Expect can still contain proof obligations.
Map can still route to source surfaces.
But Facts can now define stable policies once.

## What was deliberately not changed

### Did not remove Acts

Acts still belongs in FRAME for checked work, handoff state, blockers, and execution provenance.
The adjustment only makes its scope clearer.

### Did not harden all open facts buckets

`identity`, `classification`, `technology`, `architecture`, `environments`, and `persistence` remain permissive for now.

Reason:
The fit loop shows these buckets are useful, but not enough evidence exists yet to freeze their final typed shapes.
The safer next step was to add one small repeated shape: `policy_entry`.

### Did not add fixture-specific fields

No `pharmacy`, `invoice`, `browser`, `download`, or `organize`-specific fields were added.

## Next loop recommendation

Run another refit against the same three fixtures, but this time ask fitters to:

1. set `frame.representation_scope`
   - Facts/Rules/Map/Expect should usually be `baseline_project`
   - Acts should usually be `execution_record` or `handoff`

2. move durable policies/workflows into `facts.policies`
   - Pharmax role policy and invoice lifecycle are the best first test
   - Autopahe path/state/browser safety may also fit as policy entries
   - Organize filesystem mutation safety may fit as a safety constraint

3. check whether this reduces duplicated workflow/policy text in Rules and Expect

Promotion criteria for the next loop:
- policy truth appears once, then gets referenced cleanly
- Acts no longer feels forced into baseline project representation
- no loss in coverage or agent usefulness
- token efficiency improves on `pharmax` without making `organize` feel heavier

## Current verdict

FRAME schema `0.1.0` advanced through a conservative second adjustment.

The schema is still intentionally early-stage, but the loop is working:
real fixtures exposed repeated friction, scoring made the friction visible, and the schema changed minimally instead of growing random complexity.
