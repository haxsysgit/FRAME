# Investigator report: organize + autopahe fit reality check

Scope:
- compared generated FRAME fits under `Frame lab/evaluations/fits/frame-five-part-v0/`
- against real repo anchors in `Frame lab/fixtures/organize/project` and `Frame lab/fixtures/autopahe/project`
- using the grounding card + required-signal docs as the evaluation frame

## Executive verdict

Overall:
- `organize` fit is mostly grounded and appropriately lean, but it still smuggles a few task/meta statements into repo-facing files and overstates one live-run claim in `acts.yaml`.
- `autopahe` fit captures the repo shape reasonably well, but it misses the biggest repo-reality hazard: the fixture is import-rewritten to `example_projects.autopahe.*` even though no such package path exists in the workspace. Because of that, several run/verify claims read as if the source checkout is directly runnable when the checked fixture itself appears structurally broken without extra path adaptation.

Biggest grounded catches:
1. `autopahe` runability is overclaimed in `rules.yaml` and `expect.yaml`.
   - Fit files say `uv run autopahe --help` is the normal source-check smoke path.
   - Actual repo code imports `example_projects.autopahe...` throughout runtime and tests (`cli.py`, `auto_pahe.py`, `config.py`, tests), but there is no `example_projects/autopahe` package path anywhere under `/home/hax/FRAME`.
   - This is not just a quirk; it is a likely execution blocker.
2. `organize/acts.yaml` claims a help command was run, but the repo itself does not contain the output; the fit gives command-evidence without a persisted artifact.
3. Both repos show some schema-pressure leakage into `acts.yaml`: evaluation commentary and task/meta framing appear where project-activity truth should live.

---

## A. organize

Repo anchors used:
- `Frame lab/fixtures/organize/project/organize.py`
- `Frame lab/fixtures/organize/project/README.md`
- repo file listing from `Frame lab/fixtures/organize/project`

### What matches well

1. `organize/facts.yaml`
   - Correctly matches the card on project identity and scale.
   - Grounded claims that hold up:
     - tiny CLI utility
     - near-minimal single-script repo
     - stdlib-only Python surface
     - README/script-name drift (`file_manager.py` vs `organize.py`)
     - Linux hardcoded default path in code
   - Repo anchors:
     - `Frame lab/fixtures/organize/project/organize.py:10-16`
     - `Frame lab/fixtures/organize/project/organize.py:19-52`
     - `Frame lab/fixtures/organize/project/README.md:55-109`

2. `organize/rules.yaml`
   - The strongest rules are real and useful:
     - CLI flags are the public surface
     - path safety matters because the tool moves/deletes files
     - README command name drift must be checked against code
   - Repo anchors:
     - `Frame lab/fixtures/organize/project/organize.py:19-52`
     - `Frame lab/fixtures/organize/project/organize.py:92-192`
     - `Frame lab/fixtures/organize/project/organize.py:196-289`
     - `Frame lab/fixtures/organize/project/README.md:55-109`

3. `organize/map.yaml` and `organize/expect.yaml`
   - These stay fairly lean and keep the right anchors central:
     - `organize.py`
     - `README.md`
   - This fits the tiny-repo pressure from `frame-required-signals.md`.

### Overclaims / stale-risk

1. `Frame lab/evaluations/fits/frame-five-part-v0/organize/acts.yaml`
   - Overclaim: `actions[act_help_check]` says the CLI help command was run successfully and emitted a `SyntaxWarning`.
   - Problem: the fit cites only `source: "command: python3 organize.py --help"`; no captured output artifact is present in the repo or fit set.
   - This is stale-risk and weak grounding compared with file-backed anchors.
   - Repo anchor for the real help surface is only the parser definition in `Frame lab/fixtures/organize/project/organize.py:19-52`, not a saved run log.

2. `organize/map.yaml` and `organize/expect.yaml`
   - Stale-risk: both repeat command-evidence references (`"command: python3 organize.py --help"`) instead of grounding entirely in code and README.
   - This is not fatal, but it is more fragile than the repo itself warrants.

### Missed truths

1. `organize/facts.yaml` misses a sharper behavioral quirk in the actual mutation logic.
   - `create_ext_dir()` explicitly skips moving `organize.py` itself when bulk-organizing: `Frame lab/fixtures/organize/project/organize.py:177-181`.
   - That is a repo-specific safety/behavior detail and arguably more actionable than some of the more generic prose in the fit.

2. `organize/facts.yaml` / `organize/rules.yaml` do not mention that the script prints `args.__dict__` on normal invocation.
   - Repo anchor: `Frame lab/fixtures/organize/project/organize.py:62-64`.
   - This is a small but real UX quirk and possible drift hazard for agents expecting clean stdout.

### Misleading placements

1. `Frame lab/evaluations/fits/frame-five-part-v0/organize/acts.yaml`
   - `reflect_loop` is mostly schema commentary (`Acts feels weak on this fixture...`) rather than project activity.
   - This matches the loop-plan warning that `acts` may be weak, but it is still a placement smell: the file is carrying evaluator judgment more than repo truth.

