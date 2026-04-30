![Cover](linkedin-video-2026-04-30.mp4)

*Cover video. Upload as native LinkedIn video. Use linkedin-thumbnail-2026-04-30.png as the custom thumbnail.*

---

**Most retrieval systems fail not because the answer is missing but because the scoring formula treats all distance equally.** MemPalace published benchmarks this week that changed how I think about memory for AI agents. 96.6% recall at rank 5 on LongMemEval, zero API key, zero LLM calls.

The core formula is one expression. Fused distance equals semantic distance times one minus 0.30 times keyword overlap. Dense vector search combined with sparse keyword matching, no learned weights, no training data.

Three tiers, each activating only when the tier below fails. Tier one handles 96.6% locally. Tier two adds temporal proximity boosting and a two-pass approach for assistant-reference questions, reaching 98.4% without any API. Tier three sends the top-20 to a small model for one pick.

Content is typed at storage time into halls by content type. Preferences, facts, events, and assistant advice each get their own hall. A facts question searches only the facts hall before scoring begins. Hall-validated sessions get a 25% distance reduction in the final ranking.

What MemPalace got right is verbatim storage plus structural scoping over summarization. Every other memory system compresses the original content. This one keeps the raw text.

The benchmark failures are public. The wrong answers are in the repo. That transparency is the signal that matters most.
