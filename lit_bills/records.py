"""Turn API responses into the bill records described in docs/DATA.md."""
from __future__ import annotations

from typing import Any


def bill_url(court: int, number: str) -> str:
    return f"https://malegislature.gov/Bills/{court}/{number}"


def history(actions: list[dict]) -> list[dict[str, str]]:
    rows = []
    for h in actions or []:
        if h.get("IsStricken"):
            continue
        rows.append({"date": (h.get("Date") or "")[:10] or None, "branch": h.get("Branch") or "", "action": (h.get("Action") or "").strip()})
    # Some actions have no date (study orders, clerk processing). Keep them, after the dated ones,
    # in the order the API gives them.
    rows.sort(key=lambda r: (r["date"] is None, r["date"] or ""))
    return rows


def record(court: int, listing: dict, detail: dict | None, actions: list[dict] | None, topics: list[str], review: str) -> dict[str, Any]:
    detail = detail or {}
    hist = history(actions or [])
    sponsor = (detail.get("PrimarySponsor") or listing.get("PrimarySponsor") or {}).get("Name")
    return {
        "bill": listing["BillNumber"],
        "docket": listing.get("DocketNumber"),
        "court": court,
        "title": (listing.get("Title") or "").strip(),
        "url": bill_url(court, listing["BillNumber"]),
        "primary_sponsor": sponsor,
        "cosponsor_count": len(detail.get("Cosponsors") or []),
        "filed": next((h["date"] for h in hist if h["date"]), None),
        "last_action": hist[-1] if hist else None,
        "history": hist,
        "topics": topics,
        "review": review,
        "summary": None,
    }
