"""Draw the article's figures as SVG (docs/assets/img/), from saved runs (no network).

Each SVG carries its own light and dark colours (prefers-color-scheme), so the same file works on
the website, on GitHub and in a PNG export for LinkedIn. Chart numbers come from
runs/p2-headline.json; the tool-format lines are copied from the qwen2.5 measurement.

Usage: python scripts/article_figures.py
"""

from __future__ import annotations

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets" / "img"

STYLE = """<style>
  .bg{fill:#fcfcfb} .card{fill:#f0efea} .ink{fill:#0b0b0b} .ink2{fill:#52514e} .mut{fill:#77756f}
  .acc{fill:#2a78d6} .accw{fill:#e8f1fc} .soft{fill:#86b6ef} .none{fill:#d6d4cc}
  .warn{fill:#a35200} .warnw{fill:#fdf1e3} .white{fill:#ffffff}
  .ln{stroke:#77756f;fill:none} .accl{stroke:#2a78d6;fill:none} .warnl{stroke:#a35200;fill:none} .rule{stroke:#e1e0d9}
  text{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
  .mono{font-family:ui-monospace,Consolas,Menlo,monospace}
  @media (prefers-color-scheme: dark){
    .bg{fill:#1a1a19} .card{fill:#232321} .ink{fill:#f0efec} .ink2{fill:#c3c2b7} .mut{fill:#9a988f}
    .acc{fill:#3987e5} .accw{fill:#142338} .soft{fill:#184f95} .none{fill:#3a3936}
    .warn{fill:#ec9a5a} .warnw{fill:#2d1d0f}
    .ln{stroke:#9a988f} .accl{stroke:#6da7ec} .warnl{stroke:#ec9a5a} .rule{stroke:#2c2c2a}
  }
</style>"""


def svg(w: int, h: int, title: str, desc: str, body: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-labelledby="t d">\n<title id="t">{escape(title)}</title>\n'
            f'<desc id="d">{escape(desc)}</desc>\n{STYLE}\n'
            f'<rect class="bg" width="{w}" height="{h}" rx="14"/>\n{body}\n</svg>\n')


def t(x, y, s, cls="ink", size=15, weight=400, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}" {extra}>{escape(s)}</text>')


def badge(x, y, n):
    return f'<circle cx="{x}" cy="{y}" r="12" class="acc"/>' + t(x, y + 5, str(n), "white", 13, 700, "middle")


def box(x, y, w, h, cls="card"):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" class="{cls}"/>'


def arrow(x1, y, x2):
    return (f'<line x1="{x1}" y1="{y}" x2="{x2 - 6}" y2="{y}" class="ln" stroke-width="2"/>'
            f'<path d="M{x2 - 8},{y - 5} L{x2},{y} L{x2 - 8},{y + 5} Z" class="mut"/>')


