"""Match bill titles to topic tags defined in topics/topics.toml."""
from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path = ROOT / "topics" / "topics.toml") -> dict[str, dict]:
    with path.open("rb") as f:
        topics = tomllib.load(f)
    for tid, t in topics.items():
        if not re.fullmatch(r"[a-z][a-z0-9-]*", tid):
            raise ValueError(f"topic id {tid!r}: lowercase letters, digits and hyphens")
        for key in ("name", "description", "match"):
            if key not in t:
                raise ValueError(f"topic {tid}: missing {key}")
    return topics


def _pattern(phrase: str) -> re.Pattern:
    return re.compile(r"(?<![a-z0-9])" + re.escape(phrase.lower()) + r"(?![a-z0-9])")


def match(title: str, topics: dict[str, dict]) -> list[str]:
    """Topic ids whose phrases appear in the title as whole words, minus excluded phrases."""
    text = title.lower()
    found = []
    for tid, t in topics.items():
        if any(_pattern(p).search(text) for p in t.get("exclude", [])):
            continue
        if any(_pattern(p).search(text) for p in t["match"]):
            found.append(tid)
    return found
