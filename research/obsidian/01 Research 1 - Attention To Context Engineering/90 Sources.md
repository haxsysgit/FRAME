---
tags:
  - research/topic-1
  - sources
---

# Sources

These are the main sources for Research 1.

## Core Papers

### Attention Is All You Need

- Link: https://arxiv.org/abs/1706.03762
- Used for: Transformer foundation and attention-first architecture.
- Claim support: Transformers are foundational; attention lets sequence positions weigh relationships.

### The Prompt Report

- Link: https://arxiv.org/abs/2406.06608
- Used for: Broad prompt-engineering taxonomy.
- Claim support: Prompt engineering is a large map of techniques, not one magic phrase.

### Chain-of-Thought Prompting

- Link: https://arxiv.org/abs/2201.11903
- Used for: Reasoning-example prompting.
- Claim support: Step-style examples can improve some reasoning tasks.

### ReAct

- Link: https://arxiv.org/abs/2210.03629
- Used for: Connecting reasoning-style traces with actions/tools.
- Claim support: Agent work is not only answer generation; it involves actions.

### Retrieval-Augmented Generation

- Link: https://arxiv.org/abs/2005.11401
- Used for: External knowledge retrieval.
- Claim support: Fetching relevant external knowledge can improve some generation tasks.

### Lost In The Middle

- Link: https://arxiv.org/abs/2307.03172
- Used for: Long-context reliability warning.
- Claim support: Useful information can be missed depending on where it appears in long context.

### RULER

- Link: https://arxiv.org/abs/2404.06654
- Used for: Practical long-context evaluation.
- Claim support: Claimed context length and reliable usable context are not always the same thing.

### NoLiMa

- Link: https://arxiv.org/abs/2502.05167
- Used for: Long-context reasoning and lexical-match pressure.
- Claim support: Long-context models can still struggle when the task needs more than simple matching.

### Context Engineering Survey

- Link: https://arxiv.org/abs/2507.13334
- Used for: Current framing of context engineering.
- Claim support: Context engineering includes selection, compression, memory, tools, and system design.

## Official And Practical Agent Sources

### OpenAI Prompting Guide

- Link: https://developers.openai.com/api/docs/guides/prompting
- Used for: Official guidance on prompt setup, iteration, and evals.

### OpenAI Codex Agent Loop

- Link: https://openai.com/index/unrolling-the-codex-agent-loop/
- Used for: Modern coding-agent loop, environment, and compaction direction.

### OpenAI Prompt Caching

- Link: https://developers.openai.com/api/docs/guides/prompt-caching
- Used for: Why stable repeated context can matter for cost and latency.

### LangChain Context Engineering

- Link: https://www.langchain.com/blog/context-engineering-for-agents
- Used for: Practical context-engineering framing for agents.

### Anthropic Building Effective Agents

- Link: https://www.anthropic.com/engineering/building-effective-agents
- Used for: Workflow/agent design lessons and avoiding overcomplex agent systems.

## Local Project Sources

These local files shaped the Haxaml/FRAME angle:

- `research_plan.md`
- `capability.md`
- `FRAME/reports/haxaml-0.7.7-closure-and-0.8-opening.md`
- `FRAME/reports/haxaml-vision-realignment.md`

## Notes On Evidence Quality

| Source type | How it is used |
| --- | --- |
| Papers | Strong evidence for model behavior, prompting, retrieval, and long-context limits. |
| Official docs | Strong evidence for current product and agent-system direction. |
| Local docs | Evidence of Haxaml's current intent, not proof that FRAME is correct. |
| Inference | Used only when the docs point in the same direction but do not prove a claim directly. |
