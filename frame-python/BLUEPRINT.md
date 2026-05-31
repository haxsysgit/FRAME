# frame-python v0.1 blueprint

This blueprint is for the fresh `frame-python` track after the reset.
Its job is to test and clarify the FRAME contract, not to freeze it too early.

## Design intent

`frame-python` should act as:
- a normalized-model experiment bed
- a validator for clearly earned invariants
- a fixture runner for project-family examples
- a reporter of underspecified contract areas

It should not act as:
- the owner of FRAME meaning
- a full old-SDK recreation
- a schema-first code generator pipeline
- a runtime-specific interpretation of FRAME canon

## Recommended package layout

Keep the first layout small and biased toward fixtures/tests rather than feature surface.

```text
frame-python/
  pyproject.toml
  README.md
  BLUEPRINT.md
  src/
    frame_python/
      __init__.py
      model.py
      validate.py
      load.py
      report.py
      provisional.py
  tests/
    test_model_minimal.py
    test_validate_strict_vs_provisional.py
    test_fixture_roundtrip.py
    test_contract_gaps_are_reported.py
  fixtures/
    minimal-cli/
      frame.json
      notes.md
    backend-api/
      frame.json
      notes.md
    monorepo-slice/
      frame.json
      notes.md
  examples/
    inspect_fixture.py
```

## Why this layout

- `model.py`
  - holds the first normalized Python types
  - one top-level model, nested language-native submodels beneath it
- `validate.py`
  - enforces only the invariants the reset docs already justify
- `load.py`
  - converts JSON/YAML/dict input into the normalized model without assuming disk layout canon
- `report.py`
  - emits human-usable findings: strict errors, provisional warnings, unknown areas
- `provisional.py`
  - central place for explicitly non-final assumptions and feature flags
- `fixtures/`
  - package-local experiments that back model and validation decisions
- `tests/`
  - package behavior tests, distinct from root-level future cross-language contract/eval tests

## v0.1 scope

v0.1 should be intentionally narrow.

1. Load a candidate FRAME document from Python dict plus one file format on disk.
   - Prefer JSON first.
   - YAML can wait unless it is trivial.

2. Materialize one top-level `FrameDocument` model with nested optional parts.

3. Support the candidate five-part structure as named fields:
   - `facts`
   - `rules`
   - `acts`
   - `map`
   - `expect`

4. Treat those parts as candidate structure, not permanent truth.
   - Presence may be optional in v0.1.
   - Unknown extra fields should be preserved or surfaced, not discarded silently.

5. Implement two validation modes:
   - `strict`
   - `provisional`

6. In `strict`, only validate very safe invariants such as:
   - top-level document must be object-like
   - known parts, if present, must have expected container shape
   - entry ids, if present, must be unique within a part
   - obviously malformed types are errors

7. In `provisional`, allow underspecified shapes but produce warnings such as:
   - candidate part missing
   - freeform field not yet normalized
   - ambiguous value shape
   - probable concept overlap between parts

8. Add reporting that makes contract gaps visible.
   - Example: "`expect` entry uses fields not modeled yet; preserved as extension payload"

9. Use fixtures from multiple project families from day one.
   - even if small
   - even if incomplete

## What to explicitly avoid in v0.1

Do not add these yet:

- no full schema compilation/generation pipeline
- no promise that file paths or export layout are canonical
- no aggressive coercion from messy input into "valid" model state
- no giant field inventory inherited from old implementation
- no lifecycle engine or automation runtime semantics
- no Haxaml-specific affordances in the core model
- no plugin system
- no graph database abstraction
- no repo scanner that tries to infer FRAME automatically
- no cross-file reference system unless a fixture proves it is already needed
- no stable public API beyond the small load/validate/report surface
- no claim that five parts are mandatory or final

These are exactly the kinds of choices that would let implementation capture the contract too early.

## First candidate Python model/interface

