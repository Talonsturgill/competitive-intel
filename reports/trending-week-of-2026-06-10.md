# Trending Agent Repos - Week of 2026-06-10

Three picks this week, chosen from 71 unique candidates surfaced across the
ai-agents, llm-agents, mcp, and multi-agent topics, all pushed within the last
seven days and over 100 stars, none already in covered-repos.txt.

Selection notes (one sentence each):
- **IBM/mcp-context-forge** picked for direct n8n-stack relevance as an MCP
  gateway plus genuine architectural novelty in federating many MCP servers
  behind one virtual endpoint with health-gated routing and a per-call plugin
  pipeline.
- **microsoft/agent-framework** picked for production-grade agent orchestration
  built on a typed superstep graph with checkpointing, which maps cleanly onto
  the n8n AI Agent node and Switch routing.
- **MemTensor/MemOS** picked for architectural novelty in a self-evolving memory
  layer with hybrid retrieval and a consolidation phase that reports real token
  savings, distinct from the simpler memory systems covered in prior weeks.

---

## IBM mcp-context-forge - 3859 stars
**Link:** https://github.com/IBM/mcp-context-forge
**Pitch:** A gateway and registry that federates many MCP, A2A, and REST or gRPC
backends into one unified MCP endpoint with central governance and observability.
**Stack:** Python 3.11 to 3.13 on FastAPI with SQLAlchemy and Alembic, a Rust
acceleration path for the hot proxy routes, Redis for caching and federation,
OpenTelemetry for traces. Model integration is provider agnostic through the MCP
and A2A protocols rather than a hardcoded SDK.
**Architecture pattern:**
- A registry service holds servers, tools, resources, and prompts with
  many-to-many associations, so any backend can be exposed as a virtual MCP
  server (mcpgateway/services/server_service.py, gateway_service.py).
- Every aggregated tool is namespaced in a server-scoped form so two backends
  that both expose a tool named search never collide downstream.
- A transport layer translates between stdio, SSE, WebSocket, and streamable
  HTTP at runtime, so a stdio-only server can be reached over HTTP without
  changes (mcpgateway/transports/).
- Periodic per-server health probes feed a liveness state, and routing skips a
  degraded backend before invocation rather than failing mid-call.
- A per-call plugin pipeline runs pre and post hooks on every tool invocation
  (tool_pre_invoke, resource_post_fetch) for things like PII scrubbing, header
  injection, caching, and circuit breaking (mcpgateway/plugins/).
**Reusable for me:** The federation idea ports straight into n8n. Stand up one
HTTP Request node that points at a single gateway URL instead of wiring a node
per MCP server, then use a Switch node keyed on a namespaced tool name to fan
out to the right backend. The pre and post hook pipeline becomes a pair of Code
nodes wrapped around the AI Agent node, one to scrub or inject before the call
and one to validate or cache after. The health-gated routing becomes a small
scheduled workflow that pings each backend and writes a status flag the Switch
node reads, so a dead service is dropped before the agent ever calls it.
**Skip if:** You only talk to one or two MCP servers. The gateway earns its keep
at five or more backends with shared auth and observability needs. Below that the
registry, RBAC, and tenant layers are overhead you will not use.

---

## microsoft agent-framework - 11214 stars
**Link:** https://github.com/microsoft/agent-framework
**Pitch:** A Python and .NET framework for orchestrating multi-agent workflows as
a typed graph of executors with checkpointing and provider flexibility.
**Stack:** Python 3.10 plus and C#, Pydantic 2 for typed messages, OpenTelemetry
for tracing, MCP client support. Providers include Azure OpenAI and Foundry,
OpenAI, Amazon Bedrock, Google Gemini, Anthropic, Mistral, and Ollama through
optional subpackages.
**Architecture pattern:**
- Work is modeled as executors with decorated handler methods that receive typed
  messages and emit to peers via send_message or yield workflow output
  (python/packages/core/agent_framework/_workflows/).
- Execution runs in supersteps. Each iteration runs every eligible executor
  concurrently and the step converges when no new messages are in flight.
