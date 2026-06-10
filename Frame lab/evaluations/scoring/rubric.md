# FRAME Lab Phased Scoring Rubric

Use a 1-5 scale for each dimension.

- 1 = weak / clearly failing
- 2 = partial but rough
- 3 = workable with notable friction
- 4 = strong
- 5 = excellent / unusually clean fit

This rubric is now phased on purpose.

Why:
- early schema work should answer "does this structure fit real project reality?" first
- only after that should we care more about usefulness and context cost

Do not treat the final weighted number like magic.
The phase breakdown matters more than one tidy average.

---

## Phase 1 -- Structural fit

Phase 1 asks:
Can this candidate structure represent the project cleanly enough to earn further attention?

This phase is about whether the schema has a believable shape.
Not whether it is already maximally helpful or compact.

### 1. Coverage
Can the candidate capture the important project reality without obvious holes?

What to look for:
- project identity
- major code surfaces
- important rules/constraints
- major operating expectations
- source-of-truth locations that would matter to an agent

Concrete example -- `pharmax`:
- A strong candidate should have a clean way to represent that Pharmax is not just a generic CRUD app.
- It is a pharmacy operations platform with role-based workflows: ADMIN, CASHIER, STAFF.
- It has two major delivery surfaces: `Backend/` and `Frontend/`.
- It has operational rules like admin approval for registrations, invoice lifecycle states, and environment-sensitive deployment behavior.

High score:
- the schema can capture those realities without awkward workarounds

Low score:
- role-based workflow semantics, split frontend/backend structure, or deployment constraints keep spilling into vague extensions

### 2. Clarity
Is the structure understandable without schema archaeology?

What to look for:
- distinct jobs for each part
- low boundary confusion
- low temptation to store the same thing in multiple places

Concrete example -- `pharmax`:
If the evaluator keeps asking:
- should invoice lifecycle rules go in rules or facts?
- should role-based permissions live in facts, rules, or map?
- should `render.yaml` deployment assumptions live in map or expect?

...then clarity is weak, even if the schema can technically store everything.

High score:
- an evaluator can explain why a Pharmax fact belongs where it belongs

Low score:
- the schema technically fits the project, but placement choices feel like coin flips

### 3. Stability across fixtures
Does the same structure keep making sense across different repo shapes?

What to look for:
- does the candidate that works for `pharmax` also still make sense for something smaller like `httpie/cli`?
- does it stay coherent when moving from app workflow repos to tool repos?

Concrete example:
A candidate might look great on Pharmax because Pharmax has rich workflow/state structure.
But if the same candidate becomes bloated or silly on `httpie/cli`, it is probably overfit to richer product apps.

High score:
- the candidate travels from Pharmax to simpler or differently shaped fixtures without bending out of shape

Low score:
- it feels like it secretly expects every repo to have roles, workflows, deployment contracts, or app-state complexity

### Phase 1 gate

Phase 1 is the gate.
If the candidate does badly here, do not let strong later-phase scores distract you.

Practical rule:
- if two or more Phase 1 dimensions score 1 or 2, treat the candidate as structurally weak
- you may still record later-phase impressions, but the main conclusion should stay: the fit is not earned yet

---

## Phase 2 -- Operational usefulness

Phase 2 asks:
If the structure fits, would it actually help agents and humans work inside the repo?

This is where we judge whether FRAME is becoming useful rather than just well-organized.

### 4. Agent usefulness
Would this likely improve agent behavior inside the repo?

What to look for:
- better task setup
- better constraint-following
- better routing to the right code or docs
- better behavior around project-specific rules

Concrete example -- `pharmax`:
A strong candidate should help an agent avoid dumb mistakes like:
- editing cashier behavior without noticing role separation
- changing invoice logic without realizing lifecycle constraints matter
- treating frontend and backend as one undifferentiated surface

Another concrete example:
If FRAME could help an agent quickly understand that Pharmax has inventory, invoice, auth, audit, and deployment concerns split across specific areas, that is real usefulness.
Not decorative usefulness. Real behavioral usefulness.

High score:
- an agent would likely make better decisions after reading the FRAME representation

