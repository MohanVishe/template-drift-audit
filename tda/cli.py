"""tda: audit the chat prompt Ollama applies against the model author's own template.

  tda local   [--mapping M]   packages in the local Ollama store (read-only)
  tda library  --mapping M    Ollama library packages, metadata and GGUF headers only
  tda hf       --mapping M    hf.co/... packages, same
  tda report   RUN_DIR        rebuild report.md and cells.csv from a saved run
  tda check   [--folder F]    a plain-language safety check-up of this computer's local AI setup

Every network read goes through the cache; --offline fails on anything not already cached.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path

from tda import __version__, mapping, report
from tda.audit import Auditor
from tda.http import Fetcher
from tda.render import go_helper
from tda.render.sandbox import JinjaSandbox
from tda.sources.ollama_store import LocalStore

ROOT = Path(__file__).resolve().parents[1]


def _targets(args, kind: str, store: LocalStore | None) -> list[mapping.Target]:
    rows = mapping.load(Path(args.mapping)) if args.mapping else []
    if kind == "local":
        local = {m.short_name for m in store.models()}
        mapped = [t for t in rows if t.package in local]
        return mapped + [mapping.Target(n) for n in sorted(local - {t.package for t in mapped})]
    rows = [t for t in rows if t.kind == kind]
    return rows[: args.top] if args.top else rows


def _excluded(targets) -> list[dict]:
    return [{"package": t.package, "reason": t.reason} for t in targets if t.excluded]


def _audit(args, kind: str) -> int:
    f = Fetcher(Path(args.cache), offline=args.offline)
    store = LocalStore() if kind == "local" else None
    targets = _targets(args, kind, store)
    excluded = _excluded(targets)
    targets = [t for t in targets if not t.excluded]
    if not targets:
        print("no packages to audit (is --mapping set?)", file=sys.stderr)
        return 2
    run_id = args.run_id or f"{time.strftime('%Y-%m-%d')}-{kind}"
    run_dir = Path(args.runs) / run_id
    with JinjaSandbox() as sb:
        auditor = Auditor(f, store=store, sandbox=sb)
        audits = []
        for t in targets:
            a = auditor.audit(t, local=kind == "local")
            print(f"{t.package:55} {a.status:8} {a.selection.get('source', '-'):20} {a.reason}")
            audits.append(a)
        restarts = sb.restarts
    meta = {
        "run_id": run_id,
        "date": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "kind": kind,
        "tool_version": __version__,
        "ollama_version": go_helper.version(),
        "fixture_hash": auditor.fx_hash,
        "fixture_ids": [fx.id for fx in auditor.fx],
        "classifier_sha256": hashlib.sha256((ROOT / "tda" / "classify.py").read_bytes()).hexdigest(),
        "mapping": args.mapping or "",
        "mapping_sha256": hashlib.sha256(Path(args.mapping).read_bytes()).hexdigest() if args.mapping else "",
        "offline": args.offline,
        "network_requests": f.network_requests,
        "network_bytes": f.network_bytes,
        "gguf_header_bytes": auditor.header_bytes,
        "sandbox_restarts": restarts,
        "excluded": excluded,
        "sources": sorted(f.used),
    }
    report.save(run_dir, meta, audits)
    print(f"report: {report.build(run_dir)}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="tda", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("local", "library", "hf"):
        p = sub.add_parser(name)
        p.add_argument("--mapping", help="mapping.yaml or .json: package -> upstream repo@sha")
        p.add_argument("--top", type=int, default=0, help="audit only the first N mapped packages")
        p.add_argument("--offline", action="store_true", help="read only from the cache")
        p.add_argument("--cache", default=str(ROOT / ".cache"))
        p.add_argument("--runs", default=str(ROOT / "runs"))
        p.add_argument("--run-id")
    p = sub.add_parser("report")
    p.add_argument("run_dir")
    p = sub.add_parser("check", help="a read-only safety check-up of this computer's local AI setup")
    p.add_argument("--folder", default=".", help="the folder an AI helper works in (default: this folder)")
    p.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    if args.cmd == "check":
        from tda import check
        findings = check.run(Path(args.folder).resolve())
        print(check.to_json(findings) if args.json else check.render(findings))
        return 0
    if args.cmd == "report":
        print(report.build(Path(args.run_dir)))
        return 0
    return _audit(args, args.cmd)


if __name__ == "__main__":
    sys.exit(main())
