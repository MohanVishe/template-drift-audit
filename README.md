# template-drift-audit

A read-only auditor for one question: **is the prompt Ollama gives a model the prompt its author
wrote the model to expect?**

A chat model is trained on one exact prompt format, which its author publishes as a Jinja chat
template. By the time a conversation reaches the model through Ollama, that template has passed
through three hands:

| Layer | What it is | Where it lives |
|---|---|---|
| **L0** | the author's template, pinned to a commit | the author's Hugging Face repo |
| **L1** | the template embedded at GGUF conversion | `tokenizer.chat_template` in the GGUF header |
| **L3** | what Ollama actually runs | the package's Go template or built-in renderer, chosen by Ollama's own selection rule |

`tda` renders the same benign test conversations through every layer, diffs the results and
classifies each difference: whitespace, JSON spacing, a dropped default system prompt, tool
definitions printed as Go structs, re-wrapped tool calls, and so on. It also reports where each
difference first appears.

The audit never loads model weights. GGUF headers are read with HTTP range requests, and rendering
needs no GPU. A separate behavioural test (`tda/h3`, below) does run a model, on an isolated
Ollama server, to measure what the drift changes.

**The article, in plain language:** [ARTICLE.md](ARTICLE.md), the six weak spots of a local AI setup for everyday users and AI engineers.

**The tool test:** [TOOL-TEST.md](TOOL-TEST.md), whether the layout changes how well qwen2.5 uses tools.

