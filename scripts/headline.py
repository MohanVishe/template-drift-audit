"""The article's headline numbers, computed from saved runs (no network, no re-rendering).

For every package with both L0 and L3 renders:
  material      at least one tool fixture (F04-F09) differs materially, L0 -> L3, by the frozen classifier
  tool_capable  the author's own template shows the tool definitions to the model (the tool name
                appears in its F04 render); only these models were built to use tools this way
  strict        material even after setting aside tool-schema differences that are only a change of
                key order (same keys and values, different order)

Usage: python scripts/headline.py runs/p2-library [runs/p2-hf ...] [--out runs/p2-headline.json]
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
from tda.classify import SEVERITY, classify, default_system_texts, recover  # noqa: E402

TOOL = sorted(fixtures.TOOL_SET)


def _sorted_json(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _strict_classes(a: str, b: str, fx, ds, r) -> list[str]:
    """Material classes after dropping TOOL_SCHEMA hunks that sit inside tool definitions which are
    equal once key order is ignored. TOOL_SCHEMA hunks outside the definitions (instruction wording,
    layout) are kept."""
    A, B = recover(a, fx.messages, fx.tools, ds), recover(b, fx.messages, fx.tools, ds)
    da, db = A.of("tool_def"), B.of("tool_def")
    reordered = (bool(da) and len(da) == len(db) and all(s.is_json for s in da + db)
                 and all(_sorted_json(x.parsed) == _sorted_json(y.parsed) for x, y in zip(da, db)))

    def inside(rng, spans):
        return any(rng[0] < s.end and s.start < rng[1] or s.start <= rng[0] <= s.end for s in spans)

    keep = set()
    for h in r.hunks:
        if SEVERITY.get(h.cls, "material") != "material":
            continue
        if h.cls == "TOOL_SCHEMA" and reordered and (inside(h.a, da) or inside(h.b, db)):
            continue
        keep.add(h.cls)
    keep.update(c for c in r.classes if c in ("TOOLS_DROPPED", "RENDER_ERROR"))
    return sorted(keep)


def package(run: Path, mp: Path, fx: dict) -> dict | None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    rd = run / "renders" / mp.stem

    def read(layer, fid):
        p = rd / f"{layer}.{fid}.txt"
        return p.read_text(encoding="utf-8") if p.exists() else None

    if not any(c["pair"] == "end_to_end" for c in m["cells"]):
        return None
    ds = set()
    for layer in ("L0", "L3"):
        t = read(layer, "F01")
        if t:
            ds.update(default_system_texts(t, fx["F01"].messages))
    ds = sorted(ds)
    l0_f04 = read("L0", "F04") or ""
    out = {"package": m["target"]["package"], "source": m["selection"].get("source"),
           "tool_capable": "get_weather" in l0_f04, "material": False, "strict": False,
           "classes": Counter(), "strict_classes": Counter(), "fixtures_compared": 0,
           "approximate": not all(L["exact"] for L in m["layers"].values()),
           "origin": None, "conversion_match": (m.get("conversion") or {}).get("match")}
    conv_material = any(c["pair"] == "conversion" and c["fixture"] in TOOL and c["severity"] == "material"
                        for c in m["cells"])
    pack_material = any(c["pair"] == "packaging" and c["fixture"] in TOOL and c["severity"] == "material"
                        for c in m["cells"])
    has_l1 = "L1" in m["layers"]
    for fid in TOOL:
        a, b = read("L0", fid), read("L3", fid)
        if a is None:
            continue  # the author's template cannot render this fixture: not counted
        out["fixtures_compared"] += 1
        r = classify(a, b, fx[fid].messages, fx[fid].tools, default_system=ds)
        mat = [c for c in r.classes if SEVERITY.get(c, "material") == "material"]
        if not mat:
            continue
        out["material"] = True
        out["classes"].update(mat)
        strict = mat if b is None else _strict_classes(a, b, fx[fid], ds, r)
        if strict:
            out["strict"] = True
            out["strict_classes"].update(strict)
    if out["material"]:
        out["origin"] = ("no GGUF template" if not has_l1 else
                         "conversion and Ollama" if conv_material and pack_material else
                         "conversion" if conv_material else "Ollama" if pack_material else "combined")
    out["classes"], out["strict_classes"] = sorted(out["classes"]), sorted(out["strict_classes"])
    return out


def summarise(rows: list[dict]) -> dict:
    def count(rs):
        return {"packages": len(rs), "material": sum(r["material"] for r in rs),
                "strict": sum(r["strict"] for r in rs),
                "origin": dict(Counter(r["origin"] for r in rs if r["material"])),
                "classes": dict(Counter(c for r in rs if r["strict"] for c in r["strict_classes"]).most_common())}
    scored = [r for r in rows if r["fixtures_compared"]]
    return {"all": count(scored), "tool_capable": count([r for r in scored if r["tool_capable"]]),
            "no_tool_fixture_renderable": [r["package"] for r in rows if not r["fixtures_compared"]],
            "approximate": [r["package"] for r in rows if r["approximate"]],
            "reorder_only": [r["package"] for r in scored if r["material"] and not r["strict"]]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--out")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    fx = {f.id: f for f in fixtures.load()[0]}
    result = {}
    for run in map(Path, args.runs):
        rows = [r for mp in sorted((run / "models").glob("*.json")) if (r := package(run, mp, fx))]
        result[run.name] = {"summary": summarise(rows), "packages": rows}
        s = result[run.name]["summary"]
        print(f"== {run.name}")
        for k in ("all", "tool_capable"):
            c = s[k]
            print(f"  {k:13} material {c['material']}/{c['packages']}   strict {c['strict']}/{c['packages']}   "
                  f"origin {c['origin']}")
            print(f"  {'':13} classes {c['classes']}")
        print(f"  reorder-only: {s['reorder_only']}")
        print(f"  no tool fixture renderable by L0: {s['no_tool_fixture_renderable']}")
        print(f"  approximate L3: {s['approximate']}")
    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
