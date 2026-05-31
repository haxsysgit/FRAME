# FRAME Lab Plan

This document describes how FRAME should mature after the reset.

The old lab direction leaned too hard on extending an existing implementation path.
The new direction is broader and more disciplined.

## The new job of FRAME Lab

FRAME Lab should help answer:
- what parts of FRAME survive real project-family testing?
- what parts of the current five-part design are strong vs weak?
- what schema choices are actually justified?
- what normalized model shape works best for implementation?
- how helpful is FRAME compared to native agent docs alone?
- how token-efficient is FRAME compared to more ad hoc approaches?

## Main workstreams

### 1. Contract clarification

Before rebuilding too much code, the project needs sharper answers about:
- stable concepts
- provisional concepts
- file/model boundaries
- validation boundaries
- core vs implementation-specific behavior

### 2. Project-family evaluation

Collect multiple project examples such as:
- CLI
- backend API
- web app
- monorepo
- infra/tooling repo
- mixed enterprise codebase

Then test:
- does the candidate FRAME structure fit naturally?
- what feels forced?
- what is missing?
- what becomes too verbose?

### 3. frame-python implementation track

`frame-python` should be the first fresh implementation track.
Its job is not just to “recreate the old SDK.”
Its job is to pressure-test the reset architecture.

Questions `frame-python` should help answer:
- what should the normalized model look like?
- what needs strict validation?
- what should stay provisional for now?
- which assumptions from the old implementation were actually useful?
- which ones should be abandoned?

### 4. Schema iteration

Schema work should happen after architecture clarification and example pressure-testing.
The schema should be revised only when it reflects earned understanding, not premature certainty.

### 5. Evaluation suite

This repo should eventually contain a real evaluation setup that compares FRAME against alternatives.
That should include:
- project-family fixtures
- context quality checks
- consistency checks across tools/agents
- token efficiency comparisons
- usefulness comparisons against native agent-doc approaches

## Practical near-term order

1. refine the architecture docs
2. define candidate invariants
3. gather project fixtures
4. sketch the first fresh `frame-python` model direction
5. write/revise schema candidates
6. build tests and evaluations around that work

## What not to do

Do not let the rebuild collapse back into:
- blindly restoring the old SDK
- freezing old schema choices too early
- designing only for Haxaml
- assuming one repo shape proves the architecture

## Bottom line

FRAME Lab now exists to help the project earn its contract through examples, evaluation, and careful implementation — not just through elegant-sounding architecture notes.
