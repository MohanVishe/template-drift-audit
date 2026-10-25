"""H3 spike on one model (notes/H3-PLAN.md section 6). Arms A and A1 only.

Arm B is rendered and checked here but never generated: its results stay unseen until the
settings, parsers and analysis are frozen.

  1. Render every item both ways (L0 and L3): failures, leading BOS text, items where they match.
  2. Raw-mode checks: BOS handling, and whether tool tags survive in raw output.
  3. A vs A1 on a spread of single-turn items, plus a repeat of A1 for determinism.
  4. A vs A1 on a few multi-turn items: step-by-step agreement, longest prompt.
  5. Speed, and the time a full run would take.

Usage: python scripts/h3_spike.py [--per-category 10] [--multi-turn 5] [--out runs/h3-spike]
"""

from __future__ import annotations

import argparse
import json
import random
import re
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tda.h3 import bfcl  # noqa: E402
from tda.h3.run import Clients, multi_turn, single_turn  # noqa: E402
from tda.h3.runtime import GoSession, ModelCtx, Ollama, Worker  # noqa: E402
from tda.render.sandbox import JinjaSandbox  # noqa: E402

SINGLE = ["simple_python", "multiple", "parallel", "parallel_multiple", "irrelevance"]
HERMES_BLOCK = re.compile(r"<tool_call>\n.*?\n</tool_call>", re.S)
MODEL = {"package": "qwen2.5:latest", "serve_as": "qwen2.5:7b-instruct", "parser": "hermes"}


def spread(items: list, n: int) -> list:
    """n items evenly spaced through the list (deterministic)."""
    if n >= len(items):
        return list(items)
    step = len(items) / n
    return [items[int(i * step)] for i in range(n)]


def canon(calls) -> str:
    return json.dumps(calls, sort_keys=True)


