#!/usr/bin/env python3
"""Write a weekly digest of tracked bills, for the newsletter and the site.

    python3 scripts/digest.py --court 194 --since 2026-10-13

Lists confirmed bills with any action on or after --since, grouped by topic. Candidates are left
out until a person confirms them. The text stays neutral: it reports what happened, never whether
it's good.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lit_bills import topics as topic_mod  # noqa: E402


def digest(bills: list[dict], topics: dict, since: str) -> str:
    lines = [f"## Massachusetts tech bills: activity since {since}", ""]
    any_rows = False
    for tid, t in topics.items():
        rows = []
        for b in bills:
            if b["review"] != "confirmed" or tid not in b["topics"]:
                continue
            recent = [h for h in b["history"] if h["date"] and h["date"] >= since]
            if recent:
                rows.append((b, recent[-1]))
        if not rows:
            continue
        any_rows = True
        lines += [f"### {t['name']}", ""]
        for b, h in sorted(rows, key=lambda r: r[1]["date"], reverse=True):
            lines.append(f"- [{b['bill']}]({b['url']}), {b['title']}: {h['action']} ({h['branch']}, {h['date']})")
        lines.append("")
    if not any_rows:
        lines.append("No activity on tracked bills this week.")
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Weekly digest of tracked bills.")
    ap.add_argument("--court", type=int, required=True)
    ap.add_argument("--since", default=(dt.date.today() - dt.timedelta(days=7)).isoformat())
    args = ap.parse_args(argv)
    data = json.loads((ROOT / "data" / str(args.court) / "bills.json").read_text(encoding="utf-8"))
    print(digest(data["bills"], topic_mod.load(), args.since), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
