---
name: editorial-kinetic-type
description: Generate a 25-second 1080x1080 MP4 in the editorial kinetic-typography style (Anthropic-adjacent visual language - cream and clay default, fully brand-themable). 8 punchy scenes of bold serif headlines on a soft background, ambient atmospheric audio with mallet hits on emphasis moments, no diagrams, no node graphs, no robots, no faces. Use when a LinkedIn or social post needs a modern educational video that reads like a magazine edit, not a SaaS explainer. Trigger especially when the user requests "modern," "Anthropic style," "editorial," "kinetic typography," or critiques an existing video as "old-looking" or "generic." Outputs a downloadable MP4, a GIF preview, a thumbnail PNG, and an MP3 of the soundtrack alone.
---

# editorial-kinetic-type

A skill that produces a 25-second 1080x1080 MP4 in the editorial kinetic-typography style. The visual language is intentionally minimal: a warm-paper background, deep-ink headlines in a high-contrast serif, a single accent color used sparingly, and a sans-serif used only for eyebrow labels and small italic copy. Audio is ambient electronic, not boom-bap. No drums. The only percussive elements are mallet bell hits on the emphasis moments.

This skill is the visual baseline. The colors, typography, and tonal copy are all parameters. The structure is fixed because the structure is what makes it work.

## When to use

Use this skill any time a LinkedIn or social post needs a video and the user wants a modern educational tone. Trigger words and contexts:

- "Anthropic style," "Stripe-like," "editorial," "modern," "kinetic typography"
- The user has critiqued a previous video as "old," "generic," "stock," "corporate"
- The post is a teardown, a pattern explanation, a contrarian take, or a builder's note
- The audience is engineers, designers, or technical operators (not marketing/sales)

Do NOT use this skill for:

- Product demos that require showing UI
- Architecture diagrams (use a node-graph skill instead)
- Anything that needs talking-head footage or stock video
- Posts longer than one focused idea (this format compresses to one takeaway)

## What you're producing

A directory of files saved to `<repo>/reports/` (or another output dir if specified):

- `linkedin-video-YYYY-MM-DD.mp4` — the deliverable, 1080x1080, ~900 KB, H.264 baseline + AAC, 25 seconds
- `linkedin-preview-YYYY-MM-DD.gif` — silent half-resolution GIF for in-chat previews and review
- `linkedin-thumbnail-YYYY-MM-DD.png` — frame from scene 5 (the strongest emphasis moment) for use as the LinkedIn upload custom thumbnail
- `linkedin-audio-YYYY-MM-DD.mp3` — the soundtrack alone in case the user wants to audition the audio independently
- `scene-spec-YYYY-MM-DD.json` — the input spec, saved alongside outputs for reference and re-runs

## Required inputs

Before invoking the renderer, you write a `scene-spec.json` with the eight scenes filled in. The spec is the only thing that varies per video. The skill ships a default theme; the spec can override it.

### Scene roles (fixed structure, do not reorder)

1. **Title** — `<headline>` (the topic) + `<eyebrow>` (small sans copy under it)
2. **Three things** — eyebrow label + 3 stacked items, each with a small italic descriptor
3. **The problem** — two-line statement, accent color on the second line
4. **The specific case** — three-line statement, accent on the middle line
5. **The fix** — primary statement (largest type in the video) + a secondary delayed line
6. **The mechanism** — three sequential lines describing how it works, accent on the punchline
7. **The consequence** — three-line statement that hammers the inverse of scene 5
8. **The close** — primary line + accent line + small italic subtitle

### Theme inputs

Either pass `theme: "default"` (cream/clay/ink, the baseline shown to the user) or supply a custom theme:

```json
"theme": {
  "background": "#F0EEE6",
  "ink": "#191919",
  "accent": "#CC785C",
  "muted": "#7C7C7C",
  "rule": "#D9D5C8",
  "serif": "'Bitstream Charter', 'DejaVu Serif', Georgia, serif",
  "sans": "'DejaVu Sans', sans-serif"
}
```

