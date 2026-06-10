# Schema critique: frame-five-part-v0 vs required signals

Candidate under test:
- `schemas/facts.schema.yaml`
- `schemas/rules.schema.yaml`
- `schemas/acts.schema.yaml`
- `schemas/map.schema.yaml`
- `schemas/expect.schema.yaml`
- shared defs in `schemas/frame.schema.yaml`

Comparison target:
- `Frame lab/fixtures/metadata/frame-required-signals.md`

Grounding note:
- This critique is about the schema itself, not whether a careful human can force-fit content into it.
- I am calling out where the current field shapes naturally support the repeated signals, and where they invite drift, repetition, or weak placement.

## Short verdict

The five-part candidate can cover most of the required signal sheet, but it does so unevenly.

Big picture:
- `facts` has broad capacity for identity/stack/repo-shape truth, but right now that capacity is mostly unconstrained buckets.
- `rules` has the cleanest home for structural rules, contributor constraints, and run/setup commands.
- `map` is the strongest part for key paths, major surfaces, and navigation anchors.
- `expect` can cover verification and correctness signals, but it overlaps with `rules.commands` quickly.
- `acts` is the least aligned with the repeated project-structure signals and looks more like execution/history scaffolding than project representation.

The candidate is therefore not obviously missing whole categories, but it is still muddy about where several repeated truths belong.

## 1) Where the schema already has good homes for repeated required signals

### Project identity
Required signal sheet wants:
- what the project is
- what role it plays
- what kind of software shape it belongs to

Good homes now:
- `facts.identity` in `schemas/facts.schema.yaml:23`
- `facts.classification` in `schemas/facts.schema.yaml:25`
- `facts.architecture` in `schemas/facts.schema.yaml:31`

Why this works:
- `identity` is an obvious place for project description and role.
- `classification` can hold software-type labeling.
- `architecture` can hold the repo-shape summary when it is project-defining.

Weakness inside the strength:
- all three are `type: object` with `additionalProperties: true`, so the schema gives almost no guidance about how identity differs from classification or architecture.
- The required signal sheet explicitly wants lean capture, but these buckets allow open-ended prose or ad hoc mini-ontologies.

### Primary stack and runtime/tooling surface
Required signal sheet wants:
- primary languages/frameworks
- major runtime/tooling assumptions

Good homes now:
- `facts.technology` in `schemas/facts.schema.yaml:28`
- `facts.environments` in `schemas/facts.schema.yaml:34`
- `facts.persistence` in `schemas/facts.schema.yaml:37`
- `rules.commands` in `schemas/rules.schema.yaml:26`
- `rules.critical_rules` in `schemas/rules.schema.yaml:22`

Why this works:
- `technology` is the obvious place for languages/frameworks.
- `environments` can hold runtime/setup assumptions.
- `commands` can hold the practical tooling surface.
- `critical_rules` can capture pinned workflow/toolchain constraints like “use uv” or “install Playwright first”.

### Repo shape
Required signal sheet wants:
- overall structural shape
- main organizational split

Good homes now:
- `facts.architecture` in `schemas/facts.schema.yaml:31`
- `map.roots` in `schemas/map.schema.yaml:20`
- `map.classifications` in `schemas/map.schema.yaml:28`

Why this works:
- `architecture` can say “single-script repo”, “split backend/frontend app”, or “workspace monorepo”.
- `roots` and `classifications` can anchor that shape to actual paths.

### Major surfaces and boundaries
Required signal sheet wants:
- important working surfaces
- meaningful boundaries between them

Good homes now:
- `map.roots` in `schemas/map.schema.yaml:20`
- `map.paths` in `schemas/map.schema.yaml:24`
- `map.classifications` in `schemas/map.schema.yaml:28`
- `map.access_points` in `schemas/map.schema.yaml:32`
- `map.managed_paths` in `schemas/map.schema.yaml:36`
- shared `links`/`ref` defs in `schemas/frame.schema.yaml:55-72`

Why this works:
- `path_summary_entry`, `classification_entry`, and `managed_path_entry` are concrete enough to say what a path is for and why it matters.
- `access_points` is especially useful for entrypoints and high-leverage anchors.
- `managed_paths.reason` gives a real slot for “do not casually edit generated/vendor/build-managed areas”.

