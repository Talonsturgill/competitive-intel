**Most multi-agent systems route on instinct. oh-my-openagent routes from a manifest.** I cloned 25 trending agent repos this week and one pattern kept me re-reading the source. When Sisyphus, the orchestrator, boots up, it does not start with a hardcoded routing table.

Every sub-agent in the system publishes a metadata block. Trigger domains. When to use it. When to avoid it. A single builder function reads all those manifests and assembles the orchestrator's delegation table at startup. Add a new agent. The table rebuilds. Remove one. The table shrinks. The orchestrator never carries stale knowledge about what it can route to.

This solves something specific. An orchestrator that routes to an agent with capabilities it no longer has fails silently. The manifest approach makes that impossible because the routing table is always built from what actually exists.

There is also an identity injection pattern in the same codebase. Each sub-agent prompt opens with an XML block that explicitly overrides the base model's prior identity. Sisyphus is Sisyphus. The base model's default behavior is displaced, not appended to. In long multi-turn sessions, base model identity bleeds back through. This shuts that down.

The repo has 55k stars and ships cross-platform binaries. The delegation manifest pattern is small enough to port in a day.
