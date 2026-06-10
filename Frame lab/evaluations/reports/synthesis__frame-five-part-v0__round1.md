# Round 1 synthesis -- frame-five-part-v0

Scope:
- fixtures: `organize`, `autopahe`
- candidate: current five-part schema in `schemas/`
- inputs used: schema critic, two fit reports, two scorecards, investigator report, and parent-side validation

Parent-side verification note:
- I re-validated all 10 produced YAML fit files against the current schemas with a local Python validator that resolves the cross-file schema refs.
- Result: all 10 fit files validate.

Important honesty note:
- the dedicated synthesis subagent hit a rate limit (`HTTP 429`) and did not complete
- this synthesis is therefore produced directly by Hermes from the verified artifacts above

---

## Short verdict

The old schema is absolutely needed.
But now it is being used the right way:
- not as the thing that defines reality
- as the candidate being pressure-tested against reality

Round 1 says:
- the candidate is real and usable
- it scales up better than it scales down
- `map` and `rules` are the strongest shelves
- `acts` is the weakest shelf for baseline project representation
- Phase 3 duplication pressure is already a real problem

---

## Repeated wins

### 1) The candidate can represent both fixtures without collapsing
Evidence:
- all 10 fit YAML files validated against the current schemas
- both fixtures were fitted into full five-part drafts

Why this matters:
- we are not dealing with a fantasy schema that instantly breaks on contact
- the baseline is viable enough to test seriously

### 2) `map` is consistently strong
Repeated pattern:
- it gave the cleanest home for key paths, access points, and major repo surfaces
- this showed up in the schema critic and both fit reports

Why this matters:
- source-of-truth anchors and repo navigation are clearly earned by the candidate

### 3) `rules` is consistently useful
Repeated pattern:
- it handled contributor/runtime constraints, setup cautions, and command surface better than the other parts
- especially strong on autopahe where real operating constraints exist

Why this matters:
- the candidate has a believable home for project discipline and safe-working rules

### 4) The candidate becomes more useful on medium repos
Repeated pattern:
- `autopahe` gave `facts`, `rules`, `map`, and `expect` legitimate work to do
- scores reflect that: autopahe was materially stronger than organize

Why this matters:
- the design is not inherently useless
- it just appears tuned more toward medium/richer repo shapes than tiny ones

---

## Repeated friction

### 1) `acts` keeps looking misaligned
Repeated pattern:
- weak in organize fit
- still weak in autopahe fit
- schema critic predicted this before scoring
- investigator found schema/evaluator commentary leaking into acts files

What this means:
- `acts` behaves more like execution/session/history memory than project representation
- that matches Arinze’s warning almost exactly

### 2) Facts / rules / map / expect can repeat the same truth too easily
Repeated pattern:
- organize repeated entrypoint/help/drift truths across multiple parts
- autopahe repeated major surfaces and setup/verify flows across multiple parts
- both scorecards punished this in Phase 3

What this means:
- the candidate can store truth, but it does not yet prevent “README 2: schema remix” behavior

### 3) There is no sharp home for structural quirks / drift hazards
Repeated pattern:
- organize: README says `file_manager.py`, repo has `organize.py`
- autopahe: fixture-adapted `example_projects.autopahe.*` imports materially affect how the repo should be interpreted
- both the schema critic and investigator called this out

What this means:
- known weird-but-important truths are getting smeared through prose instead of landing in one crisp place

### 4) Tiny repos expose cost failure fast
Repeated pattern:
- organize scorecard rejected the candidate for that fixture
- biggest failures were bloat resistance and token efficiency

What this means:
- the five-part split currently asks too much ceremony from tiny repos unless a strong compression discipline exists

---

## Investigator corrections that changed confidence

### 1) Autopahe source-run confidence should go down
Investigator catch:
- the fit treated `uv run autopahe --help` like a normal source-check path
- but the fixture imports `example_projects.autopahe.*` all over the codebase
- parent-side search confirmed those imports exist widely
- parent-side search also confirmed there is no `./example_projects/autopahe` path in the workspace

Why this matters:
- this is not a tiny wording issue
- it means the fit understated a likely execution blocker in the checked fixture

Correction:
- future autopahe fits should treat this as a high-severity structural quirk / verification hazard
- we should not present source-run verification as straightforward unless actually proven

### 2) Organize acts overclaim is softer than the investigator made it sound
Investigator catch:
- it said `organize/acts.yaml` overclaimed a live help run because no persisted artifact lives in the repo

Parent correction:
- Hermes did in fact run `python3 ./Frame lab/fixtures/organize/project/organize.py --help` earlier in the parent session
- so the claim is not fabricated
- but the investigator is still right about one thing: the evidence inside `acts.yaml` points to a command string, not a stronger saved artifact

Why this matters:
- this is more a grounding-quality issue than a false claim issue

Correction:
- keep the caution, but downgrade it from “overclaim” to “weak evidence packaging”

---

## Round 1 score picture

### organize
- coverage: 3
- clarity: 2
- stability: 2
- agent usefulness: 3
- retrieval usefulness: 2
- adoptability: 2
- bloat resistance: 1
- token efficiency: 1
- recommendation: `candidate_rejected`

Meaning:
- the candidate does not earn tiny-repo cleanliness yet

### autopahe
- coverage: 4
- clarity: 3
- stability: 3
- agent usefulness: 4
- retrieval usefulness: 4
- adoptability: 3
- bloat resistance: 2
- token efficiency: 2
- recommendation: `hold`

Meaning:
- usable on medium repos, but still paying too much duplication tax

---

## Candidate-change proposals after round 1

### Proposal 1: stop treating `acts` as mandatory baseline project representation
Best current interpretation:
- `acts` belongs more to execution memory / checked activity / session history
- not to the minimal project paraphrase layer

This does not force deletion yet.
But it does mean:
- score it skeptically in fit work
- do not let it contaminate project representation
- consider moving it out of the baseline project-core set later

### Proposal 2: add a crisp home for structural quirks / drift hazards
Need:
- known hazards that are real, settled, and likely to mislead future agents/devs

Because right now they get smeared across:
- facts prose
- rules cautions
- map summaries
- reports

That is ugly and duplication-prone.

### Proposal 3: tighten ownership boundaries between `rules.commands` and `expect.verify`
Needed distinction:
- `rules.commands` = how the repo is normally operated / invoked
- `expect.verify` = what counts as acceptable proof after changes

Without that, the same commands keep getting restated twice.

### Proposal 4: add an explicit tiny-repo compression rule
Needed behavior:
- if the repo is basically one script or very low-surface-area, the fit should not pretend all five parts deserve equal weight

This could be a fit policy first, even before schema surgery.

### Proposal 5: tighten `facts` so it is less junk-drawer friendly
Problem:
- several big open objects with `additionalProperties: true`

Effect:
- easy overlap
- easy prose sprawl
- weak placement discipline

---

## Strongest takeaway

Your former schema was not being ignored.
It was being held back until we had a grounded measuring surface.

Now that we do, round 1 is pretty clear:
- the schema has real bones
- it is not nonsense
- but it is currently too willing to duplicate truth
- and `acts` still looks like the odd one out for baseline project representation

That is exactly the kind of thing this lab is supposed to reveal.
