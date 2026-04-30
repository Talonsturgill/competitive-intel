# Trending Agent Repos - Week of 2026-04-30

## NousResearch/hermes-agent - 126,030 stars
**Link:** https://github.com/NousResearch/hermes-agent
**Pitch:** A self-improving AI agent with a closed learning loop that creates skills from experience, improves them during use, and builds a persistent user model across sessions.
**Stack:** Python 3.11, prompt_toolkit, Rich, SQLite (FTS5), ChromaDB, Honcho; model-agnostic via OpenAI-compatible APIs (Nous Portal, OpenRouter, NVIDIA NIM, OpenAI, Hugging Face, and more)
**Architecture pattern:**
- Core conversation loop (`run_agent.py::AIAgent.run_conversation`) iterates tool calls against an OpenAI-format message list with iteration budget and interrupt checks; tools are auto-discovered via `tools/registry.py` at import time
- Skills system stores procedural memory as markdown files; slash commands inject skills as user messages (not system prompt) to preserve prompt caching; skills autonomously self-improve after complex tasks
- Three-layer memory: session SQLite with FTS5 full-text search plus LLM summarization for cross-session recall, pluggable external memory providers (honcho, mem0, supermemory, byterover, hindsight), and a Honcho dialectic user model that deepens over time
- Gateway layer multiplexes a single agent across Telegram, Discord, Slack, WhatsApp, Signal, and more via platform adapters with a shared slash-command registry
- Cron scheduler delivers natural-language automations to any platform; subagent delegation spawns isolated child agents for parallel workstreams

**Reusable for me:**
- Tool registry auto-discovery pattern (tools register themselves at import time) maps cleanly to n8n's Code node calling HTTP Request nodes by name
- Skill injection as user message preserves LLM prompt caching; n8n AI Agent node system prompt cache slot can replicate this: keep system prompt stable, inject skill content in first user turn
- Multi-memory provider ABC (`agent/memory_provider.py`) with `sync_turn`, `prefetch`, `shutdown` lifecycle is a clean interface to port as an n8n sub-workflow that runs on every AI Agent turn
- FTS5 session search with LLM summarization is reproducible in n8n with a SQLite Code node plus a summarization AI Agent node chained before context injection

**Skip if:** You need a standalone library or API; Hermes is an interactive agent harness, not a composable SDK. The 12k-LOC AIAgent class is deep-coupled to its TUI and gateway; porting the whole loop is not worth it. Mine the patterns, not the code.

---

## MemPalace/mempalace - 50,469 stars
**Link:** https://github.com/MemPalace/mempalace
**Pitch:** Local-first AI memory that stores conversations verbatim in a hierarchical palace structure and retrieves them with a three-tier pipeline reaching 99.4% recall at rank 5 on LongMemEval.
**Stack:** Python 3.9+, ChromaDB (pluggable), SQLite (knowledge graph), sentence-transformers (local embedding model, ~300 MB); zero API key required for base tier
**Architecture pattern:**
- Verbatim storage: conversations are stored as-is, never summarized or paraphrased; the index is hierarchical with halls (content type), closets (sessions), and drawers (individual turns)
- Tier 1 retrieval (96.6% R@5, zero LLM): semantic ChromaDB query over top-50 candidates, then keyword overlap re-ranking using fused distance formula `dist * (1.0 - 0.30 * overlap)` with stop-word filtering
- Tier 2 adds temporal proximity boost (up to 40% distance reduction for sessions near parsed date offset) and two-pass assistant-reference retrieval (user-turn index to find sessions, full-text index for within-session search)
- Tier 3 adds an optional LLM re-rank pass: top-20 sessions sent to a small model (Haiku) with a minimal prompt asking for a single best session number; gracefully degrades if API is unavailable
- 29 MCP tools expose reads, writes, knowledge-graph operations, cross-wing navigation, and agent diaries; each specialist agent gets its own wing and diary, discoverable at runtime via `mempalace_list_agents`
- Pluggable backend ABC (`mempalace/backends/base.py`) with typed `QueryResult` and `GetResult`; drop in any vector store without touching retrieval logic

**Reusable for me:**
- The three-tier retrieval pipeline is directly portable to n8n: Tier 1 as an HTTP Request node to ChromaDB with a Code node for keyword re-scoring, Tier 2 as a Code node parsing temporal offsets and applying date-proximity scoring, Tier 3 as an optional AI Agent node that reads the top-20 snippets and returns one index
- The hall classification (content typed as preferences, facts, events, assistant advice, general) maps to n8n Switch nodes routing writes to separate ChromaDB collections; queries are pre-classified to narrow the search pool before the main retrieval
- Preference extraction via regex patterns producing synthetic documents is a zero-cost way to bridge vocabulary gaps; implement as a Code node that runs at storage time against each user message
- The `mempalace wake-up` CLI command (loads recent context for a new session) is a pattern for n8n's session-start webhook trigger: query recent memories and prepend to the AI Agent node's initial system context

