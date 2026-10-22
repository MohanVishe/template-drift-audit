# template-drift-audit: design

Written 2026-10-22, before any code, and kept as written. What was built and measured is in
`P0-RESULTS.md`, `P1-RESULTS.md` and `P2-RESULTS.md`. The optional impact study (H3, §6) has not
been run yet.

## 1. The question

When you run a model in Ollama, the prompt the model actually reads is produced by a chat template.
That template can come from four different places, written by four different parties:

| Layer | Who writes it | Where it lives |
|---|---|---|
| **L0 reference** | The model author | `chat_template` in the upstream HF repo (`tokenizer_config.json` or `chat_template.jinja`) |
| **L1 embedded** | Whoever made the GGUF (Ollama, bartowski, unsloth, ...) | `tokenizer.chat_template` in the GGUF header |
| **L2 packaged** | Ollama library maintainers, or Hugging Face's converter for `hf.co/...` pulls | Go `TEMPLATE` layer and `SYSTEM` layer in the Ollama manifest; `renderer`/`parser` in its config blob |
| **L3 applied** | Ollama's selection rule, at a given version | Whichever of the above Ollama picks at run time |

**Research question:** for the same conversation, does the prompt Ollama feeds the model (L3) match
what the model author's template (L0) produces? Where it differs, which layer introduced the
difference, and does the difference touch tool calling?

This is a reliability and supply-chain-integrity measurement. It is read-only. It does not create,
modify or distribute templates or models.

## 2. Why this is new (checked 2026-10-22)

