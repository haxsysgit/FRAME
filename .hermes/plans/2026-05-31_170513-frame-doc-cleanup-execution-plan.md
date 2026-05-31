# FRAME doc cleanup execution plan

> For Hermes: this plan is for immediate doc cleanup execution in the current repo.

Goal: reduce conflicting explanations of FRAME, establish a clear canonical doc surface, and align the docs to the agreed architecture boundary:
- FRAME = contract
- FRAME SDK = official interpreter
- Haxaml = runtime actor

---

## Cleanup goals

1. Create a real top-level front door for the repo.
2. Remove broken canonical references.
3. Align FRAME/Haxaml/SDK boundary language.
4. Reduce misleading wording around FRAME as only “memory”.
5. Stop duplicate docs from competing for canonical authority.
6. Keep research/planning/history, but demote them from the main product story.

---

## Phase 1: Highest-value fixes now

### Task 1: Create root `README.md`

Objective: give the repo a canonical entrypoint.

Files:
- Create: `README.md`

Content should include:
- what FRAME is
- what it is not
- why it exists
- relationship to Haxaml
- canonical doc map
- repo layout overview
- current maturity/status note

Verification:
- root README exists
- it points to real files only
- it matches the agreed boundary

### Task 2: Rewrite the top of `learn/FRAME.md`

Objective: make the opening define FRAME as a layered project-reality standard, not just “shared memory.”

Files:
- Modify: `learn/FRAME.md`

Edits:
- remove broken `goals.md` pointer
- replace “memory and protocol model” framing with the newer “portable standard / project reality / consistency across agents and tools” framing
- keep the motivating context-chaos examples, but subordinate them to the main value proposition
- avoid wording that makes Haxaml the owner of FRAME meaning

Verification:
- opening lines reflect the agreed definition
- no `goals.md` reference remains

### Task 3: Rewrite the top of `learn/haxaml.md`

Objective: make Haxaml clearly downstream of FRAME and the FRAME SDK/interface.

Files:
- Modify: `learn/haxaml.md`

Edits:
- remove broken `goals.md` pointer
- update the boundary so Haxaml uses the official FRAME SDK/interface
- preserve MCP/runtime/lifecycle emphasis
- remove any implication that Haxaml defines official FRAME reading/assembly semantics

Verification:
- top section reflects: FRAME contract -> FRAME SDK -> Haxaml runtime
- no `goals.md` reference remains

### Task 4: Fix `sdk/python/README.md`

Objective: make the SDK README point at real paths and reflect the standard-interface role.

Files:
- Modify: `sdk/python/README.md`

Edits:
- fix `FRAME/schemas/0.8.0/` to `schemas/0.8.0/` or clarify relative repo path correctly
- describe the SDK as the official reader / validator / normalizer layer

Verification:
- no stale schema path remains
- README matches the agreed boundary

### Task 5: Demote `docs/frame-block-report.md`

Objective: stop this file from competing with architecture canon.

Files:
- Modify: `docs/frame-block-report.md`

Edits:
- add a clear note that this is a short supporting summary, not the canonical architecture/spec doc
- point readers to `docs/frame-architecture.md` and `docs/frame-blocks.md`

Verification:
- file no longer reads like a competing canon source

---

## Phase 2: Canon tightening next

### Task 6: Tighten `docs/frame-architecture.md`

Objective: make this the unquestioned technical canon.

Files:
- Modify: `docs/frame-architecture.md`

Edits:
- strengthen the opening to match the final agreed definition
- ensure the normalized model and boundary sections are easy to find
- explicitly state the layered split:
  - FRAME core
  - FRAME profiles
  - FRAME SDK/interface
  - Haxaml

### Task 7: Decide what to do with `docs/frameparts.md`

Options:
- keep as a supporting note if it adds distinct value
- or merge its “real jobs” material into architecture or blocks docs

### Task 8: Keep `docs/frame-blocks.md` as reference, not marketing canon

Objective:
- preserve it as detailed spec/reference
- avoid duplicating top-level conceptual explanation already covered elsewhere

---

## Phase 3: Demotion and cleanup later

### Task 9: Demote exploratory docs from the canonical path

Files:
- `docs/framelabplan.md`
- `research/obsidian/**`
- `geminifindings.md`
- `reports/**`

Objective:
- preserve them
- stop them from functioning as the repo’s public entrypoint story

### Task 10: Optional archival/merge decisions

Potential candidates:
- archive or fold `docs/frame-block-report.md`
- merge selected content from `docs/frameparts.md`

---

## Edit order for execution

1. `README.md` create
2. `learn/FRAME.md` top rewrite
3. `learn/haxaml.md` top rewrite
4. `sdk/python/README.md` fix
5. `docs/frame-block-report.md` demotion note
6. `docs/frame-architecture.md` strengthening pass
7. verification search for stale references and conflicting wording

---

## Validation checklist

After edits, verify:

- no `goals.md` references remain in canonical docs
- root README exists
- FRAME is described as project-reality standard, not just generic memory
- Haxaml is clearly downstream of FRAME + FRAME SDK
- SDK is clearly the official interpretation layer
- canonical docs point to real files only
- no short supporting doc reads like the main architecture source

---

## Scope guard

This cleanup phase should avoid:
- rewriting all long-form research content
- deleting exploratory docs outright
- changing schema meaning yet
- introducing new implementation claims that the repo cannot support

The job is alignment first, not grand reinvention.
