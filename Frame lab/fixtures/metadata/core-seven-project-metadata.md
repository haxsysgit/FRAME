# Core seven project metadata

This is not a FRAME schema.
This is a short grounded extraction sheet for seven working comparison projects.

Goal:
- capture what the project is
- capture the stack
- capture the repo shape
- capture the main structural rules/constraints
- capture the basic run/test surface
- keep it short enough to compare across projects

Default working seven used here
1. organize
2. autopahe
3. pharmax
4. httpie/cli
5. modelcontextprotocol/python-sdk
6. terragrunt
7. twentyhq/twenty

Why these seven
- they include your three local examples first: organize, autopahe, pharmax
- then four public comparison repos with clearly different structural pressure:
  - mature CLI
  - SDK
  - infra tooling
  - large web-app monorepo

Sources used
- local READMEs, manifests, config files, project trees, key source files, and where useful basic command verification
- this file intentionally avoids deep feature-by-feature modeling

---

## Comparison matrix

| Project | Type | Main stack | Repo shape | Structural pressure |
| --- | --- | --- | --- | --- |
| organize | tiny script tool | Python stdlib | single-file CLI | minimal/no scaffolding, doc-code drift |
| autopahe | CLI/tooling app | Python, Typer, Playwright, Rich | medium Python package + docs + Docker + tests | browser automation, local state, packaging, fixture-adapted imports |
| pharmax | full-stack app | FastAPI, SQLAlchemy, Vue, Pinia, Vite | backend/frontend/docs/scripts/tests | split surfaces, env/deploy/docs/progress noise |
| httpie/cli | mature CLI | Python, requests, rich, pytest | package + docs + tests + release workflows | command surface, plugins, sessions, distribution |
| python-sdk | protocol SDK | Python, anyio, pydantic, httpx, uv | src/tests/examples/docs/scripts | strict public API, mirrored tests, transport surfaces |
| terragrunt | infra tooling CLI | Go, OpenTofu/Terraform ecosystem | Go CLI + internal/pkg + heavy fixtures + CI | infra config pressure, integration matrices, nested helper tool |
| twenty | large web-app monorepo | TypeScript, Nx, React, NestJS, Postgres, Redis | packages monorepo | multi-app workspace, explicit coding rules, infra breadth |

---

## 1) organize

Identity
- Tiny Python file-organization CLI.
- Upstream remote: haxsysgit/organize.

Stack
- Python 3
- stdlib-only imports found: os, sys, shutil, string, argparse

Repo shape
- basically `organize.py` + `README.md` + `LICENSE`
- no packaging metadata
- no test folder discovered

Key paths
- `Frame lab/fixtures/organize/project/organize.py`
- `Frame lab/fixtures/organize/project/README.md`

Key structural rules / constraints
- command-line flags drive everything
- side-effectful filesystem mutation tool: creates folders, moves files
- very small repo with weak scaffolding
- README examples refer to `file_manager.py` while actual script is `organize.py` (real doc/code drift)

Run / test surface
- `python3 organize.py --help`
- common operations are path/flag based
- no tests discovered

Why it matters for FRAME fitting
- perfect tiny baseline
- pressures FRAME to represent a real project even when the repo is almost all “just one script”
- good for checking whether FRAME overgrows on small projects

---

## 2) autopahe

Identity
- Cross-platform AnimePahe assistant / downloader helper
- package name: `autopahe`
- version: `3.6.1`

Stack
- Python >= 3.10
- Typer + Click + Rich + Colorama
- requests + BeautifulSoup + Playwright
- setuptools/pyproject packaging
- Docker support present

Repo shape
- not a single script anymore
- root executable modules plus internal packages:
  - `ap_core/`
  - `features/`
  - `collection/`
- has docs, tests, Docker, release notes, config handling, local-state handling

Key paths
- `Frame lab/fixtures/autopahe/project/pyproject.toml`
- `Frame lab/fixtures/autopahe/project/README.md`
- `Frame lab/fixtures/autopahe/project/auto_pahe.py`
- `Frame lab/fixtures/autopahe/project/cli.py`
- `Frame lab/fixtures/autopahe/project/ap_core/`
- `Frame lab/fixtures/autopahe/project/tests/`

Key structural rules / constraints
- setup is important because Playwright browser install is part of real operation
- downloads are browser-assisted and locally verified, not magically auto-faked
- config is OS-specific and stored in platform config dirs
- fixture has adapted imports like `example_projects.autopahe...`, which is a real structural quirk worth capturing

Run / test surface
- install/setup path uses `uv`
- source run path includes:
  - `uv sync`
  - `uv run playwright install chromium`
  - `uv run autopahe --help`
- pytest-style tests exist
- Docker build/run path also exists

Why it matters for FRAME fitting
- strong CLI/tooling pressure without being a toy
- combines package structure, browser automation, local state, config, Docker, docs, and tests
- good for checking whether FRAME can represent “how this project is built and operated” without collapsing into feature soup

---

## 3) pharmax

