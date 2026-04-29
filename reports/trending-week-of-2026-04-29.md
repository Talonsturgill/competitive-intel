# Trending Agent Repos - Week of 2026-04-29

## mem0ai/mem0 - 54,414 stars

**Link:** https://github.com/mem0ai/mem0
**Pitch:** Universal memory layer for AI agents with a new adaptive three-signal retrieval algorithm published April 2026.
**Stack:** Python, TypeScript; vector stores (Qdrant, Chroma, OpenSearch, Pinecone, pgvector), spaCy for entity extraction, BM25Okapi, SQLite for local storage, Alembic for migrations; model-provider agnostic (OpenAI, Anthropic, Gemini, Ollama).
**Architecture pattern:**
- ADD-only memory extraction: single LLM call using `ADDITIVE_EXTRACTION_PROMPT`, no UPDATE or DELETE operations. Memories accumulate; conflict resolution is a retrieval problem, not a write problem.
- Dual vector store layout: a primary store holds memory embeddings keyed by entity scope (user_id, agent_id, or run_id); a separate entity store holds extracted entities (also as embeddings) linked back to memory IDs via `linked_memory_ids` arrays.
- Multi-signal retrieval fusion: three signals fire in parallel (semantic cosine via vector store, BM25 keyword via `BM25Okapi` on the in-scope memory corpus, entity-linked boost from entity store lookup). Results are combined additively and normalized by an adaptive divisor (1.0 to 2.5) that reflects which signals actually fired.
- Adaptive BM25 sigmoid normalization: raw BM25 scores are sigmoid-normalized with a midpoint that scales from 5.0 to 12.0 as query token count grows from 1-3 to 15+ terms, preventing over-weighting of longer queries.
- Semantic threshold gate: the semantic cosine score must clear a configurable floor (default 0.1) before BM25 or entity boost can influence the combined score. Candidates below threshold are excluded entirely, preventing noise compounding across signals.

**Reusable for me:**
- Three-signal memory retrieval as an n8n pattern: HTTP Request node to vector store (semantic), Code node for BM25 normalization with adaptive sigmoid, Code node to query entity store and compute boost, Code node to gate on semantic threshold and fuse scores. Four nodes replicate the full scoring loop.
- ADD-only memory write: use an AI Agent node with a single extraction prompt and no deduplication logic. Simplifies the write path substantially versus update-and-merge approaches.
- Entity-linked retrieval boost: store a separate entity collection in the same vector DB, query it in parallel on each retrieval call, add a fixed boost weight (0.5 in mem0) to candidates whose entity IDs appear in results. Implementable as a second HTTP Request node in parallel with the main semantic query.
- Scoped memory filters: the user_id/agent_id/run_id filter pattern maps directly to n8n's expression system. Scope each memory lookup by the active workflow context variable.

**Skip if:** You need deduplication or memory correction. The ADD-only model works when the agent can override via downstream context injection, not via memory rewriting. If your agent needs to update stored facts (user changed address, preference reversed), this model requires additional resolver logic at read time.

---

## bytedance/deer-flow - 64,252 stars

**Link:** https://github.com/bytedance/deer-flow
**Pitch:** Open-source super agent harness built on LangGraph that orchestrates a lead agent, composable middleware stack, subagents, and sandboxed skill execution.
**Stack:** Python 3.12+, Node.js 22+, LangGraph, LangChain; Docker for sandboxed execution; supports OpenAI, Anthropic, Google, DeepSeek, Qwen, Ollama; optional LangSmith or Langfuse tracing.
**Architecture pattern:**
- Lead agent with middleware composition: `_build_middlewares()` assembles an ordered chain: ClarificationMiddleware, TodoMiddleware (plan mode), MemoryMiddleware, DeerFlowSummarizationMiddleware, SubagentLimitMiddleware, LoopDetectionMiddleware, ViewImageMiddleware, TitleMiddleware, TokenUsageMiddleware. Each concern is isolated in its own class and can be enabled or disabled via config.
- Summarization-triggered memory flush: `memory_flush_hook` is registered as a `BeforeSummarizationHook`. When the summarization middleware fires (configurable token trigger), it writes the current conversation state to the memory store before truncating. Memory is consistent with the window, not the full history.
- Subagent delegation with skills isolation: the lead agent can spawn subagents via tool call. Each subagent runs with an explicit set of available skills, separate sandbox, and independent token budget tracked by `SubagentLimitMiddleware`.
- Skill packaging and security scanning: skills are installable archives with a `security_scanner.py` gate. Skills run inside a sandboxed file system with a `FileOperationLock` to prevent race conditions on shared artifacts.
- DeerFlowClient as embedded harness: `DeerFlowClient` wraps the full agent stack as a Python object, usable without a server process. Supports streaming via SSE-compatible event types aligned with LangGraph protocol.

