# Competitive Intelligence Repo

This repo holds weekly trending agent repository teardowns and the LinkedIn drafts
they generate. The Trending Agent Repos routine writes here.

## Mission

Identify reusable architectural patterns from trending AI agent and automation
GitHub repositories that can be ported into Transform Labs n8n workflows. Generate
a LinkedIn teardown post draft from the top pattern of the week.

## Selection criteria for repos

Include only if all are true:
- More than 100 stars
- Last commit within the last 30 days
- Not a wrapper, course material, or "awesome list"
- Not a model training or fine-tuning library
- Not already in covered-repos.txt

Prefer repos that show:
- Architectural novelty over framework clones
- Production readiness signals (tests, CI, real docs)
- Direct relevance to n8n stack: MCP servers, agent orchestration,
  Writer Critic Editor patterns, evaluation harnesses

## Voice rules for any generated content

Hard fails (do not ship if any of these appear):
- Em dashes
- Semicolons
- Colons inside body sentences (titles and headers are fine)
- Emojis
- Questions as hooks
- Phrases: "Here's the thing", "We've spent 30 years", buzzwords like
  "leverage", "synergy", "unlock", "game-changer"

LinkedIn post format:
- 800 to 1400 characters
- First 250 characters must read as one continuous paragraph
  (no double line breaks before character 250)
- Bold declarative open
- Pattern recognition perspective from a builder POV
- Land on what the trending repo got right
- Tease the insight, do not give it away

## Output locations

- Pattern reports: reports/trending-week-of-YYYY-MM-DD.md
- LinkedIn drafts: reports/linkedin-draft-YYYY-MM-DD.md
- Covered repos log: covered-repos.txt (append only, owner/name format)

## Branch and PR convention

Routine writes to a branch named claude/trending-YYYY-MM-DD and opens a PR
against main. Never push directly to main.