Low score:
- the schema stores information but would not materially change agent behavior

### 5. Retrieval usefulness
Does the candidate make important project truth easier to find and reuse?

What to look for:
- can a human or agent locate the right truth faster?
- does the structure reduce scavenger hunts across READMEs, code, env notes, and deployment files?

Concrete example -- `pharmax`:
Right now, key truth is split across:
- root `README.md`
- `Backend/README.md`
- `Frontend/README.md`
- code layout under `app/api/routes`, `app/services`, and env/config files

A strong candidate should make it easier to recover answers like:
- where invoice workflow logic lives
- what env vars matter most
- what role boundaries matter operationally
- where deployment assumptions come from

High score:
- the FRAME representation acts like a sharper retrieval index for Pharmax reality

Low score:
- the evaluator still has to re-read the repo docs/code almost as much as before

### 6. Adoptability / editability
Would a real team plausibly maintain this without hating it?

What to look for:
- learnable structure
- reasonable edit burden
- low stale-risk for core fields
- not too much ceremony

Concrete example -- `pharmax`:
If capturing Pharmax well requires constant manual updates for:
- role definitions
- invoice state changes
- deployment/env details
- service/module mapping

...then the candidate may be too expensive to maintain.

High score:
- the important stable truths can be maintained without turning FRAME into a second project README universe

Low score:
- every meaningful repo change would require a bunch of FRAME babysitting

---

## Phase 3 -- Pressure / cost

Phase 3 asks:
Even if this candidate fits and helps, is it worth the context cost?

This phase exists because FRAME should not become a giant tax on every project.

### 7. Bloat resistance
Does the candidate stay lean under pressure?

What to look for:
- resistance to field sprawl
- healthy use of extensions for niche truths
- refusal to turn every repo detail into core FRAME

Concrete example -- `pharmax`:
Pharmax tempts over-modeling.
You could easily try to add core fields for:
- every role
- every invoice state nuance
- every deployment/env nuance
- every backend service category
- every frontend view grouping

A good candidate resists that temptation.
It captures what is portable and important, then uses extensions or local notes for the rest.

High score:
- the schema stays disciplined even when the repo offers lots of detail to model

Low score:
- Pharmax causes the candidate to start growing new core fields for every interesting app-specific behavior

### 8. Token efficiency
Does the candidate seem reasonably compact relative to what it gives back?

What to look for:
- value per token
- concise representation of stable truth
- low repetition across parts

Concrete example -- `pharmax`:
If representing Pharmax requires repeating the same truths across facts, rules, map, and expect just to make the document feel complete, token efficiency is weak.

A strong candidate should let you express things like:
- two main app surfaces
- role-based workflow constraints
- key env/deployment assumptions
- source-of-truth locations

...without writing a small novel.

High score:
- strong project understanding for modest context cost

Low score:
- lots of text, modest payoff

---

## Default weighting

Use this default weighting unless a specific evaluation question says otherwise:

### Phase 1
- coverage = 1.50
- clarity = 1.50
- stability = 1.50

### Phase 2
- agent_usefulness = 1.25
- retrieval_usefulness = 1.25
- adoptability = 1.25

### Phase 3
- bloat_resistance = 1.50
- token_efficiency = 1.50

Why this weighting:
- Phase 1 has to matter most early because bad fit cannot be rescued by nice usefulness stories
- Phase 3 still matters a lot because FRAME loses if it becomes expensive context theater

---

## Required evidence for low scores

If any dimension is scored 1 or 2, add:
- what felt wrong
- whether the problem belongs to the candidate, the fixture weirdness, or the evaluation method
- at least one concrete repo anchor

Good anchors:
- `README.md` sections
- specific folders like `Backend/app/services/`
- concrete files like `render.yaml`
- route modules, schemas, env/config files, or workflow docs

Bad anchors:
- vague claims like "the project is complex"

---

## Tie-break rule

If two candidates score similarly, prefer the one that:
1. survives Phase 1 more cleanly
2. is easier to explain
3. is easier to maintain
4. adds fewer low-value fields

That bias is intentional.
FRAME should earn complexity, not smuggle it in.