Identity
- Pharmacy operations platform
- backend package name: `pharmax`
- backend version: `0.1.0`

Stack
- Backend: Python 3.12+, FastAPI, SQLAlchemy, Alembic, Pydantic, uv
- Frontend: Vue 3, Pinia, Vue Router, Vite, Vuestic UI, ECharts
- local SQLite default, env-driven production DB path

Repo shape
- clear full-stack split:
  - `Backend/`
  - `Frontend/`
  - docs/planning/progress files
  - scripts and tests
- realistic app repo with project docs and implementation docs living together

Key paths
- `Frame lab/fixtures/pharmax/project/README.md`
- `Frame lab/fixtures/pharmax/project/Backend/README.md`
- `Frame lab/fixtures/pharmax/project/Backend/pyproject.toml`
- `Frame lab/fixtures/pharmax/project/Backend/app/`
- `Frame lab/fixtures/pharmax/project/Frontend/package.json`
- `Frame lab/fixtures/pharmax/project/Frontend/src/`
- `Frame lab/fixtures/pharmax/project/PROJECT_BRIEF.md`
- `Frame lab/fixtures/pharmax/project/PROGRESS.md`

Key structural rules / constraints
- strong backend/frontend separation
- env and deployment assumptions matter a lot
- docs + progress notes + code all contribute to project reality
- has realistic repo noise: checked-in frontend dependencies and at least one README-to-filesystem mismatch around `render.yaml`
- good example of a repo where architecture/order matters because many surfaces can drift

Run / test surface
- Backend:
  - `uv sync`
  - `cp .env.example .env`
  - `uv run fastapi dev main.py`
  - migrations/scripts/tests under Backend
- Frontend:
  - `npm install`
  - `npm run dev`
  - `npm run build`

Why it matters for FRAME fitting
- this is the strongest local “ai-assisted app can sprawl” fixture
- perfect for evaluating whether FRAME captures structure, surfaces, and project decisions without trying to encode every business behavior

---

## 4) httpie/cli

Identity
- Human-friendly HTTP client CLI
- package/app: `httpie`
- version found in fixture: `3.2.4`

Stack
- Python >= 3.7
- requests ecosystem, rich, Pygments, multidict
- pytest test setup

Repo shape
- mature Python CLI package
- clear split across:
  - package code
  - tests
  - docs
  - extras/packaging
  - CI/release workflows
- plugin and session/config surfaces are first-class, not accidental

Key paths
- `Frame lab/fixtures/public/cli/cli/setup.cfg`
- `Frame lab/fixtures/public/cli/cli/httpie/__main__.py`
- `Frame lab/fixtures/public/cli/cli/httpie/core.py`
- `Frame lab/fixtures/public/cli/cli/httpie/cli/definition.py`
- `Frame lab/fixtures/public/cli/cli/httpie/plugins/`
- `Frame lab/fixtures/public/cli/cli/tests/`

Key structural rules / constraints
- packaging metadata matters
- test/doc expectations are explicit
- there is a real extension model via plugins
- release/distribution workflows are part of project reality

Run / test surface
- `make all`
- `make test`
- `make test-cover`
- `python3 -m httpie --version`

Why it matters for FRAME fitting
- good mature CLI contrast against autopahe
- pressures FRAME to represent command-centric repos with plugins, docs, packaging, and distribution surfaces cleanly

---

## 5) modelcontextprotocol/python-sdk

Identity
- Python SDK for MCP
- package name: `mcp`
- current mainline is a v2 rework; README split between stable v1 and in-progress v2 is part of repo reality

Stack
- Python >= 3.10
- anyio, httpx, pydantic v2, starlette, uvicorn, jsonschema
- uv for package management
- ruff, pyright, pytest, coverage

Repo shape
- very clear source tree:
  - `src/`
  - `tests/`
  - `examples/`
  - `docs/`
  - `scripts/`
- public API is deliberately controlled
- test tree mirrors source tree strongly

Key paths
- `Frame lab/fixtures/public/sdk/python-sdk/pyproject.toml`
- `Frame lab/fixtures/public/sdk/python-sdk/AGENTS.md`
- `Frame lab/fixtures/public/sdk/python-sdk/README.v2.md`
- `Frame lab/fixtures/public/sdk/python-sdk/src/mcp/__init__.py`
- `Frame lab/fixtures/public/sdk/python-sdk/tests/`

Key structural rules / constraints
- use `uv`, not `pip`
- use `uv run --frozen` to avoid lockfile churn
- strict typing and strict test/coverage rules are part of the project shape
- public API boundary is explicit, not implied

Run / test surface
- `uv run mcp`
- `uv run --frozen pytest`
- `./scripts/test`
- `uv run --frozen ruff format .`
- `uv run --frozen ruff check . --fix`
- `uv run --frozen pyright`

Why it matters for FRAME fitting
- very good “clean SDK/protocol repo” fixture
- helps test whether FRAME can represent architecture, contributor rules, and public API boundaries without needing bloated memory-style fields

---

