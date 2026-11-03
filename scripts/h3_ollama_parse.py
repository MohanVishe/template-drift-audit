"""H3 mini-test, step 1 of the follow-ups: the maker's layout read by Ollama's own parser.

No model run. The saved raw replies of arms A1 (Ollama's layout) and B (the maker's layout) go
through Ollama's tool-call parser offline (go-helper op "parse", the /api/chat path for a model
with a Go template), then BFCL's checker, unchanged. Arms written:
- A1o: A1's replies, read by Ollama's parser. A check: it must match the live arm A, which sent the
  same prompt through /api/chat.
- Bo: B's replies, read by Ollama's parser. The maker's layout as an Ollama user would get it if
  Ollama used that layout and kept its parser.

Written before any result was read. Headline: overall Bo vs A1o, exact two-sided McNemar (the
layout effect with Ollama's parser on both sides). Also Bo vs B (Ollama's parser on the maker's
layout), Holm across the five categories within each comparison.

Usage: python scripts/h3_ollama_parse.py [--run runs/h3-mini/qwen2.5]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from h3_mini_report import CATS  # noqa: E402
from h3_mini_report_a import compare, load  # noqa: E402
from tda.h3 import bfcl  # noqa: E402
from tda.h3.models import MODELS  # noqa: E402
from tda.h3.runtime import GoSession, ModelCtx, Worker  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=str(ROOT / "runs" / "h3-mini" / "qwen2.5"))
    ap.add_argument("--model", default="qwen2.5:7b-instruct")
    args = ap.parse_args()
    run = Path(args.run)
    ctx = ModelCtx.from_spec(MODELS[args.model])
    go, worker = GoSession(), Worker()
    by = defaultdict(dict)
    for r in load(run / "records.jsonl") + load(run / "records-A.jsonl"):
        by[r["id"]][r["arm"]] = r
    out = []
    try:
        for cat in CATS:
            for e in worker.ok({"op": "load", "category": cat})["entries"]:
                tools, names = bfcl.to_tools(e["function"])
                for src, arm in (("A1", "A1o"), ("B", "Bo")):
                    r = go.ask({"op": "parse", "template": ctx.pkg.template, "tools": tools,
                                "text": by[e["id"]][src]["text"]})
                    if not r["ok"]:
                        raise RuntimeError(f"{e['id']}: {r['error']}")
                    parsed = bfcl.from_ollama({"content": r.get("content", ""), "tool_calls": r.get("tool_calls")})
                    output = bfcl.bfcl_output(parsed.calls, names)
                    if cat == "irrelevance":
                        score = worker.ok({"op": "score_irrelevance", "output": output})
                    else:
                        score = worker.ok({"op": "score_ast", "category": cat, "functions": e["function"],
                                           "output": output, "answer": e["answer"]})
                    out.append({"id": e["id"], "category": cat, "arm": arm, "valid": score["valid"],
                                "error_type": score.get("error_type"), "calls": parsed.calls,
                                "content": parsed.content, "tag": r.get("tag")})
    finally:
        go.close()
        worker.close()

    path = run / "records-ollama-parser.jsonl"
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out), encoding="utf-8", newline="\n")
    for r in out:
        by[r["id"]][r["arm"]] = r

    a = [v for v in by.values() if "A" in v and "A1o" in v]
    checks = {
        "items": len({r["id"] for r in out}),
        "tags": sorted({r["tag"] for r in out}),
        "A1o_matches_live_A_verdict": sum(v["A"]["valid"] == v["A1o"]["valid"] for v in a),
        "A1o_matches_live_A_calls": sum(v["A"]["calls"] == v["A1o"]["calls"] for v in a),
        "A1o_matches_live_A_content": sum(v["A"]["text"] == v["A1o"]["content"] for v in a),
    }
    report = {"checks": checks, "Bo_vs_A1o": compare(by, "Bo", "A1o"), "Bo_vs_B": compare(by, "Bo", "B")}
    (run / "report-ollama-parser.json").write_text(json.dumps(report, indent=1), encoding="utf-8", newline="\n")

    print(json.dumps(checks, indent=1))
    for name in ("Bo_vs_A1o", "Bo_vs_B"):
        x, y = name.split("_vs_")
        print(f"\n{name}\n{'category':18} {'n':>4} {x:>5} {y:>5} {x + 'only':>6} {y + 'only':>6} {'p':>9} {'p_holm':>8}")
        for cat, r in report[name].items():
            print(f"{cat:18} {r['n']:>4} {r[x + '_correct']:>5} {r[y + '_correct']:>5} {r[x + '_only']:>6} "
                  f"{r[y + '_only']:>6} {r['p_exact']:>9.2e} {r.get('p_holm', float('nan')):>8.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
