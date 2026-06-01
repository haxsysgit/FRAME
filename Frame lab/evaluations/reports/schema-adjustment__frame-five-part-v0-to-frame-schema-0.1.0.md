# Schema adjustment: frame-five-part-v0 → FRAME schema 0.1.0

Date: 2026-06-01

Inputs used:
- `Frame lab/evaluations/reports/frame-five-part-v0__organize-fit-pass.md`
- `Frame lab/evaluations/reports/subagent-fit__organize.md`
- `Frame lab/evaluations/reports/subagent-fit__autopahe.md`
- `Frame lab/evaluations/reports/schema-critic__frame-five-part-v0__round1.md`

Changed files:
- `schemas/frame.schema.yaml`
- `schemas/facts.schema.yaml`
- `schemas/rules.schema.yaml`
- `schemas/expect.schema.yaml`
- `schemas/acts.schema.yaml`

Validation performed:
- YAML parse passed for every file in `schemas/*.schema.yaml`
- JSON Schema Draft 2020-12 meta-validation passed for every file in `schemas/*.schema.yaml`

## Frame Lab loop model

Frame Lab should operate as a supervised design loop:

```text
fit candidate schema to real projects
→ score fit quality and pressure cost
→ identify repeated losses
→ adjust schema minimally
→ rerun on old and new fixtures
→ keep changes that improve general fit without overfitting
```

The important rule: a single fixture can expose a flaw, but it should not define the standard alone.

A schema change earns promotion only when it improves at least one repeated pressure point without making unrelated project families worse.

## Loss signals from the reports

### 1. `acts` is not baseline project representation

Evidence:
- `organize` had almost no natural content for `acts`.
- `autopahe` also made `acts` feel like execution/work history, not repo description.
- The schema critic called `acts` the strongest overfit risk.

Adjustment:
- Updated `acts.schema.yaml` description to say Acts is checked execution/work-history, not baseline project representation.
- Added optional `representation_policy.baseline_project_representation: false`.

Intent:
- Keep Acts in FRAME, but stop fitters from stuffing stable repo facts into it just because the fifth file exists.

Anti-overfit note:
- This does not delete Acts yet. It only clarifies its role while future loops decide whether baseline project packs should omit it.

### 2. Settled quirks/drift hazards need a first-class home

Evidence:
- `organize`: README says `file_manager.py`, actual entry is `organize.py`; hardcoded Linux path; warning on help command.
- `autopahe`: fixture-adapted imports, browser setup caveat, checked-in state/artifact noise.
- Existing `facts.ambiguities` was question-shaped, but many hazards are known truths, not open questions.

Adjustment:
- Added shared `$defs.quirk_entry`.
- Added `facts.structural_quirks` array.

Intent:
- Give Haxaml and future agents a crisp place to check “what will probably mislead me?” before acting.

Anti-overfit note:
- The field is not `organize_doc_drift` or `autopahe_browser_weirdness`; it is a general hazard shape across project families.

### 3. Source-of-truth ranking is needed when repo files disagree

Evidence:
- `organize` has README/code drift.
- `autopahe` has truth split across `pyproject.toml`, README, CLI files, tests, and path/config modules.
- Evidence metadata was too generic to express authority ordering.

Adjustment:
- Added shared `$defs.source_truth_entry`.
- Added `facts.source_truth` array.

Intent:
- Let tools decide whether code, README, generated output, package metadata, or tests should be trusted first for a given claim.

Haxaml use:
- At task start, Haxaml can prioritize canonical or strong sources and down-rank stale/generated/noisy sources.

### 4. Tiny repos need explicit compression pressure

Evidence:
- `organize` showed that five files can feel like tax paperwork for a one-script repo.
- The schema had no compact signal for “do not over-decompose this project.”

Adjustment:
- Added shared `$defs.project_profile_entry`.
- Added `facts.project_profile` with `family`, `system_role`, `complexity`, and optional `scale_guidance`.

Intent:
- Give every fit a compact early routing signal.
- Make scale-down behavior explicit instead of relying on evaluator discipline.

Haxaml use:
- Before loading every FRAME section deeply, Haxaml can use `complexity` and `scale_guidance` to decide how much context to pull.

### 5. Command inventory and verification meaning were overlapping

Evidence:
- Both reports warned that `rules.commands` and `expect.verify` would repeat command strings.
- `autopahe` needs setup/run/test/browser commands, while `expect` should describe what those checks prove.

Adjustment:
- Added shared `$defs.command_entry` with `kind`, `run`, `purpose`, and `when_to_use`.
- Replaced inline `rules.commands` shape with `$defs.command_entry`.
- Added shared `$defs.verification_entry`.
- Changed `expect.verify` to use `verification_entry`, with optional `command_ref` pointing back to `rules.commands.<id>`.

Intent:
- `rules.commands` stores executable surfaces.
- `expect.verify` stores correctness meaning and proof type.
- Command strings should live once.

Haxaml use:
- Haxaml can list available commands from Rules, then decide which verification obligation they satisfy through Expect refs.

### 6. Boundary typing in `map` needed light strengthening

Evidence:
- `autopahe` has real boundaries: CLI entry, core logic, config/path helpers, tests, Docker/support material, checked-in state/noise.
- Current `classification_entry.summary` forced too much boundary meaning into prose.

Adjustment:
- Extended shared `$defs.classification_entry` with optional `boundary_type` and `interface_role`.

Intent:
- Give Haxaml a better routing hint without turning Map into a full dependency graph.

Anti-overfit note:
- This is deliberately light. It does not encode autopahe-specific folders.

## What was not changed yet

### Open facts buckets remain open for now

The reports correctly flagged `identity`, `classification`, `technology`, `architecture`, `environments`, and `persistence` as too open.

I did not harden them yet because the evidence only proves they are risky, not exactly what the final typed shape should be.

Next loop should test whether `project_profile`, `structural_quirks`, and `source_truth` reduce junk-drawer behavior before replacing the open buckets.

### Acts was constrained, not removed

The reports strongly suggest Acts is not baseline project representation.

I did not remove it because FRAME may still need Acts for checked work, handoff state, blockers, and execution provenance.

Next loop should score whether baseline project packs should treat Acts as optional or separate from the core project representation set.

## Next fit pass recommendation

Run a new fit using FRAME schema 0.1.0 against:
1. `organize` — tests scale-down and doc/code drift.
2. `autopahe` — tests medium CLI/package boundaries, setup/runtime caveats, and command/verification separation.
3. `pharmax` — tests full-stack app pressure: frontend/backend split, database models, API surfaces, seed/smoke scripts, and business workflow correctness.

Promotion criteria:
- lower repetition between Facts/Rules/Map/Expect
- less forced content in Acts
- clearer placement for quirks and source authority
- no fixture-specific schema bloat
- Haxaml can make routing/verification decisions from the fields

## Current verdict

This is a conservative schema adjustment, not a new canon.

It moves the candidate from “can represent the fixtures awkwardly” toward “has explicit slots for the repeated friction the fixtures exposed.”

The next loop should fit and score this adjusted candidate before we harden more fields.
