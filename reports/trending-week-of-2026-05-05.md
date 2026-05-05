# Trending Agent Repos - Week of 2026-05-05

**Selection notes:**
- EvoMap/evolver: Chosen for architectural novelty (GEP protocol, Gene/Capsule evolution assets) and direct relevance as a pattern for auditable agent self-improvement loops.
- pydantic/pydantic-ai: Chosen for strongest production readiness signals (Pydantic team, CI, comprehensive evals, OTel), graph-based agent loop, and DBOS/Prefect/Temporal durable execution directly portable to n8n.
- SolaceLabs/solace-agent-mesh: Chosen for event-driven multi-agent mesh architecture (directly analogous to n8n webhook/event model) with DAG dependency tracking and A2A protocol over message broker.

---

## EvoMap/evolver - 7,231 stars

**Link:** https://github.com/EvoMap/evolver

**Pitch:** A self-evolution engine that encodes agent experience as typed Gene and Capsule assets under a protocol-constrained Genome Evolution Protocol, so every prompt improvement is auditable, reusable, and rollback-safe via git.

**Stack:** Node.js >= 18, dotenv; model-agnostic (outputs GEP prompts consumed by any host runtime); integrates with Claude Code, Cursor, OpenClaw via hook system; backed by arXiv research (2604.15097).

**Architecture pattern:**
- Memory scan: on each cycle, reads `memory/` directory for runtime logs, error patterns, and signals to identify what went wrong or could improve.
- Gene/Capsule selection: queries an asset pool of typed evolution assets (Genes = compact strategy representations, Capsules = bundled improvement packages) and picks the best match for current signals using a confidence-score + success-streak gate.
- GEP prompt emission: outputs a protocol-bound prompt that instructs the host agent runtime on the precise evolution step to apply; never directly edits code.
- Solidify step: a human-approval or auto-approve cycle confirms the change; on failure, git rollback restores prior state (blast radius limits cap changes at configurable file/line counts).
- EvolutionEvent audit trail: every cycle writes a JSON event to `memory/` capturing gene id, outcome, and confidence; capsules only broadcast to the EvoMap network after two consecutive success streaks and a passing blast-radius check.

**Reusable for me:**
- Blast-radius-gated evolution loop: model each n8n workflow improvement as a candidate change with explicit file+line limits before apply; use the Switch node to gate on a confidence threshold.
- Audit trail pattern: write every AI Agent node output to a structured log (Code node → external DB) so a future evaluation pass can compute streak-based promotion, same as capsule promotion logic.
- Solidify-or-rollback: wire an n8n HTTP Request node to a git API after each AI-driven config change; if the downstream test fails, trigger the rollback endpoint.
- Gene vs. skill-doc insight: the paper shows compact Gene representations outperform verbose skill docs for iterative improvement signal. Apply this in n8n by compressing learned patterns into short structured records rather than growing prompt context.

**Skip if:** Core `evolve.js` is obfuscated (JavaScript obfuscator listed as devDependency) and the repo is transitioning from GPL-3.0 to source-available. Architecture is well-documented but the actual signal-scoring and gene-selection internals cannot be read or forked. Network features depend on a paid EvoMap Hub account.

---

## pydantic/pydantic-ai - 16,846 stars

**Link:** https://github.com/pydantic/pydantic-ai

**Pitch:** A production-grade Python agent framework from the Pydantic team that models the agent run as a typed graph (UserPromptNode → ModelRequestNode → CallToolsNode → End), adds durable execution backends (DBOS, Prefect, Temporal) so agents survive process crashes mid-run, and ships a first-class evaluation harness with dataset-driven case tracking.

**Stack:** Python 3.9+, pydantic-graph (internal graph runtime), pydantic-evals (evaluation), pydantic-logfire (OTel observability); model-agnostic (OpenAI, Anthropic, Gemini, Bedrock, Vertex, Ollama, 30+ providers); optional durable backends via DBOS/Prefect/Temporal.

**Architecture pattern:**
- Typed graph agent loop: each agent run traverses explicit node types (UserPromptNode, ModelRequestNode, CallToolsNode, End); nodes are iterable and inspectable, so the host can observe, pause, and redirect mid-run.
- Durable execution: wraps the graph run in a DBOS, Prefect, or Temporal workflow so each node transition is a persisted checkpoint; a crashed process restarts from the last completed node, not from scratch.
- Capabilities as composable units: tools, hooks, instructions, and model settings are bundled into typed Capability objects (Thinking, WebSearch, MCP, etc.) that compose onto agents without subclassing.
- Human-in-the-loop deferred tools: specific tool calls can be flagged to pause execution and wait for external approval before proceeding, based on tool arguments, conversation state, or user preferences.
- Structured evals: pydantic-evals ships Dataset + Case + CaseLifecycle; each test case defines inputs, expected outputs, and evaluator functions; results stream to Logfire for time-series performance monitoring.

