"""The model author's own chat template (layer L0), pinned to a commit.

transformers looks for a template in this order: `chat_template.jinja`, then
`chat_template.json`, then the `chat_template` key of `tokenizer_config.json`.
The same order is used here, and the file that supplied it is recorded.
"""

from __future__ import annotations

import json
import urllib.error
from dataclasses import dataclass

from tda.http import Fetcher

HF = "https://huggingface.co"


@dataclass
class UpstreamTemplate:
    repo: str
    sha: str
    file: str
    templates: dict[str, str]  # "default" plus any named templates (e.g. "tool_use")
    bos_token: str | None
    eos_token: str | None

    @property
    def default(self) -> str:
        return self.templates["default"]


def _token(v) -> str | None:
    if isinstance(v, dict):  # AddedToken serialisation
        return v.get("content")
    return v


def _as_templates(value) -> dict[str, str]:
    if isinstance(value, str):
        return {"default": value}
    if isinstance(value, list):  # [{"name": ..., "template": ...}]
        return {t["name"]: t["template"] for t in value}
    raise ValueError(f"unexpected chat_template type {type(value).__name__}")


def resolve_sha(f: Fetcher, repo: str, revision: str = "main") -> str:
    return f.get_json(f"{HF}/api/models/{repo}/revision/{revision}")["sha"]


def load_from_api(f: Fetcher, repo: str, sha: str) -> UpstreamTemplate:
    """The same template, as the Hub's revision API reports it. Used for gated repos, whose files
    need a token with the licence accepted; the API returns the template text without one."""
    cfg = f.get_json(f"{HF}/api/models/{repo}/revision/{sha}").get("config", {})
    tok_cfg = cfg.get("tokenizer_config", {})
    bos, eos = _token(tok_cfg.get("bos_token")), _token(tok_cfg.get("eos_token"))
    if cfg.get("chat_template_jinja"):
        return UpstreamTemplate(repo, sha, "api:chat_template.jinja", {"default": cfg["chat_template_jinja"]}, bos, eos)
    if "chat_template" in tok_cfg:
        return UpstreamTemplate(repo, sha, "api:tokenizer_config.json", _as_templates(tok_cfg["chat_template"]), bos, eos)
    raise LookupError(f"{repo}@{sha}: the revision API reports no chat template")


def load(f: Fetcher, repo: str, sha: str) -> UpstreamTemplate:
    def file(name: str) -> bytes | None:
        return f.get_optional(f"{HF}/{repo}/resolve/{sha}/{name}")

    try:
        tok_cfg = json.loads(file("tokenizer_config.json") or b"{}")
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):  # gated
            return load_from_api(f, repo, sha)
        raise
    bos, eos = _token(tok_cfg.get("bos_token")), _token(tok_cfg.get("eos_token"))

    if (jinja := file("chat_template.jinja")) is not None:
        return UpstreamTemplate(repo, sha, "chat_template.jinja", {"default": jinja.decode()}, bos, eos)
    if (cj := file("chat_template.json")) is not None:
        templates = _as_templates(json.loads(cj)["chat_template"])
        return UpstreamTemplate(repo, sha, "chat_template.json", templates, bos, eos)
    if "chat_template" in tok_cfg:
        return UpstreamTemplate(repo, sha, "tokenizer_config.json", _as_templates(tok_cfg["chat_template"]), bos, eos)
    raise LookupError(f"{repo}@{sha} has no chat template")


@dataclass(frozen=True)
class Commit:
    sha: str
    date: str
    title: str


def history(f: Fetcher, repo: str, revision: str = "main") -> list[Commit]:
    """The repo's commits, newest first (one page of the Hub API)."""
    return [Commit(c["id"], c.get("date", ""), c.get("title", ""))
            for c in f.get_json(f"{HF}/api/models/{repo}/commits/{revision}")]


def _squash(t: str) -> str:
    return " ".join(t.split())


def revision_matching(f: Fetcher, repo: str, template: str) -> tuple[str, Commit | None, Commit | None, int]:
    """Find the newest commit whose default template is `template`: the author's template as it was
    when a GGUF was converted. Returns (match kind "exact" | "whitespace" | "none", that commit, the
    newer commit that replaced the template, commits checked)."""
    commits = history(f, repo)
    loose = newer = None
    for c in commits:
        try:
            t = load(f, repo, c.sha).default
        except (LookupError, ValueError, KeyError):
            continue  # commits before the repo had a chat template
        if t == template:
            return "exact", c, newer, len(commits)
        if loose is None and _squash(t) == _squash(template):
            loose = (c, newer)
        newer = c
    return ("whitespace", *loose, len(commits)) if loose else ("none", None, None, len(commits))
