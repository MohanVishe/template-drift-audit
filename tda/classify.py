"""Classify the differences between two rendered prompts of the same fixture.

Method: both renders are tokenised (special tokens, tags, words, punctuation,
whitespace runs) and diffed. Every changed hunk is assigned one class by
locating it against spans recovered from the fixture itself: tool definitions,
tool calls, tool results, reasoning, message contents, the template's default
system prompt, and the turn that holds the tools. The rules are ordered and
listed in `_classify_hunk`. Classes and severities follow labels/GUIDE.md.
"""

from __future__ import annotations

import difflib
import json
import re
from dataclasses import dataclass, field

NONE, MINOR, MATERIAL = "none", "minor", "material"
SEVERITY = {"IDENTICAL": NONE, "WHITESPACE": NONE, "BOS": NONE, "DATE": NONE, "JSON_SPACING": MINOR}
RANK = {NONE: 0, MINOR: 1, MATERIAL: 2}

BOS_TOKENS = ("<|begin_of_text|>", "<|endoftext|>", "<s>", "<bos>", "<|startoftext|>", "[gMASK]<sop>")
_TOKEN = re.compile(r"<\|[^|\s]{1,40}\|>|\[/?[A-Z_]{2,30}\]|</?[A-Za-z_][\w\-]{0,30}>|\s+|\w+|[^\w\s]")
_BOUNDARY = re.compile(r"<\|[^|\s]{1,40}\|>|\[/?(?:INST|SYSTEM_PROMPT|AVAILABLE_TOOLS|TOOL_RESULTS)\]|<(?:start|end)_of_turn>|</?s>")
_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b"
                   r"|\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}\b")
_THINK_TAG = re.compile(r"</?think>|<\|(?:begin|end)_of_thought\|>|<\|channel\|>analysis")
_STRUCTURAL_WORDS = {"system", "user", "assistant", "tool", "model", "ipython", "human", "gpt", "INST"}


def severity_of(classes) -> str:
    return max((SEVERITY.get(c, MATERIAL) for c in classes), key=RANK.get, default=NONE)


@dataclass
class Span:
    start: int
    end: int
    kind: str  # tool_def | tool_call | tool_result | reasoning | content | default_system
    is_json: bool = False
    parsed: object = None


@dataclass
class Side:
    text: str
    spans: list[Span] = field(default_factory=list)
    tool_turn: tuple[int, int] | None = None

    def of(self, kind: str) -> list[Span]:
        return [s for s in self.spans if s.kind == kind]


@dataclass
class Hunk:
    a: tuple[int, int]
    b: tuple[int, int]
    a_text: str
    b_text: str
    cls: str = ""


@dataclass
class Result:
    classes: list[str]
    severity: str
    hunks: list[Hunk]


# --- span recovery ---------------------------------------------------------------------

def _json_object_around(text: str, pos: int, window: int = 2500, want=None) -> tuple[int, int, object] | None:
    """Outermost JSON object (within `window` chars before pos) whose span covers pos."""
    dec = json.JSONDecoder()
    best = None
    lo = max(0, pos - window)
    for i in range(pos, lo - 1, -1):
        if text[i] != "{":
            continue
        try:
            obj, end = dec.raw_decode(text, i)
        except ValueError:
            continue
        if end > pos and (want is None or want(obj)):
            best = (i, end, obj)
    return best


def _line_span(text: str, pos: int) -> tuple[int, int]:
    s = text.rfind("\n", 0, pos) + 1
    e = text.find("\n", pos)
    return s, (len(text) if e < 0 else e)


def _inside(pos: int, spans: list[Span]) -> bool:
    return any(s.start <= pos < s.end for s in spans)


def _tool_defs(text: str, tools: list[dict]) -> list[Span]:
    spans: list[Span] = []
    for tool in tools or []:
        fn = tool.get("function", tool)
        anchor = fn.get("description") or fn.get("name")
        start = 0
        while (p := text.find(anchor, start)) >= 0:
            start = p + len(anchor)
            if _inside(p, spans):
                continue
            found = _json_object_around(text, p, want=lambda o, n=fn["name"]: n in json.dumps(o))
            if found:
                spans.append(Span(found[0], found[1], "tool_def", True, found[2]))
            else:
                s, e = _line_span(text, p)
                spans.append(Span(s, e, "tool_def", False))
    return sorted(spans, key=lambda s: s.start)


