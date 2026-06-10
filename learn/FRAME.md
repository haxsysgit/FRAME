# Learn FRAME

This file explains FRAME in simple terms while the project is being rebuilt.

## The simple version

FRAME is an attempt to give AI-assisted projects a better way to represent current project reality.

Not just random docs.
Not just one agent’s prompt file.
Not just chat history.

The big idea is:
if multiple tools and agents are going to work in the same project, they need a more stable source of truth than scattered instructions and stale memory fragments.

## The problem

Today, project context gets split across too many places:
- READMEs
- AGENTS.md
- CLAUDE.md
- IDE rules
- issue threads
- planning notes
- old chat sessions
- human memory

Then a new agent or tool arrives and only sees part of the story.
That is how you get drift, inconsistency, repeated prompting, and wasted tokens.

## What FRAME is trying to do

FRAME is trying to make project reality:
- more portable
- more structured
- more validateable
- more useful across different agents and tools

The target is not “make the project sound smart.”
The target is “make agent behavior inside the project more consistent and less messy.”

## The current reset

The project is being rebuilt on purpose.
That matters.

Why:
- the older implementation started shaping the concept too much
- the schema may have become too tied to earlier assumptions
- the architecture needed a cleaner definition before more code was added

So the current job is not to pretend everything is settled.
It is to figure out what should actually survive into the long-term contract.

## The five-part idea

The five-part FRAME idea still matters a lot:
- Facts
- Rules
- Acts
- Map
- Expect

But right now, treat that as a strong candidate structure rather than sacred final law.

It is valuable because it tries to separate:
- what is true
- what must be followed
- what has happened
- how the project is structured
- what counts as correct

That is a really useful split.
But the exact details still need pressure-testing.

## What success would look like

A mature FRAME should help different agents and tools:
- produce more consistent work
- understand projects with less repeated prompting
- avoid context rot more often
- stay closer to the intended architecture and constraints
- support better validation and governance

## What should happen next

The next phase is:
1. sharpen the architecture
2. revisit schema direction
3. build `frame-py` from the new contract
4. test FRAME against real project families
5. compare it honestly against native agent-doc approaches

That is how FRAME earns legitimacy.
