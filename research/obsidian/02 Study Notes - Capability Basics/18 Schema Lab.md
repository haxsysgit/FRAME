---
tags:
  - study/path
  - schema-lab
  - evaluation
---

# Schema Lab

## Tiny Idea

A schema lab is where FRAME gets tested against real project shapes.

Not vibes.
Not one perfect demo.
Real pressure.

## Why Haxaml Alone Is Not Enough

If FRAME only fits Haxaml, the schema will become Haxaml-shaped.

That is useful for Haxaml, but weak as a standard architecture.

The lab should test:

- CLI/library
- web app
- API service
- mobile app
- monorepo
- agent/MCP project
- messy legacy repo

## What The Lab Checks

| Check | Question |
| --- | --- |
| fit | does the schema feel natural? |
| weight | is it too much for small projects? |
| behavior | can fields change runtime decisions? |
| evidence | can claims point to sources? |
| blockers | can missing info stop work? |
| handoff | can the next agent continue fast? |

## Rule

> Keep bad-fit examples. They show where the architecture is weak.

Related:

- [[06 Evaluation Plan For Standard Context Architecture]]
- [[08 Roadmap Recommendations For 0_8]]
