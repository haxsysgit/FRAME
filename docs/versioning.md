# FRAME Versioning and Tags

This document defines how FRAME versions should work while the project is still maturing.

## Core idea

A FRAME version is a milestone in the evolution of the standard, not just a random code snapshot.

That means tags should mainly mark:
- architectural milestones
- contract/schema direction changes
- meaningful implementation/evaluation progress
- release-quality package states later on

## Naming format

Use semantic-version-style tags:
- `v0.x.y` while FRAME is still pre-1.0
- `v1.0.0` when the core contract and evaluation story are mature enough to call the project stable

## What versions mean right now

While pre-1.0:

- `v0.MINOR.0`
  - significant project milestone
  - major doc/architecture reset
  - meaningful contract shift
  - new implementation phase opening

- `v0.MINOR.PATCH`
  - smaller but real improvements within the same milestone
  - clarified docs
  - validation improvements
  - fixture/test expansion
  - non-breaking package progress

## Pre-release tags

Use pre-release tags when a milestone is real but clearly not stable enough for a plain release.

Recommended format:
- `v0.1.0-alpha.1`
- `v0.1.0-beta.1`
- `v0.1.0-rc.1`

Suggested meaning:
- `alpha`
  - architecture/implementation still moving a lot
- `beta`
  - shape is more settled and wider testing has started
- `rc`
  - candidate for the next stable milestone if verification goes well

## FRAME-specific guidance

During this phase, tag when one of these happens:
- the core FRAME definition materially changes
- the candidate part model materially changes
- schema direction changes in a meaningful way
- `frame-python` reaches a meaningful executable milestone
- evaluation harness/fixtures become meaningfully stronger

Do not tag for every small commit.
Tags should mean something when someone reads the history later.

## Language-package relation

Right now the repo is a monorepo-in-progress.
So repo tags are FRAME-wide milestone tags.

Later, if language implementations split into their own repos, they can have their own package release tags.
Until then:
- repo tags = FRAME milestone tags
- package versions inside `frame-python` can stay lightweight and pre-1.0

## Recommended current baseline

The current reset-and-rebuild state is best treated as:
- `v0.1.0-alpha.1`

Why:
- the architecture reset is real
- the repo structure has been intentionally reset
- docs are now unified
- `frame-python` has a defined lane
- but the implementation is still early and clearly unstable

## Release note habit

For each tag, record:
- what changed in the FRAME definition
- what changed in docs/schema direction
- what changed in implementations
- what was verified
- what remains provisional

That will matter a lot later when comparing milestone quality honestly.
