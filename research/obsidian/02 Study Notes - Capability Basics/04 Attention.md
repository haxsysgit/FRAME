---
tags:
  - concept/core
  - attention
  - study/basics
---

# Attention

## Tiny Idea

Attention is how the model weighs relationships between visible tokens.

It helps the model decide which parts of the context matter to each other.

## Simple Analogy

Attention is like a spotlight moving across the workbench.

The workbench is the context.

The spotlight is attention.

The person using the spotlight is the model.

## Not The Same As Context

| Thing | Meaning |
| --- | --- |
| Context | The visible input. |
| Attention | The model mechanism that weighs links inside that input. |

This distinction is important.

FRAME does not replace attention.

FRAME organizes what attention receives.

## Haxaml Connection

If Haxaml gives the model cleaner project context, the model has a better chance of attending to the right facts, rules, files, and blockers.

## Practical Rule

> Do not say "attention is context." Say "attention works over context."

Related:

- [[02 Attention Is Not Context]]
- [[05 Transformers]]
- [[07 Context Engineering]]
