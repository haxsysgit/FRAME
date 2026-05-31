# FRAME vision and doc cleanup plan

> For Hermes: stay in plan mode only. No implementation. Use this plan to clarify FRAME’s concrete purpose, then prune or rewrite conflicting docs.

Goal: Define the concrete, visionary function of FRAME in plain language, then align the repo docs around that single truth.

Architecture:
FRAME should be treated first as a product idea and protocol boundary, not just a bundle of schema files. The immediate job is to decide what real-world problem FRAME exists to solve, what it is explicitly not, and which docs are canonical versus exploratory.

Tech Stack: markdown docs, schema docs, Python SDK, repo structure under `learn/`, `docs/`, `reports/`, `sdk/python/`, `schemas/`

---

## Current context / assumptions

- The repo currently mixes several layers:
  - FRAME as concept / protocol
  - Haxaml as implementation/runtime
  - research notes and exploratory writing
  - a Python SDK and schemas
- The idea is relevant to AI today, but the repo currently presents too many overlapping stories.
- Some docs conflict, drift, or point to missing files.
- Before deleting or rewriting docs, we need one sharp answer to: “What is FRAME actually for?”

## Vision survey findings so far

### Product truth draft from Arinze

FRAME is a structured architecture for representing AI-assisted project context and current project reality, especially for serious startups, enterprise workflows, and large codebases.

Its main job is to let teams and individuals move across agents and tools without constantly re-explaining the project, re-scanning the whole repo, or accepting context rot, stale memory, hallucinations, or token waste.

FRAME should make project context:
- portable across agents
- deterministic enough to guide behavior
- structured enough to validate
- interconnected enough to function like a project map
- implementation-aware so it can support real runtime tooling later
- representable in concrete formats such as YAML, JSON, or Markdown

Important nuance:
Project truth is not static. In AI-assisted work, the project changes continuously through orientation, planning, execution, validation, and iteration. So FRAME should not be framed as merely storing "truth" in the abstract; it should represent the best current structured reality of a project in a way that can evolve safely over time.

The long-term shape is layered:
- FRAME core = representation + protocol + architecture
- FRAME profiles/conventions = use-case-specific structure over the core
- FRAME SDK / standard interface = the official reader/output contract/API over FRAME files, schemas, and representations
- Haxaml = the actor / runtime / dynamic execution layer that interacts with agent runtimes (including via MCP) and can set up FRAME-backed projects

Important boundary correction from Arinze:
Haxaml should not be the thing that defines how FRAME is read or assembled. FRAME itself should ship with a standard output contract/interface and an official library/SDK for reading FRAME schemas/files/APIs.

Why this matters:
1. If each tool implements its own reader/assembler, the ecosystem fragments and FRAME loses standard meaning across Python, JavaScript, and other stacks.
2. A standard FRAME SDK/interface removes the burden from tools so they can focus on runtime interaction, orchestration, MCP/tool use, and dynamic operations that static FRAME alone cannot do.

So the intended split is:
- FRAME defines the contract, representations, and official read/interface layer
- FRAME SDK implements standard reading/parsing/normalization/output behavior
- Haxaml consumes FRAME through that standard layer and focuses on dynamic execution/runtime concerns

This means FRAME includes elements of:
- A: file/schema representation
- D: project-truth exchange protocol
- E: layered system design

But E is the main official framing, with D and A as supporting characteristics.

### Priority ranking from Arinze

Primary truth order:
- B: Working engineering truth
- A: Project intent
- D: Behavioral truth for agents
- C: Execution truth

Primary outcome order:
- C: Predictable implementation behavior
- B: Faster high-quality context loading
- E: Cross-tool project portability
- D: Validation and auditability
- A: Agent handoff continuity

Important nuance from Arinze:
- C and E matter most.
- A matters least of the five because smooth handoff still depends partly on the intelligence/capability of the model or agent consuming FRAME.

Implication:
FRAME should first be optimized around architecture, decisions, relationships, system understanding, and durable engineering reality — before task/status tracking.

More specifically, FRAME should primarily aim to:
- make agent behavior more predictable against project structure
- reduce the need to scan whole codebases for context
- create a portable project-truth format usable across tools and assistants
- support validation/auditing of whether work followed the intended project map

This means FRAME should not be defined primarily as a chat-handoff tool. Portability and predictability are more central than mere continuity.

---

## Proposed approach

1. Define FRAME from the outside-in.
   - Start with user problem, not schema design.
   - Decide what job FRAME does in the AI ecosystem.
