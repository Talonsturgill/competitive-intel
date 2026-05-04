**The hardest thing in agent systems is not making the agent smarter.** It is knowing when a learned behavior is safe to keep. Most teams iterate on prompts by hand. One good run and they ship the change. Evolver, built by EvoMap, treats that as the failure mode it is.

Evolver is a Node.js evolution engine that encodes agent experience as Genes rather than skill documents. A Gene is a compact representation of what worked, extracted from git history and runtime logs, not written by a person after the fact.

A Gene that proves itself gets promoted to a Capsule. A Capsule is the unit that gets reused across sessions and shared with peer agents on the EvoMap hub.

But the promotion path is the architecture that matters. Three gates must clear before any Capsule advances.

First, an outcome score above 0.7. Second, a consecutive success streak, not just one good result. Third, a blast-radius check confirming the behavior touched fewer than five files and two hundred lines of code.

The streak gate is the one most builders miss. A single high-scoring run is noise. Two in a row is signal.

The arXiv paper behind this project ran 4,590 controlled trials and showed Gene encoding beats skill documents by almost 2x on hard reasoning tasks. That number is what makes this architecture worth a second read.
