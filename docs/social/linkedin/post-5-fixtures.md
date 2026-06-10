# Post 5 -- the fixtures

Target: LinkedIn
Status: paste-ready draft, no Markdown formatting in body
Series role: fixtures
Asset suggestion: ../assets/frame-post-5-fixtures-2800.png

---

For the current FRAME tests, i did not want to use only one kind of project.

That is a trap.

If you test a project-context architecture on only one repo shape, you can accidentally design around that repo and think you discovered a standard.

So i started putting pressure on FRAME with different fixtures.

The current set i have been using includes organize, autopahe, and Pharmax.

They stress FRAME in different ways.

organize is small and simple.

That matters because if FRAME cannot stay lightweight on a tiny Python CLI, then the design is already too heavy. A standard like this cannot require ceremony for every small project.

autopahe adds more tooling pressure.

It has CLI/package shape, browser setup, Playwright concerns, Docker, config, state paths, and more operational details. That kind of project asks: can FRAME represent practical tooling reality without turning into a messy setup note?

Pharmax is heavier in a different way.

It has backend/frontend boundaries, role workflows, invoice lifecycle logic, deployment drift, generated-state noise, and product rules that matter. That kind of project asks: can FRAME handle workflow pressure without making the core architecture app-specific?

That is why fixtures matter.

They are not just examples.

They are pressure surfaces.

Each fixture tries to expose a different weakness in the design.

A small repo checks if FRAME is too much.

A tooling-heavy repo checks if FRAME can hold operational reality.

A workflow-heavy app checks if FRAME can represent product rules and boundaries without becoming bloated.

Basically i am saying FRAME has to earn trust across project shapes.

If it only works when the repo is easy, then it has not earned anything yet.

#FRAME #agent
