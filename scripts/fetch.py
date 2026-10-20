#!/usr/bin/env python3
"""Refresh data/<court>/bills.json from the Legislature's API.

    python3 scripts/fetch.py --court 194

1. Pull every document title for the session (one request).
2. Match titles against topics/topics.toml to find candidates.
3. Apply data/<court>/review.toml: rejected bills are dropped; confirmed bills are kept even if
   their title no longer matches; topics can be overridden there.
4. Fetch details and history for every kept bill (two requests per bill, one per second).
5. Keep any summaries already written in bills.json.
"""
from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lit_bills import api, records, topics as topic_mod  # noqa: E402


def load_review(path: Path) -> dict:
    if not path.exists():
        return {"confirmed": {}, "rejected": {}}
    with path.open("rb") as f:
        data = tomllib.load(f)
    return {"confirmed": data.get("confirmed", {}), "rejected": data.get("rejected", {})}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Refresh tracked bills from malegislature.gov.")
    ap.add_argument("--court", type=int, required=True, help="General Court number, e.g. 194 for 2025-2026")
    ap.add_argument("--limit", type=int, default=0, help="fetch details for at most this many bills (testing)")
    args = ap.parse_args(argv)
    out_dir = ROOT / "data" / str(args.court)
    out_dir.mkdir(parents=True, exist_ok=True)
    client = api.Client(cache_dir=ROOT / ".cache")
    topics = topic_mod.load()
    review = load_review(out_dir / "review.toml")
    old = {}
    if (out_dir / "bills.json").exists():
        old = {b["bill"]: b for b in json.loads((out_dir / "bills.json").read_text(encoding="utf-8"))["bills"]}

    listing = client.documents(args.court)
    keep = []
    for doc in listing:
        num = doc.get("BillNumber")
        if not num or num in review["rejected"]:
            continue
        matched = topic_mod.match(doc.get("Title") or "", topics)
        if num in review["confirmed"]:
            keep.append((doc, review["confirmed"][num].get("topics") or matched, "confirmed"))
        elif matched:
            keep.append((doc, matched, "candidate"))
    if args.limit:
        keep = keep[: args.limit]

    bills = []
    for i, (doc, tids, state) in enumerate(keep, 1):
        detail = client.document(args.court, doc["BillNumber"])
        actions = client.history(args.court, doc["BillNumber"])
        rec = records.record(args.court, doc, detail, actions, tids, state)
        if doc["BillNumber"] in old and old[doc["BillNumber"]].get("summary"):
            rec["summary"] = old[doc["BillNumber"]]["summary"]
        bills.append(rec)
        if i % 25 == 0:
            print(f"  {i}/{len(keep)}")
    bills.sort(key=lambda b: (b["bill"][0], int("".join(c for c in b["bill"] if c.isdigit()) or 0)))
    payload = {"schema_version": 1, "court": args.court, "documents_scanned": len(listing), "bills": bills}
    (out_dir / "bills.json").write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    by_state = {s: sum(1 for b in bills if b["review"] == s) for s in ("confirmed", "candidate")}
    print(f"scanned {len(listing)} documents; kept {len(bills)} ({by_state['confirmed']} confirmed, {by_state['candidate']} candidates)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