- Edges carry optional conditions, so routing between executors is decided at
  runtime by a callable on the message, which is type-checked against the target.
- A WorkflowBuilder fluent API assembles the directed graph, and higher-level
  builders wrap it for sequential, concurrent, handoff, and group-chat patterns.
- Checkpoint storage captures executor state, in-transit messages, and shared
  state at superstep boundaries, so a run can pause and resume across restarts.
**Reusable for me:** The handoff and group-chat builders are the parts worth
copying. A triage agent that auto-routes to specialists maps onto an AI Agent
node feeding a Switch node, where each branch is a specialist AI Agent node. The
superstep convergence rule is a clean mental model for an n8n loop that keeps
cycling agents until no branch produces new work. The conditional edge becomes a
Switch condition on the agent output, and the checkpoint idea becomes writing run
state to a data store node between steps so a long workflow survives a restart.
**Skip if:** You want a thin function-to-node mapping. Wrapping plain code as an
executor needs a subclass, and serialized checkpoints are versioned by a graph
signature that does not survive structural changes to the graph. The framework is
worth it for stateful multi-agent runs, not for a single linear chain.

---

## MemTensor MemOS - 9700 stars
**Link:** https://github.com/MemTensor/MemOS
**Pitch:** A memory operating system for LLM agents that unifies persistent
storage, hybrid retrieval, and async scheduling behind one MemCube container.
**Stack:** Python 3.10 plus, Qdrant or Milvus for vectors, Neo4j or Postgres for
the memory graph, embedders from OpenAI, Ollama, or sentence-transformers, an
HTTP BGE reranker, and Redis or RabbitMQ for the scheduler. Models include
OpenAI, Azure, Qwen, DeepSeek, and local vLLM.
**Architecture pattern:**
- A MemCube is the unit of memory and holds textual, activation, and parametric
  memory under one API (src/memos/mem_cube/).
- Retrieval is hybrid and runs graph lookup, vector similarity, and BM25 lexical
  search in parallel, then merges and deduplicates by memory id
  (src/memos/memories/textual/tree_text_memory/retrieve/recall.py).
- A scheduler routes ingestion and consolidation work to label-based thread
  pools over Redis Streams, so writes can be async without blocking the agent.
- A consolidation phase, named the dream module, binds related memories into
  context nodes and extracts reusable skill priors offline (src/memos/dream/).
- A reranker stage reorders the merged candidate set before returning the top k.
**Reusable for me:** The async write path is the takeaway. In n8n, the agent does
not wait on memory ingestion. An AI Agent node returns to the user while a Code
node pushes new memories onto a queue that a second workflow drains and
consolidates on a schedule. Retrieval becomes an HTTP Request node to a single
search endpoint that already fuses vector and lexical results, so the AI Agent
node gets ranked context without three separate lookups. The dream-style nightly
consolidation maps onto a cron-triggered n8n workflow that compresses and
deduplicates the day's memories.
**Skip if:** You need sub-100ms retrieval over millions of items, or you cannot
run a graph database. Neo4j is required for the hierarchical memory and there is
no SQL-only fallback for graph traversal. For a small memory store the simpler
systems covered in prior weeks are less to operate.

---

## Top pattern of the week

**Federated MCP gateway with a namespaced virtual tool registry and
health-gated routing.** From IBM mcp-context-forge. The specific insight is not
"use a gateway." It is the three moves that make the gateway safe at scale. One,
every backend is registered as a virtual MCP server and each of its tools is
namespaced in a server-scoped form, so identical tool names across backends
never collide. Two, the gateway translates transports at runtime, so a stdio-only
server is reachable over streamable HTTP with no change to the server. Three,
periodic health probes maintain a liveness state and the router drops a degraded
backend before invocation, so the agent never calls a dead tool and the failure
surfaces at the gateway rather than mid-reasoning. The reusable shape is one
endpoint, a namespaced tool table, and a pre-invocation health gate.

## Session
Run URL: https://claude.ai/code/cse_01TRLLLjNSTTc9MoRnenaSqi
