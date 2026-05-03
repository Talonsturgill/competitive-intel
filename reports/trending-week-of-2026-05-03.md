# Trending Agent Repos - Week of 2026-05-03

## pydantic/pydantic-ai - 16,813 stars
**Link:** https://github.com/pydantic/pydantic-ai
**Pitch:** A Python agent framework from the Pydantic team that brings type-safe, graph-based agent execution with composable capability wrappers and a built-in eval harness.
**Stack:** Python, pydantic_graph, OpenTelemetry (Logfire), supports OpenAI / Anthropic / Gemini / 20+ providers; MCP and A2A protocol built in
**Architecture pattern:**
- Agent execution runs as a typed graph: UserPromptNode -> ModelRequestNode -> CallToolsNode, looping until an End node is reached
- Capabilities are composable interception units that each wrap exactly one handler slot: WrapRunHandler, WrapModelRequestHandler, WrapToolExecuteHandler, or WrapOutputValidateHandler
- Capabilities have an explicit ordering (CapabilityPosition: before/after each node) so stacking WebSearch, Thinking, and ProcessHistory never collides
- Structured outputs are validated by Pydantic schemas at the CallToolsNode boundary before the loop continues, turning schema failures into retry signals rather than exceptions
- AgentSpec (YAML/JSON) lets you declare an agent entirely without code; pydantic_evals provides a dataset-driven eval harness that plugs into the same graph and emits OTel spans to Logfire

**Reusable for me:**
- The capability stacking pattern maps directly to n8n's Code node chain before the AI Agent node: one Code node injects the thinking budget, another filters tool schemas, another validates structured output. Each is independently replaceable.
- AgentSpec in YAML mirrors n8n's workflow-as-config philosophy. A team could maintain an agents.yaml file and hydrate it into the AI Agent node via the Code node at runtime.
- pydantic_evals' scorer + dataset pattern is portable as an n8n sub-workflow that feeds test cases into the AI Agent node via HTTP Request and compares outputs in a Switch node.
- WrapOutputValidateHandler is the cleanest implementation of a Critic node I have seen: it sits between the model response and the agent's return value, can rewrite the output or trigger a retry, and requires zero changes to the base agent.

**Skip if:** You are not building in Python. The graph primitives are Python-only and the capability hooks require Pydantic's type system. Also skip if your agent needs to be defined in low-code without any Python scaffolding.

---

## SolaceLabs/solace-agent-mesh - 3,393 stars
**Link:** https://github.com/SolaceLabs/solace-agent-mesh
**Pitch:** An event-driven Python framework where specialized AI agents communicate over a Solace pub/sub event broker, with a DAG executor handling parallel fan-out, loop, and sub-workflow node types.
**Stack:** Python, Solace AI Connector (event broker), Google ADK for agent logic, asyncio DAG executor; supports REST, Slack, and custom gateways
**Architecture pattern:**
- Agents are decoupled services that publish and subscribe to topics on the Solace event mesh rather than calling each other directly; the orchestrator agent decomposes tasks and emits delegation events
- A DAG executor translates a workflow definition into a dependency graph; nodes can be AgentNode, SwitchNode, LoopNode, MapNode (parallel fan-out), or WorkflowInvokeNode (sub-workflow nesting)
- MapNode fans out one agent call per item in a list and collects results asynchronously, enabling parallel processing without a shared thread pool
- WorkflowExecutionContext tracks state across the DAG run so any node can read outputs from its dependency nodes by ID
- The config portal (frontend + backend) lets non-developers define agent workflows visually, which the DAG executor then runs

