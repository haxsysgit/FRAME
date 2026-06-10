# FRAME Finalized Decisions

**Status:** Living document  --  updated as we agree on things
**Started:** 2026-06-09
**Purpose:** Single source of truth for what FRAME, frame-py, and Haxaml are and what fields exist

---

## 1. What the three pieces are

### FRAME
The convention. Language-agnostic typed project-context architecture.
Defines what Facts, Rules, Map, Expect, Acts mean, what fields exist, and what shape each field takes.
FRAME is a schema/standard, not code.

### frame-py (frame SDK)
The uniform interface library for Python.
Loads FRAME YAML/JSON files, validates against schema, converts to typed Python models, builds cross-reference graphs, and returns a consistent output shape.
No governance. No agent interaction. Pure library.
Equivalent SDKs in other languages: frame-js, frame-rs, etc.

### Haxaml
The governance runtime. Tools that interact with agents through MCP, skills, CLI.
Uses frame-py to load and understand FRAME data.
Enforces lifecycle, runs mechanical validation, gates agent actions, records run history.
Haxaml is the tool. frame-py is its library dependency.

---

## 2. FRAME file structure

Each FRAME file is made of **blocks** (e.g., `architecture`, `quirks`, `commands`).
Each block contains **fields** (scalar values) or **sub-blocks** (nested objects).

Files: facts.yaml, rules.yaml, map.yaml, expect.yaml, acts.yaml
Shared: every file has a `frame` header block with file, schema_version, role, scope, status, last_reviewed, updated_by, update_reason.

---

## 3. Design principles

1. **Proportionality.** Small projects fill less. Large projects fill more. Same schema, different depth.
2. **Token/character caps per field.** Each field has a max length. Enforced by frame-py on load.
3. **Links before duplication.** Reference another block's ID instead of repeating the same truth.
4. **Tool-facing, not just human-facing.** Fields must be structured enough that Haxaml can query them programmatically.
5. **Readable to a developer reading the YAML file directly.** The files are the interface.
6. **No redundancy.** If content fits an existing block, use that block. Don't spawn new blocks for one-off problems.
7. **Agents fill, devs review.** Agents generate FRAME content. Developers verify and correct. The files are human-editable.

---

## 4. Field decisions

### frame header (shared across all 5 files)

| Field | Type | Required | Max | Decision |
|---|---|---|---|---|
| file | string (enum: facts/rules/map/expect/acts) | yes |  --  | |
| schema_version | string (const: "0.3.0") | yes |  --  | |
| role | string | yes |  --  | |
| scope | string (enum: baseline_project/execution_record/handoff/mixed/null) | no |  --  | |
| status | string (enum: draft/active/deprecated) | yes |  --  | |
| last_reviewed | date | no |  --  | |
| updated_by | string | no | 100 chars | |
| update_reason | string | no | 500 chars | |

---

### Facts blocks

| Block | Field | Type | Required | Max | Decision |
|---|---|---|---|---|---|
| **profile** | name | string | yes | 100 chars | |
| | summary | string | yes | 300 chars | |
| | repo_shape | string | no | 50 chars | **FIXED ENUM:** split-backend-frontend, monorepo, single-package, monolith, microservices |
| | delivery_family | string | no | 50 chars | **FIXED ENUM:** cli, web-app, mobile-app, sdk, infra-tooling, data-pipeline, desktop-app, browser-extension, static-site, chatbot, game, devops-automation |
| **classification** | kind | string | no | 100 chars | |
| | surface_count | integer | no |  --  | |
| | surfaces | array[string] | no | 200 chars each | |
| **technology** | (structured object) | object | no | 2000 chars total | **STRUCTURED.** Required keys: language, framework, database. Optional free-form extensions. |
| **architecture** | summary | string | yes | 500 chars | **STRUCTURED + ANNOTATION.** Required human-readable summary. |
| | backend_layers | array[string] | no | 300 chars each | Optional structured sub-blocks. Each has an optional `_note` for human annotation. |
| | frontend_layers | array[string] | no | 300 chars each | |
| | data_flow | string | no | 500 chars | |
| | deployment_topology | string | no | 500 chars | |
| **environments** | (free-form per-env object) | object | no | 1000 chars total | |
| **persistence** | (free-form object) | object | no | 1000 chars total | |
| **sources** | (array) | array | no |  --  | |
| sources[] | id | string | yes | 100 chars | |
| | path | string | yes | 200 chars | |
| | purpose | string | yes | 300 chars | |
| **quirks** | (array) | array | no |  --  | |
| quirks[] | id | string | yes | 100 chars | |
| | description | string | yes | 200 chars | |
| | why | string | yes | 300 chars | |
| **open_questions** | (array) | array | no |  --  | |
| open_questions[] | id | string | yes | 100 chars | |
| | question | string | yes | 300 chars | |
| | context | string | yes | 300 chars | |

