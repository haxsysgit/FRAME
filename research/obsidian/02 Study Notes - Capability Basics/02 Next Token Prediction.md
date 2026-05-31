---
tags:
  - concept/core
  - study/basics
---

# Next Token Prediction

## Tiny Idea

The model's basic job is to predict the next token from the tokens it can see.

```text
visible context -> next token
```

Then it repeats that process.

## Simple Analogy

It is like autocomplete, but much stronger.

Autocomplete guesses the next word in your text.

An LLM learned enough patterns that the same guessing process can produce:

- explanations
- code
- plans
- summaries
- tool calls
- debugging steps

## Important Correction

Next-token prediction does not mean the model is "just random text."

Training on huge amounts of text teaches patterns that can look like reasoning, memory, style, and planning.

But it also means the visible context matters a lot.

## Haxaml Connection

If the model predicts from visible context, then Haxaml's job is to make visible context cleaner:

- stable facts
- hard rules
- relevant files
- current blockers
- proof from previous work
- expected outcome

## Practical Rule

> Better context does not guarantee a better answer, but bad context is an easy way to get a bad answer.

Related:

- [[01 Tokens]]
- [[04 Attention]]
- [[07 Context Engineering]]
