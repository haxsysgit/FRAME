# FRAME Competitive Landscape Report

**Date:** 2026-06-09
**Purpose:** Honest assessment of whether anything already does what FRAME + Haxaml is trying to do.
**Method:** Parallel subagent research across GitHub, agent docs, MCP spec, and coding tool conventions.

---

## Executive Summary

**No single tool or standard combines typed project context, cross-reference graphs, mechanical validation, cross-agent run history, and lifecycle governance.** Several tools address pieces. Two are direct competitors. The industry standard is completely unstructured Markdown. FRAME's approach is unique but adoption is the real challenge.

---

## 1. The Industry Standard: Free-Form Markdown

Every major coding agent uses unstructured Markdown for project context:

| Agent | Context File | Typed Schema? | Validation? | Governance? |
|---|---|---|---|---|
| Claude Code | CLAUDE.md | No | No | No |
| GitHub Copilot | .github/copilot-instructions.md | No | No | No |
| Cursor | .cursorrules / .cursor/rules/*.mdc | No | No | No |
| Codex CLI | AGENTS.md | No | No | No |
| Gemini CLI | GEMINI.md | No | No | No |
| OpenCode | AGENTS.md | No | No | No |
| Aider | CONVENTIONS.md | No | No | No |
| Continue.dev | .continue/rules/*.md | No | No | No |

**Key finding:** The benchmark is one flat Markdown file. Any FRAME adoption strategy must answer: "Why maintain 5 typed YAML files when one CLAUDE.md already works?"

---

## 2. Closest Competitors (by FRAME component)

### Typed Project Context

| Project | Format | Schema | Overlap with FRAME |
|---|---|---|---|
| **ktext** | CONTEXT.yaml (8 sections) | JSON Schema 2020-12 | ~60% — typed project context, CI validation, but no governance/runtime |
| **agent-memory** | Structured Markdown with @id anchors | Loose per-category | ~40% — structured project memory, MCP, review gates, but no typed schema or mechanical validation |

**ktext** (github.com/arithmetike/ktext) is the most direct threat on project context. It generates a typed CONTEXT.yaml with 8 sections (identity, constraints, decisions, conventions, risks, dependencies, working, ownership), validates against JSON Schema, and gates via `ktext validate -threshold 80` in CI. It integrates with Claude Code SessionStart hooks.

**agent-memory** (github.com/xChuCx/agent-memory) is the most relevant for project memory. It provides structured Markdown with sections, MCP tools (fetch_context, propose_update, status), human review gates, secret scanning, and FTS5 search. It proves people want structured project memory — but it's a team wiki model, not a project truth model.

### Agent Governance + Policy Engines

| Project | Mechanism | Scope | Overlap with Haxaml |
|---|---|---|---|
| **Vectimus** | Cedar policy engine, 11 policy packs, sub-10ms eval | All major coding agents | ~50% — deterministic policy enforcement, but no typed project context |
| **AgenticContract** | `.acon` binary policy, 38 MCP tools, sub-ms eval | Multi-agent | ~45% — policy engine with MCP, but no project context schema |
| **Centinela** | Hook system, gate checks, claim verification | Claude Code + OpenCode | ~55% — governance + validation + workflow, closest overall but free-form context |
| **ControlKeel** | Typed memory, policy checks, proof bundles, scanner validation | OpenCode, Codex, Claude, Copilot | ~50% — deterministic validation in ~52ms, caught 12/12 risky scenarios vs 0/12 ungoverned |

**Centinela** (github.com/samuelnp/centinela) is the strongest overall competitor. It enforces plan→code→tests→validate→docs workflow, has hook-based gate checks (file size, layer boundaries, build cross-compile), claim verification that independently re-derives ground truth, and architecture archetypes. But it uses free-form CLAUDE.md for context — no typed schema.

**ControlKeel** (github.com/aryaminus/controlkeel) has the most mature governance engine. Capture intent rules → validate agent output → gate when needed → persist evidence → improve with evals. Benchmarked at catching 12/12 risky scenarios. Supports multiple agents. Has "typed memory" concept but not a full typed schema for project truth categorization.

### Cross-Agent Configuration Portability

| Project | What it does |
|---|---|
| **ai-rulez** | Write rules ONCE in `.ai-rulez/`, generate native configs for 19+ platforms |
| **agentsync** | Migrate agent configs between Claude Code, Gemini CLI, OpenCode, Cursor |
| **bridle** | TUI/CLI config manager for 7+ coding agents |
| **ai-sync-cli** | Universal sync for 20+ agents, 12+ IDEs |

These prove the multi-agent portability problem is real and growing. But they sync config, not project truth.

### MCP (Model Context Protocol)

MCP is a JSON-RPC transport protocol, NOT a project context format. It defines Resources, Tools, Roots, and Elicitation — but has zero concept of project truth, project memory, or project representation. MCP is complementary to FRAME, not competitive. Haxaml already uses MCP as its transport layer.

---

## 3. What FRAME+Haxaml Has That No One Else Combines

| Capability | Anyone else have it? | Closest competitor |
|---|---|---|
| Typed project context schema (5 parts, YAML, JSON Schema) | No — all use free-form Markdown | ktext (CONTEXT.yaml, 8 sections but no 5-part split) |
| Cross-reference graph with 9 typed relations | No | agent-memory (@id anchors, looser) |
| Mechanical validation (deterministic, agent-invisible) | Yes — Centinela, ControlKeel, Vectimus | Centinela (gate checks, claim verification) |
| Cross-agent run history (Acts) | No | ControlKeel (persists findings, not runs) |
| Lifecycle state machine (prebuild→verify→record) | Partial — Centinela (plan→code→tests, but not lifecycle) | Centinela |
| Governance level (relaxed/normal/strict) | No | Vectimus (Cedar policies, not tiered) |
| Agent-invisible grep/tests/pytest validation | Yes — ControlKeel (scanner) | ControlKeel |

---

## 4. Honest Assessment

### FRAME is not reinventing the wheel. It's combining separate wheels into a vehicle.

The pieces exist:
- ktext has typed project context
- Centinela/ControlKeel have governance + validation
- ai-rulez has multi-tool portability
- agent-memory has structured project memory

But no one has combined them into one system where typed project context feeds a governance runtime that mechanically validates agent output across any coding agent.

### The real competitor is not another tool. It's inertia.

Every coding agent already has CLAUDE.md or AGENTS.md. It's free. It's trivial. It works for simple cases. FRAME's adoption cost (5 files, schema learning, tool setup) competes against zero-cost unstructured Markdown. The question is: at what project scale does the free Markdown approach break, and FRAME's structure becomes worth the cost?

### The biggest threat: ktext or ai-rulez adding a governance layer.

If ktext (typed CONTEXT.yaml) added mechanical validation + lifecycle governance, it would overlap ~70% with FRAME+Haxaml. If Centinela added a typed project context schema, it would overlap ~80%. The window exists because no one has connected both sides yet.

### How FRAME is genuinely unique:

1. **5-part split (Facts/Rules/Map/Expect/Acts)** — No other tool separates project truth into these categories with typed cross-references
2. **Expect → Rules.commands → Mechanical Validator pipeline** — The connection from declarative expectations to executable verification is unique
3. **Acts as cross-agent run history with checks_seen/checks_ran honesty** — No tool tracks what checks were considered vs actually executed across different agents
4. **Governance level dial (relaxed/normal/strict)** — No tool lets the developer control enforcement strictness at the project level

---

## 5. Recommendations

1. **Differentiate on mechanical validation.** This is FRAME's strongest unique feature. Centinela and ControlKeel do it but without typed context. The combination of "here's what the project expects" (Expect) + "here's how to verify it" (Rules.commands) + "the validator runs it and the agent can't fake it" is the pitch.

2. **Make onboarding trivial.** The AGENTS.md benchmark means FRAME's first experience must be fast. An agent-assisted `frame init` that scans the repo and generates initial FRAME files. Not a manual 5-file ceremony.

3. **Interoperate with existing conventions.** Read CLAUDE.md and AGENTS.md as input sources for initial FRAME generation. Don't fight the standard — ingest it.

4. **Watch ktext and Centinela closely.** They're one feature away from overlapping significantly.
