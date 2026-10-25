"""BFCL items as chat requests: tool conversion, call strings and output parsers.

Pure functions, no I/O. The rules follow BFCL at the pinned commit (6ea57973c7a6):
- tools: `model_handler/utils.py` convert_to_tool and _cast_to_openai_type, OpenAI-completions style
  (dots in names become underscores, the tool is wrapped as {"type": "function", "function": ...});
- call strings: utils.convert_to_function_call;
- Hermes-style output (Qwen): local_inference/qwen_fc.py _extract_tool_calls.
The same objects go to every arm, so any difference between arms comes from the prompt layout.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import re
from dataclasses import dataclass, field

# bfcl_eval/constants/type_mappings.py GORILLA_TO_OPENAPI
GORILLA_TO_OPENAPI = {
    "integer": "integer", "number": "number", "float": "number", "string": "string",
    "boolean": "boolean", "bool": "boolean", "array": "array", "list": "array", "dict": "object",
    "object": "object", "tuple": "array", "any": "string", "byte": "integer", "short": "integer",
    "long": "integer", "double": "number", "char": "string", "ArrayList": "array", "Array": "array",
    "HashMap": "object", "Hashtable": "object", "Queue": "array", "Stack": "array", "Any": "string",
    "String": "string", "Bigint": "integer",
}

MAX_STEPS = 20  # bfcl_eval/constants/default_prompts.py MAXIMUM_STEP_LIMIT


def _type(t: str | None) -> str:
    return GORILLA_TO_OPENAPI.get(t or "string", "string")


def _cast(properties: dict) -> dict:
    for value in properties.values():
        if "type" not in value:
            value["type"] = "string"
        else:
            if value["type"] == "float":
                value["format"] = "float"
                value["description"] = value.get("description", "") + " This is a float type value."
            value["type"] = _type(value["type"])
        if value["type"] in ("array", "object"):
            if "properties" in value:
                value["properties"] = _cast(value["properties"])
            elif "items" in value:
                items = value["items"]
                items["type"] = _type(items.get("type"))
                if items["type"] == "array" and "items" in items:
                    items["items"]["type"] = _type(items["items"].get("type"))
                elif items["type"] == "object" and "properties" in items:
                    items["properties"] = _cast(items["properties"])
    return properties


def to_tools(functions: list[dict]) -> tuple[list[dict], dict[str, str]]:
    """BFCL function docs -> OpenAI-style tools, plus a map from tool name back to BFCL's name.

    The non-standard `response` field of the multi-turn docs is left out: it is not part of an
    OpenAI tool, so a user would not send it."""
    tools, names = [], {}
    for f in copy.deepcopy(functions):
        name = f["name"].replace(".", "_")
        names[name] = f["name"]
        params = f.get("parameters") or {"type": "dict", "properties": {}}
        params["type"] = "object"
        params["properties"] = _cast(params.get("properties", {}))
        tools.append({"type": "function",
                      "function": {"name": name, "description": f.get("description", ""), "parameters": params}})
    return tools, names


def call_string(name: str, arguments: dict) -> str:
    """utils.convert_to_function_call: `name(k=repr(v),...)`."""
    return f"{name}({','.join(f'{k}={v!r}' for k, v in arguments.items())})"


@dataclass
class Parsed:
    """One model reply. `calls` is None when the reply could not be decoded as tool calls."""

    text: str
    calls: list[dict] | None = None  # [{"name": ..., "arguments": {...}}]
    content: str = ""
    notes: list[str] = field(default_factory=list)

    @property
    def has_calls(self) -> bool:
        return bool(self.calls)

    def history_message(self) -> dict:
        """The assistant turn added to the chat history (qwen_fc: content is empty when there are calls)."""
        if self.has_calls:
            return {"role": "assistant", "content": "",
                    "tool_calls": [{"id": "", "type": "function",
                                    "function": {"name": c["name"], "arguments": c["arguments"]}}
                                   for c in self.calls]}
        return {"role": "assistant", "content": self.content}


_HERMES = re.compile(r"<tool_call>\n(.*?)\n</tool_call>", re.S)


def parse_hermes(text: str) -> Parsed:
    blocks, notes = [], []
    for raw in _HERMES.findall(text):
        try:
            blocks.append(json.loads(raw))
        except ValueError:
            notes.append("skipped a <tool_call> block that is not JSON")
    p = Parsed(text, content=text, notes=notes)
    if all(isinstance(b, dict) and isinstance(b.get("name"), str) and isinstance(b.get("arguments"), dict)
           for b in blocks):
        p.calls = [{"name": b["name"], "arguments": b["arguments"]} for b in blocks]
    else:
        p.notes.append("a block lacks a name or an arguments object")
    return p


_BAD = (ValueError, SyntaxError, TypeError, RecursionError, MemoryError)


def _loads(text: str):
    """JSON, or a Python literal. BFCL's Llama decoder uses eval(); this never evaluates code."""
    try:
        return json.loads(text)
    except ValueError:
        return ast.literal_eval(text)


