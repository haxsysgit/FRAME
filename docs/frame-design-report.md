# FRAME Design Report

This report is the current design correction for FRAME after the reset.

It is written to answer a specific need:
- make FRAME's aim precise enough that Haxaml and multiple agents can test-fit it consistently
- pressure-test the five-part candidate without blindly freezing it
- reduce bloat before more implementation hardens the wrong ideas

## Executive summary

FRAME should be treated as a project-context architecture for AI-assisted work.
It is not just a schema set, not just a memory product, and not just a Haxaml feature.

Its job is to organize the minimum structured project reality that tools and agents need in order to:
- understand what a project is
- obey the right constraints
- look in the right places
- know what counts as correct
- carry forward checked work without excessive drift

The five-part candidate still looks useful:
- Facts
- Rules
- Acts
- Map
- Expect

But the value of FRAME does not come from having five files.
The value comes from whether those files help tools act better across multiple project families with acceptable overhead.

So the next phase should not be "implement the old schema harder."
It should be:
1. sharpen FRAME aim and boundaries
2. define how tools like Haxaml would use FRAME in real tasks
3. test candidate structure across project families in Frame Lab
4. freeze only the structure that survives those tests

## The problem FRAME is really solving

Today project truth gets scattered across:
- prompt files
- README files
- docs
- issue threads
- commit history
- human memory
- agent-specific instruction files

That creates two common failures:
1. drift: different agents use different fragments of project truth
2. waste: every agent has to re-scan the repo to rediscover the same basics

FRAME should solve that by creating a portable context layer that is:
- structured enough for tools
- simple enough for humans
- neutral enough for many runtimes
- small enough to stay worth maintaining

## Standardized FRAME aim

Recommended working description:

> FRAME is a portable architecture for storing the minimum structured project reality needed for AI agents and tools to work consistently inside a software repository.

Expanded form:

> FRAME separates project reality into a small set of context shelves so tools can understand what the project is, what they must obey, where they should look, what has happened, and what counts as correct.

This description matters because it prevents FRAME from collapsing into any one of these wrong identities:
- not a generic notes system
- not a full knowledge graph
- not a replacement for source code
- not a verbose documentation framework
- not a one-tool-specific runtime format

## What FRAME is not

This needs to stay brutally clear.

FRAME is not:
- a substitute for reading the actual code
- a full project management system
- a universal archive of every past action
- a giant schema for every imaginable repo fact
- a place to dump speculative metadata because it sounds intelligent

If a field does not help a tool or human do better work often enough, it should not live in core FRAME.

## The real role of the five candidate files

The five-part split is still a strong candidate because it mirrors recurring context needs.

### Facts
What stable project reality is currently believed to be true?

### Rules
What must an agent or tool obey while working here?

### Acts
What checked work, blockers, decisions, and handoff state are worth carrying forward?

### Map
Where should a tool look first in the repo, and what do those places broadly mean?

### Expect
What outcomes, checks, and done conditions define correctness for the current direction of work?

That said, the five-part idea should remain a candidate architecture, not sacred canon.

The test is not whether the labels sound clean.
The test is whether they reduce drift across real repos.

## How Haxaml would actually use FRAME

This is the key practical question.

Haxaml should not treat FRAME as a pretty static schema.
It should treat FRAME as a context-routing layer.

### Haxaml usage model

A strong usage loop looks like this:

1. classify the incoming task
   - bug fix
   - feature addition
   - refactor
   - infra/setup
   - investigation
   - documentation

2. read just the relevant FRAME slices
   - Facts for stable reality
   - Rules for constraints
   - Map for where to inspect
   - Expect for correctness target
   - Acts for recent verified work or blockers

3. assemble a task-specific context packet
   - short project identity
   - relevant commands/rules
   - likely paths
   - likely invariants
   - current blockers or unknowns

4. direct the agent/tool into repo inspection
   - FRAME points the agent where to start
   - source code and real files still confirm truth

5. verify work against Expect and Rules
   - run the right checks
   - collect evidence
   - record only durable useful outcomes in Acts

6. update FRAME carefully
   - only update fields whose truth genuinely changed
   - do not let temporary run noise pollute stable shelves

### What each file should do in Haxaml context assembly

#### Facts in Haxaml
Used to answer:
- what family is this repo?
- what stack is confirmed?
- what runtime or persistence assumptions matter?
- what broad system shape should the tool expect?

Facts should activate context, not narrate the universe.

#### Rules in Haxaml
Used to answer:
- what commands are canonical?
- what actions are forbidden?
- when must the agent stop and ask?
- what style/process constraints matter?

Rules should change behavior directly.
If a rule does not influence behavior, it may just be documentation pretending to be control.

#### Map in Haxaml
Used to answer:
- where should the agent inspect first?
- what directories/modules are probably relevant?
- what paths are generated, vendor, or managed?
- where are likely entry points?

Map should reduce blind repo wandering.

#### Expect in Haxaml
Used to answer:
- what outcome is the agent aiming for?
- what invariants must remain true?
- what evidence or checks count as done?

Expect should shape verification, not force a fake script.

#### Acts in Haxaml
Used to answer:
- what was recently verified?
- what blockers are still active?
- what decision/handoff state matters?
- what previous attempt should not be repeated blindly?

Acts should be trusted only when checked against rules/evidence freshness.

## What FRAME needs to stay useful without becoming bloated

FRAME only works if it stays disciplined.

### Core anti-bloat rules

1. every core field must justify its runtime use
   - if Haxaml or another tool never uses it, question it

