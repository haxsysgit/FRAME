---
tags:
  - research/topic-3
  - sources
status: draft-1
date: 2026-05-24
---

# Research 3 Sources

These are the main sources used for Research 3.

## Repo Instruction And Provider Memory Sources

### AGENTS.md

- Link: https://agents.md/
- Used for: open markdown instruction format for coding agents.
- Claim support: repo-level agent instructions are becoming a shared convention, but AGENTS.md has no required fields and stays plain Markdown.

### OpenAI Codex AGENTS.md Guide

- Link: https://developers.openai.com/codex/guides/agents-md
- Used for: Codex instruction discovery and precedence.
- Claim support: Codex reads layered AGENTS.md files and applies closest-directory guidance later in the prompt chain.

### Claude Code Memory

- Link: https://code.claude.com/docs/en/memory
- Used for: CLAUDE.md, auto memory, scoped project instructions, and imports.
- Claim support: Claude treats memory files as context, not enforced config; concise project instructions matter.

### Gemini CLI GEMINI.md Context Files

- Link: https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html
- Used for: hierarchical context files and imports.
- Claim support: Gemini CLI loads global, project, and subdirectory context files and supports imports.

## Project Memory And Spec Workflow Sources

### Cline Memory Bank

- Link: https://docs.cline.bot/best-practices/memory-bank
- Used for: structured markdown project memory.
- Claim support: role-separated memory files are a known project-continuity pattern.

### Agent OS 3-Layer Context

- Link: https://buildermethods.com/agent-os/v2/3-layer-context
- Used for: standards/product/spec context layers.
- Claim support: agent context can be split by phase and purpose.

### GitHub Spec Kit

- Link: https://github.github.com/spec-kit/index.html
- Used for: spec-driven development flow.
- Claim support: spec -> plan -> tasks -> implement gives agents structured context instead of ad-hoc prompts.

### Kiro Steering

- Link: https://kiro.dev/docs/steering/
- Used for: steering files, scopes, inclusion modes, file references.
- Claim support: persistent project guidance benefits from scope and loading rules.

### Kiro Specs

- Link: https://kiro.dev/docs/specs/
- Used for: requirements, design, tasks workflow.
- Claim support: specs can formalize feature and bugfix work into structured artifacts.

## Runtime Protocol And Agent System Sources

### Model Context Protocol

- Link: https://modelcontextprotocol.io/specification/2025-06-18/basic/index
- Used for: protocol shape, lifecycle, schema, resources, prompts, tools.
- Claim support: mature protocols separate components, lifecycle, messages, and schema source of truth.

### Agent2Agent Protocol

- Link: https://a2a-protocol.org/latest/specification/
- Used for: agent-to-agent communication boundary.
- Claim support: A2A is about agent discovery, capability exchange, tasks, messages, and artifacts, not repo-owned project memory.

### AG-UI

- Link: https://docs.ag-ui.com/introduction
- Used for: agent-user interaction protocol.
- Claim support: agent systems need evented UI/state/human-interaction protocols, separate from repo memory.

### Open Agent Specification

- Link: https://oracle.github.io/agent-spec/development/
- Used for: declarative agent/workflow portability.
- Claim support: agent/workflow definitions are another protocol layer, separate from project-brain state.

## Repo Map And Memory Sources

### Aider Repository Map

- Link: https://aider.chat/docs/repomap.html
- Used for: codebase map as compressed routing context.
- Claim support: a map can help an agent decide what files to inspect and how code relates.

### Letta Stateful Agents

- Link: https://docs.letta.com/guides/core-concepts/stateful-agents
- Used for: persistent memory, messages, runs, steps.
- Claim support: agent state and memory need storage beyond the current context window.

### MemGPT

- Link: https://arxiv.org/abs/2310.08560
- Used for: virtual context management and memory tiers.
- Claim support: long-running agent work benefits from managed memory instead of stuffing everything into context.

### MemGym

- Link: https://arxiv.org/abs/2605.20833
- Used for: agentic memory evaluation.
- Claim support: memory for coding/web/deep-research agents needs evaluation beyond chat retention.

## Local Project Sources

- `research_plan.md`
- `0.8.x_Roadmap.md`
- `frame.txt`
- [[01 Full Report - Attention To Context Engineering]]
- [[01 Full Report - Prompt Engineering Mapped To FRAME]]

## Evidence Quality Notes

| Source type | How it is used |
| --- | --- |
| official docs | strong evidence of current tool behavior |
| papers | evidence for memory/context concepts and evaluation needs |
| local docs | evidence of Haxaml intent, not proof of correctness |
| inference | used only where multiple sources point to the same gap |

