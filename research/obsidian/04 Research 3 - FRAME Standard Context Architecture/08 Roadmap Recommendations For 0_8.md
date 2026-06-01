---
tags:
  - research/topic-3
  - roadmap/0.8
  - frame/standard-context-architecture
status: draft-1
date: 2026-05-24
---

# Roadmap Recommendations For 0.8

## Tiny Idea

Research 3 supports the revised 0.8 roadmap.

Do not mature FRAME one file at a time.

Mature it in layers across all five files.

## Why Vertical Slices Are Correct

`frame.txt` already shows why:

```yaml
conditional_rules:
  - id: use_uv_when_declared
    when:
      fact: "technology.package_managers"
      includes: "uv"
```

Rules depend on Facts.

That means:

> Rules cannot be fully designed without Facts, and Facts cannot be useful unless Rules can act on them.

Same pattern:

- Acts records Expect progress.
- Map recommends verification.
- Rules decide blockers.
- Facts shape Map.
- Expect shapes context.

## Recommended 0.8 Flow

| Release | Layer | Why |
| --- | --- | --- |
| `0.8.0` | shared base fields | all files need identity, version, role, owner, source, unknowns |
| `0.8.1` | evidence/source | claims need proof before behavior depends on them |
| `0.8.2` | unknowns/blockers/advisory | missing info must have consistent meaning |
| `0.8.3` | references and conditional behavior | the five files need safe links |
| `0.8.4` | context/runtime behavior | FRAME must shape what Haxaml loads and permits |
| `0.8.5` | verification/progress/record | expected work, real work, and proof must connect |
| `0.8.6` | schema lab | test against varied project shapes |
| `0.8.7` | standard architecture draft | freeze only what survived |

## What To Add To 0.8 Standards

Each schema slice should define:

- plain-language meaning
- YAML shape
- allowed values
- source/evidence rule
- blocking behavior
- summary behavior
- cross-file references
- runtime effect
- migration path
- example in at least 3 project types

## Subagent Usage

Use subagents as cross-file reviewers.

Good:

- evidence reviewer across all files
- blocker reviewer across all files
- context/runtime reviewer across all files
- schema-lab reviewer across project types

Bad:

- one subagent designs only Facts
- one subagent designs only Rules
- one subagent designs only Acts

That creates file silos again.

## First 0.8.0 Target

Start with the smallest true base.

Every FRAME file should probably have:

```yaml
frame:
  file: facts
  schema_version: 0.1.0
  role: stable_project_truth
  status: draft
  last_reviewed: null
  updated_by: null
  update_reason: null
  source_policy: owner_or_verified_repository
```

The exact fields need research and testing.

But the shape is right:

> each file identifies itself, explains its role, declares version, and admits what is not known.

## What 0.8 Should Not Do

- Do not lock a huge schema before the schema lab.
- Do not make every field required too early.
- Do not turn missing fields into agent guesses.
- Do not make Haxaml-only details part of FRAME.
- Do not freeze Expect behavior before Acts and verification are clear.

## Bottom Line

Research 3 says the standard context architecture direction is plausible.

But the win condition for 0.8 is not "more YAML."

The win condition is:

> a connected context structure where the five files can explain and control agent behavior together.
