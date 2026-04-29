#!/usr/bin/env python3
"""
editorial-kinetic-type frame renderer.

Reads scene-spec.json and theme.json (or default_theme.json), produces 750
PNG frames at 1080x1080 in an output directory.

Usage:
    python render_frames.py <spec.json> <output_dir> [--theme theme.json]
"""

import argparse
import json
import math
from pathlib import Path

import cairosvg

# ---- canvas ----
W, H = 1080, 1080
FPS = 30
TOTAL_FRAMES = 750


# ---- easing ----
def ease_out_cubic(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def lerp(a, b, t):
    return a + (b - a) * t


def clamp01(v):
    return max(0.0, min(1.0, v))


# ---- SVG primitives ----
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(content, x, y, size, color, weight=400, family="serif",
         opacity=1.0, anchor="middle", letter_spacing=0, italic=False):
    style = 'font-style:italic;' if italic else ''
    ls = f' letter-spacing="{letter_spacing}"' if letter_spacing else ''
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="{family}" font-size="{size}" font-weight="{weight}" '
        f'fill="{color}" opacity="{opacity:.3f}" style="{style}"{ls}>{esc(content)}</text>'
    )


def rect(x, y, w, h, fill, opacity=1.0):
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'fill="{fill}" opacity="{opacity:.3f}"/>'
    )


def svg_doc(content, theme):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
        f'<rect width="{W}" height="{H}" fill="{theme["background"]}"/>'
        f'{content}'
        f'</svg>'
    )


# ---- transitions ----
def scene_envelope(frame_in_scene, total_frames, fade_in=12, fade_out=8):
    if frame_in_scene < fade_in:
        return ease_out_cubic(frame_in_scene / fade_in)
    if frame_in_scene > total_frames - fade_out:
        out_frame = frame_in_scene - (total_frames - fade_out)
        return 1.0 - ease_out_cubic(out_frame / fade_out)
    return 1.0


def intro_translate_y(frame_in_scene, fade_in=12, distance=8):
    if frame_in_scene >= fade_in:
        return 0
    return lerp(distance, 0, ease_out_cubic(frame_in_scene / fade_in))


def staggered_frame(frame_in_scene, delay_frames):
    return frame_in_scene - delay_frames


# ============================================================
# SCENE RENDERERS
# ============================================================
def scene_title(f, dur, spec, theme):
    data = spec["scenes"]["title"]
    op = scene_envelope(f, dur, fade_in=18, fade_out=10)
    ty1 = intro_translate_y(f, fade_in=18, distance=14)
    ty2 = intro_translate_y(staggered_frame(f, 8), fade_in=18, distance=14)
    op2 = scene_envelope(staggered_frame(f, 8), dur, fade_in=18, fade_out=10)

    cx = W / 2
    parts = []
    parts.append(text(data["headline"], cx, H / 2 - 20 + ty1, 110,
                      color=theme["ink"], weight=700, family=theme["serif"], opacity=op))
    parts.append(text(data["eyebrow"], cx, H / 2 + 60 + ty2, 32,
                      color=theme["muted"], family=theme["sans"], opacity=op2 * 0.9))
    return svg_doc("".join(parts), theme)


def scene_three_things(f, dur, spec, theme):
    data = spec["scenes"]["three_things"]
    op_outer = scene_envelope(f, dur, fade_in=12, fade_out=8)
    cx = W / 2
    parts = []

    parts.append(text(data["eyebrow"].upper(), cx, 280, 26,
                      color=theme["accent"], weight=600, family=theme["sans"],
                      opacity=op_outer, letter_spacing=4))
    rule_w = 120 * ease_out_cubic(min(1.0, f / 20))
    parts.append(rect(cx - rule_w / 2, 305, rule_w, 2, theme["rule"], op_outer))

    base_y = 470
    row_height = 130
    for i, item in enumerate(data["items"]):
        delay = 8 + i * 10
        local_f = staggered_frame(f, delay)
        if local_f < 0:
            continue
        op_row = clamp01(local_f / 14) * op_outer
        ty = lerp(20, 0, ease_out_cubic(min(1.0, local_f / 14)))
        y = base_y + i * row_height + ty
        parts.append(text(item["name"], cx, y, 64,
                          color=theme["ink"], weight=700, family=theme["serif"], opacity=op_row))
        parts.append(text(item["descriptor"], cx, y + 40, 22,
                          color=theme["muted"], family=theme["sans"],
                          opacity=op_row * 0.8, italic=True))
    return svg_doc("".join(parts), theme)


