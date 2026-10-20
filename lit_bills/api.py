"""A small, polite client for the Massachusetts Legislature's public API (malegislature.gov/api).

The API is documented at https://malegislature.gov/api/swagger. It needs no key. We keep to one
request per second, identify ourselves in the User-Agent, and cache responses on disk so reruns
don't hit the server again.
"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://malegislature.gov/api"
USER_AGENT = "LITSA ma-lit-bills (github.com/suffolklitsa/ma-lit-bills)"


class Client:
    def __init__(self, cache_dir: Path | None = None, min_interval: float = 1.0, max_age_hours: float = 20):
        self.cache_dir = cache_dir
        self.min_interval = min_interval
        self.max_age = max_age_hours * 3600
        self._last = 0.0

    def _cache_path(self, path: str) -> Path | None:
        if not self.cache_dir:
            return None
        return self.cache_dir / (hashlib.sha256(path.encode()).hexdigest()[:24] + ".json")

    def get(self, path: str):
        cached = self._cache_path(path)
        if cached and cached.exists() and time.time() - cached.stat().st_mtime < self.max_age:
            return json.loads(cached.read_text(encoding="utf-8"))
        for attempt in range(4):
            wait = self.min_interval - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            req = urllib.request.Request(BASE + path, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(req, timeout=90) as r:
                    data = json.load(r)
                break
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise
        if cached:
            cached.parent.mkdir(parents=True, exist_ok=True)
            cached.write_text(json.dumps(data), encoding="utf-8")
        return data

    def documents(self, court: int) -> list[dict]:
        """Every document filed in a General Court: bill number, docket, title, primary sponsor."""
        return self.get(f"/GeneralCourts/{court}/Documents")

    def document(self, court: int, number: str) -> dict:
        """One bill: sponsors, cosponsors, committee recommendations. `BillHistory` is a link, not data."""
        return self.get(f"/GeneralCourts/{court}/Documents/{number}")

    def history(self, court: int, number: str) -> list[dict]:
        """Every action on a bill: date, branch, action text, whether it was stricken.

        The API answers 400 for a bill with no actions yet; that means an empty history.
        """
        try:
            return self.get(f"/GeneralCourts/{court}/Documents/{number}/DocumentHistoryActions")
        except urllib.error.HTTPError as e:
            if e.code == 400:
                return []
            raise
