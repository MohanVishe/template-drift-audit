# Study population and L0 mapping

Snapshot date: **2026-10-22** (local). All fetches ran 2026-10-21 22:16–22:33 UTC.
Read-only, metadata only: no weights, no registry manifests or blobs, no local Ollama.

## Files

| File | What |
|---|---|
| `library_top50.csv` | Top 50 chat models from the Ollama library, with pulls, capability tags, and what `latest` resolves to |
| `hf_top30.csv` | Top 30 text chat GGUF repos on Hugging Face by downloads, with the chosen quant |
| `mapping.yaml` | One row per package (80): upstream author repo, pinned sha, template file, confidence, reason |
| `snapshots/ollama-library-popular-2026-10-22.html` | `https://ollama.com/library?sort=popular`, as served |
| `snapshots/ollama-tags-2026-10-22/<name>.html` | `https://ollama.com/library/<name>/tags` for each of the 50 (fetched with Mohan's OK) |
| `snapshots/hf-gguf-by-downloads-2026-10-22.json` | `https://huggingface.co/api/models?filter=gguf&sort=downloads&direction=-1&limit=100`, raw |
| `snapshots/build-summary-2026-10-22.json` | Counts and the population-level skips, as printed by the build |
| `tools/` | The parsers and the build script; the hand mapping lives in `tools/build_population.py` |

Every other response (151 calls to `huggingface.co/api/models/<repo>/revision/main`) is stored by sha256 in
`.cache-population/`, with URL, time and status in `.cache-population/provenance.jsonl`.

Rebuild from the cache with no network:

```
python -I -X utf8 population/tools/build_population.py --offline
```

## Network use

202 requests and 13.7 MB, all HTTP 200, at no more than one request per second (`tda.http.Fetcher`):
- `ollama.com`: 51 requests (the library page, plus 50 tags pages);
- `huggingface.co`: 151 requests (the GGUF list, plus `revision/main` for the GGUF repos and every candidate upstream repo).

No repo files were downloaded. The revision API already returns the file list, the card's
`base_model`, the gate status, and the template text (`config.chat_template_jinja` and
`config.tokenizer_config.chat_template`) for gated repos too, so that was enough.

## Method

### Ollama library (50)

1. Parse the popular page in page order (258 entries).
2. Drop embedding-only models (capability tag `embedding`) and keep the first 50 that remain. That
   reaches page rank 57. Seven embedding models fell before the cutoff: `nomic-embed-text`,
   `mxbai-embed-large`, `bge-m3`, `qwen3-embedding`, `all-minilm`, `snowflake-arctic-embed`,
   `embeddinggemma`.
3. The default tag is `latest`. The tags page lists every tag with a 12-character digest. The tags
   that share `latest`'s digest show which size and quant it is (`latest_size_tag`,
   `latest_full_tag`). For example, `qwen3:latest` is `8b-q4_K_M` and `qwen3-vl:latest` is
   `8b-thinking-q4_K_M`.
4. `pulls` is the page's rounded display value converted to a number (for example, `120.5M` becomes
   120,500,000). `pulls_display` keeps the original text.

No other filter was applied. OCR (`glm-ocr`), translation (`translategemma`), code and vision
models stay in, because the rule excludes embedding models only.

### Hugging Face (30)

1. Take the top 100 GGUF repos by downloads, in API order.
2. Skip repos that are not text chat models. A repo is skipped if its pipeline tag is speech,
   image, video, music, object detection or embedding, or if hand inspection shows it is a
   music, video or OCR package (listed in `HF_NONCHAT_REPOS`). Keep the first 30 that remain.
   That reaches download rank 43.
3. Skipped before the cutoff:
   - by pipeline tag: `mudler/locate-anything.cpp-gguf`, `audio-cpp/audio.cpp-gguf`,
     `abenzerps/Qwen-Image-2.1-Uncensored-Quantized`, `mixedbread-ai/mxbai-embed-large-v1`,
     `unsloth/MiniMax-H3-GGUF`, `handy-computer/nemotron-3.5-asr-streaming-0.6b-gguf`,
     `handy-computer/parakeet-unified-en-0.6b-gguf`, `unsloth/Qwen-Image-2.1-GGUF`,
     `scragnog/MOSS-Music-8B-Instruct-GGUF`, `pnnbao-ump/VieNeu-TTS-v3-Turbo`,
     `nvidia/nemotron-3.5-asr-streaming-0.6b`;
   - by hand: `Serveurperso/YuE2-GGUF` and `Serveurperso/ACE-Step-1.5-GGUF` (both music).
