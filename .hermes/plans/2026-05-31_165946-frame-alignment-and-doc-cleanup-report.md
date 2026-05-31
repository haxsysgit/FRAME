# FRAME alignment and doc cleanup report

> For Hermes: synthesis-only report. No implementation edits yet beyond this report file.

## Goal

Turn the agreed discussion into:
- a minimal canonical definition of FRAME
- a stable boundary between FRAME core, FRAME SDK/interface, profiles, and Haxaml
- a practical doc classification
- a cleanup sequence that removes confusion without deleting useful thinking too early

---

## 1. Final agreed FRAME definition

FRAME is a layered architecture and portable repo standard for representing the current structured reality of AI-assisted software projects.

Its purpose is to make project context more portable, validateable, and predictable across agents and tools, so work does not depend on repeated prompting, full-repo rescans, provider-specific memory files, or fragile chat history.

FRAME is designed first to improve consistency of agent behavior across tools, then to improve context loading quality, portability, and auditability.

It is not a generic context tool, not a full runtime, and not a replacement for every planning or memory system. Its job is to provide a shared project-truth contract that tools and runtimes can consume consistently.

### Short version

FRAME is a standard way to represent AI-assisted project reality so different agents and tools can behave more consistently inside the same project.

### Even shorter version

FRAME gives AI-assisted projects one portable, structured source of truth that agents and tools can consume the same way.

---

## 2. Canonical architecture boundary

### FRAME core

FRAME core owns:
- the five-part conceptual structure
- representation rules
- schema/protocol meaning
- stable semantic roles of each part
- minimal lifecycle primitives
- the meaning of the normalized model

FRAME core does not own:
- runtime orchestration
- agent session management
- MCP lifecycle enforcement
- provider-specific adapters
- heavy context packing strategy as a product category

### FRAME profiles / conventions

Profiles own:
- use-case-specific conventions
- stricter patterns for certain repo types or workflow environments
- richer lifecycle expectations beyond the minimal core
- export styles for particular environments when needed

Profiles should not redefine core semantics.

### FRAME SDK / standard interface

The FRAME SDK/interface owns:
- official reading/parsing of FRAME files
- validation against FRAME schemas/contracts
- normalization into native language models
- standard output/API contract for tools and runtimes
- derived but standardized outputs like graph/project-map views and validation reports

Primary first output:
- one normalized FRAME model composed of five nested models

Secondary outputs:
- graph / relationship view
- validation and audit reports
- task-scoped derived views
- agent-contract views
- lifecycle hints where appropriate

Important principle:
Tools should not each invent their own FRAME reader/assembler. The SDK/interface exists to preserve shared meaning across Python, JavaScript, and other implementations.

### Haxaml

Haxaml owns:
- runtime interaction with agents
- MCP-based tool contracts
- governed workflow/lifecycle enforcement
- setup/adoption of FRAME-backed projects
- dynamic context operations
- execution-time validation/use of FRAME through the standard FRAME layer

Haxaml should consume FRAME through the official FRAME SDK/interface rather than define FRAME meaning itself.

### Best one-line split

- FRAME = contract
- FRAME SDK = official interpreter
- Haxaml = runtime actor

---

## 3. Value priorities we agreed on

### Truth priority
1. Working engineering truth
2. Project intent
3. Behavioral truth for agents
4. Execution truth

### Outcome priority
1. Predictable implementation behavior
2. Faster high-quality context loading
3. Cross-tool portability
4. Validation and auditability
5. Agent handoff continuity

### First undeniable win case
1. Most important: different agents/tools produce more consistent outputs because they consume the same FRAME standard
2. Next: agents stay closer to intended project architecture and rules
3. Next: teams can validate whether the work followed the intended structure and constraints

Implication:
FRAME should be described more as governance/predictability infrastructure than as a chat-handoff convenience layer.

---

## 4. Product wedge we agreed on

### Adoption order
1. Portable repo standard
2. Official reader / validator / normalizer / API / SDK
3. Context assembly built on top of the standard layer
4. Limited lifecycle guidance, but not a bloated full operating layer

### Why this order matters

If assembly/runtime behavior comes before shared interpretation, every tool invents its own meaning and FRAME stops being a standard.

So the correct order is:
- shared representation first
- shared interpretation second
- derived behavior third

---

## 5. Native output model we agreed on

The first important output of FRAME is not an opaque context blob.

It is a normalized FRAME-native model:
- one top-level FRAME model
- five nested models, one for each FRAME part
- typed internal structures with clear semantics
- suitable for language-native use in Python, JavaScript, and others
- Python-first likely via Pydantic