Color contract:
- `background` — the paper/canvas color, must be light enough for `ink` to read at AA contrast or better (4.5:1)
- `ink` — primary text, must contrast strongly against background
- `accent` — used on exactly one phrase per scene where used, never more
- `muted` — eyebrow labels and small italic descriptors only
- `rule` — the thin divider line under the eyebrow in scene 2

If the user gives you brand colors, you map them to these roles using this priority:
1. Brand background color → `background`
2. Brand primary text → `ink`
3. Brand accent / call-to-action color → `accent`
4. If only two brand colors are given, derive `muted` as a 50% blend of `ink` toward `background`, derive `rule` as a 90% blend
5. Always verify contrast. If `ink` on `background` is below 4.5:1, fall back to `#191919` ink or `#F0EEE6` background and tell the user

Typography contract:
- `serif` is a stack with at least 3 fallbacks. Always include `Georgia, serif` as the final fallback so any environment renders something.
- `sans` is a stack ending in `sans-serif`.
- Never load remote fonts. The renderer runs offline. Use only fonts present in the cloud sandbox: `Bitstream Charter`, `DejaVu Serif`, `Georgia`, `DejaVu Sans`, `DejaVu Sans Mono`.

### Copy rules (hard, no exceptions)

These rules come from the calibration that makes the format land. They apply to every line of text in the spec:

- No em dashes
- No semicolons
- No colons in body sentences (eyebrow labels and titles are fine)
- No emojis
- No questions
- No arrow characters (→ ← ↑ ↓). The available serif fonts in the cloud sandbox do not include glyphs for these and they render as missing. If you want to imply consequence, use a verb ("becomes resumable") or a period followed by a new line, not an arrow.
- Headlines max 22 characters per line, max 2 lines
- Emphasis lines max 18 characters
- Eyebrow labels are uppercase, small caps style, max 16 characters
- Italic descriptors max 24 characters
- The whole script across all 8 scenes should read in under 12 seconds when spoken silently. If you have to rush mentally, it's too dense.

Voice: pattern-recognition, builder's POV, declarative. No hedging. No "perhaps." No "it could be argued." If the user has a `write-like-X` skill committed to the repo, use it to draft the copy first, then trim to fit the character limits.

## Workflow

### Step 1: Read or create the scene spec

If a scene spec already exists at `<repo>/reports/scene-spec-YYYY-MM-DD.json`, read it. Otherwise, draft one from the source post or topic. Save to that path before proceeding.

Spec shape:

```json
{
  "date": "2026-04-29",
  "theme": "default",
  "scenes": {
    "title": {
      "headline": "Hybrid Retrieval",
      "eyebrow": "what mem0 just shipped"
    },
    "three_things": {
      "eyebrow": "THREE SIGNALS",
      "items": [
        {"name": "Semantic", "descriptor": "vector match"},
        {"name": "BM25", "descriptor": "lexical match"},
        {"name": "Entity match", "descriptor": "named entities"}
      ]
    },
    "problem": {
      "line_a": "Fusion alone",
      "line_b": "ships bugs.",
      "accent_line": "b"
    },
    "specific_case": {
      "line_a": "BM25 can rescue",
      "line_b": "a semantically wrong",
      "line_c": "match.",
      "accent_line": "b"
    },
    "fix": {
      "primary": "Gate first.",
      "secondary": "Fuse second."
    },
    "mechanism": {
      "line_a": "If the semantic score",
      "line_b": "is below threshold",
      "line_c": "→ drop.",
      "accent_line": "c"
    },
    "consequence": {
      "line_a": "BM25 can't rescue",
      "line_b": "what the gate",
      "line_c": "already dropped."
    },
    "close": {
      "primary": "Gate first.",
      "accent": "Fuse second.",
      "subtitle": "the part most builders miss."
    }
  }
}
```

### Step 2: Validate the spec

Before rendering, run these checks. Reject the spec and ask for corrections if any fail:

- Every text field passes the copy rules (em dash, semicolon, colon, emoji, question)
- Character limits met
- If `theme` is custom, contrast ratio of `ink` on `background` ≥ 4.5:1
- All required scenes present

### Step 3: Render frames

Call `render_frames.py` with the spec path and theme as arguments. The renderer produces 750 PNGs in a frames directory at 1080x1080.

