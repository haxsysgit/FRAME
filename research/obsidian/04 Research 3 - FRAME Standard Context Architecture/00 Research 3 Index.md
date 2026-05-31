---
tags:
  - research/topic-3
  - frame/standard-context-architecture
  - haxaml/runtime
status: draft-1
date: 2026-05-24
---

# Research 3 Index: FRAME As A Standard Context Architecture

## Tiny Idea

Research 3 asks:

> Can FRAME become a standard context architecture and structure for agent-ready projects, with Haxaml as the tool built on top?

Short answer from this pass:

> Yes, but only after tests and experiments prove the structure works across real project types. FRAME should be the standard context architecture. Haxaml should be the tool/runtime that installs, checks, and operates it.

That means:

- FRAME must define stable file roles, field meaning, references, gates, evidence, and update rules.
- Haxaml must implement those rules without turning its own internals into the standard.
- The idea must be tested against other systems and real projects before claiming standard maturity.

## Read In This Order

1. [[01 Full Report - FRAME Standard Context Architecture]]
2. [[02 Ecosystem Comparison Matrix]]
3. [[03 Standard Boundary - FRAME Architecture vs Haxaml Tool]]
4. [[04 Missing Center - Project Brain Gap]]
5. [[05 Security And Stale Context Risks]]
6. [[06 Evaluation Plan For Standard Context Architecture]]
7. [[07 Research 3 Public Reasoning Trace]]
8. [[08 Roadmap Recommendations For 0_8]]
9. [[09 FRAME Schema Research 0_8_0 Opening]]
10. [[10 Connected FRAME Candidate Matrix]]
11. [[11 Semantic Connection Rules]]
12. [[12 Schema Research Team Synthesis]]
13. [[13 FRAME Frontmatter 0_8_0]]
14. [[FRAME Schema Candidate Canvas.canvas]]
15. [[90 Research 3 Sources]]

## Main Claim

FRAME's possible edge is not that it invented project memory or runtime protocols.

Other tools already do parts of this:

- AGENTS.md gives repo instructions.
- Claude and Gemini use context files.
- Cline Memory Bank gives project memory files.
- Agent OS and Kiro give spec and steering workflows.
- Aider gives repo maps.
- MCP, A2A, and AG-UI define runtime protocols around tools, agents, and UI events.
- Letta and MemGPT study agent memory.

FRAME's possible edge is the architecture combination:

> typed repo-owned context structure + runtime gates + evidence + adapter generation + multi-agent continuity.

That combination still needs proof.

## What This Research Does Not Claim

- It does not claim FRAME is already a standard.
- It does not claim Haxaml is better than Agent OS, Kiro, Cline, or Spec Kit.
- It does not claim the five-file shape is final.
- It does not claim every project needs all five files in heavy form.

The honest claim:

> FRAME has a strong standard-context-architecture gap to explore. Haxaml is the tool that can prove whether the structure works in real projects.

## Schema Sub-Research

The first schema sub-research for `0.8.0` starts here:

- [[09 FRAME Schema Research 0_8_0 Opening]]
- [[10 Connected FRAME Candidate Matrix]]
- [[11 Semantic Connection Rules]]
- [[12 Schema Research Team Synthesis]]
- [[13 FRAME Frontmatter 0_8_0]]
- [[FRAME Schema Candidate Canvas.canvas]]