**Skip if:** You need real-time streaming memory or high-frequency write throughput; MemPalace's indexing is batch-oriented and the local embedding model adds latency per write. Also skip if your memory scope is a single session only; this is built for cross-session recall.

---

## ComposioHQ/agent-orchestrator - 6,665 stars
**Link:** https://github.com/ComposioHQ/agent-orchestrator
**Pitch:** A TypeScript orchestration layer that spawns parallel AI coding agents each in an isolated git worktree, auto-routes CI failures and review comments back to the responsible agent, and surfaces everything in a single dashboard.
**Stack:** TypeScript/Node.js 20+, tmux (runtime isolation), GitHub/Linear/GitLab (trackers), 7-slot plugin architecture; agent-agnostic (Claude Code, Codex, Aider, Cursor)
**Architecture pattern:**
- Each issue spawns an isolated agent session in its own git worktree and branch; the worktree is the unit of isolation, preventing agents from stepping on each other's file edits
- Reaction system in `agent-orchestrator.yaml` maps events (ci-failed, changes-requested, approved-and-green) to actions (send-to-agent, notify, auto-merge); CI failure logs are forwarded directly to the responsible agent session without human routing
- Orchestrator agent runs as its own process reading the same YAML config and issuing `ao spawn`, `ao attach`, `ao list` CLI commands; it is itself an AI agent that manages other agents, not a deterministic scheduler
- Plugin slots (runtime, agent, workspace, tracker, SCM, notifier, terminal) are TypeScript interfaces implemented and exported as `PluginModule`; lifecycle stays in core, behavior varies by plugin
- Hash-based namespacing derives a unique 12-char prefix from the config file path; worktree and session names include the hash to prevent collisions across multiple orchestrator checkouts on the same machine

**Reusable for me:**
- The reaction YAML schema (event + action + retries + escalateAfter) is a direct pattern for n8n's webhook-triggered workflow: a GitHub webhook fires an n8n HTTP trigger, a Switch node routes by event type, and each branch calls the appropriate sub-workflow (retry agent, notify human, auto-merge)
- The worktree isolation pattern (each agent gets its own filesystem context) maps to n8n's execution isolation: each AI Agent node execution gets a fresh context object, preventing state bleed between parallel runs
- The orchestrator-as-agent pattern (an AI agent issuing CLI commands to manage other agents) is portable as an n8n AI Agent node with tools that call other n8n workflow execute nodes via the Execute Workflow node
- The escalateAfter timeout pattern (escalate to human after N minutes of no resolution) maps to n8n's Wait node followed by a conditional check node

**Skip if:** You are not running a software development workflow where git, CI, and pull requests are the primary feedback loop. This is a coding-agent orchestrator; it does not generalize to research, data, or content pipelines without significant plugin work.

---

## Top pattern of the week

**MemPalace three-tier memory retrieval: semantic-first with keyword-temporal fusion scoring and optional LLM rerank, achieving 99.4% R@5 on LongMemEval with zero API key at the 96.6% base tier.**

The specific insight is the fusion formula at tier 1: `fused_distance = semantic_distance * (1.0 - 0.30 * keyword_overlap)`. This single expression combines dense vector search with sparse keyword matching without any learned weights, no training data, and no added dependencies. Tier 2 adds a temporal proximity reduction (up to 40% for sessions matching a parsed date offset) and a two-pass approach for assistant-reference questions (user-turn index to find sessions, full-text index to search within them). Tier 3 is a single LLM call that picks the best session from the top-20 and gracefully degrades if the API is unavailable.

The hierarchy (halls typed by content, closets per session, drawers per turn) adds a scoping layer that narrows the semantic search pool before scoring begins. A preference question searches only the preferences hall. A facts question searches only the facts hall. The final ranking is always score-based; hall navigation is a boost, not a filter. This architecture delivers a 25% distance reduction for hall-validated sessions on top of the base hybrid scoring, which is why palace mode and hybrid v3 both converge at 99.4% despite being structurally different.

For n8n: implement as a three-node chain: (1) HTTP Request to ChromaDB returning top-50 with a Code node applying keyword re-scoring, (2) Code node applying temporal and hall-type boosts, (3) optional AI Agent node picking the single best from top-20. The hall classification lives in a Switch node that routes writes to separate ChromaDB collections at storage time.

## Session
Run URL: https://claude.ai/code/session_01EA6MeaeJbMAzeuoUuc1nB8
