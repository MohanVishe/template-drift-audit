import hashlib
import json

import pytest

from tda.sources.ollama_store import MT_MODEL, MT_SYSTEM, MT_TEMPLATE, LocalStore, default_models_dir
from tests.test_gguf import TEMPLATE, sample


def _blob(root, data: bytes) -> str:
    digest = "sha256:" + hashlib.sha256(data).hexdigest()
    (root / "blobs" / digest.replace(":", "-")).write_bytes(data)
    return digest


@pytest.fixture
def store(tmp_path):
    (tmp_path / "blobs").mkdir()
    cfg = _blob(tmp_path, json.dumps({"model_family": "tiny", "renderer": "qwen3.5"}).encode())
    model = _blob(tmp_path, sample())
    tmpl = _blob(tmp_path, b"{{ .Prompt }}")
    system = _blob(tmp_path, b"Be brief.")
    manifest = {"config": {"digest": cfg}, "layers": [
        {"mediaType": MT_MODEL, "digest": model},
        {"mediaType": MT_TEMPLATE, "digest": tmpl},
        {"mediaType": MT_SYSTEM, "digest": system},
    ]}
    path = tmp_path / "manifests" / "registry.ollama.ai" / "library" / "tiny" / "1b"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(manifest))
    return LocalStore(tmp_path)


def test_loads_manifest_layers_and_gguf(store):
    (m,) = store.models()
    assert m.short_name == "tiny:1b"
    assert m.template == "{{ .Prompt }}"
    assert m.system == "Be brief."
    assert m.renderer == "qwen3.5" and m.parser == ""
    assert store.gguf_header(m).chat_template == TEMPLATE


@pytest.mark.skipif(not (default_models_dir() / "manifests").exists(), reason="no local Ollama store")
def test_real_local_store_reads():
    store = LocalStore()
    for m in store.models():
        h = store.gguf_header(m)
        assert h is not None and h.version in (2, 3)
