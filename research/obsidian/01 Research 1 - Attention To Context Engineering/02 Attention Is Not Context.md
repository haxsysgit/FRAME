---
tags:
  - research/topic-1
  - concept/core
  - attention
---

# Attention Is Not Context

This is the correction we need to keep clean.

## Tiny Idea

Attention is inside the model.

Context is outside the model, in the input it can currently see.

They connect, but they are not the same thing.

## Simple Analogy

Think of a student studying for an exam.

| Part | Analogy |
| --- | --- |
| Context | The books and notes on the desk. |
| Attention | The student's focus moving between pages. |
| Context engineering | Choosing the right books, marking key pages, removing junk notes. |

If the right book is missing, focus cannot fix that.

If the desk has 400 random books, focus can still get lost.

## Technical Version

Attention lets the model weigh relationships between visible tokens.

Context is the visible token set:

- prompt
- instructions
- examples
- files
- chat history
- tool results
- memory
- summaries

The model uses attention over that visible input. So context quality matters because attention only works on what the model receives.

## Why The Distinction Matters For FRAME

Bad pitch:

> FRAME is attention for projects.

Better pitch:

> FRAME organizes project context so the model receives cleaner, more reliable input.

## Practical Rule

When writing FRAME docs, use this wording:

- Say "context architecture."
- Say "structured project context."
- Say "information environment."
- Do not say "FRAME is attention."

## Check Yourself

If a sentence says:

> Better attention means better project memory.

Rewrite it as:

> Better project memory gives the model better context to attend to.
