"""Build the website's figures from saved runs (no network). Writes HTML snippets to
docs/_includes/fig/, which the pages include. Every number in them comes from:
  runs/p2-headline.json  (scripts/headline.py)
  runs/p2-lint.json      (scripts/lint_population.py)
  runs/p2-library/renders/qwen2.5_latest/{L0,L3}.F04.txt  (the before/after example)

Charts are plain HTML and SVG styled by docs/_layouts/default.html; each mark carries a
`data-tip` the page's small tooltip script shows on hover and keyboard focus. The results page
has every value as a table.

Usage: python scripts/site_figures.py [--runs runs] [--out docs/_includes/fig]
"""

from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SHORT = {
    "TOOL_RESULT": "Tool answers laid out differently or left out",
    "DEFAULT_SYSTEM": "A standing instruction added or dropped",
    "TOOL_CALL": "Earlier tool requests written differently",
    "OTHER": "Other wording differs",
    "TOOLS_DROPPED": "The list of tools not shown",
    "TOOL_SCHEMA": "Tool instructions worded differently",
    "CONTENT": "Your message text changed",
    "TOOL_SCHEMA_NOT_JSON": "Tools described in Go format, not JSON",
    "STRUCTURE": "Turn layout changed",
    "THINKING": "Thinking-block handling differs",
}
WHERE = {
    "Ollama": "Ollama's own version of the template",
    "conversion and Ollama": "An old copy in the model file, then Ollama's version",
    "no GGUF template": "Ollama's version (the model file has no template)",
    "conversion": "The template inside the uploaded file",
}
STATE_LABEL = {"differs": "Reads differently", "order": "Only the field order differs", "same": "Reads the same"}


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def name(pkg: str) -> str:
    if pkg.startswith("hf.co/"):
        repo = pkg[len("hf.co/"):].split(":")[0]
        return repo if len(repo) <= 44 else repo[:42] + "…"
    return pkg.removesuffix(":latest")


def state(r: dict) -> str:
    return "differs" if r["strict"] else "order" if r["material"] else "same"


def tip(r: dict) -> str:
    s = state(r)
    parts = [name(r["package"]), STATE_LABEL[s]]
    if s == "differs":
        parts.append(WHERE.get(r["origin"], ""))
        parts.append("; ".join(SHORT.get(c, c) for c in r["strict_classes"][:3]).lower())
    return " · ".join(p for p in parts if p)


def scored(h: dict) -> list[dict]:
    return [r for r in h["packages"] if r["fixtures_compared"]]


def stats(lib: dict, hf: dict, stale: int, files: int) -> str:
    a, ha = lib["summary"]["all"], hf["summary"]["all"]
    tiles = [
        (f"{a['material']}<span> of {a['packages']}</span>", "Ollama library models that read their tool conversations differently"),
        (f"{a['strict']}<span> of {a['packages']}</span>", "…counting only changes bigger than the order of fields"),
        (f"{ha['material']}<span> of {ha['packages']}</span>", "Hugging Face models that differ, all already in the uploaded file"),
        (f"{stale}<span> of {files}</span>", "Library model files that carry an outdated copy of the maker's template"),
    ]
    out = ['<div class="stats">']
    for v, label in tiles:
        out.append(f'  <div class="stat"><div class="stat-v">{v}</div><div class="stat-l">{esc(label)}</div></div>')
    out.append("</div>")
    return "\n".join(out)