def fig_setup() -> str:
    """The parts of a local setup and the six weak spots."""
    b = [t(28, 40, "A local AI setup, and its six weak spots", "ink", 20, 700)]
    main = [("You", "type a message"), ("The app", "Ollama or LM Studio"),
            ("The layout step", "chat template"), ("The model", "reads one block of text")]
    spots = {1: [1, 2], 2: [4]}
    x0, bw, gap, y = 28, 170, 40, 70
    for i, (name, sub) in enumerate(main):
        x = x0 + i * (bw + gap)
        b.append(box(x, y, bw, 78))
        b.append(t(x + 16, y + 34, name, "ink", 16, 700))
        b.append(t(x + 16, y + 58, sub, "ink2", 13))
        for k, n in enumerate(spots.get(i, [])):
            b.append(badge(x + bw - 18 - (len(spots[i]) - 1 - k) * 28, y + 2, n))
        if i < 3:
            b.append(arrow(x + bw + 4, y + 39, x + bw + gap - 4))
    side = [("The model file", "model, settings, template", 3), ("Helpers", "read files, run commands", 5),
            ("Saved chats", "files on your disk", 6)]
    bw2 = 260
    for i, (name, sub, n) in enumerate(side):
        x = x0 + i * (bw2 + 12)
        b.append(box(x, 178, bw2, 70))
        b.append(t(x + 16, 208, name, "ink", 16, 700))
        b.append(t(x + 16, 231, sub, "ink2", 13))
        b.append(badge(x + bw2 - 18, 180, n))
    legend = ["the app answers anyone who can reach it", "older versions have known holes",
              "the model file carries more than the model", "the layout can change what it reads",
              "helpers turn words into actions", "chats are kept as ordinary files"]
    for i, s in enumerate(legend):
        x, y = 28 + (i % 3) * 272, 284 + (i // 3) * 26
        b.append(badge(x + 10, y - 5, i + 1).replace('r="12"', 'r="9"').replace('font-size="13"', 'font-size="11"'))
        b.append(t(x + 26, y, s, "ink2", 12.5))
    return svg(856, 330, "A local AI setup and its six weak spots",
               "You type a message; the app lays it out with the chat template; the model reads the result. "
               "The model file, helpers and saved chats sit alongside. Numbers mark the six weak spots.",
               "\n".join(b))


def fig_reach() -> str:
    """Who can reach the app, by setting, and what they get."""
    b = [t(28, 40, "Who can reach your Ollama, and what they can do", "ink", 20, 700)]
    rings = [(28, 64, 384, 252, "accw", "The internet", "if your router forwards port 11434"),
             (48, 126, 344, 172, "card", "Your Wi-Fi or office network", "OLLAMA_HOST=0.0.0.0, or LM Studio's network switch"),
             (68, 196, 304, 84, "bg", "This computer only", "the default: 127.0.0.1")]
    for x, y, w, h, cls, name, sub in rings:
        b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" class="{cls}" stroke-width="1.5" '
                 f'style="stroke:#77756f;stroke-opacity:.35"/>')
        b.append(t(x + 16, y + 26, name, "ink", 15, 700))
        b.append(t(x + 16, y + 46, sub, "ink2", 12.5, extra='' if cls != "accw" else ''))
    b.append(t(442, 82, "Anyone who can connect can, with no login:", "ink", 15, 700))
    rows = [("Chat with your models", "and see which ones you have"),
            ("Download, copy or delete models", ""),
            ("Create a model with its own instructions", ""),
            ("If you're signed in to ollama.com:", "warn"),
            ("see your account's name, email and plan", "w"),
            ("see its usage and balance", "w"),
            ("run cloud models and web searches on it", "w")]
    y = 112
    for s, kind in rows:
        if kind == "warn":
            y += 6
            b.append(t(442, y, s, "warn", 14, 700))
        elif kind == "w":
            b.append(f'<circle cx="450" cy="{y - 5}" r="3" class="warn"/>' + t(462, y, s, "ink", 14))
        else:
            b.append(f'<circle cx="450" cy="{y - 5}" r="3" class="acc"/>' + t(462, y, s, "ink", 14))
            if kind:
                y += 20
                b.append(t(462, y, kind, "ink2", 13))
        y += 26
    b.append(t(28, 338, "Source: Ollama v0.40.7, server/routes.go and server/cloud_proxy.go (read by the author).",
               "mut", 12))
    return svg(856, 356, "Who can reach your Ollama, and what they can do",
               "Three nested zones: this computer only (the default), your network (if OLLAMA_HOST is 0.0.0.0), "
               "and the internet (if the port is forwarded). Anyone who can connect can chat with, download, "
               "delete and create models, and, if the app is signed in to ollama.com, see the account and use "
               "its cloud models and web search.", "\n".join(b))


