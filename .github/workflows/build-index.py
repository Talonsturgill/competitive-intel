#!/usr/bin/env python3
"""Generate an index.html listing every video HTML file in videos/.

Run from inside the videos/ directory. Writes to stdout.
"""
import os
import sys
from datetime import datetime, timezone

EXCLUDE = {"index.html"}

def title_from_filename(name: str) -> str:
    base = os.path.splitext(name)[0]
    return base.replace("-", " ").replace("_", " ")

def main() -> int:
    files = sorted(
        f for f in os.listdir(".")
        if f.endswith(".html") and f not in EXCLUDE and os.path.isfile(f)
    )

    items = "\n".join(
        f'      <li><a href="{f}"><span class="t">{title_from_filename(f)}</span>'
        f'<span class="f">{f}</span></a></li>'
        for f in files
    ) or '      <li class="empty">no videos yet</li>'

    built = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    sys.stdout.write(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>competitive-intel · videos</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;600;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0A0A0B;
    --fg: #F5F5F4;
    --dim: #6E6E72;
    --line: #1E1E22;
    --accent: #7C5CFF;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    background: var(--bg);
    color: var(--fg);
    font-family: "Inter Tight", system-ui, sans-serif;
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
  }}
  main {{
    max-width: 720px;
    margin: 0 auto;
    padding: 80px 24px 120px;
  }}
  .kicker {{
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    letter-spacing: 0.18em;
    color: var(--dim);
    text-transform: uppercase;
    margin-bottom: 18px;
  }}
  h1 {{
    font-weight: 800;
    font-size: 44px;
    letter-spacing: -0.02em;
    line-height: 1.05;
    margin-bottom: 14px;
  }}
  h1 em {{ font-style: normal; color: var(--accent); }}
  p.lede {{
    color: var(--dim);
    font-size: 16px;
    line-height: 1.5;
    margin-bottom: 48px;
    max-width: 50ch;
  }}
  ul {{
    list-style: none;
    border-top: 1px solid var(--line);
  }}
  li a {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 24px;
    padding: 22px 4px;
    border-bottom: 1px solid var(--line);
    color: var(--fg);
    text-decoration: none;
    transition: background .2s, padding .2s;
  }}
  li a:hover {{
    background: linear-gradient(90deg, transparent, rgba(124,92,255,0.06), transparent);
    padding-left: 12px;
  }}
  li a:hover .t {{ color: var(--accent); }}
  .t {{
    font-size: 18px;
    font-weight: 600;
    text-transform: capitalize;
    transition: color .2s;
  }}
  .f {{
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    color: var(--dim);
  }}
  li.empty {{
    padding: 40px 4px;
    color: var(--dim);
    font-family: "JetBrains Mono", monospace;
    font-size: 13px;
    border-bottom: 1px solid var(--line);
  }}
  footer {{
    margin-top: 64px;
    font-family: "JetBrains Mono", monospace;
    font-size: 10px;
    color: var(--dim);
    letter-spacing: 0.1em;
  }}
</style>
</head>
<body>
<main>
  <div class="kicker">competitive-intel</div>
  <h1>video <em>teardowns</em></h1>
  <p class="lede">Animated explainers built from the trending agent repo routine. Each one runs in a 9:16 frame, ready to screen-record for export.</p>
  <ul>
{items}
  </ul>
  <footer>built {built}</footer>
</main>
</body>
</html>
""")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
