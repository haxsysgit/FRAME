---
tags:
  - research/topic-3
  - subagents
  - synthesis
status: draft-2
date: 2026-05-24
---

# Schema Research Team Synthesis

## Tiny Idea

The first pass went too far.

FRAME should not act like a runtime engine.

FRAME is the static context shape: five files with clear meanings. Haxaml, Codex, Claude, or any other tool can read those files and do the active work.

Analogy:

> FRAME is the labeled map on the wall. Haxaml is the person using the map to drive.

The map should be useful enough to guide the driver, but it should not pretend to drive the car.

## Corrected FRAME Roles

| File | Simple job | What it must not become |
| --- | --- | --- |
| `facts.yaml` | The stable base truth of the project: identity, stack, purpose, broad shape. | A guessed README, marketing doc, or runtime memory dump. |
| `rules.yaml` | The rules a tool or agent must obey while working. | A file that changes because one run happened. |
| `acts.yaml` | A record of what actually happened, including proof, blockers, decisions, and handoff notes. | A source of new rules or permanent project truth by itself. |
| `map.yaml` | A short repo map: what files or areas do, at a glance. | A verbose documentation site or a stale fake map. |
| `expect.yaml` | The planned direction, expected runs, and done checks. | A rigid prophecy. Actual work can take another path if it still reaches the high-level goal. |

## The Biggest Correction

Rules do not get rewritten by Acts.

Acts should follow Rules, and recorded Acts should be checked against Rules.

Better wording:

| Old wording | Better idea |
| --- | --- |
| `Rules -> Acts`: proof before record | `Rules -> Acts`: Acts entries should be valid under Rules before they are trusted. |
| `Acts -> Rules`: history can shape rules | Avoid this early. Past work may reveal that Rules need human review, but Acts should not silently create or change Rules. |
| `Acts -> Expect`: verified work updates Expect | A tool may mark checklist progress in Expect using verified Acts. FRAME itself only provides the structure. |

That keeps FRAME static and honest.

## Map Needs Extra Care

`map.yaml` is dangerous when it is wrong.

If Facts is slightly incomplete, an agent can still inspect files.

If Map says the wrong thing about where logic lives, it can send the agent to the wrong part of the repo and poison the whole context.

So Map should be simple, strict, and easy to refresh:

| Map entry | Meaning |
| --- | --- |
| `path` or `paths` | The file or folder being described. |
| `summary` | One short, accurate explanation of what it does. |
| `kind` | The rough type: app, package, module, screen, command, config, test, docs, generated, vendor. |
| `touch_when` | When an agent should inspect this area. |
| `check_when_changed` | What should be checked if this area changes. |
| `confidence` later | How sure the map is. This likely belongs after the evidence/source slice. |

The map should feel like:

```text
src/cart/ -> cart pricing and item updates
src/payments/ -> payment provider integration
tests/cart/ -> cart behavior tests
```

Not like:

```text
src/cart/ -> massive design essay with five kinds of policy
```

## Team Findings, Cleaned Up

| File | Strongest recommendation |
| --- | --- |
| Facts | Keep the first slice small: identity, project type, lifecycle stage, stack, unknowns. |
| Rules | Keep rules stable. Rules can be active or inactive, but Acts should not rewrite them. |
| Acts | Keep a checked activity record: work, verify, blocker, decision, handoff. |
| Map | Store accurate repo summaries at a glance. Wrong summaries are worse than missing summaries. |
| Expect | Store the expected direction and done checks. Treat it like a roadmap, not a prison. |

## Better Connection Model

FRAME files should connect by meaning, not by constant automatic updates.

| Connection | Correct meaning |
| --- | --- |
| Facts -> Rules | Stable facts can make some rules relevant. Example: a Python project activates Python command rules. |
| Facts -> Map | Facts can explain the broad project shape, but Map still needs direct repo inspection. |
| Rules -> Acts | Acts must be checked against Rules before a tool trusts the record. |
| Map -> Agent/tool | Map tells the tool where to look first. The tool still verifies by reading real files. |
| Expect -> Agent/tool | Expect gives the high-level goal and likely work path. It is guidance, not a forced script. |
| Acts -> Expect | A tool may mark checklist progress from verified Acts. The plan should not pretend every real run matched the original guess. |

## What Should Stay Local

Not every entry needs a cross-file link.

| File | Good local-only data |
| --- | --- |
| Facts | repository URL, human owner, broad product context |
| Rules | severity wording, escalation classes, forbidden action list |
| Acts | failed attempt note, short handoff note, temporary workaround |
| Map | ignore paths, generated paths, vendor folders, aliases |
| Expect | estimated runs, soft sequencing, notes, rough priority |

This is the sweet spot:

> connected enough to guide agents, static enough that another tool can implement it, simple enough that a human can edit it.

## 0.8.0 Recommendation

Start with the smallest shared shape across all five files.

Do freeze:

- shared `frame` block
- clear file role for each FRAME file
- minimal valid empty body per file
- simple IDs where lists exist
- explicit unknowns so agents do not guess
- Map as short repo summaries, not full documentation

Do not freeze yet:

- heavy cross-file reference syntax
- automatic rule changes from activity history
- complex runtime behavior
- final evidence/confidence model
- full archive behavior
- exact Expect progress sync behavior

The clean 0.8 opening is:

> FRAME defines the stable context shelves. Haxaml and other tools decide how to use those shelves while doing real work.