This normalized model is the base for later outputs like:
- project graph / relationship map
- validators / auditors
- context slices
- export adapters
- governance tooling

---

## 6. Lifecycle boundary we agreed on

Lifecycle semantics should be layered.

- FRAME core = minimal lifecycle primitives
- FRAME profiles = richer lifecycle conventions
- Haxaml/tools = enforcement and operationalization

This keeps the core stable while still allowing guided orientation -> planning -> execution -> validation flows at higher layers.

---

## 7. What FRAME is not

FRAME is not:
- a generic memory app competitor
- a replacement for Honcho, Mem0, or every context system
- a full runtime session manager by itself
- a provider-specific prompt format
- a giant architecture wiki
- a task tracker pretending to be a standard

The lane is narrower and stronger:
- project governance
- standardized project reality
- predictability across tools/agents
- lower context drift and repeated prompting

---

## 8. Doc classification

### Canonical

These should define the project publicly and consistently after rewrite:

1. `README.md` (create)
   - role: top-level entrypoint
   - should explain what FRAME is, why it exists, how repo is organized, and how FRAME/Haxaml relate

2. `learn/FRAME.md`
   - role: canonical product/standard definition
   - status: keep but rewrite/trim
   - issue: currently strong on motivation, but still too tied to older wording like “shared memory” and points to missing `goals.md`

3. `docs/frame-architecture.md`
   - role: canonical architecture + boundary doc
   - status: keep
   - issue: already the closest current doc to the agreed model, including normalized type model and boundary language; should become the main technical canon after cleanup and minor rewrites

4. `docs/project-family.md`
   - role: canonical cross-project/repo-family positioning
   - status: keep
   - issue: supporting canon for how FRAME generalizes across repo shapes

5. `sdk/python/README.md`
   - role: SDK-specific entrypoint
   - status: keep and fix
   - issue: currently points at `FRAME/schemas/0.8.0/`, which does not match this repo layout

### Supporting

Useful, but should not define the product on their own:

1. `docs/frameparts.md`
   - useful explanation of the real jobs of each file
   - could remain as supporting spec note or be partially merged into architecture docs

2. `docs/frame-blocks.md`
   - strong supporting spec/reference doc
   - good as a block canon reference if kept technical and subordinate to the architecture doc

3. `learn/haxaml.md`
   - useful Haxaml-side explanation
   - should become Haxaml-specific supporting canon after boundary rewrite
   - currently conflicts with the updated SDK/interface split because it still frames Haxaml as the layer that reads/assembles FRAME more directly

4. `learn/haxaml-mcp.md`
   - useful operator/runtime guide
   - should remain as Haxaml runtime documentation, not FRAME canon

5. `learn/haxaml-prebuild.md`
   - useful tool/lifecycle doc
   - should remain clearly downstream of FRAME canon

### Exploratory

These contain useful design thinking but should not be treated as product-defining canon:

1. `docs/framelabplan.md`
   - useful maturation plan and reasoning
   - exploratory/planning doc, not core public canon
   - parts of it should be absorbed into architecture/canon docs

2. `research/obsidian/**`
   - valuable research base
   - clearly exploratory/research, not canon

3. `geminifindings.md`
   - exploratory findings, not canon

### Archive

Keep for historical context, but do not let them define the live story:

1. `reports/haxaml-0.7x-closeout.md`
2. `reports/haxaml-test-strategy-audit.md`
3. `reports/haxaml-vision-realignment.md`
4. `reports/haxaml-critical-bug-audit.md`
5. `reports/haxaml-0.7.7-closure-and-0.8-opening.md`

These are useful evidence/history, but they are not the source of current truth.

### Delete / merge candidates

These should likely be merged, demoted, or retired from the top-level doc story:

1. `docs/frame-block-report.md`
   - likely merge into `docs/frame-architecture.md` or archive
   - reason: it overlaps heavily with `frameparts.md` and `frame-blocks.md`

2. `docs/frameparts.md`
   - either keep as a support note OR merge selected material into `docs/frame-architecture.md`
   - avoid duplicating “real job of each file” in too many places

3. `learn/haxaml.md`
   - not delete, but rewrite/merge boundary-sensitive sections
   - reason: current wording can mislead readers into thinking Haxaml owns FRAME interpretation rather than consuming the official interface

4. references to `goals.md`
   - must be removed or replaced everywhere unless that file is created for real

---

## 9. Concrete conflicts already visible

### Conflict 1: Missing canonical destination
- `learn/FRAME.md` and `learn/haxaml.md` point to `../goals.md`
- problem: broken canonical reference
- recommendation: replace with `README.md` or a real canonical vision doc that actually exists