def fig_reach_narrow() -> str:
    """fig_reach stacked for phones: the zones on top, the list below, same words."""
    b = [t(16, 32, "Who can reach your Ollama,", "ink", 18, 700), t(16, 54, "and what they can do", "ink", 18, 700)]
    rings = [(16, 72, 328, 230, "accw", "The internet", ["if your router forwards port 11434"]),
             (30, 136, 300, 154, "card", "Your Wi-Fi or office network", ["OLLAMA_HOST=0.0.0.0, or", "LM Studio's network switch"]),
             (44, 220, 272, 58, "bg", "This computer only", ["the default: 127.0.0.1"])]
    for x, y, w, h, cls, name, subs in rings:
        b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" class="{cls}" stroke-width="1.5" '
                 f'style="stroke:#77756f;stroke-opacity:.35"/>')
        b.append(t(x + 14, y + 24, name, "ink", 15, 700))
        for i, sub in enumerate(subs):
            b.append(t(x + 14, y + 43 + i * 17, sub, "ink2", 13))
    y = 336
    b.append(t(16, y, "Anyone who can connect can,", "ink", 15, 700))
    b.append(t(16, y + 20, "with no login:", "ink", 15, 700))
    y += 50
    rows = [("Chat with your models", "acc"), ("and see which ones you have", "sub"),
            ("Download, copy or delete models", "acc"), ("Create a model with its own", "acc"),
            ("instructions", "sub"), ("If you're signed in to ollama.com:", "warn"),
            ("see your account's name, email", "w"), ("and plan", "sub"), ("see its usage and balance", "w"),
            ("run cloud models and web", "w"), ("searches on it", "sub")]
    for s_, kind in rows:
        if kind == "warn":
            y += 8
            b.append(t(16, y, s_, "warn", 14.5, 700))
        elif kind == "sub":
            y -= 4
            b.append(t(36, y, s_, "ink", 14.5))  # second line of the item above
        else:
            dot = "acc" if kind == "acc" else "warn"
            b.append(f'<circle cx="24" cy="{y - 5}" r="3" class="{dot}"/>' + t(36, y, s_, "ink", 14.5))
        y += 26
    b.append(t(16, y + 4, "Source: Ollama v0.40.7, server/routes.go", "mut", 12))
    b.append(t(16, y + 21, "and server/cloud_proxy.go (read by the author).", "mut", 12))
    return svg(360, y + 38, "Who can reach your Ollama, and what they can do",
               "Three nested zones: this computer only (the default), your network (if OLLAMA_HOST is 0.0.0.0), "
               "and the internet (if the port is forwarded). Anyone who can connect can chat with, download, "
               "delete and create models, and, if the app is signed in to ollama.com, see the account and use "
               "its cloud models and web search.", "\n".join(b))


def bars(b, x, y, label, num, den, width=330, cls="acc"):
    w = round(width * num / den, 1)
    b.append(t(x, y, label, "ink", 14))
    b.append(f'<rect x="{x}" y="{y + 8}" width="{width}" height="14" rx="4" class="none"/>')
    b.append(f'<rect x="{x}" y="{y + 8}" width="{w}" height="14" rx="4" class="{cls}"/>')
    b.append(t(x + width + 10, y + 21, f"{num} of {den}", "ink", 14, 700))


def fig_results(head: dict) -> str:
    lib, hf = head["p2-library"]["summary"], head["p2-hf"]["summary"]
    b = [t(28, 40, "How many popular models read their tool conversations differently", "ink", 20, 700),
         t(28, 62, "Compared with the maker's own template. Snapshot of 22 October 2026, Ollama v0.40.7.", "ink2", 13)]
    a, tc = lib["all"], lib["tool_capable"]
    rows = [("Ollama library, all compared models", a["material"], a["packages"]),
            ("…setting aside field-order-only changes", a["strict"], a["packages"]),
            ("Ollama library, models built for tools", tc["material"], tc["packages"]),
            ("Hugging Face downloads", hf["all"]["material"], hf["all"]["packages"])]
    y = 100
    for label, n, d in rows:
        bars(b, 28, y, label, n, d, cls="acc" if "Hugging" not in label else "soft")
        y += 52
    o = a["origin"]
    total = sum(o.values())
    b.append(t(470, 100, f"Where the {total} library differences start", "ink", 15, 700))
    parts = [("Ollama's own version of the template", o.get("Ollama", 0)),
             ("An old copy in the model file, then Ollama's", o.get("conversion and Ollama", 0)),
             ("The model file has no template", o.get("no GGUF template", 0))]
    y = 132
    for label, n in parts:
        bars(b, 470, y, label, n, total, width=290)
        y += 52
    b.append(t(28, 318, "Source: runs/p2-headline.json in the project repository.", "mut", 12))
    return svg(856, 336, "How many popular models read their tool conversations differently",
               f"Ollama library: {a['material']} of {a['packages']} differ ({a['strict']} setting aside "
               f"order-only changes); built for tools: {tc['material']} of {tc['packages']}; Hugging Face: "
               f"{hf['all']['material']} of {hf['all']['packages']}. Of the library differences, "
               f"{o.get('Ollama', 0)} start in Ollama's own template, {o.get('conversion and Ollama', 0)} in an old "
               f"copy in the model file, {o.get('no GGUF template', 0)} where the file has no template.",
               "\n".join(b))


MAKER = ['{"type": "function", "function": {', '  "name": "get_weather",',
         '  "description": "Current weather for a city",', '  "parameters": {"type": "object",',
         '    "properties": {"city": {"type": "string",', '      "description": "City name"},',
         '      "unit": {"type": "string",', '               "enum": ["c", "f"]}},', '    "required": ["city"]}}}']
