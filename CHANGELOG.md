# Changelog

All notable changes to the active FRAME line should be tracked here.

## FRAME 0.2.0

This is the current active candidate line.

### What 0.2.0 holds

The 0.2.0 line is centered on:
- the five-part linked architecture: Facts, Rules, Map, Expect, Acts
- simpler entry and block names
- stronger typed cross-linking across the 5 parts
- cleaner ownership of truth
- a retrieval-friendly view of Acts
- clearer separation between referenced checks and executed checks
- stronger design pressure from future typed tooling like Haxaml and `frame-py`
- lower tolerance for schema bloat

### Main changes from 0.1.0

#### 1. Simpler names

Examples:
- `project_profile` -> `profile`
- `source_truth` -> `sources`
- `structural_quirks` -> `quirks`
- `critical_rules` -> `rules`
- `negative_instructions` -> `donts`
- `stop_and_ask` -> `ask_first`
- `classifications` -> `groups`
- `access_points` -> `entrypoints`
- `invariants` -> `must_hold`
- `required_evidence` -> `proof`
- `representation_scope` -> `scope`

Why it changed:
- the older names were more abstract and harder to scan
- the new names are easier for developers and future tools to use quickly

#### 2. Stronger linked-system thinking

0.1.0 still had too much “five files sitting beside each other” energy.

0.2.0 pushes a stronger typed link pattern:
- each meaningful thing should have a stable id when needed
- one place owns a truth
- other parts should reference that truth instead of duplicating it

#### 3. Acts changed role

0.1.0 still carried more confusion around Acts as baseline representation or generic provenance.

0.2.0 makes Acts much clearer:
- Acts is run history
- Acts is there to help retrieval, review, and handoff
- Acts should show touched surfaces, changed facts, rules followed, and check status
- Acts should not act like a second Facts file

#### 4. Better tool-facing retrieval fields

0.2.0 added or clarified Acts run fields like:
- `work_kind`
- `keywords`
- `checks_seen`
- `checks_ran`

Why it matters:
- future tools can retrieve similar past runs more reliably
- agents can see what kind of work happened before
- proof stays more honest

#### 5. Better proof honesty

0.1.0 left more room for blurring “this check exists” with “this check was actually run.”

0.2.0 draws a cleaner line:
- `checks_seen` means known or linked checks
- `checks_ran` means checks actually executed in that run

#### 6. Lower bloat tolerance

0.2.0 is more aggressive about rejecting fields that do not improve:
- fit
- retrieval
- checks
- tool behavior
- portability

### Why 0.2.0 is stronger

The short version is simple:
0.2.0 is better because it got simpler, more linked, and more honest.

It treats FRAME more like one typed system and less like a pile of schema buckets.

### Evidence behind the line

The active 0.2.0 line was pressure-tested through:
- the current three-fixture loop
- three fitter/scorer agents
- one investigator pass
- one synthesis/adjuster pass

Current aggregate result from the active round:
- organize: 4.25 / 5
- autopahe: 4.35 / 5
- pharmax: 4.49 / 5
- weighted average: 4.36 / 5

### Status

0.2.0 is the current active line.
It is strong, but still pre-final.
The next work is refinement and further fixture pressure, not schema sprawl.

## Historical note on 0.1.0

0.1.0 still matters as lab history.
It showed that the five-part idea was viable, but it also exposed:
- naming friction
- duplication pressure
- weaker cross-link discipline
- Acts ambiguity
- proof ambiguity

That pressure is what helped produce 0.2.0.
