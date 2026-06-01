# Core seven project cards

This is the stricter comparison format for the working seven fixtures.

Rules for this file:
- one fixed card shape for every project
- short, grounded, and structural
- project representation first
- no deep feature encyclopedia

Fixed card fields
- fixture_id
- repo_root
- delivery_family
- system_role
- primary_stack
- repo_shape
- major_surfaces
- structural_rules
- run_verify_surface
- source_of_truth
- frame_pressure

---

## 1) organize

- fixture_id: `organize`
- repo_root: `Frame lab/fixtures/organize/project`
- delivery_family: tiny CLI utility
- system_role: file/folder organization helper
- primary_stack: Python 3, stdlib only, argparse
- repo_shape: near-minimal single-script repo with README and LICENSE
- major_surfaces:
  - `organize.py`
  - `README.md`
- structural_rules:
  - command-line flags are the whole interface
  - filesystem mutation is the core behavior, so path safety matters
  - scaffolding is weak: no package metadata, no test suite discovered
  - docs drift exists: README examples say `file_manager.py` while the real script is `organize.py`
  - Linux default path is hardcoded in code, which is a real repo-specific quirk
- run_verify_surface:
  - `python3 organize.py --help`
  - path/flag-based manual runs
- source_of_truth:
  - CLI arguments and behavior: `Frame lab/fixtures/organize/project/organize.py`
  - usage/docs: `Frame lab/fixtures/organize/project/README.md`
- frame_pressure:
  - pressures FRAME on tiny-repo representation
  - checks whether FRAME stays lean when the project is basically one script
  - checks whether structural quirks can be captured without inventing big abstractions

---

## 2) autopahe

- fixture_id: `autopahe`
- repo_root: `Frame lab/fixtures/autopahe/project`
- delivery_family: medium CLI/tooling app
- system_role: AnimePahe assistant/downloader helper
- primary_stack: Python >= 3.10, Typer, Click, Rich, requests, BeautifulSoup, Playwright, setuptools/pyproject, Docker
- repo_shape: medium Python package repo with docs, tests, config handling, release notes, Docker, and local-state handling
- major_surfaces:
  - `auto_pahe.py`
  - `cli.py`
  - `ap_core/`
  - `features/`
  - `collection/`
  - `tests/`
  - `pyproject.toml`
  - `README.md`
- structural_rules:
  - Playwright install/setup is part of the real operating shape
  - browser-assisted downloads are core pressure, not side decoration
  - config is OS-specific and stored in platform config dirs
  - fixture-adapted imports are a structural quirk worth preserving during fitting
  - package/docs/tests/Docker all matter to project reality at once
- run_verify_surface:
  - `uv sync`
  - `uv run playwright install chromium`
  - `uv run autopahe --help`
  - pytest-style test runs
  - Docker build/run path exists
- source_of_truth:
  - package + dependency truth: `Frame lab/fixtures/autopahe/project/pyproject.toml`
  - usage/setup: `Frame lab/fixtures/autopahe/project/README.md`
  - entrypoints: `auto_pahe.py`, `cli.py`
  - package structure: `ap_core/`, `features/`, `collection/`
- frame_pressure:
  - pressures FRAME on medium CLI/package shape
  - checks whether operation/setup/state/config can be captured without collapsing into feature soup
  - checks whether project representation can hold browser/runtime dependencies cleanly

---

## 3) pharmax

- fixture_id: `pharmax`
- repo_root: `Frame lab/fixtures/pharmax/project`
- delivery_family: full-stack business app
- system_role: pharmacy operations platform
- primary_stack: Backend Python 3.12+, FastAPI, SQLAlchemy, Alembic, Pydantic, uv; Frontend Vue 3, Pinia, Vue Router, Vite, Vuestic UI, ECharts
- repo_shape: split backend/frontend app repo with docs, planning/progress docs, scripts, and tests
- major_surfaces:
  - `Backend/`
  - `Frontend/`
  - root docs like `README.md`, `PROJECT_BRIEF.md`, `PROGRESS.md`
  - backend app tree and frontend src tree
