**Most multi-agent systems are one failed step away from starting over.** I spent this week inside Microsoft Agent Framework, and the part that stuck was not the model support or the long provider list. It was what happens when a long agent run dies halfway through, because that is where most frameworks quietly fall apart.

Most of them treat a multi-agent run like a script. One tool call throws, one approval times out, and you replay the entire thing from the top. Tokens burned, state gone, trust right behind it.

Agent Framework treats the run like a state machine instead. It borrows a proven idea from large-scale graph processing and brings it to agents. Every step commits a snapshot of what just happened, what is still in flight, and what is waiting on a human. The run resumes from the last good point. It can also rewind to an earlier one and branch a different way.

The detail I keep turning over is what those snapshots are tied to. Not the run itself, which is the quiet choice that lets a saved state drop into a completely different run later.

That one decision turns a fragile agent pipeline into something you can pause, recover, and replay on purpose.

If you are building anything past a single prompt, this is the pattern to study.

Repo in the comments.
