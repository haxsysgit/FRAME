# FRAME Candidate: frame-five-part-v0.2.0

This candidate is the simplified version of the current FRAME five-part shape.

Goal:
- keep the five-part brain
- make names obvious on sight
- make links first-class across all 5 parts
- stop solving pressure by adding more blocks
- make typed models and tooling easier to build

## Core idea

FRAME is one typed project brain with 5 linked parts:
- Facts
- Rules
- Map
- Expect
- Acts

Each part owns a different kind of truth.
But they should work together through clear refs instead of repeated prose.

Important:
FRAME is not being optimized as five raw files that must feel magical by themselves.
The deeper value shows up when typed tooling like Haxaml uses the fields for:
- governance
- retrieval
- routing
- safer edits
- better cross-agent handoff

So when we refine a field, the question is not just:
- is this nice for a human to read?

It is also:
- can a tool use this to help an agent make a sharper decision?

## Naming rule

Prefer names a normal developer can understand at a glance.

If a name sounds abstract, too clever, or needs a schema lecture, replace it.

## Top-level naming changes

### Shared header
- `representation_scope` -> `scope`

Reason:
- shorter
- more obvious
- still clear in typed models

### Facts
- `project_profile` -> `profile`
- `source_truth` -> `sources`
- `structural_quirks` -> `quirks`
- `ambiguities` -> `open_questions`

Keep:
- `identity`
- `classification`
- `technology`
- `architecture`
- `environments`
- `persistence`
- `policies`
- `evidence`

### Rules
- `critical_rules` -> `rules`
- `git_workflow` -> `git`
- `negative_instructions` -> `donts`
- `stop_and_ask` -> `ask_first`
- `skill_hints` -> `hints`

Keep:
- `commands`
- `code_style`
- `evidence`

### Map
- `classifications` -> `groups`
- `access_points` -> `entrypoints`

Keep:
- `roots`
- `paths`
- `managed_paths`
- `unmapped_paths`
- `evidence`

### Expect
- `invariants` -> `must_hold`
- `verify` -> `checks`
- `required_evidence` -> `proof`

Keep:
- `outcomes`
- `done_when`
- `handoff`

### Acts
Drop the old reflective structure.

Replace:
- `representation_policy`
- `action_overview`
- `reflect_loop`
- `actions`
- `archive`

With:
- `summary`
- `runs`
- `blockers`
- `handoff`

Reason:
Acts should be obvious and practical.
It is run history, not a second project summary.
Its job is to help future agents and tools answer things like:
- what kind of work happened here?
- what area was touched?
- when did we last do something similar?
- which facts changed?
- which checks were only referenced and which were actually run?

## Simple typed link pattern

Every addressable entry should be able to expose:
- `id`
- `links`
- `evidence`

### Ref shape
Use simple dotted refs:
- `facts.profile`
- `facts.sources.runtime_code`
- `facts.quirks.readme_name_drift`
- `rules.commands.help`
- `map.entrypoints.cli`
- `expect.checks.cli_help`
- `acts.runs.fit_organize_round3`

### Link object
Use:
- `rel`
- `ref`

Example:
```yaml
links:
  - rel: uses
    ref: rules.commands.help
  - rel: checks
    ref: expect.checks.cli_help
```

## Allowed link relations

Use a small set.
Do not invent relation names casually.

- `uses`
- `follows`
- `checks`
- `proves`
- `points_to`
- `changes`
- `touches`
- `supports`
- `explains`
- `blocks`

### Relation meaning
- `uses` = this entry depends on another entry for operation
- `follows` = this run or rule follows another rule/policy
- `checks` = this entry validates another entry
- `proves` = this evidence proves or supports another entry
- `points_to` = this entry routes to a file/path/surface
- `changes` = this run changed a fact or stateful truth
- `touches` = this run edited or inspected a file/path/group
- `supports` = this entry gives supporting context
- `explains` = this entry gives the reason or explanation for another
- `blocks` = this blocker or constraint prevents another thing

## Ownership rule