def _find_call(text: str, call: dict, cursor: int, defs: list[Span]) -> Span | None:
    fn = call.get("function", call)
    name, args = fn["name"], fn.get("arguments")
    if isinstance(args, str):
        args = json.loads(args)
    start = cursor
    while (p := text.find(name, start)) >= 0:
        start = p + len(name)
        if _inside(p, defs):
            continue
        # the call's JSON either contains the name, or follows it (name-then-arguments formats)
        found = _json_object_around(text, p, window=300, want=lambda o: isinstance(o, dict) and name in json.dumps(o))
        if found:
            return Span(found[0], found[1], "tool_call", True, found[2])
        q = text.find("{", p, p + 200)
        if q >= 0:
            try:
                obj, end = json.JSONDecoder().raw_decode(text, q)
                if obj == args:
                    return Span(p, end, "tool_call", True, obj)
            except ValueError:
                pass
        s, e = _line_span(text, p)
        if args is not None and all(str(v) in text[p:e] for v in args.values()):
            return Span(p, e, "tool_call", False)
    return None


def recover(text: str, messages: list[dict], tools: list[dict] | None, default_system: list[str]) -> Side:
    side = Side(text)
    defs = _tool_defs(text, tools)
    side.spans += defs
    for ds in default_system:
        start = 0
        while (p := text.find(ds, start)) >= 0:
            side.spans.append(Span(p, p + len(ds), "default_system"))
            start = p + len(ds)

    cursor = 0
    for m in messages:
        kind = "tool_result" if m["role"] == "tool" else "content"
        reasoning = m.get("reasoning_content") or m.get("thinking")
        if reasoning:
            p = text.find(reasoning, cursor)
            if p >= 0:
                side.spans.append(Span(p, p + len(reasoning), "reasoning"))
                cursor = p + len(reasoning)
        content = m.get("content") or ""
        if content:
            p = text.find(content, cursor)
            while p >= 0 and _inside(p, defs):
                p = text.find(content, p + 1)
            if p >= 0:
                side.spans.append(Span(p, p + len(content), kind))
                cursor = p + len(content)
        for call in m.get("tool_calls") or []:
            span = _find_call(text, call, cursor, defs)
            if span:
                side.spans.append(span)
                cursor = span.end

    if defs:
        before = [b.end() for b in _BOUNDARY.finditer(text, 0, defs[0].start)]
        after = _BOUNDARY.search(text, defs[-1].end)
        side.tool_turn = (before[-1] if before else 0, after.start() if after else len(text))
    return side


# --- hunk classification ---------------------------------------------------------------

def _overlaps(rng: tuple[int, int], spans: list[Span]) -> list[Span]:
    a, b = rng
    if a == b:  # insertion point: must fall strictly inside
        return [s for s in spans if s.start < a < s.end]
    return [s for s in spans if a < s.end and s.start < b]


def _near(rng: tuple[int, int], spans: list[Span], dist: int) -> tuple[int, Span] | None:
    a, b = rng
    best = None
    for s in spans:
        d = 0 if (a < s.end and s.start < b) else min(abs(a - s.end), abs(s.start - b), abs(a - s.start), abs(b - s.end))
        if d <= dist and (best is None or d < best[0]):
            best = (d, s)
    return best


def _canon(obj) -> str:
    # Key order is kept: a reordered schema is a different prompt. Spacing and string escapes are not.
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def _same_json(A: Side, B: Side, kind: str) -> bool:
    pa, pb = [s.parsed for s in A.of(kind)], [s.parsed for s in B.of(kind)]
    return (len(pa) == len(pb) and all(s.is_json for s in A.of(kind) + B.of(kind))
            and all(_canon(x) == _canon(y) for x, y in zip(pa, pb)))


def _defs_verdict(A: Side, B: Side) -> str:
    if any(not s.is_json for s in A.of("tool_def") + B.of("tool_def")):
        return "TOOL_SCHEMA_NOT_JSON"
    return "JSON_SPACING" if _same_json(A, B, "tool_def") else "TOOL_SCHEMA"


