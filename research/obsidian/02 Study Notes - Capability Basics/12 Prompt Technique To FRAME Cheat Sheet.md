---
tags:
  - study/path
  - frame/mapping
  - prompt-engineering
---

# Prompt Technique To FRAME Cheat Sheet

## Tiny Idea

Prompt techniques are not all the same kind of thing.

Some are project truth.
Some are task setup.
Some are provider tricks.
Some should be thrown away after the session.

## The Cheat Sheet

| Prompt technique | FRAME/Haxaml home |
| --- | --- |
| project identity | `facts.yaml` |
| agent behavior rules | `rules.yaml` |
| hard constraints | `rules.yaml` |
| task goal | `expect.yaml` |
| done criteria | `expect.yaml` |
| past decisions | `acts.yaml` |
| file routing | `map.yaml` |
| examples that always matter | `rules.yaml` or docs |
| examples only for this run | runtime context |
| provider wording | adapter |
| output format | adapter + `expect.yaml` |
| verification proof | `acts.yaml` |
| raw reasoning | do not store as canonical state |

## Simple Rule

> If every future agent should trust it, put it in FRAME. If only this provider needs the wording, put it in an adapter.

Related:

- [[02 Technique Mapping Table]]
- [[13 FRAME File Roles]]
- [[14 Runtime Context Assembly]]

