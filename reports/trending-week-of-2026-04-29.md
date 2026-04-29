# Trending Agent Repos - Week of 2026-04-29

**Selection rationale:**
- JackChen-me/open-multi-agent: Only TypeScript-native orchestrator that auto-decomposes goals into task DAGs at runtime rather than requiring pre-declared graphs, with just 3 runtime dependencies and native MCP support.
- bytedance/deer-flow: Ground-up 2.0 rewrite of a top-trending SuperAgent harness with a two-tier memory architecture that is unusually well-engineered and directly portable.
- evalstate/fast-agent: The only framework with a typed four-tier quality rating loop that tracks best-response-across-iterations, not just the final output, and supports full MCP including Sampling and Elicitations.

---

## open-multi-agent - 5,966 stars
**Link:** https://github.com/JackChen-me/open-multi-agent
**Pitch:** Give it a goal in one function call and a coordinator agent decomposes it into a parallel task DAG, assigns work to a typed team, and synthesizes the final result.
**Stack:** TypeScript 5.6, Node.js 18+, 3 runtime deps (Anthropic SDK, OpenAI SDK, Zod), 9 native LLM adapters, MCP via connectMCPTools()

**Architecture pattern:**
- `runTeam(team, goal)` spins up a temporary coordinator agent that emits a task DAG from the goal string rather than requiring the developer to declare the graph up front
- `isSimpleGoal()` heuristic (complexity regex patterns + 200-char length ceiling) short-circuits coordinator overhead for trivial prompts and routes direct to single-agent execution
- `TaskQueue` tracks dependency state; `Scheduler` assigns tasks using one of four strategies: round-robin, least-busy, keyword capability-match, or dependency-first BFS critical path
- `AgentPool` caps concurrency at 5 by default; failed tasks mark themselves failed and leave dependents permanently blocked without halting unrelated branches
- Pluggable `MemoryStore` (InMemoryStore by default, swap to Redis/Postgres by implementing the interface); `onProgress` events and `onTrace` spans feed an HTML dashboard rendering the executed DAG

**Reusable for me:**
- The coordinator-decomposes-at-runtime pattern ports cleanly to n8n as a single AI Agent node that outputs a JSON task list, followed by a Code node that fans out to parallel HTTP Request nodes calling downstream AI Agent nodes
- The `dependency-first` scheduler is a direct model for a Switch node that gates which AI Agent node to activate next based on which task would unblock the most downstream work
- The `isSimpleGoal()` complexity heuristic is worth porting verbatim as a Code node guard before any orchestration flow to avoid unnecessary token spend on straightforward requests

**Skip if:** You need checkpointed resumption after failure, human-in-the-loop mid-DAG, or a Python stack. This is TypeScript-only and state is in-process by default.

---

## deer-flow - 64,206 stars
**Link:** https://github.com/bytedance/deer-flow
**Pitch:** ByteDance's ground-up SuperAgent harness orchestrates sub-agents, sandboxed code execution, extensible skills, and a two-tier memory layer that persists across sessions.
**Stack:** Python 3.12+, LangGraph, LangChain, FastAPI, Next.js frontend, Docker deployment, LangSmith/Langfuse tracing

**Architecture pattern:**
- Lead agent receives a goal and spawns sub-agents via skill invocations; sandboxed file system and bash tool isolate execution from the host
- `MemoryMiddleware` wraps each LangGraph agent via `AgentMiddleware.after_agent()`; after each turn it filters the message list to keep only user inputs and final assistant responses (tool calls stripped), then enqueues that filtered conversation for async memory update with 30-second debounce to batch rapid interactions
- Memory update pipeline detects correction and reinforcement signals in the filtered messages to prioritize how extracted facts are weighted before writing
- Structured memory stores in a versioned JSON schema with six temporal buckets: `user.workContext`, `user.personalContext`, `user.topOfMind`, `history.recentMonths`, `history.earlierContext`, `history.longTermBackground`; facts list is confidence-gated at 0.7 threshold with a 100-fact ceiling
- At inference time, memory injects up to 2000 tokens back into the system prompt; per-user and per-agent memory files are isolated by path convention
- Skills live in `.agent/skills/` (private) and `skills/public/`; message gateway routes across WeChat, Slack, Discord, Telegram, and others without touching the agent logic

