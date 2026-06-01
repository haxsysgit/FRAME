# FRAME Lab subagent loop plan

This is the first real multi-agent loop for FRAME fitting.

Important note:
- yes, the existing schema set in `~/FRAME/schemas/` is needed
- it is the baseline candidate under test
- the earlier metadata/card work was intentionally pre-schema so we would not let the old schema tell us what reality is
- now that the grounding layer exists, the old schema becomes the thing we pressure-test against that reality

So for this loop:
- candidate under test = current five-part schema in `schemas/`
- supporting grounding layer = `Frame lab/fixtures/metadata/core-seven-project-cards.md`
- repeated-signal target = `Frame lab/fixtures/metadata/frame-required-signals.md`
- scoring rubric = `Frame lab/evaluations/scoring/rubric.md`

---

## Team roles for the first loop

### 1) fitter-organize
Job:
- fit the current five-part schema to `organize`
- produce actual draft FRAME files
- keep them lean and grounded

Outputs:
- `Frame lab/evaluations/fits/frame-five-part-v0/organize/facts.yaml`
- `Frame lab/evaluations/fits/frame-five-part-v0/organize/rules.yaml`
- `Frame lab/evaluations/fits/frame-five-part-v0/organize/acts.yaml`
- `Frame lab/evaluations/fits/frame-five-part-v0/organize/map.yaml`
- `Frame lab/evaluations/fits/frame-five-part-v0/organize/expect.yaml`
- `Frame lab/evaluations/reports/subagent-fit__organize.md`

### 2) fitter-autopahe
Job:
- fit the current five-part schema to `autopahe`
- produce actual draft FRAME files
- keep them lean and grounded

Outputs:
- `Frame lab/evaluations/fits/frame-five-part-v0/autopahe/facts.yaml`
- `Frame lab/evaluations/fits/frame-five-part-v0/autopahe/rules.yaml`
- `Frame lab/evaluations/fits/frame-five-part-v0/autopahe/acts.yaml`
- `Frame lab/evaluations/fits/frame-five-part-v0/autopahe/map.yaml`
- `Frame lab/evaluations/fits/frame-five-part-v0/autopahe/expect.yaml`
- `Frame lab/evaluations/reports/subagent-fit__autopahe.md`

### 3) schema-critic
Job:
- inspect the current `schemas/` candidate against the required-signal sheet
- identify likely overfit, underfit, and repetition risks before scoring

Output:
- `Frame lab/evaluations/reports/schema-critic__frame-five-part-v0__round1.md`

### 4) scorer-organize
Job:
- score the organize fit using the shared rubric
- ground claims in repo anchors and the produced fit files

Output:
- `Frame lab/evaluations/scoring/frame-five-part-v0__organize__subagent.toml`

### 5) scorer-autopahe
Job:
- score the autopahe fit using the shared rubric
- ground claims in repo anchors and the produced fit files

Output:
- `Frame lab/evaluations/scoring/frame-five-part-v0__autopahe__subagent.toml`

### 6) investigator
Job:
- compare generated fits against real repo anchors
- catch overclaims, omissions, and stale-risk fields

Output:
- `Frame lab/evaluations/reports/investigator__organize_autopahe__round1.md`

### 7) synthesizer
Job:
- collect repeated wins, repeated friction, and candidate change proposals from the fitters/scorers/investigator

Output:
- `Frame lab/evaluations/reports/synthesis__frame-five-part-v0__round1.md`

### 8) supervisor (Hermes)
Job:
- scope each task tightly
- verify outputs exist
- validate candidate artifacts where possible
- prevent agent drift and vague claims
- summarize what the round actually proved

---

## Working rules

1. The schema is under test, not sacred.
2. The project cards are grounding, not final FRAME.
3. Do not invent broad memory/context buckets to make the fit feel easier.
4. Repetition across facts/rules/map/expect is a smell and should be called out.
5. `acts` is allowed to look weak if the repo does not naturally justify it.
6. Repo anchors beat evaluator vibes.
7. Keep tiny repos tiny; do not write FRAME fanfiction for `organize`.

---

## Round 1 scope

Use only:
- `organize`
- `autopahe`

Why this pair:
- `organize` checks whether the schema scales down
- `autopahe` checks whether the same schema scales up to a medium package/tooling repo with runtime/setup pressure

This is the smallest honest loop that can expose both under-structure and over-structure.
