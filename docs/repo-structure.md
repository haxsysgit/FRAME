# FRAME Repo Structure

This repo is the umbrella home for FRAME as a standard-in-progress.
It is not just a single-language package repo anymore.

## Root responsibilities

The root repo should contain:
- docs
- learn material
- research
- scripts
- tests
- fixtures/examples
- language-specific implementation tracks

## Current intended structure

- `docs/`
  - canonical architecture and direction docs
- `learn/`
  - concept teaching, examples, and educational material
- `research/`
  - raw and refined research, comparisons, archived thinking
- `tests/`
  - future contract fixtures, project-family evals, token-efficiency evals, portability evals
- `scripts/`
  - helpers for validation, setup, release, fixture generation, and experiments
- `frame-python/`
  - fresh Python implementation track

## Future structure

Over time this repo may also include:
- `frame-js/`
- `frame-ts/`
- `frame-c/`
- `frame-cpp/`

Those should appear only when there is enough maturity to justify them.

## What was removed during the reset

The previous active implementation-shaped areas were removed from the root path because they encoded assumptions that should no longer lead the project:
- old SDK path
- old lab implementation path
- old makeframe artifacts
- old version-pinned schema folder

That does not mean the ideas were useless.
It means they should not masquerade as the new foundation.

## Reset note

This repo reset was intentional.
The previous implementation path had started to lead the architecture too much, so the code and schema-shaped foundation were removed from the active root.

What replaced it is an umbrella structure centered on:
- clearer architecture docs
- research and evaluation
- tests and fixtures
- a fresh `frame-python` implementation track