The render takes 60-90 seconds in the sandbox.

### Step 4: Synthesize audio

Call `synth_audio.py`. The audio is fixed: ambient C major pad, sub drone on C2, white-noise swells at scene boundaries, mallet hits on scene 5 entrance and scene 8 entrances, soft UI ticks scattered for text-appearance moments, 60% master peak. Output is a 25-second stereo WAV.

The audio does NOT vary by theme. Brand colors change the visual; the soundtrack is part of the format identity.

### Step 5: Mux video + audio

Use ffmpeg to encode H.264 baseline + AAC into a single MP4. Settings are fixed and chosen for cross-platform compatibility (LinkedIn, Twitter, mobile browsers):

```bash
ffmpeg -y -framerate 30 -i frames/frame_%05d.png -i audio/soundtrack.wav \
  -c:v libx264 -profile:v baseline -level 3.1 -pix_fmt yuv420p \
  -crf 18 -preset medium \
  -c:a aac -b:a 128k -ar 44100 \
  -movflags +faststart -shortest \
  reports/linkedin-video-YYYY-MM-DD.mp4
```

### Step 6: Generate the secondary deliverables

```bash
# GIF preview (silent, half-res, for review surfaces that don't autoplay video)
ffmpeg -y -framerate 30 -i frames/frame_%05d.png \
  -vf "fps=20,scale=540:540:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4" \
  -loop 0 reports/linkedin-preview-YYYY-MM-DD.gif

# MP3 of the soundtrack alone
ffmpeg -y -i audio/soundtrack.wav -c:a libmp3lame -b:a 192k \
  reports/linkedin-audio-YYYY-MM-DD.mp3

# Thumbnail: pull a representative frame from scene 5
cp frames/frame_00420.png reports/linkedin-thumbnail-YYYY-MM-DD.png
```

### Step 7: Validate outputs

- MP4 size between 500 KB and 5 MB (smaller means render failed; larger means encoding settings drifted)
- MP4 duration is 25.0 seconds exactly
- All four deliverables exist at the expected paths
- Open the GIF inline in the response so the user sees the animation without downloading

### Step 8: Embed in the LinkedIn draft

If a LinkedIn draft markdown file exists at `<repo>/reports/linkedin-draft-YYYY-MM-DD.md`, prepend a media reference block:

```markdown
![Cover](linkedin-video-YYYY-MM-DD.mp4)

*Cover video. Upload as native LinkedIn video. Use linkedin-thumbnail-YYYY-MM-DD.png as the custom thumbnail.*

---

(existing draft content)
```

## Visual language reference

### Scene timing (fixed)

| Scene | Frames | Time |
|-------|--------|------|
| 1. Title | 0 to 90 | 0 to 3s |
| 2. Three things | 90 to 180 | 3 to 6s |
| 3. Problem | 180 to 270 | 6 to 9s |
| 4. Specific case | 270 to 360 | 9 to 12s |
| 5. Fix | 360 to 450 | 12 to 15s |
| 6. Mechanism | 450 to 540 | 15 to 18s |
| 7. Consequence | 540 to 630 | 18 to 21s |
| 8. Close | 630 to 750 | 21 to 25s |

Every scene has a 12-frame fade in (0.4s) and an 8-frame fade out (0.27s). Scene 5 gets a subtle scale-in on the primary line. Scene 8 holds longer because it carries the closing weight.

### Type sizing (do not improvise)

| Element | Size | Weight | Family |
|---------|------|--------|--------|
| Scene 1 headline | 110 | 700 | serif |
| Scene 1 eyebrow | 32 | 400 | sans |
| Scene 2 eyebrow | 26 | 600 | sans, letter-spacing 4 |
| Scene 2 item name | 64 | 700 | serif |
| Scene 2 descriptor | 22 | 400 italic | sans |
| Scene 3 lines | 96 | 700 | serif |
| Scene 4 lines | 64 | 400 (700 on accent) | serif |
| Scene 5 primary | 140 | 700 | serif |
| Scene 5 secondary | 64 | 400 italic | serif |
| Scene 6 lines | 56 (72 on accent) | 400 (700 on accent) | serif |
| Scene 7 line a | 70 | 700 | serif |
| Scene 7 line b/c | 56 | 400 (italic on c) | serif |
| Scene 8 primary/accent | 100 | 700 | serif |
| Scene 8 subtitle | 26 | 400 italic | sans |

