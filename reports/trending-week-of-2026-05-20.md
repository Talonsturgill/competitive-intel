# Trending Agent Repos - Week of 2026-05-20

## MemTensor/MemOS - 9,211 stars

**Link:** https://github.com/MemTensor/MemOS
**Pitch:** MemOS is a memory operating system for LLM agents that provides a four-tier composable memory container (textual/graph, KV-cache, LoRA weights, preference) with an async Redis Streams scheduler for decoupled memory consolidation, served via FastAPI and an MCP server.
**Stack:** Python core; Neo4j + Qdrant/Milvus; Redis Streams or RabbitMQ; OpenAI, Azure, Qwen, DeepSeek, Ollama, vLLM, HuggingFace

**Architecture pattern:**
- Incoming queries fan out across all user-accessible MemCubes in parallel (ThreadPoolExecutor) searching Neo4j graph and Qdrant/Milvus vector stores simultaneously, with results injected into the LLM system prompt before the call
- Slow memory tasks (ingestion, graph updates, preference learning) are dispatched as typed events to a Redis Streams consumer group with xautoclaim for exactly-once delivery, fully decoupling memory writes from chat latency
- The DeepSearchAgent runs an iterative reflect-and-refine loop: a QueryRewriter rewrites the query, a ReflectionAgent assesses whether context is sufficient or missing_info, and the loop repeats up to max_iterations accumulating context across passes
- Four discrete memory tiers (textual/graph, activation/KV-cache, parametric/LoRA, preference) sit in one MemCube container with swappable backend adapters keyed on config strings, making provider switching a one-line change
- The MCP server wraps all memory operations via fastmcp, making the entire memory layer accessible to any MCP-compatible agent host without additional integration code

**Reusable for me:**
- Redis Streams task queue for decoupled memory consolidation maps directly to n8n: the AI Agent node dispatches to an n8n queue trigger, and a Code node runs the consolidation job asynchronously outside the chat loop
- The DeepSearchAgent reflect-and-refine loop is a 250-line standalone pattern that maps to an n8n sub-workflow with a Switch node (sufficient vs. needs_more) driving a retry loop
- The FastMCP-wrapped memory API becomes an MCP tool callable from any n8n MCP node with no custom integration
- The four-tier MemCube abstraction is a useful design pattern for partitioning agent memory without coupling to a specific database vendor

**Skip if:** Neo4j is a hard dependency for the textual memory tier; teams without an existing graph database need to treat MemOS as a sidecar service rather than port the code directly. The 28% minimum test coverage threshold signals that parts of the codebase are still maturing.

---

## SolaceLabs/solace-agent-mesh - 4,197 stars

**Link:** https://github.com/SolaceLabs/solace-agent-mesh
**Pitch:** Solace Agent Mesh is a Python framework that runs Google ADK agents as independent processes connected by a Solace event broker, enabling fully async multi-agent systems over the A2A protocol with progressive session compaction, peer delegation via injected tools, and an Argo-compatible DAG workflow executor.
**Stack:** Python; Google ADK, A2A SDK, Solace AI Connector, LiteLLM; SQLAlchemy with Alembic; FastAPI, APScheduler; any LiteLLM-compatible model provider (OpenAI, Anthropic, Vertex, Bedrock, Azure OpenAI)

**Architecture pattern:**
- A SamAgentComponent subscribes to a Solace topic and routes incoming A2A JSON-RPC messages to the Google ADK runner, which streams partial LLM events back to the broker as status updates visible in real time
- When the LLM calls a peer agent tool, the call is dispatched as a new A2A request to that peer agent's Solace topic; the originating task parks as long-running and resumes via a TTL-cache callback when responses arrive or a timeout fires a compensation message
- Before each LLM call, a before-model-callback injects live PeerAgentTool objects built from the current agent registry, sorted alphabetically to stabilize the prompt for provider-side caching; capability-scoped filtering removes tools the requesting user is not authorized to access
- When context overflows, a progressive compaction loop (up to 3 retries with per-session lock) runs an LlmEventSummarizer that writes a single compaction event re-summarizing old turns; ghost events are filtered on session read so the resumed session sees clean history
- The DAGExecutor runs YAML-defined prescriptive workflows with AgentNode, SwitchNode, LoopNode, and MapNode types, each backed by per-node retry logic with configurable exponential backoff modeled in Pydantic

