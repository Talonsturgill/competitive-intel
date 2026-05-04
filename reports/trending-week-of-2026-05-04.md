# Trending Agent Repos — Week of 2026-05-04

## IBM/mcp-context-forge — 3,655 stars

**Link:** https://github.com/IBM/mcp-context-forge
**Pitch:** An open-source MCP registry and proxy that federates MCP, A2A, and REST/gRPC backends behind one governed endpoint with a 40-plugin middleware pipeline.
**Stack:** Python (FastAPI, SQLAlchemy, Pydantic), Rust (mcp_runtime, a2a_runtime, native extension crates), Redis, PostgreSQL, Docker/Kubernetes; model-provider agnostic via A2A routing.
**Architecture pattern:**
- Single gateway endpoint receives all inbound calls (MCP JSON-RPC, A2A agent tasks, REST, gRPC); a protocol translation layer normalizes them into internal tool/resource/prompt objects.
- Plugin chain runs pre- and post-request: 40+ plugins cover rate limiting, JWT auth, circuit breaker, response caching, content moderation, SQL sanitization, output length guard, and OpenTelemetry span emission.
- Four service registries (ToolService, ResourceService, PromptService, GatewayService) each own their entity lifecycle; GatewayService handles federation health checks and capability aggregation across multiple upstream gateways.
- Redis-backed session registry and resource cache enable horizontal scale; multiple gateway instances share the same tool namespace without coordination code in the client.
- gRPC reflection protocol drives automatic service discovery: point ContextForge at a gRPC server and it introspects all methods, generates JSON Schema, and exposes them as MCP-compliant tools with no manual registration.

**Reusable for me:**
- Plugin chain pattern maps directly to an n8n sub-workflow chain: each plugin is a Switch node routing to a Code node (rate check), then HTTP Request node (upstream call), then another Code node (response sanitize). The "plugin as middleware" mental model ports cleanly.
- REST-to-MCP virtualization mirrors what the n8n AI Agent node does when given an HTTP Request tool — ContextForge just formalizes it with JSON Schema extraction, retry policy, and an admin UI for registration.
- The circuit breaker plugin (in `plugins/circuit_breaker/`) tracks failure rate per tool and stops routing to a failing upstream after a threshold — worth porting as a Code node wrapper around any flaky HTTP Request call in n8n.
- OpenTelemetry instrumentation per tool call is directly portable: emit a trace event from a Code node after each AI Agent tool invocation to get token usage and latency per tool in a unified backend.

**Skip if:** You are not running multiple MCP servers that need unified governance. ContextForge is enterprise infrastructure — the Redis federation, Kubernetes Helm chart, Ansible playbooks, and Keycloak integration are all real production concerns that add ops overhead a single n8n instance does not need.

---

## RightNow-AI/openfang — 17,132 stars

**Link:** https://github.com/RightNow-AI/openfang
**Pitch:** An Agent Operating System written in Rust that compiles to a single 32 MB binary, runs autonomous "Hands" on schedules without human prompting, and enforces per-agent resource quotas with a rolling hourly token budget.
**Stack:** Rust (14 crates, Axum 0.8, Tokio, SQLite via rusqlite, Tauri 2.0 for desktop), WASM sandbox via Wasmtime, 3 native LLM drivers (Anthropic, Gemini, OpenAI-compatible covering 20 providers).
**Architecture pattern:**
- openfang-kernel assembles 18 subsystems at boot: AgentRegistry, AgentScheduler, CapabilityManager, EventBus, Supervisor, WorkflowEngine, TriggerEngine, WasmSandbox, ModelCatalog, MeteringEngine, ModelRouter, and AuthManager (RBAC).
- Each autonomous Hand bundles a HAND.toml manifest (tools, settings, dashboard metrics), a multi-phase system prompt of 500+ words, a SKILL.md domain reference injected into context at runtime, and explicit approval gates for sensitive actions (purchases, public posts).
- openfang-memory is a SQLite substrate with five schema versions: structured KV, semantic search with vector embeddings, a knowledge graph (entities + typed relations + confidence scores), session management, and usage event persistence — all queried through an async bridge using spawn_blocking.
- AgentScheduler enforces resource quotas with a rolling hourly window: per-agent token budget and tool-call count reset every 3,600 seconds; agents that exceed quota receive a QuotaExceeded error and pause until the window resets.
- WorkflowEngine chains steps across multiple agents: output from one agent step flows as input to the next, with support for parallel fan-out, conditional branching, and quality-gate loops.

**Reusable for me:**
- HAND.toml manifest pattern maps directly to an n8n workflow with a Webhook trigger and a Config node at the top: name, required tools, rate limits, and delivery channel all declared in one place before any logic node.
- The approval gate (before any irreversible action, route through a human-in-the-loop node) is immediately portable to n8n using the Wait node followed by a Webhook listener for approval or rejection.
- Knowledge graph memory (entities, relations, confidence score) is implementable in n8n as a Code node that writes to a lightweight SQLite file or a Postgres table — the entity-relation schema is not complex and the confidence float gives you a natural ranking filter.
- Per-agent token budget enforcement maps to a Code node at the start of each AI Agent node call that reads a counter from a KV store, rejects if over budget, and increments after each successful call.

