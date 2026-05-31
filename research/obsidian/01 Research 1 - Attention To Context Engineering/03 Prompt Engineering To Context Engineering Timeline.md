---
tags:
  - research/topic-1
  - prompt-engineering
  - context-engineering
---

# Prompt Engineering To Context Engineering Timeline

This note gives the fast history.

## Timeline

| Year | Shift | Why it mattered |
| --- | --- | --- |
| 2017 | Transformer architecture | Attention became the main sequence-modeling engine. |
| 2020 | RAG | External documents could be fetched and placed into context. |
| 2022 | Chain-of-thought prompting | Reasoning examples improved some reasoning tasks. |
| 2022 | ReAct | Models could combine reasoning-style traces with tool actions. |
| 2023 | Lost in the Middle | Long context was shown to have real placement and use problems. |
| 2024 | The Prompt Report | Prompting became a large technique map, not one trick. |
| 2024 | RULER | Long-context claims got stronger benchmark pressure. |
| 2025 | NoLiMa and context-engineering surveys | The field pushed harder on whether models truly use long context. |
| 2026 | Agent loop docs and coding-agent workflows | Real systems focus on files, memory, compaction, tools, and verification. |

## What Changed

Prompt engineering started as:

> How do I word the instruction?

It became:

> How do I set up the model's whole workbench?

For simple tasks, the first question is enough.

For agents, the second question matters more.

## Prompt Engineering Patterns

| Pattern | Plain meaning |
| --- | --- |
| Role/persona | Tell the model what kind of helper it should act like. |
| Constraints | Tell it hard limits and rules. |
| Few-shot | Show examples. |
| Output format | Tell it the shape of the answer. |
| Reasoning examples | Show how a task can be broken down. |
| Tool-use prompts | Tell it when and how to act with tools. |

## Context Engineering Patterns

| Pattern | Plain meaning |
| --- | --- |
| Retrieval | Find relevant info instead of loading everything. |
| Memory | Keep useful state across sessions. |
| Compaction | Shorten history while keeping important facts. |
| Isolation | Keep untrusted or noisy context from overriding rules. |
| Ordering | Put the most important context where the model can use it well. |
| Verification | Tie output back to proof. |

## Why This Matters

FRAME lives closer to context engineering than prompt engineering.

It is not just "how to ask."

It is:

> how to keep the repo's brain organized so any agent can enter, act, prove, and leave useful state behind.
