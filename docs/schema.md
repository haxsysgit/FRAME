# FRAME Schema Direction

This doc exists to make one thing clear:

The schema is not assumed to be correct just because a previous version existed.

## Current position

FRAME likely needs a schema eventually.
But the project should not let an old schema freeze the wrong architecture too early.

That means schema work now has to answer harder questions first:
- what parts of FRAME are truly stable concepts?
- what parts are just one implementation guess?
- what needs to be machine-validated?
- what should stay human-friendly and flexible?
- what belongs in the core contract vs tool-specific extensions?

## What the schema should eventually do

A good FRAME schema should help:
- represent structured project reality clearly
- validate core invariants
- support a normalized language-native model in implementations like `frame-python`
- stay portable across tools and languages
- avoid overfitting to one runtime or one repo style

## What the schema should avoid

A bad FRAME schema would:
- hard-code one runtime’s assumptions into the contract
- overfit to Haxaml or any single tool
- become too rigid before enough project-family testing exists
- confuse implementation convenience with conceptual truth
- make the format look “finished” before the architecture is actually stable

## Working rule after the reset

For now, treat schema design as an output of clarified architecture + tested examples.
Not the other way around.

That means the order should be:
1. clarify the contract
2. test the contract against real project families
3. shape the normalized model
4. then write or revise schema candidates
5. then validate implementation behavior against those candidates

## frame-python implication

`frame-python` should not blindly recreate the old schema pipeline.
It should help test:
- what the normalized model should be
- what must be validated strictly
- what should remain provisional
- where the contract is still underspecified
