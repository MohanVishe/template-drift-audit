"""Report for arm A of the H3 mini-test (scripts/h3_mini.py --arms A). Written before any A result
was read.

Arm A sends each item through Ollama's /api/chat and reads the reply with Ollama's own parser: the
path everyday use takes. It is compared, item by item, with the published arms:
- A vs A1: same prompt (checked by prompt_sha), different reader. Measures Ollama's parser.
- A vs B: everyday Ollama against the maker's layout read by BFCL's parser. Layout and parser
  together, so it answers "what does a user get" rather than isolating either one.
Exact two-sided McNemar per comparison, Holm across the five categories within each comparison.
The overall A vs B test is the headline. Checks as for A1/B, plus A's prompt equal to A1's.

Usage: python scripts/h3_mini_report_a.py [--run runs/h3-mini/qwen2.5]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from h3_mini_report import CATS, holm, mcnemar_exact  # noqa: E402


def load(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]


def compare(by: dict, x: str, y: str) -> dict:
    """Paired x vs y per category and overall: correct counts, discordant pairs, exact and Holm p."""
    rows, ps = {}, {}
    for cat in CATS + ["overall"]:
        pairs = [v for v in by.values() if x in v and y in v and (cat == "overall" or v[x]["category"] == cat)]
        b = sum(v[x]["valid"] and not v[y]["valid"] for v in pairs)
        c = sum(v[y]["valid"] and not v[x]["valid"] for v in pairs)
        rows[cat] = {"n": len(pairs), f"{x}_correct": sum(v[x]["valid"] for v in pairs),
                     f"{y}_correct": sum(v[y]["valid"] for v in pairs), f"{x}_only": b, f"{y}_only": c,
                     "p_exact": mcnemar_exact(b, c)}
        if cat != "overall":
            ps[cat] = rows[cat]["p_exact"]
    for cat, p in holm(ps).items():
        rows[cat]["p_holm"] = p
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=str(ROOT / "runs" / "h3-mini" / "qwen2.5"))
    args = ap.parse_args()
    run = Path(args.run)
    a = load(run / "records-A.jsonl")
    by = defaultdict(dict)
    for r in load(run / "records.jsonl") + a:
        by[r["id"]][r["arm"]] = r

    checks = {
        "records": len(a),
        "items": len({r["id"] for r in a}),
        "items_missing_a_published_arm": sum(("A1" not in v or "B" not in v) for v in by.values() if "A" in v),
        "steps_with_cached_tokens": sum(r["cached_tokens"] != 0 for r in a),
        "prompt_equal_to_A1": sum(v["A"]["prompt_sha"] == v["A1"]["prompt_sha"] for v in by.values()
                                  if "A" in v and "A1" in v),
        "hit_num_predict": sum(r["done_reason"] == "length" for r in a),
        "max_prompt_tokens": max(r["prompt_tokens"] for r in a),
        "same_calls_as_A1": sum(v["A"]["calls"] == v["A1"]["calls"] for v in by.values() if "A" in v and "A1" in v),
    }
    rep = run / "repeat-A.jsonl"
    if rep.exists():
        rr = load(rep)
        checks["repeat_identical"] = f"{sum(r['same_as_first'] for r in rr)} of {len(rr)}"

    # Where Ollama's parser and BFCL's disagree on the verdict: the category and A's error type.
    flips = {"A_only": Counter(), "A1_only": Counter()}
    for v in by.values():
        if "A" in v and "A1" in v and v["A"]["valid"] != v["A1"]["valid"]:
            win, lose = ("A", "A1") if v["A"]["valid"] else ("A1", "A")
            flips[f"{win}_only"][f"{v[lose]['category']}: {v[lose]['error_type']}"] += 1

    report = {"checks": checks, "A_vs_B": compare(by, "A", "B"), "A_vs_A1": compare(by, "A", "A1"),
              "parser_flips_losing_side": {k: dict(c.most_common(12)) for k, c in flips.items()}}
    (run / "report-A.json").write_text(json.dumps(report, indent=1), encoding="utf-8", newline="\n")

    print(json.dumps(checks, indent=1))
    for name in ("A_vs_B", "A_vs_A1"):
        x, y = name.split("_vs_")
        print(f"\n{name}\n{'category':18} {'n':>4} {x:>5} {y:>5} {x + 'only':>6} {y + 'only':>6} {'p':>9} {'p_holm':>8}")
        for cat, r in report[name].items():
            print(f"{cat:18} {r['n']:>4} {r[x + '_correct']:>5} {r[y + '_correct']:>5} {r[x + '_only']:>6} "
                  f"{r[y + '_only']:>6} {r['p_exact']:>9.2e} {r.get('p_holm', float('nan')):>8.4f}")
    print(json.dumps(report["parser_flips_losing_side"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