These sizes are tuned for 1080x1080. Do not scale. If the brand uses a heavier or lighter serif, the weights still apply (700 = bold, 400 = regular).

### Animation tokens (do not improvise)

- Fade in: 12 frames, ease-out cubic
- Fade out: 8 frames, ease-out cubic
- Y-translate on intro: 8 to 14 pixels, resolves to 0
- Stagger between elements within a scene: 8 to 16 frames
- Scene 5 primary scale-in: 0.95 to 1.00 over 16 frames

## Audio language reference

The soundtrack is fixed in identity even when the visual theme changes. The full composition:

- **Pad layer 1**: Cmaj9 chord (C-E-G-B-D), stacked sines with subtle detune, slow LFO breathing at 0.12 Hz, 3-second attack, 4-second release
- **Pad layer 2**: C-G fifth one octave down for warmth, slower LFO at 0.09 Hz
- **Sub drone**: C2 sine + 2nd harmonic, very slow tremolo at 0.13 Hz
- **Scene transition swells**: bandpass white noise (600 Hz to 8 kHz), 1.2 second crescendo peaking at the cut, soft sub thump on the boundary
- **Mallet bells**: at 12.0s (scene 5 enter, C5+G4), 21.0s (scene 8 enter, C5+E5), 22.5s (scene 8 second beat, G5)
- **UI ticks**: high-passed noise bursts at text-appearance moments (around 0.6, 3.4, 3.8, 4.1, 4.4, 6.4, 9.4, 15.4, 15.8, 16.4, 18.4 seconds)
- **Master**: gentle tanh saturation, 13 kHz low-pass, subtle band-passed air noise floor, 2.5-second outro fade, peak normalized to 0.6

The mallet hits are the only intentional sync points. They land precisely on the entrance of the largest type moments. If you're tempted to add a kick drum, don't. The format gets its energy from typography pacing, not percussion.

## What "good" looks like

Do this:
- Trim copy aggressively. Each scene says one thing.
- Use the accent color exactly once per scene where it's used. More than once dilutes it.
- Let scene 5 be the loudest visual beat. Don't compete with it.
- Match the user's brand colors exactly when supplied. If they say "our blue is #1234AB," use #1234AB, not what you think a better blue would be.

Do not do this:
- Stretch the format past 25 seconds. The pacing is part of the identity.
- Add background music with vocals or melody. The pad is meant to recede; vocals don't recede.
- Use stock typography (Helvetica, Arial). The serif is what makes it editorial.
- Replace the white-noise swells with whoosh sound effects. Whooshes signal YouTube tutorial; swells signal magazine-quality production.
- Add the brand wordmark to the outro frame. The outro is for the takeaway. Branding goes in the LinkedIn post body, not the video.

## File map

```
.claude/skills/editorial-kinetic-type/
├── SKILL.md                     (this file)
├── render_frames.py             (renders 750 SVG frames to PNG via cairosvg)
├── synth_audio.py               (synthesizes the 25-second soundtrack)
├── default_theme.json           (the cream/clay/ink baseline)
├── example_specs/
│   ├── mem0-retrieval.json      (the original example)
│   └── README.md                (notes on how to adapt the example)
└── README.md                    (developer notes for editing the skill itself)
```

## Failure handling

- Renderer fails to produce 750 frames: stop, show the user the frame count actually produced, and inspect the spec for invalid characters
- ffmpeg fails to encode: usually means a frame is missing, re-run the renderer
- Audio fails to synthesize: ship the video silent and tell the user, do not block the deliverable
- Theme contrast check fails: tell the user which color failed and why, fall back to default theme for that property only

## Versioning notes

- The visual structure (8 scenes, fixed timing) is v1.0 and should not change without a version bump.
- The audio composition is v1.0 and should not change without a version bump.
- Themes and copy can be edited freely without versioning.
- If a future version changes structure or audio, save the old version as `editorial-kinetic-type-v1` and create the new one alongside it.