**Reusable for me:**
- The `filter_messages_for_memory()` pattern (strip tool calls, keep only human and final AI turns) is the single highest-value thing to copy into any n8n memory node built with a Code node; it prevents tool-call noise from polluting the summary LLM's input and significantly cuts token cost
- The six-bucket temporal schema (`recentMonths`, `earlierContext`, `longTermBackground`) directly maps to three n8n memory HTTP Request payloads at different TTLs written after each AI Agent node execution
- The correction/reinforcement signal detection maps to a Switch node that tags an incoming user message as corrective before routing to the memory update branch, so corrections get written immediately rather than waiting for debounce

**Skip if:** You want a lightweight drop-in library. This is a full-stack application with a FastAPI backend, a Next.js frontend, and Docker orchestration. Porting specific patterns is easy; running it as-is is a commitment.

---

## fast-agent - 3,759 stars
**Link:** https://github.com/evalstate/fast-agent
**Pitch:** A Python framework for building and evaluating agents with first-class MCP support and a typed evaluator-optimizer loop that tracks the best-rated response across all refinement iterations, not just the final one.
**Stack:** Python, uv, Pydantic, native Anthropic/OpenAI/Google providers, TensorZero for 60+ additional models, ACP support alongside MCP

**Architecture pattern:**
- Agents and workflows are declared with Python decorators (`@fast.agent`, `@fast.evaluator_optimizer`, `@fast.iterative_planner`); the framework wires composition at startup
- `EvaluatorOptimizerAgent.generate_impl()` runs a loop: generator produces a response, evaluator returns a structured `EvaluationResult` (Pydantic model with `rating: QualityRating`, `feedback: str`, `needs_improvement: bool`, `focus_areas: list[str]`), the loop exits when `needs_improvement` is False or `max_refinements` is reached
- Best-response tracking uses `QUALITY_RATING_VALUES` (POOR=0, FAIR=1, GOOD=2, EXCELLENT=3) to compare across iterations and retain the highest-rated response, not the final one, preventing degradation from over-refinement
- `IterativePlanner` decouples planning from execution with a `plan_iterations` ceiling; agents execute each plan step, then the planner revises before the next round
- Full MCP support including Sampling and Elicitations; Streamable HTTP transport with OAuth and diagnostic tooling; ACP adapter lets any fast-agent setup expose as an ACP service

**Reusable for me:**
- The `EvaluationResult` schema (rating enum + needs_improvement bool + focus_areas list) is worth adopting verbatim in any n8n evaluator-optimizer flow: the AI Agent node that acts as evaluator outputs this JSON, a Switch node reads `needs_improvement`, and a Set node passes `focus_areas` as context to the next generator invocation
- Best-response tracking across iterations (not final-response-wins) is a concrete fix for n8n flows where a mid-loop response is highest quality but subsequent refinements degrade it; implement with a Compare node on the rating int value and a Set node that preserves the best text
- The `refinement_instruction` override param (custom prompt for the refinement turn) maps directly to a separate system prompt in the n8n AI Agent node on the loop-back path, letting each refinement iteration have different instructions than the initial generation

**Skip if:** You need a production server, a persistent backend, or multi-user isolation out of the box. fast-agent is primarily a developer toolkit and evaluation platform, not a deployable service.

---

## Top pattern of the week

**Typed quality-gated refinement with best-response-across-iterations tracking and structured focus signals**

fast-agent's `EvaluatorOptimizerAgent` solves the most common failure mode in generator-evaluator loops: the final iteration is not necessarily the best one. The evaluator returns a Pydantic model with a four-tier ordinal rating (POOR=0 through EXCELLENT=3), a boolean exit gate (`needs_improvement`), and a `focus_areas` list that tells the generator exactly what to fix next. The loop tracks the numerically highest-rated response seen across all iterations and returns that one, not the last one.

This matters because refinement loops can degrade. A generator that produces a GOOD response on iteration 2 can produce a FAIR one on iteration 3 if the evaluator's feedback is too broad. Tracking best-by-rating-int prevents that regression without requiring the developer to manually save checkpoints.

The `focus_areas` field is what makes the feedback actionable rather than decorative. Instead of "improve clarity," the evaluator returns `["trim the second paragraph", "add a concrete example in section 3"]`, and those strings get injected into the next generator prompt. The generator receives targeted instructions, not a vague critique.

In n8n, this ports as four nodes: an AI Agent node (generator), an AI Agent node (evaluator) with a schema-constrained JSON output, a Compare node that checks `rating_int > stored_best_rating_int` and updates a stored best, and a Switch node on `needs_improvement` that either loops back with `focus_areas` appended to the generator's input or exits with the best-stored response.

## Session
Run URL: https://claude.ai/code/$CLAUDE_CODE_REMOTE_SESSION_ID
