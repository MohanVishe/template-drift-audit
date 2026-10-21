"""Parse a saved ollama.com/library/<name>/tags page: every tag with its digest, size and inputs.

The default tag is `latest`; `aliases_of_latest` lists the other tags that share its digest
(for example `8b` and `8b-q4_K_M`), which says which size and quant `latest` is.
"""

from __future__ import annotations

import re


def parse(page: str) -> dict:
    tags = []
    for m in re.finditer(r'<a href="/library/([^"]+)" class="md:hidden.*?</a>', page, re.S):
        block = m.group(0)
        name = m.group(1)
        digest = re.search(r'<span class="font-mono">\s*([0-9a-f]{12})</span>', block)
        detail = re.search(r'</span>\s*•\s*([^•<]+?)\s*•\s*([^•<]+?)\s*•', block)
        inputs = re.search(r'<div class="flex sm:hidden">\s*([^•<]+?)\s*•', block)
        tags.append({
            "tag": name.split(":", 1)[1] if ":" in name else name,
            "digest": digest.group(1) if digest else None,
            "size": detail.group(1).strip() if detail else "",
            "context": detail.group(2).strip() if detail else "",
            "input": inputs.group(1).strip() if inputs else "",
        })
    latest = next((t for t in tags if t["tag"] == "latest"), None)
    aliases = [t["tag"] for t in tags if latest and t is not latest and t["digest"] and t["digest"] == latest["digest"]]
    return {"tags": tags, "latest": latest, "aliases_of_latest": aliases}


def best_alias(aliases: list[str]) -> str:
    """The shortest alias, which is the size tag (`8b`) rather than the quant tag (`8b-q4_K_M`)."""
    return min(aliases, key=lambda a: (len(a), a)) if aliases else ""
