"""Which prompt source Ollama runs for a model: a port of its selection rule.

Ported from Ollama v0.40.7 (MIT): `selectedTemplateSource`, `shouldUseGoTemplate`,
`shouldPreferChatTemplate` and helpers in server/images.go and server/routes.go,
`TemplateSupportsThinking` in thinking/template.go.

The chat-template checks are plain substring tests, so they port exactly. The
Go-template side needs the parsed template (its identifiers and inferred
thinking tags). The Go helper supplies those exactly; `approx_go_info` is a
regex fallback that is marked as such in every result that uses it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

OLLAMA_VERSION = "v0.40.7"

TOOLS, INSERT, THINKING = "tools", "insert", "thinking"


@dataclass(frozen=True)
class GoTemplateInfo:
    raw: str
    vars: frozenset[str]  # lower-cased identifiers, as template.Vars() returns them
    think_tags: tuple[str, str]  # thinking.InferTags; ("", "") when none
    exact: bool  # True when computed by Ollama's own code (Go helper)


@dataclass(frozen=True)
class Selection:
    source: str  # renderer_parser | renderer | parser | harmony | go_template | gguf_chat_template | none
    prefer_chat_template: bool
    go_caps: tuple[str, ...]
    chat_caps: tuple[str, ...]
    exact: bool


# --- chat (Jinja) template side: exact ports -------------------------------------------

def chat_has_tool_support(t: str) -> bool:
    return "tools" in t or "tool_call" in t


def chat_has_tool_round_trip(t: str) -> bool:
    if not chat_has_tool_support(t):
        return False
    tool_calls = "tool_calls" in t or "assistant_tool_call" in t
    return tool_calls and any(s in t for s in (
        "tool_response", "tool_results",
        "role'] == 'tool'", "role'] == \"tool\"", "role\"] == 'tool'", "role\"] == \"tool\"",
        "message.role == 'tool'", "message.role == \"tool\"", "ipython",
    ))


def chat_has_tool_call_ids(t: str) -> bool:
    return "[CALL_ID]" in t and "tool_call.id" in t


def chat_supports_thinking(t: str) -> bool:
    if "<think>" in t and "</think>" in t:
        return True
    return (("content.split('</think>')" in t or 'content.split("</think>")' in t)
            and "reasoning_content" not in t and "<SPECIAL_12>" not in t)


def chat_caps(t: str) -> list[str]:
    caps: list[str] = []
    if not t:
        return caps
    if chat_has_tool_support(t):
        caps.append(TOOLS)
    if chat_supports_thinking(t):
        caps.append(THINKING)
    return caps


# --- Go template side ------------------------------------------------------------------

_ACTION = re.compile(r"\{\{-?(.*?)-?\}\}", re.S)
_CHAIN = re.compile(r"(\$[A-Za-z0-9_]*|(?<![A-Za-z0-9_)\]])\.[A-Za-z_][A-Za-z0-9_]*)((?:\.[A-Za-z_][A-Za-z0-9_]*)*)")


def approx_go_info(raw: str) -> GoTemplateInfo:
    """Regex stand-in for template.Vars() and thinking.InferTags(). Not exact."""
    idents: set[str] = set()
    for action in _ACTION.findall(raw):
        action = re.sub(r'"(?:\\.|[^"\\])*"', '""', action)  # ignore string literals
        for head, rest in _CHAIN.findall(action):
            parts = ([head] if head.startswith("$") else [head[1:]]) + [p for p in rest.split(".") if p]
            idents.update(p.lower() for p in parts)
    tags = ("", "")
    m = re.search(r"\{\{-?\s*if\s+\.Thinking\s*-?\}\}(.*?)\{\{-?\s*\.Thinking\s*-?\}\}(.*?)\{\{-?\s*end", raw, re.S)
    if m and re.search(r"range[^}]*\.Messages", raw):
        tags = (m.group(1).strip(), m.group(2).strip())
    return GoTemplateInfo(raw, frozenset(idents), tags, exact=False)


def go_caps(info: GoTemplateInfo | None) -> list[str]:
    if info is None:
        return []
    caps: list[str] = []
    if "tools" in info.vars:
        caps.append(TOOLS)
    if "suffix" in info.vars:
        caps.append(INSERT)
    if info.think_tags[0] and info.think_tags[1]:
        caps.append(THINKING)
    return caps


def go_has_tool_round_trip(info: GoTemplateInfo | None) -> bool:
    if info is None or "tools" not in info.vars or "toolcalls" not in info.vars:
        return False
    return 'eq .Role "tool"' in info.raw or "tool_response" in info.raw or "TOOL_RESULTS" in info.raw


def should_prefer_chat_template(chat: str, ccaps: list[str], go: GoTemplateInfo | None, gcaps: list[str]) -> bool:
    if len(ccaps) > len(gcaps):
        return not go_has_tool_round_trip(go) or chat_has_tool_round_trip(chat)
    if set(ccaps) != set(gcaps) or len(ccaps) != len(gcaps) or TOOLS not in ccaps or TOOLS not in gcaps:
        return False
    if chat_has_tool_call_ids(chat):
        return True
    return chat_has_tool_round_trip(chat) and not go_has_tool_round_trip(go)


def uses_harmony(model_family: str, go_raw: str | None) -> bool:
    return (model_family in ("gptoss", "gpt-oss") and go_raw is not None
            and "<|start|>" in go_raw and "<|end|>" in go_raw)


def select_source(
    *,
    renderer: str = "",
    parser: str = "",
    model_family: str = "",
    go: GoTemplateInfo | None = None,
    gguf_chat_template: str = "",
    go_template_env: bool | None = None,  # OLLAMA_GO_TEMPLATE; None = unset (default true)
) -> Selection:
    """Return the prompt source Ollama would run, for the default environment unless told otherwise."""
    has_go = go is not None
    harmony = uses_harmony(model_family, go.raw if go else None)
    ccaps = chat_caps(gguf_chat_template)
    gcaps = go_caps(go)
    prefer = (go_template_env is None and has_go and bool(gguf_chat_template) and not renderer
              and not parser and not harmony
              and should_prefer_chat_template(gguf_chat_template, ccaps, go, gcaps))

    if not has_go:
        use_go = False
    elif go_template_env is not None:
        use_go = go_template_env
    else:
        use_go = not prefer

    if renderer and parser:
        source = "renderer_parser"
    elif renderer:
        source = "renderer"
    elif parser:
        source = "parser"
    elif harmony:
        source = "harmony"
    elif use_go:
        source = "go_template"
    elif gguf_chat_template:
        source = "gguf_chat_template"
    else:
        source = "none"
    return Selection(source, prefer, tuple(gcaps), tuple(ccaps), exact=go is None or go.exact)
