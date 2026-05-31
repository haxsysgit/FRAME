---
tags:
  - research/topic-2
  - claims
  - evidence
status: draft-1
date: 2026-05-23
---

# Research 2 Claims, Evidence, And Unknowns

## How To Read This

This note separates what is supported, what is inferred, and what still needs testing.

That matters because FRAME should not grow from vibes.

## Claim Table

| Claim | Label | Confidence | Support |
| --- | --- | --- | --- |
| Prompt engineering includes many techniques beyond simple instruction writing. | Evidence | High | [[90 Research 2 Sources#The Prompt Report|The Prompt Report]] gives a broad taxonomy. |
| Clear roles, constraints, examples, and output formats are common prompt patterns. | Evidence | High | OpenAI and Anthropic prompting docs both teach structured task setup. |
| Durable prompt instructions can be moved into project-level context files. | Inference | Medium-high | If prompts are visible context, stable prompt parts can be stored and reused. |
| FRAME maps cleanly to many stable prompt/context patterns. | Inference | Medium-high | Facts, Rules, Acts, Map, and Expect match stable truth, constraints, memory, routing, and goals. |
| FRAME should not store raw chain-of-thought. | Inference | High | Useful project memory is decisions/evidence/outcomes, not hidden reasoning text. |
| Haxaml can act as a runtime context engine. | Hypothesis | Medium | The architecture fits, but needs tests comparing it against simpler approaches. |
| FRAME's exact five-file design is better than nearby systems. | Unknown | Unknown | Needs Research 3 ecosystem comparison and evals. |
| Context structure will stay valuable even as context windows grow. | Inference | High | Long-context evidence from Research 1 shows bigger windows still need good selection and structure. |

## Strongest Evidence

| Evidence | What it supports |
| --- | --- |
| Prompt taxonomy research | prompt engineering is a real technique space, not one trick |
| official prompting docs | role, instructions, examples, and output shape matter in practice |
| RAG and context-engineering sources | useful external context can improve work when selected well |
| long-context research from Research 1 | larger windows do not remove the need for structure |

## Main Unknowns

| Unknown | Why it matters | How to test |
| --- | --- | --- |
| Does FRAME outperform one strong `AGENTS.md`? | If not, the architecture may be too heavy. | Compare tasks with AGENTS-only vs FRAME+Haxaml. |
| Which FRAME fields should be required? | Too strict hurts adoption; too loose weakens the architecture. | Try minimal schemas on real repos. |
| How much Acts history should be hot? | Too much creates noise; too little loses continuity. | Measure task success and token cost with different budgets. |
| How should Expect update after work? | Expect is plan/checklist, Acts is reality. | Test lifecycle variants and see which stays clear. |
| Which prompt techniques should stay adapter-only? | Prevents schema bloat. | Keep a rejected-pattern list and review it across providers. |

## Practical Conclusion

Research 2 supports the direction, but not the full standard architecture yet.

Good claim:

> FRAME appears to be a strong structure for durable project context.

Too-strong claim:

> FRAME is already the standard context architecture for agents.

We are not there yet.
