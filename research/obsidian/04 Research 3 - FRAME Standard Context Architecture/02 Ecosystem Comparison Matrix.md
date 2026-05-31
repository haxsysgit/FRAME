---
tags:
  - research/topic-3
  - ecosystem
  - comparison
status: draft-1
date: 2026-05-24
---

# Ecosystem Comparison Matrix

## Tiny Idea

FRAME does not live in an empty room.

Lots of tools already solve parts of the agent-context problem.

The research question is:

> What part is still missing, and is FRAME actually pointed at that gap?

## Comparison Table

| System | Main job | Close to FRAME? | Strong lesson | Gap FRAME could fill |
| --- | --- | --- | --- | --- |
| AGENTS.md | shared markdown instructions for coding agents | yes, but thinner | simple repo instructions are becoming normal | no typed state, history, map, or evidence model |
| OpenAI Codex AGENTS.md | layered Codex instruction discovery | yes | precedence and byte limits matter | provider-specific instruction chain |
| Claude Code memory | CLAUDE.md, scoped rules, auto memory | yes | concise persistent context works better than repeated chat | provider-specific and not full FRAME contract |
| Gemini `GEMINI.md` | hierarchical context files and imports | yes | context hierarchy and imports are useful | instructions, not full project brain |
| Cline Memory Bank | structured project memory markdown files | very close | project memory should be split by role | weaker schema, evidence, and runtime gate model |
| Agent OS | standards/product/spec context layers | very close | context should load at the right phase | not exactly repo-owned Facts/Rules/Acts/Map/Expect |
| GitHub Spec Kit | spec-driven development workflow | close for Expect | specs, plans, and tasks reduce prompt chaos | feature flow, not persistent project-state protocol |
| Kiro | steering, specs, hooks | close | steering needs inclusion modes and scope | IDE-centered, not vendor-neutral FRAME schema |
| Aider repo map | concise codebase map | close for Map | maps help agents choose files | only map/routing, not whole project brain |
| MCP | tool/resource/prompt protocol | adjacent | protocols need lifecycle, schema, and clear roles | runtime integration, not repo memory |
| A2A | agent-to-agent protocol | adjacent | agents need discovery and task exchange | communication protocol, not project brain |
| AG-UI | agent-user UI event protocol | adjacent | traces, state, and human control matter | UI protocol, not repo schema |
| Letta/MemGPT | memory management | close for Acts/archive | memory needs tiers and persistence | agent memory, not repo-native project contract |
| Open Agent Spec | declarative agent/workflow definition | adjacent | portability needs clear agent definitions | defines agents, not repo project brain |

## What The Ecosystem Already Proves

| Pattern | Evidence |
| --- | --- |
| repo instructions matter | AGENTS.md, Codex AGENTS.md, CLAUDE.md, GEMINI.md |
| context should be scoped | Kiro inclusion modes, Claude rules, Gemini hierarchy |
| memory should be structured | Cline Memory Bank, Letta, MemGPT |
| maps help code agents | Aider repo map |
| specs reduce build chaos | Spec Kit, Kiro specs, Agent OS specs |
| protocols are emerging | MCP, A2A, AG-UI, Agent Spec |

## What Still Looks Missing

After this pass, I did not find a widely adopted system that combines all of this as one vendor-neutral repo-owned schema:

- project facts
- hard rules
- real work history
- file map and impact model
- expected run path
- blockers and advisory state
- verification evidence
- adapter generation for multiple agents
- runtime gates

That does not prove FRAME is unique forever.

It means:

> FRAME is aiming at a gap that looks real enough to research hard.

## Strongest Nearby Competitors

| Nearby system | Why it matters |
| --- | --- |
| Cline Memory Bank | closest simple "project brain" pattern |
| Agent OS | closest standards/product/spec layering pattern |
| Kiro | strongest steering/spec workflow with inclusion modes |
| GitHub Spec Kit | strongest broad agent-neutral spec-driven workflow |

These should become serious comparison targets in the schema lab.

If FRAME cannot explain why it is different from these, then the standard architecture story is weak.

## Practical Takeaway

Do not pitch FRAME as:

> We invented agent memory.

Pitch it as:

> We are testing a repo-owned project-brain contract that connects truth, rules, history, map, and expected work with runtime gates and evidence.

That is sharper.
