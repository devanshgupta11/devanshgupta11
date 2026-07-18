#!/usr/bin/env python3
"""
Render data/contributions.json as an animated 53-week x 7-day SVG heatmap.

Reveal animation: boxes slide down + fade in, staggered diagonally
(column then row), play once on load, then freeze. Pure CSS keyframes,
no JS -- GitHub's README sanitizer allows this inside an <img>-embedded SVG.
"""

import json
from datetime import date, datetime
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "contributions.json"
OUT_PATH = Path(__file__).resolve().parent.parent / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
# index 0..4 = GitHub's real levels, index 5 reserved as a neon top accent
# (used only if you want to highlight an all-time-high day; unused by default)

CELL = 11
GAP = 3
LEFT_PAD = 30
TOP_PAD = 20
DAY_LABELS = ["", "Mon", "", "Wed", "", "Fri", ""]
MONTH_LABELS_Y = 12


def load_data():
    return json.loads(DATA_PATH.read_text())


def build_weeks(days):
    """Group day dicts into weeks (columns) the same way GitHub's grid does:
    each column is a week starting Sunday."""
    by_date = {d["date"]: d for d in days}
    if not days:
        return []

    first = datetime.strptime(days[0]["date"], "%Y-%m-%d").date()
    # back up to the preceding Sunday so week columns align
    start = first
    while start.weekday() != 6:  # Sunday = 6 in Python's weekday() only for Mon=0..Sun=6
        start = date.fromordinal(start.toordinal() - 1)

    last = datetime.strptime(days[-1]["date"], "%Y-%m-%d").date()

    weeks = []
    cursor = start
    while cursor <= last:
        week = []
        for i in range(7):
            d = date.fromordinal(cursor.toordinal() + i)
            key = d.isoformat()
            entry = by_date.get(key, {"date": key, "level": 0, "count": 0})
            week.append(entry)
        weeks.append(week)
        cursor = date.fromordinal(cursor.toordinal() + 7)
    return weeks


def month_ticks(weeks):
    """Return [(week_index, 'Jan'), ...] for the first week each month appears."""
    ticks = []
    seen = set()
    for wi, week in enumerate(weeks):
        for day in week:
            d = datetime.strptime(day["date"], "%Y-%m-%d").date()
            key = (d.year, d.month)
            if key not in seen:
                seen.add(key)
                ticks.append((wi, d.strftime("%b")))
                break
    return ticks


def render(payload):
    days = payload["days"]
    stats = payload["stats"]
    weeks = build_weeks(days)
    n_weeks = len(weeks)

    grid_w = n_weeks * (CELL + GAP)
    grid_h = 7 * (CELL + GAP)
    width = LEFT_PAD + grid_w + 20
    height = TOP_PAD + grid_h + 70  # extra room for legend + stats footer

    svg_parts = []
    svg_parts.append(
        f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="Consolas, Menlo, monospace">'
    )

    # background (transparent so it blends with GitHub's theme)
    svg_parts.append(f'<rect width="{width}" height="{height}" fill="transparent"/>')

    # style: keyframes for a diagonal slide-down + fade reveal, play once
    svg_parts.append("""
    <style>
      .cell { opacity: 0; transform: translateY(-6px); animation: reveal 0.4s ease-out forwards; }
      @keyframes reveal {
        to { opacity: 1; transform: translateY(0); }
      }
      .lbl { fill: #8b949e; font-size: 10px; }
      .footer { fill: #c9d1d9; font-size: 12px; }
      .legend-lbl { fill: #8b949e; font-size: 10px; }
    </style>
    """)

    # month labels
    for wi, label in month_ticks(weeks):
        x = LEFT_PAD + wi * (CELL + GAP)
        svg_parts.append(f'<text x="{x}" y="{MONTH_LABELS_Y}" class="lbl">{label}</text>')

    # day-of-week labels
    for row, label in enumerate(DAY_LABELS):
        if not label:
            continue
        y = TOP_PAD + row * (CELL + GAP) + CELL - 2
        svg_parts.append(f'<text x="0" y="{y}" class="lbl">{label}</text>')

    # cells, staggered diagonally: delay grows with column + row
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            level = min(day["level"], 4)  # keep 0-4 for the real palette range
            color = PALETTE[level]
            x = LEFT_PAD + wi * (CELL + GAP)
            y = TOP_PAD + di * (CELL + GAP)
            delay = (wi + di) * 0.008
            title = f'{day["count"]} contribution{"s" if day["count"] != 1 else ""} on {day["date"]}'
            svg_parts.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" ry="2" '
                f'fill="{color}" style="animation-delay:{delay:.3f}s"><title>{title}</title></rect>'
            )

    # legend: Less -> More
    legend_y = TOP_PAD + grid_h + 20
    legend_x = LEFT_PAD
    svg_parts.append(f'<text x="{legend_x}" y="{legend_y + 9}" class="legend-lbl">Less</text>')
    lx = legend_x + 34
    for level, color in enumerate(PALETTE[:5]):
        svg_parts.append(
            f'<rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" ry="2" fill="{color}"/>'
        )
        lx += CELL + GAP
    svg_parts.append(f'<text x="{lx + 4}" y="{legend_y + 9}" class="legend-lbl">More</text>')

    # stats footer
    footer_y = legend_y + 28
    footer_text = (
        f'{stats["total_last_year"]:,} contributions in the last year &#183; '
        f'current streak {stats["current_streak"]}d &#183; longest streak {stats["longest_streak"]}d'
    )
    svg_parts.append(f'<text x="{LEFT_PAD}" y="{footer_y}" class="footer">{footer_text}</text>')

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


def main():
    payload = load_data()
    svg = render(payload)
    OUT_PATH.write_text(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
