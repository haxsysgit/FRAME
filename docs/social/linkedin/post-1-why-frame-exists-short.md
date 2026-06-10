# Post 1 — why FRAME exists, short LinkedIn version

Target: LinkedIn
Status: paste-ready shorter version
Series role: introduce the problem before Frame Lab/test evidence
Asset suggestion: ../assets/frame-context-rot.svg

---

No this is not another "i'm building this" or "i built that" kind of post.

This is a post series to share my findings from research, tests, failed ideas, and things i am pressure-testing. FRAME is not finished yet. I am still checking where the design breaks before pretending the thing is solid.

The simple way to explain FRAME is this: FRAME is a typed context architecture for projects.

Basically, FRAME is my attempt to give a project a clear shape that both developers and agents can keep up with.

I started thinking about this because coding agents are already very good. That is not the issue anymore.

The agent can read the repo, inspect files, trace patterns, generate a feature, fix bugs, write tests, and keep going.

A lot of times the harder part is the way we are building with the agent.

Once an agent starts generating serious code, the developer now has another problem: keeping up.

Keeping up with what changed, why it changed, which files got touched, which rules were followed, which assumptions still hold, and whether the generated work still matches the goal.

That is the part i think a lot of people feel but do not always name.

Agents can move fast now, but software projects still need order.

There are five main reasons that pushed me toward FRAME.

Reason 1: project context has no real shape yet.

We have project metadata, goals, rules, constraints, agent history, expectations, and validation, but most of it is scattered across README files, AGENTS.md, chat memory, issues, commits, and the developer’s head.

Memory is useful, but memory is not the same thing as project representation. Memory keeps growing, context rots, then you switch agents and onboard the next one again.

Reason 2: switching agents still has too much friction.

I want to move between Claude Code, Codex, Gemini, Hermes, local agents, or whatever comes next without rebuilding the project brain.

Reason 3: markdown files alone are not enough.

They are useful, but they can be stale, vague, duplicated, ignored, or hard to validate. FRAME is trying to take the useful part of prompt/context engineering and give it structure.

Reason 4: generating code is not the same thing as governing a project.

Agents can generate a lot now. Sometimes too much. But the developer still needs to understand what entered the codebase, what changed, what risk came with it, and what needs checking.

Reason 5: validation and traceability.

If agents are going to make more changes, we need better ways to record what happened, validate the work, and define what the agent was allowed to touch.

That is where FRAME is going.

Because agent-assisted development itself needs better structure.

FRAME is trying to help developers keep up, organize the project, and make sense of what agents are generating in the repo.

Post 1 is just this: if agents are now part of how we build software, then projects need a better way to explain themselves to both the agent and the developer.

#FRAME #agent