def scene_problem(f, dur, spec, theme):
    data = spec["scenes"]["problem"]
    op = scene_envelope(f, dur, fade_in=12, fade_out=8)
    ty = intro_translate_y(f, fade_in=12, distance=10)
    cx = W / 2
    parts = []
    color_a = theme["accent"] if data.get("accent_line") == "a" else theme["ink"]
    color_b = theme["accent"] if data.get("accent_line") == "b" else theme["ink"]
    italic_a = data.get("accent_line") == "a"
    italic_b = data.get("accent_line") == "b"
    parts.append(text(data["line_a"], cx, H / 2 - 40 + ty, 96,
                      color=color_a, weight=700, family=theme["serif"], opacity=op,
                      italic=italic_a))
    parts.append(text(data["line_b"], cx, H / 2 + 70 + ty, 96,
                      color=color_b, weight=700, family=theme["serif"], opacity=op,
                      italic=italic_b))
    return svg_doc("".join(parts), theme)


def scene_specific_case(f, dur, spec, theme):
    data = spec["scenes"]["specific_case"]
    op = scene_envelope(f, dur, fade_in=12, fade_out=8)
    ty = intro_translate_y(f, fade_in=12, distance=10)
    cx = W / 2

    accent_line = data.get("accent_line", "b")

    def color_for(letter):
        return theme["accent"] if accent_line == letter else theme["ink"]

    def weight_for(letter):
        return 700 if accent_line == letter else 400

    parts = []
    parts.append(text(data["line_a"], cx, H / 2 - 90 + ty, 64,
                      color=color_for("a"), weight=weight_for("a"),
                      family=theme["serif"], opacity=op))
    parts.append(text(data["line_b"], cx, H / 2 + 0 + ty, 64,
                      color=color_for("b"), weight=weight_for("b"),
                      family=theme["serif"], opacity=op))
    parts.append(text(data["line_c"], cx, H / 2 + 90 + ty, 64,
                      color=color_for("c"), weight=weight_for("c"),
                      family=theme["serif"], opacity=op))
    return svg_doc("".join(parts), theme)


def scene_fix(f, dur, spec, theme):
    data = spec["scenes"]["fix"]
    op_outer = scene_envelope(f, dur, fade_in=12, fade_out=8)
    cx = W / 2

    f_gate = f
    op_gate = clamp01(f_gate / 14) * op_outer
    scale_gate = lerp(0.95, 1.0, ease_out_cubic(min(1.0, f_gate / 16)))

    f_fuse = staggered_frame(f, 16)
    op_fuse = clamp01(f_fuse / 14) * op_outer
    ty_fuse = lerp(12, 0, ease_out_cubic(min(1.0, f_fuse / 14)))

    parts = []
    parts.append(
        f'<g transform="translate({cx} {H/2 - 30}) scale({scale_gate}) translate(-{cx} -{H/2 - 30})">'
        f'{text(data["primary"], cx, H / 2 - 30, 140, color=theme["ink"], weight=700, family=theme["serif"], opacity=op_gate)}'
        f'</g>'
    )
    parts.append(text(data["secondary"], cx, H / 2 + 110 + ty_fuse, 64,
                      color=theme["muted"], weight=400, family=theme["serif"],
                      opacity=op_fuse, italic=True))
    return svg_doc("".join(parts), theme)


def scene_mechanism(f, dur, spec, theme):
    data = spec["scenes"]["mechanism"]
    op = scene_envelope(f, dur, fade_in=12, fade_out=8)
    cx = W / 2
    accent_line = data.get("accent_line", "c")

    line1_op = clamp01(f / 14) * op
    line1_ty = lerp(12, 0, ease_out_cubic(min(1.0, f / 14)))
    line2_op = clamp01(staggered_frame(f, 12) / 14) * op
    line2_ty = lerp(12, 0, ease_out_cubic(min(1.0, staggered_frame(f, 12) / 14)))
    line3_op = clamp01(staggered_frame(f, 30) / 14) * op
    line3_ty = lerp(12, 0, ease_out_cubic(min(1.0, staggered_frame(f, 30) / 14)))

    def color_for(letter):
        return theme["accent"] if accent_line == letter else theme["ink"]

    def weight_for(letter):
        return 700 if accent_line == letter else 400

    def size_for(letter):
        return 72 if accent_line == letter else 56

    parts = []
    parts.append(text(data["line_a"], cx, H / 2 - 90 + line1_ty, size_for("a"),
                      color=color_for("a"), weight=weight_for("a"),
                      family=theme["serif"], opacity=line1_op))
    parts.append(text(data["line_b"], cx, H / 2 + 0 + line2_ty, size_for("b"),
                      color=color_for("b"), weight=weight_for("b"),
                      family=theme["serif"], opacity=line2_op))
    parts.append(text(data["line_c"], cx, H / 2 + 110 + line3_ty, size_for("c"),
                      color=color_for("c"), weight=weight_for("c"),
                      family=theme["serif"], opacity=line3_op))
    return svg_doc("".join(parts), theme)


