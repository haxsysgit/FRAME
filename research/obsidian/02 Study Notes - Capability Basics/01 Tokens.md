---
tags:
  - concept/core
  - study/basics
---

# Tokens

## Tiny Idea

A token is a small chunk of text the model reads or writes.

It is not always the same as a word.

## Simple Example

This sentence:

```text
Haxaml checks project context.
```

might become several tokens like:

- `H`
- `ax`
- `aml`
- ` checks`
- ` project`
- ` context`
- `.`

The exact split depends on the model's tokenizer.

## Why It Matters

The model has a token budget.

Every instruction, file, tool result, summary, and chat message spends that budget.

If we spend too much on noise, the useful context gets pushed out or becomes harder to use.

## Haxaml Connection

FRAME files can grow.

Haxaml should not load everything every time.

It should turn project memory into a focused context pack.

## Practical Rule

> If a note does not help the current task, it should probably not be in the hot context.

Related:

- [[03 Context Window]]
- [[07 Context Engineering]]
- [[10 Compaction]]
