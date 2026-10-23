#!/usr/bin/env python3
"""Check every data/<court>/bills.json and review.toml against docs/DATA.md. Runs in CI."""
from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lit_bills import topics as topic_mod  # noqa: E402

BILL = re.compile(r"^[HS]D?\d+$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REVIEW_STATES = {"candidate", "confirmed"}


def check_bill(b: dict, topic_ids: set[str]) -> list[str]:
    where = b.get("bill", "?")
    out = []
    for key in ("bill", "court", "title", "url", "topics", "review", "history", "summary"):
        if key not in b:
            out.append(f"{where}: missing {key}")
    if out:
        return out
    if not BILL.match(b["bill"]):
        out.append(f"{where}: bill number should look like H1234 or S567")
    if b["review"] not in REVIEW_STATES:
        out.append(f"{where}: review must be one of {sorted(REVIEW_STATES)}")
    unknown = set(b["topics"]) - topic_ids
    if unknown:
        out.append(f"{where}: unknown topics {sorted(unknown)}")
    for h in b["history"]:
        if h.get("date") is not None and not DATE.match(h["date"]):
            out.append(f"{where}: history date {h.get('date')!r}")
    s = b["summary"]
    if s is not None:
        for key in ("text", "written_by", "reviewed_by", "reviewed_on"):
            if not s.get(key):
                out.append(f"{where}: summary needs {key}")

        summary_text = s.get("text")
        if summary_text:
            word_count = len(summary_text.split())
            if word_count > 120:
                out.append(
                    f"{where}: summary has {word_count} words (maximum 120)"
                )

        if b["review"] != "confirmed":
            out.append(f"{where}: only confirmed bills get summaries")
    return out


def main() -> int:
    topic_ids = set(topic_mod.load())
    problems = []
    for court_dir in sorted((ROOT / "data").glob("[0-9]*")):
        bills_path = court_dir / "bills.json"
        if bills_path.exists():
            data = json.loads(bills_path.read_text(encoding="utf-8"))
            seen = set()
            for b in data.get("bills", []):
                problems += check_bill(b, topic_ids)
                if b.get("bill") in seen:
                    problems.append(f"{b['bill']}: duplicate")
                seen.add(b.get("bill"))
        review_path = court_dir / "review.toml"
        if review_path.exists():
            with review_path.open("rb") as f:
                review = tomllib.load(f)
            both = set(review.get("confirmed", {})) & set(review.get("rejected", {}))
            problems += [f"{court_dir.name}/review.toml: {n} is both confirmed and rejected" for n in sorted(both)]
            for n, entry in review.get("confirmed", {}).items():
                problems += [f"{court_dir.name}/review.toml: {n} unknown topic {t}" for t in entry.get("topics", []) if t not in topic_ids]
    for p in problems:
        print(p)
    print("ok" if not problems else f"{len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
