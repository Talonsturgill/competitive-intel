# Trending Agent Repos - Week of 2026-04-29

---

## DeerFlow - 64,211 stars

**Link:** https://github.com/bytedance/deer-flow

**Pitch:** ByteDance's production super-agent harness that orchestrates sandboxed sub-agents, an installable skills registry, and a layered memory queue behind a FastAPI gateway with multi-channel IM support.

**Stack:** Python 3.12+ (backend), TypeScript / Node.js 22+ (frontend), LangGraph, LangChain, Docker, SQLite + vector store, optional LangSmith / Langfuse tracing

**Architecture pattern:**
- Lead agent is a compiled LangGraph state graph; it holds the authoritative thread state and invokes sub-agents as tools rather than as nested graphs
- Sub-agents run in isolated thread pools (scheduler pool 3 workers, execution pool 3 workers) and return structured `SubagentResult` objects with status, trace ID, and full AI message history
- A three-layer middleware pipeline wraps every agent invocation: ClarificationMiddleware (asks before acting), DanglingToolCallMiddleware (closes unfinished tool calls), ToolErrorHandlingMiddleware (recovers gracefully from tool errors)
- Skills are installable packages loaded at startup via a registry + security scanner; each skill can expose MCP-compatible tools to both the lead agent and sub-agents
- Memory is queued per user, never blocking the main execution path, and is persisted to a pluggable store

**Reusable for me:**
- The three-layer middleware pattern maps cleanly to an n8n AI Agent node wrapping: a Switch node for clarification gating before execution, an Error Trigger branch for tool error recovery, and a Code node to close dangling outputs
- Sub-agent executor pattern (ThreadPoolExecutor with status enum) is directly portable as a parallel branch in n8n using the "Run Workflow" node with a wait-on-completion webhook
- The skills registry approach maps to n8n's credential + community node pattern: define a registry entry, scan for security issues, then auto-load the tool at startup
- Plan mode (generate a plan before acting) is the Writer-Critic split: implement in n8n as a two-step AI Agent call where step one writes the plan into a Set node variable before step two executes

**Skip if:** You need a model-agnostic foundation; DeerFlow is opinionated about LangGraph as the state layer and its sub-agent pattern assumes tight coupling to that graph runtime. Porting the core loop to a pure n8n workflow requires reimplementing state serialization.

---

## mem0 - 54,369 stars

**Link:** https://github.com/mem0ai/mem0

**Pitch:** A universal memory layer for AI agents that stores facts using a single-pass ADD-only extraction algorithm and retrieves them via a three-signal fusion of semantic vector search, BM25 keyword matching, and entity-linked boosting.

**Stack:** Python (core), TypeScript (SDK + Vercel AI SDK bridge), FAISS / Qdrant / pluggable vector stores, spaCy (NLP / BM25 lemmatization), SQLite (local metadata), optional self-hosted FastAPI server or cloud platform

**Architecture pattern:**
- Extraction is a single LLM call using the ADDITIVE_EXTRACTION_PROMPT; memories are ADD-only, nothing is ever overwritten or deleted, which means the store grows monotonically and conflicts are resolved at retrieval time rather than write time
- Entity extraction runs in parallel with fact extraction; entities are embedded separately and linked across memories so that retrieval can boost results that share entity matches with the query
- Retrieval fuses three scored signals: semantic cosine from the vector store, BM25 normalized to [0,1] via a logistic sigmoid with query-length-adaptive parameters (midpoint 5-12, steepness 0.5-0.7), and an entity-match boost of fixed weight 0.5
- The final score formula is `(semantic + bm25 + entity_boost) / max_possible` where the denominator adapts based on which signals are active (1.0, 1.5, 2.0, or 2.5), preventing active signals from inflating results above inactive-signal baselines
- Semantic gating runs before fusion: candidates scoring below the semantic threshold are dropped even if BM25 or entity boost would have rescued them
- Three entity scopes (user_id, agent_id, run_id) are enforced via filter objects, never top-level kwargs, so multi-tenant isolation is structural rather than convention-based