OLLAMA = ['{"type": "function", "function": {', '  get_weather', '  Current weather for a city',
          '  {object <nil> <nil> [city]', '   {"city":{"type":"string",', '     "description":"City name"},',
          '    "unit":{"type":"string","enum":["c","f"]}}}}}']


def fig_tool_format() -> str:
    b = [t(28, 40, "The same tool, as qwen2.5 reads it", "ink", 20, 700),
         t(28, 62, "One weather tool from a practice conversation. Line breaks added for reading.", "ink2", 13)]
    for x, title, lines, cls in ((28, "From the maker's template (what it was trained on)", MAKER, "card"),
                                 (440, "From Ollama's template", OLLAMA, "warnw")):
        b.append(box(x, 80, 388, 272, cls))
        b.append(t(x + 16, 106, title, "ink", 14, 700))
        for i, line in enumerate(lines):
            y = 136 + i * 22
            parts = line.split("<nil>") if "<nil>" in line else [line]
            if len(parts) == 1:
                b.append(t(x + 16, y, line, "ink", 13, extra='class="mono" xml:space="preserve"').replace(
                    'class="ink"', 'class="ink mono"', 1).replace(' class="mono"', ""))
            else:
                spans = ('<tspan class="warn" font-weight="700">&lt;nil&gt;</tspan>').join(escape(p) for p in parts)
                b.append(f'<text x="{x + 16}" y="{y}" class="ink mono" font-size="13" xml:space="preserve">{spans}</text>')
    b.append(t(28, 376, "Left: every part is labelled (\"name\", \"description\", \"parameters\"). "
               "Right: the labels are gone, and <nil> (Go for \"empty\") appears.", "ink2", 13))
    return svg(856, 396, "The same tool, as qwen2.5 reads it",
               "On the left, the maker's template gives the tool as labelled JSON. On the right, Ollama's "
               "template gives the same tool in Go's default format: the labels are missing and <nil> appears.",
               "\n".join(b))


CATEGORY_NAMES = {"simple_python": "One tool, one call", "multiple": "Pick the right tool",
                  "parallel": "One tool, several calls", "parallel_multiple": "Several tools, several calls",
                  "irrelevance": "No suitable tool: don't call"}


def pct(c: int, n: int) -> str:
    """Percentage to one decimal, rounding halves up (147/240 -> 61.3, not float's 61.2)."""
    return f"{(1000 * c + n // 2) // n / 10:.1f}%"


def fig_tool_test(report: dict) -> str:
    """H3 mini-test: correct answers per category, Ollama's layout (A1) vs the maker's (B)."""
    rows = report["results"]
    b = [t(28, 40, "Does the layout change how well qwen2.5 uses tools?", "ink", 20, 700),
         t(28, 62, "Share of test questions answered correctly, same model and settings, two prompt layouts.",
           "ink2", 13)]
    b.append(f'<rect x="470" y="76" width="12" height="12" rx="3" class="acc"/>' + t(488, 87, "Ollama's layout", "ink", 13))
    b.append(f'<rect x="610" y="76" width="12" height="12" rx="3" class="warn"/>' + t(628, 87, "The maker's layout", "ink", 13))
    y, width = 120, 300
    for cat in list(CATEGORY_NAMES) + ["overall"]:
        r = rows[cat]
        n = r["n"]
        name = CATEGORY_NAMES.get(cat, "All five together")
        b.append(t(28, y + 14, name, "ink", 14, 700 if cat == "overall" else 400))
        b.append(t(28, y + 32, f"{n} questions", "mut", 12))
        for k, (arm, cls) in enumerate((("A1", "acc"), ("B", "warn"))):
            c = r[f"{arm}_correct"]
            yy = y + k * 18
            w = round(width * c / n, 1)
            b.append(f'<rect x="250" y="{yy}" width="{width}" height="13" rx="4" class="none"/>')
            b.append(f'<rect x="250" y="{yy}" width="{w}" height="13" rx="4" class="{cls}"/>')
            b.append(t(560, yy + 11, f"{pct(c, n)}  ({c} of {n})", "ink", 12.5))
        diff = r["B_correct"] - r["A1_correct"]
        sig = r.get("p_holm", r["p_exact"])
        verdict = "clear" if sig < 0.05 else "not conclusive alone"
        b.append(t(828, y + 22, f"{diff:+d}, {verdict}", "ink2", 12.5, anchor="end"))
        y += 58 if cat != "irrelevance" else 66
    b.append(t(28, y + 8, "Right: extra correct answers with the maker's layout. \"Clear\": exact paired test, p below 0.05 "
               "(categories corrected for five tests).", "mut", 12))
    b.append(t(28, y + 26, "Source: runs/h3-mini/qwen2.5/report.json; questions from the Berkeley Function Calling "
               "Leaderboard (BFCL).", "mut", 12))
    return svg(856, y + 44, "Does the layout change how well qwen2.5 uses tools?",
               "; ".join(f"{CATEGORY_NAMES.get(c, 'Overall')}: Ollama's layout {rows[c]['A1_correct']} of "
                         f"{rows[c]['n']}, maker's layout {rows[c]['B_correct']} of {rows[c]['n']}"
                         for c in list(CATEGORY_NAMES) + ["overall"]), "\n".join(b))


