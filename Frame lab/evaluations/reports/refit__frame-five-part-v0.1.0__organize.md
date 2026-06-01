# Refit report: frame-five-part-v0.1.0 on organize

Date: 2026-06-01
Fixture: `/home/hax/FRAME/Frame lab/fixtures/organize/project`
Output fit: `/home/hax/FRAME/Frame lab/evaluations/fits/frame-five-part-v0.1.0/organize`
Schema version: `0.1.0`

## Work performed

Refit the adjusted five-file FRAME schema against the `organize` fixture and wrote:

- `facts.yaml`
- `rules.yaml`
- `acts.yaml`
- `map.yaml`
- `expect.yaml`

The fit was grounded by direct inspection of:

- `schemas/facts.schema.yaml`
- `schemas/rules.schema.yaml`
- `schemas/acts.schema.yaml`
- `schemas/map.schema.yaml`
- `schemas/expect.schema.yaml`
- `schemas/frame.schema.yaml`
- `Frame lab/fixtures/organize/project/organize.py`
- `Frame lab/fixtures/organize/project/README.md`
- `Frame lab/fixtures/organize/project/LICENSE`

I also ran `python3 organize.py --help` in the fixture repo.

## Fixture reality

`organize` is a tiny Python 3 CLI utility for local file organization. The repo is essentially:

- `organize.py`: the implementation and real CLI entrypoint
- `README.md`: supporting docs and flag descriptions
- `LICENSE`: MIT license

The script uses only the Python standard library. Its core behavior is filesystem mutation: creating extension/name folders, moving files into them, and deleting generated extension folders while moving files back.

## Live check result

`python3 organize.py --help` exited with code 0 and printed the argparse surface for:

- `-m / --file-match`
- `-p / --path`
- `-c / --create_ext_dir`
- `-obr / --organize_by_relation`
- `-obe / --organize_by_extension`
- `-d / --delete_ext_dir`
- `-de / --delete_ext_dirtype`
- `-ce / --create_ext_dirtype`

It also emitted:

`SyntaxWarning: invalid escape sequence '\/'` at `organize.py:239`.

## Adjusted schema fit notes

- `facts.project_profile` worked well for compactly identifying this as a tiny CLI tool and preventing over-modeling.
- `facts.structural_quirks` cleanly captured README/code drift, hardcoded Linux path assumptions, import-time argparse behavior, and the help warning.
- `facts.source_truth` provided a good place to rank `organize.py` above stale README command examples.
- `rules.commands` now acts as a command inventory only. Verification meaning was moved to `expect.verify` through `command_ref` links.
- `expect.verify` links back to command refs and avoids repeating full command prose except where no command exists.
- `acts` was kept deliberately small and only records checked activity/handoff, not stable project representation.
- `map` was kept compact and omits `.git` internals.

## Friction found

1. `acts` remains the least natural file for this fixture. Once it is forbidden from carrying baseline representation, it only honestly records the fit/check events and handoff notes.
2. The repo is so small that repetition pressure is high. The adjusted schema helps, but the fit still requires discipline to avoid restating the same one-script truths in facts, map, rules, and expect.
3. Mutating commands cannot be safely verified against the fixture root. Proper behavior checks need a disposable temp directory and before/after tree evidence.
4. README usage examples are stale (`file_manager.py`) compared with the actual entrypoint (`organize.py`), so code must be treated as canonical for command spelling.

## Bottom line

The adjusted FRAME five-file schema fits `organize` better than the earlier pass because compact profile, structural quirks, source truth ranking, command inventory, and command-ref verification all reduce duplication. The fit still shows that tiny repos need aggressive compression, and that `acts` should stay out of baseline project representation.
