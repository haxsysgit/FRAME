# frame-five-part-v0 on organize

Candidate: `frame-five-part-v0`
Fixture: `organize`
Phase focus: first real manual fit pass on the smallest fixture

## Short verdict

The five-part candidate can represent `organize`, but it already feels slightly overbuilt for a one-script repo.

So this is not a failure.
But it is a warning.

The good news:
- identity, stack, repo shape, command surface, and a few real quirks do have homes
- the project is simple enough to expose placement problems quickly

The warning:
- `acts` is basically not project representation here
- `facts`, `map`, and `expect` can start repeating each other on a tiny repo if we are not disciplined
- maintainability/value ratio drops fast when the repo barely has any scaffolding

## Grounded fixture reality

From repo inspection:
- project is a Python CLI script for file-management automation
- the repo is basically `organize.py` + `README.md` + `LICENSE`
- CLI arguments are the main interface
- the script mutates the filesystem
- README usage examples say `file_manager.py`, but the actual script is `organize.py`
- the script has a Linux-specific hardcoded default path
- no test suite was discovered
- `python3 organize.py --help` runs successfully, but emits a `SyntaxWarning` around an invalid escape sequence

Key anchors:
- `Frame lab/fixtures/organize/project/README.md`
- `Frame lab/fixtures/organize/project/organize.py`

## Candidate fit by part

### 1) facts
What fits well:
- identity: tiny file-organization CLI
- technology: Python 3, stdlib-only imports, argparse
- architecture: single-script repo with minimal scaffolding
- important quirk: Linux hardcoded path in code
- ambiguity/drift note: docs mention `file_manager.py` instead of `organize.py`

What feels risky:
- if we let `facts` become a junk drawer, tiny repos will dump everything there
- we need a hard rule that `facts` captures stable project truth, not every command or behavior detail

### 2) rules
What fits well:
- side-effectful filesystem tool, so path caution belongs here
- command-line usage expectations belong here
- negative instruction like “do not assume the README command names are correct without checking code” is realistic

What feels risky:
- for a repo this small, rules can become partly duplicate of facts and expect
- some truths are descriptive, not prescriptive, so we need clean rule/fact separation

### 3) acts
What fits:
- almost nothing from the repo itself
- acts may be useful for work history or verified activity logs during agent execution, but not for the project representation

Why this matters:
- this pass reinforces your point: project representation is not the same thing as memory or activity trail
- `acts` may still be useful in the wider FRAME system, but it does not help much with describing this repo

### 4) map
What fits well:
- root and important paths are very clear
- access points are obvious: `organize.py`, README usage section
- this part is helpful even on a tiny repo because it keeps navigation explicit

What feels risky:
- if map gets too detailed, it becomes silly for small repos
- tiny repos need a very lean map representation

### 5) expect
What fits well:
- successful CLI help run is a real verification anchor
- “done” and “verify” ideas can represent basic correctness checks for changes
- we can store the fact that no tests exist and manual CLI verification is the actual check surface

What feels risky:
- project-level correctness on a tiny script can blur into task-level expectations
- if we are not careful, expect becomes a generic QA notes bucket

## Friction found

### Forced fits
- trying to give `acts` meaningful project-representation content
- splitting tiny-repo truths across too many top-level files

### Missing semantics
- a very compact way to represent repo size/shape pressure directly
- a better home for “doc/code drift” as a recurring structural quirk

### Redundant-field risk
- `facts.architecture` vs `map.roots/paths` on a tiny repo
- `rules.commands` vs `expect.verify` when there is only one cheap verification path

### Stale-risk fields
- detailed command examples copied from README
- every specific flag meaning if the code can drift faster than the summary

## What organize is teaching us about FRAME

1. FRAME must scale down cleanly.
   - If the project is basically one script, the representation should not feel like tax paperwork.

2. Project representation and activity history are different jobs.
   - This fixture makes that painfully obvious in a good way.

3. Tiny repos still have real structure.
   - Identity, run surface, important paths, constraints, and quirks are still worth capturing.
   - We just need to do it without bloat.

4. Structural quirks matter.
   - Doc/code drift and hardcoded environment assumptions are exactly the kinds of truths that help future agents avoid dumb mistakes.

## Practical recommendation after this pass

Keep testing the five-part candidate for now, but treat this as a warning that:
- `acts` should not be allowed to contaminate project representation work
- tiny repos need an aggressively compact fit style
- repeated drift/quirk signals may deserve a clearer slot than generic prose notes

## Suggested next comparison

After `organize`, compare the same candidate against `autopahe`.

Why:
- it keeps the cost low
- it adds package structure, tests, config, browser setup, and Docker pressure
- it will show whether the same candidate grows naturally or starts leaking fields everywhere
