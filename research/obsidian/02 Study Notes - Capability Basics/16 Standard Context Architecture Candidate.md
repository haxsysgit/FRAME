---
tags:
  - study/path
  - context-architecture
  - standard
  - frame/future
---

# Standard Context Architecture Candidate

## Tiny Idea

A standard context architecture candidate is not a finished standard.

It is an idea with enough shape that other tools could maybe understand it later.

## Plain Definition

A standard context architecture says:

- what things exist
- what they mean
- how they connect
- what behavior follows from them
- how errors or conflicts are handled

For FRAME, that means:

- what `facts.yaml` means
- what `rules.yaml` means
- what `acts.yaml` means
- what `map.yaml` means
- what `expect.yaml` means
- how Haxaml or another runtime should act on them

## Not Enough

```text
We have five YAML files.
```

That is a file format.

## Better

```text
Rules with severity block stop work.
Facts with owner evidence outrank detected guesses.
Acts records verified reality.
Expect guides expected progress.
Map routes file inspection and verification.
```

That starts to become architecture behavior.

Better wording for FRAME:

> That starts to become a standard context structure that tools can operate.

Related:

- [[01 Full Report - FRAME Standard Context Architecture]]
- [[03 Standard Boundary - FRAME Architecture vs Haxaml Tool]]
