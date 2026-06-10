# Post 3 — five parts, five jobs

Target: LinkedIn
Status: paste-ready draft, no Markdown formatting in body
Series role: five parts five jobs
Asset suggestion: ../assets/frame-post-3-five-jobs-2800.png

---

One thing i do not want FRAME to become is “five files because five sounds neat.”

That would be pointless.

The five parts only make sense if each one has a different job.

This is the part i kept coming back to while thinking through agent-assisted coding: project truth does not all behave the same way.

Some things are stable.

Some things are rules.

Some things are locations.

Some things are expectations.

Some things are history.

When all of that gets mixed together inside one big markdown file, one memory dump, or one long prompt, it may still be readable to a human for a while. But once agents start doing more work, the difference starts to matter.

Facts is for stable project truth.

Things like what the project is, important product decisions, tech choices, real constraints, user roles, naming decisions, and other truths that should not change every run.

Rules is for what must be obeyed.

Not vibes. Actual constraints. Things like “do not touch generated files,” “backend owns this decision,” “never hardcode this value,” or “this repo uses this test path.”

Map is for where to look.

Agents can search, yes, but good search still needs anchors. A project should be able to say where the important surfaces live instead of making every agent rediscover the repo from zero.

Expect is for what should pass.

This is where expectations, checks, acceptance rules, test commands, proof hints, and “what good looks like” belong.

Acts is for what happened.

Not the project truth itself. More like run history. What went in, what came out, what files changed, what facts changed, what was checked, and what still needs attention.

Basically i am saying the five parts are not five storage boxes.

They are five jobs.

And the more i test the idea, the more i think this separation matters because agents can generate fast, but fast generation without clean project structure becomes hard to govern.

Post 4 is where Frame Lab enters, because this kind of idea can sound nice and still fail badly on real repos.

#FRAME #agent
