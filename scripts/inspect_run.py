"""Show the hunks behind a run's classifications, for hand review.

Usage: python scripts/inspect_run.py RUN_DIR [--pair end_to_end] [--cls OTHER] [--pkg substring] [--fixture F05]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tda import fixtures  # noqa: E402
from tda.audit import PAIRS  # noqa: E402
from tda.classify import classify, default_system_texts  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--pair", default="end_to_end")
    ap.add_argument("--cls")
    ap.add_argument("--pkg")
    ap.add_argument("--fixture")
    ap.add_argument("--width", type=int, default=110)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    fx = {f.id: f for f in fixtures.load()[0]}
    a_name, b_name = next((a, b) for a, b, p in PAIRS if p == args.pair)
    run = Path(args.run_dir)
    for mp in sorted((run / "models").glob("*.json")):
        m = json.loads(mp.read_text(encoding="utf-8"))
        pkg = m["target"]["package"]
        if args.pkg and args.pkg not in pkg:
            continue
        rdir = run / "renders" / mp.stem

        def read(layer, fid):
            p = rdir / f"{layer}.{fid}.txt"
            return p.read_text(encoding="utf-8") if p.exists() else None

        ds = set()
        for layer in (a_name, b_name):
            t = read(layer, "F01")
            if t:
                ds.update(default_system_texts(t, fx["F01"].messages))
        for c in m["cells"]:
            if c["pair"] != args.pair or (args.fixture and c["fixture"] != args.fixture):
                continue
            if args.cls and args.cls not in c["classes"]:
                continue
            a, b = read(a_name, c["fixture"]), read(b_name, c["fixture"])
            if a is None or b is None:
                continue
            f = fx[c["fixture"]]
            r = classify(a, b, f.messages, f.tools, default_system=sorted(ds))
            print(f"== {pkg} {c['fixture']} {args.pair}: {', '.join(r.classes)}")
            for h in r.hunks:
                if args.cls and h.cls != args.cls:
                    continue
                print(f"   {h.cls:20} A:{h.a_text[:args.width]!r}\n   {'':20} B:{h.b_text[:args.width]!r}")


if __name__ == "__main__":
    main()