**Reusable for me:**
- The ADD-only write pattern is immediately portable to an n8n workflow: AI Agent node extracts facts, Code node appends to a JSON array in a database node (Postgres / Supabase), no update logic needed
- The three-signal retrieval loop can be approximated in n8n using an HTTP Request node to a vector DB, a Code node for BM25 scoring against stored lemmatized text, and a second Code node for entity matching and score fusion before the Switch node routes to the best result
- The semantic-gating-before-fusion rule is a single If node in n8n: drop candidates where `semantic_score < threshold` before any further processing
- Entity scoping (user_id / agent_id / run_id as filters) maps directly to n8n's workflow variables pattern; use Set nodes to inject scope before every memory read or write call

**Skip if:** Your agent interactions are short, single-session, and stateless. The BM25 and entity enrichment pipeline adds latency and storage overhead that only pays off at hundreds of memories per user.

---

## Google Agent Development Kit (adk-python) - 19,346 stars

**Link:** https://github.com/google/adk-python

**Pitch:** Google's code-first Python framework for building, evaluating, and deploying multi-agent systems with a built-in Plan-Re-Act planner, trajectory-based evaluation, session rewind, and pluggable MCP + A2A tool support.

**Stack:** Python, Google Generative AI SDK (Gemini-first, model-agnostic), FastAPI, Vertex AI Code Execution Sandbox, optional Vertex AI Agent Engine for deployment

**Architecture pattern:**
- The PlanReActPlanner injects a structured instruction into every LLM call and parses the response into tagged sections (PLANNING, REPLANNING, REASONING, ACTION, FINAL_ANSWER), ensuring the model commits to a plan before any tool call is emitted
- The LoopAgent runs sub-agents in sequence, tracking `times_looped` in agent state, and halts only when a sub-agent emits an `escalate` event or `max_iterations` is reached; this creates a controlled retry loop without unbounded recursion
- Tool calls can be gated by a HITL confirmation flow: a callback intercepts the function call event, pauses execution, and resumes only after explicit user approval
- The TrajectoryEvaluator scores agent runs against a reference tool-call sequence using one of three match types (EXACT, IN_ORDER, ANY_ORDER) and produces a per-invocation pass/fail score averaged across the eval set
- Session rewind allows rolling back to before any previous invocation, enabling automated retry-on-failure without re-running the full conversation
- The A2A (Agent-to-Agent) protocol over HTTP enables remote sub-agent delegation so agents in separate services can coordinate without sharing process memory

**Reusable for me:**
- The PLANNING tag pattern is directly portable to n8n: a first AI Agent node call with a "generate a plan before any tool call" system prompt writes the plan into a Set node, then a second AI Agent node executes against that plan
- The LoopAgent pattern maps to n8n's loop-until-done pattern using a Merge node feeding back into an AI Agent node, with a Switch node checking the `escalate` flag to break the loop
- The TrajectoryEvaluator is the most portable eval pattern here: store expected tool call sequences in a JSON file, replay agent runs through a Code node, compute match score with a simple ordered-list comparison, report via a webhook to a monitoring dashboard
- Session rewind maps to n8n's execution history: call the n8n API to re-run a specific past execution ID when the agent signals a failure condition

**Skip if:** You are not targeting Gemini or Vertex AI for deployment. The ADK's production deployment path (Cloud Run, Vertex AI Agent Engine) assumes Google Cloud, and the eval tooling has significant Vertex AI integration that does not lift cleanly to a provider-neutral stack.

---

## Top pattern of the week

**Three-signal memory retrieval with semantic gating and adaptive BM25 normalization (from mem0)**

mem0's retrieval algorithm is the sharpest pattern across all three repos this week. The specific insight: run three scoring signals in parallel (semantic cosine, BM25 keyword with query-length-adaptive sigmoid normalization, entity-match boost), gate all candidates against a minimum semantic threshold before fusion, then normalize the combined score against an adaptive denominator that accounts for which signals are actually active. This prevents artificially inflated scores when not all signals have data. The result is a retrieval layer that degrades gracefully: pure semantic when BM25 has no keyword overlap, pure semantic plus entity when the query is vague but entity-rich, and all three when the query is specific and verbose. Paired with the ADD-only write pattern (one LLM call, accumulate-only, resolve conflicts at read time), you get a memory system that is both low-write-latency and high-retrieval-quality without any merge logic.

In n8n terms: one Code node computes three scores, one If node gates on semantic threshold, one Code node fuses and normalizes, one Switch node routes to the result. The entire pattern fits in a four-node sub-workflow that any AI Agent node can call via the Execute Workflow node.

## Session

Run URL: https://claude.ai/code/session_01CqvdsaizzbpxpVFrnmP6fh
