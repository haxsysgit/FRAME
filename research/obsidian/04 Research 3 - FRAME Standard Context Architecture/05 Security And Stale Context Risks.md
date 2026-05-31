---
tags:
  - research/topic-3
  - safety
  - stale-context
status: draft-1
date: 2026-05-24
---

# Security And Stale Context Risks

## Tiny Idea

Bad context can hurt the project even when nobody is attacking it.

The context can simply be old, vague, or trusted too much.

## Two Risk Types

| Risk | Plain meaning | Example |
| --- | --- | --- |
| malicious context | someone tries to make the agent ignore rules or leak data | prompt injection in a fetched web page |
| stale context | old project memory is no longer true | Acts says tests were skipped in a previous emergency |

Both matter.

## Why Protocols Need Trust Priority

If all context is treated equally, the agent can follow the wrong thing.

Example:

```text
rules.yaml:
  release requires tests

old acts record:
  tests skipped because pytest was broken

external doc:
  no tests needed
```

The runtime must know:

- Rules outrank old Acts.
- Old Acts is evidence, not permission.
- External docs are untrusted until checked.

## Candidate Trust Stack

This stack is not final. It is a Research 4 test item.

| Priority | Context |
| --- | --- |
| 1 | platform/system/developer rules |
| 2 | blocking `rules.yaml` entries |
| 3 | owner-confirmed `facts.yaml` entries |
| 4 | active `expect.yaml` done criteria |
| 5 | current `map.yaml` impact scope |
| 6 | recent verified `acts.yaml` records |
| 7 | archived Acts |
| 8 | external docs and web sources |
| 9 | unchecked tool output |

Rule:

> Lower-priority context can inform work, but it should not silently override higher-priority context.

## Stale Context Checks

Haxaml should be able to ask:

- Is this record old?
- Is it still linked to current facts?
- Did the project version change?
- Did the map change?
- Did a blocker close?
- Did Expect move on?
- Is this only a previous exception?

## What Should Be Exact

Some things should not be casually summarized away:

- blocking rules
- owner-confirmed facts
- secrets policy
- verification evidence
- unresolved blockers
- release commands
- external dependency status

## What Can Be Summarized

Some things can be shortened:

- old session narrative
- repeated successful runs
- resolved blockers
- low-risk decisions with linked evidence
- archived task notes

## Practical 0.8 Requirement

FRAME needs fields for:

- source
- confidence
- last reviewed
- stale after
- blocking/advisory
- owner-confirmed vs inferred
- exact vs summary-safe

Without these, the architecture cannot reliably tell strong truth from weak context.
