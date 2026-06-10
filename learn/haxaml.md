# Haxaml and FRAME

This file should now be read as historical/contextual material, not as the active canonical definition of FRAME.

## What changed

Earlier versions of the project were more tightly entangled with Haxaml.
That helped generate useful ideas, but it also risked making FRAME too Haxaml-shaped.

The reset direction is cleaner:
- FRAME should be able to stand on its own as a standard candidate
- implementations and runtimes should inform it, not own it
- Haxaml should be treated as one influential implementation/runtime line, not as FRAME itself

## What Haxaml still represents

Haxaml still matters as a source of lessons about:
- runtime governance
- MCP-based interactions
- agent workflow discipline
- what static structure alone cannot do

## What Haxaml should not decide by itself

Haxaml should not unilaterally define:
- the final FRAME contract
- the final schema shape
- the final normalized model
- what all future implementations must look like

## Why this matters

If FRAME only fits Haxaml neatly, then FRAME is probably too narrow.
The standard needs room to support other tools, runtimes, and implementations.

## Current stance

Right now, focus the active rebuild on FRAME itself and on `FrameSDK` as the first fresh implementation track.
Use Haxaml mainly as historical pressure, lessons, and future runtime context.
