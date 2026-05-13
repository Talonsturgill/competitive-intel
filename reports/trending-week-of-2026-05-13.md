# Trending Agent Repos - Week of 2026-05-13

## VectifyAI/PageIndex - 30,962 stars

**Link:** https://github.com/VectifyAI/PageIndex
**Pitch:** Vectorless RAG that builds a hierarchical tree index from long documents and uses LLM reasoning to traverse it for retrieval, replacing cosine similarity with goal-directed structural tree search.
**Stack:** Python, LiteLLM (model-agnostic), PyMuPDF, PyPDF2; cloud tier via API and MCP server at pageindex.ai
**Architecture pattern:**
- Index phase: LLM reads PDF pages and builds a hierarchical tree of section nodes, each storing title, page range, and a generated summary
- Retrieval phase: the tree (with text stripped out to save tokens) is passed to a second LLM call that reasons over the structure to identify relevant node IDs
- Fetch phase: only the targeted pages are retrieved and passed as context to the answer LLM
- Agentic mode: three tool functions (get_document, get_document_structure, get_page_content) wrap the pattern into a tool-calling loop compatible with any agents SDK
- Concurrent processing: ThreadPoolExecutor drives parallel title-verification calls during index construction

**Reusable for me:** The two-pass pattern (index once, retrieve per query) fits directly in n8n. An HTTP Request node calls the PageIndex API for the document tree; an AI Agent node receives the compact JSON tree and reasons over it to pick section node IDs; a second HTTP Request fetches only those pages; a final AI Agent node answers with only the relevant context. The pattern eliminates the vector database entirely for structured documents. The MCP server makes this callable as a tool from any Claude agent session.

**Skip if:** Documents are unstructured prose with no section hierarchy (news articles, email threads, chat logs). The tree index assumes meaningful navigational structure. Vector RAG still wins on flat corpora.

---

## Yeachan-Heo/oh-my-claudecode - 33,643 stars

**Link:** https://github.com/Yeachan-Heo/oh-my-claudecode
**Pitch:** Multi-agent orchestration layer for Claude Code that routes tasks through typed worker pools (Haiku/Sonnet/Opus), coordinates via tmux panes with file-based inbox/outbox messaging, and executes a staged pipeline from planning through verification.
**Stack:** TypeScript, Node.js, tmux (worker spawning), SQLite via better-sqlite3 (persistence), vitest; supports Claude, Codex, and Gemini workers
**Architecture pattern:**
- Worker registry: agents spawn into named tmux panes, register with heartbeat files, and are discovered via a registration manifest; liveness checked by heartbeat timeout
- Inbox/outbox messaging: each worker has a JSONL outbox the orchestrator tails; leader pushes instructions to worker inboxes; files rotate on size threshold
- Task file system: each task is a JSON file with status (pending/in-progress/completed/failed), dependency list, and a failure sidecar for retry tracking
- Allocation policy: tasks are matched to worker tiers by complexity score and current load; dependency-aware ordering ensures blockers resolve before dependents start
- Event-driven v2 runtime: replaced polling watchdog with lifecycle transitions and heartbeat-based liveness checks, eliminating sleep-based polling
- Staged pipeline: team-plan, then team-prd, then team-exec, then team-verify, then team-fix (cycles up to N times)

**Reusable for me:** The inbox/outbox JSONL pattern maps directly to n8n: each worker is an AI Agent node, the inbox is a shared data store (Redis or filesystem), and the orchestrator is a Switch plus Loop combination. The allocation policy (route by task complexity to different model tiers) translates to n8n Switch node routing AI Agent calls to Haiku, Sonnet, or Opus endpoints. The heartbeat liveness check gives any n8n workflow a retry signal without polling.

**Skip if:** Work is sequential and deterministic. The coordination layer adds overhead only justified when tasks are truly independent and parallelizable. For linear n8n pipelines the built-in sequential execution is simpler and faster.

---

## daytonaio/daytona - 72,416 stars

**Link:** https://github.com/daytonaio/daytona
**Pitch:** Open-source infrastructure runtime that spins up isolated OCI/Docker sandbox computers in under 90ms for AI-generated code execution, with stateful snapshots, multi-language SDKs, and an MCP server for agent tool use.
**Stack:** TypeScript (API, dashboard), Go (CLI, runner, daemon), NestJS (REST API entry point); SDKs for Python, TypeScript, Go, Ruby, Java; three-plane architecture across interface, control, and compute planes
**Architecture pattern:**
- Sandbox lifecycle: each sandbox is a full composable computer (dedicated kernel, filesystem, network stack, vCPU, RAM, disk) provisioned in under 90ms via REST API or SDK
- Daemon architecture: a Go daemon runs inside each sandbox handling process execution, filesystem operations, terminal sessions, and LSP; communicates back via the runner toolbox API
- Stateful snapshots: snapshot-manager orchestrates point-in-time captures so agent sessions restore to exact state; enables pause and resume across workflow steps without rebuilding from scratch
- Three-plane separation: interface plane (CLI, SDK, API), control plane (orchestrates sandbox operations), compute plane (runner nodes that execute sandboxes); each plane independently scalable
- MCP server integration: agents provision and control sandboxes via the Daytona MCP server, making sandbox creation a tool call rather than infrastructure configuration
- Network controls and volume mounting: sandboxes can be network-restricted for safety, with explicit volume mounts for shared state between agent steps

**Reusable for me:** The snapshot pattern is directly applicable to long-running n8n workflows: save sandbox state after expensive setup steps, restore before each agent tool-use step to avoid rebuilding environments. The SDK-first model means any n8n Code node can create and destroy sandboxes programmatically (pip install daytona plus API key). The MCP server means Claude agents in n8n's AI Agent node can self-provision code execution environments as tool calls. The three-plane separation is a reusable pattern for any n8n workflow that provisions external compute.

**Skip if:** You only need to execute short, stateless scripts. The sandbox provisioning overhead is not justified for sub-second operations. For simple code eval a plain Code node is sufficient.

---

## Top pattern of the week

**Two-pass document retrieval: index structure first, then retrieve by reasoning over the index.**

PageIndex builds a hierarchical tree of a document's natural sections (titles, page ranges, LLM-generated summaries), strips the text content out to save tokens, passes the compact tree to a second LLM call that reasons over the index to identify relevant node IDs, then fetches only those targeted pages. This replaces cosine similarity search with structure-aware goal-directed tree traversal, and achieves 98.7% accuracy on FinanceBench versus best-in-class vector RAG systems.

The portable pattern for n8n: index phase as a one-time HTTP Request to the PageIndex API (or a custom Code node that builds the tree); retrieval phase as an AI Agent node that receives the tree JSON and returns node IDs; fetch phase as an HTTP Request for only the targeted pages; answer phase as a final AI Agent node with only the relevant context injected.

What makes this reusable beyond PageIndex is the core separation: the indexing problem and the retrieval problem are different problems, and handling each with a distinct LLM call that does a different job is the architectural move that produces the accuracy gain.

## Session

Run URL: https://claude.ai/code/$CLAUDE_CODE_REMOTE_SESSION_ID