4. **Quant.** Use `Q4_K_M` when the repo has it (unsloth's `UD-Q4_K_M` counts). Otherwise use the
   nearest quant by bits per weight, in the order set by `QUANT_PREF` in `tools/hfinfo.py`.
   Files that bundle an MTP draft head are used only when no other file exists. Projector, imatrix
   and draft files are ignored. Two repos with no standard quant names were set by hand
   (`antirez/deepseek-v4.1-flash-gguf`: MXFP4; `mudler/Laguna-XS-2.1-APEX-GGUF`: APEX-Balanced),
   and so was `antirez/deepseek-v4-gguf` (Q4_K experts). 18 of the 30 repos offer Q4_K_M. The
   rest are noted in `quant_note`.

### L0 mapping (80 rows)

Rules, applied by hand to every package:

| Package is | upstream_repo |
|---|---|
| An Ollama library model | The author's post-trained (instruct, chat or thinking) repo for exactly the size and version `latest` resolves to |
| A pure quantisation (unsloth, ggml-org, bartowski-style, ISTA-DASLab, ...) | The quantised model's own repo, i.e. the card's base, after checking that it is the post-trained model and not a base model |
| A fine-tune or weight edit whose author also publishes a safetensors repo | That author repo, not the model it was trained from (the GGUF card often skips it) |
| A fine-tune or weight edit published **only** as GGUF | Excluded: no author template exists outside the GGUF. `candidate_repo` records what its card points at |
| A model whose author ships no Jinja chat template | Excluded with the reason |

- `upstream_sha` is `revision/main` on the snapshot date.
- `template_file` follows the load order in `tda.sources.upstream`: `chat_template.jinja`, then
  `chat_template.json`, then `tokenizer_config.json`.
- Redirected repo ids were replaced by their canonical ids (`cognitivecomputations/` is now `dphn/`).

**Confidence:**
- **high:** the identity is unambiguous from the tag or card, and the template file is clear.
- **medium:** the repo is right, but there is a stated doubt about the exact variant, the
  precision repo, or which file counts as L0.
- **low:** the mapping is a best guess that needs Mohan's review.

**Evidence (HF rows only):** the hub's parse of the GGUF's embedded template is compared with the
upstream template text at main. The result is "byte-identical", "differs (n vs m chars)" or
"absent". This is a sanity check on the mapping, not a drift result:
- the hub parses one file per repo;
- the comparison is against the current upstream, not the one in effect when the GGUF was made.

Library rows have no such check, because their GGUF headers come from registry blobs, which were
out of scope here.

## Counts

| | Packages | Included | Excluded | high | medium | low |
|---|---|---|---|---|---|---|
| Ollama library | 50 | 45 | 5 | 39 | 5 | 1 |
| Hugging Face | 30 | 27 | 3 | 18 | 7 | 2 |
| **Total** | **80** | **72** | **8** | **57** | **12** | **3** |

The confidence columns count included rows only. The 72 included packages map to 62 distinct
upstream repos.

The three low-confidence rows (`llava:latest`, `peculiar-ragdoll/Tiel-Coder-35B-A3B-GGUF-MTP`,
`peculiar-ragdoll/Dirk-Qwen3.8-27B-GGUF`) were reviewed by Mohan on 2026-10-22 and kept as mapped,
at low confidence.

Template files, for the included rows:

| Source | tokenizer_config.json | chat_template.jinja | chat_template.json |
|---|---|---|---|
| Library | 32 | 9 | 4 |
| Hugging Face | 0 | 27 | 0 |

12 of the included upstream repos are gated (11 manual, 1 auto); see the `gated` field.

## Exclusions

| Package | Why |
|---|---|
| `orca-mini:latest` | `pankajmathur/orca_mini_3b` has no chat template; its prompt format is only prose in the card |
| `starcoder2:latest` | `latest` is the 3B base completion model; `bigcode/starcoder2-3b` has no chat template |
| `llama2-uncensored:latest` | `georgesung/llama2_7b_chat_uncensored` has no chat template |
| `mistral-small3.2:latest` | Mistral ships `tekken.json` and `SYSTEM_PROMPT.txt` for mistral-common, with no Jinja template |
| `minimax-m2.7` | Cloud-only in Ollama (its only tag is `cloud`), so there is no local package to audit |
| `hf.co/HauhauCS/Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-MTP-GGUF` | GGUF-only weight edit; candidate `Qwen/Qwen3.8-27B` |
| `hf.co/SC117/Qwen3.8-Flash-Next-GSQ-RCO-abliterated-GGUF` | GGUF-only weight edit; candidate `Qwen/Qwen3.8-Flash-Next` |
| `hf.co/antirez/deepseek-v4-gguf` | DeepSeek-V4-Flash defines its prompt in Python (`encoding/encoding_dsv4.py`), not Jinja |

## Things P2 needs to know

- **L0 is pinned once here, at main.** P0 found that L0 needs a second pin: the upstream commit in
  effect when the GGUF was made. That second pin is not in this mapping.
- **Gated repos.** `tda.sources.upstream.load` fetches `resolve/<sha>/...`. For the 12 gated repos
  this needs an HF token with each license accepted. The alternative is to read the template text
  from the revision API, as this build did.
- **The HF population is concentrated.** 13 of the 30 HF repos have Qwen3.8 in their name, and 7
  of the included HF rows map to `Qwen/Qwen3.8-27B`. Report H2 with that in view.
- **Some packages may not load in Ollama:**
  - `antirez/deepseek-v4.1-flash-gguf` uses a custom architecture (`deepseek41`);
  - `prism-ml/Ternary-Bonsai-2-27B-gguf` has ternary quants only;
  - `cdiamond/...-NVFP4-MTP-GGUF` is an NVFP4 file.

  Their metadata can still be audited, but the `hf.co` manifest and the live tier may fail.
- **Ornith 1.5 repos carry two templates.** `ornith-ai/Ornith-1.5-{9B,35B-A3B,397B}` each have a
  `chat_template.jinja` and a different `chat_template` in `tokenizer_config.json`. Their GGUFs
  embed a third version. `chat_template.jinja` is taken as L0, which is what transformers loads.
