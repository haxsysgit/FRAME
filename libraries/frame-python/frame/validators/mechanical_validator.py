#!/usr/bin/env python3
"""
FRAME Mechanical Validator — v0.1.0

Reads expect.yaml checks and rules.yaml commands, executes declared checks,
and returns a deterministic pass/fail verdict.

The LLM cannot influence the result. This is an external, mechanical gate.

Usage:
    python3 mechanical_validator.py <project_dir>
"""

import subprocess
import sys
from pathlib import Path


def load_yaml(path):
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f)
    except ImportError:
        return _parse_simple_yaml(path)


def _parse_simple_yaml(path):
    """Minimal YAML parser that handles the FRAME subset."""
    content = Path(path).read_text()
    result = {}
    stack = [(result, -1)]
    current_key = None

    for line in content.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        indent = len(line) - len(line.lstrip())
        while stack and indent <= stack[-1][1]:
            stack.pop()
        if ':' in stripped:
            key, _, value = stripped.partition(':')
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            parent = stack[-1][0] if stack else result
            if value:
                parent[key] = value
            else:
                parent[key] = {}
                stack.append((parent[key], indent))
        elif stripped.startswith('- '):
            item = stripped[2:].strip()
            parent = stack[-1][0] if stack else result
            if current_key:
                if current_key not in parent:
                    parent[current_key] = []
                parent[current_key].append(item)
    return result


def find_expect_checks(expect):
    """Extract checks from expect.yaml that have command_ref values."""
    checks = []
    expect_checks = expect.get('checks', {})
    for check_id, check_data in expect_checks.items():
        if isinstance(check_data, dict):
            command_ref = check_data.get('command_ref', '')
            if command_ref:
                checks.append({
                    'id': check_id,
                    'name': check_data.get('name', check_id),
                    'what': check_data.get('what', ''),
                    'command_ref': command_ref,
                    'how': check_data.get('how', 'command'),
                })
    return checks


def resolve_command(command_ref, rules):
    """Resolve a dotted command_ref to the command dict."""
    # command_ref format: rules.commands.<command_name>
    parts = command_ref.split('.')
    if len(parts) >= 3 and parts[0] == 'rules' and parts[1] == 'commands':
        cmd_name = parts[2]
        commands = rules.get('commands', {})
        return commands.get(cmd_name, None)
    return None


def run_check(check, command, project_dir):
    """Execute a check command and return pass/fail with details."""
    run_str = command.get('run', '')
    purpose = command.get('purpose', '')
    kind = command.get('kind', 'verify')

    # Skip server-start / interactive commands
    if kind in ('run', 'serve', 'dev'):
        print(f"\n  [{check['name']}]")
        print(f"    command:     {run_str}")
        print(f"    result:      SKIP (kind={kind} — server/interactive)")
        return {
            'check_id': check['id'],
            'name': check['name'],
            'passed': None,
            'exit_code': 0,
            'skipped': True,
        }

    print(f"\n  [{check['name']}]")
    print(f"    description: {check.get('what', check['name'])}")
    print(f"    command:     {run_str}")
    print(f"    purpose:     {purpose}")

    try:
        result = subprocess.run(
            run_str,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(project_dir),
        )
        passed = result.returncode == 0
        status = "PASS" if passed else "FAIL"
        print(f"    result:      {status} (exit {result.returncode})")

        return {
            'check_id': check['id'],
            'name': check['name'],
            'passed': passed,
            'exit_code': result.returncode,
            'stdout': result.stdout[:200] if result.stdout else '',
            'stderr': result.stderr[:200] if result.stderr else '',
        }
    except subprocess.TimeoutExpired:
        print(f"    result:      FAIL (timeout)")
        return {
            'check_id': check['id'],
            'name': check['name'],
            'passed': False,
            'exit_code': -1,
            'stderr': 'Command timed out after 60 seconds',
        }
    except Exception as e:
        print(f"    result:      FAIL (error: {e})")
        return {
            'check_id': check['id'],
            'name': check['name'],
            'passed': False,
            'exit_code': -1,
            'stderr': str(e),
        }


def find_frame_dir(project_dir):
    """Find .haxaml/ or project root with expect.yaml."""
    pd = Path(project_dir)
    haxaml = pd / '.haxaml'
    if (haxaml / 'expect.yaml').exists():
        return haxaml
    if (pd / 'expect.yaml').exists():
        return pd
    raise FileNotFoundError(f"No expect.yaml found in {project_dir}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 mechanical_validator.py <project_dir>")
        sys.exit(1)

    project_dir = Path(sys.argv[1]).resolve()
    frame_dir = find_frame_dir(project_dir)

    expect_path = frame_dir / 'expect.yaml'
    rules_path = frame_dir / 'rules.yaml'

    expect = load_yaml(expect_path)
    rules = load_yaml(rules_path)

    checks = find_expect_checks(expect)

    if not checks:
        print("No checks with command_ref found in expect.yaml.")
        sys.exit(0)

    print(f"FRAME Validator — {len(checks)} check(s)\n")

    results = []
    for check in checks:
        command = resolve_command(check['command_ref'], rules)
        if not command:
            print(f"  [{check['name']}] command_ref not found: {check['command_ref']}")
            results.append({'check_id': check['id'], 'name': check['name'], 'passed': False, 'stderr': 'command_ref not found'})
            continue
        results.append(run_check(check, command, project_dir))

    total = len(results)
    passed = sum(1 for r in results if r.get('passed') is True)
    failed = sum(1 for r in results if r.get('passed') is False)
    skipped = total - passed - failed

    print(f"\n{'='*60}")
    print(f"RESULTS: {passed}/{total} passed, {failed} failed, {skipped} skipped")

    if failed > 0:
        print(f"\nFAILED:")
        for r in results:
            if r.get('passed') is False:
                print(f"  {r['name']}")
                if r.get('stderr'):
                    print(f"    {r['stderr'][:120]}")
        sys.exit(1)
    else:
        print("ALL VERIFIABLE CHECKS PASSED")
        sys.exit(0)


if __name__ == '__main__':
    main()
