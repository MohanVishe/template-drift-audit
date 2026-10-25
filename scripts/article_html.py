"""A Markdown article -> a plain HTML page in article/ (gitignored) to open in a browser and copy
into LinkedIn's article editor (which keeps headings, bold, lists and links from pasted HTML but
does not read Markdown). Handles only what the articles use: headings, paragraphs, lists (one
level of nesting), tables (as lists), fenced code, rules, `code`, **bold**, *italic*, [links](url) and bare URLs.

Usage: python scripts/article_html.py                    (ARTICLE.md -> article/linkedin-article.html)
       python scripts/article_html.py TOOL-TEST.md article/linkedin-tool-test.html
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "ARTICLE.md"
OUT = ROOT / "article" / "linkedin-article.html"


def inline(text: str) -> str:
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) > 1:
            out.append(f"<code>{html.escape(p[1:-1])}</code>")
            continue
        p = html.escape(p, quote=False)
        p = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', p)
        p = re.sub(r"(?<![\"'>])(https?://[^\s<]+[^\s<.,;:)])", r'<a href="\1">\1</a>', p)
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", p)
        out.append(p)
    return "".join(out)


def join_items(lines: list[str]) -> list[str]:
    """Fold a list item's wrapped lines into it, so inline markup can span them."""
    out: list[str] = []
    in_code = False
    for line in lines:
        if line.startswith("```"):
            in_code = not in_code
        elif (not in_code and out and line.startswith(" ") and line.strip()
              and not re.match(r"^\s*(?:[-*]|\d+\.) ", line)
              and re.match(r"^\s*(?:[-*]|\d+\.) ", out[-1])):
            out[-1] += " " + line.strip()
            continue
        out.append(line)
    return out


def convert(md: str) -> str:
    lines = join_items(md.splitlines())
    out: list[str] = []
    para: list[str] = []
    stack: list[tuple[str, int]] = []  # open lists: (tag, indent)
    item_open: list[bool] = []
    i = 0

    def flush_para():
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()

    def close_lists(to_indent: int = -1):
        while stack and stack[-1][1] > to_indent:
            tag, _ = stack.pop()
            if item_open.pop():
                out.append("</li>")
            out.append(f"</{tag}>")

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            flush_para()
            close_lists()
            j = i + 1
            while not lines[j].startswith("```"):
                j += 1
            out.append("<pre><code>" + html.escape("\n".join(lines[i + 1:j])) + "</code></pre>")
            i = j + 1
            continue
        if line.startswith("|"):
            flush_para()
            close_lists()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            # LinkedIn's editor has no tables: one list item per row, "first cell: header value; ..."
            head, *body = rows
            out.append("<ul>" + "".join(
                f"<li><strong>{inline(r[0].strip('*'))}</strong>: "
                + "; ".join(f"{inline(h)}: {inline(c.strip('*'))}" for h, c in zip(head[1:], r[1:])) + "</li>"
                for r in body) + "</ul>")
            continue
        img = re.match(r"^!\[([^\]]*)\]\(docs/assets/img/([\w-]+)\.svg\)$", line)
        if img:
            # LinkedIn does not take pasted local images: show the PNG to upload at this spot.
            flush_para()
            close_lists()
            out.append(f'<div class="img"><p class="note">Insert image here: article/img/{img.group(2)}.png '
                       f'(delete this line)</p><img src="img/{img.group(2)}.png" alt="{html.escape(img.group(1))}"></div>')
            i += 1
            continue
        m = re.match(r"^(#{1,3}) (.*)", line)
        if m:
            flush_para()
            close_lists()
            n = len(m.group(1))
            out.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
        elif line.strip() == "---":
            flush_para()
            close_lists()
            out.append("<hr>")
        elif not line.strip():
            flush_para()
            # a blank line ends a list unless the next line continues it
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            if not re.match(r"^\s*(?:[-*]|\d+\.) ", nxt):
                close_lists()
        else:
            m = re.match(r"^(\s*)([-*]|\d+\.) (.*)", line)
            if m:
                flush_para()
                indent = len(m.group(1))
                tag = "ol" if m.group(2)[0].isdigit() else "ul"
                close_lists(indent)
                if not stack or stack[-1][1] < indent:
                    out.append(f"<{tag}>")
                    stack.append((tag, indent))
                    item_open.append(False)
                if item_open[-1]:
                    out.append("</li>")
                out.append(f"<li>{inline(m.group(3))}")
                item_open[-1] = True
            else:
                close_lists()
                para.append(line.strip())
        i += 1
    flush_para()
    close_lists()
    return "\n".join(out)


def main() -> None:
    src = ROOT / sys.argv[1] if len(sys.argv) > 1 else SRC
    out = ROOT / sys.argv[2] if len(sys.argv) > 2 else OUT
    md = src.read_text(encoding="utf-8")
    title = md.splitlines()[0].lstrip("# ").strip()
    body = convert(md)
    out.write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} (LinkedIn copy)</title>
<style>body{{max-width:46rem;margin:2rem auto;padding:0 16px;font:17px/1.6 Georgia,serif;color:#1d1d1f;background:#fff}}
pre{{white-space:pre-wrap;word-break:break-all;background:#f4f4f4;padding:10px;font-size:13px}}
code{{font-size:0.92em}} .img img{{max-width:100%;border-radius:10px}} .note{{font:14px/1.5 system-ui,sans-serif;background:#fff6d6;padding:10px 14px;border-radius:8px}}</style>
</head><body>
<p class="note">For LinkedIn: select everything below this box (from the title to the end), copy, and paste into a new LinkedIn article. Put the title in LinkedIn's title field and delete it from the body.</p>
{body}
</body></html>
""", encoding="utf-8", newline="\n")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
