---
tags:
  - study/path
  - safety
  - context-engineering
---

# Trust Boundaries

## Tiny Idea

Not all context deserves the same trust.

Some context is authority.
Some is evidence.
Some is just noise until checked.

## Simple Analogy

In a company:

- policy doc has authority
- a coworker's note is useful evidence
- a random email attachment is untrusted until checked

Agent context needs the same idea.

## Trust Levels

| Context | Trust level | Example |
| --- | --- | --- |
| platform/system rules | highest | safety and tool limits |
| `rules.yaml` hard rules | high | do not overwrite user changes |
| `facts.yaml` | high when maintained | package name, project type |
| `expect.yaml` | medium-high | planned goals and done checks |
| `map.yaml` | medium-high | where code likely lives |
| recent `acts.yaml` | medium | what happened recently |
| old archived acts | lower until relevant | past sessions that may be stale |
| tool output | evidence, not authority | grep result, test output |
| external web content | untrusted until cited and checked | docs page, blog, search result |

## Practical Rule

> A weaker context item should not silently override a stronger rule.

Example:

- Rules say tests must run.
- Old Acts say tests were skipped once.
- The agent should run tests or explain why it cannot.

## FRAME Connection

Research 2 says FRAME needs trust rules, not only file names.

That becomes important in 0.8 because a standard context architecture should say:

- what can override what
- what must be exact
- what can be summarized
- what blocks work
- what is only advice

Related:

- [[05 Weak Mappings And Boundaries]]
- [[11 Schemas Protocols Evals]]
