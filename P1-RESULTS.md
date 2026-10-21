# P1 results: classifier, labelled set, sandboxed rendering, report

Date: 2026-10-22. Everything below comes from runs on this machine. The commands that reproduce it
are listed at the end.

## 1. What was built

| Part | Files | Notes |
|---|---|---|
| Sandboxed Jinja rendering | `tda/render/jinja_ref.py`, `jinja_worker.py`, `sandbox.py` | transformers-compatible `ImmutableSandboxedEnvironment`, run in a subprocess (`python -E -P`) with a 10 s timeout, a 1 MiB output cap and restart on timeout |
| Diff set | `scripts/build_diffset.py`, `labels/pairs/`, `labels/pairs.jsonl` | 52 pairs: 32 real (Qwen2.5 7B library and HF packages, local Qwen2.5-Coder 7B), 20 constructed with one known change each |
| Hand labels | `labels/GUIDE.md`, `labels/labels.jsonl` | written before the classifier existed; not edited since |
| Classifier | `tda/classify.py` | rule-based over a token-level diff, with tool definitions, calls, results, reasoning and content located in each render |
| Audit pipeline | `tda/audit.py`, `tda/mapping.py`, `tda/known_issues.py` | L0, L1 and L3 renders per fixture; pairs L0→L1, L1→L3, L0→L3 |
| Report | `tda/report.py`, `tda/cli.py` | `run.json`, per-model JSON, every render as a file, `report.md`, `cells.csv` |
| Tests | `tests/` | 39 pass (`python -m pytest -q`) |

## 2. Classifier against the hand labels

The rules were tuned on the dev split only. Then the classifier, labels and pairs were hashed
(`runs/p1/frozen.sha256`), and the test split was scored once (`runs/p1/test-score.txt`).

| Split | Pairs | Exact class-set match | Severity agreement |
|---|---|---|---|
| dev | 24 | 23/24 | 24/24 |
| test | 28 | 28/28 | 28/28 |

Per-class precision and recall on test were 1.00 for all 13 classes that occur there.

**The one dev disagreement (`con-14-content-escaped-F10`).**
- The construction replaced `Zürich` with `Zürich` everywhere. That hit the user message and
  also the tool-call arguments.
- The label records `CONTENT` only.
- The classifier reports `CONTENT` + `JSON_SPACING`. The arguments decode to the same JSON, so the
  classifier reads that hunk as an escape-only change.
- It is left as a reported disagreement. The label was not changed.

**How far these numbers reach:**
- The set is small (52 pairs), and one labeller wrote both the labels and the rules.
- Every real pair comes from the Qwen2.5 template family. The test half holds two templates the dev
  half never shows (the HF-converted one and the Coder one), but both are still Qwen2.5.
- The constructed pairs were designed by the same author as the classifier.
- Before these agreement figures appear in the article, a human should review a sample of the
  labels (GUIDE.md says so too). The population run should also add pairs from other template
  families.

**Rule decisions made during dev tuning:**
1. If only whitespace changes inside a tool definition or tool call, the hunk gets the verdict of
   the whole definition or call. It is `JSON_SPACING` only when both sides parse to the same JSON.
   Otherwise it is `TOOL_SCHEMA_NOT_JSON`, `TOOL_SCHEMA` or `TOOL_CALL`.
2. The JSON comparison keeps key order, because a reordered schema is a different prompt. Spacing
   and string escapes are ignored. So escape-only differences in tool JSON count as `JSON_SPACING`
   (minor). GUIDE.md describes that class as spacing only, so the report's method notes say
   "spacing or escapes".

## 3. Pipeline runs

Ollama v0.40.7 (Go helper), fixtures v745406c928e5, classifier `00e9bd5ae2a2` (unchanged since
it was frozen).

**Network reads.** The first online library run made 30 requests and read 14,740,207 bytes; the
user approved these reads on 2026-10-22. Almost all of it is two GGUF headers (7,340,032 bytes each,
header only, no weights). The rest is:
- the Coder library manifests and small layers;
- the Coder upstream `tokenizer_config.json` files;
- one page of Qwen2.5-7B-Instruct commit history, and that repo's `tokenizer_config.json` at the
  commits checked.

Every later run (library rerun, hf, local) made 0 requests. All reads are logged in
`.cache/provenance.jsonl`.