- structural_rules:
  - backend/frontend separation is a first-class project boundary
  - env and deployment assumptions matter heavily
  - docs + code + progress notes all contribute to current project reality
  - realistic repo noise exists, including checked-in frontend dependencies and at least one README/filesystem mismatch around `render.yaml`
  - a lot of project truth is spread across multiple surfaces, so representation quality really matters
- run_verify_surface:
  - backend: `uv sync`, `cp .env.example .env`, `uv run fastapi dev main.py`
  - frontend: `npm install`, `npm run dev`, `npm run build`
  - backend migrations/scripts/tests exist
- source_of_truth:
  - root overview: `Frame lab/fixtures/pharmax/project/README.md`
  - backend setup/shape: `Frame lab/fixtures/pharmax/project/Backend/README.md`, `Backend/pyproject.toml`, `Backend/app/`
  - frontend setup/shape: `Frame lab/fixtures/pharmax/project/Frontend/package.json`, `Frontend/src/`
  - planning/progress reality: `PROJECT_BRIEF.md`, `PROGRESS.md`
- frame_pressure:
  - pressures FRAME on split-surface app representation
  - checks whether repo boundaries, operational assumptions, and source-of-truth spread can be captured cleanly
  - strong test for avoiding app-specific core-field explosion

---

## 4) httpie/cli

- fixture_id: `httpie-cli`
- repo_root: `Frame lab/fixtures/public/cli/cli`
- delivery_family: mature CLI tool
- system_role: human-friendly HTTP client
- primary_stack: Python >= 3.7, requests ecosystem, rich, Pygments, multidict, pytest
- repo_shape: mature Python CLI package with package code, tests, docs, packaging/extras, and release workflows
- major_surfaces:
  - `httpie/`
  - `tests/`
  - docs and packaging config
  - plugin surfaces
  - CI/release workflows
- structural_rules:
  - command surface is central, not incidental
  - plugin/extension model is real project structure
  - config/session behavior is first-class project reality
  - release/distribution workflow is part of the repo shape
- run_verify_surface:
  - `make all`
  - `make test`
  - `make test-cover`
  - `python3 -m httpie --version`
- source_of_truth:
  - package/config: `Frame lab/fixtures/public/cli/cli/setup.cfg`
  - entry + core CLI flow: `httpie/__main__.py`, `httpie/core.py`, `httpie/cli/definition.py`
  - plugins: `httpie/plugins/`
  - tests: `tests/`
- frame_pressure:
  - pressures FRAME on mature command-centric repo shape
  - checks whether plugins, distribution, and docs/tests structure fit naturally
  - good contrast against autopahe without becoming giant

---

## 5) modelcontextprotocol/python-sdk

- fixture_id: `python-sdk`
- repo_root: `Frame lab/fixtures/public/sdk/python-sdk`
- delivery_family: protocol SDK
- system_role: Python SDK for MCP
- primary_stack: Python >= 3.10, anyio, httpx, pydantic v2, starlette, uvicorn, jsonschema, uv, ruff, pyright, pytest
- repo_shape: very clean src/tests/examples/docs/scripts repo with explicit public API discipline
- major_surfaces:
  - `src/`
  - `tests/`
  - `examples/`
  - `docs/`
  - `scripts/`
  - project rules/docs like `AGENTS.md`
- structural_rules:
  - public API is deliberately controlled
  - test tree mirrors source tree strongly
  - `uv` and frozen command flows matter to contribution discipline
  - typing/lint/test standards are part of the project shape, not just optional hygiene
- run_verify_surface:
  - `uv run mcp`
  - `uv run --frozen pytest`
  - `./scripts/test`
  - `uv run --frozen ruff format .`
  - `uv run --frozen ruff check . --fix`
  - `uv run --frozen pyright`
- source_of_truth:
  - package/config: `Frame lab/fixtures/public/sdk/python-sdk/pyproject.toml`
  - contributor rules: `AGENTS.md`
  - current v2 direction: `README.v2.md`
  - API root: `src/mcp/__init__.py`
  - tests: `tests/`
