---
tags:
  - concept/core
  - compaction
  - study/basics
---

# Compaction

## Tiny Idea

Compaction means turning long history into shorter useful state.

It is not just deleting text.

It is controlled summarizing.

## Simple Analogy

After a long debugging session, you do not hand the next engineer a 900-line terminal scroll.

You hand them:

- what broke
- what changed
- what passed
- what is still risky
- where to look next

That is compaction.

## What Must Stay Exact

Some things should not be loosely summarized:

- exact error messages
- command names
- file paths
- test names
- version numbers
- security constraints
- user decisions

## What Can Usually Be Shortened

- long command output
- repeated failed attempts
- old completed runs
- background explanation
- outdated chat details

## Haxaml Connection

Acts compaction should preserve active continuity without turning hot state into a replay dump.

## Practical Rule

> Summarize the story, but preserve the receipts.

Related:

- [[09 Memory]]
- [[03 Context Window]]
- [[04 Long Context Reality Check]]