Verdict for organize:
- Mostly accurate and lean.
- Main problems are evidence fragility in `acts.yaml` and mild schema-meta leakage.

---

## B. autopahe

Repo anchors used:
- `Frame lab/fixtures/autopahe/project/pyproject.toml`
- `Frame lab/fixtures/autopahe/project/README.md`
- `Frame lab/fixtures/autopahe/project/cli.py`
- `Frame lab/fixtures/autopahe/project/auto_pahe.py`
- `Frame lab/fixtures/autopahe/project/config.py`
- `Frame lab/fixtures/autopahe/project/ap_core/platform_paths.py`
- `Frame lab/fixtures/autopahe/project/ap_core/browser.py`
- `Frame lab/fixtures/autopahe/project/ap_core/updater.py`
- `Frame lab/fixtures/autopahe/project/collection/manager.py`
- `Frame lab/fixtures/autopahe/project/tests/*.py`
- repo file listing from `Frame lab/fixtures/autopahe/project`

### What matches well

1. `autopahe/facts.yaml`
   - The medium Python CLI/tooling classification is directionally correct.
   - Good grounded hits:
     - Python >= 3.10, Typer/Click/requests/bs4/Playwright/Rich stack
     - package-style repo with tests/docs/Docker/assets
     - setup/runtime pressure from Playwright
     - platform-path-based config/data handling
     - distinction between core CLI orchestration and heavier operational logic
   - Repo anchors:
     - `Frame lab/fixtures/autopahe/project/pyproject.toml:1-60`
     - `Frame lab/fixtures/autopahe/project/README.md:14-59`
     - `Frame lab/fixtures/autopahe/project/cli.py:21-24,184-230`
     - `Frame lab/fixtures/autopahe/project/config.py:19-130`
     - `Frame lab/fixtures/autopahe/project/ap_core/platform_paths.py:22-123`

2. `autopahe/rules.yaml`
   - Several structural rules are real and important:
     - Playwright is a real runtime prerequisite
     - platform-path helpers should be respected
     - source update flow differs from installed-tool upgrade flow
   - Repo anchors:
     - `Frame lab/fixtures/autopahe/project/README.md:24-45`
     - `Frame lab/fixtures/autopahe/project/ap_core/browser.py:50-87,179-197`
     - `Frame lab/fixtures/autopahe/project/ap_core/updater.py:74-145`

3. `autopahe/map.yaml`
   - Correctly points to `pyproject.toml`, `README.md`, `cli.py`, `auto_pahe.py`, `config.py`, `ap_core/`, `features/`, `collection/`, and `tests/` as the main working surfaces.

### Biggest overclaim: runnable source-check surface

1. `Frame lab/evaluations/fits/frame-five-part-v0/autopahe/rules.yaml`
   - `commands.run_help.run: uv run autopahe --help`
   - `commands.install_source.run: uv sync`
   - `commands.install_browser.run: uv run playwright install chromium`

2. `Frame lab/evaluations/fits/frame-five-part-v0/autopahe/expect.yaml`
   - `outcomes.cli_usable`
   - `verify.help_path`
   - both read as if a normal source checkout can reach CLI help after setup.

Why this is overclaimed:
- The checked fixture imports `example_projects.autopahe...` throughout the runtime and tests:
  - `Frame lab/fixtures/autopahe/project/cli.py:17-18,34`
  - `Frame lab/fixtures/autopahe/project/auto_pahe.py:63-90,368-369,1720`
  - `Frame lab/fixtures/autopahe/project/config.py:11-17`
  - `Frame lab/fixtures/autopahe/project/tests/test_cli.py:1`
  - `Frame lab/fixtures/autopahe/project/tests/test_setup.py:1-3`
- But there is no `example_projects/autopahe` path anywhere in `/home/hax/FRAME`.
- `pyproject.toml` defines `autopahe = "auto_pahe:main"`, not an `example_projects.autopahe` package remap.

What this means:
- The fit notices the fixture-adapted imports as a quirk, but it understates their operational consequence.
- In the repo as checked, this looks like a direct source-run blocker, not just a “preserve this import style” note.

This should have been elevated in at least one of:
- `autopahe/facts.yaml` as a high-severity structural quirk
- `autopahe/rules.yaml` as a stop-and-ask / verification hazard
- `autopahe/expect.yaml` as a qualifier on source-run claims

### Other overclaims / stale-risk

1. `Frame lab/evaluations/fits/frame-five-part-v0/autopahe/acts.yaml`
   - `actions[act_repo_inspection]` is acceptable as a process summary, but still not repo truth.
   - `reflect_loop` cites `Frame lab/evaluations/task-prompts/fixture-fit-pass.md:21-41`, which is evaluator/task context, not repo evidence.
   - This is a placement problem and weakens grounding.

