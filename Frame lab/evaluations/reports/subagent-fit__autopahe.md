# frame-five-part-v0 on autopahe

Candidate: `frame-five-part-v0`
Fixture: `autopahe`
Repo root: `Frame lab/fixtures/autopahe/project`

## Short verdict

The five-part candidate fits `autopahe` better than it fits a tiny repo, because this fixture really does have multiple active surfaces: package metadata, CLI entrypoints, Playwright/browser setup, stateful config/data paths, tests, and Docker.

The fit is still not frictionless.

Main result:
- `facts`, `rules`, and `map` all have legitimate work to do here
- `expect` can hold repo-level verification anchors, but it starts leaning toward task QA notes if left unchecked
- `acts` is still weak and feels imported from a different job than project representation

## Grounded fixture reality

From repo inspection:
- project is a Python CLI/package repo for AnimePahe search, browser-download handoff, streaming, sorting, and record/collection management
- source installs are documented around `uv sync`, `uv run playwright install chromium`, and `uv run autopahe --help`
- Playwright browser setup is part of the real operating shape, not side decoration
- config, cache, data, and logs are routed through platform-specific helpers
- state is centralized and includes migration from legacy locations
- the fixture carries a repeated `example_projects.autopahe` import prefix across runtime code and tests
- checked-in `dist/`, `data/`, `__pycache__/`, and release-note/history material add repo noise that should not be mistaken for core source
- tests are small but real, especially around CLI normalization and setup preservation

Key anchors:
- `Frame lab/fixtures/autopahe/project/pyproject.toml`
- `Frame lab/fixtures/autopahe/project/README.md`
- `Frame lab/fixtures/autopahe/project/cli.py`
- `Frame lab/fixtures/autopahe/project/auto_pahe.py`
- `Frame lab/fixtures/autopahe/project/ap_core/platform_paths.py`
- `Frame lab/fixtures/autopahe/project/config.py`
- `Frame lab/fixtures/autopahe/project/ap_core/updater.py`
- `Frame lab/fixtures/autopahe/project/tests/test_cli.py`
- `Frame lab/fixtures/autopahe/project/tests/test_setup.py`

## Candidate fit by part

### 1) facts
What fit cleanly:
- project identity, delivery family, system role
- primary stack and runtime dependencies that materially shape operation
- repo shape as a medium Python package/tooling repo
- structural quirks like fixture-adapted imports and checked-in state/artifact noise
- persistence reality: platform-specific config/data/cache/log paths and migration behavior

What felt slightly forced:
- the schema has no crisp built-in slot for recurring structural quirks/drift hazards, so some of that ended up as prose under classification/architecture

### 2) rules
What fit cleanly:
- real operating constraints belong here: install Playwright, respect path helpers, keep source-update vs installed-tool update flows distinct
- commands work well for setup and smoke-test anchors
- negative instructions are useful because the fixture contains tempting but misleading checked-in state/artifact paths

What felt forced:
- some “rules” are really operating facts with imperative phrasing added
- the command list risks overlapping with `expect.verify`

### 3) acts
What fit cleanly:
- almost nothing from the repo itself
- only a minimal note about why acts is thin felt honest

Why that matters:
- this fixture again suggests `acts` is not naturally part of baseline project representation
- it makes more sense as execution-time history than as repo description

### 4) map
What fit cleanly:
- this repo really benefits from a map because boundaries matter: `cli.py` vs `auto_pahe.py`, `ap_core/`, `features/`, `collection/`, `tests/`
- access points also fit naturally: console entry, setup path, config command workflow
- `managed_paths` is useful for the state/config/browser-profile surfaces

What felt forced:
- `classifications` and `paths` can start saying similar things when summarizing important surfaces
- `unmapped_paths` is mildly awkward when the goal is simply “these are secondary, don’t overread them”

### 5) expect
What fit cleanly:
- repo-level correctness anchors like setup preserving config, browser handoff being real behavior, and help/test verification paths
- this part is a reasonable home for “what should still be true after edits”

What felt forced:
- it is easy for `expect` to drift from project correctness contract into task-level acceptance criteria
- verify items repeat the same commands already named in `rules`

## Friction found

### Clean fits
- identity and stack in `facts`
- setup/runtime constraints in `rules`
- repo boundaries in `map`
- smoke-test and regression anchors in `expect`

### Forced fits
- trying to make `acts` carry meaningful project truth
- placing recurring fixture quirks without a sharper first-class home

### Repetition risk
- `facts.architecture.major_surfaces` vs `map.paths`
- `rules.commands` vs `expect.verify`
- quirk notes repeated across facts, rules, and report prose if not tightly controlled

### Missing semantics
- no especially clean built-in slot for “structural quirk / drift hazard” even though autopahe clearly has them
- limited distinction between descriptive operational truth and prescriptive rule when setup constraints are both

### Stale-risk fields
- detailed command inventories copied too literally from README
- broad feature lists for search/download/stream/collection behavior
- over-describing checked-in data/artifact directories that are not stable source-of-truth surfaces

## What autopahe is teaching us about FRAME

1. The schema scales up better than it scales down.
   - A medium repo with real boundaries gives most parts something legitimate to do.

2. Browser/runtime prerequisites are core project truth.
   - This fixture proves FRAME needs to capture operational setup without turning into install-doc paste.

3. Persistence and path logic matter structurally.
   - `autopahe` is not just “a CLI”; it is a CLI with OS-specific state layout and legacy migration behavior.

4. Repetition pressure rises once a repo has both commands and verification paths.
   - The current five-part split can represent them, but it does not strongly prevent overlap.

5. `acts` still looks orthogonal.
   - Even here, where the repo is richer than `organize`, `acts` did not become a strong project-representation surface.

## Practical recommendation after this pass

Keep pressure-testing the five-part candidate, but carry forward three warnings:
- `acts` still looks like system/execution memory, not baseline repo representation
- recurring quirks/drift hazards deserve a cleaner home than scattered prose
- command and verification fields need stronger anti-duplication discipline
