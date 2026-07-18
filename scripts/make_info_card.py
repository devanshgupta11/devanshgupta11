#!/usr/bin/env python3
"""
Hand-authored neofetch-style info card SVG.
Each line fades + slides in on a short stagger, prints once, freezes.

Edit ROWS below with your own story -- this is the panel for the numbers
the contribution graph can't tell.

Run with STATIC=1 to emit a frozen (no-animation) frame for a Quick Look
preview: STATIC=1 python3 make_info_card.py
"""

import os
from pathlib import Path

OUT_PATH = Path(__file__).resolve().parent.parent / "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

TITLE = "devansh@github"

ROWS = [
    ("Now", "AI & Full-Stack Developer @ TTL Engg. Pvt. Ltd."),
    ("Prev", "Building real-world CV / GenAI projects"),
    ("Stack", "Python, C++, Java, JS, React, Next.js, Node, Express"),
    ("Learning", "Deep Learning, CNNs, Generative AI & Scalable Systems"),
    ("Highlights", "5 followers, 25 repos, active daily on GitHub"),
]

WIDTH = 490
LINE_H = 24
TOP_PAD = 46
BOTTOM_PAD = 20
HEIGHT = TOP_PAD + len(ROWS) * LINE_H + BOTTOM_PAD

KEY_COLOR = "#39d353"
VAL_COLOR = "#c9d1d9"
TITLE_COLOR = "#e6edf3"
BAR_RED, BAR_YELLOW, BAR_GREEN = "#ff5f56", "#ffbd2e", "#27c93f"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build():
    parts = []
    parts.append(
        f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="Consolas, Menlo, monospace">'
    )
    parts.append(f'<rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" rx="10" ry="10" '
                 f'fill="#0d1117" stroke="#30363d" stroke-width="1"/>')

    if not STATIC:
        parts.append("""
        <style>
          .line { opacity: 0; transform: translateX(-6px); animation: type-in 0.35s ease-out forwards; }
          @keyframes type-in { to { opacity: 1; transform: translateX(0); } }
        </style>
        """)

    # fake title bar with traffic-light dots
    parts.append(f'<circle cx="18" cy="18" r="6" fill="{BAR_RED}"/>')
    parts.append(f'<circle cx="38" cy="18" r="6" fill="{BAR_YELLOW}"/>')
    parts.append(f'<circle cx="58" cy="18" r="6" fill="{BAR_GREEN}"/>')
    parts.append(f'<text x="{WIDTH/2}" y="22" text-anchor="middle" fill="#8b949e" font-size="12">{esc(TITLE)}</text>')
    parts.append(f'<line x1="0" y1="34" x2="{WIDTH}" y2="34" stroke="#30363d" stroke-width="1"/>')

    for i, (key, val) in enumerate(ROWS):
        y = TOP_PAD + i * LINE_H
        cls = "" if STATIC else "class=\"line\""
        style = "" if STATIC else f'style="animation-delay:{0.15 + i * 0.18:.2f}s"'
        parts.append(
            f'<text {cls} {style} x="24" y="{y}">'
            f'<tspan fill="{KEY_COLOR}" font-weight="bold">{esc(key)}</tspan>'
            f'<tspan fill="{VAL_COLOR}">:  {esc(val)}</tspan>'
            f'</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    svg = build()
    OUT_PATH.write_text(svg)
    print(f"Wrote {OUT_PATH} (static={STATIC})")


if __name__ == "__main__":
    main()