Use links before duplication.

The same truth should not be rewritten in 3 or 4 places just to make files feel complete.

Preferred pattern:
1. define stable truth once in the best owner file
2. link to it from other files
3. only restate when a different file genuinely needs a different angle

## File ownership

### Facts owns
- stable project truth
- what the project is
- main shape
- main stack
- stable policies
- quirks
- trusted sources
- open questions

### Rules owns
- how to work safely in the repo
- commands
- do and do-not guidance
- ask-first triggers
- code style and git norms

### Map owns
- where things live
- main repo surfaces
- entrypoints
- path groups
- managed paths

### Expect owns
- what should stay true
- what counts as done
- what needs to be checked
- what proof is required

### Acts owns
- run history
- what went in
- what came out
- what was touched
- what changed
- what rules were followed
- what checks were run
- blockers and handoff

## Acts typed shape

Acts should center on `runs`.

Each run should store:
- `id`
- `actor`
- `goal`
- `work_kind`
- `keywords`
- `input_summary`
- `output_summary`
- `status`
- `touched`
- `changed_facts`
- `rules_followed`
- `checks_seen`
- `checks_ran`
- `links`
- `evidence`

Reason:
- `work_kind` helps tools filter runs by type of work
- `keywords` helps retrieval by topic or area
- `checks_seen` keeps planning/review links useful
- `checks_ran` keeps proof honest

### Example
```yaml
runs:
  - id: payment_bugfix_round12
    actor: agent_backend_fix
    goal: Fix payment callback bug and tighten payment status handling
    work_kind:
      - code
      - test
    keywords:
      - payment
      - checkout
      - webhook
      - status-sync
    input_summary: Read payment service, checkout flow, recent payment bug notes, and related expectations
    output_summary: Patched callback handling, updated payment status mapping, added regression coverage, and refreshed payment-related acts links
    status: complete
    touched:
      - map.paths.payment_service
      - map.paths.checkout_service
      - map.groups.payments
    changed_facts:
      - facts.quirks.payment_status_drift
    rules_followed:
      - rules.rules.no_silent_status_changes
      - rules.ask_first.payment_provider_contract_change
    checks_seen:
      - expect.checks.payment_callback_contract
      - expect.checks.checkout_regression
    checks_ran:
      - expect.checks.checkout_regression
    links:
      - rel: touches
        ref: map.groups.payments
      - rel: changes
        ref: facts.quirks.payment_status_drift
      - rel: follows
        ref: rules.rules.no_silent_status_changes
      - rel: checks
        ref: expect.checks.checkout_regression
```

This lets a future agent or Haxaml-style tool ask:
- show me recent payment-related runs
- find runs tagged checkout or webhook
- find the last run that changed payment facts
- find similar runs that touched payment surfaces

## Acts retrieval rule

Acts should help future work cycles.

A good Acts run should make it easier for a later agent to ask:
- what similar work happened before?
- what area did that run touch?
- what kind of work was it?
- what facts changed?
- what checks were actually run?

That is why `work_kind`, `keywords`, `touched`, `changed_facts`, and the split between `checks_seen` and `checks_ran` matter.

This is not memory for memory's sake.
It is structured retrieval support for governance and decision quality.

## Typed modeling rule

A candidate is better when the same shape would be easy to express in:
- Pydantic
- Python dataclasses
- TypeScript types
- Rust structs
- JSON Schema

That means:
- obvious field names
- stable ownership
- reusable small entry shapes
- simple refs
- few junk-drawer fields

## Anti-bloat rule

Do not add a new core block or entry type unless it repeatedly earns its place by improving:
- fit
- routing
- retrieval
- checks
- governance
- or downstream agent behavior

If a new field mostly makes the doc feel more complete, it is probably bloat.

## What the next round should test

The next 3-fixture round should test whether this simplification:
- makes names easier to understand instantly
- reduces repetition
- makes cross-links more natural across all 5 parts
- makes Acts clearly useful as run history
- stays typed and tool-friendly
- avoids pushing us toward more blocks again