### Structural rules and contributor/runtime constraints
Required signal sheet wants:
- real rules shaping safe work
- operating assumptions or contribution discipline

Good homes now:
- `rules.critical_rules` in `schemas/rules.schema.yaml:22`
- `rules.negative_instructions` in `schemas/rules.schema.yaml:52`
- `rules.stop_and_ask` in `schemas/rules.schema.yaml:56`
- `rules.skill_hints` in `schemas/rules.schema.yaml:60`
- `rules.commands` in `schemas/rules.schema.yaml:26`

Why this works:
- this file has the clearest norm-vs-description intent in the candidate.
- `question_entry` and `hint_entry` give structure to intervention points and non-default caution.

### Key paths and source-of-truth anchors
Required signal sheet wants:
- where important truths live
- main files/folders for understanding or changing the repo

Good homes now:
- `map.access_points` in `schemas/map.schema.yaml:32`
- `map.roots` in `schemas/map.schema.yaml:20`
- `map.paths` in `schemas/map.schema.yaml:24`
- `path_summary_entry.path` + `summary` in `schemas/frame.schema.yaml:185-199`

Why this works:
- this is the cleanest and least ambiguous part of the whole candidate.
- the schema encourages saying both path and why it matters.

### Run / verify surface
Required signal sheet wants:
- how the project is run or checked
- normal verification path

Good homes now:
- `rules.commands` in `schemas/rules.schema.yaml:26`
- `expect.verify` in `schemas/expect.schema.yaml:34`
- `expect.done_when` in `schemas/expect.schema.yaml:30`
- `expect.required_evidence` in `schemas/expect.schema.yaml:38`

Why this works:
- `commands` can store the executable surface.
- `verify` and `done_when` can store what counts as acceptable checking.
- `required_evidence.expectation` can express what proof a future change should provide.

### Recurring structural quirks and drift hazards
Required signal sheet wants:
- weird but important truths likely to mislead future agents/devs

Best homes now:
- `facts.ambiguities` in `schemas/facts.schema.yaml:42`
- `rules.critical_rules` / `negative_instructions` in `schemas/rules.schema.yaml:22,52`
- `map.managed_paths.reason` in `schemas/map.schema.yaml:36`
- generic `evidence` and `links` fields across shared defs

Why this only partly works:
- the candidate can store quirks, but there is no crisp quirk/drift-hazard field.
- `ambiguity_entry.question` is built around open questions, not settled but weird truths.
- many recurring hazards are not ambiguous; they are known structural caveats.

## 2) What looks muddy or repetitive

### `facts` is too open and therefore too overlap-prone
Concrete issue:
- `identity`, `classification`, `technology`, `architecture`, `environments`, and `persistence` are all open objects with `additionalProperties: true` in `schemas/facts.schema.yaml:23-39`.

Why this matters:
- the required signal sheet is asking for lean repeated structure.
- the current candidate instead creates six large catch-all buckets.
- this makes repeated truths easy to duplicate with slightly different wording.

Likely repetition patterns:
- repo shape in both `facts.architecture` and `map.roots`/`map.classifications`
- stack/tooling in both `facts.technology` and `rules.commands`
- runtime assumptions in both `facts.environments` and `rules.critical_rules`
- important paths copied into `facts.architecture` prose instead of staying in `map`

### `statement_entry` is too generic, so `map` and `expect` can start sounding the same
Concrete issue:
- `statement_entry` in `schemas/frame.schema.yaml:172-183` only requires `summary`.
- it is reused by `map.paths` and all of `expect.outcomes`, `expect.invariants`, `expect.done_when`, and `expect.verify`.

Why this matters:
- a path summary and a correctness rule are different kinds of statements, but the schema gives them the same shape.
- this will encourage prose duplication instead of stronger semantic separation.

Expected failure mode:
- `map.paths[tests/] = "verification lives here"`
- `expect.verify[test_suite] = "run tests in tests/"`
- `rules.commands.pytest = "run tests"`
All three may be true, but the schema does not force sharper distinctions.

