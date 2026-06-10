# Red Room Test  --  FRAME Mechanical Validator

Tests whether the FRAME mechanical validator actually catches real agent errors
in a realistic agent-coding scenario. Pattern: CV governance experiment applied to code.

## Setup

```
red_room_test/
├── pharmax_frame/       ← Ground-truth FRAME (we created this)
│   ├── facts.yaml       ← What the project IS
│   ├── rules.yaml       ← Commands + constraints
│   ├── map.yaml         ← Where things live
│   ├── expect.yaml      ← What must pass (checks with command_ref)
│   └── acts.yaml        ← Run history (starts empty)
│
├── pharmax_clean/        ← Clean copy of Pharmax (agent workspace)
│   └── (no .haxaml/  --  the agent cannot see our truth)
│
└── test_harness.py       ← Runs verification
```

## How it works

1. We deeply traversed Pharmax and created the ground-truth FRAME in `pharmax_frame/`.
   This is the source of truth  --  it captures what the project actually is.

2. `pharmax_clean/` is a copy of Pharmax WITHOUT FRAME files.
   The agent can only see this directory. It cannot see `pharmax_frame/`.

3. An agent is told: "Add feature X to pharmax_clean/".
   The agent works, generates code, makes changes.

4. We run the test harness against `pharmax_clean/`:
   - It copies the ground-truth FRAME files into `.haxaml/`
   - It runs basic deterministic checks (grep for banned patterns, verify file existence)
   - It runs the mechanical validator (reads expect checks, executes commands, returns pass/fail)

5. If the validator catches agent errors → test proves the system works.
   If the validator misses errors → we improve expect.yaml and retry.
   If the validator gives false positives → we fix the checks.

## Usage

```bash
# Validate ground-truth FRAME files parse correctly
python3 test_harness.py validate-ground-truth

# Reset project to clean state and install ground-truth FRAME
python3 test_harness.py reset

# Run only basic deterministic checks (no agent work yet)
python3 test_harness.py checks

# Run full validation (basic checks + mechanical validator)
python3 test_harness.py full
```

## Agent loop (future)

The loop will be:

```
for each feature to add:
    1. Reset project to clean state
    2. Tell agent: "Add feature X to pharmax_clean/"
       (Agent can ONLY see pharmax_clean/ directory)
    3. After agent finishes:
       a. Run test_harness.py full
       b. Record which checks passed/failed
       c. If failures found but agent shouldn't have caused them → fix validator
       d. If validator missed an agent error → improve expect.yaml
    4. Repeat with next feature
```

## What we're testing

- Does the validator catch agents touching managed paths?
- Does the validator catch agents introducing banned patterns?
- Does the validator catch agents breaking invariants?
- Does the validator produce false positives on valid changes?
- What checks are missing from expect.yaml?
