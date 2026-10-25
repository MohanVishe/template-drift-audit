"""Frozen H3 settings: one spec per model, plus the options every arm shares.

Changing anything here after a model's first full run invalidates that run. The upstream pins and
model digests are the ones P2 audited (runs/p2-library/models/<name>_latest.json); a run refuses to
start if the registry copy differs.
"""

from __future__ import annotations

from dataclasses import dataclass

# Same for every model and arm (notes/H3-SPIKE.md). num_ctx is checked per model at run start:
# the loaded model must sit fully in VRAM (size_vram == size), or the run stops.
OPTIONS = {"temperature": 0, "seed": 42, "num_ctx": 16384, "num_predict": 1024}
SERVER = "serve-h3"  # scripts/live_setup.sh: RAM prompt cache off; every step must show 0 cached tokens


@dataclass(frozen=True)
class Spec:
    p2: str  # runs/p2-library/models/<p2>.json
    package: str  # as audited in P2
    serve_as: str  # name in the isolated store
    parser: str  # key into bfcl.PARSERS
    upstream_repo: str
    upstream_sha: str
    model_digest: str  # sha256 prefix of the model layer
    one_call_per_message: bool = False
    think: bool | None = None
    optional: bool = False


MODELS: dict[str, Spec] = {s.serve_as: s for s in (
    Spec("qwen2.5_latest", "qwen2.5:latest", "qwen2.5:7b-instruct", "hermes",
         "Qwen/Qwen2.5-7B-Instruct", "a09a35458c702b33eeacc393d103063234e8bc28", "2bada8a74506"),
    Spec("qwen2.5-coder_latest", "qwen2.5-coder:latest", "qwen2.5-coder:7b", "hermes",
         "Qwen/Qwen2.5-Coder-7B-Instruct", "c03e6d358207e414f1eca0bb1891e29f1db0e242", "60e05f210007"),
    # Thinking off in both layouts: Ollama's think=false and the maker's enable_thinking=False.
    Spec("qwen3_latest", "qwen3:latest", "qwen3:8b", "hermes",
         "Qwen/Qwen3-8B", "b968826d9c46dd6066d109eabc6255188de91218", "a3de86cd1c13", think=False),
    # Llama 3.1's own template refuses an assistant message with more than one call.
    Spec("llama3.1_latest", "llama3.1:latest", "llama3.1:8b", "llama_json",
         "meta-llama/Llama-3.1-8B-Instruct", "0e9e39f249a16976918f6564b8830bc894c89659", "667b0c1932bc",
         one_call_per_message=True),
    Spec("mistral_latest", "mistral:latest", "mistral:7b", "mistral",
         "mistralai/Mistral-7B-Instruct-v0.3", "c170c708c41dac9275d15a8fff4eca08d52bab71", "f5074b1221da"),
    # Optional: Ollama renders it with a built-in renderer, which the harness does not reproduce yet.
    Spec("qwen3.5_latest", "qwen3.5:latest", "qwen3.5:9b", "hermes",
         "Qwen/Qwen3.5-9B", "c202236235762e1c871ad0ccb60c8ee5ba337b9a", "02d45dc1cf45", think=False,
         optional=True),
)}
