# P2 results: population audit and `tda check`

Date: 2026-10-22. Everything below comes from runs on this machine, with the classifier frozen in P1
(`tda/classify.py`, sha256 `00e9bd5ae2a2cacfa79d192415648bd9031afe74ab294d98a0286876b8fe0e1b`,
recorded in every `run.json`). The commands that reproduce it are listed at the end.

## 1. Runs

| Run | Packages in mapping | Excluded by mapping | Audited | Scored | Network |
|---|---|---|---|---|---|
| `p2-library` | 50 | 5 | 45 | 43 | 616 requests, 458 MB |
| `p2-hf` | 30 | 3 | 22 (+5 skipped) | 22 | 28 requests, 32 MB |

- Population and mapping: `population/README.md`, `population/mapping.yaml` (sha256
  `44d81a5a…286fbf`). Ollama v0.40.7 (Go helper). Fixtures `745406c928e5`.
- Library, not scored: `gpt-oss:latest`, because Ollama selects the harmony renderer, which is not
  rendered offline; and `translategemma:latest`, whose author template renders none of F04–F09.
- HF skipped: 5 packages for which `hf.co` returned HTTP 400 to the manifest request (sharded
  or non-standard quant names). unsloth packages tagged `Q4_K_M` resolve only as `UD-Q4_K_M`. The
  auditor retries with `UD-` on a 404 and records `resolved as …` in the model's JSON.
- Sandbox restarts: 0 in both runs.

## 2. Headline

Computed by `scripts/headline.py` (output `runs/p2-headline.json`). For each scored package:
- **material**: at least one tool fixture (F04–F09) differs materially, L0 → L3.
- **tool-capable**: the tool name appears in the L0 F04 render.
- **strict**: material after dropping TOOL_SCHEMA hunks that sit inside tool definitions which
  are equal once key order is ignored.

| Population | Material | Strict | Tool-capable: material | Tool-capable: strict |
|---|---|---|---|---|
| Ollama library | 32 / 43 | 28 / 43 | 15 / 19 | 11 / 19 |
| Hugging Face | 5 / 22 | 5 / 22 | 4 / 21 | 4 / 21 |

**Key order only (library):** `qwen3-vl`, `qwen3.5`, `qwen3.6`, `qwen3.8`. Ollama's Qwen 3.x
renderers emit `required` before `properties`, and nothing else differs.

**Origin of material drift (library, 32):**
- Ollama packaging only (L1 = L0 on tool fixtures): 24.
- Conversion and packaging: 6 (`falcon3`, `mistral-nemo`, `mistral`, `phi4`, `qwen2.5`, `qwen`).
- No GGUF template: 2 (`codellama`, `glm-ocr`).

**Origin (HF, 5):** conversion only, in all 5. Ollama runs the GGUF's own template for these
packages, and the packaging pair shows no material difference.

**Strict classes, library (packages with the class, out of 28):** TOOL_RESULT 20, DEFAULT_SYSTEM 10,
TOOL_CALL 10, OTHER 8, TOOLS_DROPPED 7, TOOL_SCHEMA 7, CONTENT 4, TOOL_SCHEMA_NOT_JSON 4,
STRUCTURE 3.

**ollama/ollama#14601 (Go-struct tool definitions):** `qwen2`, `qwen2.5`, `qwen2.5-coder`, `qwen3`.

**No drift on any tool fixture:** `codegemma`, `gemma`, `gemma2`, `gemma4`, `deepseek-v3`,
`llava`, `mixtral`, `nemotron-3-super`, `qwen3-coder`, `translategemma` (not scored), and
`deepseek-r1` and `llama3.2-vision` (approximate L3, see §5).

## 3. L0 at conversion

The library GGUF templates were matched against the author repo's commit history (`revision_matching`):
- 30 are equal to the pinned L0 (`current`).
- 9 match an older revision exactly.
- 6 have no GGUF template, or the template could not be matched.

