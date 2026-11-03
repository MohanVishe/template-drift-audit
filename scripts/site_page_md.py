"""A site page (docs/*.md, Jekyll + HTML blocks) -> plain Markdown for GitHub, at the repo root.

Drops the front matter and the layout <div>s, turns figures into Markdown images and the stat tiles
into a list, and points links at the GitHub copies. Fails if any HTML is left.

Usage: python scripts/site_page_md.py docs/tool-test.md TOOL-TEST.md
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://mohanvishe.github.io/template-drift-audit/"
LINKS = {
    'href="./"': "ARTICLE.md",
    "./#the-layout-step-can-change-what-the-model-reads": "ARTICLE.md#weak-spot-4-the-layout-step-can-change-what-the-model-reads",
}


def convert(src: str, page: str) -> str:
    s = src.split("---\n", 2)[2].lstrip("\n")
    s = re.sub(r'<a href="\./">([^<]+)</a>', r"[\1](ARTICLE.md)", s)
    s = s.replace("./#the-layout-step-can-change-what-the-model-reads", LINKS["./#the-layout-step-can-change-what-the-model-reads"])
    s = re.sub(r'<p class="lede">(.*?)</p>', lambda m: m.group(1), s, flags=re.S)

    def stats(m: re.Match) -> str:
        tiles = re.findall(r'<div class="stat-v">(.*?)</div><div class="stat-l">(.*?)</div>', m.group(0))
        return "".join(f"- **{html.unescape(re.sub(r'</?span>', '', v))}:** {html.unescape(l)}\n" for v, l in tiles)

    s = re.sub(r'<div class="stats">.*?\n</div>\n', stats, s, flags=re.S)
    s = re.sub(r'<figure class="fig-img">.*?<img src="assets/img/([\w-]+)\.svg" alt="([^"]*)"></picture></figure>',
               lambda m: f"![{m.group(2)}](docs/assets/img/{m.group(1)}.svg)", s)
    s = re.sub(r"^</?div[^>]*>\n", "", s, flags=re.M)
    s = s.replace("### The short version", "## The short version")
    s = re.sub(r"\n{3,}", "\n\n", s)
    title, rest = s.split("\n", 1)
    s = f"{title}\n\n*Also on the website: {SITE}{page}*\n{rest}"
    left = [l for l in s.splitlines() if re.search(r"<(?!nil>)[a-z/]", l)]
    if left:
        raise SystemExit(f"HTML left over: {left[:3]}")
    return s


def main() -> None:
    src, out = ROOT / sys.argv[1], ROOT / sys.argv[2]
    page = src.with_suffix(".html").name
    out.write_text(convert(src.read_text(encoding="utf-8"), page), encoding="utf-8", newline="\n")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
