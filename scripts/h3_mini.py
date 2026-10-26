"""H3 mini-test: one model, single-turn BFCL tiers only, arms A1 (Ollama's layout) and B (the
maker's layout). Same server, same weights, same raw transport, same parser: B - A1 is the
layout effect alone. Frozen settings from tda/h3/models.py.

Writes one JSON line per (item, arm) to <out>/records.jsonl and resumes from it. After the main
pass it reruns a spread of items in both arms to check determinism.

--arms A runs arm A instead: the same items through Ollama's /api/chat and Ollama's own parser,
the path everyday use takes. Its files get a suffix (records-A.jsonl, repeat-A.jsonl, meta-A.json),
so the A1/B data stays as published. Arm A also fetches the prompt Ollama ran, so its prompt_sha
can be checked against A1's.

Usage: python scripts/h3_mini.py [--model qwen2.5:7b-instruct] [--out runs/h3-mini/qwen2.5] [--repeat 20]
                                 [--arms A1,B]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tda.h3.models import MODELS, OPTIONS  # noqa: E402
from tda.h3.run import Clients, single_turn  # noqa: E402
from tda.h3.runtime import GoSession, ModelCtx, Ollama, Worker  # noqa: E402
from tda.render.sandbox import JinjaSandbox  # noqa: E402

SINGLE = ["simple_python", "multiple", "parallel", "parallel_multiple", "irrelevance"]
ARMS = ("A1", "B")


def same(r: dict) -> str:
    """What a repeat must reproduce: the raw text, and for arm A the tool calls Ollama parsed."""
    return json.dumps([r["text"], r["calls"]], ensure_ascii=False, sort_keys=True)


def log(msg: str) -> None:
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def record(r: dict) -> dict:
    s = r["step"]
    return {"id": r["id"], "category": r["category"], "arm": r["arm"], "valid": r["valid"],
            "error_type": r["error_type"], "calls": s["calls"], "text": s["text"], "notes": s["notes"],
            "prompt_sha": s["prompt_sha"], "prompt_tokens": s["prompt_tokens"],
            "output_tokens": s["output_tokens"], "cached_tokens": s["cached_tokens"],
            "done_reason": s["done_reason"], "seconds": round(s["seconds"], 3)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5:7b-instruct")
    ap.add_argument("--out", default=str(ROOT / "runs" / "h3-mini" / "qwen2.5"))
    ap.add_argument("--repeat", type=int, default=20)
    ap.add_argument("--arms", default=",".join(ARMS))
    args = ap.parse_args()
    arms = tuple(args.arms.split(","))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    sfx = "" if arms == ARMS else "-" + "".join(arms)
    rec_path, rep_path, meta_path = out / f"records{sfx}.jsonl", out / f"repeat{sfx}.jsonl", out / f"meta{sfx}.json"

    spec = MODELS[args.model]
    ctx = ModelCtx.from_spec(spec)
    cl = Clients(Ollama(), GoSession(), JinjaSandbox(timeout=30), Worker(), record_a_prompt="A" in arms)
    try:
        meta = {"model": args.model, "spec": spec.__dict__, "options": OPTIONS, "ollama": cl.ollama.version(),
                "bfcl": cl.worker.ok({"op": "version"}), "model_digest": ctx.model_digest,
                "runtime": ctx.check_runtime(cl.ollama, OPTIONS), "started": time.strftime("%Y-%m-%d %H:%M:%S")}
        meta["arms"] = arms
        meta_path.write_text(json.dumps(meta, indent=1), encoding="utf-8", newline="\n")
        log(f"meta {json.dumps(meta['runtime'])}")

        done = set()
        if rec_path.exists():
            for line in rec_path.read_text(encoding="utf-8").splitlines():
                d = json.loads(line)
                done.add((d["id"], d["arm"]))
        entries = {c: cl.worker.ok({"op": "load", "category": c})["entries"] for c in SINGLE}
        total = sum(len(v) for v in entries.values()) * len(arms)
        n = len(done)
        t0 = time.perf_counter()
        with rec_path.open("a", encoding="utf-8", newline="\n") as f:
            for cat, es in entries.items():
                for e in es:
                    for arm in arms:
                        if (e["id"], arm) in done:
                            continue
                        r = record(single_turn(e, cat, arm, ctx, cl, OPTIONS, keep_prompt=False))
                        f.write(json.dumps(r, ensure_ascii=False) + "\n")
                        f.flush()
                        n += 1
                        if n % 100 == 0:
                            rate = (time.perf_counter() - t0) / max(1, n - len(done))
                            log(f"{n}/{total}  ~{(total - n) * rate / 60:.0f} min left")
        log("main pass done")

        # Determinism: rerun an even spread of items in both arms, compare the raw text.
        flat = [(c, e) for c, es in entries.items() for e in es]
        step = max(1, len(flat) // args.repeat)
        first = {(d["id"], d["arm"]): d for d in map(json.loads, rec_path.read_text(encoding="utf-8").splitlines())}
        with rep_path.open("w", encoding="utf-8", newline="\n") as f:
            for c, e in flat[::step][:args.repeat]:
                for arm in arms:
                    r = record(single_turn(e, c, arm, ctx, cl, OPTIONS, keep_prompt=False))
                    r["same_as_first"] = same(r) == same(first[(e["id"], arm)])
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
        log("repeat done")
    finally:
        cl.go.close()
        cl.worker.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