### `rules.commands` and `expect.verify` overlap heavily
Concrete issue:
- `rules.commands` stores `run`, `purpose`, `links`, `evidence` in `schemas/rules.schema.yaml:26-43`.
- `expect.verify` is an object of free keys to `statement_entry` in `schemas/expect.schema.yaml:34-37`.

Why this matters:
- the required signal sheet wants the run/verify surface captured once, cleanly.
- the current design makes it natural to store command strings in `rules.commands`, then re-describe the same checks in `expect.verify`.

Likely result:
- two parallel command inventories, one procedural and one evaluative, drifting out of sync.

### `facts.ambiguities` is the wrong shape for non-ambiguous quirks
Concrete issue:
- `ambiguity_entry` in `schemas/frame.schema.yaml:234-250` requires `id` and `question`, with optional `status`.

Why this matters:
- doc/code drift in `organize` is not primarily a question; it is a known hazard.
- fixture-adapted imports in `autopahe` are not an open ambiguity either; they are a structural caveat.
- forcing those into `question` form will distort the representation.

### Shared defs include design/evaluation machinery that the five project files do not use
Concrete issue:
- `field_design_card` in `schemas/frame.schema.yaml:352-395`
- `relationship_condition` in `schemas/frame.schema.yaml:397-420`

Why this matters:
- these defs are not referenced by the current five project schemas.
- they read like schema-design metadata, not the repeated project signals from the sheet.
- this is not fatal, but it is a smell: the shared schema is carrying framework-internal concepts while the project-representation side still has open buckets.

## 3) Where `acts` seems misaligned with project representation

Concrete schema elements:
- `action_overview` open object in `schemas/acts.schema.yaml:22-24`
- `reflect_loop` array of `reflect_entry` in `schemas/acts.schema.yaml:25-28`
- `actions` array of `action_entry` in `schemas/acts.schema.yaml:29-32`
- `blockers` array of `blocker_entry` in `schemas/acts.schema.yaml:33-36`
- `archive` open object in `schemas/acts.schema.yaml:37-39`

Why this looks misaligned:
- the required signal sheet is about stable project structure: identity, stack, repo shape, boundaries, rules, key paths, verify surface, quirks.
- `acts` instead models activity records, reflections, blockers, and archive/history.
- that aligns with agent execution tracking, not with a structured project paraphrase.

Why the mismatch is especially clear on the current fixtures:
- `organize` has almost no natural project content for `reflect_loop`, `actions`, or `blockers` unless we start logging evaluator work rather than repo truth.
- `autopahe` has more operational complexity, but even there the repeated signals are about package shape, browser/runtime setup, tests, Docker path, config locations, and import quirks -- not about historical action logs.

Specific schema-shape problem:
- both `action_overview` and `archive` are `additionalProperties: true`, so if `acts` feels empty the path of least resistance is to stuff project description back into them.
- that would directly violate the working rule in `Frame lab/evaluations/reports/subagent-loop-plan.md` that `acts` is allowed to look weak if the repo does not justify it.

Bottom line on `acts`:
- as a five-part project-representation candidate, `acts` is the weakest part and the strongest overfit risk.
- as a wider FRAME-system file for execution history, it may still be fine -- but that is a different job than the required-signal sheet is testing.

## 4) Where missing semantics are likely to show up in `organize` and `autopahe`

### A) No clean dedicated home for settled quirks / drift hazards
This is the biggest repeated semantic gap.

Why it will show up in `organize`:
- README examples using `file_manager.py` while the real entrypoint is `organize.py`
- Linux-specific hardcoded default path
- `python3 organize.py --help` emitting a warning

Why it will show up in `autopahe`:
- fixture-adapted imports are a known structural adaptation
- browser-install/setup truth is easy to misunderstand as optional
- Docker path and local-state/config behavior add “important but weird” truth that is neither pure fact nor pure rule nor pure expectation

Current candidate fallback homes are all imperfect:
- `facts.ambiguities` is question-shaped
- `rules.negative_instructions` makes quirks sound normative
- `map.managed_paths.reason` only works when the quirk is path-specific
- `expect` is about correctness, not interpretation hazards

