"""Message preparation Ollama applies before rendering.

Port of `chatMessagesForRequest` and `filterThinkTags` (server/routes.go, v0.40.7):
the SYSTEM layer is prepended when the conversation has no leading system
message, and for qwen3 / deepseek-r1 inline <think> blocks are stripped from
assistant turns before the last user turn.
"""

from __future__ import annotations

import copy
import re


def chat_messages_for_request(messages: list[dict], *, system: str | None, model_family: str = "",
                              model_name: str = "", preset_messages: list[dict] | None = None) -> list[dict]:
    if not messages:
        return []
    msgs = copy.deepcopy(preset_messages or []) + copy.deepcopy(messages)
    if messages[0]["role"] != "system" and system:
        msgs = [{"role": "system", "content": system}] + msgs
    return filter_think_tags(msgs, model_family, model_name)


_THINK = re.compile(r"^\s*<think>(.*?)(</think>\s*|$)", re.S)


def filter_think_tags(msgs: list[dict], model_family: str, model_name: str) -> list[dict]:
    """Strip a leading <think>...</think> from the content of earlier assistant turns.

    Approximates thinkingparser.Parser.AddContent for complete messages; the live
    tier checks it.
    """
    if model_family != "qwen3" and model_name.split(":")[0].split("/")[-1] != "deepseek-r1":
        return msgs
    last_user = max((i for i, m in enumerate(msgs) if m["role"] == "user"), default=-1)
    for i, m in enumerate(msgs):
        if i < last_user and m["role"] == "assistant":
            m["content"] = _THINK.sub("", m.get("content") or "", count=1)
    return msgs
