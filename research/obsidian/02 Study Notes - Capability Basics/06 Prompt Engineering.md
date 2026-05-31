---
tags:
  - concept/core
  - prompt-engineering
  - study/basics
---

# Prompt Engineering

## Tiny Idea

Prompt engineering is setting up the model's task using instructions, examples, constraints, and output format.

It is not magic wording.

It is task setup.

## Common Patterns

| Pattern | Plain meaning |
| --- | --- |
| Role | "Act like a senior backend engineer." |
| Constraints | "Do not change public API." |
| Few-shot | Show examples. |
| Output format | "Return JSON with these fields." |
| Rubric | "Judge success by these criteria." |
| Tool instruction | "Search files before editing." |

## Why It Works

The prompt becomes part of the visible context.

Since the model predicts from visible context, the task setup changes the result.

## Haxaml Connection

FRAME can turn prompt engineering into durable project setup:

- role and behavior -> Rules
- stable project identity -> Facts
- task target -> Expect
- past decisions -> Acts
- file routing -> Map

## Practical Rule

> If a prompt rule must survive across agents, it probably belongs in FRAME, not only in chat.

Related:

- [[03 Prompt Engineering To Context Engineering Timeline]]
- [[07 Context Engineering]]
- [[06 What This Means For FRAME And Haxaml]]
