# frame-python v0.1 scope

This file turns the blueprint into a practical first-build boundary.

## v0.1 goal

Build the smallest useful Python implementation that helps clarify the FRAME contract.

It should:
- load candidate FRAME data from Python dicts and JSON files
- normalize into one top-level Python document model
- preserve unknown structure instead of silently deleting it
- support strict vs provisional validation modes
- produce reports that show contract gaps clearly
- run against a small multi-project fixture set

It should not:
- declare the schema final
- declare the five-part model frozen forever
- recreate the old SDK surface
- implement runtime/lifecycle behavior
- become Haxaml-shaped
- promise canonical on-disk layout too early

## v0.1 deliverables

1. package skeleton under `src/frame_python/`
2. first candidate normalized model
3. loader for dict + JSON file input
4. validation/reporting surface
5. at least 3 starter fixtures
6. tests for strict/provisional behavior and contract-gap reporting

## minimal public surface

Expected first surface:
- `load_frame(data)`
- `load_frame_file(path)`
- `validate_frame(frame, mode=...)`
- `ValidationReport`

## first decision rules

When in doubt during v0.1:
- prefer preserving unknown data over coercing it away
- prefer explicit warnings over fake certainty
- prefer narrow invariants over broad premature strictness
- prefer proving value with fixtures over designing a giant ontology

## exit criteria for v0.1 planning phase

Before serious implementation starts, we should be able to answer:
- what the first normalized model looks like
- what the loader accepts initially
- what strict validation really means
- what stays provisional
- what the first fixtures are