def scene_consequence(f, dur, spec, theme):
    data = spec["scenes"]["consequence"]
    op = scene_envelope(f, dur, fade_in=12, fade_out=8)
    ty = intro_translate_y(f, fade_in=12, distance=10)
    cx = W / 2
    parts = []
    parts.append(text(data["line_a"], cx, H / 2 - 70 + ty, 70,
                      color=theme["ink"], weight=700, family=theme["serif"], opacity=op))
    parts.append(text(data["line_b"], cx, H / 2 + 30 + ty, 56,
                      color=theme["ink"], weight=400, family=theme["serif"], opacity=op))
    parts.append(text(data["line_c"], cx, H / 2 + 110 + ty, 56,
                      color=theme["muted"], weight=400, family=theme["serif"],
                      opacity=op, italic=True))
    return svg_doc("".join(parts), theme)


def scene_close(f, dur, spec, theme):
    data = spec["scenes"]["close"]
    op_outer = scene_envelope(f, dur, fade_in=18, fade_out=18)
    cx = W / 2

    f_a = f
    op_a = clamp01(f_a / 18) * op_outer
    ty_a = lerp(14, 0, ease_out_cubic(min(1.0, f_a / 18)))

    f_b = staggered_frame(f, 14)
    op_b = clamp01(f_b / 18) * op_outer
    ty_b = lerp(14, 0, ease_out_cubic(min(1.0, f_b / 18)))

    f_c = staggered_frame(f, 40)
    op_c = clamp01(f_c / 24) * op_outer
    ty_c = lerp(14, 0, ease_out_cubic(min(1.0, f_c / 24)))

    parts = []
    parts.append(text(data["primary"], cx, H / 2 - 60 + ty_a, 100,
                      color=theme["ink"], weight=700, family=theme["serif"], opacity=op_a))
    parts.append(text(data["accent"], cx, H / 2 + 60 + ty_b, 100,
                      color=theme["accent"], weight=700, family=theme["serif"], opacity=op_b))
    parts.append(text(data["subtitle"], cx, H / 2 + 180 + ty_c, 26,
                      color=theme["muted"], family=theme["sans"],
                      opacity=op_c * 0.85, italic=True))
    return svg_doc("".join(parts), theme)


# ============================================================
# DISPATCH
# ============================================================
SCENES = [
    (scene_title,           90),
    (scene_three_things,    90),
    (scene_problem,         90),
    (scene_specific_case,   90),
    (scene_fix,             90),
    (scene_mechanism,       90),
    (scene_consequence,     90),
    (scene_close,           120),
]


def render_frame(absolute_frame, spec, theme):
    cursor = 0
    for fn, dur in SCENES:
        if absolute_frame < cursor + dur:
            return fn(absolute_frame - cursor, dur, spec, theme)
        cursor += dur
    return svg_doc("", theme)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", help="Path to scene-spec.json")
    parser.add_argument("output_dir", help="Directory to write PNG frames into")
    parser.add_argument("--theme", help="Path to theme.json (defaults to default_theme.json next to this script)")
    args = parser.parse_args()

    spec = json.loads(Path(args.spec).read_text())

    # Resolve theme
    if args.theme:
        theme = json.loads(Path(args.theme).read_text())
    elif spec.get("theme") and isinstance(spec["theme"], dict):
        theme = spec["theme"]
    else:
        default_path = Path(__file__).parent / "default_theme.json"
        theme = json.loads(default_path.read_text())

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    total = sum(d for _, d in SCENES)
    assert total == TOTAL_FRAMES, f"scene durations sum to {total}, expected {TOTAL_FRAMES}"

    print(f"Rendering {TOTAL_FRAMES} frames to {out_dir}")
    for f in range(TOTAL_FRAMES):
        svg = render_frame(f, spec, theme)
        png_path = out_dir / f"frame_{f:05d}.png"
        cairosvg.svg2png(bytestring=svg.encode("utf-8"),
                         write_to=str(png_path),
                         output_width=W, output_height=H)
        if f % 75 == 0:
            print(f"  frame {f}/{TOTAL_FRAMES}")
    print("done")


if __name__ == "__main__":
    main()