def grid(lib: dict, hf: dict) -> str:
    order = {"differs": 0, "order": 1, "same": 2}
    out = ['<figure class="viz" aria-labelledby="fig-grid-title">',
           '  <figcaption><strong id="fig-grid-title">Every model measured: does it read what its maker designed?</strong>',
           '  <span>Each square is one model, on six practice conversations that use tools. Hover or tab to a square for its name.</span></figcaption>']
    counts = Counter()
    for title, h in (("Ollama library", lib), ("Hugging Face", hf)):
        rows = sorted(scored(h), key=lambda r: (order[state(r)], name(r["package"]).lower()))
        c = Counter(state(r) for r in rows)
        counts.update(c)
        cols, cell, gap = 15, 22, 4
        n_rows = -(-len(rows) // cols)
        w, ht = cols * (cell + gap) - gap, n_rows * (cell + gap) - gap
        summary = ", ".join(f"{c[k]} {STATE_LABEL[k].lower()}" for k in ("differs", "order", "same") if c[k])
        out.append(f'  <div class="grid-group"><div class="grid-label">{title} <span>{len(rows)} models: {summary}</span></div>')
        out.append(f'  <svg class="unit" viewBox="0 0 {w} {ht}" width="{w}" height="{ht}" role="img" '
                   f'aria-label="{esc(title)}: {esc(summary)}">')
        for i, r in enumerate(rows):
            x, y = (i % cols) * (cell + gap), (i // cols) * (cell + gap)
            out.append(f'    <rect class="m-{state(r)}" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="4" '
                       f'tabindex="0" data-tip="{esc(tip(r))}"><title>{esc(tip(r))}</title></rect>')
        out.append("  </svg></div>")
    out.append('  <div class="legend">')
    for k in ("differs", "order", "same"):
        out.append(f'    <span><i class="key m-{k}"></i>{STATE_LABEL[k]} ({counts[k]})</span>')
    out.append("  </div>")
    out.append('  <p class="viz-note">The full list, with what changes for each model, is on the '
               '<a href="results.html">results page</a>.</p>')
    out.append("</figure>")
    return "\n".join(out)


def bars(fig_id: str, title: str, sub: str, items: list[tuple[str, int, str]], total: int, unit: str) -> str:
    peak = max(v for _, v, _ in items)
    out = [f'<figure class="viz" aria-labelledby="{fig_id}">',
           f'  <figcaption><strong id="{fig_id}">{esc(title)}</strong><span>{esc(sub)}</span></figcaption>',
           '  <div class="bars">']
    for label, v, t in items:
        pct = 100 * v / peak
        out.append(f'    <div class="bar-row" tabindex="0" data-tip="{esc(t)}"><span class="bar-label">{esc(label)}</span>'
                   f'<span class="bar-track"><span class="bar" style="width:{pct:.1f}%"></span></span>'
                   f'<span class="bar-v">{v}<small> of {total}</small></span></div>')
    out.append("  </div>")
    out.append(f'  <p class="viz-note">{esc(unit)}</p>')
    out.append("</figure>")
    return "\n".join(out)


def specimen(runs: Path) -> str:
    d = runs / "p2-library" / "renders" / "qwen2.5_latest"

    def line(layer):
        text = (d / f"{layer}.F04.txt").read_text(encoding="utf-8")
        return next(l for l in text.splitlines() if "get_weather" in l)

    a, b = esc(line("L0")), esc(line("L3"))
    b = b.replace("&lt;nil&gt;", "<mark>&lt;nil&gt;</mark>")
    b = re.sub(r"\{get_weather", "{<mark>get_weather</mark>", b, count=1)
    return "\n".join([
        '<figure class="viz specimen" aria-labelledby="fig-spec-title">',
        '  <figcaption><strong id="fig-spec-title">The same tool, as the model reads it</strong>',
        '  <span>One line from a practice conversation for <code>qwen2.5</code>, describing a weather tool. '
        'Copied exactly from the measurement.</span></figcaption>',
        '  <div class="spec-pair">',
        f'    <div class="spec"><div class="spec-h">What the maker\'s template gives the model</div><pre>{a}</pre>'
        '<p>Neat JSON: every part is named (<code>"name"</code>, <code>"description"</code>, <code>"parameters"</code>).</p></div>',
        f'    <div class="spec spec-b"><div class="spec-h">What Ollama gives the model</div><pre>{b}</pre>'
        '<p>The names are gone, and placeholders like <code>&lt;nil&gt;</code> (Go for "empty") appear in their place.</p></div>',
        "  </div>",
        "</figure>",
    ])


def checkup_example() -> str:
    """The check-up's real output for a made-up computer: every line is produced by tda.check from
    the example inputs below (none of them read from this machine)."""
    import sys
    import tempfile
    sys.path.insert(0, str(ROOT))
    from tda import check
    from tda.sources.ollama_store import OllamaModel

    class ExampleStore:
        def models(self):
            return [OllamaModel("registry.ollama.ai/library/qwen2.5:7b", {}, {}, template="{{ .Prompt }}"),
                    OllamaModel("hf.co/someone/Some-Model-GGUF:Q4_K_M", {}, {}, template="{{ .Prompt }}")]

        def gguf_header(self, m):
            return None

    netstat = "  TCP    0.0.0.0:11434          0.0.0.0:0              LISTENING\n"
    with tempfile.TemporaryDirectory() as tmp:
        home, proj = Path(tmp, "home"), Path(tmp, "my-project")
        (home / ".ollama").mkdir(parents=True)
        (home / ".ollama" / "history").write_bytes(b"x" * 2300)
        proj.mkdir()
        (proj / ".env").write_bytes(b"")
        findings = [check.check_network(netstat, ollama_host=""), check.check_version("0.15.2", "Windows"),
                    *check.check_models(ExampleStore()), check.check_secrets(proj),
                    *check.check_saved(home, "Linux", None, setting=lambda k: "")]
        text = check.render(findings).replace(tmp, "…")
    text = text.replace(str(Path("…", "home")), "~").replace(str(Path("…", "my-project")), "my-project")
    body = esc(text)
    for mark, cls in (("[OK]", "ok"), ("[!!]", "warn"), ("[--]", "info")):
        body = body.replace(mark, f'<span class="{cls}">{mark}</span>')
    return ('<figure class="viz" aria-labelledby="fig-term-title">\n'
            '  <figcaption><strong id="fig-term-title">Example: what the check-up prints</strong>'
            '<span>Produced by the real check-up code for a made-up computer that has Ollama open to its network, '
            'an old version, and a <code>.env</code> file in the project folder.</span></figcaption>\n'
            f'  <div class="term">{body}</div>\n</figure>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=str(ROOT / "runs"))
    ap.add_argument("--out", default=str(ROOT / "docs" / "_includes" / "fig"))
    args = ap.parse_args()
    runs, out = Path(args.runs), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    head = json.loads((runs / "p2-headline.json").read_text(encoding="utf-8"))
    lib, hf = head["p2-library"], head["p2-hf"]

    lib_models = sorted((runs / "p2-library" / "models").glob("*.json"))
    stale = 0
    for mp in lib_models:
        cv = json.loads(mp.read_text(encoding="utf-8")).get("conversion") or {}
        stale += bool(cv.get("match") == "exact" and cv.get("replaced_by"))

    a = lib["summary"]["all"]
    origin = a["origin"]
    origin_items = [(WHERE[k], v, f"{v} of the {a['material']} models that differ: {WHERE[k]}")
                    for k, v in sorted(origin.items(), key=lambda kv: -kv[1])]
    class_items = [(SHORT.get(k, k), v, f"{v} of the {a['strict']} models: {SHORT.get(k, k)}")
                   for k, v in a["classes"].items()]

    files = {
        "stats.html": stats(lib, hf, stale, len(lib_models)),
        "grid.html": grid(lib, hf),
        "origin.html": bars("fig-origin-title", "Where the difference starts",
                            f"The {a['material']} Ollama library models that read differently, by where the change first appears.",
                            origin_items, a["material"], "Counted from the three versions of each model's text: maker's, model file's, and Ollama's."),
        "classes.html": bars("fig-classes-title", "What changes most often",
                             f"The {a['strict']} library models that differ by more than field order. A model can have several kinds.",
                             class_items, a["strict"], "Each model counts once per kind of change, across the six tool conversations."),
        "specimen.html": specimen(runs),
        "checkup.html": checkup_example(),
    }
    for fname, text in files.items():
        (out / fname).write_text(text + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {out / fname}")


if __name__ == "__main__":
    main()
