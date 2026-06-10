# Fixtures And Example Projects

Fixtures are the real repos we use to test FRAME.

## Tiny idea

If you only test a context standard on one project, the project starts teaching you bad habits.

That is why fixtures matter.

## Current core fixtures

The active 0.2.0 round uses:
- `organize`
- `autopahe`
- `pharmax`

## Why these three help

### organize
A small script/tool repo.
Good for checking whether FRAME can stay lightweight.

### autopahe
A CLI/tooling-style repo.
Good for checking commands, setup caveats, config safety, and package structure.

### pharmax
A fuller app/workflow repo.
Good for checking frontend/backend boundaries, richer correctness expectations, and workflow pressure.

## What fixtures are testing

Not just “can we fill five files?”

They are testing whether:
- Facts holds stable truth well
- Rules changes behavior in useful ways
- Map reduces blind repo wandering
- Expect makes correctness clearer
- Acts helps retrieval and handoff without turning into baseline project truth
