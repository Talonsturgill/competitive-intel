# editorial-kinetic-type

A skill that produces 25-second 1080x1080 MP4s in the editorial kinetic-typography style. Anthropic-adjacent default theme, fully brand-themable.

See `SKILL.md` for the full invocation guide.

## What's in this directory

- `SKILL.md` — the skill spec, read by Claude when invoking
- `render_frames.py` — produces 750 PNG frames from a scene spec
- `synth_audio.py` — produces the 25-second WAV soundtrack
- `default_theme.json` — the cream/clay/ink baseline theme
- `example_specs/` — reference scene specs

## Local testing

The skill assumes the cloud sandbox environment (Claude Code Routines). To test locally:

```bash
cd .claude/skills/editorial-kinetic-type
pip install cairosvg numpy scipy
mkdir -p /tmp/frames /tmp/audio /tmp/output

# Render frames
python render_frames.py example_specs/mem0-retrieval.json /tmp/frames

# Synthesize audio
python synth_audio.py /tmp/audio/soundtrack.wav

# Mux
ffmpeg -y -framerate 30 -i /tmp/frames/frame_%05d.png -i /tmp/audio/soundtrack.wav \
  -c:v libx264 -profile:v baseline -level 3.1 -pix_fmt yuv420p \
  -crf 18 -preset medium \
  -c:a aac -b:a 128k -ar 44100 \
  -movflags +faststart -shortest \
  /tmp/output/video.mp4
```

Total time: ~90 seconds.

## Editing the visual identity

The structure (8 scenes, fixed timing, type sizes) should not be edited without a version bump. The places it IS safe to edit:

- `default_theme.json` — change the baseline colors
- Scene copy in any spec — within the character limits
- Any new theme JSON file passed at render time

## Editing the audio identity

The audio is part of the format identity. Do not edit `synth_audio.py` without a version bump. If you need different audio for a specific brand, create a new skill (`editorial-kinetic-type-instrumental-X`) instead of forking this one.

## Dependencies

- Python 3.9+
- cairosvg
- numpy
- scipy
- ffmpeg (system binary)
- Fonts: Bitstream Charter, DejaVu Serif, DejaVu Sans (preinstalled in the cloud sandbox)