**Reusable for me:**
- Graph-as-workflow mapping: UserPromptNode maps to an n8n trigger, ModelRequestNode to the AI Agent node, CallToolsNode to HTTP Request or Code nodes, End to a final webhook response. Model any multi-step agent as an explicit n8n graph rather than a single AI Agent black-box.
- Per-node checkpointing: use n8n's execution state + a Redis/Postgres write after each AI Agent node to replicate the durable execution pattern; if a workflow run fails, restart from the last written checkpoint key.
- Capability composition: build reusable n8n sub-workflows (MCP connector, web search, SQL query) and wire them in via the Switch node based on capability flags in the incoming payload, mirroring how capabilities attach to agents.
- Evaluation harness pattern: create a dedicated n8n workflow that replays logged AI Agent inputs against a dataset of expected outputs and pushes pass/fail metrics to a dashboard.

**Skip if:** Deep n8n integration of the durable execution layer (DBOS/Prefect/Temporal) requires standing up an additional orchestration service. The pattern is directly portable in concept but adds infrastructure overhead if you need true crash-resilient execution rather than best-effort retry.

---

## SolaceLabs/solace-agent-mesh - 3,440 stars

**Link:** https://github.com/SolaceLabs/solace-agent-mesh

**Pitch:** An event-driven multi-agent framework that routes every agent-to-agent message through a Solace event broker, enabling fully asynchronous, decoupled agent teams that execute workflow DAGs where nodes fire as soon as their dependencies complete.

**Stack:** Python 3.10-3.13, Google ADK (agent runtime + tool execution), Solace AI Connector (broker integration), Solace Platform event broker (required); Apache 2.0 license; ships a CLI with GUI init.

**Architecture pattern:**
- Event mesh routing: all agent communication travels through a Solace message broker topic hierarchy; no direct agent-to-agent HTTP calls; decoupling is structural, not optional.
- A2A protocol over broker: agents advertise capabilities via the Agent2Agent protocol; the Orchestrator agent discovers peers and delegates subtasks by publishing to their topic; peers publish results back.
- DAG workflow executor: a DAGExecutor class tracks node dependency graphs (depends_on lists), fires nodes whose dependencies are all in the `completed_nodes` set, supports AgentNode, SwitchNode, LoopNode, MapNode, and WorkflowInvokeNode types.
- Dynamic embeds: response templates can include placeholder tokens that the framework resolves at runtime with context-dependent data (real-time queries, file contents, computed values) before delivering to the user.
- Evaluation harness: ships an `evaluation/` directory with a report generator, message organizer, and subscriber for capturing agent-to-agent exchanges and scoring them against expected outputs.

**Reusable for me:**
- Dependency-gated parallel execution: port the `get_next_nodes` pattern (fire all nodes whose deps are in `completed`) to n8n using the Merge node to gate downstream AI Agent nodes on completion of parallel branches.
- Event-driven agent delegation: replace direct AI Agent calls with n8n webhook triggers per agent; the orchestrator publishes a task event (HTTP Request node) and each specialized agent workflow listens on its webhook, matching the broker topic model.
- MapNode pattern: apply parallel fan-out across a list (n8n Split In Batches → parallel AI Agent calls → Merge) to replicate the MapNode's scatter-gather behavior.
- SwitchNode in DAG: model conditional routing in n8n with the Switch node based on structured output fields from a preceding AI Agent node, same as SwitchNode uses its condition expressions.

**Skip if:** The Solace Platform event broker is required infrastructure; a free tier (Solace Cloud) exists but production use requires a paid broker plan. The framework is tightly coupled to the broker for all inter-agent communication, making it impractical to run in a fully local or lightweight setup without Solace.

---

## Top pattern of the week

**Pydantic-AI's typed-graph agent loop with per-node durable checkpointing.**

The specific mechanism: pydantic-ai decomposes the agent run into three explicit typed graph nodes (UserPromptNode → ModelRequestNode → CallToolsNode), each a first-class object in a pydantic-graph run. When a durable execution backend (DBOS, Prefect, or Temporal) is attached, each node transition writes a persistence snapshot before handing off to the next node. A process crash at any point restarts from the last persisted node, not from the beginning of the conversation. This is not generic retry logic: it is checkpoint-per-graph-node, with full state reconstruction including message history, tool results, and conversation ID.

Why this matters for n8n: most n8n AI Agent workflows fail silently mid-run and restart the entire chain. Mapping the pydantic-ai node types to n8n's own node primitives (trigger → AI Agent → HTTP Request → response) and writing execution state to an external key-value store after each node gives the same crash-resilience without standing up a full workflow orchestrator.

## Session

Run URL: https://claude.ai/code/$CLAUDE_CODE_REMOTE_SESSION_ID
