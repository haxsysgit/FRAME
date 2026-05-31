---
tags:
  - concept/core
  - study/basics
  - context-engineering
---

# Context Window

## Tiny Idea

The context window is the information the model can currently see.

It is the model's workbench.

## What Can Be In The Window

- user request
- system/developer instructions
- chat history
- files
- command output
- search results
- memory notes
- examples
- schemas
- generated summaries

## Simple Analogy

Imagine fixing a laptop.

Your workbench can hold tools, screws, notes, manuals, and the laptop itself.

A bigger bench helps, but it can still become a mess.

## Why Bigger Is Not Always Better

Long context can fail when:

- important info is buried
- old info conflicts with new info
- noisy details distract the model
- exact proof was summarized away
- context has no priority order

## Haxaml Connection

FRAME gives Haxaml different drawers:

- Facts drawer
- Rules drawer
- Acts drawer
- Map drawer
- Expect drawer

The context pack should pull only the drawers needed for the current task.

Related:

- [[04 Long Context Reality Check]]
- [[07 Context Engineering]]
- [[10 Compaction]]
