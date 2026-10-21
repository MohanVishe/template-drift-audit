"""Read Ollama-style registries without pulling weights.

Covers registry.ollama.ai (the Ollama library) and hf.co (Hugging Face's
Ollama-compatible endpoint for GGUF repos). Small layers are fetched whole; the
model layer is read only as far as its GGUF metadata section.
"""

from __future__ import annotations

import json

from tda.gguf import GGUFHeader, RangedSource, read_header
from tda.http import Fetcher
from tda.sources.ollama_store import MT_MODEL, MT_PARAMS, MT_SYSTEM, MT_TEMPLATE, OllamaModel

MANIFEST_ACCEPT = "application/vnd.docker.distribution.manifest.v2+json"
SMALL_LAYER_LIMIT = 1 << 20  # never fetch a non-model layer bigger than this


class Registry:
    def __init__(self, fetcher: Fetcher, base: str):
        self.f = fetcher
        self.base = base.rstrip("/")

    def _manifest_url(self, repo: str, tag: str) -> str:
        return f"{self.base}/v2/{repo}/manifests/{tag}"

    def blob_url(self, repo: str, digest: str) -> str:
        return f"{self.base}/v2/{repo}/blobs/{digest}"

    def _small(self, repo: str, layer: dict) -> str:
        if layer["size"] > SMALL_LAYER_LIMIT:
            raise ValueError(f"{layer['mediaType']} layer of {layer['size']:,} bytes is not a small layer")
        return self.f.get(self.blob_url(repo, layer["digest"])).decode("utf-8")

    def load(self, repo: str, tag: str, display_name: str) -> OllamaModel:
        manifest = self.f.get_json(self._manifest_url(repo, tag), accept=MANIFEST_ACCEPT)
        config = json.loads(self._small(repo, manifest["config"]))
        m = OllamaModel(display_name, manifest, config)
        for layer in manifest.get("layers", []):
            mt = layer["mediaType"]
            m.layer_digests.setdefault(mt, layer["digest"])
            if mt == MT_MODEL and m.model_digest is None:
                m.model_digest = layer["digest"]
            elif mt == MT_TEMPLATE:
                m.template = self._small(repo, layer)
            elif mt == MT_SYSTEM:
                m.system = self._small(repo, layer)
            elif mt == MT_PARAMS:
                m.params = json.loads(self._small(repo, layer))
        return m

    def gguf_header(self, repo: str, m: OllamaModel) -> tuple[GGUFHeader, int]:
        """Header plus the number of bytes it took to read it."""
        url = self.blob_url(repo, m.model_digest)
        src = RangedSource(lambda s, e: self.f.get(url, rng=(s, e)))
        return read_header(src), src.bytes_read


def ollama_library(fetcher: Fetcher) -> Registry:
    return Registry(fetcher, "https://registry.ollama.ai")


def huggingface(fetcher: Fetcher) -> Registry:
    return Registry(fetcher, "https://hf.co")


def library_ref(name: str) -> tuple[str, str, str]:
    """'qwen2.5:7b-instruct' -> ('library/qwen2.5', '7b-instruct', 'qwen2.5:7b-instruct')."""
    model, _, tag = name.partition(":")
    tag = tag or "latest"
    repo = model if "/" in model else f"library/{model}"
    return repo, tag, f"{model}:{tag}"


def hf_ref(name: str) -> tuple[str, str, str]:
    """'bartowski/Qwen2.5-7B-Instruct-GGUF:Q4_K_M' -> (repo, quant, 'hf.co/...:Q4_K_M')."""
    repo, _, quant = name.removeprefix("hf.co/").partition(":")
    quant = quant or "latest"
    return repo, quant, f"hf.co/{repo}:{quant}"
