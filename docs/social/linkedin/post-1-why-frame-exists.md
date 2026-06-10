# Post 1 -- why FRAME exists

Target: LinkedIn
Status: paste-ready LinkedIn intro post, no Markdown formatting
Series role: introduce the problem before Frame Lab/test evidence
Asset suggestion: ../assets/frame-context-rot.svg

---

No this is not another "i'm building this" or "i built that" kind of post.

This is a post series to share my findings from a lot of research, tests, failed ideas, and things i am still trying to pressure-test. FRAME is not finished work yet. I am still going through the design, testing it against projects, and trying to find the places where i am wrong before pretending the thing is solid.

The simple way to explain FRAME is this: FRAME is a typed context architecture for projects.

That sounds more serious than it is, so basically what i mean is this: FRAME is my attempt to give a software project a clear shape that both developers and AI agents can understand.

I started thinking about this because of how much we currently let AI agents just do whatever inside our projects. Not because the agents are bad. That is not really the point anymore.

In today’s coding agent space, the models are already very good. Maybe saying “we are set for the next five years” is a stretch, but that is how strong the current tools already feel. Claude, Codex, Gemini, Cursor-style agents, local agents, MCP tools, all of it. There are already enough options for people to build serious things, and more tools are still coming.

Also the access keeps getting cheaper. Vibe coder or not, almost anyone can start building with agents now for something like 20 pounds a month or even less depending on what they use. That is wild when you actually sit with it.

So the question for me became less “can agents code?” They can. The better question is: how do we guide them properly when the project is real?

Because real projects are not clean demos. Real projects have old decisions, wrong docs, local setup issues, rules nobody wrote down properly, tests that only work in one folder, files that should not be touched, and product decisions that live inside someone’s head.

Then we throw an agent into that project and expect it to magically understand everything from a README, a prompt file, a few chats, and whatever happens to fit inside the context window. That is where things start getting messy.

There are five main reasons that pushed me toward FRAME.

Reason 1: project context has no real shape yet.

I could not find a real convention for representing project context properly.

We have pieces of it everywhere:

1. project metadata
2. project goals
3. project rules and constraints
4. project agent history
5. project expectations and validation

But most of the time they are scattered. Some things are in README files. Some are in AGENTS.md or CLAUDE.md. Some are in chat memory. Some are in issue threads. Some are in commit history. Some are just in the developer’s head.

I am not saying memory is useless. We need memory. Agents need memory. Developers need memory too. But memory is not the same thing as project representation.

Memory keeps growing. Then you need memory about the memory. Then context starts rotting. Then you switch from Claude Code to Codex or Gemini because of rate limits or workflow reasons, and suddenly you are onboarding the next agent again.

Same project. Same rules. Same constraints. Same explanations. Same “ignore that old doc, this one is the real one.”

That cycle is one of the things that made me feel like something is missing.

A bigger context window does not fully solve it either. It helps, yes. But more context does not automatically mean better context. If the project truth is scattered, duplicated, stale, or badly shaped, then giving the model more of it can still produce confused work.

Basically i am saying the issue is not only about how much context the agent has. It is about the shape of that context.

Reason 2: switching agents still has too much friction.

I do not want to be locked into one agent or one workflow. I want to be able to move between Claude Code, Codex, Gemini, Hermes, local agents, or whatever comes next without feeling like i have to rebuild the whole project brain every time.

Right now switching agents in the middle of a project still has a lot of friction. The agent may have the repo, but it does not really have the project. It does not have the decisions, the trust boundaries, the actual rules, the previous run summaries, the validation expectations, or the parts of the project that are sensitive.

So FRAME is me asking: is there a better way to represent the project itself for transformer-based coding agents? Not just prompt them better. Not just paste more docs. Not just make bigger memory. Actually represent the project in a way that can move across tools.

Reason 3: markdown files alone are not enough.

They are useful, but they are not robust enough once projects get bigger and agent workflows become more serious. A markdown file can say anything. It can be stale, vague, duplicated, ignored, or impossible to validate. It is still mostly human-shaped text.

FRAME is trying to take the best part of prompt/context engineering and give it a more structured form. Something simple enough for developers to fill, but typed enough that tools can inspect it, validate it, and use it consistently.

Reason 4: agents can generate a lot now, but generation is not the same as understanding.

An agent can build a feature, maybe two features, maybe even a whole app in one long run. But it is still working from tokens, attention, examples, tools, and the context we give it. It does not “know” the project the way a long-term maintainer knows it.

So if we are going to use more autonomous agents, we need a better way to order our interaction with them.

Reason 5: governance.

If agents are going to make more changes, we need better ways to validate what they did, record what happened, and define what they are allowed to touch. Not in a heavy enterprise way. Just in a practical way that makes agent work less random.

That is where FRAME is going.

It is basically like a project form, but not a generic form More like a structured project brain.

The developer and the agent should be able to fill in:

- what the project is
- what matters
- what rules must be followed
- where important things live
- what each run is expected to prove
- what happened in previous runs
- what changed
- what still needs checking

Each project should have its own FRAME files, because each project has its own reality. That is the whole point.

FRAME is not trying to make agents generate more code. Agents already generate enough code. Sometimes too much.

FRAME is trying to make agent-assisted development more predictable, more structured, less bloated, and easier to continue across tools.

This is still early. I am still testing the design. I am still checking where it breaks. The next posts will go into the actual shape, the five parts, Frame Lab, the fixtures i tested with, and the method i am using to decide when the structure should change.

But post 1 is just this: if AI agents are now part of how we build software, then projects need a better way to explain themselves to those agents.

That is the problem FRAME is trying to work on.

#FRAME #agent