| Package | GGUF matches revision of | Replaced upstream on | Upstream commit title |
|---|---|---|---|
| `falcon3` | 2024-12-17 | 2024-12-18 | fix chat_template for tool use (#7) |
| `mistral-nemo` | 2024-07-30 | 2024-07-31 | Fix chat template (#56) |
| `mistral-small` | 2025-01-30 | 2025-01-30 | Add system message to chat template (#6) |
| `mistral` | 2024-05-22 | 2024-06-20 | Updating chat template, trying to make it match with `mistral_common` (#44) |
| `phi4` | 2025-01-08 | 2025-02-04 | Suggested tokenizer changes by Unsloth.ai (#21) |
| `qwen2.5` | 2024-09-18 | 2024-09-19 | Upload ./tokenizer_config.json with huggingface_hub |
| `qwen3-coder` | 2025-08-01 | 2025-08-07 | Update chat_template in tokenizer_config.json (#14) |
| `qwen3` | 2025-04-29 | 2025-05-19 | update tokenizer_config.json |
| `qwen` | 2024-02-05 | 2024-02-06 | update tokenizer_config.json |

HF: 10 `current`, 1 exact older revision (`JiRackUltra_1b`, same day), 11 matching no revision.
Of those 11, 7 render **identically** to L0 on all 12 fixtures:
- `huihui-ai` Qwen3.8-27B abliterated;
- Ornith-1.5 at 9B, 35B-A3B and 397B;
- unsloth gemma-4-12b-it, Qwen3.6-35B-A3B and Qwen3.8-27B.

Their template text differs, but what the model reads does not. This is the case for diffing
renders rather than template source.

## 4. Hand review

Every library package classified material was reviewed with `scripts/inspect_run.py`. Each one has
at least one genuine material tool-fixture difference. Notable ones:
- **llama3.1 / 3.2 / 3.3:** Ollama's template replaces the tool instructions and drops
  "Environment: ipython". The parallel-call fixture is a reference error on L0.
- **falcon3:** the tool system prompt is dropped.
- **dolphin3, tinyllama, olmo2:** a default system prompt is added.
- **qwen, minicpm-v:** the author's default system prompt is dropped.
- **phi3, tinyllama:** no generation prompt after tool turns.
- **qwen2.5vl, qwen, llama3:** tool results are dropped or merged.
- **HF Dirk-Qwen3.8-27B and Tiel-Coder-35B-A3B (same uploader):** the GGUF template
  - rewrites the tool instructions;
  - adds think-block guidance and a standing answer-style instruction;
  - drops the author's "Reasoning effort is set to …" system text.
- **HF unsloth Qwen3.5 4B / 9B:** the GGUF template closes an empty think block after tool turns.

**Classifier gaps found in review.** The classifier is frozen, so these are not fixed:
- DeepSeek's BOS token `<｜begin▁of▁sentence｜>` is not in `BOS_TOKENS`, so it lands in OTHER.
  This is the only false material hunk found. Every package it touches has other material
  classes, so no package verdict changes.
- "Assistant:" role headers, an empty `<<SYS>><</SYS>>` block and Granite's tool instructions
  land in OTHER. They are genuine material differences with a vague label.

**Fixture limit.** Mistral's author templates require 9-character alphanumeric tool-call ids. The
fixtures use `call_1`, so those cells are REFERENCE_ERROR and are not counted.

## 5. Exactness

- Library L3 via the Go template or a built-in renderer is Ollama's own code (P0: byte-identical
  to a live render).
- When Ollama selects `gguf_chat_template` (all HF packages; `deepseek-r1`, `deepseek-v3` and
  `llama3.2-vision` in the library), L3 is an emulation of llama-server's Jinja path in Python.
  It is marked approximate in every report.

## 6. `tda check` on the population

`scripts/lint_population.py` runs the check's template rules over every cached template:
L0, L1 and the Ollama Go template, 95 distinct templates from 65 packages (`runs/p2-lint.json`).
3 are flagged, and on reading, all 3 are benign, visible features:
- `gpt-oss` (L0): harmony channel markers.
- Dirk-Qwen3.8 and Tiel-Coder (L1): `<|think_…|>` words that switch the reasoning mode.

No template in the population contains a URL.

**Other checks.** `tda check` also lists where conversations are saved (the Ollama history file,
the Ollama app database and LM Studio's conversations folder, by name and size only), and warns
when `OLLAMA_DEBUG_LOG_REQUESTS` is on. The locations come from Ollama v0.40.7's source and LM
Studio's documentation. The `OLLAMA_HOST` rule parses the value the way Ollama's `envconfig.Host()`
does, so `http://0.0.0.0:11434`, `:11434` and a LAN address are all reported as reachable from
other devices.

## 7. Not measured here

- **Behavioural effect.** This study counts how often the text differs, not how much that changes
  a model's answers. The design's optional H3 (DESIGN.md §6) would run a few drifted models on a
  small tool-calling set twice: once through Ollama's normal path, and once with the L0 render sent
  raw. That needs the models run locally and is the next study.
- **Non-default tags.** Only each package's `latest` tag was audited.

## 8. Reproduce

The P2 runs are published in `runs/p2-library/`, `runs/p2-hf/`, `runs/p2-headline.json` and
`runs/p2-lint.json`. That covers every model's JSON and every render. The HTTP cache (`.cache/`) is
not published, so re-running from scratch fetches the metadata again.

```bash
python -m tda library --mapping population/mapping.yaml --run-id p2-library
```

```bash
python -m tda hf --mapping population/mapping.yaml --run-id p2-hf
```

```bash
python scripts/headline.py runs/p2-library runs/p2-hf --out runs/p2-headline.json
```

```bash
python scripts/lint_population.py
```

```bash
python scripts/results_page.py
```

```bash
python scripts/site_figures.py
```

With a local `.cache/`, add `--offline` to the first two commands to re-run with no network.
