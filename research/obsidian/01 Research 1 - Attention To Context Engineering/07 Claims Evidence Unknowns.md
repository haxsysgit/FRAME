---
tags:
  - research/topic-1
  - evidence
  - frame/future
---

# Claims, Evidence, And Unknowns

This note keeps the research honest.

## Claim Labels

| Label | Meaning |
| --- | --- |
| Evidence | Directly supported by a paper, official doc, repo, or test. |
| Inference | Logical read from evidence, but not directly proven. |
| Hypothesis | Plausible idea we need to test. |
| Unknown | Not enough evidence yet. |

## Claims Table

| Claim | Label | Current reason |
| --- | --- | --- |
| Transformers are foundational to current LLMs. | Evidence | The Transformer architecture became the base family for modern LLM systems. |
| Attention is not context. | Evidence | Attention is a model mechanism; context is the visible input/state. |
| Prompt wording can strongly affect output. | Evidence | Prompting research and official docs depend on task setup, examples, constraints, and format. |
| Retrieval improves some knowledge-heavy tasks. | Evidence | RAG showed external retrieved knowledge can improve generation for knowledge-intensive work. |
| Long context has practical failure modes. | Evidence | Lost in the Middle, RULER, and NoLiMa pressure long-context reliability. |
| Agent work needs more than a good prompt. | Evidence | Tool-use and agent docs focus on files, memory, compaction, tools, and verification. |
| Context engineering is becoming a core agent skill. | Inference | The same pattern appears across papers, docs, and agent systems. |
| FRAME maps naturally to context engineering. | Hypothesis | The file roles match common context needs, but we need tests. |
| Haxaml can become the main tool/runtime for FRAME. | Hypothesis | The package exists and has the right shape, but the architecture/tool boundary needs work. |
| FRAME is a new standard. | Unknown | It is not widely adopted or proven yet. |
| FRAME beats `AGENTS.md` alone. | Unknown | Needs controlled comparison. |

## The Research Line We Should Defend

Strong:

> LLM outputs depend heavily on visible context, and agent reliability depends on choosing and managing that context well.

Still unproven:

> FRAME is the best standard context architecture shape.

That is the clean line.
