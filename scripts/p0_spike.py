"""P0 spike: render the fixtures through every layer for one model and show where they differ.

Layers rendered:
  L0      model author's template (current upstream commit), Python jinja2 like transformers
  L1      template embedded in the Ollama library GGUF, same renderer
  L3      what Ollama v0.40.7 applies to the library package (selection rule + Go helper)
  L3-hf   what Ollama applies to the hf.co package (HF-generated Go template, no SYSTEM layer)
  live    (optional, --live) Ollama v0.40.7 _debug_render_only on the isolated instance

Usage: python scripts/p0_spike.py [--live http://127.0.0.1:11500] [--offline]
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tda import fixtures  # noqa: E402
from tda.http import Fetcher  # noqa: E402
from tda.ollama_prep import chat_messages_for_request  # noqa: E402
from tda.render import go_helper, jinja_ref  # noqa: E402
from tda.select import GoTemplateInfo, select_source  # noqa: E402
from tda.sources import registry, upstream  # noqa: E402

LIBRARY_MODEL = "qwen2.5:7b-instruct"
HF_MODEL = "bartowski/Qwen2.5-7B-Instruct-GGUF:Q4_K_M"
UPSTREAM_REPO = "Qwen/Qwen2.5-7B-Instruct"


def exact_go_info(raw: str) -> GoTemplateInfo:
    r = go_helper.call([{"op": "inspect", "template": raw}])[0]
    if not r["ok"]:
        raise RuntimeError(r["error"])
    return GoTemplateInfo(raw, frozenset(r["vars"]), tuple(r["think_tags"]), exact=True)


def ollama_requests(pkg, fx_list, model_name):
    reqs = []
    for fx in fx_list:
        msgs = chat_messages_for_request(fixtures.to_ollama(fx.messages), system=pkg.system,
                                         model_family=pkg.config.get("model_family", ""), model_name=model_name)
        reqs.append({"op": "render", "source": "go_template", "template": pkg.template,
                     "messages": msgs, "tools": fx.tools})
    return reqs


def live_render(base: str, model: str, fx) -> str:
    body = json.dumps({"model": model, "messages": fixtures.to_ollama(fx.messages), "tools": fx.tools,
                       "stream": False, "_debug_render_only": True}).encode()
    req = urllib.request.Request(f"{base}/api/chat", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)["_debug_info"]["rendered_template"]


def first_diff(a: str, b: str, ctx: int = 60) -> str:
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op != "equal":
            return f"{op}: {a[max(0, a1 - ctx):a2 + 10]!r}\n           -> {b[max(0, b1 - ctx):b2 + 10]!r}"
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", help="base URL of the isolated Ollama instance")
    ap.add_argument("--live-model", default=LIBRARY_MODEL, help="model name inside the isolated instance")
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()

    f = Fetcher(ROOT / ".cache", offline=args.offline)
    fx_list, fx_hash = fixtures.load()
    out = ROOT / "runs" / "p0" / LIBRARY_MODEL.replace(":", "_")
    out.mkdir(parents=True, exist_ok=True)

    lib = registry.ollama_library(f)
    repo, tag, name = registry.library_ref(LIBRARY_MODEL)
    pkg = lib.load(repo, tag, name)
    hdr, _ = lib.gguf_header(repo, pkg)

    hf = registry.huggingface(f)
    hrepo, quant, hname = registry.hf_ref(HF_MODEL)
    hpkg = hf.load(hrepo, quant, hname)
    hhdr, _ = hf.gguf_header(hrepo, hpkg)

    up = upstream.load(f, UPSTREAM_REPO, upstream.resolve_sha(f, UPSTREAM_REPO))

    sel = select_source(renderer=pkg.renderer, parser=pkg.parser, model_family=pkg.config.get("model_family", ""),
                        go=exact_go_info(pkg.template), gguf_chat_template=hdr.chat_template or "")
    hsel = select_source(renderer=hpkg.renderer, parser=hpkg.parser, model_family=hpkg.config.get("model_family", ""),
                         go=exact_go_info(hpkg.template), gguf_chat_template=hhdr.chat_template or "")
    print(f"go-helper: Ollama {go_helper.version()}   fixtures v{fx_hash}")
    print(f"L0 {up.repo}@{up.sha[:12]} ({up.file})")
    print(f"selection  library: {sel.source} (go_caps={sel.go_caps}, chat_caps={sel.chat_caps}, prefer_chat={sel.prefer_chat_template})")
    print(f"selection  hf.co  : {hsel.source} (go_caps={hsel.go_caps}, chat_caps={hsel.chat_caps}, prefer_chat={hsel.prefer_chat_template})")
    for s in (sel, hsel):
        if s.source != "go_template":
            print("NOTE: a non-go_template source was selected; this spike only renders go_template for L3")

    special = {"bos_token": up.bos_token or "", "eos_token": up.eos_token or ""}
    gguf_special = {"bos_token": hdr.special_token("bos") or "", "eos_token": hdr.special_token("eos") or ""}
    l3 = go_helper.call(ollama_requests(pkg, fx_list, LIBRARY_MODEL))
    l3hf = go_helper.call(ollama_requests(hpkg, fx_list, hname))

    rows = []
    for fx, r3, r3h in zip(fx_list, l3, l3hf):
        renders = {
            "L0": jinja_ref.render(up.default, fx.messages, fx.tools, special_tokens=special),
            "L1": jinja_ref.render(hdr.chat_template, fx.messages, fx.tools, special_tokens=gguf_special),
            "L3": r3["prompt"] if r3["ok"] else f"<ERROR {r3['error']}>",
            "L3-hf": r3h["prompt"] if r3h["ok"] else f"<ERROR {r3h['error']}>",
        }
        if args.live:
            renders["live"] = live_render(args.live, args.live_model, fx)
        for layer, text in renders.items():
            (out / f"{fx.id}.{layer}.txt").write_text(text, encoding="utf-8")
        pairs = [("L0", "L1"), ("L1", "L3"), ("L0", "L3"), ("L0", "L3-hf")] + ([("L3", "live")] if args.live else [])
        rows.append((fx, {p: renders[p[0]] == renders[p[1]] for p in pairs}, renders))

    pairs = list(rows[0][1])
    print("\n" + "fixture".ljust(9) + "".join(f"{a}={b}".ljust(13) for a, b in pairs))
    for fx, eq, _ in rows:
        print(fx.id.ljust(9) + "".join(("same" if eq[p] else "DIFF").ljust(13) for p in pairs) + fx.about)

    print("\nFirst difference per fixture, L0 -> L3:")
    for fx, eq, r in rows:
        if not eq[("L0", "L3")]:
            print(f"  {fx.id}  {first_diff(r['L0'], r['L3'])}")
    if args.live:
        mismatches = [fx.id for fx, eq, _ in rows if not eq[("L3", "live")]]
        print(f"\nfidelity: offline L3 == live on {len(rows) - len(mismatches)}/{len(rows)} fixtures {mismatches or ''}")
    print(f"\nrenders written to {out.relative_to(ROOT)}; network this run: {f.network_requests} requests")


if __name__ == "__main__":
    main()
