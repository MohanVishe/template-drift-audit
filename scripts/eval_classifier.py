"""Score tda.classify against the hand labels (labels/labels.jsonl).

Usage: python scripts/eval_classifier.py --split dev|test|all [--show-errors]
Reports pair-level exact match of the class set, severity agreement, and per-class
precision/recall. The test split is meant to be scored once, after rules are frozen.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tda import fixtures  # noqa: E402
from tda.classify import classify, default_system_texts  # noqa: E402

PAIRS = ROOT / "labels" / "pairs"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev", choices=["dev", "test", "all"])
    ap.add_argument("--show-errors", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    fx = {f.id: f for f in fixtures.load()[0]}
    meta = {r["id"]: r for r in map(json.loads, (ROOT / "labels" / "pairs.jsonl").open(encoding="utf-8"))}
    labels = [r for r in map(json.loads, (ROOT / "labels" / "labels.jsonl").open(encoding="utf-8"))
              if args.split == "all" or r["split"] == args.split]

    tp, fp, fn = Counter(), Counter(), Counter()
    exact = sev_ok = 0
    confusion = Counter()
    for lab in labels:
        m = meta[lab["id"]]
        f = fx[m["fixture"]]
        ctx = PAIRS / "_ctx"
        ds = []
        for layer in (m["a"], m["b"]):
            p = ctx / f"{m['group']}.{layer}.F01.txt"
            if p.exists():
                ds += default_system_texts(p.read_text(encoding="utf-8"), fx["F01"].messages)
        a = (PAIRS / f"{lab['id']}.a.txt").read_text(encoding="utf-8")
        b = None if m["b_error"] else (PAIRS / f"{lab['id']}.b.txt").read_text(encoding="utf-8")
        res = classify(a, b, f.messages, f.tools, default_system=sorted(set(ds)))
        got, want = set(res.classes), set(lab["classes"])
        exact += got == want
        sev_ok += res.severity == lab["severity"]
        confusion[(lab["severity"], res.severity)] += 1
        for c in got | want:
            if c in got and c in want:
                tp[c] += 1
            elif c in got:
                fp[c] += 1
            else:
                fn[c] += 1
        if args.show_errors and got != want:
            print(f"{lab['id']}: want {sorted(want)} got {sorted(got)}")
            for h in res.hunks:
                print(f"    {h.cls:20} A:{h.a_text[:70]!r} B:{h.b_text[:70]!r}")

    n = len(labels)
    print(f"split={args.split}  pairs={n}")
    print(f"class set exact match: {exact}/{n}   severity agreement: {sev_ok}/{n}")
    print("severity confusion (label -> classifier):", dict(sorted(confusion.items())))
    print(f"{'class':22}{'tp':>4}{'fp':>4}{'fn':>4}  precision  recall")
    for c in sorted(set(tp) | set(fp) | set(fn)):
        p = tp[c] / (tp[c] + fp[c]) if tp[c] + fp[c] else float("nan")
        r = tp[c] / (tp[c] + fn[c]) if tp[c] + fn[c] else float("nan")
        print(f"{c:22}{tp[c]:4}{fp[c]:4}{fn[c]:4}  {p:9.2f}  {r:6.2f}")


if __name__ == "__main__":
    main()
