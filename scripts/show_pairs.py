"""Print every difference in labelled-set pairs, with context. Neutral: no classification.

Usage: python scripts/show_pairs.py [id-substring ...]
"""

import difflib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAIRS = ROOT / "labels" / "pairs"


def show(pid: str, width: int = 170) -> None:
    a = (PAIRS / f"{pid}.a.txt").read_text(encoding="utf-8")
    b = (PAIRS / f"{pid}.b.txt").read_text(encoding="utf-8")
    print(f"=== {pid}  (a {len(a)} chars, b {len(b)} chars)")
    lines = difflib.unified_diff(a.splitlines(keepends=True), b.splitlines(keepends=True), "a", "b", n=1)
    for line in list(lines)[2:]:
        print("   " + repr(line)[1:-1][:width])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    rows = [json.loads(line) for line in (ROOT / "labels" / "pairs.jsonl").read_text(encoding="utf-8").splitlines()]
    for r in rows:
        if len(sys.argv) == 1 or any(s in r["id"] for s in sys.argv[1:]):
            if r["b_error"]:
                print(f"=== {r['id']}  (b failed to render)")
            else:
                show(r["id"])
