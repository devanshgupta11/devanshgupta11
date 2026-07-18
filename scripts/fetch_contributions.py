#!/usr/bin/env python3
"""
Fetch a GitHub user's public contribution calendar with no token / no auth.

GitHub serves the calendar fragment used on the profile page at:
    https://github.com/users/<username>/contributions

This scrapes that HTML, pulls every day cell (date, level 0-4, count),
and writes data/contributions.json with the raw days plus derived stats
(current streak, longest streak, best day, monthly totals, yearly total).
"""

import json
import re
import sys
from datetime import datetime, date, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "devanshgupta11"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def fetch_html() -> str:
    headers = {"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}
    resp = requests.get(URL, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_days(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    cells = soup.select("td.ContributionCalendar-day, [data-date]")

    days = []
    for cell in cells:
        d = cell.get("data-date")
        if not d:
            continue
        level = cell.get("data-level")
        level = int(level) if level is not None else 0

        # The visible count lives in a nested sr-only tooltip like
        # "3 contributions on December 14th." or "No contributions on July 13th."
        tooltip_id = cell.get("id")
        count = 0
        tooltip = None
        if tooltip_id:
            tooltip = soup.find(id=f"{tooltip_id}-{d}") or None
        # Fallback: search the tooltip text near this cell by data-date match
        if tooltip is None:
            tooltip = soup.find(
                lambda tag: tag.name == "tool-tip" and tag.get("for") == tooltip_id
            )
        text = tooltip.get_text(strip=True) if tooltip else ""
        m = re.match(r"(\d+)\s+contribution", text)
        if m:
            count = int(m.group(1))
        elif text.lower().startswith("no contributions"):
            count = 0
        else:
            # last resort: level 0 -> 0, otherwise unknown but non-zero
            count = 0 if level == 0 else level

        days.append({"date": d, "level": level, "count": count})

    days.sort(key=lambda x: x["date"])
    return days


def compute_stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)

    # streaks
    longest = current = 0
    running = 0
    today = date.today()
    for d in days:
        if d["count"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    # current streak = trailing run ending at the most recent day with data
    for d in reversed(days):
        if d["count"] > 0:
            current += 1
        else:
            break

    best_day = max(days, key=lambda x: x["count"], default=None)

    monthly = {}
    for d in days:
        ym = d["date"][:7]  # YYYY-MM
        monthly[ym] = monthly.get(ym, 0) + d["count"]

    return {
        "total_last_year": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best_day,
        "monthly_totals": monthly,
    }


def main():
    print(f"Fetching contributions for {USERNAME}...")
    html = fetch_html()
    days = parse_days(html)
    if not days:
        print("ERROR: no contribution cells parsed — GitHub markup may have changed.", file=sys.stderr)
        sys.exit(1)

    stats = compute_stats(days)

    payload = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        "stats": stats,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {len(days)} days -> {OUT_PATH}")
    print(f"Total: {stats['total_last_year']}  Current streak: {stats['current_streak']}  Longest streak: {stats['longest_streak']}")


if __name__ == "__main__":
    main()
