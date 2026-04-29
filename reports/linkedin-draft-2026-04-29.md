# LinkedIn Draft - Week of 2026-04-29

---

**Most AI agents forget everything the moment the conversation ends. mem0 just shipped a retrieval algorithm that changes the math on that.** The write side is one LLM call. Facts accumulate. Nothing is ever overwritten. Conflicts resolve at read time, not write time.

The retrieval side is where the engineering lives.

Three scoring signals run in parallel. Semantic vector search finds the conceptual match. BM25 keyword scoring finds the lexical match, normalized via a sigmoid curve that adapts to query length. Entity matching adds a boost when retrieved memories share named entities with the query.

Before those signals combine, a hard gate runs first. If the semantic score does not clear a minimum threshold, the candidate is dropped. BM25 and entity boosts cannot rescue a semantically irrelevant result. That one rule prevents a whole class of retrieval bugs that naive hybrid search silently ships.

The fusion formula adapts its denominator to whichever signals are active. All three active means dividing by 2.5. Semantic alone means dividing by 1.0. Scores stay comparable whether a user has two memories or two thousand.

Four n8n nodes implement this entire pattern. The part builders keep missing is the semantic gate before fusion. That is the specific thing mem0 got right.
