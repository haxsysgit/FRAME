# FRAME LinkedIn series plan

Status: working progression plan
Purpose: keep the FRAME series from jumping into lab evidence before the audience understands the problem.

## Core rule

Do not make Post 1 carry everything.

The series should move from relatable pain → simple FRAME idea → structure → lab method → test progress → adjustment method → Haxaml.

Frame Lab evidence matters, but it should arrive after the audience understands why the evidence matters.

## Audience path

The reader should feel this progression:

1. “Yeah, agent context really is messy.”
2. “Okay, this is not just another memory trick.”
3. “I understand the five parts without needing schema docs.”
4. “Now I see why Frame Lab exists.”
5. “The fixtures are proof pressure, not random examples.”
6. “The scoring/weight method is how the structure changes safely.”
7. “Haxaml is where this becomes useful in real agent work.”

## Series outline

### Post 1 -- The problem: agents are strong, project context is weak

Job:
- introduce the pain
- relate with developers who use agents
- avoid fixture scores and lab details
- create the reason FRAME needs to exist

Core story:
Agents are getting better, but projects still explain themselves badly. We keep feeding agents scattered docs, old chats, rules files, README fragments, and tribal knowledge. Bigger context windows do not solve scattered truth. They just let us carry more mess.

Basically I am saying:
If agents are becoming part of development, then the project itself needs a clearer way to explain what is true, what matters, what changed, and what should not be touched.

Mention lightly:
- this is what pushed me toward FRAME
- FRAME is still early and being tested
- future posts will show the lab/tests

Do not include yet:
- aggregate scores
- fixture names in detail
- weight/scoring algorithm
- schema adjustment mechanics
- Haxaml architecture

### Post 2 -- The simple FRAME idea: better-shaped context, not more context

Job:
- define FRAME simply
- keep it intuitive before schema talk

Core story:
FRAME is my attempt to give a project a typed shape that agents and humans can both use. It is not “more docs.” It is a way to separate different kinds of project truth so they do not keep fighting each other.

Explain lightly:
- Facts = what is true
- Rules = what must be obeyed
- Map = where things live
- Expect = what should pass/prove correctness
- Acts = what happened during work

Basically I am saying:
A project should not have to reintroduce itself from scratch every time a new agent enters.

### Post 3 -- Why five parts: not five files, five jobs

Job:
- explain why the parts exist
- avoid sounding like ontology/schema overkill

Core story:
The five parts are not there because five sounds elegant. They exist because different project truths behave differently. Stable facts should not be mixed with run history. Rules should not be buried inside old chat. Checks should not be confused with proof. File maps should not live only in someone’s memory.

Possible mini-illustration:
- If a backend role changed from SALES to STAFF, where should that truth live?
- If an agent only inspected tests but did not run them, where should that be recorded?

### Post 4 -- Frame Lab: how I stop FRAME from becoming theory

Job:
- introduce Frame Lab as the testing workshop
- now bring in the “not just vibes” idea

Core story:
FRAME Lab exists because a context architecture can sound clever and still fail on real repos. So the lab fits a candidate shape to real projects, scores the fit, investigates weak claims, and only changes the structure when pressure repeats.

Simple loop:
1. pick a fixture
2. fit the current FRAME shape
3. score where it works or feels forced
4. investigate weak claims
5. adjust only when pressure repeats
6. rerun

Basically I am saying:
The schema does not get to grow just because one repo made it uncomfortable.

### Post 5 -- The fixtures: why organize, autopahe, and Pharmax matter

Job:
- introduce the current test set
- show why each fixture stresses FRAME differently

Core story:
I picked different repo shapes because one repo can teach a standard bad habits.

Fixtures:
- organize: tiny Python CLI, tests whether FRAME can stay lightweight
- autopahe: Python CLI/package with browser setup, Playwright, Docker, config, state paths
- Pharmax: FastAPI + Vue app with workflow pressure, role policy, frontend/backend boundaries, deployment drift, generated-state noise

Basically I am saying:
If FRAME only works on the easy repo, it has not earned trust.

### Post 6 -- Current test progress: what v0.2.0 taught me

Job:
- share scores and findings
- now the data makes sense because the reader already knows the method

Use evidence:
- organize 4.25 / 5
- autopahe 4.29 / 5
- Pharmax 4.50 / 5
- average 4.35 / 5

Findings:
- simpler names helped immediately
- the five parts behaved more like one linked brain
- Acts became useful as run history
- no new core blocks were needed under this pressure
- proof discipline still needs tightening

### Post 7 -- The adjustment method: weights, pressure, and resisting bloat

Job:
- explain your “weight” idea simply
- show how FRAME changes without turning into a field monster

Simple explanation:
A weight is how much repeated pressure a problem applies to the design. One weird repo does not automatically earn a new block. A problem becomes heavier when it appears across fixtures, affects agent usefulness, causes repeated confusion, or blocks typed tooling.

Possible weight factors:
- does this pain repeat across fixtures?
- does it change agent behavior?
- does it improve retrieval or verification?
- does it reduce duplication?
- does it stay understandable to normal devs?
- does it avoid making the schema bloated?

Basically I am saying:
FRAME should adjust from repeated pressure, not from vibes.

### Post 8 -- Where Haxaml fits

Job:
- connect FRAME to implementation/tooling
- avoid making Haxaml sound like it owns FRAME

Core story:
FRAME is the project representation. Haxaml is the runtime/tooling layer that can use that representation during real agent work.

Explain simply:
- FRAME says what the project knows
- Haxaml helps agents operate against that knowledge
- Acts/Expect become important because agent work needs proof, handoff, and safe memory updates

### Optional later posts

- Why Acts matters more than I expected
- Why bigger context windows do not solve project memory
- Why Markdown memory files are useful but not enough
- What I learned from Pharmax as a workflow-heavy fixture
- What I learned from autopahe as browser/tooling pressure
- Why I care about typed references across all five parts

## Post 1 guardrails

Post 1 should not feel like a lab report.
It should feel like the start of a series from someone who keeps running into the same agent-context problem.

Tone target:
- raw but readable
- young developer thinking in public
- simple social-media wording, not rigid grammar
- preserve Arinze’s rough phrasing when it carries the idea
- remove generic AI-assistant phrases like “Honestly, I think...”
- no forced emoji unless it actually fits the line

Good phrases:
- “Basically i am saying...”
- “That is where things start getting messy.”
- “The model is not always the weak part anymore.”
- “More context does not automatically mean better context.”

Avoid in Post 1:
- too many scores
- fixture names unless teased very lightly
- schema vocabulary overload
- long list of findings
- proof/investigator details

## Visual progression

Post 1 visual:
- context rot / scattered project truth

Post 2 visual:
- simple five-part FRAME shape

Post 3 visual:
- five parts as five jobs, not five files

Post 4 visual:
- Frame Lab loop

Post 5 visual:
- fixture set map

Post 6 visual:
- current scores and findings

Post 7 visual:
- weight/pressure adjustment loop

Post 8 visual:
- FRAME + Haxaml runtime relationship
