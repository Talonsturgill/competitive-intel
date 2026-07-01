**Most agent review loops fail for one boring reason. The critic can see the author's reasoning.** I watched an open source project called zeroshot fix this with a single move. The agent that writes the code and the agents that check it never share a context. Validators get the diff and the acceptance criteria. Nothing else.

That sounds small. It is not.

When a critic reads the author's justification, it inherits the author's blind spot. A confident wrong answer reads as correct because the story around it is coherent. Strip the story away and the reviewer has to reproduce the result cold. It either passes on evidence or it fails with a finding you can run yourself.

zeroshot scales the gate with risk. Trivial work ships with no review. Critical work faces five validators at once, each on its own axis, requirements, security, an adversarial pass. The merge waits for all of them to agree. A rejection is not a note. It is a reproducible failure routed back to the author for another pass.

The part most builders miss is not the second opinion. Everyone already has a critic step. It is what the critic is denied that makes the review honest.

I am porting this into our n8n workflows this week. The open thread is where blindness sharpens the review and where it only slows you down.