| Existing work | What it covers | What it leaves out |
|---|---|---|
| Splunk, Feb 2026 ([blog](https://www.splunk.com/en_us/blog/security/gguf-llm-security-inference-time-poisoning-templates.html)) | ~156k HF GGUF headers; compared advertised vs embedded template text; found nothing malicious | L2/L3 entirely; no rendering |
| c4nary ([PyPI](https://pypi.org/project/c4nary/)) | Static scan of 130,592 embedded templates for dangerous constructs (self-reported) | Never renders; no Ollama layer |
| pillar-gguf-scanner 0.1.2 ([PyPI](https://pypi.org/project/pillar-gguf-scanner/)) | Heuristics plus classifier for malicious embedded templates | Benign-but-different drift; Ollama layer |
| Pillar/Fujitsu, arXiv [2602.04653](https://arxiv.org/abs/2602.04653) | Shows the template is a trusted, executable part of the model | Not a census |
| Ollama's own `model/renderers/*_reference_test.go` | Parity tests for its built-in Go renderers against the Jinja template, for the families that have one | Go `TEMPLATE` layers, `hf.co` pulls, and the selection rule |

Nobody has published the **rendered L0 vs L3 comparison**, which is what decides what the model
actually sees.

## 3. Facts the design rests on (verified from source, 2026-10-22)

1. **Ollama chooses among six prompt sources.** `selectedTemplateSource()` in `server/images.go`
   returns `renderer_parser`, `renderer`, `parser`, `harmony`, `go_template`, `gguf_chat_template`
   or `none`.
2. **Ollama can prefer the GGUF's Jinja over its own Go template.** `shouldPreferChatTemplate()`
   picks the GGUF template when it advertises more capabilities, or carries tool-call IDs, or has a
   tool round trip the Go template lacks. In that "native" mode, llama-server renders the Jinja
   (`DisableJinja` is false). This logic is present at v0.30.0 and v0.34.2, absent at v0.23.2.
   The switch is `OLLAMA_GO_TEMPLATE` (default true).
3. **Ollama reports its choice.** `/api/show` returns `template_source` from **v0.40.7**
   (18 Oct 2026); earlier versions only log a `template selection` line.
4. **Ollama renders without generating.** `_debug_render_only: true` on `/api/chat` and
   `/api/generate` returns the exact prompt (`_debug_info.rendered_template`). It still loads the
   model first, because the check comes after `scheduleRunnerForModel`.
5. **Built-in renderers.** About 25 names (`qwen3-coder`, `qwen3.5`, `gemma4`, `glm-4.7`,
   `deepseek3.1`, `olmo3`, `lfm2`, ...) are selected through `renderer` in the config blob.
6. **Registry reads need no weights.** `registry.ollama.ai/v2/library/<m>/manifests/<tag>` is
   anonymous. Blob GETs redirect to Cloudflare R2 and honour `Range` (tested: HTTP 206 returned the
   `GGUF` magic).
7. **Hugging Face makes its own Go template.** `hf.co/v2/<repo>/manifests/<quant>` serves an
   Ollama manifest whose template layer comes from HF's converter (`@huggingface/ollama-utils`,
   with a hand-kept `CUSTOM_TEMPLATE_MAPPING`). `huggingface.co/api/models/<repo>?expand[]=gguf`
   returns one parsed `chat_template` per repo.
8. **GGUF headers are big.** The chat template sits after the tokenizer arrays. On the local
   `qwen2.5:7b-instruct` the key-value section ends at byte 5,934,631, so ranged reads must grow
   their window. Splunk read ~20 MB.
9. **Reference renderer.** transformers renders chat templates with
   `ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True, extensions=[AssistantTracker, loopcontrols])`,
   a `tojson` with `ensure_ascii=False`, and the globals `raise_exception` and `strftime_now`
   (`utils/chat_template_utils.py`). That can be reproduced with `jinja2` alone.
10. **Popularity list.** `ollama.com/library?sort=popular` lists 258 entries with pull counts and
    capability tags such as `tools`.

### A worked example already on your disk (read from the template text, not yet rendered)

For `qwen2.5:7b-instruct` (manifest `registry.ollama.ai/library/qwen2.5/7b-instruct`):

- **L1, the GGUF's Jinja:** puts back-to-back tool results into a single `<|im_start|>user` turn.
  It emits assistant text and tool calls together.
- **L2, Ollama's Go template:** gives each tool result its own turn. It uses
  `if .Content ... else if .ToolCalls`, so an assistant turn with both keeps only the text. The
  default system prompt moves to a separate `SYSTEM` layer.
- **`hf.co/bartowski/Qwen2.5-7B-Instruct-GGUF:Q4_K_M` gets a different L2.** HF serves a template
  with a fill-in-the-middle (`.Suffix`, `<|fim_prefix|>`) branch, which is the coder model's
  layout, and no `SYSTEM` layer.
- The GGUF's `general.base_model.0.repo_url` points to the base model `Qwen/Qwen2.5-7B`, not the
  Instruct repo. So the mapping from L1 to L0 cannot trust metadata alone.

The tool exists to measure exactly this, across a population, with rendering and classification.

## 4. What the tool does

### 4.1 Commands

```
tda local                          # audit models in the local Ollama store (read-only)
tda library --top 50               # Ollama library, metadata-only via the registry
tda hf --top 30 --quant Q4_K_M     # Hugging Face GGUF repos via hf.co manifests
tda validate --live                # check offline renders against a pinned, isolated Ollama
tda report                         # Markdown, JSON, CSV from the cached run
```

### 4.2 Pipeline for one model

1. **Collect** (cached and content-addressed; each artifact stores URL, time and sha256):
   - manifest, config blob, `template`, `system` and `params` layers;
   - GGUF header via a growing ranged read, capped at 64 MB;
   - L0 from the mapped upstream repo, pinned to a commit sha.
2. **Select:** compute L3's source with a Python port of `selectedTemplateSource` for the pinned
   Ollama version. Where the live tier is available, cross-check it against
   `/api/show.template_source`.
3. **Render** every fixture (§4.3) through:
   - L0 and L1 with the transformers-compatible Jinja environment;
   - L2 or the renderer with the Go helper (§5.2);
   - L3 = whichever path step 2 selected.
4. **Normalise:** pin the date, unify line endings, and mark the leading-BOS handling. Keep the raw
   strings too.
5. **Diff and classify** each pair (L0↔L1, L1↔L3, L0↔L3) into the drift taxonomy (§4.4).
6. **Lint (secondary):** flag static constructs in every template, such as URLs, base64 blobs,
   branches on message content, and text added outside message slots. Also run
   pillar-gguf-scanner as an independent comparator. This finds review prompts, not verdicts.

### 4.3 Conversation fixtures (benign, deterministic, versioned)

| ID | Content |
|---|---|
| F01 | single user turn |
| F02 | system + user |
| F03 | three-turn chat |
| F04 | no system message (exposes default system prompts) |
| F05 | tools defined, user asks |
| F06 | assistant tool call → tool result → generation prompt |
| F07 | two parallel tool calls → two tool results (grouping) |
| F08 | assistant text **and** a tool call in one turn |
| F09 | tool call with an ID (`tool_call_id`) |
| F10 | non-ASCII and JSON-special characters in content and tool arguments |
| F11 | reasoning/thinking content in an earlier assistant turn |
| F12 | a literal `{{ }}` / `{% %}` string inside user content, which must come out verbatim |

F05–F09 are the tool-calling set used by the headline.

### 4.4 Drift taxonomy

The class decides whether a difference counts toward the headline. "Material" means it changes
tokens the model conditions on in a way the author's template did not intend.

| Class | Material? | Example |
|---|---|---|
| `IDENTICAL` | no | |
| `WHITESPACE` | no | trailing newline, indentation |
| `BOS` | no, reported | BOS added by template vs by tokenizer |
| `DATE` | no | date injection, normalised |
| `DEFAULT_SYSTEM` | yes | default system prompt added, dropped or changed |
| `TOOL_SCHEMA` | yes | tool definitions serialised differently (keys, wrapper, format) |
| `TOOL_CALL` | yes | assistant tool-call serialisation; text and calls not both kept |
| `TOOL_RESULT` | yes | tool results grouped, re-roled or re-wrapped differently |
| `TOOLS_DROPPED` | yes, flagged | tools passed but absent from the rendered prompt |
| `THINKING` | yes | reasoning kept or stripped differently in history |
| `EXTRA_BRANCH` | reported | a branch the author template lacks (e.g. FIM) that the fixture didn't hit |
| `RENDER_ERROR` | yes | one side cannot render the fixture |
| `OTHER` | yes, hand-reviewed | anything unmatched; every case gets a manual read |

The classifier is rule-based over a token-level diff. It is checked against a hand-labelled set of
about 60 diff pairs before any population number is reported.

### 4.5 Outputs

- **Per model:** layer digests, selected source, a fixture × pair class matrix, and the raw diffs.
- **Per run:** a `run.json` with tool version, Ollama version, fixture-set hash, snapshot dates and
  every source URL.
- **Report:** a Markdown table plus a CSV for charts.

## 5. Architecture

### 5.1 Python core

Pure Python 3.12+, Windows-native. Runtime dependency: `jinja2` only (stdlib `urllib` for HTTP).
Dev: `pytest`.

```
tda/
  gguf.py              header reader over any seekable or ranged stream (no numpy)
  sources/
    ollama_store.py    ~/.ollama/models manifests + blobs, opened read-only
    ollama_registry.py manifests, small blobs, ranged GGUF reads
    hf.py              hf.co manifests, ?expand[]=gguf, upstream files at a commit sha
    library.py         popular-list snapshot (saved HTML + parsed CSV)
  mapping.yaml         model -> upstream L0 repo@sha, with a written reason per row
  select.py            port of selectedTemplateSource for the pinned Ollama version
  render/
    jinja_ref.py       transformers-compatible ImmutableSandboxedEnvironment
    go_helper.py       client for the WSL Go helper (5.2)
    ollama_live.py     client for the isolated Ollama instance (5.3)
  fixtures/*.json
  normalize.py  classify.py  lint.py  report.py
  cache.py             content-addressed cache with provenance
```

**Rendering untrusted Jinja safely.** Rendering a hostile template is itself a known risk: this is
the CVE-2024-34359 class. So:
- only the immutable sandbox is used;
- each render runs in a subprocess with a timeout and an output cap;
- templates are linted before rendering, and a template with a lint hit is rendered only in the
  sandbox, never with a plain `Environment`.

### 5.2 Go helper (WSL, about 100 lines)

- A small program that imports `github.com/ollama/ollama/template` and
  `github.com/ollama/ollama/model/renderers` at the **same tag** as the pinned Ollama.
- It reads `{template | renderer, messages, tools, think}` as JSON on stdin and writes the rendered
  string.
- It renders `go_template` and `renderer` paths exactly as Ollama's own code would, with no weights
  and no server.
- Built and run in WSL (`Ubuntu-24.04`), so Smart App Control is not involved.

### 5.3 Live validation tier (isolated, pinned)

- A pinned Linux Ollama (**v0.40.7**, the first release with `template_source`) unpacked into a
  project directory inside WSL.
- Run as `ollama serve` with `OLLAMA_HOST=127.0.0.1:11500` and `OLLAMA_MODELS=<project>/.ollama-iso`.
- It never touches the Windows install, its model store, its updater or any config.
- For a validation subset of about 10–12 models that fit in 8 GB, every fixture goes through
  `_debug_render_only`.
- **Fidelity metric:** the share of model × fixture pairs where the offline render (5.1/5.2) is
  byte-identical to the live render, split by source path. It is reported, and it bounds how far the
  static tier can be trusted. The `gguf_chat_template` path is rendered natively by llama-server's
  Jinja engine, so it is the path most likely to differ from Python `jinja2`. If its fidelity is
  low, those models get live renders only.

## 6. Population and headline

- **Ollama library:** the top 50 chat models from the `sort=popular` snapshot.
  - Embedding-only models are excluded.
  - Each model uses its default tag; the size tags are audited too and deduplicated by template
    digest.
  - Models without a public upstream chat template are listed and excluded.
- **Hugging Face:** the top 30 GGUF repos by downloads (HF API, `filter=gguf`, snapshot dated),
  at `Q4_K_M` or the nearest available quant.
- **L0 mapping:** done by hand in `mapping.yaml`, one reason per row, pinned to a commit sha.

**Headline H1:** *k of N popular Ollama library chat models feed the model a prompt that
materially differs from the model author's own template on at least one tool-calling conversation
(F05–F09).*
- The number is reported with the per-class breakdown and the per-layer origin (L1 vs L2 vs
  selection).
- It is a census of a dated top-N list, so it is stated as k/N, not as a sampled estimate.

**H2:** the same measure for `hf.co/...` pulls.

**Supporting numbers:**
- static-vs-live fidelity;
- how often L1 ≠ L0, i.e. the quantiser changed the author's template;
- `template_source` distribution;
- lint hits, with the pillar-gguf-scanner agreement rate.

No number is stated anywhere until it comes from a run.

**Optional H3 (impact, GPU):** for 3–5 materially drifted models that fit in 8 GB, run a
multi-turn tool-calling subset (BFCL multi-turn, or the F07/F08 patterns at scale) twice:
- once through Ollama's normal path;
- once with the L0-rendered prompt sent as `raw: true`.

The result is the accuracy difference attributable to drift. This links the audit to the
reliability theme.

## 7. Plan and effort

| Phase | Work | Estimate |
|---|---|---|
| P0 spike | GGUF ranged reader; registry + hf.co collectors; Go helper builds in WSL; isolated v0.40.7 renders `qwen2.5:7b-instruct` with `_debug_render_only`; confirm which source v0.34.2/v0.40.7 selects for it | 2 days |
| P1 core | Selection port + parity tests, Jinja reference env, fixtures, normaliser, classifier + 60-pair labelled set, report | 5 days |
| P2 runs | Library top-50 and HF top-30 static runs; live validation subset; manual review of every `OTHER` | 4 days |
| P3 optional | H3 impact runs on GPU | 3–4 days |
| P4 write-up | Article, README, tests in CI (offline fixtures only), reproducibility notes | 3 days |

Core total is about 2.5 weeks; about 3 weeks with H3.

**Network budget:**
- The static tier reads about 6–30 MB of header per GGUF plus kilobyte-sized blobs, so roughly
  1–2 GB for 80 models.
- Requests are paced at about one per second, use an honest User-Agent, and are cached so nothing
  is fetched twice.
- The live tier needs full weights only for the validation subset: about 10–12 models, roughly
  40 GB. Models already on disk are reused by copying blobs into the isolated store, never by
  pointing the instance at the real store.

## 8. Threats to validity, and how the write-up handles them

- **Drift is not a bug, and a bug is not malice.** Ollama may diverge on purpose, for example to
  fix a broken upstream template. The article reports classes and origins and does not call
  differences errors. Each material class gets a worked example, checked by hand.
- **The L0 template changes upstream.** It is pinned to a commit sha and dated.
- **Ollama changes fast.** Results are tied to one pinned version; a re-run script is shipped.
- **Python `jinja2` vs llama.cpp's Jinja engine vs `@huggingface/jinja`.** The fidelity metric
  measures this instead of assuming it away.
- **The popularity list is one snapshot.** The saved HTML is committed with its date.
- **Mapping errors.** Every row in `mapping.yaml` carries a reason, and the HF base-model metadata
  quirk in §3 shows why this is needed.

## 9. Boundaries

- **Read-only** against public metadata and the local store. No weights are downloaded in the
  static tier.
- **No live endpoints.** No exposed or third-party Ollama servers are probed; the live tier talks
  only to the isolated `127.0.0.1:11500` instance.
- **No altered templates.** No templates or models are created, altered or uploaded. Lint unit
  tests use inert synthetic templates that only insert a harmless marker string.
- **No changes to your setup.** Your Windows Ollama install, its store, its auto-update setting and
  your configs are untouched.
- **Nothing outward without your go-ahead.** Reporting a drift to Ollama or Hugging Face as an
  issue, publishing the repo, and the article all wait for an explicit OK.

## 10. Decisions needed before P0

1. **Go helper in WSL** (needs a Go toolchain download inside WSL), or the live tier only (needs
   weights for every model). Recommended: the Go helper.
2. **Pinned Ollama for the study:** v0.40.7 as a separate Linux install in WSL (recommended). Your
   Windows install's pending update is a separate choice of yours.
3. **Population size:** 50 library + 30 HF, or smaller.
4. **Include H3 or not.**
5. **Repo name.**