def _calls(objs, args_key: str) -> list[dict] | None:
    if not all(isinstance(o, dict) and isinstance(o.get("name"), str) and isinstance(o.get(args_key), dict)
               for o in objs):
        return None
    return [{"name": o["name"], "arguments": o[args_key]} for o in objs]


def _semicolon_json(body: str) -> list | None:
    """JSON values joined by ';', read one value at a time so a ';' inside a string stays put."""
    dec, out, i = json.JSONDecoder(), [], 0
    while True:
        try:
            obj, i = dec.raw_decode(body, i)
        except ValueError:
            return None
        out.append(obj)
        rest = body[i:].lstrip()
        if not rest:
            return out
        if not rest.startswith(";"):
            return None
        i = len(body) - len(rest) + 1
        while i < len(body) and body[i].isspace():
            i += 1
        if i == len(body):
            return out


def parse_llama_json(text: str) -> Parsed:
    """Llama 3.1 custom tools (local_inference/llama_3_1.py decode_execute): an optional
    <|python_tag|>, then {"name": ..., "parameters": {...}}, a list of them, or several joined by ';'.
    Differs from BFCL only where BFCL would fail: no eval(), and a ';' inside a string is kept."""
    body = text.replace("<|python_tag|>", "").strip()
    p = Parsed(text, content=text)
    try:
        objs = _loads(body)
    except _BAD:
        if ";" not in body:
            p.notes.append("not a JSON call")
            return p
        objs = _semicolon_json(body)
        if objs is None:
            p.notes.append("not a JSON call")
            return p
    objs = [objs] if isinstance(objs, dict) else objs
    p.calls = _calls(objs, "parameters") if isinstance(objs, list) else None
    if p.calls is None:
        p.notes.append("not {name, parameters} objects")
    return p


def parse_mistral(text: str) -> Parsed:
    """Mistral v0.3 (local_inference/mistral_fc.py): a JSON list of {"name", "arguments"}. In raw
    mode the [TOOL_CALLS] control token may or may not appear in the text, so a leading one is dropped."""
    body = text.strip()
    if body.startswith("[TOOL_CALLS]"):
        body = body[len("[TOOL_CALLS]"):].strip()
    p = Parsed(text, content=text)
    try:
        objs = json.loads(body)
    except ValueError:
        p.notes.append("not a JSON list")
        return p
    p.calls = _calls(objs, "arguments") if isinstance(objs, list) else None
    if p.calls is None:
        p.notes.append("not a list of {name, arguments} objects")
    return p


PARSERS = {"hermes": parse_hermes, "llama_json": parse_llama_json, "mistral": parse_mistral}


def call_id(*parts) -> str:
    """A 9-character alphanumeric id (Mistral's template requires exactly that), fixed by position
    so every arm gives the same call the same id."""
    digest = hashlib.sha256(":".join(map(str, parts)).encode()).digest()
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(alphabet[b % len(alphabet)] for b in digest[:9])


def history_messages(parsed: Parsed, results: list[str], ids: list[str], one_call_per_message: bool) -> list[dict]:
    """The assistant turn and its tool results, as added to the chat history.

    With one_call_per_message, N calls become N (assistant call, tool result) pairs: Llama 3.1's own
    template refuses an assistant message with more than one call. The same rule applies in every
    arm, so the conversation content never differs between arms."""
    if not parsed.has_calls:
        return [parsed.history_message()]
    calls = [{"id": i, "type": "function", "function": {"name": c["name"], "arguments": c["arguments"]}}
             for c, i in zip(parsed.calls, ids)]
    tools = [{"role": "tool", "content": r, "name": c["name"], "tool_call_id": i}
             for c, r, i in zip(parsed.calls, results, ids)]
    if one_call_per_message:
        out = []
        for call, tool in zip(calls, tools):
            out += [{"role": "assistant", "content": "", "tool_calls": [call]}, tool]
        return out
    return [{"role": "assistant", "content": "", "tool_calls": calls}] + tools


def from_ollama(message: dict) -> Parsed:
    """Arm A: the calls Ollama's own parser returned for /api/chat."""
    content = message.get("content") or ""
    calls = [{"name": tc["function"]["name"], "arguments": tc["function"].get("arguments") or {}}
             for tc in message.get("tool_calls") or []]
    return Parsed(content, calls=calls, content=content)


def bfcl_output(calls: list[dict], names: dict[str, str]) -> list[dict]:
    """[{BFCL name: arguments}], the decoded form BFCL's AST checker takes."""
    return [{names.get(c["name"], c["name"]): c["arguments"]} for c in calls]
