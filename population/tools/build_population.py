"""Build the study population and the hand-checked L0 mapping from the dated snapshots.

Reads:  population/snapshots/ (library page, tags pages, HF GGUF list)
Fetches (cached in .cache-population, 1 request/second): huggingface.co/api/models/<repo>/revision/main
Writes: population/library_top50.csv, population/hf_top30.csv, population/mapping.yaml

The mapping itself (which upstream repo, how sure, and why) is written by hand below; the script only
pins shas, finds the template file and adds the evidence it can check from metadata.

Usage: python -I -X utf8 population/tools/build_population.py [--offline]
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
POP = HERE.parent
ROOT = POP.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import hfinfo as h  # noqa: E402
import parse_library  # noqa: E402
import parse_tags  # noqa: E402
from tda.http import Fetcher  # noqa: E402

DATE = "2026-10-22"
SNAP = POP / "snapshots"
LIBRARY_HTML = SNAP / f"ollama-library-popular-{DATE}.html"
TAGS_DIR = SNAP / f"ollama-tags-{DATE}"
HF_JSON = SNAP / f"hf-gguf-by-downloads-{DATE}.json"

# Hugging Face pipeline tags that are not text chat models.
HF_NONCHAT_PIPELINES = {
    "object-detection", "text-to-speech", "automatic-speech-recognition", "text-to-image", "image-text-to-video",
    "image-to-video", "image-to-image", "text-to-audio", "audio-text-to-text", "feature-extraction",
}
# Repos the pipeline tag lets through but that are not chat models (read from their GGUF metadata and card).
HF_NONCHAT_REPOS = {
    "Serveurperso/YuE2-GGUF": "music generation (GGUF architecture mert2, no chat template)",
    "Serveurperso/ACE-Step-1.5-GGUF": "music generation (architecture acestep-lm, no chat template)",
    "DeepBeepMeep/Wan2.1": "video-generation bundle; its GGUF is a text encoder, not a chat package",
    "DeepBeepMeep/MiniMax-H3": "video-generation bundle; its GGUF is a text encoder, not a chat package",
    "DeepBeepMeep/LTX-2": "video generation (architecture ltxv)",
    "Serveurperso/MiniMax-Music3-GGUF": "music generation (architecture mm3-cond)",
    "datalab-to/surya-ocr-2-gguf": "OCR model, not a chat model",
}
# Nearest quant set by hand where the file names use no standard label.
HF_QUANT_OVERRIDE = {
    "antirez/deepseek-v4.1-flash-gguf": ("MXFP4", "DeepSeek-V4.1-Flash-1017-MXFP4-experts-00001-of-00009.gguf",
                                         "4-bit MXFP4 experts; the only other files are 2-bit"),
    "mudler/Laguna-XS-2.1-APEX-GGUF": ("APEX-Balanced", "Laguna-XS-2.1-APEX-Balanced.gguf",
                                       "APEX mixed-precision quants only; Balanced is the middle tier"),
    "antirez/deepseek-v4-gguf": ("Q4K-experts", "DeepSeek-V4-Flash-Q4KExperts-F16HC-F16Compressor-F16Indexer-Q8Attn-Q8Shared-Q8Out-chat-v2-imatrix-0731.gguf",
                                 "mixed per-layer quants; Q4_K experts (newest 0731 build) is nearest to Q4_K_M"),
}
HF_QUANT_NOTE = {
    "prism-ml/Ternary-Bonsai-2-27B-gguf": "ternary/2-bit quants only (PQ2_0, PTQ1_0) plus F16; PQ2_0 chosen",
    "cdiamond/Qwen3.8-27B-iMatrix-NVFP4-MTP-GGUF": "single NVFP4 file with a bundled MTP head",
    "ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF": "GSQ-RCO 2- and 3-bit quants only; IQ3_S is the largest",
    "ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF": "GSQ-RCO 2- and 3-bit quants only; IQ3_S is the largest",
    "ukisai/Swift-1.5-Qwen3.8-27B-GSQ-RCO-GGUF": "GSQ-RCO 2- and 3-bit quants only; IQ3_S is the largest",
    "SC117/Qwen3.8-Flash-Next-GSQ-RCO-abliterated-GGUF": "GSQ-RCO 2- and 3-bit quants only; IQ3_S is the largest",
    "peculiar-ragdoll/Tiel-Coder-35B-A3B-GGUF-MTP": "every file bundles an MTP head; no Q4_K_M",
    "HauhauCS/Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-MTP-GGUF": "uses its own K_P quant names; no Q4_K_M",
    "byteshape/Qwen3.8-27B-GGUF": "IQ quants only; IQ4_XS is the largest",
    "antirez/deepseek-v4.1-flash-gguf": "custom architecture deepseek41 for antirez's own engine; may not load in Ollama",
    "antirez/deepseek-v4-gguf": "custom architecture deepseek4 for antirez's own engine",
}

# ---------------------------------------------------------------------------------------------
# Hand mapping. Each entry: upstream repo (None when excluded), confidence, reason, and for
# exclusions an optional candidate repo the package's own metadata points at.
# ---------------------------------------------------------------------------------------------

LIB = {
    "llama3.1": ("meta-llama/Llama-3.1-8B-Instruct", "high", "latest = 8b-instruct-q4_K_M; Meta's own 8B Instruct repo."),
    "deepseek-r1": ("deepseek-ai/DeepSeek-R1-0528-Qwen3-8B", "high", "latest = 8b-0528-qwen3-q4_K_M, DeepSeek's R1-0528 distill into Qwen3-8B, so DeepSeek's repo for it, not Qwen's."),
    "llama3.2": ("meta-llama/Llama-3.2-3B-Instruct", "high", "latest = 3b-instruct-q4_K_M."),
    "qwen2.5": ("Qwen/Qwen2.5-7B-Instruct", "high", "latest = 7b-instruct-q4_K_M; the same repo P0 used (GGUF base_model metadata points at the base Qwen2.5-7B instead)."),
    "gemma3": ("google/gemma-3-4b-it", "high", "latest = 4b-it-q4_K_M."),
    "qwen3": ("Qwen/Qwen3-8B", "high", "latest = 8b-q4_K_M. Qwen3-8B is the post-trained hybrid-thinking model (base is Qwen3-8B-Base); no 2507 Instruct exists at 8B."),
    "gemma2": ("google/gemma-2-9b-it", "high", "latest = 9b-instruct-q4_0."),
    "mistral": ("mistralai/Mistral-7B-Instruct-v0.3", "high", "latest = 7b-instruct-v0.3-q4_K_M."),
    "gemma4": ("google/gemma-4-E4B-it", "medium", "latest = e4b, which shares its digest with no -it-q4_K_M or -it-qat tag, so the exact build is not visible from the tags page. Google's E4B instruct repo is the only E4B chat model; google/gemma-4-E4B-it-qat-q4_0-unquantized is the alternative if latest is the QAT build."),
    "llama3": ("meta-llama/Meta-Llama-3-8B-Instruct", "high", "latest = 8b-instruct-q4_0."),
    "qwen3.5": ("Qwen/Qwen3.5-9B", "high", "latest = 9b. Qwen/Qwen3.5-9B is the post-trained model (its card's base is Qwen3.5-9B-Base)."),
    "qwen2.5-coder": ("Qwen/Qwen2.5-Coder-7B-Instruct", "high", "latest = 7b-instruct-q4_K_M."),
    "phi3": ("microsoft/Phi-3-mini-128k-instruct", "medium", "latest = 3.8b-mini-128k-instruct-q4_0 (not the 4k variant). Microsoft has revised this repo since the package was built (last modified 2025-12-10), so the template at main may be newer than the GGUF's."),
    "llava": ("liuhaotian/llava-v1.6-mistral-7b", "low", "latest = 7b-v1.6-mistral-q4_0. The author repo's tokenizer_config.json carries the Mistral-Instruct template inherited from the base tokenizer; LLaVA's actual prompt format is defined in the LLaVA code (conv mode mistral_instruct) and the template has no image placeholder. Alternative: llava-hf/llava-v1.6-mistral-7b-hf, Hugging Face's transformers port, which has a processor chat template but is not the author's."),
    "gpt-oss": ("openai/gpt-oss-20b", "high", "latest = 20b."),
    "qwen3-coder": ("Qwen/Qwen3-Coder-30B-A3B-Instruct", "high", "latest = 30b-a3b-q4_K_M."),
    "glm-ocr": ("zai-org/GLM-OCR", "high", "latest = bf16; Z.ai's only GLM-OCR repo. An OCR model, kept because the population rule excludes embedding models only."),
    "gemma": ("google/gemma-1.1-7b-it", "high", "latest = 7b-instruct-v1.1-q4_0, so Gemma 1.1, not the original gemma-7b-it."),
    "qwen": ("Qwen/Qwen1.5-4B-Chat", "high", "latest = 4b-chat-v1.5-q4_0."),
    "phi4": ("microsoft/phi-4", "high", "latest = 14b-q4_K_M. Repo last modified 2026-07-14, after the package (2025-01-08)."),
    "llama2": ("meta-llama/Llama-2-7b-chat-hf", "high", "latest = 7b-chat-q4_0; the transformers-format chat repo."),
    "codellama": ("codellama/CodeLlama-7b-Instruct-hf", "medium", "latest = 7b-instruct-q4_0. Meta publishes this model in two orgs: codellama/ (the original transformers release, ungated) and meta-llama/CodeLlama-7b-Instruct-hf (gated); codellama/ chosen as the original."),
    "qwen3.6": ("Qwen/Qwen3.6-35B-A3B", "high", "latest = 35b-a3b (not 27b)."),
    "qwen3-vl": ("Qwen/Qwen3-VL-8B-Thinking", "high", "latest = 8b-thinking-q4_K_M, so the Thinking repo, not 8B-Instruct."),
    "qwen2": ("Qwen/Qwen2-7B-Instruct", "high", "latest = 7b-instruct-q4_0."),
    "tinyllama": ("TinyLlama/TinyLlama-1.1B-Chat-v1.0", "high", "latest = 1.1b-chat-v1-q4_0."),
    "mistral-nemo": ("mistralai/Mistral-Nemo-Instruct-2407", "high", "latest = 12b-instruct-2407-q4_0."),
    "minicpm-v": ("openbmb/MiniCPM-V-2_6", "high", "latest = 8b-2.6-q4_0."),
    "llama3.2-vision": ("meta-llama/Llama-3.2-11B-Vision-Instruct", "high", "latest = 11b-instruct-q4_K_M."),
    "qwen2.5vl": ("Qwen/Qwen2.5-VL-7B-Instruct", "high", "latest = 7b-q4_K_M."),
    "deepseek-coder": ("deepseek-ai/deepseek-coder-1.3b-instruct", "high", "latest = 1.3b-instruct-q4_0."),
    "qwen3.8": ("Qwen/Qwen3.8-27B", "high", "latest = 27b; the only Qwen3.8 size in the library."),
    "llama3.3": ("meta-llama/Llama-3.3-70B-Instruct", "high", "latest = 70b-instruct-q4_K_M."),
    "dolphin3": ("dphn/Dolphin3.0-Llama3.1-8B", "high", "latest = 8b-llama3.1-q4_K_M. cognitivecomputations/Dolphin3.0-Llama3.1-8B now redirects to dphn/."),
    "smollm2": ("HuggingFaceTB/SmolLM2-1.7B-Instruct", "high", "latest = 1.7b-instruct-q8_0."),
    "deepseek-v3": ("deepseek-ai/DeepSeek-V3", "medium", "latest = 671b-q4_K_M. Package last updated 2025-01-13, before DeepSeek-V3-0324 existed, so the original V3 repo; that repo was itself modified on 2025-03-27, after the package."),
    "olmo2": ("allenai/OLMo-2-1124-7B-Instruct", "high", "latest = 7b-1124-instruct-q4_K_M."),
    "codegemma": ("google/codegemma-1.1-7b-it", "high", "latest = 7b-instruct-v1.1-q4_0, so CodeGemma 1.1."),
    "deepseek-coder-v2": ("deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct", "high", "latest = 16b-lite-instruct-q4_0."),
    "mistral-small": ("mistralai/Mistral-Small-24B-Instruct-2501", "high", "latest = 24b-instruct-2501-q4_K_M."),
    "orca-mini": (None, "high", "latest = 3b-q4_0, from pankajmathur/orca_mini_3b. That repo has no chat template; its prompt format is given only as prose in the model card.", "pankajmathur/orca_mini_3b"),
    "granite3.1-moe": ("ibm-granite/granite-3.1-3b-a800m-instruct", "high", "latest = 3b-instruct-q4_K_M."),
    "starcoder2": (None, "high", "latest = 3b-q4_0, the base completion model bigcode/starcoder2-3b, which has no chat template (starcoder2:instruct is a separate, non-default tag).", "bigcode/starcoder2-3b"),
    "nemotron-3-super": ("nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16", "medium", "latest = 120b-a12b-q4_K_M. NVIDIA publishes this model only as precision-suffixed repos (no unsuffixed repo exists); BF16 is the full-precision one. The other precision repos were not checked."),
    "mixtral": ("mistralai/Mixtral-8x7B-Instruct-v0.1", "high", "latest = 8x7b-instruct-v0.1-q4_0."),
    "llama2-uncensored": (None, "high", "latest = 7b-chat-q4_0, from georgesung/llama2_7b_chat_uncensored, which has no chat template.", "georgesung/llama2_7b_chat_uncensored"),
    "translategemma": ("google/translategemma-4b-it", "high", "latest = 4b-it-q4_K_M."),
    "falcon3": ("tiiuae/Falcon3-7B-Instruct", "high", "latest = 7b-instruct-q4_K_M."),
    "mistral-small3.2": (None, "high", "latest = 24b-instruct-2506-q4_K_M. Mistral's repo ships tekken.json, params.json and SYSTEM_PROMPT.txt for mistral-common and no Jinja chat template.", "mistralai/Mistral-Small-3.2-24B-Instruct-2506"),
    "minimax-m2.7": (None, "high", "Cloud-only in Ollama: the tags page lists only `cloud`, so there is no local package (no GGUF, Go template or selection) to audit. The author repo does have chat_template.jinja.", "MiniMaxAI/MiniMax-M2.7"),
}

HF_MAP = {
    "ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF": ("Qwen/Qwen3.8-Flash-Next", "high", "Pure quantisation (card: base_model_relation quantized) of Qwen's post-trained Flash-Next."),
    "unsloth/Qwen3.8-27B-GGUF": ("Qwen/Qwen3.8-27B", "high", "Quantisation of Qwen3.8-27B (card base_model). unsloth is known to patch templates, so L1 may differ from L0 by design."),
    "ornith-ai/Ornith-1.5-9B-GGUF": ("ornith-ai/Ornith-1.5-9B", "medium", "Same author, same name; the card sets no base_model. The repo holds two different templates: chat_template.jinja (7593 chars, the file transformers loads first) and a chat_template key in tokenizer_config.json (7756 chars); the GGUF embeds a third (7828 chars). chat_template.jinja is taken as L0, per transformers' load order."),
    "ornith-ai/Ornith-1.5-35B-A3B-GGUF": ("ornith-ai/Ornith-1.5-35B-A3B", "medium", "Same author, same name; the card sets no base_model. The repo holds two different templates: chat_template.jinja (7536 chars, the file transformers loads first) and a chat_template key in tokenizer_config.json (7764 chars); the GGUF embeds a third (7828 chars). chat_template.jinja is taken as L0, per transformers' load order."),
    "prism-ml/Ternary-Bonsai-2-27B-gguf": ("Qwen/Qwen3.8-27B", "medium", "The card lists Qwen/Qwen3.8-27B as the quantized base and prism-ml publishes no unquantised Bonsai repo (prism-ml/Ternary-Bonsai-2-27B does not exist). Ternary conversion may involve retraining, so Qwen is the template author only if prism-ml kept the template."),
    "JonathanColetti/Qwen3.8-27B-Uncensored-GGUF": ("JonathanColetti/Qwen3.8-27B-Uncensored", "medium", "Same author's fine-tune repo (its card: finetune of Qwen3.8-27B). The GGUF repo's card points straight at Qwen/Qwen3.8-27B, skipping the fine-tune, the same base-model quirk P0 found."),
    "CMSManhattan/JiRackUltra_1b": ("CMSManhattan/JiRackUltra_1b", "medium", "The author's own repo holds both the GGUF files and the transformers files (chat_template.jinja, tokenizer_config.json), so L0 and L1 come from the same repo. It also carries chat_template.jinja.bak and a _with_thinking variant; the default chat_template.jinja is used."),
    "huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF": ("huihui-ai/Huihui-Qwen3.8-27B-abliterated", "high", "Same author's safetensors repo with the same name. The GGUF card points at Qwen/Qwen3.8-27B, skipping the abliterated model."),
    "ornith-ai/Ornith-1.0-9B-GGUF": ("ornith-ai/Ornith-1.0-9B", "high", "Same author, same name."),
    "HauhauCS/Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-MTP-GGUF": (None, "medium", "A weight-edited (uncensored) Qwen3.8-27B published only as GGUF: HauhauCS has no safetensors repo for it, so there is no author template outside the GGUF. If re-included, the candidate L0 is Qwen/Qwen3.8-27B (the card's base).", "Qwen/Qwen3.8-27B"),
    "cdiamond/Qwen3.8-27B-iMatrix-NVFP4-MTP-GGUF": ("Qwen/Qwen3.8-27B", "high", "Pure quantisation (card: quantized from Qwen/Qwen3.8-27B; name says iMatrix NVFP4, no fine-tune)."),
    "ggml-org/Qwen3.8-27B-GGUF": ("Qwen/Qwen3.8-27B", "high", "llama.cpp project's reference quantisation of Qwen3.8-27B."),
    "SC117/Qwen3.8-Flash-Next-GSQ-RCO-abliterated-GGUF": (None, "medium", "An abliterated (weight-edited, 'tensor-transplant') build made from another GGUF repo and published only as GGUF; there is no author template outside the GGUF. If re-included, the candidate L0 is Qwen/Qwen3.8-Flash-Next.", "Qwen/Qwen3.8-Flash-Next"),
    "byteshape/Qwen3.8-27B-GGUF": ("Qwen/Qwen3.8-27B", "high", "Quantisation of Qwen3.8-27B (card base_model)."),
    "peculiar-ragdoll/Tiel-Coder-35B-A3B-GGUF-MTP": ("ornith-ai/Ornith-1.5-35B-A3B", "low", "The card says quantized from ornith-ai/Ornith-1.5-35B-A3B, but the package has its own name ('Tiel-Coder', 'token-efficient agentic coding') and no Tiel-Coder safetensors repo exists, so it may be a modified model. If it is a pure quant, Ornith is the template author."),
    "DavidAU/Qwen3.5-9B-The-Defiant-Fable-Uncensored-Heretic-NEO-IMATRIX-MAX-MTP-GGUF": ("DavidAU/Qwen3.5-9B-The-Defiant-Fable-Uncensored-Heretic-NEO-IMATRIX-MAX-MTP", "high", "The GGUF card's base_model is the same author's safetensors repo with the same name."),
    "mradermacher/Ornith-1.5-9B-uncensored-GGUF": ("junafinity/Ornith-1.5-9B-uncensored", "high", "mradermacher quantises other people's models; the card's base_model is junafinity's fine-tune, whose own card points at ornith-ai/Ornith-1.5-9B."),
    "DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF": ("DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NM-DAU", "medium", "The GGUF card's base_model is this same-author safetensors repo, but its name differs ('NM-DAU' vs 'NEO-CODER-MAX-MTP'), so the GGUF may be a further variant."),
    "mudler/Laguna-XS-2.1-APEX-GGUF": ("poolside/Laguna-XS-2.1", "high", "Pure quantisation (card base_model poolside/Laguna-XS-2.1)."),
    "unsloth/gemma-4-12b-it-GGUF": ("google/gemma-4-12B-it", "high", "Quantisation of Google's 12B instruct model (card base_model)."),
    "ornith-ai/Ornith-1.0-35B-GGUF": ("ornith-ai/Ornith-1.0-35B", "high", "Same author, same name."),
    "antirez/deepseek-v4.1-flash-gguf": ("deepseek-ai/DeepSeek-V4.1-Flash", "high", "Quantisation of DeepSeek-V4.1-Flash (card base_model). DeepSeek ships chat_template.jinja for V4.1, unlike V4."),
    "peculiar-ragdoll/Dirk-Qwen3.8-27B-GGUF": ("Qwen/Qwen3.8-27B", "low", "The card says quantized from Qwen/Qwen3.8-27B, but the package has its own name ('Dirk', 'token-efficient agentic coding') and no Dirk safetensors repo exists, so it may be a modified model. If it is a pure quant, Qwen is the template author."),
    "unsloth/Qwen3.5-9B-GGUF": ("Qwen/Qwen3.5-9B", "high", "Quantisation of Qwen3.5-9B (card base_model)."),
    "ukisai/Swift-1.5-Qwen3.8-27B-GSQ-RCO-GGUF": ("ukisai/Swift-1.5-Qwen3.8-27b", "high", "Same author's fine-tune repo (card base_model; that repo's card: finetune of Qwen3.8-27B)."),
    "ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF": ("Qwen/Qwen3.8-27B", "high", "Pure quantisation (card base_model Qwen/Qwen3.8-27B)."),
    "unsloth/Qwen3.5-4B-GGUF": ("Qwen/Qwen3.5-4B", "high", "Quantisation of Qwen3.5-4B (card base_model)."),
    "unsloth/Qwen3.6-35B-A3B-GGUF": ("Qwen/Qwen3.6-35B-A3B", "high", "Quantisation of Qwen3.6-35B-A3B (card base_model)."),
    "antirez/deepseek-v4-gguf": (None, "high", "deepseek-ai/DeepSeek-V4-Flash publishes its prompt format as Python (encoding/encoding_dsv4.py with test vectors), not as a Jinja chat template, so there is no author template to render. The chat template inside the GGUF was written by the quantiser.", "deepseek-ai/DeepSeek-V4-Flash"),
    "ornith-ai/Ornith-1.5-397B-GGUF": ("ornith-ai/Ornith-1.5-397B", "medium", "Same author, same name. The repo holds two different templates: chat_template.jinja (7594 chars, the file transformers loads first) and a chat_template key in tokenizer_config.json (7756 chars); the GGUF embeds a third (7828 chars). chat_template.jinja is taken as L0, per transformers' load order."),
}


def write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def yaml_scalar(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    return json.dumps(v, ensure_ascii=False)  # a JSON string is a valid YAML double-quoted scalar


def upstream_fields(f: Fetcher, repo: str | None) -> dict:
    if repo is None:
        return {"upstream_sha": None, "template_file": None, "gated": None, "upstream_last_modified": None}
    info = h.revision(f, repo)
    if info is None:
        raise SystemExit(f"mapped upstream repo not found: {repo}")
    if info["id"] != repo:
        raise SystemExit(f"{repo} redirects to {info['id']}; map the canonical id")
    tf = h.template_file(info)
    if tf is None:
        raise SystemExit(f"{repo} has no chat template; it must be an exclusion")
    return {"upstream_sha": info["sha"], "template_file": tf, "gated": info.get("gated") or False,
            "upstream_last_modified": info.get("lastModified")}


def library(f: Fetcher) -> tuple[list[dict], list[dict], list[dict]]:
    rows = parse_library.parse(LIBRARY_HTML.read_text(encoding="utf-8"))
    embedding = [r for r in rows if "embedding" in r["capabilities"]]
    chat = [r for r in rows if "embedding" not in r["capabilities"]][:50]
    last_rank = chat[-1]["rank"]
    csv_rows, mapping = [], []
    for i, r in enumerate(chat, 1):
        t = parse_tags.parse((TAGS_DIR / f"{r['name']}.html").read_text(encoding="utf-8"))
        latest = t["latest"] or {}
        quant_tag = max(t["aliases_of_latest"], key=len) if t["aliases_of_latest"] else ""
        cloud_only = not t["latest"] and all("cloud" in x["tag"] for x in t["tags"])
        csv_rows.append({
            "chat_rank": i, "page_rank": r["rank"], "name": r["name"], "pulls": r["pulls"],
            "pulls_display": r["pulls_display"], "capabilities": ";".join(r["capabilities"]),
            "sizes": ";".join(r["sizes"]), "default_tag": "" if cloud_only else "latest",
            "latest_size_tag": parse_tags.best_alias(t["aliases_of_latest"]), "latest_full_tag": quant_tag,
            "latest_digest": latest.get("digest") or "", "latest_download_size": latest.get("size", ""),
            "input": latest.get("input", ""), "cloud_only": cloud_only, "tag_count": r["tag_count"],
            "updated": r["updated"], "description": r["description"],
        })
        entry = LIB[r["name"]]
        repo, conf, reason = entry[:3]
        row = {"package": f"{r['name']}:latest" if not cloud_only else f"{r['name']}:cloud",
               "source": "ollama-library", "rank": i, "status": "included" if repo else "excluded",
               "upstream_repo": repo, **upstream_fields(f, repo), "confidence": conf, "reason": reason}
        if not repo and len(entry) > 3:
            row["candidate_repo"] = entry[3]
        mapping.append(row)
    assert set(LIB) == {r["name"] for r in chat}, "hand mapping and population differ"
    excluded_pop = [{"page_rank": r["rank"], "name": r["name"], "why": "embedding-only"}
                    for r in embedding if r["rank"] <= last_rank]
    return csv_rows, mapping, excluded_pop


def hf(f: Fetcher) -> tuple[list[dict], list[dict], list[dict]]:
    top = json.loads(HF_JSON.read_bytes())
    csv_rows, mapping, skipped = [], [], []
    for dl_rank, x in enumerate(top, 1):
        if len(csv_rows) == 30:
            break
        repo = x["id"]
        if x.get("pipeline_tag") in HF_NONCHAT_PIPELINES:
            skipped.append({"download_rank": dl_rank, "repo": repo, "why": f"pipeline {x['pipeline_tag']}"})
            continue
        if repo in HF_NONCHAT_REPOS:
            skipped.append({"download_rank": dl_rank, "repo": repo, "why": HF_NONCHAT_REPOS[repo]})
            continue
        info = h.revision(f, repo)
        g = info.get("gguf") or {}
        quant, qfile = h.pick_quant(info)
        note = HF_QUANT_NOTE.get(repo, "")
        if repo in HF_QUANT_OVERRIDE:
            quant, qfile, note = HF_QUANT_OVERRIDE[repo][0], HF_QUANT_OVERRIDE[repo][1], HF_QUANT_OVERRIDE[repo][2] + (f"; {note}" if note else "")
        i = len(csv_rows) + 1
        csv_rows.append({
            "chat_rank": i, "download_rank": dl_rank, "repo": repo, "downloads": x.get("downloads"),
            "likes": x.get("likes"), "pipeline_tag": x.get("pipeline_tag") or "", "gguf_architecture": g.get("architecture", ""),
            "quant": quant or "", "quant_file": qfile or "", "quant_note": note,
            "card_base_model": ";".join(h.base_models(info)), "hub_base_relations": ";".join(h.base_relations(info)),
            "gguf_template_chars": len(g.get("chat_template") or ""), "repo_sha": info["sha"],
            "created_at": x.get("createdAt", ""),
        })
        entry = HF_MAP[repo]
        up, conf, reason = entry[:3]
        fields = upstream_fields(f, up)
        row = {"package": f"hf.co/{repo}:{quant}" if quant else f"hf.co/{repo}", "source": "hf", "rank": i,
               "status": "included" if up else "excluded", "upstream_repo": up, **fields,
               "confidence": conf, "reason": reason}
        if not up and len(entry) > 3:
            row["candidate_repo"] = entry[3]
        row["evidence"] = template_evidence(f, g.get("chat_template"), up or (entry[3] if len(entry) > 3 else None))
        mapping.append(row)
    assert set(HF_MAP) == {r["repo"] for r in csv_rows}, "hand mapping and population differ"
    return csv_rows, mapping, skipped


def template_evidence(f: Fetcher, embedded: str | None, repo: str | None) -> str:
    """Compare the GGUF's embedded template (as the hub parsed it from one file) with the repo's at main."""
    if repo is None:
        return ""
    up = h.template_text(h.revision(f, repo))
    if not embedded:
        return "hub reports no embedded chat template for this GGUF repo"
    if up is None:
        return f"{repo} has no Jinja template to compare"
    if embedded == up:
        return "embedded GGUF template is byte-identical to the upstream template at main"
    if embedded.strip() == up.strip():
        return "embedded GGUF template equals the upstream template at main up to leading/trailing whitespace"
    return f"embedded GGUF template differs from the upstream template at main ({len(embedded)} vs {len(up)} chars)"


def write_mapping(path: Path, rows: list[dict]) -> None:
    keys = ["package", "source", "rank", "status", "upstream_repo", "upstream_sha", "template_file", "gated",
            "upstream_last_modified", "confidence", "reason", "candidate_repo", "evidence"]
    lines = [
        f"# L0 mapping for the template-drift-audit study population, snapshot {DATE}.",
        "# One entry per package: the model author's own repo, pinned to its commit at main on the snapshot date,",
        "# and the file transformers would load the chat template from. Written by hand; see README.md for the rules.",
        "# status: excluded rows have no upstream_repo; candidate_repo (if any) is what the package's own metadata points at.",
        "# evidence (HF packages only): the GGUF's embedded template, as the hub parsed it, compared with upstream main.",
        "packages:",
    ]
    for r in rows:
        first = True
        for k in keys:
            if k not in r or (k in ("candidate_repo", "evidence") and not r[k]):
                continue
            lines.append(f"  {'- ' if first else '  '}{k}: {yaml_scalar(r[k])}")
            first = False
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    f = Fetcher(ROOT / ".cache-population", offline="--offline" in sys.argv)
    lib_rows, lib_map, lib_skipped = library(f)
    hf_rows, hf_map, hf_skipped = hf(f)
    write_csv(POP / "library_top50.csv", lib_rows)
    write_csv(POP / "hf_top30.csv", hf_rows)
    write_mapping(POP / "mapping.yaml", lib_map + hf_map)
    summary = {
        "library": {"chat": len(lib_rows), "included": sum(r["status"] == "included" for r in lib_map),
                    "skipped_before_cutoff": lib_skipped},
        "hf": {"chat": len(hf_rows), "included": sum(r["status"] == "included" for r in hf_map),
               "skipped_before_cutoff": hf_skipped},
        "confidence": {c: sum(r["confidence"] == c and r["status"] == "included" for r in lib_map + hf_map)
                       for c in ("high", "medium", "low")},
        "network_requests": f.network_requests,
    }
    (POP / "snapshots" / f"build-summary-{DATE}.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
