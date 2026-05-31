---
tags:
  - research/topic-1
  - frame/future
  - haxaml
---

# What This Means For FRAME And Haxaml

## Tiny Idea

FRAME should become the project context architecture.

Haxaml should become one implementation that reads FRAME, builds useful agent context, blocks unsafe work, and records proof.

## What Research 1 Supports

Research 1 supports this:

> Better context structure should improve the chance that agents do useful work.

It does **not** prove this:

> FRAME's exact current design is final.

That second claim needs Research 2, Research 3, Research 4, and real tests.

## FRAME As Context Roles

| FRAME part | Plain role | Context-engineering job |
| --- | --- | --- |
| Facts | stable truth | stop the agent guessing project identity |
| Rules | hard constraints | keep behavior consistent |
| Acts | recorded reality | continue work without raw chat replay |
| Map | file and impact guide | help fetch likely relevant files |
| Expect | expected path | define target, milestones, and done conditions |

## Haxaml As Runtime

Haxaml should handle:

- setup
- context selection
- missing-info gates
- context pack creation
- verification
- record writing
- adapter generation

Analogy:

> FRAME is the organized garage. Haxaml is the person who hands the mechanic the right tools, checks the repair, and writes the service log.

## What To Be Careful About

| Risk | Why it matters |
| --- | --- |
| Turning FRAME into a mega-prompt | It would recreate the mess it is trying to fix. |
| Storing raw reasoning traces | It can leak noise and false confidence into project state. |
| Treating Expect as magic | Expected plans need evidence before progress is marked. |
| Letting Acts bloat | History must stay useful, not become a replay dump. |
| Forgetting source priority | Old memory should not override hard rules. |

## Clean `0.8` Direction

For `0.8`, use Research 1 as the ground:

1. Define FRAME roles in plain language.
2. Define context policies for fields.
3. Define what blocks work.
4. Define what must stay exact.
5. Define what can be summarized.
6. Define how evidence moves into Acts.
7. Define when Expect can be marked or changed.
8. Test against simpler approaches like `AGENTS.md` only.

## One-Sentence Positioning

> FRAME is not a prompt. FRAME is the repo-owned context model that prompts, agents, and tools can safely build from.
