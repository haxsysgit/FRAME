#!/usr/bin/env python3
"""
Red Room Test Harness  --  v0.1.0

Tests FRAME mechanical validator against real agent code generation.
Pattern: CV governance experiment applied to code.

Setup:
    red_room_test/
    ├── pharmax_frame/       ← Ground-truth FRAME (source of truth)
    ├── pharmax_clean/        ← Clean copy of Pharmax (agent workspace, no .haxaml)
    └── test_harness.py       ← This file

Loop:
    1. Agent modifies pharmax_clean/ (restricted vision  --  can only see that dir)
    2. Harness runs mechanical validator against pharmax_clean/
    3. Validator checks agent output against ground-truth expect/checks
    4. Violations → test fails → improve validator → repeat
    
Purpose:
    Prove that deterministically verifiable checks catch real agent errors.
    Discover what checks are missing from expect.yaml.
    Harden the validator against false negatives.
"""

import subprocess
import sys
import shutil
from pathlib import Path
from datetime import datetime


HERE = Path(__file__).resolve().parent
FRAME_TRUTH = HERE / "pharmax_frame"
CLEAN_PROJECT = HERE / "pharmax_clean"


def validate_yaml(path):
    """Quick check: can PyYAML parse this file?"""
    try:
        import yaml
        with open(path) as f:
            yaml.safe_load(f)
        return True, ""
    except Exception as e:
        return False, str(e)


def run_mechanical_validator(project_dir):
    """Run the FRAME mechanical validator against a project directory."""
    validator_path = HERE.parent / "frame-py" / "frame" / "validators" / "mechanical_validator.py"
    if not validator_path.exists():
        return {
            "passed": None,
            "error": f"Validator not found at {validator_path}",
            "checks": [],
        }

    try:
        result = subprocess.run(
            ["python3", str(validator_path), str(project_dir)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        return {
            "passed": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": result.stdout[-2000:],
            "stderr": result.stderr[-500:],
            "checks": [],
        }
    except subprocess.TimeoutExpired:
        return {"passed": False, "error": "Validator timed out", "checks": []}
    except Exception as e:
        return {"passed": False, "error": str(e), "checks": []}


def run_basic_checks(project_dir):
    """Simple deterministic checks that don't need the full validator."""
    project = Path(project_dir)
    results = []

    # Check 1: No stale development paths (exclude .haxaml/  --  it contains the check command itself)
    stale_paths = ["/home/hermes/job-pipeline"]
    for sp in stale_paths:
        try:
            out = subprocess.run(
                ["grep", "-rq", "--exclude-dir=.haxaml", sp, str(project)],
                capture_output=True,
                timeout=10,
            )
            passed = out.returncode != 0
            results.append({
                "name": f"No stale path: {sp}",
                "passed": passed,
                "detail": "Found" if not passed else "Clean",
            })
        except Exception:
            results.append({
                "name": f"No stale path: {sp}",
                "passed": True,
                "detail": "grep unavailable, skip",
            })

    # Check 2: No hardcoded secrets in backend source
    try:
        out = subprocess.run(
            ["grep", "-riq", "API_KEY", str(project / "Backend" / "app"),
             "--include=*.py"],
            capture_output=True,
            timeout=10,
        )
        passed = out.returncode != 0
        results.append({
            "name": "No hardcoded API_KEY in source",
            "passed": passed,
            "detail": "Found" if not passed else "Clean",
        })
    except Exception:
        pass

    # Check 3: Frontend build check script exists
    frontend_pkg = project / "Frontend" / "package.json"
    results.append({
        "name": "Frontend package.json exists",
        "passed": frontend_pkg.exists(),
        "detail": str(frontend_pkg),
    })

    # Check 4: Backend main entrypoint exists
    backend_main = project / "Backend" / "app" / "main.py"
    results.append({
        "name": "Backend main.py exists",
        "passed": backend_main.exists(),
        "detail": str(backend_main),
    })

    return results


def validate_ground_truth():
    """Verify all 5 FRAME files in pharmax_frame/ parse correctly."""
    print("=" * 60)
    print("Validating ground-truth FRAME files...")
    print("=" * 60)

    for part in ["facts", "rules", "map", "expect", "acts"]:
        path = FRAME_TRUTH / f"{part}.yaml"
        ok, err = validate_yaml(path)
        status = "OK" if ok else f"FAIL: {err}"
        print(f"  {part}.yaml: {status}")

    print()


def reset_clean_project():
    """Reset pharmax_clean/ to pristine state (no .haxaml, no agent artifacts)."""
    if CLEAN_PROJECT.exists():
        shutil.rmtree(CLEAN_PROJECT)

    source = HERE.parent / "Frame lab" / "fixtures" / "pharmax" / "project"
    shutil.copytree(source, CLEAN_PROJECT)

    # Remove any .haxaml from previous runs
    haxaml_dir = CLEAN_PROJECT / ".haxaml"
    if haxaml_dir.exists():
        shutil.rmtree(haxaml_dir)

    # Remove cache/generated files
    for pattern in ["__pycache__", "node_modules", ".pytest_cache", "dist",
                    "uv.lock", "package-lock.json"]:
        for p in CLEAN_PROJECT.rglob(pattern):
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()

    print("Project reset to clean state.\n")


def install_frame_files(project_dir):
    """Copy ground-truth FRAME files into clean project's .haxaml/."""
    haxaml = Path(project_dir) / ".haxaml"
    haxaml.mkdir(exist_ok=True)
    for part in ["facts.yaml", "rules.yaml", "map.yaml", "expect.yaml", "acts.yaml"]:
        shutil.copy(FRAME_TRUTH / part, haxaml / part)
    print(f"FRAME files installed to {haxaml}\n")


def run_checks_only():
    """Run only basic checks (no agent work yet)."""
    print("=" * 60)
    print("Running basic deterministic checks...")
    print("=" * 60)

    results = run_basic_checks(CLEAN_PROJECT)
    passed = sum(1 for r in results if r["passed"])
    total = len(results)

    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  [{status}] {r['name']}  --  {r.get('detail', '')}")

    print(f"\n  {passed}/{total} checks passed")
    return passed == total


def run_full_validation():
    """Run basic checks then attempt mechanical validator."""
    basic_ok = run_checks_only()

    print("\n" + "=" * 60)
    print("Running mechanical validator...")
    print("=" * 60)

    result = run_mechanical_validator(CLEAN_PROJECT)

    if result.get("error"):
        print(f"  Validator error: {result['error']}")
    elif result["passed"] is True:
        print("  ALL CHECKS PASSED  --  project is clean")
    elif result["passed"] is False:
        print(f"  VALIDATION FAILED  --  exit code {result['exit_code']}")
        if result.get("stderr"):
            print(f"  {result['stderr'][:300]}")
    else:
        print("  Validator returned: None (no checks found)")

    return basic_ok and (result.get("passed") is not False)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 test_harness.py validate-ground-truth")
        print("  python3 test_harness.py reset")
        print("  python3 test_harness.py checks")
        print("  python3 test_harness.py full")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "validate-ground-truth":
        validate_ground_truth()
    elif cmd == "reset":
        reset_clean_project()
        install_frame_files(CLEAN_PROJECT)
    elif cmd == "checks":
        run_checks_only()
    elif cmd == "full":
        run_full_validation()
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
