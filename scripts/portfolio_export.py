"""Export the two articles and their figures to the portfolio site (github.com/MohanVishe/portfolio).

- Figures: docs/assets/img/*.svg -> <portfolio>/content/figures/tda-*.svg. The portfolio inlines its
  figures and themes them with its own CSS variables, so each class from this project's <style>
  block becomes inline fill/stroke attributes using the portfolio's --color-* and --fig-* tokens
  (with light fallbacks), and the <style> block and fixed sizes are dropped.
- Articles: ARTICLE.md and TOOL-TEST.md -> <portfolio>/content/blog/<slug>.mdx with front matter.
  Images become the portfolio's figure placeholders, links between the two articles become blog
  links, and the category table becomes a list (the portfolio right-aligns non-first columns).

Usage: python scripts/portfolio_export.py ../portfolio
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "docs" / "assets" / "img"
REPO = "https://github.com/MohanVishe/template-drift-audit"

FIGURES = ["glance", "setup", "reach", "wild", "cves", "journey", "results", "tool-format", "helpers",
           "tool-test", "tool-readers"]

# class -> attributes, in the portfolio's tokens. Fallbacks are its light theme.
FILL = {
    "bg": 'fill="var(--color-surface, #ffffff)" stroke="var(--color-line, #e7e7e4)"',
    "card": 'fill="var(--color-chip, #f4f4f2)"',
    "ink": 'fill="var(--color-ink, #0a0a0b)"',
    "ink2": 'fill="var(--color-muted, #52525b)"',
    "mut": 'fill="var(--color-faint, #71717a)"',
    "acc": 'fill="var(--fig-blue, #1f5fa8)"',
    "accw": 'fill="var(--fig-blue-bg, #e7f0fb)"',
    "soft": 'fill="var(--fig-blue, #1f5fa8)" fill-opacity="0.45"',
    "none": 'fill="var(--color-line-strong, #d9d9d4)"',
    "warn": 'fill="var(--fig-orange, #c2670f)"',
    "warnw": 'fill="var(--fig-orange-bg, #fcefe3)"',
    "white": 'fill="var(--fig-on-colour, #ffffff)"',
    "ln": 'stroke="var(--color-faint, #71717a)" fill="none"',
    "accl": 'stroke="var(--fig-blue, #1f5fa8)" fill="none"',
    "warnl": 'stroke="var(--fig-orange, #c2670f)" fill="none"',
    "rule": 'stroke="var(--color-line, #e7e7e4)"',
    "mono": 'font-family="ui-monospace, Consolas, Menlo, monospace"',
}

POSTS = {
    "ARTICLE.md": {
        "slug": "running-ai-locally",
        "date": "2026-10-24",
        "featured": True,
        "tags": ["Local AI", "Ollama", "Security", "Evaluation"],
    },
    "TOOL-TEST.md": {
        "slug": "does-the-layout-change-tool-use",
        "date": "2026-10-25",
        "title": "Part 2: does the layout change how well a model uses tools?",
        "tags": ["Local AI", "Ollama", "Tool calling", "Evaluation"],
        "summary": "A paired test of 1,240 tool-calling questions on qwen2.5: the prompt layout Ollama "
                   "uses against the one the model's maker designed, read by two different parsers. "
                   "The maker's layout got 3 to 4 more right in every 100.",
    },
}


def theme_svg(svg: str, name: str) -> str:
    svg = re.sub(r"<style>.*?</style>\n?", "", svg, flags=re.S)
    svg = re.sub(r' width="\d+" height="\d+" role=', " role=", svg, count=1)
    svg = svg.replace('aria-labelledby="t d"', f'aria-labelledby="tda-{name}-t tda-{name}-d"')
    svg = svg.replace('<title id="t">', f'<title id="tda-{name}-t">').replace('<desc id="d">', f'<desc id="tda-{name}-d">')

    def attrs(m: re.Match) -> str:
        out = []
        for c in m.group(1).split():
            if c not in FILL:
                raise SystemExit(f"{name}: unknown class {c!r}")
            out.append(FILL[c])
        return " ".join(out)

    svg = re.sub(r'class="([^"]+)"', attrs, svg)
    if "class=" in svg or "<style" in svg:
        raise SystemExit(f"{name}: styling left over")
    return svg


def to_mdx(md: str, meta: dict) -> str:
    lines = md.splitlines()
    title = meta.get("title") or lines[0].removeprefix("# ").strip()
    body = "\n".join(lines[1:]).lstrip("\n")
    # The italic line under the title is the subtitle (it becomes the summary) or the "also on the
    # website" note; either way it leaves the body.
    first, body = body.split("\n\n", 1)
    summary = meta.get("summary") or re.sub(r"\s+", " ", first.strip("*")).strip()
    body = re.sub(r"!\[[^\]]*\]\(docs/assets/img/([\w-]+)\.svg\)", r'<div data-figure="tda-\1"></div>', body)
    for src, m in POSTS.items():
        body = re.sub(rf"\]\({re.escape(src)}(#[\w-]+)?\)", f"](/blog/{m['slug']})", body)
    body = re.sub(r"\]\((?!https?://|/|#)([^)]+)\)", lambda x: f"]({REPO}/blob/main/{x.group(1)})", body)

    def category_table(m: re.Match) -> str:
        rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in m.group(0).strip().splitlines()[2:]]
        return "".join(f"- **{name}** ({n} questions). {what}\n" for name, what, n in rows) + "\n"

    body = re.sub(r"^\| Category \| What the model has to do \| Questions \|\n(?:\|.*\|\n)+", category_table, body, flags=re.M)

    def advisory_table(m: re.Match) -> str:
        rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in m.group(0).strip().splitlines()[2:]]
        return "".join(f"- **{ver}** ({day}), {cve}: {what}\n" for ver, day, cve, what in rows) + "\n"

    body = re.sub(r"^\| Fixed in \| Released \| CVE \| What it is \|\n(?:\|.*\|\n)+", advisory_table, body, flags=re.M)
    # The site's headings carry no ids: drop the contents line and keep in-page links as plain text.
    body = re.sub(r"^\*\*Contents:\*\*.*?\n\n", "", body, flags=re.M | re.S)
    body = re.sub(r"\[([^\]]+)\]\(#[\w-]+\)", r"\1", body)
    if len(summary) > 400:
        summary = summary[:397].rsplit(" ", 1)[0] + "…"
    fm = [f'title: "{title}"', f"date: {meta['date']}", f'summary: "{summary.replace(chr(34), chr(39))}"',
          "tags: [" + ", ".join(f'"{t}"' for t in meta["tags"]) + "]"] + (["featured: true"] if meta.get("featured") else [])
    note = (f"\n\n---\n\n*Also published with the code and data: [the project on GitHub]({REPO}).*\n")
    return "---\n" + "\n".join(fm) + "\n---\n\n" + body.rstrip() + note


def main() -> None:
    dst = (Path.cwd() / sys.argv[1]).resolve()
    figs, blog = dst / "content" / "figures", dst / "content" / "blog"
    if not figs.is_dir() or not blog.is_dir():
        raise SystemExit(f"{dst} is not the portfolio checkout")
    for name in FIGURES:
        out = figs / f"tda-{name}.svg"
        out.write_text(theme_svg((IMG / f"{name}.svg").read_text(encoding="utf-8"), name), encoding="utf-8", newline="\n")
        print("wrote", out)
    for src, meta in POSTS.items():
        out = blog / f"{meta['slug']}.mdx"
        out.write_text(to_mdx((ROOT / src).read_text(encoding="utf-8"), meta), encoding="utf-8", newline="\n")
        print("wrote", out)


if __name__ == "__main__":
    main()
