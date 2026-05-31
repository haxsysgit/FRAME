---
tags:
  - research/topic-3
  - frame/schema
  - frame/matrix
status: draft-1
date: 2026-05-24
---

# Connected FRAME Candidate Matrix

## Tiny Idea

This note is the candidate field map.

It does not mean every field is final.

It means:

> These are the likely shelves and data points worth testing as FRAME becomes a standard context architecture.

FRAME stays static here. If something sounds like it "runs", "syncs", or "decides", that belongs to Haxaml or another tool built on top of FRAME.

## Facts Candidate

| Section | Candidate fields | Behavior |
| --- | --- | --- |
| `frame` | file, schema_version, role, status, last_reviewed, updated_by, update_reason | identifies the file and version |
| `identity` | name, version, summary, repository | anchors project identity |
| `purpose` | problem, outcome, scope, non_goals | bounds project intent |
| `classification` | domain, project_type, delivery_model, lifecycle_stage | activates project-type rules |
| `technology` | languages, runtimes, frameworks, platforms, package_managers, build_tools | drives commands and conditional rules |
| `architecture` | style, shape, entrypoints, major_parts, boundaries | seeds map routes and preserves separation |
| `interfaces` | name, type, purpose | marks public surfaces |
| `persistence` | state, stores | drives data safety and verification |
| `external_dependencies` | name, type, purpose, auth_method, status | exposes integration risk |
| `capabilities` | stable project capabilities | informs regression expectations |
| `actors` | name, type, relationship | product context |
| `unknowns` | item, impact, blocking, needed_from | makes missing facts explicit |

## Rules Candidate

| Section | Candidate fields | Behavior |
| --- | --- | --- |
| `frame` | shared metadata | identifies rules file |
| `rules[]` | id, kind, statement, severity, activates_when, applies_to, enforcement, links | stable rule list that tools can check against |
| `unknowns` | unresolved rule questions | avoids guessing policy |

Rule kinds:

| Kind | Meaning |
| --- | --- |
| `invariant` | always active rule |
| `conditional` | activates from verified Facts |
| `gate` | can stop prebuild, build, verify, or record |
| `escalation` | asks owner before risky change |
| `forbidden` | hard no |
| `trust_priority` | tells which context outranks what |

## Acts Candidate

| Section | Candidate fields | Behavior |
| --- | --- | --- |
| `frame` | shared metadata | identifies acts file |
| `entries[]` | id, ts, kind, status, summary | checked activity log |
| `archive` | policy, pointer | separates hot continuity from cold history |

Entry kinds:

| Kind | Meaning |
| --- | --- |
| `work` | actual change or action |
| `verify` | proof attempt and result |
| `blocker` | open or resolved blocker |
| `decision` | local decision that shaped work |
| `handoff` | shortest useful next-agent note |

## Map Candidate

| Section | Candidate fields | Behavior |
| --- | --- | --- |
| `frame` | shared metadata | identifies map file |
| `entries[]` or `project_routes[]` | id, name, kind, paths, summary, touch_when, check_when_changed | short repo map at a glance |
| `shared_resources[]` | id, name, kind, paths, used_by, summary | shared systems or assets |
| `dependencies[]` | from, to, reason | simple relationship hints |
| `impact_hints[]` | when, then_check, because | suggested checks after file or area changes |
| `risk_zones[]` | id, name, paths, level, reason | areas where agents should slow down |
| `map_only` | ignore_paths, generated_paths, vendor_paths, aliases | local routing hints |

Route kinds:

```text
app, package, module, service, screen, command, config, test, docs, generated, vendor, legacy_area, tooling
```

## Expect Candidate

| Section | Candidate fields | Behavior |
| --- | --- | --- |
| `frame` | shared metadata | identifies expect file |
| `planning` | slice_id, title, goal, final_outcome, strategy, status, priority, estimated_runs | expected direction |
| `runs[]` | id, title, status, objective, kind, target_refs, checklist, done_refs, blockers, notes | expected run checklist |
| `acceptance[]` | id, text, required, proof_type, rule_refs, fact_refs, map_refs | future-facing done checks |
| `progress` | current_run, overall_status, completed_runs, total_runs, last_updated_from_acts | compact progress view, updated by a tool only when proof exists |
| `course_corrections[]` | change note and reason | plan changes |

## 0.8.0 Freeze Candidate

The first slice should freeze less than the full candidate.

| File | Freeze in 0.8.0 |
| --- | --- |
| Facts | `frame`, `identity.name`, `identity.summary`, `classification.project_type`, `classification.lifecycle_stage`, `technology.languages`, `technology.package_managers`, `technology.frameworks`, `technology.runtimes`, `unknowns` |
| Rules | `frame`, `rules[]` with `id`, `kind`, `statement`, `severity`, optional `activates_when`, optional `applies_to`, `unknowns` |
| Acts | `frame`, `entries[]` with `id`, `ts`, `kind`, `status`, `summary`, `archive.policy`, `archive.pointer` |
| Map | `frame`, `entries[]` or `project_routes[]` with `id`, `name`, `kind`, `paths`, `summary`, optional `touch_when`, optional `check_when_changed` |
| Expect | `frame`, `planning.goal`, `planning.final_outcome`, `planning.status`, `runs[]` with `id`, `title`, `status`, `acceptance[]` with `id`, `text`, `required` |

## Later Slices

| Release | Add |
| --- | --- |
| `0.8.1` | evidence and source model |
| `0.8.2` | unknowns, blockers, advisory status |
| `0.8.3` | cross-file refs and conditional behavior |
| `0.8.4` | context loading and runtime behavior |
| `0.8.5` | verification, progress, and record connection |
| `0.8.6` | schema lab testing |
| `0.8.7` | standard architecture draft |
