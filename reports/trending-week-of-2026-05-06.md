# Trending Agent Repos — Week of 2026-05-06

## MemTensor/MemOS — 8,917 stars

**Link:** https://github.com/MemTensor/MemOS
**Pitch:** A Memory Operating System for LLMs and AI agents that separates long-term memory into four typed stores and routes queries through a priority-aware async scheduler.
**Stack:** Python 3.10+, Redis Streams, PostgreSQL, graph databases, vector databases (pluggable), Docker, Helm; model providers: OpenAI, Azure OpenAI, Qwen/DashScope, DeepSeek, MiniMax, Ollama, HuggingFace, vLLM
**Architecture pattern:**
- MemCube is the core abstraction: one object composing four distinct memory backends — textual (episodic context), activation (KV cache state), parametric (model-weight-level persistence), and preference (user pattern tracking)
- A MemScheduler backed by Redis Streams handles all memory operations asynchronously; tasks carry priority levels, auto-recovery on failure, and quota-based scheduling to prevent runaway ingestion
- MOS (Memory Operating System) sits above MemCube and SchedulerFactory, providing a unified add/search/update/delete API; chain-of-thought mode (PRO_MODE) decomposes complex queries into sub-queries before retrieval
- Memory feedback loop: natural-language corrections refine, supplement, or replace existing memories over time, closing the write-back gap that most vector stores leave open
- MCP plugin layer exposes the same API to external agents (Hermes, OpenClaw) without requiring SDK integration; multi-cube isolation enables per-user and per-project memory namespacing

**Reusable for me:**
- The scheduler-before-retrieval pattern: in n8n, a Code node can classify the query signal (episodic vs. preference vs. tool) and route to different HTTP Request nodes targeting different memory backends, before any embedding call is made
- The MemCube isolation pattern maps directly to n8n's multi-tenant agent flows: separate "cubes" per user or project keyed by user_id, with a Switch node routing to the right cube
- The feedback correction loop: n8n AI Agent node output can feed into a second Code node that classifies memories as "correct," "supplement," or "replace" before writing back to the store

**Skip if:** Your agents operate in single-session contexts with no persistence requirement, or you are already running mem0 (covered two weeks ago); the production setup requires Redis, PostgreSQL, and a vector database simultaneously.

---

## cft0808/edict — 15,612 stars

**Link:** https://github.com/cft0808/edict
**Pitch:** A twelve-agent multi-agent orchestration system modeled on China's Tang Dynasty Three Departments and Six Ministries, with a mandatory institutional review agent that holds veto power over every task plan before execution begins.
**Stack:** Python 3.9+, React 18 frontend, SQLAlchemy asyncpg, PostgreSQL, Redis, stdlib-only backend (zero dependency); built on top of OpenClaw agent runtime; Docker-first deployment
**Architecture pattern:**
- Strict linear governance: Crown Prince (triage) routes tasks, Planning Department (中书省) decomposes into sub-tasks, Review Department (门下省) audits and can hard-reject with mandatory rework, Dispatch Department (尚书省) assigns approved tasks, seven Ministries execute in parallel
- The Review Department is not optional middleware: every task plan must pass the veto gate before dispatch; the kanban_update.py state machine enforces legal state transitions and rejects illegal state jumps at the code level
- Per-agent workspace isolation: each agent has its own skills list, its own LLM model config (hot-swappable from the dashboard), and its own message permission matrix (who can send to whom is enforced, not just documented)
- Ten-panel real-time dashboard (Kanban, Monitor, Memorial Archive, Officials, Models, Skills, Sessions) with heartbeat monitoring, task intervention (stop/cancel/resume), and complete audit trail stored as "memorial archives"
- Data sanitization layer strips file paths, metadata, and invalid prefixes from task titles before they reach the planning agents, preventing prompt contamination from upstream sources

**Reusable for me:**
- The veto gate pattern is the most portable piece: in n8n, place a dedicated Critic AI Agent node between the Writer/Planner AI Agent node and the executor; the Critic outputs APPROVE or REJECT plus a reason; a Switch node loops back to the Planner on REJECT, with a counter node capping rework at three attempts
- The state machine with enforced transitions maps to n8n's workflow status fields: set a status field after each stage, and use an IF node at the start of each downstream step to validate the expected state before proceeding
- The per-agent model config pattern suggests storing model selection as metadata per agent identity in an n8n database node rather than hardcoding the model in the AI Agent node itself

