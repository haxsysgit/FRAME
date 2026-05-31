---
tags:
  - research/topic-2
  - sources
status: draft-1
date: 2026-05-23
---

# Research 2 Sources

These are the main sources used for Research 2.

## Core Prompting Sources

### The Prompt Report

- Link: https://arxiv.org/abs/2406.06608
- Used for: broad taxonomy of prompt engineering techniques.
- Claim support: prompt engineering is a wide technique space, not a single magic phrase.

### Language Models Are Few-Shot Learners

- Link: https://arxiv.org/abs/2005.14165
- Used for: few-shot prompting background.
- Claim support: examples inside context can steer model behavior.

### Chain-of-Thought Prompting

- Link: https://arxiv.org/abs/2201.11903
- Used for: reasoning-style examples.
- Claim support: step-style examples can improve some reasoning tasks.

### Self-Consistency Improves Chain Of Thought Reasoning

- Link: https://arxiv.org/abs/2203.11171
- Used for: runtime sampling and comparison pattern.
- Claim support: some reasoning tasks benefit from comparing multiple reasoning paths.

### ReAct

- Link: https://arxiv.org/abs/2210.03629
- Used for: action-and-observation agent loops.
- Claim support: agent work combines reasoning-style traces, tool use, and observations.

## Context And Retrieval Sources

### Retrieval-Augmented Generation

- Link: https://arxiv.org/abs/2005.11401
- Used for: fetching external knowledge instead of relying only on model weights.
- Claim support: retrieval can improve knowledge-grounded generation.

### Context Engineering Survey

- Link: https://arxiv.org/abs/2507.13334
- Used for: current context-engineering framing.
- Claim support: context work includes selection, memory, compression, tools, and system design.

### LangChain Context Engineering

- Link: https://www.langchain.com/blog/context-engineering-for-agents
- Used for: practical framing of context engineering for agents.
- Claim support: agent quality depends on what context is selected and carried through the loop.

## Official Prompting And Agent Sources

### OpenAI Prompt Engineering Guide

- Link: https://developers.openai.com/api/docs/guides/prompt-engineering
- Used for: official prompt setup patterns and advice.
- Claim support: clear instructions, context, examples, and output expectations matter.

### OpenAI Structured Outputs

- Link: https://developers.openai.com/api/docs/guides/structured-outputs
- Used for: structured response shape and schema-driven outputs.
- Claim support: output shape can be constrained and checked by schema-like structures.

### OpenAI Prompt Injection Safety

- Link: https://openai.com/safety/prompt-injections/
- Used for: trust boundary around untrusted instructions and tool output.
- Claim support: not all visible context should have equal authority.

### Anthropic Prompt Engineering Overview

- Link: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview
- Used for: official provider guidance on prompt structure.
- Claim support: prompts benefit from clear task setup, examples, and careful iteration.

### Anthropic Building Effective Agents

- Link: https://www.anthropic.com/engineering/building-effective-agents
- Used for: agent design lessons and workflow caution.
- Claim support: agent systems should be designed with simple, composable patterns and clear tool boundaries.

### Model Context Protocol

- Link: https://modelcontextprotocol.io/specification/2025-06-18/basic/index
- Used for: comparison point for runtime context/tool/resource protocol thinking.
- Claim support: protocols need clear contracts, not only docs prose.

## Local Project Sources

- `research_plan.md`
- `capability.md`
- [[00 Start Here]]
- [[01 Full Report - Attention To Context Engineering]]
- [[00 Study Notes Index]]

## Evidence Quality Notes

| Source type | How it is used |
| --- | --- |
| papers | evidence for known prompting/context techniques |
| official docs | evidence for current provider practice |
| local docs | evidence of Haxaml's design intent |
| inference | used where the sources support the direction but not FRAME directly |