**Skip if:** You need reactive, event-driven workflows rather than schedule-driven autonomous agents. OpenFang is optimized for "wake up and run" patterns; n8n's strength is inbound trigger-response. The two models are complementary rather than interchangeable, and porting OpenFang's full scheduler into n8n would be reinventing the cron trigger.

---

## EvoMap/evolver — 7,205 stars

**Link:** https://github.com/EvoMap/evolver
**Pitch:** A Node.js self-evolution engine for AI agents that encodes agent experience as compact Genes and Capsules under the GEP (Generative Evolution Protocol), backed by an arXiv paper showing Gene encoding outperforms skill documents by nearly 2x on hard reasoning tasks.
**Stack:** Node.js (>=18), Git (required for audit trail and rollback), optional Redis via A2A hub at evomap.ai; integrates with Cursor, Claude Code, and OpenClaw via setup-hooks.
**Architecture pattern:**
- On each run, the engine scans `./memory/` for runtime logs and git history to build learning signals; a strategy preset (balanced, innovate, harden, repair-only) biases which Gene types get considered.
- Gene selection picks the best-fit compact behavior representation from the asset pool; a Gene encodes what worked in a structured, versioned object rather than a verbose instructions document.
- Confirmed Genes are promoted to Capsules after clearing three independent gates: outcome score >= 0.7, a consecutive success streak of at least 2 runs, and a blast-radius check confirming the behavior touched fewer than 5 files and 200 lines.
- Each promotion writes an EvolutionEvent to `./memory/` and to git, creating a content-addressed, rollback-capable audit trail with SHA256 asset IDs.
- Capsules that pass all gates become broadcast-eligible and publish to the A2A EvoMap hub, where peer agents can consume them with a confidence-decay factor applied to externally received assets.

**Reusable for me:**
- Triple gate before promotion (score + streak + blast radius) is directly portable to any n8n workflow template library: before promoting a candidate workflow to "production template," run it N times, require two consecutive passes above a quality threshold, and reject if it touches more than a scoped set of nodes.
- Git-based audit trail for evolution events maps to n8n execution history plus a Code node that writes a structured event record after each AI Agent node completes — gives you rollback context and a trainable signal log.
- Confidence decay on externally sourced assets (externally received Capsules get their confidence multiplied by 0.6) is a useful pattern for any n8n workflow that consumes AI-generated content from a third party before passing it downstream.
- Blast-radius limit as a safety gate (max files + max lines before a change is rejected) translates to a Code node that counts token output length and node-touch scope before allowing an AI-generated n8n workflow patch to apply.

**Skip if:** Your agents are not self-modifying or self-improving. Evolver is purpose-built for evolutionary loops where the agent's own behavior changes over time. For static prompt-and-execute workflows the overhead adds no value. Also worth noting: the core GEP engine files are obfuscated JavaScript as the project transitions to source-available, so you are building on a closed inner loop you cannot fully audit.

---

## Top pattern of the week

**Triple-gated capsule promotion: outcome score threshold, consecutive success streak, and blast-radius scope limit — all three must clear before any evolved agent behavior becomes a reusable asset or peer broadcast.**

Evolver's three-gate system is the most directly portable architectural pattern this week. The specificity is the point. "Gate on quality" is obvious advice. "Gate on score >= 0.7, AND a streak of at least 2 consecutive successes, AND confirm that the change touched fewer than 5 files and 200 lines" is an implementable spec.

The streak gate is what makes the system reliable rather than lucky. A single high-scoring run can be an anomaly — good inputs, favorable context, a lucky draw from the model. Two consecutive successes under different conditions means the behavior is stable. The streak requirement converts a snapshot metric into a durability signal.

The blast-radius gate is the safety layer that makes self-modification tractable. By refusing to promote any behavior that touches too much of the system at once, the engine limits its own footprint during evolution. Each Gate is independent: a behavior can score 0.9 and fail on blast radius, or pass blast radius and fail on streak. Clearing all three is what earns promotion.

For an n8n builder, this pattern applies to any workflow template library that uses AI to generate or improve workflows. Before a candidate gets promoted from "experiment" to "production template," run it three to five times, require two consecutive passes above your quality threshold, and reject if the generated changes exceed a scoped node count. The numbers Evolver uses (0.7, 2 streak, 5 files) are calibrated on code-solving tasks — your thresholds will differ, but the three-gate structure transfers directly.

## Session

Run URL: https://claude.ai/code/cse_01RrYnSdoDHUvC3HGnr9qJ4Z
