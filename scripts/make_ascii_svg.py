#!/usr/bin/env python3
"""
Convert source-prepped.png into a self-typing monochrome ASCII portrait SVG.

The prepped image is downsampled to a character grid (~100 wide), and each
pixel's brightness picks a glyph from a density ramp -- sparse chars for
bright areas, dense ones for dark. Rows wipe in left-to-right (a small
block cursor rides the wipe edge), staggered top to bottom. Prints once,
freezes -- no looping.

    python scripts/make_ascii_svg.py   # writes avi-ascii.svg -> here: devansh-ascii.svg
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image

SRC_PATH = Path(__file__).resolve().parent.parent / "source-prepped.png"
OUT_PATH = Path(__file__).resolve().parent.parent / "devansh-ascii.svg"

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense); leading space = blank
GRID_W = 100
CHAR_ASPECT = 0.55        # monospace chars are taller than wide; compensate

FILL_COLOR = "#c9d1d9"    # single light-gray fill -- no per-char rainbow
FONT_SIZE = 8
CHAR_W = FONT_SIZE * 0.6
CHAR_H = FONT_SIZE * 1.0


def image_to_ascii_grid(img_path: Path, grid_w: int = GRID_W):
    img = Image.open(img_path).convert("L")
    w, h = img.size
    grid_h = max(1, int(grid_w * (h / w) * CHAR_ASPECT))
    small = img.resize((grid_w, grid_h), Image.LANCZOS)
    arr = np.array(small)

    ramp_len = len(RAMP)
    rows = []
    for y in range(grid_h):
        row_chars = []
        for x in range(grid_w):
            brightness = arr[y, x] / 255.0  # 0 = black, 1 = white
            idx = int((1 - brightness) * (ramp_len - 1))
            idx = max(0, min(ramp_len - 1, idx))
            row_chars.append(RAMP[idx])
        rows.append("".join(row_chars))
    return rows


def esc(ch: str) -> str:
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(ch, ch)


def build_svg(rows: list[str]) -> str:
    n_rows = len(rows)
    n_cols = max(len(r) for r in rows) if rows else 0

    width = n_cols * CHAR_W + 20
    height = n_rows * CHAR_H + 20

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {width:.0f} {height:.0f}" width="{width:.0f}" height="{height:.0f}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="Consolas, Menlo, monospace" '
        f'font-size="{FONT_SIZE}">'
    )
    parts.append(f'<rect width="{width:.0f}" height="{height:.0f}" fill="transparent"/>')

    parts.append(f"""
    <style>
      .row {{ clip-path: inset(0 100% 0 0); animation: wipe 0.5s linear forwards; }}
      .cursor {{ fill: {FILL_COLOR}; animation: cursor-fade 0.5s linear forwards; }}
      @keyframes wipe {{ to {{ clip-path: inset(0 0 0 0); }} }}
      @keyframes cursor-fade {{
        0% {{ opacity: 1; }}
        90% {{ opacity: 1; }}
        100% {{ opacity: 0; }}
      }}
      text {{ fill: {FILL_COLOR}; white-space: pre; }}
    </style>
    """)

    row_stagger = 0.045  # seconds between each row starting
    for ri, row_text in enumerate(rows):
        y = 10 + (ri + 1) * CHAR_H
        delay = ri * row_stagger
        escaped = "".join(esc(c) for c in row_text)
        # group per row: clipped wipe reveals the text; a cursor rect rides the edge
        row_width = len(row_text) * CHAR_W
        parts.append(f'<g class="row" style="animation-delay:{delay:.3f}s">')
        parts.append(f'  <text x="10" y="{y:.1f}" xml:space="preserve">{escaped}</text>')
        parts.append(
            f'  <rect class="cursor" x="{10 + row_width - 2:.1f}" y="{y - CHAR_H + 1:.1f}" '
            f'width="3" height="{CHAR_H - 2:.1f}" style="animation-delay:{delay:.3f}s"/>'
        )
        parts.append("</g>")

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    if not SRC_PATH.exists():
        print(f"ERROR: {SRC_PATH} not found. Run prep_photo.py first.", file=sys.stderr)
        sys.exit(1)

    rows = image_to_ascii_grid(SRC_PATH)
    svg = build_svg(rows)
    OUT_PATH.write_text(svg)
    print(f"Wrote {OUT_PATH} ({len(rows)} rows x {GRID_W} cols)")


if __name__ == "__main__":
    main()