---

### Rules blocks

| Block | Field | Type | Required | Max | Decision |
|---|---|---|---|---|---|
| **governance_level** | (top-level field) | string | no |  --  | **FIXED ENUM:** relaxed, normal, strict. Default: normal. Controls how aggressively Haxaml enforces rules, ask_first, and validation. Does NOT affect mechanical validator (always runs). |
| **rules** | (array) | array | no |  --  | Core behavioral constraints |
| rules[] | id | string | yes | 100 chars | |
| | rule | string | yes | 500 chars | |
| **policies** | (array) | array | no |  --  | **Moved from Facts.** Policies are behavioral constraints, not current project truth. |
| policies[] | id | string | yes | 100 chars | |
| | name | string | yes | 150 chars | |
| | rule | string | yes | 500 chars | |
| **commands** | (object) | object | no |  --  | Named shell commands |
| commands.<name> | run | string | yes | 500 chars | Shell command |
| | kind | string | yes |  --  | **FIXED ENUM:** setup, verify, run |
| | purpose | string | yes | 300 chars | |
| **code_style** | (free-form object) | object | no | 1000 chars | |
| **git** | (free-form object) | object | no | 1000 chars | |
| **donts** | (array) | array | no |  --  | Things you must never do |
| donts[] | id | string | yes | 100 chars | |
| | rule | string | yes | 300 chars | |
| | severity | string | no |  --  | **FIXED ENUM:** critical, warning. Default: critical. |
| **ask_first** | (array) | array | no |  --  | **BOTH trigger types.** `trigger_type: file_pattern | task_pattern`. `trigger` holds the pattern. `reason` explains why. Enforcement determined by `governance_level` (relaxed | normal | strict). |
| ask_first[] | id | string | yes | 100 chars | |
| | trigger_type | string | yes |  --  | **FIXED ENUM:** file_pattern, task_pattern |
| | trigger | string | yes | 300 chars | |
| | reason | string | yes | 300 chars | |
| **hints** | (array) | array | no |  --  | Skill references, gotchas |
| hints[] | id | string | yes | 100 chars | |
| | hint | string | yes | 300 chars | |

---

### Map blocks (to be populated)

| Block | Field | Type | Required | Max | Decision |
|---|---|---|---|---|---|
| **structure** | (top block) | string | no | 800 chars | **TOP BLOCK.** Quick visual overview of repo layout. Flat text like "Backend/ → FastAPI (routes→services→models), Frontend/ → Vue 3 (views→stores→services)". Connects to roots/groups/paths below. |
| **roots** | (free-form object) | object | no |  --  | Top-level directory purposes |
| **groups** | (array) | array | no |  --  | Logical groupings. **Supports wildcards** for flexible coverage as repos scale. |
| groups[] | id | string | yes | 100 chars | |
| | label | string | yes | 150 chars | |
| | paths | array[string] | yes | 300 chars each | **Wildcards allowed** (e.g., `Backend/app/**/*.py`). |
| **paths** | (array) | array | no |  --  | Critical individual files. **Explicit paths only.** |
| paths[] | id | string | no | 100 chars | **Optional id.** Needed when a path is referenced from expect.checks or acts.runs.touched. |
| | path | string | yes | 200 chars | |
| | purpose | string | yes | 300 chars | |
| **entrypoints** | (array) | array | no |  --  | CLI/API/web entry points. **Explicit paths only.** |
| entrypoints[] | id | string | yes | 100 chars | |
| | path | string | yes | 200 chars | |
| | kind | string | yes |  --  | **FIXED ENUM:** cli, api, web, script |
| **managed_paths** | (array) | array | no |  --  | Paths under special rules. **Supports wildcards.** |
| managed_paths[] | id | string | no | 100 chars | **Optional id.** Needed when rules reference specific managed paths (e.g., donts link to managed_paths.migrations). |
| | path | string | yes | 200 chars | **Wildcards allowed** (e.g., `node_modules/**`, `*.pyc`). |
| | rule | string | yes | 100 chars | **FIXED ENUM:** generated, config, immutable |
| **unmapped_paths** | (array) | array | no |  --  | Honest about gaps. Invites improvement. |
| unmapped_paths[] | path | string | yes | 200 chars | |
| | reason | string | yes | 200 chars | |

