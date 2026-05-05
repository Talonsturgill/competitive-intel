**Most production AI agent runs fail mid-run and restart from the beginning. Pydantic-AI is the first framework I have seen that treats that as an architecture problem rather than a retry problem. The fix is one specific and replicable design choice.**

The team decomposes each run into three named, typed graph nodes. UserPromptNode, ModelRequestNode, and CallToolsNode each produce a persisted snapshot before handing off to the next. Attach DBOS, Prefect, or Temporal and a crash restarts from the last completed node, message history and tool results intact.

That distinction matters the moment an agent calls a paid API or writes to a database mid-run. Retry restarts the chain. Checkpoint-per-node resumes from exactly where the process stopped.

The pattern ports to n8n without an orchestrator. Map each of the three node types to a primitive. Write state to an external key after each step and skip completed steps on re-run.

The same repo ships a full eval harness with typed datasets, expected outputs, and time-series scoring built in.

What the team got right is naming the steps. Once the loop has named nodes, checkpoint logic, approval gates, and eval hooks become natural attachment points rather than afterthoughts. The architecture is not the novel part. The discipline of naming is.
