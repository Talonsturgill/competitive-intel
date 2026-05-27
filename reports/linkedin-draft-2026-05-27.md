**The hardest problem in agentic systems is not generating the answer. It is giving the agent the right context at the right cost.** thedotmack/claude-mem crossed 78,000 stars this week by solving exactly that problem in a way builders can actually port.

The architecture is a sidecar observer that watches every tool call in a live session and runs a second LLM to extract structured observations, each typed (discovery, bugfix, decision, change), each with a narrative summary and a list of files touched.

But the injection logic is what makes this worth studying.

When a new session starts, the system uses a two-tier model. The most recent N observations render in full. Older observations collapse to compact table rows showing type, title, timestamp, and token count. The system also tracks discovery_tokens versus read_tokens per observation and reports the compression ratio in the context header.

This maps directly to what n8n's AI Agent node needs when chaining across workflow runs. Store structured observations in a database node after each agent step. Inject recent items in full, older items as compact summaries, and track the token cost of both.

Most memory implementations dump everything or nothing. This one found the middle, and the mechanism it uses to get there is the insight worth carrying forward.
