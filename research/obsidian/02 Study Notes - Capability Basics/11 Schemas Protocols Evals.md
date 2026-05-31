---
tags:
  - concept/core
  - schema
  - protocol
  - evals
  - study/basics
---

# Schemas, Protocols, And Evals

## Tiny Idea

If FRAME should become more than a Haxaml habit, it needs:

- schemas
- protocol rules
- evals

## Schema

A schema says what shape data must have.

Example:

```yaml
acts:
  completed_tasks:
    - name: "setup wizard"
      status: "verified"
```

A schema can say:

- `completed_tasks` must be a list
- every item needs a name
- status must be one of a few allowed values

## Protocol

A protocol says how tools should behave around the data.

Bad protocol:

```text
Put rules in rules.yaml.
```

Better protocol:

```text
Rules have higher priority than retrieved context.
Blocking missing materials stop build.
Acts records proof after verification.
Expect tracks planned progress but is not the automatic end of every run.
```

## Eval

An eval is a test for whether the system works.

For FRAME, evals could compare:

- `AGENTS.md` only
- static FRAME docs
- Haxaml governed context packs

Metrics:

- task success
- tests passed
- files read
- files touched
- context size
- handoff quality
- stale-memory failures

## Haxaml Connection

Haxaml can be the reference implementation.

FRAME can become the standard context architecture.

Evals decide whether the architecture is actually useful.

## Practical Rule

> If another tool cannot understand FRAME from the docs and schemas, it is not a standard architecture yet.

Related:

- [[06 What This Means For FRAME And Haxaml]]
- [[07 Claims Evidence Unknowns]]