**Reusable for me:**
- Middleware composition pattern: each n8n workflow concern (memory, loop detection, summarization, subagent routing) can be modeled as a sub-workflow called in sequence. Use a Switch node to route based on middleware outcomes (needs clarification, loop detected, subagent needed).
- Memory-before-summarization hook: before any context compaction step in an n8n AI Agent node, fire an HTTP Request to write the current conversation to memory. Prevents the memory store from lagging the active context.
- SubagentLimitMiddleware concept: use a Code node to track subagent call counts per run and throw a hard stop if exceeded. Prevents runaway delegation trees in long-horizon workflows.

**Skip if:** You are not on LangGraph. The middleware stack is tightly coupled to LangGraph's agent middleware protocol. Porting individual middlewares to a different framework requires rewriting the middleware interface. The skill packaging system is Docker-first and assumes containerized execution.

---

## aaif-goose/goose - 43,546 stars

**Link:** https://github.com/aaif-goose/goose
**Pitch:** Linux Foundation-governed, Rust-based general-purpose AI agent with MCP-native tool routing, automatic context compaction, and a recipe system for declarative task execution with retry logic.
**Stack:** Rust, with TypeScript UI (desktop app, web); 15+ model providers via ACP and direct API; 70+ MCP extensions; rmcp for MCP protocol; Tokio async runtime; OpenTelemetry tracing.
**Architecture pattern:**
- MCP-native extension routing: all tools load as MCP extensions via `ExtensionManager`. Each call routes through `ToolConfirmationRouter` (permission check), then through `AdversaryInspector` and `EgressInspector` (security layers), then to `tool_execution.rs`. Extensions can be loaded at runtime without restart.
- Automatic context compaction at threshold: `check_if_compaction_needed` triggers when context fills to 80% of provider token limit. `compact_messages()` batch-summarizes tool call pairs (10 per batch) via a separate LLM call, injects a continuation message, and the conversation continues without losing task state.
- Recipe-driven execution with retry: `Recipe` is a declarative task spec (instructions, success checks, retry config). `RetryManager` tracks attempt count; `RepetitionInspector` detects looping behavior. On failure, the agent re-runs from a fresh state up to `max_attempts`.
- Subagent spawning via tool call: `run_subagent_task()` creates a new `Agent` instance with its own recipe, tool set, session ID, and `CancellationToken`. Output is extracted as text and returned to the parent agent as a tool result. Subagents are fully isolated processes.
- Context compaction with skill preservation: similar to deer-flow, the compaction step preserves skill-related messages at configurable recent-N counts and token budgets to prevent skill context from being summarized away mid-task.

**Reusable for me:**
- Context compaction trigger pattern: in n8n, use a Code node to estimate token count from the message array, compare to a configured threshold (e.g., 80% of 128k), and route to a summarization sub-workflow via Switch node before continuing the agent loop.
- Recipe-as-workflow pattern: model each n8n workflow as a recipe with explicit success checks (a Code node that evaluates output against criteria) and a retry counter stored in a workflow variable. Retry by looping back to the AI Agent node with a reset context.
- MCP extension registry: use n8n's MCP node as the extension loader and route tool calls through a Switch node keyed on tool name. Mirrors goose's `ExtensionManager` dispatch logic.

**Skip if:** You need to modify the agent core. Rust adds a significant contribution barrier. The binary distribution model means customization is distro-level (via `CUSTOM_DISTROS.md`), not source-level for most teams. The recipe system assumes you can declare tasks upfront, which breaks down for highly dynamic workflows.

---

## Top pattern of the week

**Adaptive three-signal memory retrieval with semantic threshold gating (mem0, April 2026)**

The specific pattern: semantic cosine search gates candidates at a configurable similarity floor (default 0.1), removing irrelevant memories before any additional scoring runs. BM25 keyword score is then computed over the in-scope memory corpus and normalized using a query-length-adaptive sigmoid (midpoint scales from 5.0 to 12.0 as query grows from 1-3 to 15+ tokens, steepness steps down from 0.7 to 0.5). Entity boost is added from a parallel vector entity store query, weighted at 0.5. The combined score divides by an adaptive max-possible (1.0 to 2.5) that reflects only the signals that actually fired. Final ranking is descending by combined score, truncated to top-k.

This pattern is worth copying because the semantic gate prevents noise compounding across signals, the adaptive BM25 normalization handles query length variance without a hyperparameter sweep, and the parallel entity store adds structured recall without changing the primary memory schema. All three components are independently implementable in n8n using HTTP Request, Code, and Switch nodes.

## Session

Run URL: https://claude.ai/code/session_01YDxGVUubdS4Nwg1JGpo4xQ