**Skip if:** You need a lightweight, minimal-dependency agent system; the edict stack requires PostgreSQL, Redis, and OpenClaw and adds meaningful infrastructure overhead. Also skip if the oversight model does not fit: the veto gate adds at least one full LLM call per task, which adds latency and cost.

---

## agentscope-ai/agentscope — 24,633 stars

**Link:** https://github.com/agentscope-ai/agentscope
**Pitch:** A production-ready Python agent framework from Alibaba that separates working memory from typed long-term memory, exposes a message hub for decoupled multi-agent orchestration, and ships built-in OTel tracing and A2A protocol support.
**Stack:** Python 3.10+, asyncio, DashScope/Qwen as default model provider (also supports OpenAI, Anthropic), Redis, SQLAlchemy, Tablestore for working memory backends; Mem0 and ReMe for long-term memory; K8s/serverless deployment; OTel tracing
**Architecture pattern:**
- Two-layer memory: working memory (InMemory, Redis, or AsyncSQLAlchemy) holds the conversation window with database-backed compression; long-term memory is further typed into personal (ReMePersonal), task (ReMeTask), and tool (ReMeTool) stores, each with a different retrieval strategy
- ReAct agent loop exposes three distinct methods: \_reasoning() to produce tool call decisions, \_acting() to execute tool calls and collect results, and \_summarizing() to compress memory when the window exceeds threshold; each is overridable independently
- Message hub (MsgHub) decouples agent communication: agents subscribe to named topics and broadcast to groups without direct references, enabling add/remove of agents at runtime without rewiring
- A2A (Agent-to-Agent) protocol built in: agents expose a standard interface that other frameworks (not just AgentScope) can call, enabling cross-framework agent composition without a shared runtime
- OTel (OpenTelemetry) tracing is first-class: every agent call, tool call, and memory operation emits spans, making production observability possible without instrumentation work

**Reusable for me:**
- The two-layer memory split (working vs. typed long-term) maps directly to n8n: working memory as in-memory session state in an Execute Workflow node, long-term as HTTP Request calls to a ReMe or Mem0 endpoint; the split prevents the long-term store from being polluted with short-lived context
- The \_reasoning/\_acting/\_summarizing separation is a clean pattern for n8n AI Agent node composition: one AI Agent node for decision, one Code node for tool dispatch, one AI Agent node for compression when token count exceeds threshold
- The message hub pattern: n8n webhooks can act as a lightweight message bus where each agent workflow subscribes to a named path and publishes results back to the hub path, enabling the same topology without a shared framework

**Skip if:** Your team is outside the Alibaba/DashScope ecosystem — the default config and docs are DashScope-first and the OpenAI adapter adds friction; also skip if you need a stable v1 API today (AgentScope 2.0 is in active development per the Jan 2026 roadmap).

---

## Top pattern of the week

**Four-store memory cube with a signal-routing scheduler, not a single vector index**

MemOS's core architectural decision is to split memory into four typed backends — textual episodic, KV activation, parametric model-weight, and preference — and place a Redis Streams priority scheduler in front of all retrieval. The scheduler classifies the query signal first, activates only the relevant store or stores, applies recency scoring before the embedding call, and queues ingestion operations asynchronously with priority and auto-recovery. Nothing hits the retrieval layer until the scheduler has made the routing decision.

The documented outcome of this architecture is 43% better accuracy than OpenAI Memory on long-horizon benchmarks, with 35% fewer memory tokens consumed per session. The token reduction is a direct consequence of not querying all four stores simultaneously on every call.

The portable insight for n8n workflows is the routing layer itself: a Code node or Switch node that classifies the query type before any AI Agent node or HTTP Request to a vector database is called, ensuring that preference retrieval, episodic retrieval, and tool-history retrieval each hit the backend best suited for that signal.

---

## Session

Run URL: https://claude.ai/code/$CLAUDE_CODE_REMOTE_SESSION_ID
