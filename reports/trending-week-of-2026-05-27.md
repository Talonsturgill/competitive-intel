# Trending Agent Repos - Week of 2026-05-27

## thedotmack/claude-mem - 78,954 stars

**Link:** https://github.com/thedotmack/claude-mem
**Pitch:** A TypeScript sidecar agent that captures every tool call in a coding session, compresses it into structured observations via a second LLM, and injects a recency-ranked memory timeline into the next session.
**Stack:** TypeScript, Bun runtime, SQLite (primary store), ChromaDB (optional semantic layer), @anthropic-ai/claude-agent-sdk, BullMQ/Redis (optional queue), Express HTTP worker daemon
**Architecture pattern:**
- Lifecycle hooks (PostToolUse, Stop, SessionStart) fire into a long-running HTTP worker on port 37777
- Worker spawns an isolated observer LLM that reads raw tool input/output and produces typed XML (type, title, narrative, facts, files_read, files_modified)
- At session end, a mode-switch prompt generates a structured summary (request, investigated, learned, completed, next_steps)
- Dual-store writes observations to SQLite with FTS5 search and optionally syncs sub-documents to ChromaDB with semantic search
- On SessionStart, ContextBuilder fetches observations ordered by recency, applies progressive disclosure (full narrative for recent N items, compact table rows for older items), and injects the rendered timeline as the session's opening context

**Reusable for me:**
- The hook-capture pattern maps directly to n8n PostExecution webhooks that pipe agent output to a Code or HTTP Request node
- The structured XML extraction prompt (buildObservationPrompt) is a drop-in template for any n8n summarization step using the AI Agent node
- The dual-store pattern (SQLite primary, vector DB secondary with graceful fallback) is directly portable to n8n with a database node as primary and a Qdrant/Weaviate HTTP Request as optional overlay
- Progressive disclosure injection: store observations in a database node, inject recent rows in full, older rows as compact summaries — directly configurable as an expression in an n8n Code node
- Token economics tracking (discovery_tokens vs. read_tokens per observation) can be logged to a monitoring table in n8n to measure memory compression ROI

**Skip if:** Your agent sessions are short-lived and stateless — the value only compounds over repeated sessions on the same project.

---

## lobehub/lobehub - 77,784 stars

**Link:** https://github.com/lobehub/lobehub
**Pitch:** A full-stack multi-agent operating system built on Next.js 16 where a Supervisor/Executor state machine orchestrates a dynamic roster of agents, each carrying a fully serializable AgentState passport through every execution step.
**Stack:** TypeScript, Next.js 16, React 19, PostgreSQL with Drizzle ORM, tRPC, Zustand 5, Vitest, Playwright, Electron (desktop), 70+ model providers
**Architecture pattern:**
- Single-agent loop: AgentRuntime.step() increments stepCount, calls the Brain to produce typed AgentInstruction objects, dispatches each to an executor (call_llm, call_tool, call_tools_batch, request_human_approve, finish), returns serializable {events, newState, nextContext}
- Group orchestration: GroupOrchestrationRuntime runs Supervisor → Executor cycles; supervisor maps previous result type to next instruction type (speak, broadcast, execute_task, execute_tasks, delegate, finish); loops until finish or abort
- AgentState carries messages array, stepCount, status, usage, cost, costLimit, securityBlacklist, operationId, toolManifestMap as serializable JSON — enabling interrupt and resume at any step
- Dual scheduling: agentCronJobs table (cron pattern + timezone + maxExecutions) and tasks table (schedule mode vs. heartbeat mode with configurable interval and timeout alert)
- LLM-as-judge eval harness (eval-rubric package): weighted rubrics with contains, regex, levenshtein, jsonSchema, numeric, and LLM judge matchers; configurable passThreshold

**Reusable for me:**
- The Supervisor/Executor loop maps to n8n's Switch node routing to sub-workflows per instruction type
- The serializable AgentState passport pattern translates directly to an n8n execution context variable that survives loop iterations and can resume after human approval
- The dual scheduling model (cron + heartbeat) can be replicated with n8n Schedule Trigger for cron and a Watch node for heartbeat detection
- The LLM-as-judge rubric pattern is portable as an n8n AI Agent node call after generation, scoring output against criteria and thresholds before passing downstream
- The InterventionChecker security layer (never/always/required per tool with argument matchers) maps to n8n's If node as a pre-execution gate

