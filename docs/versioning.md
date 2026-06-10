# FRAME Versioning

## Naming format

Semantic-version-style tags:
- `v0.x.y` while FRAME is still pre-1.0
- `v1.0.0` when the core contract and evaluation story are mature

## What versions mean

- `v0.MINOR.0`  --  significant milestone: major doc/architecture shift, contract change, new implementation phase
- `v0.MINOR.PATCH`  --  smaller improvements within the same milestone: clarified docs, validation improvements, fixture/test expansion

## Release rhythm

- Stay inside a themed minor line. Use patch releases for progress within that theme.
- Only bump minor when the project theme changes meaningfully.
- Do not tag for every small commit. Tags should mean something.

## FRAME-specific guidance

Tag when:
- the core FRAME definition materially changes
- schema direction changes in a meaningful way
- `FrameSDK` reaches a meaningful executable milestone
- evaluation harness/fixtures become meaningfully stronger

## Current baseline

Current target: **v0.3.0**  --  schema finalization, JSON/YAML schemas, FrameSDK Python SDK rebuild.

Previous lines:
- v0.2.0  --  simplified naming, stronger cross-links, Acts as run history
- v0.1.0  --  initial five-part candidate, early Frame Lab rounds
- v0.0.x  --  exploration and initial architecture
