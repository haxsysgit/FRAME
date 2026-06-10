# The Multi Agent Loop

The lab does not rely on one agent’s opinion anymore.

## Current loop

The active round uses:
- 3 fitting/scoring agents
- 1 investigator
- 1 adjuster/synthesizer

## What each role does

### Fitter/scorer
Each fitter:
- inspects the candidate
- inspects one real fixture repo
- writes the fit files
- writes a scorecard
- writes a fit report

### Investigator
The investigator checks whether the fitters described the repo honestly.
This matters because a fit can look tidy and still overclaim.

### Adjuster/synthesizer
The adjuster reviews the round, corrects optimistic scoring when needed, and decides what the line actually learned.

## Why this loop is better

It reduces three common problems:
- one-agent tunnel vision
- unchallenged optimistic scoring
- random schema changes based on vibes

## Rules for the loop

- do not add new structure just because one fixture feels awkward
- do not ignore repeated pressure across fixtures
- do not invent broad context buckets to make fitting easier
- do not let Acts become fake project truth
