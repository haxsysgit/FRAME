---
tags:
  - concept/core
  - transformers
  - study/basics
---

# Transformers

## Tiny Idea

Transformers are the architecture family that made attention the main engine for modern language models.

## Why They Mattered

The Transformer showed that models could process sequences using attention-heavy layers instead of depending mainly on older step-by-step sequence designs.

The practical benefits included:

- better parallel training
- stronger long-range token links
- easier scaling
- a reusable architecture for text, code, images, audio, and agents

## Simple Analogy

Older sequence models were like reading a book mostly page by page.

Transformers made it easier to compare many parts of the page at once.

## Haxaml Connection

Haxaml does not change transformer internals.

It changes the project context sent into transformer-based agents.

That still matters because the model can only use what it can see.

Related:

- [[04 Attention]]
- [[01 Full Report - Attention To Context Engineering]]
- [[07 Context Engineering]]
