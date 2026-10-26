"""Report for the H3 mini-test (scripts/h3_mini.py). Written before any B result was read.

Primary: per category and overall, paired B vs A1 on BFCL's own verdict. b = items right in A1
only, c = right in B only. Exact two-sided McNemar (binomial on b + c discordant pairs), Holm
across the five categories. Checks: every step has 0 cached tokens, every item has both arms,
A1 and B prompts differ, repeat runs give identical text.

Usage: python scripts/h3_mini_report.py [--run runs/h3-mini/qwen2.5]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATS = ["simple_python", "multiple", "parallel", "parallel_multiple", "irrelevance"]


def mcnemar_exact(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def holm(ps: dict[str, float]) -> dict[str, float]:
    order = sorted(ps, key=ps.get)
    m, adj, running = len(order), {}, 0.0
    for i, k in enumerate(order):
        running = max(running, min(1.0, (m - i) * ps[k]))
        adj[k] = running
    return adj


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=str(ROOT / "runs" / "h3-mini" / "qwen2.5"))
    args = ap.parse_args()
    run = Path(args.run)
    recs = [json.loads(l) for l in (run / "records.jsonl").read_text(encoding="utf-8").splitlines()]
    by = defaultdict(dict)
    for r in recs:
        by[r["id"]][r["arm"]] = r

    checks = {
        "records": len(recs),
        "items": len(by),
        "items_missing_an_arm": sum(len(v) != 2 for v in by.values()),
        "steps_with_cached_tokens": sum(r["cached_tokens"] != 0 for r in recs),
        "items_with_identical_prompts": sum(v["A1"]["prompt_sha"] == v["B"]["prompt_sha"] for v in by.values() if len(v) == 2),
        "hit_num_predict": dict(Counter(r["arm"] for r in recs if r["done_reason"] == "length")),
        "max_prompt_tokens": max(r["prompt_tokens"] for r in recs),
    }
    rep = run / "repeat.jsonl"
    if rep.exists():
        rr = [json.loads(l) for l in rep.read_text(encoding="utf-8").splitlines()]
        checks["repeat_identical"] = f"{sum(r['same_as_first'] for r in rr)} of {len(rr)}"

    rows, ps = {}, {}
    for cat in CATS + ["overall"]:
        pairs = [v for v in by.values() if len(v) == 2 and (cat == "overall" or v["A1"]["category"] == cat)]
        a = sum(v["A1"]["valid"] for v in pairs)
        bb = sum(v["B"]["valid"] for v in pairs)
        b = sum(v["A1"]["valid"] and not v["B"]["valid"] for v in pairs)
        c = sum(v["B"]["valid"] and not v["A1"]["valid"] for v in pairs)
        same_text = sum(v["A1"]["text"] == v["B"]["text"] for v in pairs)
        decode_fail = {arm: sum(v[arm]["calls"] is None for v in pairs) for arm in ("A1", "B")}
        p = mcnemar_exact(b, c)
        rows[cat] = {"n": len(pairs), "A1_correct": a, "B_correct": bb, "A1_only": b, "B_only": c,
                     "p_exact": p, "identical_output": same_text, "decode_failures": decode_fail}
        if cat != "overall":
            ps[cat] = p
    for cat, p in holm(ps).items():
        rows[cat]["p_holm"] = p

    # What the discordant items have in common: the error type on the losing side.
    flips = {"A1_only": Counter(), "B_only": Counter()}
    for v in by.values():
        if len(v) != 2:
            continue
        if v["A1"]["valid"] and not v["B"]["valid"]:
            flips["A1_only"][f"{v['B']['category']}: {v['B']['error_type']}"] += 1
        elif v["B"]["valid"] and not v["A1"]["valid"]:
            flips["B_only"][f"{v['A1']['category']}: {v['A1']['error_type']}"] += 1
    report = {"checks": checks, "results": rows,
              "losing_side_errors": {k: dict(c.most_common(12)) for k, c in flips.items()}}
    (run / "report.json").write_text(json.dumps(report, indent=1), encoding="utf-8", newline="\n")

    print(json.dumps(checks, indent=1))
    print(f"{'category':18} {'n':>4} {'A1':>5} {'B':>5} {'A1only':>6} {'Bonly':>5} {'p':>8} {'p_holm':>8} {'same':>5}")
    for cat, r in rows.items():
        print(f"{cat:18} {r['n']:>4} {r['A1_correct']:>5} {r['B_correct']:>5} {r['A1_only']:>6} {r['B_only']:>5} "
              f"{r['p_exact']:>8.4f} {r.get('p_holm', float('nan')):>8.4f} {r['identical_output']:>5}")
    print(json.dumps(report["losing_side_errors"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