**Reusable for me:**
- The MapNode pattern maps exactly to n8n's SplitInBatches + parallel AI Agent nodes: one item in, one agent invocation, results merged. Replace the event broker with an HTTP Request node calling a webhook.
- WorkflowInvokeNode is the sub-workflow pattern n8n uses natively. The key insight here is that each sub-workflow gets its own WorkflowExecutionContext, so state isolation is structural rather than disciplinary.
- The orchestrator-as-event-publisher model (rather than orchestrator-as-direct-caller) maps to n8n's webhook trigger pattern: the orchestrator fires a webhook, the specialist agent workflow handles it, results come back via a response webhook. No synchronous blocking.
- SwitchNode with dependency-based branching maps to n8n's Switch node wired to downstream agent sub-workflows.

**Skip if:** You need zero infrastructure. Solace Agent Mesh requires a Solace broker (cloud or self-hosted). The event mesh adds reliability and scale but the setup cost is real. For single-agent use cases the broker is pure overhead.

---

## langwatch/better-agents - 1,516 stars
**Link:** https://github.com/langwatch/better-agents
**Pitch:** A CLI tool that scaffolds new agent projects with a versioned prompts directory, end-to-end scenario tests, evaluation notebooks, and pre-wired MCP configuration so every project ships with observability and testing from day one.
**Stack:** TypeScript CLI (npm), framework-agnostic scaffolding (supports Agno, Mastra, LangGraph, and others), Langwatch eval API, Scenario testing library, YAML prompt files
**Architecture pattern:**
- Project scaffold separates agent code (app/), prompts (prompts/ as YAML), scenario tests (tests/scenarios/), and evaluation notebooks (tests/evaluations/) into distinct directories with no cross-contamination
- Prompts are versioned YAML files tracked in a prompts.json registry; the coding assistant is told to read the registry before touching any prompt, creating a diff-friendly prompt audit trail
- Scenario tests simulate a full multi-turn conversation with the agent and assert on end-state behavior, not on individual token outputs
- Evaluation notebooks hold labeled datasets and offline scoring runs that measure a specific pipeline step (RAG retrieval quality, classification accuracy) independent of the full agent loop
- .mcp.json is pre-generated with the right MCP servers for the chosen framework, so the coding assistant knows the framework's APIs from the first message

**Reusable for me:**
- The prompts-as-YAML-with-registry pattern is directly portable to n8n: store system prompts in a Google Drive folder (one file per prompt version), read the active version via HTTP Request at workflow start, and log the version ID alongside every run output.
- Scenario tests as multi-turn conversation assertions translate to an n8n test sub-workflow that replays a fixed conversation script through the AI Agent node and checks the final output against expected values via a Code node.
- The evaluation notebook structure (dataset + scorer + results) maps to an n8n workflow that reads a CSV of test cases via HTTP Request, runs each through the AI Agent node, and writes pass/fail results to a Google Sheet.

**Skip if:** Your agent code is already structured and tested. This tool is most valuable at project start. Retrofitting the scaffold onto an existing repo requires manually reorganizing directories and rewriting import paths.

---

## Top pattern of the week

**Capability-ordered interception hooks on a typed agent graph.**

pydantic-ai's `capabilities` module defines four independent interception slots that wrap the agent execution graph: `WrapRunHandler` (outermost, controls the whole run), `WrapModelRequestHandler` (controls what gets sent to the model), `WrapToolExecuteHandler` (controls what happens when a tool fires), and `WrapOutputValidateHandler` (controls whether the model output is accepted or retried). Each capability declares which slot it occupies and what position it takes relative to other capabilities at that slot. The framework then stacks them in declared order before running the graph.

The portability insight for n8n is that this is not a framework feature. It is a design decision: split the agent loop into named interception points, make each one independently replaceable, and compose them without coupling. In n8n terms, a pre-model Code node is a `WrapModelRequestHandler`, an output schema Check node after the AI Agent is a `WrapOutputValidateHandler`, and a retry sub-workflow is a `WrapRunHandler`. The capability system names the pattern explicitly so builders stop jamming all this logic inside the system prompt or a single monolithic Code node.

## Session
Run URL: https://claude.ai/code/session_011jLj3r7wXcBf1m14VG2pzA
