"""Run `tda check`'s template red-flag rules over every real template in the population.

Reads only from the cache (run the library and hf audits first). For each package it lints the
author's template (L0), the GGUF's embedded templates (L1) and Ollama's Go template, and prints
how many were flagged and why. The result is the check's alarm rate on real, published templates.

Usage: python scripts/lint_population.py [--mapping population/mapping.yaml] [--out runs/p2-lint.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tda import mapping  # noqa: E402
from tda.check import lint_template  # noqa: E402
from tda.http import Fetcher  # noqa: E402
from tda.sources import registry, upstream  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapping", default=str(ROOT / "population" / "mapping.yaml"))
    ap.add_argument("--out", default=str(ROOT / "runs" / "p2-lint.json"))
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    f = Fetcher(ROOT / ".cache", offline=True)
    regs = {"library": registry.ollama_library(f), "hf": registry.huggingface(f)}
    rows, texts_seen = [], {}
    for t in mapping.load(Path(args.mapping)):
        if t.excluded:
            continue
        repo, tag, name = registry.hf_ref(t.package) if t.kind == "hf" else registry.library_ref(t.package)
        layers = {}
        try:
            pkg = regs[t.kind].load(repo, tag, name)
            if pkg.template:
                layers["ollama_go"] = pkg.template
            if pkg.model_digest:
                hdr, _ = regs[t.kind].gguf_header(repo, pkg)
                for k, v in hdr.chat_templates().items():
                    layers[f"gguf:{k}"] = v
        except Exception as e:  # noqa: BLE001
            rows.append({"package": t.package, "error": f"{type(e).__name__}: {e}"})
            continue
        try:
            up = upstream.load(f, t.upstream_repo, t.upstream_sha)
            for k, v in up.templates.items():
                layers[f"author:{k}"] = v
        except Exception as e:  # noqa: BLE001
            layers["author_error"] = None
            rows.append({"package": t.package, "note": f"author template not cached: {type(e).__name__}"})
        flags = {k: lint_template(v) for k, v in layers.items() if v}
        for k, v in layers.items():
            if v:
                texts_seen[v] = flags[k]
        rows.append({"package": t.package, "flags": {k: v for k, v in flags.items() if v}, "layers": sorted(flags)})

    pkgs = [r for r in rows if "flags" in r]
    flagged = [r for r in pkgs if r["flags"]]
    distinct_flagged = sum(1 for v in texts_seen.values() if v)
    summary = {"packages": len(pkgs), "packages_flagged": len(flagged), "distinct_templates": len(texts_seen),
               "distinct_templates_flagged": distinct_flagged,
               "errors": [r for r in rows if "error" in r], "flagged": flagged}
    Path(args.out).write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"packages linted: {len(pkgs)}; with any flag: {len(flagged)}")
    print(f"distinct templates: {len(texts_seen)}; flagged: {distinct_flagged}")
    for r in flagged:
        for layer, fl in r["flags"].items():
            print(f"  {r['package']} [{layer}]: " + "; ".join(fl))


if __name__ == "__main__":
    main()
