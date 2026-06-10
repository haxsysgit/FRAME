# Current State And Next Moves

This is where Frame Lab stands right now.

## Current active line

FRAME is currently on the active 0.2.0 candidate line.

Important split:
- FRAME 0.2.0 is the active contract line
- Haxaml is a future major consumer and pressure source
- those are related, but not the same thing

## Current audited fixture round

The active committed 0.2.0 round has fit outputs for:
- `organize`
- `autopahe`
- `pharmax`

Each has five fit files:
- `facts.yaml`
- `rules.yaml`
- `map.yaml`
- `expect.yaml`
- `acts.yaml`

That gives 15 fit files total.

## Current score result

The audited 0.2.0 round scored:
- `organize`: 4.25 / 5
- `autopahe`: 4.35 / 5
- `pharmax`: 4.49 / 5

Weighted average: 4.36 / 5.

That is strong enough to treat 0.2.0 as the best line so far.
Not final, but clearly stronger.

## What the line now holds

0.2.0 now stands for:
- simpler names
- stronger cross-link discipline
- cleaner ownership of truth
- Acts as retrieval-friendly run history
- clearer proof honesty with `checks_seen` and `checks_ran`
- stronger design pressure from future typed tools

## Best next moves

1. tighten authoring rules for `work_kind`, `keywords`, touched refs, and proof fields
2. run more fixtures closer to haxjobs and dashboard-style app realities
3. turn the strongest parts into better typed models in `FrameSDK`
4. keep refusing schema growth unless repeated evidence forces it

## Main lesson

The next goal is not “more schema.”
The next goal is “more usefulness per field.”

That is the real direction.
