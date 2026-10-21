"""Read-only view of a local Ollama model store (manifests + blobs).

Layout: <models>/manifests/<registry>/<namespace>/<model>/<tag> holds an OCI-style
manifest; every layer and the config live in <models>/blobs/sha256-<hex>.
Nothing here writes to the store.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from tda.gguf import GGUFHeader, read_header_file

MT_MODEL = "application/vnd.ollama.image.model"
MT_TEMPLATE = "application/vnd.ollama.image.template"
MT_SYSTEM = "application/vnd.ollama.image.system"
MT_PARAMS = "application/vnd.ollama.image.params"
MT_ADAPTER = "application/vnd.ollama.image.adapter"
MT_PROJECTOR = "application/vnd.ollama.image.projector"


def default_models_dir() -> Path:
    env = os.environ.get("OLLAMA_MODELS")
    return Path(env) if env else Path.home() / ".ollama" / "models"


@dataclass
class OllamaModel:
    """One manifest and the small layers that shape the prompt."""

    name: str  # e.g. registry.ollama.ai/library/qwen2.5:7b-instruct
    manifest: dict
    config: dict
    template: str | None = None
    system: str | None = None
    params: dict | None = None
    model_digest: str | None = None
    layer_digests: dict[str, str] = field(default_factory=dict)

    @property
    def short_name(self) -> str:
        reg_ns_model, tag = self.name.rsplit(":", 1)
        parts = reg_ns_model.split("/")
        if parts[0] == "registry.ollama.ai" and parts[1] == "library":
            return f"{parts[2]}:{tag}"
        return self.name

    @property
    def renderer(self) -> str:
        return self.config.get("renderer", "")

    @property
    def parser(self) -> str:
        return self.config.get("parser", "")


class LocalStore:
    def __init__(self, models_dir: Path | None = None):
        self.root = Path(models_dir) if models_dir else default_models_dir()

    def blob_path(self, digest: str) -> Path:
        return self.root / "blobs" / digest.replace(":", "-")

    def _read_blob_text(self, digest: str) -> str:
        return self.blob_path(digest).read_text(encoding="utf-8")

    def manifests(self) -> list[Path]:
        base = self.root / "manifests"
        return sorted(p for p in base.rglob("*") if p.is_file()) if base.exists() else []

    def name_for(self, manifest_path: Path) -> str:
        rel = manifest_path.relative_to(self.root / "manifests").parts
        return "/".join(rel[:-1]) + ":" + rel[-1]

    def load(self, manifest_path: Path) -> OllamaModel:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        config = json.loads(self._read_blob_text(manifest["config"]["digest"]))
        m = OllamaModel(self.name_for(manifest_path), manifest, config)
        for layer in manifest.get("layers", []):
            mt, digest = layer["mediaType"], layer["digest"]
            m.layer_digests.setdefault(mt, digest)
            if mt == MT_MODEL and m.model_digest is None:
                m.model_digest = digest  # first model layer is the weights; later ones are shards
            elif mt == MT_TEMPLATE:
                m.template = self._read_blob_text(digest)
            elif mt == MT_SYSTEM:
                m.system = self._read_blob_text(digest)
            elif mt == MT_PARAMS:
                m.params = json.loads(self._read_blob_text(digest))
        return m

    def models(self) -> list[OllamaModel]:
        return [self.load(p) for p in self.manifests()]

    def gguf_header(self, m: OllamaModel) -> GGUFHeader | None:
        if not m.model_digest:
            return None
        return read_header_file(str(self.blob_path(m.model_digest)))
