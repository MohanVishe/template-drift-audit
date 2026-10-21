"""Small helpers over huggingface.co/api/models/<repo>/revision/main (the only HF endpoint used here)."""

from __future__ import annotations

import json
import re
import urllib.error

HF = "https://huggingface.co"
TEMPLATE_FILES = ("chat_template.jinja", "chat_template.json")


def revision(f, repo: str) -> dict | None:
    """Model info at main, or None if the repo does not exist (404) or is hidden (401)."""
    try:
        body = f.get_optional(f"{HF}/api/models/{repo}/revision/main")
        return json.loads(body) if body is not None else None
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return None
        raise


def files(info: dict) -> list[str]:
    return [s["rfilename"] for s in info.get("siblings", [])]


def template_file(info: dict) -> str | None:
    """Which file transformers would load the chat template from, in transformers' own order."""
    names = set(files(info))
    for name in TEMPLATE_FILES:
        if name in names:
            return name
    tok = (info.get("config") or {}).get("tokenizer_config") or {}
    if tok.get("chat_template") and "tokenizer_config.json" in names:
        return "tokenizer_config.json"
    return None


def base_models(info: dict) -> list[str]:
    b = (info.get("cardData") or {}).get("base_model") or []
    return [b] if isinstance(b, str) else list(b)


def base_relations(info: dict) -> list[str]:
    """'quantized:Qwen/Qwen3.8-27B' style entries from the hub's normalised `base_model:<relation>:<repo>` tags."""
    return [t.removeprefix("base_model:") for t in info.get("tags", []) if t.count(":") == 2 and t.startswith("base_model:")]


def template_text(info: dict) -> str | None:
    """The default chat template the hub reports for a (non-GGUF) repo, or None."""
    cfg = info.get("config") or {}
    if isinstance(cfg.get("chat_template_jinja"), str):
        return cfg["chat_template_jinja"]
    ct = (cfg.get("tokenizer_config") or {}).get("chat_template")
    if isinstance(ct, list):
        ct = next((t["template"] for t in ct if t.get("name") == "default"), None)
    return ct if isinstance(ct, str) else None


# Q4_K_M first, then the nearest alternatives by bits per weight.
QUANT_PREF = ["Q4_K_M", "Q4_K_XL", "Q4_K_L", "Q4_K_P", "Q4_K_S", "IQ4_XS", "IQ4_NL", "NVFP4", "MXFP4", "Q4_0", "Q4_1",
              "Q5_K_M", "Q5_K_S", "Q3_K_XL", "Q3_K_L", "Q3_K_M", "IQ3_M", "IQ3_S", "IQ3_XS", "IQ3_XXS", "Q6_K", "Q8_0",
              "IQ2_M", "IQ2_S", "IQ2_XS", "Q2_K", "PQ2_0"]
SKIP = re.compile(r"(mmproj|(^|/)imatrix|(^|/)mtp-|vision|encoder|draft)", re.I)  # projectors, imatrix data, draft heads


def pick_quant(info: dict) -> tuple[str | None, str | None]:
    """(quant label, file) for Q4_K_M or the nearest quant. Prefers files without a bundled MTP head."""
    ggufs = [n for n in files(info) if n.lower().endswith(".gguf") and not SKIP.search(n)]
    for pool in ([n for n in ggufs if "mtp" not in n.lower()], ggufs):
        for q in QUANT_PREF:
            pat = re.compile(rf"(?<![A-Za-z0-9]){q}(?![A-Za-z0-9])", re.I)
            hits = sorted(n for n in pool if pat.search(n.replace("UD-", "")))
            if hits:
                return q, hits[0]
    return (None, ggufs[0]) if ggufs else (None, None)
