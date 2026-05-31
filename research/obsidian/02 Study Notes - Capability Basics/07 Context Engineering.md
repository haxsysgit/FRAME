---
tags:
  - concept/core
  - context-engineering
  - study/basics
---

# Context Engineering

## Tiny Idea

Context engineering is designing what the model sees and how it sees it.

It is the bigger version of prompt engineering.

## What It Includes

- selecting relevant files
- ordering important info
- trimming noise
- compressing long history
- fetching old records only when needed
- keeping source links
- isolating untrusted context
- checking missing materials
- recording proof after work

## Simple Analogy

Prompt engineering is writing the note.

Context engineering is setting up the whole desk:

- the right manual
- the right tools
- the checklist
- the warnings
- the repair log
- the trash bin for old notes

## Haxaml Connection

FRAME is the stored context model.

Haxaml is the context operator:

- reads FRAME
- builds context packs
- asks for missing info
- records verified work
- keeps history small enough to use

## Practical Rule

> Agents need less "dump everything" and more "show the right truth with the right priority."

Related:

- [[03 Context Window]]
- [[08 Retrieval]]
- [[09 Memory]]
- [[10 Compaction]]
