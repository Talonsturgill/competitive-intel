**Most teams pay the context tax twice and never feel the second hit.** The trending repo this week is headroom, a compression layer that sits between your agent and the model and shrinks tool outputs, logs, and retrieved chunks by most of their size before the model reads a single token. Cutting the bill is the easy half. What headroom guards while it cuts is the part worth studying.

Cheap compression truncates. You trim context to fit a budget, lose whatever fell off the end, and recall quietly degrades. headroom treats the same job as routing and retrieval instead of a haircut.

It sends each payload to a compressor built for that content, so code is handled like code and dense JSON like JSON. It keeps every original cached and addressable, so any dropped span can be pulled back the moment a downstream step asks for it. And it holds the prompt prefix stable so the provider cache keeps hitting instead of resetting on every call.

I have watched this exact failure eat margin on live workflows. The obvious fix saves tokens and breaks two things nobody was watching, recall and the prompt cache.

The prefix-stability move is the one most builders skip, and it is the one that makes aggressive compression safe in production.

Read the repo before you write your own version.
