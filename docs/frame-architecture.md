# FRAME Architecture

This doc describes the current target architecture for FRAME after the reset.
It is a direction doc, not a declaration that the entire contract is already final.

## Core idea

FRAME is trying to become a portable architecture for representing current structured project reality for AI-assisted work.

The goal is not to be a generic memory product.
The goal is to help multiple agents and tools behave more consistently inside the same project.

That means FRAME should support:
- portability
- predictability
- validation
- governance
- lower context drift
- lower dependence on repeated repo-wide scanning

## The main problem FRAME is solving

Today, project truth gets scattered across:
- agent-native prompt files
- IDE rules
- markdown docs
- issue trackers
- chat threads
- human memory

When different agents consume different fragments of that truth, behavior becomes inconsistent.

FRAME is trying to create a better source layer for that reality.

## What is likely stable

These ideas still look central even after the reset:
- FRAME should be tool-neutral
- FRAME should not depend on one model provider
- FRAME should support multiple project families
- FRAME should be implementation-aware without being implementation-captured
- FRAME should eventually support normalized language-native models
- FRAME should support better validation than plain loose markdown alone

## What is not settled yet

These things are still under active reconsideration:
- the exact schema shape
- exact file structure on disk
- exact block/field inventory
- which parts must be strict vs flexible
- how much lifecycle semantics belong in the core
- how much should be core contract vs implementation-specific layering

## The five-part model

The five-part idea is still important, but should currently be treated as a strong candidate structure rather than untouchable final canon.

The candidate parts are still:
- Facts
- Rules
- Acts
- Map
- Expect

Why it still matters:
- it separates different kinds of project reality cleanly
- it stays more structured than random markdown
- it is still broad enough to test across many project families

Why it is not frozen yet:
- the exact semantics may still need tightening
- some parts may need splitting, merging, or re-scoping
- the eventual normalized model may expose weak spots in the current definitions

## The implementation boundary

The intended relationship is:
- FRAME = the architecture/contract being defined
- `frame-python` = the first fresh implementation track being used to test that contract
- future tools/runtimes = consumers of FRAME, not the owners of FRAME meaning

That means implementation should inform the architecture, but should not capture it too early.

## Normalized model direction

A long-term implementation target is still valuable:
- one top-level FRAME model
- nested language-native models beneath it
- clear typed semantics for stable concepts
- derived validation/reporting views on top

But the exact normalized model should be earned through reset-era design work and testing, not inherited blindly from the old implementation.

## Practical rule

When a doc or implementation detail sounds too final, ask:

Is this actually a stable FRAME truth?
Or is it just one older design choice that needs re-validation?

That question should guide the rebuild.
