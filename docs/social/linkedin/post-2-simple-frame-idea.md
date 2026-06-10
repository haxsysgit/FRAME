# Post 2 -- introducing FRAME

Target: LinkedIn
Status: paste-ready draft, no Markdown formatting in body
Series role: introduce FRAME and the architecture-development method
Asset suggestion: ../assets/frame-post-2-better-shaped-context-2800.png

---

The simple way to explain FRAME is this: i am trying to create a better convention for representing a software project when humans and agents are both working inside it.

Not another memory file. Not just a bigger prompt. Not “let me paste the whole repo into context and hope the model figures it out.” More like a project form that the developer and the agent can both keep filling, checking, and using as the repo changes.

Basically i mean, if agents are now helping us generate features, fix bugs, refactor code, write tests, and touch more parts of the repo, then the project itself needs a clearer way to say what is true, what matters, what rules exist, where things live, what should pass, and what actually happened during the work.

That is why FRAME currently has five parts: Facts, Rules, Map, Expect, and Acts. Facts hold what is true about the project. Rules hold what must be followed. Map points to where important things live. Expect describes what should pass or what “good” means for a change. Acts records what happened during work, especially agent work.

I am not treating this like i can just sit down, imagine the perfect architecture, and call it a standard. That would be fake. The way i am developing FRAME is by fitting the current shape against real projects, letting different agents try to map the repo into FRAME, scoring where the fit is clear or forced, then adjusting the architecture only when the pressure makes sense.

The important part is that i still review the outputs myself. The projects i am fitting FRAME on were written by me from beginning to end, so i can tell when an agent is actually capturing the project reality and when it is just making a clean-looking guess. That review layer matters because without it, the scoring can start rewarding nice wording instead of real fit.

So the loop is roughly: fit FRAME to a repo, score the fit, inspect the weak parts, compare agent outputs, review it myself, then adjust the structure slowly. If one project creates an awkward case, that does not automatically mean FRAME needs a new block or field. The pressure has to repeat or expose something real.

That is the kind of convention i am trying to build. Something structured enough that agents can use it, but still understandable enough that a developer can keep up with it without feeling like they now need to maintain another whole system on top of the repo.

FRAME is still early, but the direction is clear to me: better-shaped project context, not just more context.

#FRAME #agent
