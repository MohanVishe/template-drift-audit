"""The population mapping: which upstream repo and commit is each package's L0.

Read from `mapping.yaml` (a list of flat records) or `mapping.json`. Only the YAML subset the
mapping uses is parsed (a list of `key: value` maps, comments, quoted scalars), so the tool keeps
jinja2 as its only runtime dependency.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

FIELDS = ("package", "upstream_repo", "upstream_sha", "template_file", "reason", "confidence")


@dataclass(frozen=True)
class Target:
    package: str  # "qwen2.5:7b-instruct" or "hf.co/<repo>:<quant>"
    upstream_repo: str = ""
    upstream_sha: str = ""
    template_file: str = ""
    reason: str = ""
    confidence: str = ""
    extra: dict = field(default_factory=dict, compare=False)

    @property
    def excluded(self) -> bool:
        return self.extra.get("status") == "excluded"

    @property
    def kind(self) -> str:
        return "hf" if self.package.startswith("hf.co/") else "library"


def _scalar(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return json.loads(v) if v[0] == '"' else v[1:-1].replace("''", "'")
    return "" if v in ("", "~", "null") else v


def parse_yaml_records(text: str) -> list[dict]:
    """Parse a top-level list of flat maps, optionally under one key (`models:`)."""
    records, cur = [], None
    for raw in text.splitlines():
        line = raw.rstrip()
        if " #" in line and not any(q in line for q in "\"'"):  # a trailing comment, as YAML reads it
            line = line.split(" #")[0].rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        body = line.lstrip()
        if body.startswith("- "):
            cur = {}
            records.append(cur)
            body = body[2:]
        elif cur is None:
            continue  # a wrapper key such as `models:` or `snapshot: ...`
        key, sep, value = body.partition(":")
        if not sep:
            raise ValueError(f"cannot parse mapping line: {raw!r}")
        cur[key.strip()] = _scalar(value)
    return records


def load(path: Path) -> list[Target]:
    text = Path(path).read_text(encoding="utf-8")
    records = json.loads(text) if str(path).endswith(".json") else parse_yaml_records(text)
    if isinstance(records, dict):
        records = next(v for v in records.values() if isinstance(v, list))
    out = []
    for r in records:
        known = {k: str(r.get(k) or "") for k in FIELDS}
        out.append(Target(**known, extra={k: v for k, v in r.items() if k not in FIELDS}))
    return out