2. Draw hard boundaries.
   - What FRAME is.
   - What Haxaml is.
   - What research notes are.
3. Establish canonical docs.
   - One source for vision.
   - One source for architecture.
   - One source for project-family positioning.
4. Only then remove, archive, merge, or rewrite conflicting docs.

---

## Step-by-step plan

### Phase 1: Vision definition survey

Objective: get a crisp product-definition answer before touching docs.

Questions to resolve:
- What painful thing does FRAME make easier for AI builders?
- Who is the first real user?
- What is the smallest useful outcome FRAME must produce?
- Is FRAME mainly:
  - a memory protocol,
  - a context assembly standard,
  - a project-brain format,
  - a runtime contract between tools and agents,
  - or a broader operating model?
- What must never be in FRAME’s scope?
- What would make someone switch from ad-hoc markdown/context files to FRAME?
- What proof would show FRAME works in practice?

Deliverable:
- A 1-page product truth statement for FRAME.

### Phase 2: Canonical positioning

Objective: establish the official hierarchy of ideas.

Decisions to make:
- FRAME = ?
- Haxaml = ?
- FRAME Lab = ?
- research/obsidian notes = ?
- reports/ = ?

Deliverable:
- A short canonical definitions section that can be reused across docs.

### Phase 3: Doc inventory and conflict map

Objective: classify docs by role and decide what stays.

Likely docs to inspect and classify:
- `learn/FRAME.md`
- `learn/haxaml.md`
- `docs/project-family.md`
- `docs/frame-architecture.md`
- `docs/frame-block-report.md`
- `docs/frame-blocks.md`
- `docs/frameparts.md`
- `docs/framelabplan.md`
- `sdk/python/README.md`
- `reports/*.md`

Classification buckets:
- Canonical
- Supporting
- Experimental
- Archive
- Delete / merge

Deliverable:
- A doc conflict table with recommended action per file.

### Phase 4: Canon rewrite plan

Objective: define the minimal doc set that should represent FRAME clearly.

Target shape:
- Root `README.md` — what FRAME is, why it exists, how repo is organized
- `learn/FRAME.md` or equivalent canonical vision doc — the product truth
- `docs/frame-architecture.md` — architecture only
- `docs/project-family.md` — relationship between FRAME, Haxaml, and adjacent projects
- `sdk/python/README.md` — SDK usage only

Deliverable:
- A “keep / merge / rewrite / archive” plan.

### Phase 5: Cleanup execution plan

Objective: prepare safe doc cleanup after alignment.

Actions that will likely happen later:
- remove or archive conflicting exploratory docs
- fix broken links and missing references
- separate research-note language from canonical product language
- add a root `README.md`
- standardize wording around protocol vs implementation vs lab/research

Deliverable:
- An ordered edit sequence so cleanup does not create more confusion.

---

## Files likely to change later

- `README.md` (likely create)
- `learn/FRAME.md`
- `learn/haxaml.md`
- `docs/project-family.md`
- `docs/frame-architecture.md`
- `docs/framelabplan.md`
- `sdk/python/README.md`
- possibly selected files under `reports/` or `docs/` for archival or deletion

---

## Tests / validation

Because this phase is strategic/doc-focused, validation is clarity-based:

- A newcomer should be able to answer in under 60 seconds:
  - What is FRAME?
  - What does it do?
  - Who is it for?
  - How is it different from Haxaml?
- No canonical doc should contradict another on scope or positioning.
- Broken file references should be eliminated from canonical docs.
- SDK docs should point to paths that actually exist.

---

## Risks / tradeoffs

- If vision is kept too abstract, doc cleanup will just become cosmetic.
- If FRAME tries to be too many things, every doc will drift again.
- If Haxaml and FRAME boundaries stay fuzzy, future users will not know what to adopt.
- Deleting docs too early may erase useful thinking; archiving may be safer than hard removal at first.

---

## Vision survey findings so far (continued)

### Consumer model from Arinze

FRAME should not be designed primarily for human developers first.

Refined consumer model:
- primary official consumer = FRAME SDK / standard interface
- practical downstream consumers = agents directly or tools that mediate agent/runtime interaction
- secondary human consumers = experienced developers, teams, and companies who inspect or maintain FRAME-backed projects

Important nuance:
- Not A: FRAME is not mainly a human-first documentation system.
- Not pure B: agents alone should not be relied on for deterministic validation or consistent assembly behavior.
- So the center is C, with some D:
  - C: FRAME SDK first, then tools/agents through that
  - D: humans and agents both matter, but not with equal responsibility

