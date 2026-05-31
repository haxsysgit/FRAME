---
tags:
  - study/path
  - frame/core
---

# FRAME File Roles

## Tiny Idea

FRAME is easier to understand if every file has one main job.

Do not think:

> five YAML files because five sounds cool.

Think:

> five shelves because the project brain has different kinds of memory.

## The Roles

| File | Main job | Simple question |
| --- | --- | --- |
| `facts.yaml` | stable truth | What is this project? |
| `rules.yaml` | hard behavior | What must agents obey? |
| `acts.yaml` | real history | What actually happened? |
| `map.yaml` | project routing | Where should agents look? |
| `expect.yaml` | expected path | What should happen next? |

## Example

User asks:

```text
Make setup idempotent and verify it in a temp dir.
```

Possible FRAME split:

| Need | FRAME file |
| --- | --- |
| package name/version | `facts.yaml` |
| do not overwrite user files | `rules.yaml` |
| previous setup bugs | `acts.yaml` |
| setup module paths | `map.yaml` |
| desired release checklist | `expect.yaml` |

## Why This Matters

When the roles are clear, Haxaml can build cleaner task context.

When the roles blur, everything becomes one big prompt again.

Related:

- [[03 FRAME As Structured Prompt Memory]]
- [[06 Schema Adapter Runtime Docs Split]]

