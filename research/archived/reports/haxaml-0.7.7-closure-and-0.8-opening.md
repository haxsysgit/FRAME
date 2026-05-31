# Haxaml `0.7.7` Closure And `0.8` Opening

Date: 2026-05-20

This report answers three simple questions:

1. what `0.7.7` actually closed
2. how `0.7.7` prepared Haxaml for the `0.8` series
3. what `0.8` is really about in plain terms

`0.7.7` was not meant to be another feature-heavy patch. Its job was to close the `0.7.x` line cleanly, make the handoff explicit, and remove one last release footgun before the project moves into deeper FRAME and protocol work.

## What `0.7.7` Closed

### 1. It closed the `0.7.x` line as a finished story

Before `0.7.7`, the work was real, but it still read like separate patches:

- setup foundation
- workflow accommodation
- setup trust fixes
- state and archive fixes
- lifecycle gate fixes
- release pipeline fixes

`0.7.7` tied those into one line with a final close-out report and a clearer roadmap handoff. The point was to stop treating `0.7.x` like an endless cleanup branch.

Closed outcome:

- `0.7.x` is now documented as the setup, workflow, and trust line
- the line has a proper ending instead of an implied ending
- the handoff into `0.8.0` is explicit

### 2. It closed the release-publish footgun from `0.7.6`

The last practical issue exposed by `0.7.6` was release publishing. A tag-triggered GitHub publish could fail when the same version was already on PyPI.

`0.7.7` fixed that by teaching the publish workflow to:

- check PyPI first
- detect whether the exact package version already exists
- skip duplicate uploads instead of failing halfway through

Closed outcome:

- re-tag or already-published release cases are no longer brittle
- local publish and tag-triggered publish now coexist more safely

### 3. It closed the version-alignment loop for the whole package set

By the end of `0.7.7`, the release path was validated across:

- `haxaml`
- `haxaml-mcp`
- `haxaml-ui`
- changelog
- release tag
- GitHub workflows

Closed outcome:

- the three packages move together cleanly
- release metadata and publish logic are aligned

## What Was Already Closed By The Time `0.7.7` Landed

`0.7.7` itself did not invent these capabilities. It closed the line after these earlier fixes were already in place:

### Setup and onboarding

- `haxaml setup` became the real onboarding path
- provider-specific setup stopped being silently shadowed by `generic`
- reruns became much safer
- the setup wizard became a scaffold-style terminal flow instead of a raw prompt chain

### Workflow accommodation

- workflow assets became first-class setup outputs
- provider-specific workflow files were added where the public integration surface was real
- workflow checking stayed CLI-safe and machine-friendly

### State and archive discipline

- hot `acts.yaml` stopped acting like a replay dump
- compaction became byte-budget aware
- completed task growth became bounded
- archive reads became shallower and more selective

### Governed lifecycle quality

- structured blocking questions became real gates
- structured blocking materials became real gates
- handoff summaries started surfacing blockers, decisions, failure context, and pressure context more directly

## How `0.7.7` Prepared Haxaml For `0.8`

The main preparation work was not adding more surface area. It was reducing ambiguity.

### 1. It made the boundary clear

After `0.7.7`, the project has a cleaner division:

- `0.7.x` solved trust in setup, workflow entry, state usability, and release mechanics
- `0.8.x` can focus on FRAME and governance semantics instead of circling back to those trust problems

That matters because `0.8` needs to change deeper contracts. You do not want to do that while still arguing about whether setup can be trusted or whether hot Acts is still bloated.

### 2. It made the unresolved work explicit instead of fuzzy

The close-out work names the things that are still open:

- legacy archive compatibility debt
- advisory `setup doctor`
- manual provider follow-up in some integrations
- broad `--force` behavior
- partial compatibility rules for plain-string materials/questions
- incomplete verification-against-blueprint enforcement

That gives `0.8` a clean backlog of protocol problems instead of a vague feeling that “some things still need hardening.”

### 3. It made `expect.yaml` the next clear frontier

By the time `0.7.7` closed, the big next question was no longer setup. It was:

how should the project-level plan actually live inside FRAME?

That is why `0.8` opens with `expect.yaml` maturation and FRAME role clarification instead of more setup polish.

## What `0.8` Focuses On In Plain Terms

In plain language, `0.8` is where Haxaml stops mostly improving the wrapper around agent work and starts improving the protocol that defines the work itself.

### The simple version

`0.7.x` was about making Haxaml usable.

`0.8.x` is about making Haxaml more governable, more explicit, and harder to bypass.

### Concretely, that means:

- turning `expect.yaml` into the high-level run guide for the whole project goal
- making FRAME roles clearer so Facts, Rules, Acts, Expect, and Map stop overlapping in fuzzy ways
- giving prebuild and context-pack stronger gate semantics
- making missing user answers and missing materials harder to ignore
- making verification prove work against the planned path, not just claim that work happened
- adding migration-safe protocol improvements so older projects can keep moving forward

## What `0.8` Is Not About

`0.8` is not supposed to be:

- another setup cosmetics cycle
- a memory-product pivot
- a random feature dump
- a retrieval-first release

The point of `0.8` is governance maturity.

If `0.7.x` asked, "can agents enter the repo correctly?" then `0.8` asks, "once they enter, are the project rules, expected runs, required inputs, and evidence checks strong enough to reliably steer the work?"

## Short Summary

`0.7.7` closed the line by doing three things:

- it wrapped the `0.7.x` work into one finished story
- it fixed the last release-publish footgun
- it made the `0.8` starting point explicit

`0.8` now opens with a much clearer mission:

- mature FRAME
- make `expect.yaml` the real high-level run guide
- strengthen gates and verification
- reduce ambiguity in how governed work is planned, executed, and proven
