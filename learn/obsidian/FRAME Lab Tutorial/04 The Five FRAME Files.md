# The Five FRAME Files

The active candidate uses five linked FRAME parts:
- Facts
- Rules
- Map
- Expect
- Acts

## Easy memory trick

- Facts = what is true
- Rules = what must be followed
- Map = where things are
- Expect = how we know work is correct
- Acts = what happened in relevant runs

## Facts

Facts holds stable project reality.

Examples:
- project profile
- stack
- architecture shape
- sources of truth
- quirks
- open questions

## Rules

Rules holds work constraints and safe behavior.

Examples:
- canonical commands
- do-not-do guidance
- ask-first triggers
- style/process rules

## Map

Map shows where important repo surfaces live.

Examples:
- roots
- paths
- groups
- entrypoints
- managed areas

## Expect

Expect says what counts as correct.

Examples:
- outcomes
- must_hold rules
- checks
- proof
- done_when

## Acts

Acts is run history.

In 0.2.0, Acts is much clearer than before.
It is there to help retrieval, review, and handoff.

Examples of useful Acts run fields:
- work_kind
- keywords
- touched surfaces
- changed facts
- rules followed
- checks_seen
- checks_ran

The big rule is simple:
Acts should not pretend to be a second Facts file.
