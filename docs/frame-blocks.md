# FRAME Blocks and Parts

This document is the single supporting note for candidate FRAME structure during the reset.
It replaces separate lightweight summaries about "parts" and "block reports" so the active docs stay tighter.

## What this file is for

Use this file to think about:
- what top-level parts seem worth keeping
- what kinds of structured entries might belong inside them
- which old assumptions were probably over-specified

This is supporting design material, not frozen canon.

## Candidate top-level parts

The current working candidate remains:
- Facts
- Rules
- Acts
- Map
- Expect

Why this candidate still feels strong:
- it separates different kinds of project reality
- it is more structured than random markdown
- it seems portable enough to test across very different project families

Why it is still provisional:
- some parts may be overloaded
- some semantics may need tightening
- some ideas may belong as submodels rather than top-level parts
- the normalized model may expose weaknesses we cannot see from prose alone

## Candidate block / entry filter

A candidate structure element is only worth keeping if it helps at least one of these:
- cross-tool consistency
- project-family portability
- validation
- predictable agent behavior
- cleaner normalized implementation models
- lower ambiguity or drift

If it does not help one of those, it is probably noise.

## Practical design questions

When evaluating a candidate part or block, ask:
- does it capture project truth agents/tools repeatedly need?
- does it help separate truth from rules, continuity, navigation, or correctness?
- does it deserve a normalized slot, or should it stay payload-like for now?
- does it belong in the core contract, or only in a future profile/extension?

## Reset implication

Do not use this file to smuggle old structure back in as fake certainty.
The job here is to preserve useful structural thinking while keeping the contract open to re-validation.
