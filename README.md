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

It never loads model weights. GGUF headers are read with HTTP range requests, and rendering needs
no GPU.

**Website, in plain language:** [mohanvishe.github.io/template-drift-audit](https://mohanvishe.github.io/template-drift-audit/):
the article, a step-by-step guide to the check-up, and the full results.

## Results (snapshot 2026-10-22, Ollama v0.40.7)

Six tool fixtures (F04–F09), L0 vs L3, frozen classifier. Details in `P2-RESULTS.md`.

| Population | Material drift | Excluding key-order-only | Tool-capable: material | Tool-capable: excluding key order |
|---|---|---|---|---|
| Ollama library, top 50 chat | 32 / 43 | 28 / 43 | 15 / 19 | 11 / 19 |
| Hugging Face, top 30 GGUF | 5 / 22 | 5 / 22 | 4 / 21 | 4 / 21 |

In the library, 24 of the 32 come from Ollama's packaging alone. In 6, the GGUF already carries an
older template revision, and the packaging adds to that. The remaining 2 have no GGUF template. All 5 Hugging Face cases are already in the
GGUF's embedded template.

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
- secret-looking file names in the folder.

It reads file names only, never contents. It changes nothing, and it contacts nothing except
Ollama on 127.0.0.1. `--json` gives machine-readable output.

## Why

Chat templates are executable code that ships inside model files, and they decide what the model
reads:
- A malicious template in GGUF metadata led to remote code execution in llama-cpp-python
  ([CVE-2024-34359](https://github.com/advisories/GHSA-56xg-wfcc-g829)).
- Pillar Security showed that a tampered template can plant a trigger-activated backdoor that
  survives four inference engines, Ollama among them
  ([Pillar Security, Feb 2026](https://www.pillar.security/blog/from-discovery-to-large-scale-validation-chat-template-backdoors-across-18-models-and-4-engines)).
  Their advice to deployers is to compare GGUF templates against the provider's originals.
- Splunk suggests watching for mismatches between the advertised and embedded templates
  ([Splunk, Feb 2026](https://www.splunk.com/en_us/blog/security/gguf-llm-security-inference-time-poisoning-templates.html)).

This tool does that comparison on the rendered prompt rather than on template source. It also adds
the layer those comparisons leave out: what Ollama itself runs, which can differ from both L0 and
L1.

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
| `scripts/` | headline numbers, hand-review hunk viewer, population template lint, results-page builder |
| `docs/` | the GitHub Pages site (article, guide, results, method) |
| `DESIGN.md`, `P0-RESULTS.md`, `P1-RESULTS.md`, `P2-RESULTS.md` | design and results notes, in order |

## Scope

This is a measurement tool. It reads public metadata and local files, renders benign fixtures and
reports differences. It makes no changes to any Ollama install. It does not judge intent: a
difference between layers is usually an older template or a packaging choice, not tampering.

## License

MIT
