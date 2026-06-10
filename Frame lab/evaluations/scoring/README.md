# FRAME Lab Scoring

This folder holds the phased scoring setup for comparing candidate FRAME structures across real fixtures.

## Files

- `rubric.md` -- what each score dimension means, organized by phase
- `scorecard-template.toml` -- one evaluation file per fixture/candidate pair
- `README.md` -- quick usage

## Recommended file naming

Use one scorecard per candidate/fixture pair:

`<candidate>__<fixture>.toml`

Example:
- `frame-five-part-v0__httpie-cli.toml`
- `frame-five-part-v0__openhands.toml`

## Workflow

1. copy `scorecard-template.toml`
2. fill in fixture + candidate metadata
3. score Phase 1 first: structural fit
4. then score Phase 2: operational usefulness
5. then score Phase 3: pressure / cost
6. save the finished scorecard beside other scorecards
7. run `python3 scripts/frame_lab_aggregate.py "Frame lab/evaluations/scoring"`

## Important rule

Do not let strong later-phase scores hide weak structural fit.
If Phase 1 is weak, that should dominate the judgment.

## Status rule

Use `meta.status = "draft"` while a pass is in progress.
Switch to `meta.status = "complete"` when the scorecard is ready to count.

The aggregation script ignores draft scorecards by default.
