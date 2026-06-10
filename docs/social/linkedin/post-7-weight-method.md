# Post 7 -- weight and pressure

Target: LinkedIn
Status: paste-ready draft, no Markdown formatting in body
Series role: weight method
Asset suggestion: ../assets/frame-post-7-weight-method-2800.png

---

One thing i am trying to avoid with FRAME is schema bloat.

That is where the weight idea comes in.

When a fixture creates pressure on the design, the first question should not be “what new field do i add?”

That is too easy.

If every uncomfortable project earns a new block or field, FRAME becomes the exact thing i am trying to avoid: another bloated context system that looks smart but becomes annoying to maintain.

So i started thinking about pressure as weight.

A problem becomes heavier when it repeats across fixtures, affects agent usefulness, makes retrieval or validation clearer, reduces duplication, improves governance, and still stays understandable to normal developers.

A problem stays light when it is only one weird repo detail, or when it can already be represented cleanly with the current shape.

Basically the question is:

is this pressure asking FRAME to improve, or is this just one project being one project?

That distinction matters a lot.

For example, if one fixture has a strange config rule, that does not automatically mean FRAME needs a new Config block.

Maybe it belongs in Facts.

Maybe it belongs in Rules.

Maybe Map should point to the source file.

Maybe Expect should define how to validate it.

Maybe Acts should record that an agent changed it.

The current shape should get tested first before the architecture grows.

That is the method i am using:

1. feel the pressure
2. try to place it inside the current five parts
3. check if the placement helps agents and developers
4. check if the same issue repeats elsewhere
5. only then adjust the shape

So weight is not a fancy algorithm yet.

It is more like a discipline.

A way to stop myself from turning every finding into a permanent schema decision too early.

FRAME should adjust from repeated pressure, not from vibes.

That is the whole point.

#FRAME #agent