### Expect blocks (to be populated)

| Block | Field | Type | Required | Max | Decision |
|---|---|---|---|---|---|
| **outcomes** | (object) | object | no |  --  | Named expected results of work |
| outcomes.<name> | summary | string | yes | 300 chars | |
| **must_hold** | (array) | array | no |  --  | Invariants that must stay true |
| must_hold[] | id | string | yes | 100 chars | |
| | statement | string | yes | 300 chars | |
| **checks** | (object) | object | no |  --  | Named verification checks. **These feed the mechanical validator.** |
| checks.<name> | name | string | yes | 100 chars | |
| | what | string | yes | 300 chars | What is being checked |
| | command_ref | string | no | 200 chars | Ref to rules.commands.<name> |
| | pass_condition | string | no | 200 chars | **MACHINE-PARSEABLE.** `exit_code == 0`, `stdout contains "BUILD SUCCESS"`, `stdout matches "^[a-f0-9]{12}_"`, `file_exists "dist/index.html"` |
| **done_when** | (object) | object | no |  --  | Completion conditions |
| **proof** | (array) | array | no |  --  | Required evidence types |
| proof[] | id | string | yes | 100 chars | |
| | type | string | yes |  --  | **FIXED ENUM:** review, smoke_test, static_check, unavailable |
| | description | string | yes | 300 chars | |

### Acts blocks (to be populated)

| Block | Field | Type | Required | Max | Decision |
|---|---|---|---|---|---|
| **summary** | (top block) | string | no | 500 chars | Quick overview of recent activity |
| **runs** | (array) | array | no |  --  | Per-session run records |
| runs[] | id | string | yes | 100 chars | |
| | actor | string | yes | 100 chars | |
| | goal | string | yes | 300 chars | |
| | work_kind | array[string] | no |  --  | code, test, review, docs, deploy |
| | keywords | array[string] | no | 100 chars each | |
| | input_summary | string | no | 300 chars | |
| | output_summary | string | no | 300 chars | |
| | status | string | yes |  --  | pass, pass_with_risks, fail, needs_clarification |
| | touched | array[string] | no | 200 chars each | |
| | changed_facts | array[string] | no | 200 chars each | |
| | rules_followed | array[string] | no | 100 chars each | |
| | checks | array[object] | no |  --  | **Collapsed.** Status per check: `ran` (with result) or `skipped` (with reason). No redundancy. |
| checks[] | id | string | yes | 100 chars | Ref to expect.checks.<name> |
| | status | string | yes |  --  | **FIXED ENUM:** ran, skipped |
| | result | string | no |  --  | pass, fail (only when status=ran) |
| | reason | string | no | 200 chars | Why skipped (only when status=skipped) |
| **blockers** | (array) | array | no |  --  | Things preventing progress |
| blockers[] | id | string | yes | 100 chars | |
| | description | string | yes | 300 chars | |
| **handoff** | (free-form object) | object | no | 500 chars | What next agent needs to know |
| | | | | | |
| **archival** |  --  |  --  |  --  | Size cap: acts.yaml max 50KB. Exceeded → oldest runs auto-rotated to acts_archive/YYYY-MM-acts.yaml.gz. Hot file stays fast. History preserved. |

---

## 5. Architecture decisions

### Decision 0: One general FRAME schema for all project types
**Agreed:** 2026-06-09