### Conflict 2: Haxaml reading/assembly ownership
- `learn/haxaml.md` and `docs/framelabplan.md` still imply Haxaml is the reader/meaning layer
- problem: conflicts with the agreed architecture that FRAME should ship the official SDK/interface
- recommendation: rewrite these docs so Haxaml consumes the FRAME SDK/interface rather than defining interpretation itself

### Conflict 3: FRAME framed too much as memory, not enough as standard/governance
- `learn/FRAME.md` strongly sells the memory problem, which is useful
- problem: it undersells predictability, standardization, and cross-tool consistency as the main proof of value
- recommendation: rewrite the top section so governance/consistency is at least as central as “shared memory”

### Conflict 4: SDK path mismatch
- `sdk/python/README.md` references `FRAME/schemas/0.8.0/`
- actual repo path is `schemas/0.8.0/`
- recommendation: fix immediately

### Conflict 5: Too many docs explain the five files in overlapping ways
- `learn/FRAME.md`
- `docs/frame-architecture.md`
- `docs/frameparts.md`
- `docs/frame-blocks.md`
- `docs/frame-block-report.md`
- problem: newcomers can read five docs and still not know which one is the source of truth
- recommendation: one primary explanation, one technical architecture doc, one block reference doc; merge or demote the rest

---

## 10. Recommended cleanup sequence

### Step 1: Create the top-level canonical path
Create `README.md` with:
- what FRAME is
- what problem it solves
- what it is not
- repo structure
- relationship to Haxaml
- pointer to canonical docs

### Step 2: Rewrite `learn/FRAME.md`
Focus it on:
- final agreed definition
- why consistency across tools matters
- FRAME as standard/project-reality contract
- not overclaiming as a generic context tool
- update wording from “Haxaml is the current implementation” to language that respects the new layered boundary

### Step 3: Promote `docs/frame-architecture.md` as the main technical canon
Make it the place for:
- layers
- five-file semantics
- normalized model / SDK boundary
- lifecycle boundary
- what tools may derive versus what core owns

### Step 4: Rewrite `learn/haxaml.md`
Make Haxaml clearly downstream:
- Haxaml uses the FRAME SDK/interface
- Haxaml focuses on runtime governance and tooling
- Haxaml does not own FRAME meaning

### Step 5: Consolidate overlapping docs
Preferred end state:
- keep `docs/frame-blocks.md` as the detailed block reference
- merge useful “real jobs” material from `docs/frameparts.md` into either `frame-architecture.md` or `frame-blocks.md`
- archive or absorb `docs/frame-block-report.md`

### Step 6: Demote planning/research docs from the canonical path
- keep `docs/framelabplan.md`, `research/obsidian/**`, and `reports/**`
- but stop treating them as public canonical explainers

### Step 7: Fix broken/misleading references
- remove `goals.md` references unless that file is created
- fix schema path references in SDK docs
- ensure canonical docs point only to existing canonical docs

---

## 11. Minimal canonical doc set I recommend

If you want the repo to feel sane quickly, the minimum clean doc surface is:

1. `README.md`
2. `learn/FRAME.md`
3. `docs/frame-architecture.md`
4. `docs/project-family.md`
5. `docs/frame-blocks.md`
6. `learn/haxaml.md`
7. `sdk/python/README.md`

Everything else should be explicitly supporting, exploratory, or archived.

---

## 12. Suggested canonical wording snippets

### One-liner
FRAME is a portable standard for representing the current structured reality of AI-assisted software projects.

### Short paragraph
FRAME gives AI-assisted projects a shared, validateable, tool-neutral representation of project reality so different agents and tools can behave more consistently without relying on scattered prompt files, stale memory, or repeated repo-wide scanning.

### Boundary line
FRAME defines the contract. The FRAME SDK interprets it. Haxaml operationalizes it.

---

## 13. What to remove first

If the question is “what should we simplify first without overthinking it?” then:

1. Remove/replace all `goals.md` references
2. Fix `sdk/python/README.md` path mismatch
3. Stop `docs/frame-block-report.md` from competing with the main canon
4. Rewrite any wording that implies Haxaml is the official reader/assembler/meaning owner
5. Create a root `README.md` so the repo has an actual front door

---

## 14. Bottom line

The repo does not mainly suffer from lack of ideas.
It suffers from too many overlapping tellings of the idea.

The agreed path is now much clearer:
- FRAME is the layered project-reality contract
- FRAME SDK is the official interpretation layer
- Haxaml is the runtime/tooling layer
- consistency across agents/tools is the first big proof of value

That gives a clean base for the next phase of doc cleanup and then implementation.
