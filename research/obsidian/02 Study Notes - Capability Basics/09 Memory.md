---
tags:
  - concept/core
  - memory
  - study/basics
---

# Memory

## Tiny Idea

Memory is useful state that survives beyond one model response.

For agents, memory is not just chat history.

## Useful Memory

Good memory records:

- decisions
- blockers
- verified changes
- commands run
- files touched
- risks left behind
- why a path was chosen

## Bad Memory

Bad memory records:

- vague summaries
- stale assumptions
- raw replay dumps
- unverified claims
- hidden reasoning noise
- old context that overrides new truth

## Haxaml Connection

`acts.yaml` should record what actually happened.

It should not become a giant chat transcript.

Hot Acts should be the scoreboard.

Archive can be the replay folder.

## Practical Rule

> Memory helps only when it stays current, short enough to use, and tied to proof.

Related:

- [[10 Compaction]]
- [[04 Long Context Reality Check]]
- [[06 What This Means For FRAME And Haxaml]]
