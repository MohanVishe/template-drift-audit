"""Offline render check for the frozen H3 models (no generation, no weights needed).

  1. Every BFCL item's first turn, both layouts (L0 maker, L3 Ollama).
  2. Every multi-turn entry played through with a synthetic history: at each step the assistant
     makes two calls (parallel), both get tool results, then it answers in text and the next turn's
     user message follows. Rendered before every assistant step, both layouts, under the model's
     history rule. This exercises Mistral's id length and alternation checks and Llama's
     single-call rule before any real run.

Usage: python scripts/h3_render_check.py [--models llama3.1:8b mistral:7b] [--out runs/h3-render-check.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tda.h3 import bfcl  # noqa: E402
from tda.h3.models import MODELS  # noqa: E402
from tda.h3.runtime import GoSession, ModelCtx, Worker  # noqa: E402
from tda.render.sandbox import JinjaSandbox  # noqa: E402

SINGLE = ["simple_python", "multiple", "parallel", "parallel_multiple", "irrelevance"]


def render_both(ctx, go, sb, msgs, tools, where, out):
    for layout, fn in (("L0", lambda: ctx.render_l0(sb, msgs, tools)), ("L3", lambda: ctx.render_l3(go, msgs, tools))):
        out["renders"] += 1
        try:
            fn()
        except Exception as ex:  # noqa: BLE001
            msg = str(ex)[:200]
            out["fail"][layout] += 1
            out["errors"][f"{layout}: {msg}"] += 1
            if len(out["examples"]) < 10:
                out["examples"].append([where, layout, msg])


def check(ctx, go, sb, entries) -> dict:
    out = {"renders": 0, "fail": Counter(), "errors": Counter(), "examples": [], "first_turn_items": 0,
           "synthetic_steps": 0}
    for es in entries.values():
        for e in es:
            tools, _ = bfcl.to_tools(e["function"])
            out["first_turn_items"] += 1
            render_both(ctx, go, sb, list(e["question"][0]), tools, e["id"], out)
    for e in entries["multi_turn_base"]:
        tools, _ = bfcl.to_tools(e["function"])
        names = [t["function"]["name"] for t in tools]
        msgs: list[dict] = []
        for t, turn in enumerate(e["question"]):
            msgs += turn
            out["synthetic_steps"] += 1
            render_both(ctx, go, sb, msgs, tools, f"{e['id']} turn {t} step 0", out)
            calls = [{"name": names[0], "arguments": {}}, {"name": names[-1], "arguments": {"x": 1}}]
            parsed = bfcl.Parsed("", calls=calls)
            ids = [bfcl.call_id(e["id"], t, 0, k) for k in range(2)]
            msgs += bfcl.history_messages(parsed, ['{"ok": true}', "plain text result"], ids, ctx.one_call_per_message)
            out["synthetic_steps"] += 1
            render_both(ctx, go, sb, msgs, tools, f"{e['id']} turn {t} step 1", out)
            msgs += bfcl.history_messages(bfcl.Parsed("Done.", calls=[], content="Done."), [], [],
                                          ctx.one_call_per_message)
    out["fail"] = dict(out["fail"])
    out["errors"] = dict(out["errors"].most_common(10))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=["llama3.1:8b", "mistral:7b"])
    ap.add_argument("--out", default=str(ROOT / "runs" / "h3-render-check.json"))
    args = ap.parse_args()
    worker, go, sb = Worker(), GoSession(), JinjaSandbox(timeout=30)
    try:
        entries = {c: worker.ok({"op": "load", "category": c})["entries"] for c in SINGLE + ["multi_turn_base"]}
        report = {}
        for name in args.models:
            spec = MODELS[name]
            ctx = ModelCtx.from_spec(spec)
            r = check(ctx, go, sb, entries)
            r["gguf_add_bos"] = ctx.add_bos
            report[name] = r
            print(name, json.dumps({k: r[k] for k in ("renders", "fail", "first_turn_items", "synthetic_steps")}),
                  flush=True)
            for k, v in r["errors"].items():
                print("  ", v, k, flush=True)
    finally:
        go.close()
        worker.close()
    Path(args.out).write_text(json.dumps(report, indent=1), encoding="utf-8")
    return 0 if all(not r["fail"] for r in report.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
