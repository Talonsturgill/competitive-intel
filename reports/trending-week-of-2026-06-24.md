# Trending Agent Repos - Week of 2026-06-24

Survey method note. Direct `git clone` is blocked by this run's egress policy
(the git relay returns 403 for external repositories), so each repo below was
read through GitHub's raw and web file interface rather than a local checkout.
Architecture was reconstructed from README, package layout, design docs, and
entry-point source. The three picks below cleared every selection rule in
CLAUDE.md (over 100 stars, pushed within the window, not a wrapper, course,
awesome list, or training library, and not already in covered-repos.txt).

Why these three. headroom wins on architectural novelty (a compression layer
nobody else is shipping as a first-class agent primitive). MemOS wins on a
production memory design that goes well past plain vector recall. agent-framework
wins on production readiness signals (Microsoft, shipped to PyPI and NuGet,
typed graph orchestration). All three map cleanly onto the n8n stack.

## headroom - 49,234 stars
**Link:** https://github.com/headroomlabs-ai/headroom
**Pitch:** A context compression layer that shrinks everything an agent reads (tool outputs, logs, RAG chunks, files, history) by 60 to 95 percent before it reaches the model, while keeping the original retrievable on demand.
**Stack:** Python 3.10+ core with a Rust crate for the hot path, a TypeScript SDK, ONNX Runtime plus a HuggingFace text model for learned compression. Provider-agnostic across Anthropic, OpenAI, Bedrock, and Gemini. Ships as a library, an HTTP proxy, and an MCP server.
**Architecture pattern:**
- A ContentRouter inspects each payload and dispatches it to a compressor chosen by content type rather than running one generic squeezer over everything.
- SmartCrusher handles JSON, CodeCompressor does AST-aware compression per language, and Kompress-base runs a trained model over free text.
- CacheAligner stabilizes the prefix of the compressed output so the provider KV cache still hits instead of getting invalidated on every call.
- CCR (reversible compression) caches the original locally so a dropped span can be fetched back on demand, which makes the compression lossless when it matters.
- The same pipeline is exposed three ways, with the MCP server giving `headroom_compress`, `headroom_retrieve`, and `headroom_stats` as tools.
**Reusable for me:** This is a drop-in preprocessing node. In n8n I can put a Code node (or an HTTP Request node pointed at the headroom proxy) directly upstream of the AI Agent node, route by content type with a Switch node (JSON vs code vs prose vs log), and store the originals keyed by a content hash in a data store so a later step can retrieve the full text. The cache-alignment idea alone is worth porting: compress the variable tail, keep the system prefix byte-stable, and you stop torching the provider prompt cache on every run.
**Skip if:** You only ever pass short, already-tight prompts. The compression model and ONNX runtime add a real dependency and a few hundred milliseconds, which is dead weight if your payloads were never the cost driver.

## MemOS - 9,979 stars
**Link:** https://github.com/MemTensor/MemOS
**Pitch:** A memory operating system for agents that unifies store, retrieve, and manage across a layered, self-evolving memory rather than a single flat vector index.
**Stack:** Python core (`src/memos`) with a TypeScript app layer, a uvicorn REST API at `src/memos/api/server_api.py`, Neo4j for graph memory, Qdrant for vectors, FTS5 for full text, and Redis Streams for scheduling. Providers include OpenAI, Azure OpenAI, Qwen, DeepSeek, MiniMax, Ollama, HuggingFace, and vLLM. Ships Docker Compose and a Helm chart.
**Architecture pattern:**
- Memory is split into four tiers: L1 raw interaction traces, L2 learned policies and preferences, L3 a consolidated world model of the user, and a Crystallized Skills layer.
- Retrieval is hybrid, fusing FTS5 lexical search with vector recall so exact-string queries and fuzzy semantic queries both land.
- Skill crystallization promotes recurring patterns out of raw traces into reusable units, so a solved task does not get re-derived from scratch next time.
- A Redis Streams scheduler runs the consolidation and promotion work asynchronously, off the request path.
**Reusable for me:** The tiering is the takeaway. In n8n I do not need Neo4j to copy the idea: keep a short raw-trace table, a small policies table the agent writes deliberately, and a vector store for semantic recall, then have the AI Agent node read all three and a scheduled workflow promote stable patterns up a tier. The hybrid FTS plus vector fusion maps to running a Postgres full-text query and a vector query in parallel and merging, which is cheaper and more accurate than vector-only recall.
**Skip if:** You want a memory call you can stand up in an afternoon. The four-tier design plus Neo4j, Qdrant, and Redis is a lot of moving infrastructure, and most n8n memory needs are satisfied by two tiers.

## microsoft/agent-framework - 11,618 stars
**Link:** https://github.com/microsoft/agent-framework
**Pitch:** Microsoft's open, multi-language framework for production-grade agents and multi-agent workflows, spanning .NET and Python from one design.
**Stack:** Python and .NET, Pydantic for typed contracts, OpenAI and Azure OpenAI and Azure AI Foundry clients. Shipped to PyPI (`agent-framework`) and NuGet (`Microsoft.Agents.AI`). The agent is a thin wrapper over a chat client plus instructions plus tools.
**Architecture pattern:**
- The base unit is an agent: a chat client wrapped with instructions and typed Python function tools, run with an async `run()` call.
- Above single agents sit named orchestration patterns: Sequential, Concurrent, Group Chat, Handoff, and Magentic.
- The Magentic orchestrator is the standout, a planner-led loop that maintains a task ledger and reassigns work across specialist agents until the goal is met.
- Configuration resolves through a fixed priority chain (explicit Azure inputs, then OpenAI keys, then Azure environment), which keeps the same code running across local and cloud.
**Reusable for me:** The Handoff and Group Chat patterns are exactly the Writer Critic Editor shape, and they translate to an n8n layout where each role is its own AI Agent node and a Switch node routes on a handoff signal returned in the output. The Magentic task-ledger idea is portable as a small JSON ledger passed between nodes that records what is done, what is pending, and who owns each step, which is sturdier than chaining agents blind.
**Skip if:** You want one runtime. The .NET-plus-Python split is a strength for big shops and overhead for a Python-only n8n shop, and the orchestration patterns are more ceremony than a two-node Writer Critic chain needs.

## Top pattern of the week

Content-routed reversible compression with cache-aligned prefixes, from headroom.
The insight is not "compress the context." It is three moves stacked together.
First, route by content type and compress each kind with a compressor built for
it (AST for code, structural crushing for JSON, a trained model for prose)
instead of one lossy pass over everything. Second, keep the original cached
locally and addressable, so any compressed span can be expanded back on demand,
which turns lossy compression into lossless-when-asked. Third, hold the prompt
prefix byte-stable while only the tail varies, so the provider KV cache keeps
hitting instead of being invalidated every call. The combination is what makes
it safe to run in production: you get the token savings without losing fidelity
and without paying the cache-miss tax that naive truncation creates.

## Session
Run URL: https://claude.ai/code/cse_01QGj7yNF7zHsykLEAQBn6Y1
