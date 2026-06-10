# Scoring synthesis: FRAME schema 0.1.0 refit round

Date: 2026-06-01
Candidate: `frame-five-part` / FRAME schema `0.1.0`
Fixtures:
- `organize`
- `autopahe`
- `pharmax`

Inputs:
- `Frame lab/evaluations/fits/frame-five-part-v0.1.0/organize/*.yaml`
- `Frame lab/evaluations/fits/frame-five-part-v0.1.0/autopahe/*.yaml`
- `Frame lab/evaluations/fits/frame-five-part-v0.1.0/pharmax/*.yaml`
- `Frame lab/evaluations/scorecards/frame-five-part-v0.1.0/*.toml`

Validation performed before scoring:
- all 15 fit files parsed as YAML
- all 15 fit files validated against the local FRAME `0.1.0` schemas
- all 15 fit files use `frame.schema_version: 0.1.0`

## Weighted results

Using the default rubric weights:

| Fixture | Weighted score | Percent | Verdict |
|---|---:|---:|---|
| `organize` | 40.75 / 56.25 | 72.4% | structurally good, ceremony pressure visible |
| `autopahe` | 45.00 / 56.25 | 80.0% | strongest general fit |
| `pharmax` | 44.75 / 56.25 | 79.6% | strongest coverage/usefulness, pressure visible |

Average: 77.3%.

## What improved after the first adjustment

### 1. `project_profile` worked

It gave every fixture an early routing signal:
- `organize`: tiny utility script, scale down
- `autopahe`: medium Python CLI/package, preserve browser/state caveats
- `pharmax`: full-stack app, expect richer workflow/persistence pressure

This is useful for Haxaml because it can decide how deeply to load the rest of the FRAME pack.

### 2. `source_truth` worked

All three fixtures had authority problems:
- `organize`: README names drift from actual entrypoint
- `autopahe`: package metadata, runtime modules, setup paths, and checked-in noise disagree in authority
- `pharmax`: docs/code/role names/database deployment assumptions are split

The new source-ranking shape gave those conflicts a real home.

### 3. `structural_quirks` worked

This field captured known hazards without turning them into open questions:
- doc/code drift
- hardcoded paths
- fixture import adaptation
- generated/checkpoint noise
- role-name or DB documentation drift

This is directly agent-useful: it tells Haxaml what might trick it.

### 4. command inventory + verification refs worked

`rules.commands` can now store executable surfaces while `expect.verify` stores what those checks prove.

That reduced repeated command strings and made verification meaning clearer.

## Repeated pressure points

### Pressure 1 -- Acts is still not baseline project representation

This repeated across every fixture.

- `organize`: Acts has almost no natural content except "we inspected things".
- `autopahe`: Acts is fit provenance / browser setup notes, not durable project structure.
- `pharmax`: Acts records inspection and fit actions, but does not help baseline repo understanding as much as Facts/Rules/Map/Expect.

Conclusion:
FRAME should not require Acts in every baseline project pack.

Acts should remain in FRAME, but as checked work history / execution provenance / handoff state.

### Pressure 2 -- workflow and policy truth can repeat across files

Most visible in `pharmax`.

Role policy and invoice lifecycle naturally appear in:
- `facts.architecture.business_workflows`
- `rules.critical_rules`
- `map.access_points`
- `expect.invariants`

This is not purely bad duplication. Each file sees the workflow from a different angle.

But without a lightweight reference pattern, a workflow-heavy repo can become verbose and stale-prone.

Conclusion:
Add a small shared policy/workflow reference shape before adding domain-specific fields.

### Pressure 3 -- open dict buckets are still tolerated, not solved

The adjusted schema still permits broad buckets such as:
- `facts.identity`
- `facts.classification`
- `facts.technology`
- `facts.architecture`
- `facts.environments`
- `facts.persistence`

This helped fitting speed, but it means the schema is still partly descriptive rather than strongly typed.

Conclusion:
Do not harden all these yet. The next safe move is to add reusable small shapes for repeated truths, not freeze every bucket.

## Adjustment recommendation

Make a minimal second adjustment:

1. Add a shared `policy_entry` / `workflow_entry`-style definition.
   - portable across role policy, lifecycle rules, workflow constraints, safety rules
   - supports `id`, `summary`, `applies_to`, `source_refs`, and optional `expect_refs`
   - does not encode Pharmax-specific roles or invoice states

2. Add `facts.policies` as an optional array using this shared shape.
   - lets durable business/project policies live once
   - rules and expect can reference them instead of restating all detail

3. Add an explicit baseline-pack policy to the shared frame header.
   - `representation_scope`: optional enum such as `baseline_project`, `execution_record`, `handoff`, `mixed`
   - this makes Acts’ role obvious without removing Acts from FRAME

## Current verdict

FRAME schema `0.1.0` should advance, but with one more conservative adjustment before the next fixture loop.

Do not add fixture-specific fields.
Do not model pharmacy roles or browser setup in core FRAME.
Do make baseline scope and reusable project policies clearer.
