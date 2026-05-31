# Project Families For FRAME

FRAME should not be shaped around one repo, one language, or one agent.

That is even more important after the reset.
If FRAME only fits one implementation style, then it is not a real standard candidate yet.

## Why project families matter

The same architecture has to be tested against very different project shapes:
- CLIs
- APIs
- web apps
- monorepos
- SDKs
- infra tools
- mixed legacy repos
- startup codebases moving fast
- enterprise codebases with stricter constraints

If FRAME only works nicely for one narrow shape, that is a warning sign.

## What probably stays stable across project families

Different repos use different stacks, but recurring context needs are still similar:

| Shared need | Candidate FRAME area |
| --- | --- |
| What is this project? | facts-like reality |
| What kind of project is it? | classification-like reality |
| What stack is confirmed? | technology reality |
| What runtime context matters? | environment reality |
| What persistence resources are easy to miss? | persistence reality |
| What must agents obey? | rules-like reality |
| Where should they look? | map-like reality |
| What happened recently? | acts-like reality |
| What counts as correct? | expect-like reality |

The exact field names may change.
The underlying needs probably will not.

## What this means for the reset

The reset should preserve the cross-project ambition while reopening the details.

So:
- do not assume the old schema is right just because it existed
- do not throw away the five-part intuition too quickly either
- test candidate structure against many repo families before freezing it

## Tool-facing metadata still matters

FRAME should remain useful to tools, not just humans.
That means future iterations will probably still need structured metadata for things like:
- project classification
- evidence/trustworthiness
- ambiguity/unknowns
- verification expectations

But those should be justified by real usage and tests, not included only because they sound smart.

## Bottom line

Project-family fit is one of the main ways FRAME earns legitimacy.
If it cannot generalize across messy real repos, it is not ready.
