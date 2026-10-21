"""Parse the saved ollama.com/library?sort=popular snapshot into rows.

Usage: python population/tools/parse_library.py <snapshot.html>  (prints JSON rows in page order)
"""

from __future__ import annotations

import html
import json
import re
import sys

SIZE_CLASS = "bg-[#ddf4ff]"  # size tags (8b, 70b, ...) are blue; capability tags use other colours


def parse_pulls(s: str) -> int:
    s = s.strip().replace(",", "")
    mult = {"K": 1e3, "M": 1e6, "B": 1e9}.get(s[-1:], 1)
    return int(round(float(s.rstrip("KMB")) * mult))


def parse(page: str) -> list[dict]:
    rows = []
    for rank, li in enumerate(re.findall(r'<li\s+class="flex items-baseline.*?</li>', page, re.S), 1):
        name = re.search(r'href="/library/([^"]+)"', li).group(1)
        desc = re.search(r'<p class="max-w-lg[^"]*">(.*?)</p>', li, re.S)
        caps, sizes = [], []
        for cls, text in re.findall(r'<span\s+class="inline-flex items-center rounded-md ([^"]*)">([^<]+)</span>', li):
            (sizes if SIZE_CLASS in cls else caps).append(text.strip())
        pulls = re.search(r'<span\s*>([\d.,]+[KMB]?)</span>\s*<span class="hidden sm:flex">&nbsp;Pulls', li)
        tags = re.search(r'<span\s*>(\d+)</span>\s*<span class="hidden sm:flex">&nbsp;Tags', li)
        updated = re.search(r'title="([^"]+UTC)"', li)
        rows.append({
            "rank": rank, "name": name,
            "description": html.unescape(desc.group(1).strip()) if desc else "",
            "capabilities": caps, "sizes": sizes,
            "pulls_display": pulls.group(1) if pulls else "",
            "pulls": parse_pulls(pulls.group(1)) if pulls else None,
            "tag_count": int(tags.group(1)) if tags else None,
            "updated": updated.group(1) if updated else "",
        })
    return rows


if __name__ == "__main__":
    print(json.dumps(parse(open(sys.argv[1], encoding="utf-8").read()), indent=1, ensure_ascii=False))
