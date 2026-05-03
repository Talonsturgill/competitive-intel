**Most builders treat the agent loop as one indivisible thing.** Pydantic-ai just proved it has four distinct layers, each independently swappable. The decision that stuck from this week's teardown was not the type safety or the eval harness. It was the capability ordering system.

The loop runs as a graph. User prompt in, model request out, tool calls handled, output validated, then repeat or exit. What pydantic-ai adds is four named interception slots sitting outside that graph.

WrapRunHandler controls the entire run. WrapModelRequestHandler controls what reaches the model. WrapToolExecuteHandler controls what happens when a tool fires. WrapOutputValidateHandler decides whether to accept the output or retry.

Each capability declares which slot it occupies and its order relative to others at that slot. You can stack Thinking, WebSearch, and a custom output critic without any of them knowing the others exist.

I built this pattern before without a vocabulary for it. Every pre-processing Code node before an AI Agent node in n8n is a WrapModelRequestHandler. Every output validation step after the agent returns is a WrapOutputValidateHandler.

Once you see the loop as four independent interception points, you stop trying to control everything from inside the system prompt. Each layer gets one job. The system prompt stops doing overtime.

That is what pydantic-ai got right.