2. `autopahe/facts.yaml`
   - `delivery_family: medium CLI/tooling app` is fine.
   - `system_role: AnimePahe assistant/downloader helper` is fine.
   - But `summary: Python CLI package for AnimePahe search, browser-download handoff, streaming, record management, sorting, and collection tracking.` is already nearing feature-list territory warned against by `frame-required-signals.md`.
   - Not false, but slightly inflated relative to the “project representation first, avoid feature encyclopedia” guidance.

3. `autopahe/map.yaml`
   - `roots.repo.summary` says “checked-in data/artifact noise.” This is broadly true, but the wording flattens meaningful docs/runtime surfaces with junk.
   - For example, `docker/` and `Docs/` are listed as `unmapped_paths`, even though README explicitly points users to `docker/` and docs/helper scripts are part of the actual operating surface.
   - Repo anchors:
     - `Frame lab/fixtures/autopahe/project/README.md:47-79`
     - file listing includes `docker/` and `Docs/`

### Missed truths

1. `autopahe/facts.yaml` and `autopahe/expect.yaml` miss the severity of the fixture import rewrite.
   - This is the largest omission in the whole pair review.

2. `autopahe/map.yaml` underplays the significance of `docker/`.
   - The README has multiple Docker run paths and helper scripts:
     - `Frame lab/fixtures/autopahe/project/README.md:47-79,197-220`
   - Marking `docker/` merely unmapped is misleading because Docker is a documented operating surface, not just side noise.

3. `autopahe/map.yaml` and `autopahe/facts.yaml` do not surface `ADVANCED.md`, even though it likely belongs closer to source-of-truth/supporting-doc surface than `release-notes/` or `__pycache__/`.
   - Repo anchor: root file listing includes `ADVANCED.md`.

4. `autopahe/facts.yaml` persistence section says `primary_location: platform config dir /config.ini`.
   - This is imprecise compared with the actual path model.
   - The real behavior is platform-specific app directories from `ap_core/platform_paths.py`, with `config.ini` under `get_config_dir()` and data under `get_data_dir()` / cache / logs.
   - The fit’s shorthand is understandable, but it is a stale-risk phrasing because it hides the actual OS-specific split.

### Misleading placements

1. `Frame lab/evaluations/fits/frame-five-part-v0/autopahe/acts.yaml`
   - Like `organize`, the `acts` file carries fit-process commentary more than repo activity.
   - This directly conflicts with the repo-first pressure and with the loop-plan note that `acts` should be allowed to stay weak instead of absorbing evaluation prose.

2. `Frame lab/evaluations/fits/frame-five-part-v0/autopahe/expect.yaml`
   - Some entries drift from repo correctness contract into task-execution advice.
   - The file itself even admits this in `handoff.notes`.
   - That self-awareness is useful, but it confirms the fit is not fully clean.

Verdict for autopahe:
- Structurally decent, but the largest real-world hazard is under-modeled.
- The fit recognizes fixture import rewriting but not strongly enough; it still presents source-run verification as straightforward when the checked fixture layout suggests otherwise.

---

## Cross-fit pattern findings

1. `acts.yaml` is weak in both repos, but the main failure mode is not emptiness.
   - The failure mode is evaluator/schema commentary being stored as project activity.
   - This matches the risk called out in `Frame lab/evaluations/reports/subagent-loop-plan.md:100-107` and `Frame lab/fixtures/metadata/frame-required-signals.md:248-260`.

2. Command-evidence is fragile when not backed by a saved artifact.
   - `organize` uses command references as if they were durable evidence.
   - `autopahe` uses README commands as if they were validated against the fixture’s actual import layout.

3. The best fit portions are still the lean structural ones.
   - facts/rules/map do best when they stick to identity, repo shape, boundaries, key paths, and quirks.
   - fits get shakier when they try to force activity history or task-level QA scripts into permanent repo files.

---

## Recommended corrections for next pass

1. For `autopahe`, promote the import-rewrite issue from minor quirk to major verification constraint.
   - Explicitly say the checked fixture path does not itself provide `example_projects/autopahe`.
   - Qualify or remove any direct source-run claims unless accompanied by the missing path adaptation.

2. For `organize`, downgrade the live help-run claim in `acts.yaml` unless a real saved execution artifact is included.

3. For both repos, trim evaluator commentary out of `acts.yaml`.
   - If nothing durable happened, keep `acts` nearly empty rather than storing fit-process reflection.

4. For `autopahe/map.yaml`, promote `docker/` from unmapped/noise-adjacent status to a named operating surface.

5. For `autopahe/facts.yaml` persistence wording, replace `platform config dir /config.ini` with a more exact summary of config/data/cache/log split from `ap_core/platform_paths.py` and `config.py`.

## Bottom line

- `organize` fit: mostly matches repo reality; main issues are fragile command-evidence and meta leakage into `acts`.
- `autopahe` fit: shape is mostly right, but the run/verify surface is materially overstated because the fixture-import rewrite appears incompatible with the actual checked path layout.