## 6) terragrunt

Identity
- Terragrunt
- Go-based infra orchestration/tooling repo in the OpenTofu/Terraform ecosystem

Stack
- Go
- OpenTofu / Terraform / HCL ecosystem
- mise-managed toolchain
- golangci-lint, bats, shellcheck, shfmt, jq, bun in tooling surface

Repo shape
- Go CLI repo with:
  - `internal/`
  - `pkg/`
  - `test/`
  - `docs/`
  - CI workflows
- huge integration-test and fixture surface under `test/fixtures/`
- nested helper CLI under `test/flake/`

Key paths
- `Frame lab/fixtures/public/infra-tooling/terragrunt/go.mod`
- `Frame lab/fixtures/public/infra-tooling/terragrunt/main.go`
- `Frame lab/fixtures/public/infra-tooling/terragrunt/internal/`
- `Frame lab/fixtures/public/infra-tooling/terragrunt/pkg/`
- `Frame lab/fixtures/public/infra-tooling/terragrunt/test/`
- `Frame lab/fixtures/public/infra-tooling/terragrunt/.github/workflows/`

Key structural rules / constraints
- CI/test matrix is part of the repo’s real shape
- infra fixtures are core, not just examples
- build and lint discipline are strict
- nested helper tooling adds subproject pressure without becoming a full monorepo

Run / test surface
- `mise install`
- `make build`
- `go test -v -coverprofile=coverage.out -covermode=atomic ./... -timeout 45m`
- integration tests use tag/setup matrices
- formatting/lint via make/pre-commit flows

Why it matters for FRAME fitting
- very good infra/tooling pressure repo
- tests whether FRAME can represent code + config-fixture forests + CI matrices + tooling discipline in one project description

---

## 7) twentyhq/twenty

Identity
- Twenty CRM
- large open-source CRM monorepo
- workspace version found in fixture: `0.2.1`

Stack
- TypeScript
- Yarn 4 + Nx
- Frontend: React, Jotai, Linaria, Lingui, Vite
- Backend: NestJS, TypeORM, GraphQL, PostgreSQL, Redis, BullMQ
- Docker/K8s/Helm/Podman surfaces present

Repo shape
- serious monorepo under `packages/`
- contains frontend, server, shared libs, UI, docs, website, SDKs, e2e, Docker, app-extension surfaces
- this is not just “frontend + backend”; it is a whole workspace ecosystem

Key paths
- `Frame lab/fixtures/public/web-app/twenty/package.json`
- `Frame lab/fixtures/public/web-app/twenty/nx.json`
- `Frame lab/fixtures/public/web-app/twenty/CLAUDE.md`
- `Frame lab/fixtures/public/web-app/twenty/packages/twenty-front/`
- `Frame lab/fixtures/public/web-app/twenty/packages/twenty-server/`
- `Frame lab/fixtures/public/web-app/twenty/packages/twenty-shared/`
- `Frame lab/fixtures/public/web-app/twenty/packages/twenty-docker/`

Key structural rules / constraints
- Node and Yarn versions are pinned
- npm is intentionally blocked
- coding conventions are explicit and strong
- database migration discipline is explicit
- Nx targets and workspace conventions are part of project reality

Run / test surface
- `yarn start`
- `npx nx start twenty-front`
- `npx nx start twenty-server`
- `npx nx run twenty-server:worker`
- `npx nx test twenty-front`
- `npx nx test twenty-server`
- `npx nx run twenty-server:test:integration:with-db-reset`

Why it matters for FRAME fitting
- high-pressure modern monorepo fixture
- ideal for checking whether FRAME preserves order across many packages, explicit conventions, app surfaces, infra surfaces, and extension surfaces without drowning in repetition

---

## What this extraction is already telling us

1. FRAME should mostly capture project representation, not feature encyclopedias.
- Across these seven, the recurring useful truths are:
  - what the project is
  - what stack it uses
  - how the repo is shaped
  - what the main surfaces are
  - what constraints/dev rules matter
  - how you run and verify it

2. Repo shape matters more than functionality detail.
- `organize` pressures tiny-script shape
- `autopahe` pressures medium CLI/package shape
- `pharmax` pressures split app shape
- `httpie` pressures mature CLI/plugin shape
- `python-sdk` pressures clean SDK shape
- `terragrunt` pressures infra/test-fixture shape
- `twenty` pressures large monorepo/workspace shape

3. The best FRAME pressure is around order and boundaries.
- surface separation
- key paths
- contributor/runtime constraints
- command/test entrypoints
- obvious repo decisions and structural quirks

4. We should avoid repetition aggressively.
- if the same truth can be captured once under project identity, stack, shape, or constraints, it should not keep leaking into multiple FRAME shelves unless the relationship itself matters.

---

## Good next move

Use this file as the pre-schema extraction layer.

Meaning:
- before fitting a project into FRAME,
- first extract this short metadata sheet,
- then fit FRAME against that grounded project representation,
- then compare what FRAME captures cleanly vs what still feels forced.