No per-project-type FRAME variants. The same 5-part schema applies to all software categories.
Unused blocks are explicitly left empty/null/`[]`  --  this is valid and intentional.

### Decision 1: Agents fill FRAME, devs review
**Agreed:** 2026-06-09

Agents generate FRAME content by reading the codebase and project docs. Developers verify the output and correct mistakes. The files remain human-readable and human-editable.

### Decision 2: No redundancy rule
**Agreed:** 2026-06-09

If content can naturally and efficiently fit an existing block, use that block. Do not spawn new blocks for one-off problems in a specific repo.

### Decision 3: Policies moved from Facts to Rules
**Agreed:** 2026-06-09

Policies (role access, invoice lifecycle, audit policy) are behavioral constraints, not current project truth. They belong in Rules alongside rules, donts, and commands.

### Decision 4: Structured with annotation for architecture and technology
**Agreed:** 2026-06-09

Technology uses structured key:value (required: language, framework, database). Architecture uses a required `summary` text + optional structured sub-blocks, each with a `_note` for human annotation.

### Decision 5: Identity block removed
**Agreed:** 2026-06-09

The free-form `identity` catch-all is removed. `profile.name` and `profile.summary` are sufficient for project identity.

### Decision 6: Character limits enforced by field category
**Agreed:** 2026-06-09

Every field has a max character count. Core governance fields (ids, names, rules, donts, checks, pass_condition, command references) are **enforced**  --  frame-py refuses to load if exceeded. Descriptive blocks (code_style, git, architecture sub-blocks, environment descriptions, handoff notes) are **advisory**  --  Haxaml warns but loads. Characters, not tokens  --  no tokenizer dependency.

### Decision 7: id required on linkable array entries only
**Agreed:** 2026-06-09

`id` is required on array items that other FRAME files reference by ref. NOT required on text blocks, key-value objects where the key serves as identifier, or entries never cross-referenced.

| id required (linkable) | id NOT required (not referenced) |
|---|---|
| sources[], quirks[], open_questions[] | profile, classification, technology, architecture, environments, persistence |
| rules[], policies[], donts[], ask_first[] | code_style, git, hints[], commands (key is name) |
| groups[], entrypoints[], paths[] (optional), managed_paths[] (optional) | structure, roots, unmapped_paths[] |
| must_hold[], proof[] | outcomes (key is name), checks (key is name), done_when |
| runs[], blockers[] | summary, handoff |

### Decision 8: Link relations  --  closed set of 9
**Agreed:** 2026-06-09

`supports` merged into `explains`. Final set: uses, follows, checks, proves, points_to, changes, touches, explains, blocks. Closed  --  no custom relations. If a new relation is needed, it becomes a schema update.

### Decision 9: Schema files use JSON, FRAME files use YAML
**Agreed:** 2026-06-09

JSON Schema files that define FRAME's structure are written in JSON  --  they're consumed by validators, not read by humans. JSON requires no extra parsing step, is universally parseable, and is the native format of every JSON Schema validator. FRAME files (facts, rules, map, expect, acts) remain YAML for human readability.

| Relation | Meaning | Example |
|---|---|---|
| uses | A depends on B for operation | Rule uses a command |
| follows | A complies with B | Run follows a policy |
| checks | A validates B | Check validates an outcome |
| proves | A provides evidence for B | Test result proves expectation |
| points_to | A routes to a location B | Map entry points to file path |
| changes | A modified B's state | Run changes a fact |
| touches | A edited or inspected B | Run touches a file |
| explains | A provides reason or context for B | Quirk explains a rule |
| blocks | A prevents B from proceeding | Blocker blocks an outcome |

---

## 6. Open questions (from questions.md)

1. Should Rules.commands use a fixed schema (run, kind, purpose) or stay free-form?
2. Should donts have a severity field (critical vs warning)?
3. Should ask_first triggers be keyword-based, file-based, or pattern-based?
4. Should Expect.checks have a machine-parseable pass_condition field?
5. Should Map support wildcard paths or only explicit paths?
6. How do we handle Acts growing indefinitely? Rotation? Archival?
7. Should link relations be a fixed closed set or extensible?
8. Should token/character limits be enforced or advisory?
9. Should id fields be required on every addressable entry?
