# FRAME implementation reset plan

This document corrects the current implementation direction.

## What drifted

The first `frame-python` slice drifted toward a generic loader/validator shape.
That was useful as a tiny spike, but it is not the main intended architecture.

The intended architecture is more specific:

1. FRAME is an architecture centered on five real files
   - `facts`
   - `rules`
   - `acts`
   - `map`
   - `expect`
2. each file should have its own typed Python model
3. shared schema pieces should become shared Python model pieces
4. one umbrella model should compose the five file models
5. only after that should cross-file references / graph behavior mature

## What the current repo evidence says

### From `schemas/`

The repo already has:
- `schemas/frame.schema.yaml` for shared definitions
- `schemas/facts.schema.yaml`
- `schemas/rules.schema.yaml`
- `schemas/acts.schema.yaml`
- `schemas/map.schema.yaml`
- `schemas/expect.schema.yaml`

That means the build should not pretend schema is absent.
It should treat the current schemas as the starting contract to analyze, refine, and model.

### From `0.8.x_Roadmap.md`

The roadmap says:
- build vertical schema slices across all five files
- do not mature one file in isolation first
- shared base contract comes first
- evidence, unknowns, references, runtime behavior, and verification then deepen in layers

So the correct implementation center is not a generic bucket model.
It is a connected five-file architecture.

### From `example_projects/`

The example projects show that FRAME must fit very different shapes:
- `pharmax` — multi-part application with backend/frontend, env, deployment, persistence, role workflows
- `autopahe` — CLI/package/tooling project with config, docker, release notes, caching, browser automation
- `organize` — much smaller script/tool style project

That means the models must be typed enough to be useful, but not so rigid that they only fit one project family.

## Corrected build order

## Phase 1 — schema-grounded shared base

Goal:
Build typed shared models from the common schema layer first.

Work:
- model `frame.schema.yaml` shared defs in Pydantic
- start with:
  - frame header
  - refs / links
  - evidence
  - ambiguity / blocker / required-evidence style shared entries where already defined
- confirm which shared defs are mature enough to encode directly and which need revision notes

Why first:
This gives all five files one real foundation.

## Phase 2 — five file models

Goal:
Create one Pydantic model per FRAME file.

Models:
- `FactsFile`
- `RulesFile`
- `ActsFile`
- `MapFile`
- `ExpectFile`

Each model should mirror the current schema shape first, not reinterpret it into a generic entry list.

Meaning:
- `facts.identity`, `facts.classification`, etc. should stay recognizably facts-shaped
- `rules.commands`, `rules.stop_and_ask`, etc. should stay rules-shaped
- `map.roots`, `map.paths`, etc. should stay map-shaped

Why:
The current schemas are file-specific. The implementation should respect that before abstracting.

## Phase 3 — umbrella FRAME model

Goal:
Compose the five file models into one project-level Python model.

Candidate:
- `FrameSet`
  - `facts: FactsFile`
  - `rules: RulesFile`
  - `acts: ActsFile`
  - `map: MapFile`
  - `expect: ExpectFile`

This umbrella model is the architecture center for `frame-python`.

## Phase 4 — YAML loading and file validation

Goal:
Load actual FRAME YAML files and validate them against both:
- the source JSON/YAML schemas
- the Pydantic models

Important rule:
FRAME is file-first here.
So YAML matters early, not later.
JSON can still be useful for tests, but YAML is part of the real product surface.

## Phase 5 — cross-file references and graph layer

Goal:
Add the connected-system behavior described by the roadmap.

Examples:
- refs/links validation
- broken cross-file reference reporting
- rule activation from facts
- expect ↔ acts verification linkage
- map ↔ facts/rules linkage

This is where graph-like behavior starts to make sense.
Not before the five typed files and umbrella model exist.

## Phase 6 — example-project pressure

Goal:
Use `example_projects/` throughout development, not as an afterthought.

Suggested sequence:
1. tiny/simple project (`organize`)
2. CLI/tooling project (`autopahe`)
3. app/system project (`pharmax`)

Why:
If FRAME only works for one family, the architecture is lying to us.

## What happens to the current generic slice

The current small dataclass-based `frame-python` slice should be treated as a temporary spike, not the main architecture.

It proved a few tiny things:
- test wiring works
- minimal loading/validation loop works
- fixture-driven development flow is fine

But it should not become the core design center.

## Immediate next coding move

The next serious implementation task should be:

1. create shared Pydantic models from `schemas/frame.schema.yaml`
2. create the first typed file model pair from real schemas
   - likely `FactsFile` and `RulesFile` first only as an initial implementation slice
   - but designed within the all-five-file architecture, not as isolated forever work
3. add YAML loading
4. validate real sample files from `example_projects/`

## Release/theme guidance

Do not treat every commit like a new minor line.
Use themed milestone lines.

Recommended near-term theme:
- `0.1.x` = schema-grounded modeling line

Suggested patch progression within `0.1.x`:
- `0.1.1` shared schema/base models
- `0.1.2` first typed file models
- `0.1.3` umbrella composed model
- `0.1.4` YAML loader + schema validation
- `0.1.5` initial cross-file graph/reference checks

Only open `0.2.0` when the theme changes meaningfully.
For example:
- `0.2.x` = example-project pressure / evaluation line

## Honest correction

The previous implementation work was not useless, but it was too generic relative to the intended architecture.
The corrected path is schema-centered, file-centered, and composition-first.
