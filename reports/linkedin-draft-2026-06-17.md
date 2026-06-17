**Most multi-agent frameworks make you draw the graph before you know the work.** I have spent months porting orchestration patterns into n8n, and the same wall shows up every time. You enumerate every node, every edge, every handoff, and you do it before the agents have run once. The plan is frozen the moment the goal shifts.

A TypeScript project called open-multi-agent flips that order. You hand a coordinator one plain goal and it builds the task graph at runtime, works out which steps depend on which, and runs the independent ones in parallel. The engineer describes the outcome, not the wiring.

The part I keep turning over is what they do with the plan once it exists. Most teams pay for that planning step on every run. This project lets you freeze the decomposition into plain JSON and replay the exact same graph later with no second planning call. The expensive reasoning becomes a cached artifact you can version and diff like any other file.

That is the move worth stealing. Stop rebuilding the plan on every run and start keeping it like the asset it already is.

Repo in the first comment.
