# Trending Agent Repos - Week of 2026-06-17

Three picks this week, chosen for architectural novelty and production
readiness over framework-clone noise. The high-star results were heavily
polluted by keyword-stuffed harness clones, so these were selected for a
real orchestration idea backed by tests, CI, and docs.

## open-multi-agent - 6,389 stars
**Link:** https://github.com/open-multi-agent/open-multi-agent
**Pitch:** A TypeScript multi-agent framework where you hand a coordinator a plain-language goal and it builds the task dependency graph at runtime instead of making you wire one by hand.
**Stack:** TypeScript 5.6, Node 18+, three runtime dependencies, Vitest for tests, Zod for structured output, 12 built-in LLM providers plus any OpenAI-compatible endpoint (Anthropic, OpenAI, Gemini, Ollama, vLLM, Groq).
**Architecture pattern:**
- A coordinator agent decomposes a goal string into a typed task DAG with explicit dependsOn edges
- A TaskQueue tracks the dependency graph, auto-unblocks tasks as parents complete, and cascades failure to dependents
- A Scheduler ranks ready tasks by critical path using a BFS that counts how many tasks each one transitively unblocks (dependency-first), with round-robin, least-busy, and capability-match as alternates
- An AgentPool with a semaphore runs independent tasks in parallel, each agent looping through tool dispatch until done
- The decomposition can be frozen into a plain JSON plan artifact and replayed later with runFromPlan, skipping a second coordinator call
**Reusable for me:** The goal-to-DAG decomposition maps almost directly onto n8n. An AI Agent node can act as the coordinator that emits a JSON task list with dependencies, a Code node can topologically sort it and compute the most-blocked-dependents score, and a Switch plus parallel branches can fan out the independent tasks. The plan-artifact idea is the strongest steal: cache the coordinator output as a workflow variable so repeat runs skip the planning LLM call entirely. The proposer-to-judge runConsensus loop is a clean Writer-Critic to port with two AI Agent nodes and a verify gate.
**Skip if:** You already know the exact workflow shape up front. A hand-wired graph (or a static n8n workflow) is cheaper and more predictable than paying a coordinator LLM call to rediscover a topology you could hardcode.

## Microsoft Agent Framework - 11,411 stars
**Link:** https://github.com/microsoft/agent-framework
**Pitch:** Microsoft's production-grade successor to AutoGen and Semantic Kernel for building agents and graph-based multi-agent workflows in both Python and .NET.
**Stack:** Python 3.10+ and C#/.NET, PyPI agent-framework plus NuGet Microsoft.Agents.AI, OpenTelemetry for tracing, YAML declarative agents, Microsoft Foundry and Azure OpenAI hosting, broad provider support.
**Architecture pattern:**
- Graph-based workflow engine with named patterns: sequential, concurrent, handoff, and group collaboration
- Durable execution with checkpointing, restartability, and time-travel so a long run can resume from a saved state
- A middleware pipeline wraps every request and response for exception handling, governance, and custom pre/post processing
- Built-in OpenTelemetry spans across agents, tools, and workflow steps for distributed tracing
- Declarative YAML agent definitions plus an Agent Skills layer that builds discoverable knowledge bases from files and code
**Reusable for me:** The checkpoint-and-resume model is the pattern to port. For long n8n runs I can persist workflow state to a database node after each stage so a failed run restarts mid-pipeline instead of from zero. The four named orchestration shapes are a useful vocabulary for choosing between a linear chain of AI Agent nodes (sequential), parallel branches with a merge (concurrent), and a Switch-driven handoff. The middleware idea maps to a shared pre-processing sub-workflow every agent call routes through.
**Skip if:** You want something lightweight and embeddable. MAF is a large two-language enterprise framework with an Azure and Foundry gravity well. For a small Node or n8n stack the surface area and tooling overhead are far more than the orchestration idea is worth.

## AgentScope - 26,933 stars
**Link:** https://github.com/agentscope-ai/agentscope
**Pitch:** A production-ready Python agent framework built around a unified event bus, fine-grained tool permissions, and multi-tenant serving, designed to lean on model reasoning rather than rigid prompt scaffolding.
**Stack:** Python 3.11+, PyPI agentscope, Apache-2.0, sandbox backends for local, Docker, and E2B, DashScope and other model providers, streaming event API.
**Architecture pattern:**
- A unified Event System streams every step of the reasoning-acting loop to the frontend and to human-in-the-loop gates
- A Permission System gives configurable, per-tool and per-resource control over what an agent may touch
- Multi-tenancy and multi-session serving isolates state across tenants for production deployment
- Workspace and sandbox support runs tools and code in local, Docker, or E2B isolation
- An extensible middleware system exposes composable hooks into the agent's reason-act loop
**Reusable for me:** The event-stream-everything model is the takeaway. Emitting a structured event at every reasoning and tool step (rather than only logging the final answer) is exactly what an n8n run needs for observability, and it maps to a webhook or queue node that fires per step. The per-tool permission gate is portable as an allowlist check in a Code node before any tool-calling AI Agent node executes. The sandbox-by-default tool execution is a good safety pattern for any agent that runs bash.
**Skip if:** You do not need fine-grained permissions or multi-tenant serving. For a single-tenant internal workflow the event bus and permission system are infrastructure you would carry without using, and a simpler single-agent loop will ship faster.

## Top pattern of the week

Runtime goal-to-DAG decomposition with a replayable plan artifact, from
open-multi-agent. A coordinator agent turns one natural-language goal into
a typed task dependency graph, a scheduler ranks ready tasks by
critical-path priority (a BFS counting how many tasks each one transitively
unblocks), independents run in parallel under a semaphore, and the whole
decomposition can be frozen as plain JSON and replayed so the same graph
re-runs without a second planner call. The breakthrough is the inversion:
the engineer describes the outcome, not the graph, and the expensive
planning step becomes a cacheable, version-controllable artifact instead
of a cost paid on every run.

## Session
Run URL: https://claude.ai/code/cse_014yjBKamKemg4VArJgqtq7Z
