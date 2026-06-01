# organize fit report

Candidate under test: current five-part FRAME schema in `schemas/`
Fixture: `Frame lab/fixtures/organize/project`
Date: 2026-06-01

## Repo reality used for the fit

Grounded anchors:
- `Frame lab/fixtures/organize/project/organize.py`
- `Frame lab/fixtures/organize/project/README.md`
- `Frame lab/fixtures/metadata/core-seven-project-cards.md:26-52`

What the repo actually is:
- tiny Python 3 CLI utility for organizing files/folders
- near-minimal repo: `organize.py`, `README.md`, `LICENSE`
- command-line flags are the whole interface
- core behavior is filesystem mutation: create folders, move files, undo extension folders
- README examples drift from code: docs say `file_manager.py`, repo script is `organize.py`
- Linux default path is hardcoded in source: `/home/haxsys/downloadscopy2/Downloads`
- live `python3 organize.py --help` succeeded, but emitted a `SyntaxWarning` at `organize.py:239`

## Where the schema fit cleanly

### facts
Clean fit for identity, stack, repo shape, and quirks.
This part held the compact repo card well without needing feature sprawl.

### rules
Clean fit for the real operating cautions:
- flags are the primary interface
- path safety matters because the tool mutates the filesystem
- doc/code drift should be treated as a live hazard, not ignored

### map
Clean enough as long as it stays tiny.
A small map still helps by making the actual source-of-truth paths explicit: `organize.py` and `README.md`.

### expect
Reasonable fit for the lightweight correctness surface.
This repo has no test suite, so `expect` can honestly point to CLI help and manual disposable-directory checks.

## Where the schema felt forced

### acts
This is the weakest part for `organize`.
There is no natural project activity log, workflow trail, or checked history surface in the repo.
The only honest content here was a minimal record of the live `--help` check plus a note that destructive flows need a safe sample directory.

## Main repetition risk

The repetition pressure showed up exactly where expected for a tiny repo:
- `facts.architecture` and `map.paths` both want to say that `organize.py` is the main surface
- `rules.commands.help` and `expect.verify.help_command` both want the same command
- the README/code drift hazard could appear in facts, rules, map, and expect if left unchecked

The fit stayed lean by giving each repeated truth only one main job:
- facts = stable repo truth and quirks
- rules = operating cautions and command usage
- map = navigation anchors
- expect = what counts as verification

## Main friction points

1. `acts` does not pull its weight on this fixture.
2. The schema has no dedicated compact slot for recurring structural drift hazards, so README/code mismatch gets threaded through prose fields.
3. Tiny repos need discipline or the five files start feeling like tax paperwork.

## Bottom line

The candidate can represent `organize`, but only if the fit stays aggressively compact.
That is a real win for scale-down coverage, but also a warning: on one-script repos, the cost of splitting truth across five files rises quickly, and `acts` looks more like framework overhead than project representation.