Implication:
FRAME should be authored in human-manageable formats, but its official meaning should be mediated through a standard SDK/interface so behavior stays consistent across languages, tools, and runtimes.

### First wedge from Arinze

Adoption should start with a tangible repo standard first, then the standard interface layer, then selective context assembly.

Wedge order:
- A first: FRAME as a portable repo standard
- B second: FRAME reader / validator / normalizer / API / SDK
- C third: context assembly capabilities built on top of the standard layer
- a limited bit of D: lifecycle-aware guidance and light orchestration, but not a full operating system layer

Why A comes first:
- portability needs something tangible that can be copied between repos/projects
- FRAME should exist as concrete project structure, not only as a service or runtime

Why B comes next:
- once the standard exists, it needs one official way to be read, validated, normalized, and exposed to tools consistently

Why C comes after:
- context assembly becomes much more reliable once it is built on top of a standardized representation and interface layer

Why only a bit of D:
- FRAME should help guide lifecycle order and pipeline fit over time
- but it should not try to become a bloated full runtime/orchestration product by itself
- tools can use FRAME and the FRAME SDK to point agents at the right pipeline or stage

Implication:
FRAME should be envisioned as a portable standard with an official interpretation layer first, and only then as the basis for more advanced assembly/orchestration behavior.

### SDK output model from Arinze

The most important official output is not a vague "context pack" first.
It is a FRAME-native data model.

Primary output shape:
- the five FRAME files represented as native language data types / structured models
- for Python, this likely means a Pydantic-based FRAME model
- the top-level output is one FRAME model composed of five nested models
- each nested model represents one of the five FRAME parts and their internal block structure
- inner fields should expose precise data types and semantics, such as immutable values, sets, lists, relationships, constraints, and other interaction-safe structures

This makes FRAME usable as a programming contract across languages such as Python, JavaScript, C, and others.

Priority output order:
- A first: normalized native FRAME model
- D next: relationship graph / project map derived from that normalized model
- C next: validation and audit outputs about missing, stale, conflicting, or violated structure
- B and F later/secondary: task-scoped context views and agent-contract views built on top of the normalized contract
- E may exist as lifecycle-stage signals, but should not dominate FRAME core

Important strategic boundary:
- FRAME and Haxaml do not aim to become another full-blown generic context tool in an overcrowded market
- many tools already compete there
- the differentiator is governance, predictability, deterministic-ish guidance, portability, and standardization for AI-assisted project work
- the purpose is to reduce agent drift, context rot, hallucinations, and repetitive prompting while preserving optionality across agents/tools

Research-aligned direction:
- FRAME should complement transformer/attention-based systems by structuring project reality in a form better suited for retrieval, orientation, and bounded agent behavior
- future ideas like FRAME-RAG or other retrieval/assembly techniques can build on this contract, but should not replace the importance of the standard itself

### First undeniable win case from Arinze

The first undeniable proof that FRAME beats plain markdown folders is not just convenience or faster onboarding.

Primary win order:
- C most important: two different tools/agents produce more consistent output because they consume the same FRAME standard
- A next: an agent implements a feature and stays inside the intended project architecture/rules more reliably
- D next: a team can validate whether the agent followed the intended project structure and constraints

Implication:
FRAME’s first clear value should be standard-induced consistency and governance across tools/agents, not merely documentation portability.

### Lifecycle boundary from Arinze

Lifecycle guidance should follow a layered split.

Chosen model:
- FRAME core = minimal lifecycle primitives only
- FRAME profiles/conventions = richer lifecycle expectations for particular environments or use cases
- tools/runtimes like Haxaml = enforce, operationalize, and adapt lifecycle behavior in practice

Implication:
FRAME core should stay stable and general, while higher layers carry more opinionated process semantics.
This prevents the core from becoming bloated while still allowing ordered orientation/planning/execution/validation workflows to emerge on top.

## Remaining synthesis tasks

1. Write the minimal final definition for FRAME 0.8-era canon
2. Define the official boundary between FRAME core, FRAME SDK/interface, profiles, and Haxaml
3. Classify current docs into canonical / supporting / exploratory / archive / delete-merge
4. Recommend the first cleanup edits and removals
5. Produce a final alignment report for agreed FRAME vision

---

## Immediate next step

Run a short founder-style survey with Arinze to extract the concrete visionary function of FRAME. Use the answers to write a single product-truth statement before touching any docs.
