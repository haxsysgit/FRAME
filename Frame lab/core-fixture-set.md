# Core Fixture Set

This document defines the compact working fixture set for early multi-agent FRAME fitting and scoring.

It is a correction to the earlier instinct of keeping too many heavyweight repos in the active loop.

## Goal of the core set

The core set is not meant to represent the entire software universe.
It is meant to give FRAME enough real structural pressure to evaluate candidate schemas quickly and repeatedly.

So the active set should optimize for:
- real projects
- clear project identity
- meaningful structural variety
- medium or smaller inspection cost
- good signal for fit/scoring comparisons

## Audit of the current 12 real repos

### Strong active-core candidates

1. `httpie/cli`
- Family: CLI tool
- Approx size: 4.4M
- Why it is strong: very clear project identity, classic CLI structure, docs/tests/package layout, low inspection cost
- Verdict: keep in active core

2. `yt-dlp/yt-dlp`
- Family: CLI tool
- Approx size: 19M
- Why it is strong: still affordable, much more operationally complex than `httpie`, stresses options/edge-cases/extractor-style logic
- Verdict: keep in active core

3. `OpenHands/OpenHands`
- Family: AI-native system
- Approx size: 29M
- Why it is strong: highly relevant to agent-facing context architecture, multi-surface but still inspectable, rich operational/documentation structure
- Verdict: keep in active core

4. `Kong/insomnia`
- Family: API/devtool product
- Approx size: 35M
- Why it is strong: real product, clear devtool identity, package-based layout, cross-surface behavior without absurd weight
- Verdict: keep in active core

5. `hoppscotch/hoppscotch`
- Family: API/devtool ecosystem
- Approx size: 38M
- Why it is strong: complementary to Insomnia, web/API ecosystem pressure, modern product structure
- Verdict: keep in active core

6. `immich-app/immich`
- Family: web platform / product app
- Approx size: 172M
- Why it is strong: real app complexity, multiple surfaces, enough structure to stress FRAME meaningfully without being the worst offender in size
- Verdict: keep in active core

7. `DevToys-app/DevToys`
- Family: desktop app / developer utility
- Approx size: 185M
- Why it is strong: gives desktop-app pressure that the other active fixtures do not provide, still more manageable than the heaviest candidates
- Verdict: keep in active core

### Useful but reserve-only for now

8. `appwrite/appwrite`
- Family: web platform / backend platform
- Approx size: 209M
- Why reserve: strong real platform repo, but overlaps enough with other active fixtures that it is better as reserve during early loops
- Verdict: reserve fixture

9. `apache/superset`
- Family: data platform
- Approx size: 437M
- Why reserve: valuable shape, but too heavy for the default rapid loop
- Verdict: reserve fixture

10. `organicmaps/organicmaps`
- Family: mobile app
- Approx size: 851M
- Why reserve: real and useful, but too expensive for the default active loop
- Verdict: reserve fixture

11. `airbytehq/airbyte`
- Family: data platform
- Approx size: 1.1G
- Why reserve: very real but much too heavy for early repeated fitting
- Verdict: reserve fixture

### Invalid as current fixture

12. `localstack/localstack`
- Family: infra platform
- Approx size on disk: ~364K
- Why invalid: working tree did not materialize; current clone is effectively just Git metadata
- Verdict: invalid fixture, replace later with a lighter real infra/platform repo

## Active core 7

These are the seven fixtures to use by default for the actual fit/scoring loop:

1. `httpie/cli`
2. `yt-dlp/yt-dlp`
3. `OpenHands/OpenHands`
4. `Kong/insomnia`
5. `hoppscotch/hoppscotch`
6. `immich-app/immich`
7. `DevToys-app/DevToys`

## Why this is the best current compact set

This set gives:
- small and medium repos, not giant ones by default
- both straightforward and messy-real structures
- multiple interaction surfaces: CLI, API/devtool, web product, desktop app, AI-native system
- enough variation for schema pressure without making every iteration painfully slow

It is not perfectly balanced across every software family.
It is the best current tradeoff from the 12 real repos already cloned.

## Reserve fixtures

Reserve fixtures should be used when:
- a scoring pass reveals a blind spot in FRAME
- a candidate schema works on the core 7 but may fail on heavier systems
- we want a second-stage stress pass after narrowing the architecture

Current reserve fixtures:
- `appwrite/appwrite`
- `apache/superset`
- `organicmaps/organicmaps`
- `airbytehq/airbyte`

## Gap to fix later

The current compact set still underrepresents:
- a good lightweight infra/platform repo
- a good lightweight legacy/mixed-shape repo
- a good lightweight mobile app repo

That does not block early fitting.
It just means future fixture replacement should target those gaps with lighter real repos rather than heavier famous ones.

## Working rule for subagents

Default to the core 7 first.
Only pull in reserve fixtures when the evaluation question actually needs heavier pressure.

That keeps the loop fast, comparable, and honest.
