---
tags:
  - research/topic-1
  - context-engineering
  - frame/future
---

# Research 1 Index

Research question:

> How did we get from transformer attention to prompt engineering, context engineering, long-context systems, and modern tool-using agents?

This research is the foundation for the later FRAME work. If we get this wrong, the architecture design starts on sand.

## Short Answer

Modern LLMs are built on transformer-style attention, but **attention is not the same thing as context**.

- Attention is a model mechanism.
- Context is the information the model is given.
- Context engineering is the craft of choosing, shaping, ordering, trimming, and checking that information.

Analogy:

- Context is the room full of documents.
- Attention is the flashlight.
- Context engineering is arranging the room before the flashlight turns on.

## Reading Path

1. [[01 Full Report - Attention To Context Engineering]]
2. [[02 Attention Is Not Context]]
3. [[03 Prompt Engineering To Context Engineering Timeline]]
4. [[04 Long Context Reality Check]]
5. [[05 Where The AI Race Seems To Be Going]]
6. [[06 What This Means For FRAME And Haxaml]]
7. [[07 Claims Evidence Unknowns]]
8. [[90 Sources]]

## Output Promise

This research should help us speak cleanly about:

- what attention really is
- why transformers mattered
- why prompt engineering became useful
- why context engineering is now the stronger frame for agents
- why long context still needs structure
- why FRAME could matter without overclaiming it

## Key Terms

| Term                       | Plain meaning           |                                                              |
| -------------------------- | ----------------------- | ------------------------------------------------------------ |
| [[01 Tokens                | Tokens]]                | Small chunks of text the model reads and writes.             |
| [[02 Next Token Prediction | Next Token Prediction]] | The model keeps guessing the next chunk.                     |
| [[04 Attention             | Attention]]             | The model weighs which visible chunks matter to each other.  |
| [[05 Transformers          | Transformers]]          | The model family that made attention the main engine.        |
| [[03 Context Window        | Context Window]]        | The visible workbench the model can currently use.           |
| [[06 Prompt Engineering    | Prompt Engineering]]    | Setting up the task with instructions, examples, and format. |
| [[07 Context Engineering   | Context Engineering]]   | Building the full information environment around the model.  |

## Main Takeaway For FRAME

FRAME should not be pitched as "attention, but in files."

Better:

> [!summary]
> FRAME is a repo-owned way to organize the context that agents need before, during, and after work.

That is a cleaner and more honest direction.
