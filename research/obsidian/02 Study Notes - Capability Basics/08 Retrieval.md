---
tags:
  - concept/core
  - retrieval
  - study/basics
---

# Retrieval

## Tiny Idea

Retrieval means finding relevant information instead of loading everything.

## Simple Analogy

Instead of carrying the whole library, you use the catalog to find the right shelf.

## Types Of Retrieval

| Type | What it uses |
| --- | --- |
| Keyword | exact words and phrases |
| Path-based | file names and folders |
| Symbol-based | functions, classes, modules |
| Graph-based | dependency and ownership links |
| Semantic | meaning similarity |
| Recency-based | recent changes or records |

## Haxaml Connection

`map.yaml` can become the project minimap.

It should help agents answer:

- What files probably matter?
- What modules are connected?
- What areas are risky?
- What tests should be considered?

## Practical Rule

> Start with simple retrieval: paths, names, ripgrep, and map rules. Add semantic search only when simple methods hit their limit.

Related:

- [[07 Context Engineering]]
- [[06 What This Means For FRAME And Haxaml]]
