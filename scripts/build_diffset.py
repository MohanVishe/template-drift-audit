"""Build the diff-pair corpus for hand labelling (labels/pairs/*.txt + labels/pairs.jsonl).

Real pairs come from cached or local templates only (no network):
  q25     qwen2.5:7b-instruct      L0 vs L1, L1 vs L3, L0 vs L3-hf
  coder7  qwen2.5-coder:7b (local) L1 vs L3
Constructed pairs perturb an L0 render in one known way (ground truth by construction).
Identical pairs are counted but not written. Labels live separately in labels/labels.jsonl.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tda import fixtures  # noqa: E402
from tda.http import Fetcher  # noqa: E402
from tda.ollama_prep import chat_messages_for_request  # noqa: E402
from tda.render import go_helper  # noqa: E402
from tda.render.sandbox import JinjaSandbox  # noqa: E402
from tda.sources import registry, upstream  # noqa: E402
from tda.sources.ollama_store import LocalStore  # noqa: E402

OUT = ROOT / "labels"


def go_render(pkg, fx_list, name):
    reqs = [{"op": "render", "source": "go_template", "template": pkg.template, "tools": fx.tools,
             "messages": chat_messages_for_request(fixtures.to_ollama(fx.messages), system=pkg.system,
                                                   model_family=pkg.config.get("model_family", ""), model_name=name)}
            for fx in fx_list]
    return [r["prompt"] if r["ok"] else None for r in go_helper.call(reqs)]


def main():
    f = Fetcher(ROOT / ".cache", offline=True)
    fx_list, fx_hash = fixtures.load()
    sb = JinjaSandbox()

    def jinja(tmpl, special):
        return [sb.render(tmpl, fx.messages, fx.tools, special_tokens=special).prompt for fx in fx_list]

    lib = registry.ollama_library(f)
    repo, tag, name = registry.library_ref("qwen2.5:7b-instruct")
    pkg = lib.load(repo, tag, name)
    hdr, _ = lib.gguf_header(repo, pkg)
    hf = registry.huggingface(f)
    hrepo, quant, hname = registry.hf_ref("bartowski/Qwen2.5-7B-Instruct-GGUF:Q4_K_M")
    hpkg = hf.load(hrepo, quant, hname)
    up = upstream.load(f, "Qwen/Qwen2.5-7B-Instruct", upstream.resolve_sha(f, "Qwen/Qwen2.5-7B-Instruct"))
    special = {"bos_token": up.bos_token or "", "eos_token": up.eos_token or ""}

    q = {"L0": jinja(up.default, special), "L1": jinja(hdr.chat_template, special),
         "L3": go_render(pkg, fx_list, name), "L3-hf": go_render(hpkg, fx_list, hname)}

    store = LocalStore()
    (coder,) = [m for m in store.models() if m.short_name == "qwen2.5-coder:7b"]
    chdr = store.gguf_header(coder)
    c = {"L1": jinja(chdr.chat_template, {"bos_token": "", "eos_token": chdr.special_token("eos") or ""}),
         "L3": go_render(coder, fx_list, coder.short_name)}

    real = [("q25", q, "L0", "L1"), ("q25", q, "L1", "L3"), ("q25", q, "L0", "L3-hf"), ("coder7", c, "L1", "L3")]
    (OUT / "pairs").mkdir(parents=True, exist_ok=True)
    rows, identical = [], 0

    def emit(pid, group, source, fx, a_name, a, b_name, b, construction=None):
        (OUT / "pairs" / f"{pid}.a.txt").write_text(a, encoding="utf-8")
        (OUT / "pairs" / f"{pid}.b.txt").write_text(b if b is not None else "", encoding="utf-8")
        rows.append({"id": pid, "group": group, "source": source, "fixture": fx.id, "a": a_name, "b": b_name,
                     "b_error": b is None, "construction": construction})

    for group, layers, la, lb in real:
        for i, fx in enumerate(fx_list):
            a, b = layers[la][i], layers[lb][i]
            if a == b:
                identical += 1
                continue
            emit(f"{group}-{la}-{lb}-{fx.id}", group, "real", fx, la, a, lb, b)

    # Constructed pairs: one known perturbation of a q25 L0 render each.
    by_id = {fx.id: i for i, fx in enumerate(fx_list)}
    L0 = q["L0"]
    default_sys = "<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.<|im_end|>\n"
    no_tools = [sb.render(up.default, fx.messages, None, special_tokens=special).prompt for fx in fx_list]
    constructions = [
        ("bos", "F01", lambda s: "<|endoftext|>" + s),
        ("trailing-newline", "F02", lambda s: s + "\n"),
        ("indent", "F03", lambda s: s.replace("<|im_start|>assistant\nBlue.", "<|im_start|>assistant\n Blue.")),
        ("date", "F02", lambda s: s.replace("You answer in one sentence.", "You answer in one sentence. Today is 2026-10-22.")),
        ("default-system-dropped", "F01", lambda s: s.replace(default_sys, "")),
        ("default-system-changed", "F03", lambda s: s.replace("You are Qwen, created by Alibaba Cloud.", "You are a helpful assistant.")),
        ("tools-dropped", "F05", None),
        ("tools-dropped", "F06", None),
        ("tool-def-key-order", "F05", lambda s: s.replace('{"type": "function", "function": {"name": "add", "description": "Add two numbers"',
                                                         '{"function": {"description": "Add two numbers", "name": "add"', 1).replace(', "parameters"', ', "parameters"', 1)),
        ("tool-call-args-spacing", "F06", lambda s: s.replace('"arguments": {"city": "Oslo"}', '"arguments": {"city":"Oslo"}')),
        ("tool-call-name-lost", "F06", lambda s: s.replace('{"name": "get_weather", "arguments"', '{"arguments"')),
        ("tool-result-unwrapped", "F06", lambda s: s.replace("<tool_response>\n", "").replace("\n</tool_response>", "")),
        ("tool-result-role", "F06", lambda s: s.replace("<|im_start|>user\n<tool_response>", "<|im_start|>tool\n<tool_response>")),
        ("reasoning-kept", "F11", lambda s: s.replace("<|im_start|>assistant\nYes.", "<|im_start|>assistant\n<think>\n7 has no divisors other than 1 and 7.\n</think>\nYes.")),
        ("content-escaped", "F10", lambda s: s.replace("Zürich", "Z\\u00fcrich")),
        ("content-template-eval", "F12", lambda s: s.replace("{{ messages }}", "[]")),
        ("user-turn-merged", "F03", lambda s: s.replace("<|im_end|>\n<|im_start|>user\nWhy?", "\nWhy?")),
        ("generation-prompt-missing", "F02", lambda s: s.removesuffix("<|im_start|>assistant\n")),
        ("render-error", "F07", "error"),
        ("render-error", "F11", "error"),
    ]
    for n, (kind, fid, op) in enumerate(constructions):
        fx = fx_list[by_id[fid]]
        a = L0[by_id[fid]]
        if op is None:
            b = no_tools[by_id[fid]]
        elif op == "error":
            b = None
        else:
            b = op(a)
            assert b != a, f"construction {kind} on {fid} changed nothing"
        emit(f"con-{n:02d}-{kind}-{fid}", "constructed", "constructed", fx, "L0", a, "perturbed", b, kind)

    # Context the classifier may use: each layer's render of F01 (one user turn, nothing else),
    # from which a template's own default system prompt can be read off.
    ctx = OUT / "pairs" / "_ctx"
    ctx.mkdir(exist_ok=True)
    f01 = by_id["F01"]
    for group, layers in (("q25", q), ("coder7", c)):
        for layer, renders in layers.items():
            (ctx / f"{group}.{layer}.F01.txt").write_text(renders[f01] or "", encoding="utf-8")
    (ctx / "constructed.L0.F01.txt").write_text(L0[f01], encoding="utf-8")
    (ctx / "constructed.perturbed.F01.txt").write_text(L0[f01], encoding="utf-8")

    sb.close()
    (OUT / "pairs.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    print(f"fixtures v{fx_hash}: {len(rows)} pairs written ({sum(r['source'] == 'real' for r in rows)} real, "
          f"{sum(r['source'] == 'constructed' for r in rows)} constructed); {identical} identical real pairs skipped")


if __name__ == "__main__":
    main()