**Reusable for me:**
- The progressive session compaction algorithm (summarize old turns into a single event, filter ghost events on read) is model-agnostic Python and directly portable to any n8n long-running chat workflow via a Code node that checks token count and rewrites session history
- The peer-delegation pattern maps to n8n's HTTP Request node: when an agent needs another agent, it posts to that agent's endpoint and awaits a webhook callback, exactly mirroring the Solace topic fire-and-park model
- The DAG workflow DSL (YAML-defined, Argo-compatible) is a reusable design for complex n8n multi-step orchestration; SwitchNode and MapNode concepts mirror n8n's own branching and split nodes
- Dynamic tool injection before model calls is directly applicable in n8n's AI Agent node via its tools parameter, filtered by user scope per request

**Skip if:** The entire transport layer is Solace-specific; every agent-to-agent call and status update travels over Solace topics via the SAC framework. Teams without a Solace broker cannot run SAM as-is and must extract individual patterns (compaction algorithm, DAG executor) as standalone code rather than adopting the framework.

---

## microsoft/agent-governance-toolkit - 1,593 stars

**Link:** https://github.com/microsoft/agent-governance-toolkit
**Pitch:** Microsoft's Agent Governance Toolkit is a runtime policy enforcement layer that intercepts every agent tool call before execution, evaluates it against declarative YAML/OPA/Cedar rules at sub-millisecond latency with a fail-closed default, and adds fingerprint-based MCP tool poisoning detection at registration time.
**Stack:** Python core (also TypeScript, Go, Rust, .NET SDKs); Pydantic, FastAPI, OpenTelemetry, Prometheus; no LLM provider dependency in the governance core; framework adapters for LangChain, CrewAI, AutoGen, OpenAI Agents SDK, Google ADK, LlamaIndex, Haystack, Dify, Flowise, pydantic-ai

**Architecture pattern:**
- Every agent tool call passes through a PolicyEvaluator before execution: the evaluator resolves priority-ordered rules from YAML, OPA Rego, or Cedar documents and returns allow/deny; if the evaluation engine itself errors, the result defaults to deny (fail-closed)
- A zero-trust identity layer issues Ed25519 + ML-DSA-65 agent credentials with 15-minute TTLs and auto-rotation; behavioral trust scores (0-1000) decay on policy violations and propagate through delegation chains, capping child agent trust at its parent's ceiling
- The MCP Security Gateway scans tool definitions at registration time, fingerprinting descriptions for hidden unicode characters, base64-encoded payloads, cross-server name typosquatting, and description drift (rug pulls), blocking poisoned tool definitions before any LLM ever sees them
- Four POSIX-inspired execution rings (kernel/supervisor/user/untrusted) isolate agent privilege levels; saga orchestration compensates failed multi-step workflows automatically; a kill switch signal terminates non-compliant agents immediately
- A Decision BOM reconstructs the full governance evidence chain from Merkle-chained append-only audit logs and exports CloudEvents to external SIEM systems

**Reusable for me:**
- The PolicyEvaluator is pure Pydantic with no LLM provider dependencies; wrapping it in a FastAPI sidecar creates a pre-execution governance hook that any n8n HTTP Request node can call before dispatching an AI Agent tool call
- The MCP Security Gateway is a standalone class that wraps any MCP tool registry without modifying it; directly applicable before any n8n MCP node registers tools in a workflow
- YAML policy files enable version-controlled governance rules that live in the repo alongside the workflow definition, not embedded in an LLM system prompt where the model can be prompted to ignore them
- The fail-closed default is the single design choice most worth copying: a governance gate that silently passes on engine error is not a governance gate

**Skip if:** This is a Public Preview project with documented breaking change warnings before GA; the default sandbox rules are marked illustrative rather than hardened and must be customized before production use. Sandbox enforcement sits at the Python interpreter boundary, not the OS kernel, so container-level isolation must be layered on separately.

---

## Top pattern of the week

Interception-first declarative policy gate with fail-closed default. The Agent Governance Toolkit's PolicyEvaluator accepts any agent action as a plain context dict, evaluates it against priority-ordered YAML, OPA/Rego, or Cedar rules at 35,000 operations per second with 0.012ms p50 latency, and defaults to deny if the evaluation engine itself errors. The MCP variant adds a second gate at tool registration time: a fingerprint scanner that detects hidden unicode characters, base64-encoded instructions, cross-server name typosquatting, and description drift before any poisoned tool definition reaches an LLM. The entire governance layer carries no dependency on any LLM provider SDK and wraps existing tool registries without modifying them, making it portable to any agent runtime including n8n MCP nodes via a thin FastAPI sidecar.

## Session

Run URL: https://claude.ai/code/cse_01QHxRE6VVBd42jUn7a7s5Po
