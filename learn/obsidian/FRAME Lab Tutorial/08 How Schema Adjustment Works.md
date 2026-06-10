# How Schema Adjustment Works

Schema adjustment should be conservative.

## Tiny idea

When a repo feels awkward, the first answer should not be “add more schema.”
The first answer should be “what exact pressure is repeating?”

## What earns a change

A change earns its place when:
- the same pain shows up across multiple fixtures
- the change improves fit without causing new duplication
- the change helps tools or humans materially
- the change does not bloat the core

## What 0.2.0 changed

The 0.2.0 line earned changes like:
- simpler names
- stronger typed cross-links
- narrower, clearer Acts role
- better retrieval hooks in Acts
- cleaner proof separation through `checks_seen` and `checks_ran`

## What a bad adjustment looks like

A bad change usually:
- solves only one fixture’s weirdness
- creates new repetition
- makes authoring harder without better decisions
- adds clever vocabulary that hides simple meaning

## Rule of thumb

If a change mostly makes the schema look smarter, it is probably the wrong change.
If it makes fitting, retrieval, proof, or review better across multiple repos, now it is interesting.
