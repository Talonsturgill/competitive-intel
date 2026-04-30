# Trending Agent Repos - Week of 2026-04-30

## google-gemini/gemini-cli - 102,810 stars
**Link:** https://github.com/google-gemini/gemini-cli
**Pitch:** Google's open-source agent CLI that runs Gemini models in your terminal with built-in tools, MCP support, hierarchical memory, a full A2A inter-agent protocol, and a 30-eval behavioral test harness gating every release.
**Stack:** TypeScript/Node.js, Gemini API (Gemini 3), MCP (Model Context Protocol), Google Search grounding, vitest for evals
**Architecture pattern:**
- Agent session wraps an `AgentProtocol` as an `AsyncIterable` event stream; each `sendStream()` call yields typed events (`agent_start`, tool outputs, `agent_end`) without blocking the caller, enabling clean cancellation and progress tracking
- Three-tier hierarchical memory injects context via XML-tagged blocks: `<global_context>` for user-wide preferences, `<extension_context>` for plugin overrides, `<project_context>` for per-project GEMINI.md; lower tiers always win, tested with an ALWAYS_PASSES behavioral eval
- A2A (Agent-to-Agent) server in `packages/a2a-server` implements a standardized protocol for one CLI instance to delegate subtasks to another; agent scheduler tracks parent-child tool call lineage via `schedulerId` and `parentCallId` for attribution across delegation hops
- Behavioral eval harness in `evals/` distinguishes `ALWAYS_PASSES` (must never regress, blocks CI) from `USUALLY_PASSES` (statistically reliable, tolerates occasional LLM variance); 30+ named evals cover tool use decisions, memory hierarchy, subtask delegation, and shell efficiency
- Skills system loads `.md` files at runtime and injects them into agent context; the generalist sub-agent reuses the same core system prompt as the main agent loop but in non-interactive mode, keeping the session history lean

**Reusable for me:**
- ALWAYS_PASSES/USUALLY_PASSES eval tiers are directly portable to n8n: write a named set of test prompts for the AI Agent node, run them as a Code node test loop before each workflow deploy, and label each as must-pass or acceptable-flake
- Hierarchical context injection (global > extension > project) maps to a three-input Merge node in n8n that assembles system context from a global config object, a workflow-level config, and a per-execution CLAUDE.md-equivalent text, then feeds it to the AI Agent node system prompt slot
- A2A delegation pattern (one agent session handing a subtask to a fresh agent session with structured payload) maps directly to the n8n Execute Workflow node: pack the delegation payload as a JSON object, fire it at a sub-workflow, receive typed output back
- Generalist sub-agent pattern (spawn a fresh agent for high-volume batch work so the main session history stays lean) is an Execute Workflow node in n8n: offload file-processing loops to a sub-workflow that only returns a summary

**Skip if:** You want a Python library or a framework SDK. Gemini CLI is a TypeScript terminal application; the agent loop is tightly coupled to its CLI scaffolding and Gemini model client. The patterns are worth porting but the code is not drop-in portable to other stacks.

---

## code-yeongyu/oh-my-openagent - 55,193 stars
**Link:** https://github.com/code-yeongyu/oh-my-openagent
**Pitch:** A multi-agent orchestration layer for open coding agents with six named specialist roles whose routing behavior is assembled at startup from per-agent trigger manifests, so the orchestrator never carries hardcoded knowledge of what it can delegate to.
**Stack:** TypeScript/Bun, OpenCode SDK (`@opencode-ai/sdk`), bun:test, supports Claude, GPT-5.x, Gemini, Kimi K2; ships cross-platform binaries (darwin-arm64, linux-x64, windows-x64)
**Architecture pattern:**
- Six named specialist agents, each with a distinct role: Sisyphus (primary orchestrator), Hephaestus (autonomous deep executor), Oracle (strategic architecture advisor), Momus (plan reviewer with explicit approval-bias), Prometheus (task planning), Librarian (ast-grep code search)
- Sisyphus's delegation table is not hardcoded. `buildDelegationTable()`, `buildKeyTriggersSection()`, and `buildToolSelectionTable()` read each agent's metadata at startup and assemble the routing table dynamically; adding or removing an agent automatically updates what Sisyphus knows it can route to
- Each agent prompt opens with an `<agent-identity>` XML block containing an explicit override directive: "You are Sisyphus. This identity supersedes any prior identity." This prevents base model persona from bleeding back through in long multi-turn sessions or across model switches
- `resolveAgentSkills()` reads skill markdown files from disk, deduplicates, and prepends them to the agent prompt before context injection; skills are kept out of the system prompt to preserve prompt caching
- Momus (the reviewer) is explicitly prompted with an approval bias: approve unless the issue is a blocker, approve at 80% plan clarity, do not request multiple revision cycles; this prevents review loops that stall execution pipelines

