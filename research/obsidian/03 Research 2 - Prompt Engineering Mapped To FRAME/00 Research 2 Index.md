---
tags:
  - research/topic-2
  - prompt-engineering
  - frame/mapping
status: draft-1
date: 2026-05-23
---

# Research 2 Index: Prompt Engineering Mapped To FRAME

## Tiny Idea

Research 2 asks a practical question:

> Can the prompt and context techniques people already use with LLMs be turned into clean FRAME roles?

The short answer from this pass:

> Yes, many of them map cleanly, but only if FRAME does not try to store every prompt trick.

Analogy:

- Prompt engineering is the note you give one driver before one trip.
- FRAME is the road signs, map, traffic rules, trip log, and destination board that every driver can reuse.
- Haxaml is the dispatcher that decides which signs and logs matter for this trip.

## Read In This Order

1. [[01 Full Report - Prompt Engineering Mapped To FRAME]]
2. [[02 Technique Mapping Table]]
3. [[03 FRAME As Structured Prompt Memory]]
4. [[04 Haxaml As Runtime Context Engine]]
5. [[05 Weak Mappings And Boundaries]]
6. [[06 Schema Adapter Runtime Docs Split]]
7. [[07 Research 2 Claims Evidence Unknowns]]
8. [[90 Research 2 Sources]]

## Main Outcome

FRAME works best when it stores durable project context:

| Durable thing | FRAME home |
| --- | --- |
| project identity | `facts.yaml` |
| hard rules | `rules.yaml` |
| real work history | `acts.yaml` |
| file/module routing | `map.yaml` |
| future path and done checks | `expect.yaml` |

FRAME should not become a giant prompt graveyard.

Provider-specific wording, temporary examples, UI tone, raw reasoning traces, and one-off prompt hacks should stay in adapters, runtime prompts, or session output.

## Why This Matters For 0.8

Research 2 gives Haxaml a sharper design rule:

> FRAME should store reusable project truth. Haxaml should assemble task-specific context from it. The generated prompt is output, not the source of truth.

That sentence is small, but it is a big deal for standard architecture design.
