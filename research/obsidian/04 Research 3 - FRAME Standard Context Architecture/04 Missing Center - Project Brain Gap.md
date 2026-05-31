---
tags:
  - research/topic-3
  - project-brain
  - frame/gap
status: draft-1
date: 2026-05-24
---

# Missing Center: The Project Brain Gap

## Tiny Idea

The agent world has many doors into a repo.

It does not yet have one common brain for the repo.

## The Normal Tool Stack Today

Modern agent-coded repos may have:

| File/system | What it usually stores |
| --- | --- |
| README | human overview |
| AGENTS.md | agent instructions |
| CLAUDE.md | Claude instructions |
| GEMINI.md | Gemini instructions |
| `.github/copilot-instructions.md` | Copilot instructions |
| specs/tasks files | planned feature work |
| memory files | previous decisions or active context |
| tests | behavior proof |
| package config | technical truth |

That is useful, but it is scattered.

The agent still has to guess:

- Which file is source truth?
- Which instruction is current?
- Which old decision still applies?
- Which missing info blocks work?
- Which files are likely impacted?
- Which expected run is this task part of?
- What proof is needed before "done"?

## What A Project Brain Needs

A real project brain needs at least five mental shelves.

| Shelf | Plain job | FRAME candidate |
| --- | --- | --- |
| truth | stable project facts | `facts.yaml` |
| rules | what must be obeyed | `rules.yaml` |
| history | what actually happened | `acts.yaml` |
| map | where things live and affect each other | `map.yaml` |
| expectation | what should happen next | `expect.yaml` |

This is why the five-file shape still makes sense after Research 3.

But the files must connect.

## Why One Markdown File Is Not Enough

One markdown file is simple and good for adoption.

But it struggles with:

- machine validation
- cross-file references
- source tracking
- blocker status
- context policies
- exact vs summary-safe data
- verification records
- migration/versioning

Markdown is excellent as an adapter surface.

FRAME should use markdown outputs where agents expect markdown, but the canonical project brain should be typed enough for tools to check.

## What FRAME Must Prove

FRAME must prove it is not over-engineering.

Good reasons to exist:

- less repeated context setup
- better next-agent handoff
- fewer missed blockers
- clearer file routing
- better verification discipline
- less provider drift

Bad reasons:

- more YAML looks official
- every project needs a heavy context architecture
- agents will obey because the file exists
- complex schemas automatically mean quality

## Practical Definition

For now, use this definition:

> A project brain is repo-owned context that lets a new agent know what is true, what is required, what happened, where to look, what is expected, and what proof is needed.

FRAME is one candidate shape for that brain.

Haxaml is the tool trying to operate it.