**Skip if:** You want a standalone library to extract and run — this is a monorepo product; the agent runtime packages are decoupled in theory but the agent manager is deeply coupled to Zustand frontend store state.

---

## infiniflow/ragflow - 81,344 stars

**Link:** https://github.com/infiniflow/ragflow
**Pitch:** A Python RAG engine that fuses retrieval and agent capabilities through a visual canvas DSL where any node in the graph can append chunks to a shared accumulator, producing a single grounded answer with unified citations from multiple retrieval points.
**Stack:** Python 3.13-3.14, Elasticsearch/Infinity/OceanBase (pluggable), Redis, MySQL, React frontend, 15+ reranker providers, 20+ embedding providers, Langfuse observability
**Architecture pattern:**
- Canvas DSL graph: nodes typed as Begin, Retrieval, LLM, Agent, Categorize, Switch, LoopItem, Message; wired via {component_id@output_name} variable interpolation in plain JSON
- Hybrid search in search.py: BM25 full-text (sparse) fused with ANN vector search (dense) at index time for Infinity backend (5/95 weight), post-fetch for Elasticsearch; optional cross-encoder reranker with 15+ provider options including LLM-as-reranker via QWen3-Rerank
- Agent loop in chat_model.py: standard ReAct function-calling loop with max_rounds cap (default 5), asyncio.gather for parallel tool calls per round, conversation history condensed via full_question() rewrite when history exceeds 3 turns
- Shared retrieval accumulator: every node appends chunks to canvas.retrieval[-1]; final Message node surfaces all of them as unified citations regardless of how many retrieval points fired in the graph
- DeepDoc layout-aware chunking: OCR + table transformer + domain-specific templates (paper, laws, book, resume, audio) with RAPTOR hierarchical summarization and GraphRAG entity/relation graphs as optional post-ingestion layers

**Reusable for me:**
- The canvas DSL pattern (JSON-described graph with typed nodes and variable interpolation) is a direct model for n8n workflow design — implement it with n8n's HTTP Request, AI Agent, and Code nodes as the component types
- The Retrieval-as-tool pattern (wrapping RAG as an OpenAI function tool with a single query string param) maps cleanly to an n8n Tool sub-workflow called from the AI Agent node
- The shared retrieval accumulator translates to an n8n workflow variable that grows across loop iterations before a final generation step — enables multi-hop citation tracking
- Hybrid search weight configuration (keywords_similarity_weight + vector_similarity_weight as separate floats) is a config-driven pattern portable to any vector DB with hybrid search support
- The citation post-processing pass (generate answer, then second LLM call to inject inline citations) maps to a two-node n8n sequence after generation

**Skip if:** You need to port the document parsing layer — DeepDoc OCR, RAPTOR clustering, and GraphRAG are deeply framework-bound Python subsystems with no clean API boundary for extraction.

---

## Top pattern of the week

**Two-tier progressive disclosure memory injection with per-observation token savings tracking**

From claude-mem: the ContextBuilder does not inject memory as a flat dump or a truncated window. It applies two rendering tiers based on recency. The most recent N observations (configurable via CLAUDE_MEM_CONTEXT_OBSERVATIONS) are rendered with their full narrative, facts, and file lists. Older observations are collapsed to compact table rows showing type, title, timestamp, and token count. The system then tracks two token metrics per observation: discovery_tokens (how many tokens the original tool output consumed) and read_tokens (how many tokens the compressed observation takes to inject), and reports the compression ratio in the context header.

This is specific, portable, and immediately useful for any n8n agent workflow that chains across runs. The two-tier structure means the agent always has full fidelity on recent context and compressed signal on older context, without a hard cutoff that would silently drop older work. The token tracking turns memory compression from a black box into an auditable metric.

## Session

Run URL: https://claude.ai/code/cse_015JiRKZpQzQWySMfPe4AbDa
