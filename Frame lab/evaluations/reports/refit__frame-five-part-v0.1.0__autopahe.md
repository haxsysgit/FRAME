# Refit report: frame-five-part-v0.1.0 / autopahe

Date: 2026-06-01
Fixture: `/home/hax/FRAME/Frame lab/fixtures/autopahe/project`
Output: `/home/hax/FRAME/Frame lab/evaluations/fits/frame-five-part-v0.1.0/autopahe`

## What was refit

Wrote the adjusted five-file FRAME v0.1.0 fit:

- `facts.yaml`
- `rules.yaml`
- `acts.yaml`
- `map.yaml`
- `expect.yaml`

The refit follows the adjusted schema intent:

- `facts.yaml` now uses `project_profile`, `source_truth`, and `structural_quirks` to separate compact project identity, authority ranking, and easy-to-misread hazards.
- `rules.yaml` keeps `commands` as command inventory and includes the required `kind` on every command.
- `expect.yaml` puts verification meaning in `verify` and links back to command inventory with `command_ref` instead of duplicating command strings.
- `acts.yaml` records checked activity/handoff only and explicitly declares `baseline_project_representation: false`.
- `map.yaml` focuses on boundaries and path classification rather than restating every file.

## Files inspected

Inspected actual fixture files before writing the fit, including:

- `pyproject.toml`, `requirements.txt`, `uv.lock` presence, `.python-version`
- `README.md`, `ADVANCED.md` presence, `Docs/`, `release-notes/`
- `auto_pahe.py`, `cli.py`, `kwikdown.py`, `config.py`, `state.py`
- `ap_core/browser.py`, `ap_core/config.py`, `ap_core/platform_paths.py`, `ap_core/updater.py`
- `features/`, `collection/`
- `tests/test_cli.py`, `tests/test_config.py`, `tests/test_setup.py`, `tests/test_kwikdown.py`, `tests/test_updater.py`
- `Dockerfile`, `docker-compose.yml`, `docker/README.md`
- `.gitignore` and fixture file listing for generated/state paths

## Main findings

- Autopahe is a Python CLI package (`autopahe = auto_pahe:main`) with a Typer/Click CLI wrapper and a larger root command implementation.
- Playwright/browser setup is a real operating boundary: source setup installs Chromium, runtime code offers install guidance, and `--verify-browser` opens a persistent browser profile for manual site verification.
- State/config/path behavior is centralized across `ap_core/platform_paths.py`, `ap_core/config.py`, and root `config.py`; root `config.py` has import-time directory creation/migration side effects.
- Tests are small but meaningful: they cover legacy CLI flag normalization, config fallback, setup preserving existing config, kwikdown helper behavior, and updater git-root detection.
- Docker support is first-class enough to model: a Playwright Python base image, Chromium install, editable package install, volumes, compose config, and helper scripts/docs are present.
- The fixture contains checked-in generated/state noise: `dist/`, `__pycache__/`, `data/`, backups, runtime JSON, and `.env` exist despite ignore rules excluding much of this kind of content.

## Friction / ambiguity

- Fixture imports use `example_projects.autopahe` across runtime modules and tests, which is a fixture adaptation hazard for any future import normalization.
- Dependency declarations differ slightly by surface: `pyproject.toml` has `playwright>=1.45.0`, `requirements.txt` pins `playwright==1.56.0`, and the Dockerfile uses `mcr.microsoft.com/playwright/python:v1.56.0-jammy`.
- Docker download/state paths have a small ambiguity: Dockerfile sets `AUTOPAHE_DOWNLOAD_DIR=/app/data/downloads`, while compose also mounts `~/Downloads/autopahe:/app/downloads`.
- No live project tests were required for the fit itself; schema conformance was checked locally after writing.
