"""One BFCL item under one arm: generate, parse, execute (multi-turn), score.

The multi-turn loop follows BFCL's base_handler.inference_multi_turn_FC: each turn's user message is
added, the model is queried until it returns no decodable calls, every call is executed and its
result added as a tool message, and more than MAX_STEPS steps in a turn ends the entry.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass

from tda.h3 import bfcl
from tda.h3.runtime import GoSession, ModelCtx, Ollama, Reply, Worker
from tda.render.sandbox import JinjaSandbox

ARMS = ("A", "A1", "B")


@dataclass
class Clients:
    ollama: Ollama
    go: GoSession
    sb: JinjaSandbox
    worker: Worker
    record_a_prompt: bool = False  # spike: also fetch the exact prompt Ollama ran for arm A


def _sha(text: str | None) -> str | None:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16] if text is not None else None


def generate(arm: str, ctx: ModelCtx, cl: Clients, messages: list[dict], tools: list[dict],
             options: dict) -> tuple[Reply, bfcl.Parsed, str | None]:
    if arm == "A":
        body = ctx.ollama_messages(messages)
        prompt = cl.ollama.debug_render(ctx.serve_as, body, tools, options, ctx.think) if cl.record_a_prompt else None
        rep = cl.ollama.chat(ctx.serve_as, body, tools, options, ctx.think)
        return rep, bfcl.from_ollama(rep.message), prompt
    if arm == "A1":
        prompt = ctx.render_l3(cl.go, messages, tools)
    elif arm == "B":
        prompt = ctx.render_l0(cl.sb, messages, tools)
    else:
        raise ValueError(arm)
    rep = cl.ollama.raw(arm, ctx.serve_as, prompt, options)
    return rep, bfcl.PARSERS[ctx.parser](rep.text), prompt


def _step(rep: Reply, parsed: bfcl.Parsed, prompt: str | None, keep_prompt: bool) -> dict:
    d = asdict(rep)
    d.pop("arm")
    d["calls"] = parsed.calls
    d["notes"] = parsed.notes
    d["prompt_sha"] = _sha(prompt)
    if keep_prompt:
        d["prompt"] = prompt
    return d


def single_turn(entry: dict, category: str, arm: str, ctx: ModelCtx, cl: Clients, options: dict,
                keep_prompt: bool = True) -> dict:
    tools, names = bfcl.to_tools(entry["function"])
    messages = [m for turn in entry["question"] for m in turn]
    rep, parsed, prompt = generate(arm, ctx, cl, messages, tools, options)
    output = None if parsed.calls is None else bfcl.bfcl_output(parsed.calls, names)
    if category == "irrelevance":
        score = cl.worker.ok({"op": "score_irrelevance", "output": output})
    else:
        score = cl.worker.ok({"op": "score_ast", "category": category, "functions": entry["function"],
                              "output": output, "answer": entry["answer"]})
    return {"id": entry["id"], "category": category, "arm": arm, "valid": score["valid"],
            "error_type": score.get("error_type"), "step": _step(rep, parsed, prompt, keep_prompt)}


def multi_turn(entry: dict, arm: str, ctx: ModelCtx, cl: Clients, options: dict,
               keep_prompt: bool = False) -> dict:
    tools, names = bfcl.to_tools(entry["function"])
    ns = f"{ctx.serve_as}:{arm}"
    messages: list[dict] = []
    decoded: list[list[list[str]]] = []
    turns: list[list[dict]] = []
    force_quit = False
    try:
        for t, turn in enumerate(entry["question"]):
            messages += turn
            steps, turn_decoded = [], []
            count = 0
            while True:
                rep, parsed, prompt = generate(arm, ctx, cl, messages, tools, options)
                steps.append(_step(rep, parsed, prompt, keep_prompt))
                if not parsed.has_calls:  # decode failure or no calls: on to the next turn
                    messages += bfcl.history_messages(parsed, [], [], ctx.one_call_per_message)
                    break
                calls = [bfcl.call_string(names.get(c["name"], c["name"]), c["arguments"]) for c in parsed.calls]
                results = cl.worker.ok({"op": "exec", "ns": ns, "entry": entry, "calls": calls})["results"]
                steps[-1]["results"] = results
                turn_decoded.append(calls)
                ids = [bfcl.call_id(entry["id"], t, count, k) for k in range(len(parsed.calls))]
                messages += bfcl.history_messages(parsed, results, ids, ctx.one_call_per_message)
                count += 1
                if count > bfcl.MAX_STEPS:
                    force_quit = True
                    break
            turns.append(steps)
            decoded.append(turn_decoded)
            if force_quit:
                break
    finally:
        cl.worker.ok({"op": "drop", "ns": ns})
    if len(decoded) != len(entry["answer"]):
        score = {"valid": False, "error_type": "multi_turn:force_terminated"}
    else:
        score = cl.worker.ok({"op": "score_multi_turn", "entry": entry, "decoded": decoded,
                              "answer": entry["answer"]})
    return {"id": entry["id"], "category": "multi_turn_base", "arm": arm, "valid": score["valid"],
            "error_type": score.get("error_type"), "turns": turns}