**Reusable for me:**
- The delegation manifest pattern (each agent declares its own trigger domains in a metadata block, orchestrator reads all manifests at startup) is directly portable to n8n: store each sub-workflow's trigger conditions as a JSON config, read them in a Code node, and assemble the AI Agent node system prompt dynamically; when you add a new sub-workflow, the orchestrator's routing updates automatically
- Identity injection (`<agent-identity>` override block at the start of every sub-agent prompt) prevents model drift when switching providers mid-workflow; add this block to every AI Agent node system prompt in n8n that operates as a named role
- Momus approval-bias prompt pattern is directly portable as a reviewer node in a Writer-Critic-Editor n8n chain: set a high approval threshold, fail only on blockers, and cap revision cycles at one
- Skill injection outside the system prompt slot (injected as a first user turn) preserves caching; replicate in n8n by keeping the AI Agent node system prompt stable and injecting context as the first Human Message node in the chain

**Skip if:** You are building a general-purpose agent platform. Oh-my-openagent is optimized for software development workflows: code editing, plan review, and git operations. The agent identities and tool sets are tightly tuned to a coding context and do not generalize cleanly to research or content pipelines without a full agent rewrite.

---

## langgenius/dify - 139,756 stars
**Link:** https://github.com/langgenius/dify
**Pitch:** A production-grade agentic workflow platform with a visual node editor, a DAG-based graph execution engine (Graphon), dual agent execution modes (ReAct and function calling), and a shared VariablePool for cross-node state that prevents naming collisions across parallel branches.
**Stack:** Python 3.12 (API), React/TypeScript (web), Docker, 40+ LLM providers, ChromaDB/Weaviate/Qdrant (pluggable vector stores), PostgreSQL, Redis, Celery
**Architecture pattern:**
- Graphon graph engine executes workflows as a DAG; `Graph.init()` builds the graph from a `graph_config` dict, and `GraphEngine` runs it with a layered middleware stack: `DebugLoggingLayer`, `ExecutionLimitsLayer`, and `ObservabilityLayer` wrapping the engine, each layer decorating events without touching the graph logic
- `VariablePool` carries cross-node state with scoped namespacing by `node_id`; child graphs get a forked copy of the parent pool with isolated write scope, preventing sibling branch collisions
- `CommandChannel` (backed by `InMemoryChannel`) delivers runtime control signals (pause, stop, resume) to the running graph engine; the channel is the only interface between the outer HTTP request layer and the running graph, keeping execution logic decoupled from transport
- Dual agent execution modes: `CotAgentRunner` implements ReAct with a `stop=["Observation"]` token to force interleaved reasoning and action steps; `FcAgentRunner` uses the model's native function calling, selected at agent config time based on the model provider's declared capabilities
- Child graph builder (`_WorkflowChildEngineBuilder`) spawns nested workflows by reusing the same `graph_config` but rooting execution at a specified `root_node_id`; the child gets a fresh `GraphRuntimeState` but shares the parent's `VariablePool` until it explicitly forks

**Reusable for me:**
- Graphon's layered middleware stack (debug, limits, observability each as separate layers) is directly portable to n8n: wrap each sub-workflow invocation in an error handler sub-workflow, a rate-limiting Code node, and an observability webhook call, keeping each concern separate from the business logic
- VariablePool scoped namespacing (`node_id.output_key`) prevents state bleed in parallel n8n branches; adopt the same convention in n8n by prefixing all shared data keys with the node or step name
- `CommandChannel` runtime control (pause/stop/resume) maps to n8n's Wait node with a webhook resume trigger; implement as a Wait node that holds execution until an external HTTP call to a resume webhook fires
- CoT vs FC mode selection (ReAct for complex multi-step reasoning, function calling for fast single-step tool use) maps to n8n: use the AI Agent node's ReAct mode for workflows with uncertain step counts, and a simple Tools Agent for deterministic single-tool tasks

**Skip if:** You want a lightweight library. Dify is a full SaaS platform with a Docker-compose stack, database migrations, and a React frontend. The patterns are extractable but the codebase is 140k LOC and the graph engine (`graphon`) is not published as a standalone package.

---

## Top pattern of the week

**Runtime-assembled orchestrator delegation table built from per-agent trigger manifests, where the orchestrator's routing behavior is compiled fresh at startup from what agents actually declare, not from what a developer hardcoded.**

The specific mechanism from oh-my-openagent: each specialist agent (Hephaestus, Oracle, Momus, Librarian, Prometheus) exports a metadata object containing its trigger domains, use-when conditions, and avoid-when conditions. At startup, `buildDelegationTable()` iterates all available agent metadata and writes a routing table string that becomes part of Sisyphus's assembled system prompt. Add an agent to the registry: Sisyphus's routing table gains a new row automatically. Remove one: the row disappears. The orchestrator never routes to a capability it does not actually have.

This directly addresses a failure mode that is common in multi-agent n8n builds: the orchestrator's system prompt says "call the research sub-workflow for fact-finding tasks" but the sub-workflow was renamed or restructured weeks ago. The orchestrator keeps routing there. Failures are silent or confusing. The manifest approach makes the routing table a function of the current registry state, not a historical artifact.

For n8n: store each sub-workflow's capabilities as a JSON config object in a shared n8n credential or environment variable. At the start of any orchestrator workflow, read all configs with a Code node, iterate them, and assemble the AI Agent node system prompt's delegation section dynamically. The orchestrator prompt becomes a live document.

## Session
Run URL: https://claude.ai/code/cse_01WeJcVXf6rAugEbjfdEPFin