2. stable shelves should stay stable
   - Facts should not absorb temporary run noise
   - Rules should not be rewritten by one execution
   - Map should not become a giant prose wiki

3. missing is better than fake precision
   - wrong map summaries are worse than absent ones
   - guessed facts are worse than explicit unknowns

4. cross-file links should be earned
   - not every item needs a graph edge
   - over-linking becomes maintenance tax

5. the core should stay family-portable
   - if a field only matters for one project family, it probably belongs in an extension or family profile

6. evidence should support trust, not ceremony
   - evidence fields are useful only if they help tools decide whether to trust a claim

### Practical anti-bloat test

Before freezing a field into core FRAME, ask:
- what tool behavior does this field improve?
- in which project families does it matter?
- what happens if it is absent?
- how often will it go stale?
- is it core or should it be optional/family-specific?

If the answer is fuzzy, the field is probably not ready for core.

## Current schema verdict

The current schema set is promising, but not complete enough for the full FRAME claim.

### Strong areas now
- shared frame header
- IDs/refs/links direction
- evidence direction
- rules-oriented entries like questions, hints, text entries
- simple map summaries
- explicit unknowns/ambiguities direction

### Weak or still underdesigned areas
- typed facts substructure across project families
- acts as a true checked activity record
- blocker semantics across files
- expectation verification semantics
- graph/reference rules strong enough for automation
- runtime context assembly policy
- distinction between advisory vs blocking rule behavior

This means the right move is not blind schema-to-Pydantic mirroring.
The right move is selective modeling:
- encode the parts that are already strong
- keep weak parts provisional
- let Frame Lab pressure decide what matures next

## Project-family fit: what the current structure likely handles well vs badly

### Likely good early fit
- small CLIs
- single-service APIs
- SDKs with clear entry points
- utility repos with limited moving parts

### Likely medium fit
- web apps with frontend/backend split
- moderate monorepos
- infra tools with runtime/deploy concerns

### Likely weak fit right now
- fast-moving startup codebases with messy boundaries
- enterprise repos with layered compliance/process constraints
- large monorepos with many subdomains
- legacy repos with weak docs and mixed conventions

That is not a failure.
It is exactly why Frame Lab should start early.

## What Frame Lab should be

Frame Lab should not be just a folder of examples.
It should be the proving ground for FRAME family fit.

### Frame Lab purpose

Frame Lab exists to answer:
- what stays stable across repo families?
- what is family-specific?
- what feels natural vs forced?
- what fields pay rent in real tool usage?
- what should be dropped before core freezes?

### Frame Lab should contain
- public example repos or clean snapshots from different project families
- candidate FRAME files fitted to those repos
- notes on what fit naturally and what felt forced
- evaluation prompts/tasks for agents
- comparison notes against native project docs without FRAME

### Recommended initial family set
- CLI
- backend API
- web app
- monorepo
- SDK/library
- infra/tooling repo
- messy/legacy repo

### Recommended Frame Lab folder direction

```text
Frame lab/
  README.md
  families/
    cli/
    backend-api/
    web-app/
    monorepo/
    sdk/
    infra-tooling/
    legacy-mixed/
  fixtures/
    organize/
    autopahe/
    pharmax/
  evaluations/
    task-prompts/
    scoring/
    reports/
  fitting-notes/
    facts.md
    rules.md
    acts.md
    map.md
    expect.md
```

The family folders describe what that family typically needs.
The fixture folders hold actual repos or curated snapshots.
The fitting notes capture what survives repeated fitting work.

## The right testing sequence

A better order from here:

1. freeze FRAME aim and boundaries
2. define the minimal meaning of each candidate shelf
3. create Frame Lab structure
4. add family fixtures
5. fit candidate FRAME structure to each fixture
6. record friction, redundancy, missing semantics, and stale-risk fields
7. only then revise schemas and language models
8. only then implement stricter validation and graph behavior

## What should probably freeze early

Freeze early only what is broadly portable and low-regret:
- shared frame header
- role of each candidate file
- explicit unknowns
- minimal valid empty state
- simple IDs where repeated entries exist
- rules/map/expect basics that already help real context routing

## What should not freeze early

Do not freeze yet:
- heavy graph/reference machinery
- complex activity semantics
- aggressive confidence models
- detailed family-specific facts inventory
- automatic synchronization rules across files
- verbose metadata with unclear runtime value

## Concrete design recommendation for frame-python

frame-python should become a testing implementation, not a premature authority.

Its near-term job should be:
1. model the strong shared primitives
2. model very small typed shells for the five files
3. preserve provisional zones explicitly
4. load YAML cleanly
5. generate reports about fit, ambiguity, and missing semantics
6. support lab evaluation, not just validation

That means frame-python should help answer:
- what is strict?
- what is provisional?
- what broke when fitting a real repo family?
- what fields seem redundant across families?

## The design standard for every future FRAME field

A field should enter core FRAME only if it passes all of these:
- improves tool behavior
- understandable by humans without ceremony
- useful in more than one project family
- maintainable without high stale risk
- distinct from neighboring fields
- not better represented as code inspection or extension metadata

## Bottom line

FRAME should become a small, portable, agent-usable project-context architecture.

Its legitimacy will not come from elegant theory alone.
It will come from surviving contact with many repo families while staying useful, editable, and lean.

So the immediate priority is not more generic implementation.
The immediate priority is:
- sharpen the standard description
- start Frame Lab early
- test the five-part candidate against real project families
- freeze only what repeatedly proves its value
