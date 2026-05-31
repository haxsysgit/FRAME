# FRAME

FRAME is an umbrella repo for defining, researching, testing, and eventually implementing a portable standard for representing AI-assisted project reality.

Right now, this repo is in reset mode.
The old implementation and schema assumptions were removed so the project can be rebuilt around the clearer definition we agreed on.

## What FRAME is trying to become

FRAME is not just "memory for agents."
It is a structured architecture for representing current project reality in a way that helps different agents and tools behave more consistently inside the same project.

The point is to reduce:
- repeated prompting
- scattered truth across AGENTS.md / CLAUDE.md / chats / docs
- context rot
- hallucinated certainty from stale or partial context
- full-repo rescans as the default way to understand a project

The real target is:
- more predictable agent behavior
- better portability across tools
- stronger validation and governance
- a cleaner contract between project truth and runtime tooling

## Current repo role

This root repo is the umbrella home for:
- docs
- learn material
- research
- scripts
- tests and fixtures
- implementation tracks for different languages

This repo should eventually support multiple language implementations such as:
- `frame-python`
- `frame-js`
- `frame-ts`
- `frame-c`
- `frame-cpp`

But for now the active implementation focus is:
- `frame-python`

## Important reset note

The previous Python SDK, schema set, and related experimental implementation code were intentionally removed from the active repo structure.

Why:
- the older implementation encoded assumptions that may no longer match the clearer FRAME definition
- the schema likely needs revision
- the implementation should be rebuilt from the new contract, not patched indefinitely from the old one

So at this moment:
- FRAME concept and direction are active
- implementation is being restarted
- schema is being reconsidered
- `frame-python` is the first fresh build target

## Canonical starting docs

Start here:
- `docs/index.md`
- `docs/repo-structure.md`
- `docs/frame-architecture.md`
- `docs/schema.md`
- `docs/project-family.md`
- `docs/framelabplan.md`
- `learn/FRAME.md`

## Current repo layout

- `docs/` — canonical and supporting docs
- `learn/` — teaching and concept-building material
- `research/` — research notes, archived thinking, comparison work
- `tests/` — fixtures and future evaluation suites
- `scripts/` — validation/bootstrap/release helpers
- `frame-python/` — fresh Python implementation track

## Near-term plan

1. tighten the FRAME definition
2. re-evaluate the five-part structure against the new goal
3. re-evaluate schema direction instead of assuming the previous one is correct
4. design `frame-python` from the new contract
5. build tests/fixtures that compare FRAME against native agent-doc approaches
6. later expand to other language implementations if the model proves itself

## One-line split to keep in mind

- FRAME = the architecture and contract we are trying to define
- implementations like `frame-python` = experiments that must earn alignment with that contract
- future tooling like Haxaml = runtime systems that may consume FRAME, not define it