**Website:** [mohanvishe.github.io/template-drift-audit](https://mohanvishe.github.io/template-drift-audit/):
the article, the tool test, a step-by-step guide to the check-up, and the full results.

## Results (snapshot 2026-10-22, Ollama v0.40.7)

Six tool fixtures (F04–F09), L0 vs L3, frozen classifier. Details in `P2-RESULTS.md`.

| Population | Material drift | Excluding key-order-only | Tool-capable: material | Tool-capable: excluding key order |
|---|---|---|---|---|
| Ollama library, top 50 chat | 32 / 43 | 28 / 43 | 15 / 19 | 11 / 19 |
| Hugging Face, top 30 GGUF | 5 / 22 | 5 / 22 | 4 / 21 | 4 / 21 |

In the library, 24 of the 32 come from Ollama's packaging alone. In 6, the GGUF already carries an
older template revision, and the packaging adds to that. The remaining 2 have no GGUF template.
All 5 Hugging Face cases are already in the GGUF's embedded template.

The data behind these numbers (every model's JSON and every render) is in `runs/p2-library/` and
`runs/p2-hf/`.

## Behavioural test: does the drift change tool use? (2026-10-25)

`qwen2.5:7b-instruct` (model layer `2bada8a74506`), BFCL at `6ea5797`, five single-turn categories,
1,240 items. Arm A1 is Ollama's L3 prompt rendered by the Go helper; arm B is the author's L0. Both
are sent raw to the same isolated Ollama v0.40.7 (`LLAMA_ARG_CACHE_RAM=0`, temperature 0, seed 42)
and both replies are read by BFCL's Hermes parser, so B − A1 is the layout alone.

| Category | n | A1 (L3) | B (L0) | B only | A1 only | Holm p |
|---|---|---|---|---|---|---|
| simple_python | 400 | 370 | 378 | 13 | 5 | 0.277 |
| multiple | 200 | 182 | 191 | 11 | 2 | 0.090 |
| parallel | 200 | 172 | 179 | 10 | 3 | 0.277 |
| parallel_multiple | 200 | 163 | 169 | 13 | 7 | 0.277 |
| irrelevance | 240 | 147 | 162 | 23 | 8 | 0.053 |
| **overall** | 1,240 | 1,034 (83.4%) | 1,079 (87.0%) | 70 | 25 | exact McNemar p = 4.3e-6 |

Checks: 0 cached tokens in all 2,480 steps, 40 of 40 repeats identical, no reply hit `num_predict`.
Data: `runs/h3-mini/qwen2.5/`; runner `scripts/h3_mini.py`, report `scripts/h3_mini_report.py`.

**Arm A, everyday use** (`--arms A`, 2026-10-26): the same items through `/api/chat` and Ollama's
own parser. Prompt equal to A1's on 1,240 of 1,240; 0 cached tokens; 20 of 20 repeats identical.
A 1,053 (84.9%) vs B 1,079 (87.0%): 40 vs 66 discordant, exact McNemar p = 0.015 (the
pre-registered headline in `scripts/h3_mini_report_a.py`). A vs A1 differ on 21 items: 20
irrelevance items where Ollama's parser drops a call to a tool that was not offered, and 1
parallel_multiple item where it returns `3.0` as `3`. Report: `report-A.json`.

## Quick check-up: `tda check`

A read-only check of your own machine that needs only Python, no other packages:

```bash
python -m tda check --folder <the folder your AI helper works in>
```

It reports:
- AI servers listening beyond this machine (Ollama, LM Studio, llama.cpp server);
- an Ollama version older than published security fixes;
- where each local model came from;
- template red flags (URLs, rules that react to words in a message);
- secret-looking file names in the folder;
- where conversations are saved on disk (Ollama history, the Ollama app database, LM Studio
  chats), and whether `OLLAMA_DEBUG_LOG_REQUESTS` is writing every request to disk.

It reads file names and sizes only, never contents. It changes nothing, and it contacts nothing except
Ollama on 127.0.0.1. `--json` gives machine-readable output.

## Why

Chat templates are executable code that ships inside model files, and they decide what the model
reads:
- A malicious template in GGUF metadata led to remote code execution in llama-cpp-python
  ([CVE-2024-34359](https://github.com/advisories/GHSA-56xg-wfcc-g829)).
- Splunk suggests watching for mismatches between the advertised and embedded templates
  ([Splunk, Feb 2026](https://www.splunk.com/en_us/blog/security/gguf-llm-security-inference-time-poisoning-templates.html)).

This tool compares rendered prompts rather than template source, because templates that differ as
text can render identically (7 of the 22 Hugging Face packages here do). It also covers the layer
a GGUF-only comparison leaves out: what Ollama itself runs, which can differ from both L0 and L1.

## How it stays faithful

- **L3 is rendered by Ollama's own code.** A small Go helper (`go-helper/`) imports
  `github.com/ollama/ollama` at the pinned tag (v0.40.7) and runs its template and renderer
  packages directly. On the validation model, the offline renders were byte-identical to a live,
  isolated Ollama v0.40.7 `_debug_render_only` render on 12 of 12 fixtures (`P0-RESULTS.md`).
- **Selection is a line-by-line port** of Ollama's `selectedTemplateSource`. It passes all 9 of
  Ollama's own test cases for that function.
- **L0 and L1 are rendered like transformers renders them:**
  - `ImmutableSandboxedEnvironment`, the same extensions and filters, in a subprocess;
  - a timeout and an output cap, because rendering an untrusted template is itself a risk.
- **The classifier was checked against hand labels** written before it existed. Its rules were
  tuned on a dev split and frozen (hashes in the results). It was then scored once on a held-out
  test split: 28 of 28 exact class-set matches (`P1-RESULTS.md`).
- **Known upstream issues are flagged, not claimed.** For example, Go-struct tool definitions are
  [ollama/ollama#14601](https://github.com/ollama/ollama/issues/14601).

## Use

Requirements:
- Python 3.12+ with `jinja2`.
- The Go helper, built in Linux or WSL with `go-helper/build.sh`. Set `TDA_WSL_DISTRO` and
  `TDA_GO_HELPER` if your setup differs.

```bash
pip install -e .
```

```bash
tda library --mapping population/mapping.yaml
```

```bash
tda hf --mapping population/mapping.yaml
```

```bash
tda local --mapping population/mapping.yaml
```

```bash
tda report runs/<run-id>
```

- `tda library` reads Ollama library packages: metadata and GGUF headers only.
- `tda hf` reads `hf.co/...` packages the same way.
- `tda local` reads your local Ollama store, read-only.
- `tda report` rebuilds `report.md` and `cells.csv` for a saved run.
- `--offline` reads only from the cache. Every network read is cached by content and logged, with
  its URL, time and size, in `.cache/provenance.jsonl`.

## Repository map

| Path | What |
|---|---|
| `tda/` | the auditor: GGUF reader, sources, selection port, renderers, classifier, report |
| `go-helper/` | the Go helper that runs Ollama's own template code |
| `tda/fixtures/fixtures.json` | 12 benign test conversations (F04–F09 use tools) |
| `labels/` | the labelled diff set and the labelling guide |
| `population/` | the dated study population (top Ollama library and HF GGUF packages) and its hand-made L0 mapping |
| `scripts/` | headline numbers, hand-review hunk viewer, population template lint, results page and site figures |
| `tda/h3/` | the behavioural test: BFCL items as prompts, output parsers, the isolated runtime |
| `runs/` | the published study data: P2 per-model JSON, every render, reports, headline and lint; the H3 tool test in `runs/h3-mini/` |
| `docs/` | the GitHub Pages site (article, tool test, guide, results, method) |
| `DESIGN.md`, `P0-RESULTS.md`, `P1-RESULTS.md`, `P2-RESULTS.md` | design and results notes, in order |

## Scope

This is a measurement tool. It reads public metadata and local files, renders benign fixtures and
reports differences. It makes no changes to any Ollama install. It does not judge intent: a
difference between layers is usually an older template or a packaging choice, not tampering.

## License

MIT