| Run | Package | Selected source | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|---|---|
| `runs/p1-library` | `qwen2.5:7b-instruct` | go_template | material | material | material |
| `runs/p1-library` | `qwen2.5-coder:7b` | go_template | none (12/12 identical) | material | material |
| `runs/p1-library` | `qwen2.5-coder:3b` | go_template | none (12/12 identical) | material | material |
| `runs/p1-hf` | `hf.co/bartowski/Qwen2.5-7B-Instruct-GGUF:Q4_K_M` | go_template | none (12/12 identical) | material | material |
| `runs/p1-local` | the same three library packages, from the local store | go_template | same as library | same | same |

**Headline measure.** All 4 of the 4 packages audited here (3 library, 1 HF) differ materially
from the author's template (L0→L3) on at least one tool-calling fixture. Four packages, all from
one model family, is a pipeline check and not a population result; the article's numbers come from
the population run.

What the classes say (tool fixtures F04–F09):
- **`qwen2.5:7b-instruct`.**
  - L0→L1 is `TOOL_SCHEMA` on F04–F10.
  - The GGUF template is byte-identical to an older revision of the author's template. The newest
    matching commit is `52e20a6` (2024-09-18).
  - Upstream changed the template the next day, in `acbd965` (2024-09-19, "Upload
    ./tokenizer_config.json with huggingface_hub"). 13 commits were checked.
  - So this L0→L1 difference is an upstream update the package predates. Nothing was edited in
    conversion.
  - L1→L3 adds `TOOL_SCHEMA_NOT_JSON` (tool definitions reach the model as Go structs), plus
    `TOOL_CALL` on F07 and F08, and `TOOL_RESULT` on F07.
- **`qwen2.5-coder:7b` and `:3b`.**
  - Their GGUF templates equal the current upstream template, so L0→L1 is identical everywhere.
  - All of their drift is at L1→L3: `TOOL_SCHEMA` and `TOOL_SCHEMA_NOT_JSON` on F04–F10, plus
    `TOOL_CALL` on F07 and F08, and `TOOL_RESULT` on F07.
  - The local store holds the same packages, and the local run gives the same cells as the
    library run.
- **HF package.**
  - The GGUF template matches the author's template on every fixture.
  - The HF-generated Go template drops the default system prompt (`DEFAULT_SYSTEM`) and prints tool
    definitions as Go structs.
- **Known issue.** `TOOL_SCHEMA_NOT_JSON` on the `go_template` path matches
  [ollama/ollama#14601](https://github.com/ollama/ollama/issues/14601). The report flags it as
  already reported, not as a new finding.

**Fidelity cross-check.**
- The pipeline's L3 renders for `qwen2.5:7b-instruct` are byte-identical to the P0 live
  `_debug_render_only` renders on 12/12 fixtures.
- The P0 files had been saved with CRLF line endings. They were compared with the CRs removed;
  the fixtures contain none.
- The pipeline now writes renders byte-exact (LF).

**Not in the headline count:** two locally built models have no upstream mapping, so they get
L1→L3 only.

## 4. Open items

1. **Population mapping.** The parallel session writes `population/mapping.yaml`.
   `tda library|hf --mapping population/mapping.yaml` reads it as is. Its fields are package,
   upstream_repo, upstream_sha, template_file, reason and confidence.
   - The Coder rows in `examples/mapping-p1.yaml` are example rows (confidence medium) until that
     mapping confirms them.
2. **L0 at conversion** is looked up on one page of commit history. A repo with more commits than
   one page holds would need paging; this one had 13.
3. **Paths not rendered offline.** `gguf_chat_template` is emulated in Python and flagged
   approximate until the live tier checks it. `harmony` and `parser`-only packages are marked
   partial.
4. **Human review** of a sample of the 52 labels before agreement figures are published.

## 5. Reproduce

```
python scripts/build_diffset.py                       # pairs (needs the cache and the WSL Go helper)
python scripts/eval_classifier.py --split dev --show-errors
python scripts/eval_classifier.py --split test        # once, after freezing
python -m tda.cli library --mapping examples/mapping-p1.yaml --run-id p1-library   # online once; --offline after
python -m tda.cli hf      --mapping examples/mapping-p1.yaml --offline --run-id p1-hf
python -m tda.cli local   --mapping examples/mapping-p1.yaml --offline --run-id p1-local
python -m tda.cli report runs/p1-library
python -m pytest -q
```
