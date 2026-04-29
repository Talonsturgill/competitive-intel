# LinkedIn Draft - Week of 2026-04-29

---

**Most generator-evaluator loops return the wrong response.** Not the worst one. Not a random one. The final one. And the final one is often not the best one. I found the fix this week reading fast-agent's source, and it comes down to one integer comparison per iteration.

The evaluator returns a structured object with a four-tier rating (POOR, FAIR, GOOD, EXCELLENT mapped to integers 0 through 3), a boolean called needs_improvement, and a list called focus_areas.

The part most builders miss is the best-response tracker. Every iteration, the framework compares the rating integer against a stored best. When the loop exits, it returns the stored best, not the final response.

That distinction matters. A generator that hits GOOD on iteration 2 can produce FAIR on iteration 3 if feedback is too broad and the generator overcorrects. Without the tracker, you return the degraded version.

The focus_areas field is the other piece worth copying. Instead of the full evaluation text, you pass only the list of specific things to fix next. Targeted instructions, not a paragraph of critique to interpret.

This maps to an n8n flow. One AI Agent node generates. One evaluates with JSON output. A Compare node updates the stored best. A Switch node on needs_improvement loops back with focus_areas or exits with the best stored text.

The pattern is not new. The implementation is unusually clean.

---

*Weekly teardown of trending agent repos.*
