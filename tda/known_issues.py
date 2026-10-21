"""Differences that are already publicly reported upstream.

A finding that matches one of these is reported with the link, and is not presented as new.
Checked by hand against the issue trackers on the date given.
"""

from __future__ import annotations

KNOWN = [
    {
        "id": "ollama/ollama#14601",
        "url": "https://github.com/ollama/ollama/issues/14601",
        "summary": "Go templates that print {{ .Function }} get a Go struct, not JSON, for tool definitions",
        "cls": "TOOL_SCHEMA_NOT_JSON",
        "sources": {"go_template"},
        "checked": "2026-10-22",
    },
]


def match(cls: str, source: str) -> list[dict]:
    return [k for k in KNOWN if k["cls"] == cls and source in k["sources"]]
