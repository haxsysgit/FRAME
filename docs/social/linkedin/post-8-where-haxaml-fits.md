# Post 8 — where Haxaml fits

Target: LinkedIn
Status: paste-ready draft, no Markdown formatting in body
Series role: where haxaml fits
Asset suggestion: ../assets/frame-post-8-haxaml-2800.png

---

This is where Haxaml starts to make sense.

FRAME and Haxaml are related, but they are not the same thing.

FRAME is the project representation.

Haxaml is the tooling/runtime direction around using that representation during real agent work.

That distinction matters because i do not want FRAME to be just another prompt file format.

The point is not only to write better notes for agents.

The point is to give tools something structured enough to inspect, route, validate, and update.

So in simple terms:

FRAME says what the project knows.

Haxaml helps agent work happen against that knowledge.

FRAME can hold Facts, Rules, Map, Expect, and Acts.

Haxaml can use those parts to help an agent open a session, understand constraints, know where to look, know what must be checked, record what changed, and avoid pretending unverified work is proof.

That is why Acts and Expect matter so much.

If agents are going to do more work, we need better handoff.

Not just “the agent said it worked.”

What was the input?

What was changed?

What files were touched?

What rule was followed?

What expectation was checked?

What actually passed?

What still needs a human?

That is the kind of project continuity i care about.

FRAME gives the project a typed shape.

Haxaml is where that shape starts becoming useful inside the agent lifecycle.

That is still early. I am still testing the design and looking for oversights.

But the direction is clear to me now:

agent-assisted development needs more than faster generation.

It needs better project continuity, better validation, and a better way for humans to keep up.

That is what i am trying to build toward with FRAME and Haxaml.

#FRAME #agent #Haxaml
