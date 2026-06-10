#!/usr/bin/env bash
set -euo pipefail

# Backward-compatible wrapper.
# Preferred smoke check now lives in:
#   scripts/smoke_test_workflows.py

cd "$(dirname "$0")/.."
uv run python scripts/smoke_test_workflows.py "$@"