### B) Boundary semantics exist in `map`, but project-vs-test/fixture/package boundaries are still under-specified
Why this will show up in `autopahe`:
- important boundary between CLI entry (`cli.py` / `auto_pahe.py`), core logic (`ap_core/`), optional/helping features, tests, and Docker docs/scripts
- likely need to distinguish “public entrypoint”, “internal implementation”, “tests as verification surface”, and “docs/scripts as operational support”

Current schema issue:
- `classification_entry` in `schemas/frame.schema.yaml:201-216` only requires `summary`, with optional `paths`.
- this can describe boundaries loosely, but there is no explicit notion of boundary type or interface role.

Practical consequence:
- fitters will likely compensate with prose inside `summary`, which reduces consistency and tool usefulness.

### C) Source-of-truth anchoring is present, but source-of-truth rank is not
Why it will show up in both fixtures:
- `organize` has a real conflict between README and script.
- `autopahe` likely has truths split across `pyproject.toml`, `README.md`, CLI files, and test/config code.

Current schema issue:
- `map.access_points` and `map.paths` can name important files, but there is no explicit field for “this is canonical over that other source”.
- `evidence.source` exists in `schemas/frame.schema.yaml:88-106`, but it is free-form evidence metadata, not a first-class source-of-truth ranking relation.

Practical consequence:
- important anchor conflicts will be captured only narratively.

### D) Run surface vs verify surface is still too blurred
Why it will show up in `organize`:
- there is basically one cheap command surface and one lightweight verification surface, so `rules.commands` and `expect.verify` can collapse into each other.

Why it will show up in `autopahe`:
- there are setup commands (`uv sync`, Playwright install), run commands, test commands, and Docker paths.
- the candidate can hold all of these, but not with a sharp distinction between prerequisites, normal operation, and correctness proof.

Current schema issue:
- `rules.commands` only knows about `run` and `purpose`.
- `expect.verify` only knows generic summary statements.

Practical consequence:
- the more real the workflow gets, the more likely fitters are to repeat commands across files to preserve meaning.

### E) Repo-size / complexity pressure is not explicit
Why it matters:
- the required signal sheet repeatedly stresses scaling down for tiny repos and not over-modeling them.
- `organize` is the exact case where this matters.

Current schema issue:
- there is no compact field that lets the schema say “single-script repo; do not over-decompose this”.
- yes, a human can express that in `facts.architecture`, but the candidate does not structurally acknowledge this repeated pressure.

Practical consequence:
- small repos are likely to suffer from forced distribution across five files.

## 5) Most important strengths

1. `map` is already close to earning its keep.
- `roots`, `paths`, `access_points`, and `managed_paths` line up well with key-path and major-surface pressure.

2. `rules` has a real semantic center.
- `critical_rules`, `negative_instructions`, `stop_and_ask`, and `commands` are all plausibly useful and distinct enough.

3. Shared evidence/linking primitives are good.
- `links`, `evidence`, `ref`, and `confidence` in `schemas/frame.schema.yaml` support grounded claims without forcing giant prose.

## 6) Most important risks before scoring

1. `acts` is probably the wrong fifth file for this test surface.
- It models activity history more than project structure.

2. `facts` is under-specified where it most needs discipline.
- Too many `additionalProperties: true` buckets invite junk-drawer behavior.

3. run/verify truth is split across `rules` and `expect` without enough semantic separation.
- Expect repetition and drift.

4. the schema lacks a crisp home for recurring settled quirks/drift hazards.
- This is likely to be painful in both `organize` and `autopahe`.

5. boundaries are representable, but only weakly typed.
- This is acceptable on tiny repos, but likely to get muddy on medium repos like `autopahe`.

## Final take

Against the required-signal sheet, the candidate is closer to “covers the surface awkwardly” than to “cannot represent the surface at all.”

That is encouraging, but the awkwardness is concentrated in exactly the places most likely to cause noise during real fits:
- open-ended `facts` buckets
- `acts` as project-representation overreach
- weak quirk/drift-hazard semantics
- run/verify duplication across `rules` and `expect`

If scoring is about clean capture with low repetition, those are the pressure points most likely to cost this candidate on both `organize` and `autopahe`.
