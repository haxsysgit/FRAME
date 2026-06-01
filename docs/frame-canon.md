# FRAME Canon

## One-line definition

FRAME is a portable repo standard for representing current structured project reality so AI agents and tools can work more consistently inside a software project.

## Short definition

FRAME is not a general knowledge system, a bloated runtime, or a replacement for code and docs.
It is a project-facing standard for capturing the minimum structured reality that agents and tools need in order to:
- understand what a project is
- know what must be obeyed
- find the right places to look
- track what changed or happened
- judge what counts as correct

The goal is not maximum data capture.
The goal is stable, adoptable, low-bloat project context.

## What FRAME is

FRAME is:
- a portable repo standard first
- a layered architecture for representing current project reality
- a basis for consistency, governance, validation, and predictability across agents and tools
- a way to reduce drift, guesswork, and context loss during AI-assisted work
- something that should generalize across different kinds of real software projects

## What FRAME is not

FRAME is not:
- a giant schema museum
- a notes app
- a fake knowledge graph
- a bloated runtime
- code replacement
- a Haxaml-only format
- a license to capture every possible project detail

If a field does not improve fitting, retrieval, routing, verification, or agent behavior often enough, it should not live in core FRAME.

## Core promise

FRAME should help agents and tools answer five practical questions inside a repo:
- What is true about this project?
- What must be obeyed?
- Where should I look?
- What happened or changed?
- What counts as correct?

That is the center of the standard.
Not elegance for its own sake.
Not complexity for its own sake.

## Canonical design pressure

FRAME must be able to survive repeated fitting across:
- different delivery families
- different system roles
- different repository shapes
- different operating contexts

But it should freeze only the minimum structure that remains useful across those settings.

That means:
- generalize aggressively at the principle level
- freeze cautiously at the field level
- reject redundancy, bloat, and irrelevant structure

## Relationship to implementation

FRAME is the contract.
Implementations interpret or operate on that contract.

So:
- FRAME defines the portable project standard
- SDKs implement the standard programmatically
- tools like Haxaml use the standard during real tasks

Haxaml is important to FRAME because it pressure-tests whether the standard is actually usable.
But Haxaml does not define FRAME by itself.

## Relationship to Frame Lab

Frame Lab exists to pressure-test FRAME against real projects.

Its purpose is not to collect the biggest repos.
Its purpose is to repeatedly fit and score candidate schema structures against real enough projects until the most stable, adoptable, and low-bloat structure becomes obvious.

So Frame Lab should prefer repos that are:
- real
- understandable
- structurally representative
- different enough to stress the schema
- small or medium enough for fast multi-agent iteration

## Standardization rule

Before adding or freezing any part of FRAME, ask:
- does this help capture durable project reality?
- does this improve agent/tool behavior?
- does this survive fitting across multiple real projects?
- is it worth its complexity cost?

If the answer is weak, the structure should stay provisional or be removed.

## Bottom line

FRAME should become the minimum stable project-context standard that most real software repos can adopt without turning into bureaucracy.