def fig_tool_test_narrow(report: dict) -> str:
    """fig_tool_test stacked for phones: each category's name, then its two bars and values."""
    rows = report["results"]
    b = [t(16, 32, "Does the layout change how", "ink", 18, 700), t(16, 54, "well qwen2.5 uses tools?", "ink", 18, 700),
         t(16, 76, "Share of test questions answered correctly.", "ink2", 13)]
    b.append('<rect x="16" y="90" width="12" height="12" rx="3" class="acc"/>' + t(34, 101, "Ollama's layout", "ink", 13))
    b.append('<rect x="170" y="90" width="12" height="12" rx="3" class="warn"/>' + t(188, 101, "The maker's layout", "ink", 13))
    y, width = 136, 168
    for cat in list(CATEGORY_NAMES) + ["overall"]:
        r = rows[cat]
        n = r["n"]
        diff = r["B_correct"] - r["A1_correct"]
        clear = r.get("p_holm", r["p_exact"]) < 0.05
        b.append(t(16, y, CATEGORY_NAMES.get(cat, "All five together"), "ink", 14.5, 700 if cat == "overall" else 600))
        b.append(t(344, y, f"{diff:+d}{', clear' if clear else ''}", "ink2", 13, anchor="end"))
        for k, (arm, cls) in enumerate((("A1", "acc"), ("B", "warn"))):
            c = r[f"{arm}_correct"]
            yy = y + 10 + k * 20
            b.append(f'<rect x="16" y="{yy}" width="{width}" height="13" rx="4" class="none"/>')
            b.append(f'<rect x="16" y="{yy}" width="{round(width * c / n, 1)}" height="13" rx="4" class="{cls}"/>')
            b.append(t(194, yy + 11, f"{pct(c, n)} ({c} of {n})", "ink", 12.5))
        y += 72
    b.append(t(16, y - 6, "Right of each name: extra correct answers", "mut", 12))
    b.append(t(16, y + 11, "with the maker's layout. \"Clear\": exact", "mut", 12))
    b.append(t(16, y + 28, "paired test, p below 0.05.", "mut", 12))
    b.append(t(16, y + 50, "Source: runs/h3-mini/qwen2.5/report.json;", "mut", 12))
    b.append(t(16, y + 67, "questions from BFCL.", "mut", 12))
    return svg(360, y + 84, "Does the layout change how well qwen2.5 uses tools?",
               "; ".join(f"{CATEGORY_NAMES.get(c, 'Overall')}: Ollama's layout {rows[c]['A1_correct']} of "
                         f"{rows[c]['n']}, maker's layout {rows[c]['B_correct']} of {rows[c]['n']}"
                         for c in list(CATEGORY_NAMES) + ["overall"]), "\n".join(b))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    head = json.loads((ROOT / "runs" / "p2-headline.json").read_text(encoding="utf-8"))
    figs = {"setup.svg": fig_setup(), "reach.svg": fig_reach(), "reach-narrow.svg": fig_reach_narrow(), "results.svg": fig_results(head),
            "tool-format.svg": fig_tool_format()}
    test = ROOT / "runs" / "h3-mini" / "qwen2.5" / "report.json"
    if test.exists():
        report = json.loads(test.read_text(encoding="utf-8"))
        figs["tool-test.svg"] = fig_tool_test(report)
        figs["tool-test-narrow.svg"] = fig_tool_test_narrow(report)
    for name, s in figs.items():
        (OUT / name).write_text(s, encoding="utf-8", newline="\n")
        print("wrote", (OUT / name).relative_to(ROOT))


if __name__ == "__main__":
    main()
