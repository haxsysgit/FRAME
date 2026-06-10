# Fixture Fit Pass Prompt

Use this prompt when running a manual or subagent-based FRAME fit pass on a real repo fixture.

## Goal

Fit one candidate FRAME structure to one real repo.
Do not try to redesign FRAME from scratch during the pass.
The point is to expose pressure, not to freestyle architecture poetry.

## Inputs you should have

- fixture repo path
- fixture family / system role
- candidate FRAME structure name and short description
- current scoring rubric from `../scoring/rubric.md`
- output scorecard based on `../scoring/scorecard-template.toml`

## Pass order

### 1. Extract project reality first

Before fitting, identify the repo's most important reality:
- what the project is
- its main delivery surface(s)
- major code/package layout
- operating constraints or workflows that look important
- where the source of truth actually seems to live
- what would matter most to an agent trying to work inside it

Do this first so the fit is based on the repo, not on wishful schema matching.

### 2. Fit the candidate structure

Try to express that repo using the candidate FRAME structure.
For each major part or block, ask:
- what fits naturally?
- what feels forced?
- what becomes repetitive?
- what important project truth has no clean home?
- what would go stale too fast if FRAME tried to store it?

### 3. Record friction honestly

Capture:
- missing semantics
- boundary confusion
- repeated fields
- forced abstractions
- places where repo-specific extensions are cleaner than new core fields

Do not reward a candidate just because it can technically store something.
If it stores it awkwardly, that should hurt the score.

### 4. Score the fit by phase

#### Phase 1 -- Structural fit
Score these first and take them most seriously:
- coverage
- clarity
- stability

Main question:
Does this schema structurally fit the repo well enough to deserve further trust?

If two or more Phase 1 dimensions are 1 or 2:
- mark the candidate as structurally weak
- still record later-phase impressions if useful
- but do not let strong later scores override weak structural fit

#### Phase 2 -- Operational usefulness
Only after Phase 1 is understood, score:
- agent_usefulness
- retrieval_usefulness
- adoptability

Main question:
If this structure fits, would it actually help work happen more reliably inside the repo?

#### Phase 3 -- Pressure / cost
Then score:
- bloat_resistance
- token_efficiency

Main question:
Is the candidate still worth it once context cost and field-sprawl pressure are considered?

### 5. Write the result

Save a scorecard per fixture/candidate pair.
Prefer one file per evaluation so later comparison stays clean.

## Core rule

A new FRAME field should only be justified if it repeatedly improves:
- fit
- retrieval
- routing
- verification
- or downstream agent behavior

If it just makes the document look more complete, that is probably bloat.

## Evidence rule

For every score of 1 or 2, include:
- a short explanation
- at least one concrete repo anchor (file, folder, or README section)

That keeps the evaluation grounded in the fixture instead of evaluator vibes.