def _classify_hunk(h: Hunk, A: Side, B: Side) -> str:
    changed = h.a_text + h.b_text
    both = lambda kind: _overlaps(h.a, A.of(kind)) + _overlaps(h.b, B.of(kind))  # noqa: E731

    # 1. whitespace only: inside tool JSON it takes the verdict of the definitions or calls
    if not changed.strip():
        if both("tool_def"):
            return _defs_verdict(A, B)
        if both("tool_call"):
            return "JSON_SPACING" if _same_json(A, B, "tool_call") else "TOOL_CALL"
        return "WHITESPACE"
    # 2. an injected date
    if _DATE.search(changed):
        return "DATE"
    # 3. a BOS token at the very start
    if h.a[0] == 0 and h.b[0] == 0 and changed.strip() in BOS_TOKENS:
        return "BOS"
    # 4. the template's own default system prompt
    if both("default_system"):
        return "DEFAULT_SYSTEM"
    # 5. tool definitions
    if both("tool_def"):
        return _defs_verdict(A, B)
    # 6. tool calls
    if both("tool_call"):
        return "JSON_SPACING" if _same_json(A, B, "tool_call") else "TOOL_CALL"
    # 7. tool results
    if both("tool_result"):
        return "TOOL_RESULT"
    # 8. reasoning
    if both("reasoning") or _THINK_TAG.search(changed):
        return "THINKING"
    # 9. message text
    if both("content"):
        return "CONTENT"
    # 10. anything else inside the turn that carries the tool definitions: tool instructions
    for side, rng in ((A, h.a), (B, h.b)):
        if side.tool_turn and side.tool_turn[0] <= rng[0] and rng[1] <= side.tool_turn[1]:
            return "TOOL_SCHEMA"
    # 11. markers next to a tool call or result
    near = [(n, k) for k in ("tool_call", "tool_result")
            for n in [_near(h.a, A.of(k), 40), _near(h.b, B.of(k), 40)] if n]
    if near:
        return "TOOL_CALL" if min(near, key=lambda x: x[0][0])[1] == "tool_call" else "TOOL_RESULT"
    # 12. role markers and turn structure; otherwise unexplained
    words = set(re.findall(r"[A-Za-z_]+", _BOUNDARY.sub(" ", changed)))
    if words <= _STRUCTURAL_WORDS:
        return "STRUCTURE"
    return "OTHER"


def _hunks(a: str, b: str) -> list[Hunk]:
    ta, tb = _TOKEN.findall(a), _TOKEN.findall(b)
    oa = [0]
    for t in ta:
        oa.append(oa[-1] + len(t))
    ob = [0]
    for t in tb:
        ob.append(ob[-1] + len(t))
    hunks = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes():
        if op != "equal":
            hunks.append(Hunk((oa[i1], oa[i2]), (ob[j1], ob[j2]), a[oa[i1]:oa[i2]], b[ob[j1]:ob[j2]]))
    return hunks


def default_system_texts(f01_render: str, f01_messages: list[dict]) -> list[str]:
    """Prose a template adds to a bare one-turn conversation: its default system prompt."""
    text = f01_render
    for m in f01_messages:
        if m.get("content"):
            text = text.replace(m["content"], "\x00")
    out = []
    for seg in re.split(r"\x00|\n", _BOUNDARY.sub("\x00", text)):
        seg = seg.strip()
        if len(re.findall(r"\w+", seg)) >= 3:
            out.append(seg)
    return out


def classify(a: str | None, b: str | None, messages: list[dict], tools: list[dict] | None, *,
             default_system: list[str] = ()) -> Result:
    if a is None or b is None:
        return Result(["RENDER_ERROR"], MATERIAL, [])
    if a == b:
        return Result(["IDENTICAL"], NONE, [])
    A = recover(a, messages, tools, list(default_system))
    B = recover(b, messages, tools, list(default_system))
    hunks = _hunks(a, b)
    for h in hunks:
        h.cls = _classify_hunk(h, A, B)
    classes = {h.cls for h in hunks}
    if tools and bool(A.of("tool_def")) != bool(B.of("tool_def")):
        classes -= {"TOOL_SCHEMA", "TOOL_SCHEMA_NOT_JSON"}
        classes.add("TOOLS_DROPPED")
    return Result(sorted(classes), severity_of(classes), hunks)
