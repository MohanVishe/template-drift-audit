"""Benign, deterministic test conversations, in Hugging Face message format.

`to_ollama` converts one to the /api/chat shape Ollama's templates consume.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

PATH = Path(__file__).with_name("fixtures.json")
TOOL_SET = {"F04", "F05", "F06", "F07", "F08", "F09"}  # the tool-calling set the headline uses


@dataclass(frozen=True)
class Fixture:
    id: str
    about: str
    messages: list[dict]
    tools: list[dict] | None


def load() -> tuple[list[Fixture], str]:
    raw = PATH.read_bytes()
    data = json.loads(raw)
    fixtures = [Fixture(f["id"], f["about"], f["messages"], data["tools"] if f["tools"] else None)
                for f in data["fixtures"]]
    return fixtures, hashlib.sha256(raw).hexdigest()[:12]


def to_ollama(messages: list[dict]) -> list[dict]:
    out = []
    for m in copy.deepcopy(messages):
        o = {"role": m["role"], "content": m.get("content") or ""}
        if m.get("reasoning_content"):
            o["thinking"] = m["reasoning_content"]
        if m.get("tool_calls"):
            o["tool_calls"] = [{"id": tc.get("id", ""), "function": {"index": i, "name": tc["function"]["name"],
                                                                     "arguments": tc["function"]["arguments"]}}
                               for i, tc in enumerate(m["tool_calls"])]
        if m["role"] == "tool":
            o["tool_name"] = m.get("name", "")
            o["tool_call_id"] = m.get("tool_call_id", "")
        out.append(o)
    return out
