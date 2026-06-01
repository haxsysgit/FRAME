# Project Family Research (Reset Pass)

This note revises the earlier project-family framing for FRAME.

The earlier family list was directionally useful, but it mixed several different axes into one flat list. That makes fitting noisy for agents and misleading for schema design.

## The main correction

When people say "software families" today, they usually blend together at least four different things:

1. **Delivery surface**
   - How users or developers interact with the system.
   - Examples: CLI, web app, desktop app, mobile app, API/SDK.

2. **System role**
   - What job the system plays in the world.
   - Examples: product app, developer tool, data platform, infra platform, AI system, internal tool.

3. **Repository shape**
   - How the codebase is structurally organized.
   - Examples: single-package repo, service repo, monorepo, plugin ecosystem, legacy mixed repo.

4. **Operating context**
   - How the project is governed and changed.
   - Examples: startup-speed project, enterprise-governed project, regulated system, community-driven OSS.

These are all real and useful, but they should not be collapsed into one bucket.

## Why this matters for FRAME

If FRAME treats all of these as one kind of "family", agents will confuse:
- what the project *is*
- how the repo is *laid out*
- how the team *works*
- and what kind of context the task actually needs

That leads to bloated schema fields and weak fitting.

## Better model for FRAME Lab

FRAME Lab should use a layered model.

### Layer 1: Delivery families
These are the most intuitive first-cut families because they strongly affect runtime surfaces, entrypoints, testing style, user flows, and packaging.

Current high-value delivery families:
- CLI tools
- web platforms / web products
- desktop apps
- mobile apps
- API / developer tooling products
- SDKs / libraries

### Layer 2: System-role families
These matter because they change what "project reality" and "correctness" mean.

Current high-value system-role families:
- product applications
- developer tools
- data platforms
- infrastructure / platform tooling
- AI systems / agent systems
- internal-tool / workflow systems

### Layer 3: Repository-shape families
These matter because they change how agents should navigate and assemble context.

Current high-value repo-shape families:
- single-service repo
- multi-service repo
- monorepo
- plugin / extension ecosystem
- SDK/library repo
- legacy mixed repo

### Layer 4: Operating-context overlays
These should be treated as overlays, not core families.

Examples:
- startup-speed
- enterprise-governed
- regulated / compliance-heavy
- community-maintained OSS

## Practical recommendation

For early FRAME fitting, the most useful first organizing lens is:
1. delivery family
2. system role
3. repo shape

That order is more concrete for agent behavior than starting from company context.

## Evidence from the GitHub research pass

Recent public repos surfaced during the pass naturally clustered into the following practical buckets:
- CLI tools: `httpie/cli`, `yt-dlp/yt-dlp`
- web platforms: `immich-app/immich`, `appwrite/appwrite`
- desktop apps: `DevToys-app/DevToys`
- mobile apps: `organicmaps/organicmaps`
- API/devtools: `hoppscotch/hoppscotch`, `Kong/insomnia`
- data platforms: `apache/superset`, `airbytehq/airbyte`
- AI systems: `OpenHands/OpenHands`
- infra platforms: `localstack/localstack`

This pattern suggests the ecosystem is broad enough that a single flat family list is too crude.

## Constructive criticism of the old family framing

What the old list got right:
- FRAME must not be shaped around one repo type
- cross-family fitting is necessary for legitimacy

What the old list got wrong:
- it mixed software type, repo shape, and org context in one level
- it made `monorepo` look like the same kind of category as `web app`
- it made `startup` and `enterprise` look like the same kind of category as `SDK`

That is not clean enough for agent-facing standardization.

## Recommendation for the next FRAME canon

The canon statement should not say:
- FRAME supports these fixed families: X, Y, Z

It should say something closer to:
- FRAME must generalize across delivery families, system roles, repo shapes, and operating contexts
- but it should freeze only the minimum structure that survives repeated fitting across them

That is a stronger and less bloated foundation.
