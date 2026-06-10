# FRAME Lab

FRAME Lab is where FRAME gets pressure-tested against real repos instead of winning arguments on vibes alone.

The job here is simple:
- fit candidate FRAME structures to real projects
- score how well they work
- record what feels forced, missing, or bloated
- keep iterating until the stable/adoptable shape becomes obvious

## What this folder is for

- `fixtures/` -- real repos used as test fixtures. Each fixture keeps source code under `project/` so notes and outputs can live beside it.
- `candidates/` -- candidate FRAME shapes being compared.
- `evaluations/task-prompts/` -- repeatable prompts/instructions for fit passes.
- `evaluations/fits/` -- generated FRAME fits for candidate/fixture combinations.
- `evaluations/scorecards/` and `evaluations/scoring/` -- scorecards, rubric, templates, and aggregation helpers.
- `evaluations/reports/` -- saved comparison results and scoring summaries.

## Default loop

1. pick a fixture from the active core set
2. extract the important project reality first
3. fit a candidate FRAME structure to it
4. score the fit using the shared rubric
5. compare results across fixtures and candidates
6. revise FRAME only where the pressure keeps repeating

## Working rule

Start compact. Use the active fixture set first:
- `organize` -- small CLI/script fixture
- `autopahe` -- Python automation/tooling fixture
- `pharmax` -- full-stack pharmacy web app fixture

Only add more fixtures when the current candidate survives the core loop and needs harder pressure.

## What we are optimizing for

Not elegance by itself.
Not max schema coverage.

We want the sweet spot where FRAME is:
- useful to agents and humans
- structurally clear
- broadly adoptable across real repos
- lean enough not to become a schema museum

Basically: enough structure to help, not enough to become homework.