- frame_pressure:
  - pressures FRAME on clean SDK/protocol repo shape
  - checks whether architecture and contributor rules can be represented without bloated memory-like fields
  - useful contrast against app-shaped repos

---

## 6) terragrunt

- fixture_id: `terragrunt`
- repo_root: `Frame lab/fixtures/public/infra-tooling/terragrunt`
- delivery_family: infra tooling CLI
- system_role: Go-based infra orchestration/tooling in the OpenTofu/Terraform ecosystem
- primary_stack: Go, OpenTofu/Terraform/HCL ecosystem, mise, golangci-lint, bats, shellcheck, shfmt, jq, bun
- repo_shape: Go CLI repo with `internal/`, `pkg/`, `test/`, `docs/`, CI workflows, and a large fixture/integration surface
- major_surfaces:
  - `main.go`
  - `internal/`
  - `pkg/`
  - `test/`
  - `test/fixtures/`
  - `test/flake/`
  - `.github/workflows/`
- structural_rules:
  - CI and integration matrices are part of core project structure
  - infra fixtures are central, not examples-only
  - build/lint discipline is strict
  - nested helper tooling adds subproject pressure without turning the repo into a full monorepo
- run_verify_surface:
  - `mise install`
  - `make build`
  - `go test -v -coverprofile=coverage.out -covermode=atomic ./... -timeout 45m`
  - formatting/lint via make and pre-commit flows
- source_of_truth:
  - module/build root: `Frame lab/fixtures/public/infra-tooling/terragrunt/go.mod`, `main.go`
  - internal structure: `internal/`, `pkg/`
  - fixtures/tests: `test/`
  - CI: `.github/workflows/`
- frame_pressure:
  - pressures FRAME on code + config-fixture forest + CI matrix representation
  - checks whether infra tooling shape can be captured without turning FRAME into a test manifest dump

---

## 7) twentyhq/twenty

- fixture_id: `twenty`
- repo_root: `Frame lab/fixtures/public/web-app/twenty`
- delivery_family: large workspace web app
- system_role: open-source CRM monorepo
- primary_stack: TypeScript, Yarn 4, Nx, React, Jotai, Linaria, Lingui, Vite, NestJS, TypeORM, GraphQL, PostgreSQL, Redis, BullMQ, Docker/K8s/Helm/Podman
- repo_shape: large packages-based monorepo/workspace with frontend, server, shared libs, docs, website, SDK, extension, e2e, and infra surfaces
- major_surfaces:
  - `packages/`
  - `packages/twenty-front/`
  - `packages/twenty-server/`
  - `packages/twenty-shared/`
  - `packages/twenty-docker/`
  - workspace config and convention docs
- structural_rules:
  - Node and Yarn versions are pinned
  - npm is intentionally blocked
  - coding conventions are explicit and strong
  - database migration discipline is explicit
  - Nx targets and workspace rules are part of project reality
- run_verify_surface:
  - `yarn start`
  - `npx nx start twenty-front`
  - `npx nx start twenty-server`
  - `npx nx run twenty-server:worker`
  - `npx nx test twenty-front`
  - `npx nx test twenty-server`
  - `npx nx run twenty-server:test:integration:with-db-reset`
- source_of_truth:
  - workspace root: `Frame lab/fixtures/public/web-app/twenty/package.json`, `nx.json`
  - contributor/project rules: `CLAUDE.md`
  - major package roots: `packages/twenty-front/`, `packages/twenty-server/`, `packages/twenty-shared/`, `packages/twenty-docker/`
- frame_pressure:
  - pressures FRAME on large monorepo/workspace representation
  - checks whether order survives across many packages and conventions without drowning in repetition
  - useful high-pressure ceiling fixture for later passes

---

## What this stricter format is for

This file is the fixed extraction layer before real FRAME fitting.

So the loop becomes:
1. extract project cards in this fixed shape
2. fit a FRAME candidate against one card
3. score the fit
4. compare repeated pressure across fixtures

That keeps the fitting grounded in project reality instead of schema vibes.
