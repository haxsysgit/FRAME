# FRAME

*A typed project-context architecture for AI-assisted software development.*

---

I started working on FRAME because I kept running into the same problem: every time I switched coding agents, the project forgot itself.

Not its code  --  the code was fine, sitting right there in the repo. But the *understanding* of the project. The rules we'd agreed on. The decisions we'd made and why. The checks that mattered. The things previous agents had touched or broken.

All of that lived in conversation history. Chat threads. Agent-specific memory files. My own head. When I switched from one agent to another, that context evaporated. The new agent had to rediscover the project from scratch. Prompts had to be rewritten. The same gotchas had to be explained again.

I wanted a way for the project itself  --  not any single agent, not any single conversation  --  to hold the shape of what it is, what it needs, and what's happened to it.

That's FRAME.

---

## The idea

FRAME is five linked files that live in your repo:

- **Facts**  --  what is true about this project (stack, architecture, quirks, open questions)
- **Rules**  --  what must be obeyed (commands, constraints, dont's, ask-first triggers)
- **Map**  --  where things live (directories, entrypoints, managed paths)
- **Expect**  --  what should pass (outcomes, invariants, verifiable checks)
- **Acts**  --  what happened (run history across agents, blockers, handoff)

They're not five separate documents. They're one linked system. A Fact references a Rule. A Rule references a Command. An Expect check executes that Command. An Act records whether it passed and what files changed. Everything connects.

---

## Why this exists

The industry standard for "project context" right now is a single Markdown file  --  CLAUDE.md, AGENTS.md, copilot-instructions.md. It works for simple cases. But once agents start generating thousands of lines across multiple sessions, a flat Markdown file breaks down.

The problems I kept seeing:

**Context rot.** CLAUDE.md said "we deploy to Render" but the project migrated to a VPS three weeks ago. Nobody updated the file. The agent reads stale context and makes decisions based on it.

**Scattered truth.** Rules about what not to touch lived in one file. Commands in another. Test expectations in a third. Agent history in chat threads that disappeared after the session ended. No single place said "here's what matters."

**Agent switching friction.** Every new agent meant rebuilding context. Rewriting prompts. Re-explaining conventions. The project didn't transfer  --  only the code did.

**No verification.** Agents could claim "tests passed" and nobody checked. The verify step was the agent grading its own exam.

FRAME addresses each of these. It gives the project a typed shape that agents and tools can read consistently. It separates different kinds of truth so they don't fight each other inside one file. And it connects expectations to executable checks  --  so verification is mechanical, not self-reported.

---

## How it works with agents

FRAME is not an agent. It doesn't run your build or write your code. It's a convention  --  a spec for how a project describes itself.

`frame-py` is a Python SDK that loads FRAME files, validates them against the schema, and returns a consistent typed representation. Future SDKs will do the same in other languages.

`Haxaml` is a governance runtime that agents interact with. It reads FRAME, enforces rules, runs mechanical validation against Expect checks, and records run history in Acts. The agent can't fake the results  --  verification is deterministic.

You control how strict the governance is. A project-level `governance_level`  --  relaxed, normal, or strict  --  determines how aggressively rules are enforced. Prototype in relaxed mode. Ship in strict mode. Same FRAME files, different enforcement.

---

## What FRAME is not

Not a replacement for reading code. Not a memory system. Not a notes app. Not an enterprise configuration framework.

It's a project biography. Small projects fill less. Large projects fill more. The same schema. Different depth.

Every field has a character limit. Core governance fields are enforced  --  you can't bloat them. Descriptive fields are advisory  --  you get a warning but the file still loads.

---

## What I've learned so far

FRAME has been tested by fitting it against real projects  --  a small CLI tool, a browser automation tool, and a full-stack pharmacy management platform. The five-part shape holds across all three without needing new core blocks.

I ran a "red room" experiment: gave an agent a poisoned task designed to break the rules, then ran the mechanical validator against the output. The validator caught the unauthorized endpoint and the environment variable exposure. It also revealed checks we were missing  --  which we added. The loop works.

The competitive landscape confirmed that no existing tool combines typed project context, mechanical validation, and cross-agent governance into one system. Several tools do pieces. Nobody connects them.

---

## What's next

The schema is locked at v0.3.0. Haxaml is the next build target.

## Repo structure

This is the umbrella repo for the FRAME standard. Language SDKs live in their own repos:

- **[frame-py](https://github.com/haxsysgit/FrameSDK)** — Python SDK (pip install framesdkpy)
- `frame-js` — future JavaScript SDK
- `frame-cpp` — future C++ SDK

This repo contains:

```
schemas/json/       JSON Schema (machine contract)
schemas/yaml/       YAML Schema (human-readable)
docs/               Design decisions, versioning, social
Frame lab/          Fixtures, evaluations, scoring
research/           Background research, competitive analysis
learn/              Tutorials and educational material
```

If you're curious about the exact field definitions, design decisions, or research that informed this, start with `canon.md`.

If you want to understand why prompts alone can't solve agent governance, `research/cv-governance/speculations.md` walks through a real CV hallucination experiment.

If you're skeptical  --  good. FRAME is still early. The best way to test it is to fit it against a real project and see where it breaks. That's what Frame Lab is for.
