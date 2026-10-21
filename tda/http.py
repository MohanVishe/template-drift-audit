"""Polite, cached, read-only HTTP GETs with a provenance log.

Every response body is stored once under its sha256; `provenance.jsonl` records
what was asked for, when, and what came back. Signed CDN query strings are never
written to disk.
"""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from tda import __version__

USER_AGENT = f"template-drift-audit/{__version__} (read-only research; metadata only)"
MIN_INTERVAL = 1.0  # seconds between network requests


def _strip_query(url: str) -> str:
    p = urlsplit(url)
    return urlunsplit((p.scheme, p.netloc, p.path, "", ""))


class Fetcher:
    def __init__(self, cache_dir: Path, offline: bool = False):
        self.dir = Path(cache_dir)
        (self.dir / "blobs").mkdir(parents=True, exist_ok=True)
        self.index_path = self.dir / "index.json"
        self.index: dict[str, str] = json.loads(self.index_path.read_text()) if self.index_path.exists() else {}
        self.offline = offline
        self._last = 0.0
        self.network_bytes = 0
        self.network_requests = 0
        self.used: set[str] = set()  # every URL this run read, cached or not (query strings stripped)

    def _key(self, url: str, accept: str | None, rng: tuple[int, int] | None) -> str:
        return json.dumps([url, accept or "", list(rng) if rng else None])

    def get(self, url: str, *, accept: str | None = None, rng: tuple[int, int] | None = None) -> bytes:
        """GET url (optionally bytes rng[0]..rng[1] inclusive). Cached by request, stored by content."""
        key = self._key(url, accept, rng)
        self.used.add(_strip_query(url))
        if key in self.index:
            return (self.dir / "blobs" / self.index[key]).read_bytes()
        if self.offline:
            raise LookupError(f"offline and not cached: {url} {rng or ''}")

        wait = MIN_INTERVAL - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        headers = {"User-Agent": USER_AGENT}
        if accept:
            headers["Accept"] = accept
        if rng:
            headers["Range"] = f"bytes={rng[0]}-{rng[1]}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                body, status, final = r.read(), r.status, r.geturl()
        except urllib.error.HTTPError as e:
            if rng and e.code == 416:  # range starts past the end of the file
                body, status, final = b"", 416, url
            else:
                raise
        finally:
            self._last = time.monotonic()
            self.network_requests += 1
        if rng and status == 200:
            body = body[rng[0]:rng[1] + 1]  # server ignored Range; keep only what was asked for
        self.network_bytes += len(body)

        digest = hashlib.sha256(body).hexdigest()
        (self.dir / "blobs" / digest).write_bytes(body)
        self.index[key] = digest
        self.index_path.write_text(json.dumps(self.index, indent=0))
        with open(self.dir / "provenance.jsonl", "a", encoding="utf-8") as log:
            log.write(json.dumps({
                "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "url": url, "range": rng, "accept": accept, "status": status,
                "final_url": _strip_query(final), "bytes": len(body), "sha256": digest,
            }) + "\n")
        return body

    def get_optional(self, url: str, **kw) -> bytes | None:
        """Like get, but a 404 returns None and is remembered, so offline re-runs agree."""
        key = self._key(url, kw.get("accept"), kw.get("rng")) + "#404"
        if key in self.index:
            return None
        try:
            return self.get(url, **kw)
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
            self.index[key] = ""
            self.index_path.write_text(json.dumps(self.index, indent=0))
            return None

    def get_json(self, url: str, **kw) -> dict:
        return json.loads(self.get(url, **kw))