def log(msg: str) -> None:
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-category", type=int, default=10)
    ap.add_argument("--multi-turn", type=int, default=5)
    ap.add_argument("--num-ctx", type=int, default=16384)
    ap.add_argument("--out", default=str(ROOT / "runs" / "h3-spike" / "qwen2.5"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    options = {"temperature": 0, "seed": 42, "num_ctx": args.num_ctx, "num_predict": 1024}

    p2 = json.loads((ROOT / "runs" / "p2-library" / "models" / "qwen2.5_latest.json").read_text(encoding="utf-8"))
    ctx = ModelCtx.load(MODEL["package"], MODEL["serve_as"], MODEL["parser"],
                        p2["target"]["upstream_repo"], p2["target"]["upstream_sha"])
    assert ctx.model_digest == p2["model_digest"], "registry digest differs from the one P2 audited"
    cl = Clients(Ollama(), GoSession(), JinjaSandbox(timeout=30), Worker(), record_a_prompt=True)
    summary: dict = {"model": MODEL, "model_digest": ctx.model_digest, "options": options,
                     "ollama": cl.ollama.version(), "go_helper": cl.go.ask({"op": "version"})["ollama"],
                     "bfcl": cl.worker.ok({"op": "version"}), "params": ctx.pkg.params,
                     "l0": f"{ctx.up.repo}@{ctx.up.sha[:12]}", "gguf_add_bos": ctx.add_bos,
                     "gguf_bos": ctx.gguf_special.get("bos_token"), "l0_bos": ctx.up.bos_token}
    log(f"ollama {summary['ollama']}, helper {summary['go_helper']}, bfcl {summary['bfcl']['bfcl_sha'][:12]}")

    entries = {c: cl.worker.ok({"op": "load", "category": c})["entries"] for c in SINGLE + ["multi_turn_base"]}

    # 1. Render every item both ways ---------------------------------------------------------
    renders = {"items": 0, "l0_fail": 0, "l3_fail": 0, "l0_starts_with_bos": 0, "identical": 0,
               "chars_l0": [], "chars_l3": [], "failures": []}
    for cat, es in entries.items():
        for e in es:
            tools, _ = bfcl.to_tools(e["function"])
            msgs = list(e["question"][0])
            renders["items"] += 1
            l0 = l3 = None
            try:
                l0 = ctx.render_l0(cl.sb, msgs, tools)
            except Exception as ex:  # noqa: BLE001
                renders["l0_fail"] += 1
                renders["failures"].append([e["id"], "L0", str(ex)[:200]])
            try:
                l3 = ctx.render_l3(cl.go, msgs, tools)
            except Exception as ex:  # noqa: BLE001
                renders["l3_fail"] += 1
                renders["failures"].append([e["id"], "L3", str(ex)[:200]])
            if l0 is not None:
                renders["chars_l0"].append(len(l0))
                bos = ctx.up.bos_token or ctx.gguf_special.get("bos_token") or ""
                renders["l0_starts_with_bos"] += bool(bos) and l0.startswith(bos)
            if l3 is not None:
                renders["chars_l3"].append(len(l3))
            renders["identical"] += l0 is not None and l0 == l3
    for k in ("chars_l0", "chars_l3"):
        v = renders.pop(k)
        renders[k] = {"median": statistics.median(v), "max": max(v)} if v else None
    summary["renders"] = renders
    log(f"renders: {renders['items']} items, L0 fail {renders['l0_fail']}, L3 fail {renders['l3_fail']}, "
        f"identical {renders['identical']}")

    # 2. Raw-mode checks ------------------------------------------------------------------------
    raw = {}
    one = {**options, "num_predict": 1}
    nonce = random.Random(7).randrange(10**9)
    probe = f"<|im_start|>user\nProbe {nonce}: say hi.<|im_end|>\n<|im_start|>assistant\n"
    a = cl.ollama.raw("probe", ctx.serve_as, probe, one)
    b = cl.ollama.raw("probe", ctx.serve_as, probe, one)
    raw["same_prompt_twice_prompt_tokens"] = [a.prompt_tokens, b.prompt_tokens]
    bos = ctx.gguf_special.get("bos_token") or ""
    if bos:
        c = cl.ollama.raw("probe", ctx.serve_as, bos + probe.replace(str(nonce), str(nonce + 1)), one)
        d = cl.ollama.raw("probe", ctx.serve_as, probe.replace(str(nonce), str(nonce + 2)), one)
        raw["bos_text_adds_tokens"] = c.prompt_tokens - d.prompt_tokens
    summary["raw_checks"] = raw
    log(f"raw checks: {raw}")

    # 3. A vs A1 on single-turn items ---------------------------------------------------------
    records = (out / "records.jsonl").open("w", encoding="utf-8")
    sample = {c: spread(entries[c], args.per_category) for c in SINGLE}
    compare = {"items": 0, "prompt_equal": 0, "same_generation": 0, "calls_equal": 0, "score_equal": 0,
               "parser_only": 0, "a1_tag_seen": 0, "a_has_calls": 0, "mismatches": []}
    timing: dict[str, list] = {}
    for cat, es in sample.items():
        for e in es:
            ra = single_turn(e, cat, "A", ctx, cl, options)
            r1 = single_turn(e, cat, "A1", ctx, cl, options)
            for r in (ra, r1):
                records.write(json.dumps(r, ensure_ascii=False) + "\n")
                timing.setdefault(f"{cat}:{r['arm']}", []).append(r["step"]["seconds"])
            sa, s1 = ra["step"], r1["step"]
            prompt_equal = sa["prompt"] == s1["prompt"]
            same_calls = canon(sa["calls"]) == canon(s1["calls"])
            # Ollama returns the text only when it found no calls; otherwise compare calls and length.
            same_gen = sa["output_tokens"] == s1["output_tokens"] and (
                same_calls if sa["calls"] else sa["text"].strip() == s1["text"].strip())
            # Same tokens, but Ollama's parser kept back calls that BFCL's parser accepts
            # (for example a call to a tool that was not offered): A's text is A1's without those blocks.
            parser_only = (sa["output_tokens"] == s1["output_tokens"] and not sa["calls"] and bool(s1["calls"])
                           and HERMES_BLOCK.sub("", s1["text"]).strip() == sa["text"].strip())
            compare["items"] += 1
            compare["prompt_equal"] += prompt_equal
            compare["same_generation"] += same_gen or parser_only
            compare["parser_only"] += parser_only
            compare["calls_equal"] += same_calls
            compare["score_equal"] += ra["valid"] == r1["valid"]
            compare["a1_tag_seen"] += "<tool_call>" in s1["text"]
            compare["a_has_calls"] += bool(sa["calls"])
            if not (same_gen and prompt_equal):
                compare["mismatches"].append({"id": e["id"], "prompt_equal": prompt_equal, "parser_only": parser_only,
                                              "tokens": [sa["output_tokens"], s1["output_tokens"]],
                                              "A": sa["calls"], "A1": s1["calls"],
                                              "A_valid": ra["valid"], "A1_valid": r1["valid"],
                                              "A_text": sa["text"][:300], "A1_text": s1["text"][:300]})
        log(f"{cat}: done")
    summary["single_turn"] = compare

    # determinism: each arm twice on the first two items of each category
    det = {"items": 0, "identical": {"A": 0, "A1": 0}}
    for cat, es in sample.items():
        for e in es[:2]:
            det["items"] += 1
            for arm in ("A", "A1"):
                r = [single_turn(e, cat, arm, ctx, cl, options, keep_prompt=False)["step"] for _ in range(2)]
                det["identical"][arm] += (r[0]["text"] == r[1]["text"] and canon(r[0]["calls"]) == canon(r[1]["calls"])
                                          and r[0]["output_tokens"] == r[1]["output_tokens"])
    summary["determinism"] = det
    log(f"single-turn: same generation {compare['same_generation']}/{compare['items']} "
        f"(parser-only {compare['parser_only']}), prompts equal {compare['prompt_equal']}/{compare['items']}; "
        f"determinism {det}")

    # 4. A vs A1 on multi-turn items ----------------------------------------------------------
    mt = {"items": 0, "steps": {"A": 0, "A1": 0}, "valid": {"A": 0, "A1": 0}, "max_prompt_tokens": 0,
          "steps_equal_items": 0, "step_prompts_compared": 0, "step_prompts_equal": 0,
          "first_divergence": [], "seconds": {"A": [], "A1": []}}
    for e in spread(entries["multi_turn_base"], args.multi_turn):
        res = {}
        for arm in ("A", "A1"):
            t0 = time.perf_counter()
            res[arm] = multi_turn(e, arm, ctx, cl, options, keep_prompt=True)
            mt["seconds"][arm].append(time.perf_counter() - t0)
            records.write(json.dumps(res[arm], ensure_ascii=False) + "\n")
            steps = [s for t in res[arm]["turns"] for s in t]
            for s in steps:
                timing.setdefault(f"multi_turn_step:{arm}", []).append(s["seconds"])
            mt["steps"][arm] += len(steps)
            mt["valid"][arm] += res[arm]["valid"]
            mt["max_prompt_tokens"] = max([mt["max_prompt_tokens"]] + [s["prompt_tokens"] for s in steps])
        pa = [s for t in res["A"]["turns"] for s in t]
        p1 = [s for t in res["A1"]["turns"] for s in t]
        sa, s1 = [canon(s["calls"]) for s in pa], [canon(s["calls"]) for s in p1]
        mt["items"] += 1
        mt["steps_equal_items"] += sa == s1
        k = next((i for i, (x, y) in enumerate(zip(sa, s1)) if x != y), min(len(sa), len(s1)))
        for x, y in zip(pa[:k + 1], p1[:k + 1]):  # prompts up to and including the first different step
            mt["step_prompts_compared"] += 1
            mt["step_prompts_equal"] += x["prompt"] == y["prompt"]
        if sa != s1:
            mt["first_divergence"].append({"id": e["id"], "step": k, "A": sa[k:k + 1], "A1": s1[k:k + 1],
                                           "prompt_equal": k < min(len(pa), len(p1)) and pa[k]["prompt"] == p1[k]["prompt"],
                                           "A_text": pa[k]["text"][:300] if k < len(pa) else None,
                                           "A1_text": p1[k]["text"][:300] if k < len(p1) else None})
        log(f"{e['id']}: A {res['A']['valid']} A1 {res['A1']['valid']}, steps equal {sa == s1}")
    summary["multi_turn"] = mt
    records.close()

    # 5. Speed ------------------------------------------------------------------------------------
    recs = [json.loads(line) for line in (out / "records.jsonl").open(encoding="utf-8")]
    steps = [r["step"] for r in recs if "step" in r] + [s for r in recs if "turns" in r for t in r["turns"] for s in t]
    gen_tok = sum(s["output_tokens"] for s in steps)
    gen_s = sum(s["eval_seconds"] for s in steps)
    pr_tok = sum(s["prompt_tokens"] for s in steps)
    pr_s = sum(s["prompt_seconds"] for s in steps)
    per_item = {k: statistics.mean(v) for k, v in timing.items()}
    full_single = sum(len(entries[c]) * statistics.mean([per_item[f"{c}:A"], per_item[f"{c}:A1"]]) for c in SINGLE)
    full_mt = len(entries["multi_turn_base"]) * statistics.mean(mt["seconds"]["A"] + mt["seconds"]["A1"]) \
        if mt["items"] else 0
    summary["speed"] = {"output_tokens_per_s": gen_tok / gen_s if gen_s else None,
                        "prompt_tokens_per_s": pr_tok / pr_s if pr_s else None,
                        "seconds_per_item": per_item,
                        "multi_turn_seconds_per_item": {k: statistics.mean(v) for k, v in mt["seconds"].items() if v},
                        "estimate_hours_per_arm": {"single_turn": full_single / 3600, "multi_turn": full_mt / 3600}}
    summary["cache"] = {"steps": len(steps), "steps_with_cached_tokens": sum(s.get("cached_tokens", 0) > 0 for s in steps),
                        "max_cached_tokens": max((s.get("cached_tokens", 0) for s in steps), default=0)}
    summary["gpu"] = [{"name": m["name"], "size": m["size"], "size_vram": m.get("size_vram"),
                       "context_length": m.get("context_length")} for m in cl.ollama.ps()]
    summary["accuracy_seen"] = {arm: {c: sum(r["valid"] for r in recs if r.get("category") == c and r["arm"] == arm)
                                      for c in SINGLE + ["multi_turn_base"]} for arm in ("A", "A1")}
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"speed {summary['speed']}")
    log(f"gpu {summary['gpu']}")
    cl.go.close()
    cl.worker.close()
    cl.sb.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