Start with one top-level document and one generic reusable part-entry type.
That is enough to test normalization pressure without pretending the full ontology is settled.

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True)
class FrameEntry:
    id: str | None = None
    title: str | None = None
    summary: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    extensions: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class FramePart:
    entries: list[FrameEntry] = field(default_factory=list)
    extensions: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class FrameDocument:
    facts: FramePart | None = None
    rules: FramePart | None = None
    acts: FramePart | None = None
    map: FramePart | None = None
    expect: FramePart | None = None
    extensions: dict[str, Any] = field(default_factory=dict)
```

Recommended initial interface:

```python
from frame_python.load import load_frame, load_frame_file
from frame_python.validate import validate_frame
from frame_python.report import ValidationReport

frame = load_frame(data)
report = validate_frame(frame, mode="provisional")
```

Why this is the right first cut:
- it matches the doc direction toward one top-level FRAME model
- it allows nested language-native models later
- it preserves unknown structure instead of deleting it
- it is typed enough to expose weak spots
- it does not pretend candidate part semantics are already final

## Validation boundary for v0.1

Strict validation should only cover earned invariants.

Recommended strict invariants:
- top-level must be a mapping/object
- each known part is absent or object/list shape accepted by loader rules
- normalized part entries become a list
- entry payload must remain mapping-like after normalization
- duplicate non-null ids inside the same part are errors
- unsupported scalar where structured entry is required is an error

Recommended provisional findings:
- part omitted
- part present but only freeform text available
- unknown top-level key preserved in extensions
- entry shape loaded via fallback normalization
- field appears in many fixtures but lacks normalized slot

This gives `frame-python` a useful role in clarifying strict vs provisional boundaries from `docs/schema.md`.

## First evaluation fixtures/tests to add

Add a very small fixture set immediately. The point is not coverage volume; it is comparative pressure.

### Fixture 1: minimal-cli
Use a tiny single-package CLI project example.

Should test:
- minimal viable FRAME document
- `facts` and `rules` can carry useful reality even when other parts are sparse
- omitted parts produce warnings, not failure

### Fixture 2: backend-api
Use a service-style project with runtime and persistence concerns.

Should test:
- `facts` can hold stack/runtime truth
- `expect` can express correctness/verification expectations
- distinction between project truth and behavioral rules is understandable

### Fixture 3: monorepo-slice
Use a deliberately partial monorepo slice.

Should test:
- FRAME can represent current structured reality without requiring whole-repo completeness
- `map` pressure: navigation and boundaries matter
- unknowns/partial coverage are first-class reportable conditions

### First tests

1. `test_model_minimal.py`
   - load smallest acceptable candidate document
   - assert top-level model exists
   - assert unknown keys survive in `extensions`

2. `test_validate_strict_vs_provisional.py`
   - same fixture yields warnings in provisional mode
   - malformed shapes fail in strict mode

3. `test_fixture_roundtrip.py`
   - load fixture file, normalize, serialize back to dict
   - confirm semantic preservation for known and unknown fields

4. `test_contract_gaps_are_reported.py`
   - feed intentionally ambiguous entries
   - assert report includes explicit provisional findings instead of silent coercion

5. `test_duplicate_ids_per_part.py`
   - duplicate ids within one part error
   - same id across different parts remains undecided unless architecture later says otherwise

6. `test_partial_monorepo_fixture.py`
   - confirms incomplete repo slices are acceptable and visibly incomplete, not invalid by default

## Where root-repo tests should differ later

Keep `frame-python/tests/` focused on package behavior.
Later, use root `tests/` for repo-wide contract and cross-implementation evaluation such as:
- shared project-family fixtures
- contract conformance suites
- token-efficiency comparisons
- usefulness comparisons against native-agent-doc baselines

## Practical v0.1 milestone definition

v0.1 is ready when all of these are true:
- can load a candidate FRAME document into one normalized Python model
- can validate in strict and provisional modes
- can preserve unknown structure instead of destroying it
- can run against at least three small project-family fixtures
- can produce reports that reveal underspecified contract areas

If a proposed feature does not help one of those goals, it probably belongs after v0.1.
