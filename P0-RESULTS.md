# P0 spike results (2026-10-22)

One model, end to end: `qwen2.5:7b-instruct` from the Ollama library, and
`hf.co/bartowski/Qwen2.5-7B-Instruct-GGUF:Q4_K_M`, against the author's template at
`Qwen/Qwen2.5-7B-Instruct@a09a35458c70`. Twelve fixtures (`tda/fixtures/fixtures.json`, v`745406c928e5`).
Reproduce: `python scripts/p0_spike.py --offline --live http://127.0.0.1:11500`.

## What works

| Piece | Result |
|---|---|
| GGUF header reader | Reads all 5 local models and both remote files. Remote reads use 3 range requests (7.3 MB) per file; no weights fetched |
| Registry + hf.co + upstream collectors | 15 requests, 14.7 MB for the whole example; offline re-runs make 0 requests |
| Selection port | Passes all 9 of Ollama v0.40.7's own `TestGetModelTemplateMetadata` cases. Predicted `go_template` for qwen2.5; live `/api/show` says `go_template` |
| Go helper (`tda-render`, Ollama v0.40.7 code) | Offline renders equal the live server's `_debug_render_only` output on **12/12** fixtures, byte for byte |
| Isolated live instance | Linux Ollama v0.40.7 in WSL on 127.0.0.1:11500 with its own store; qwen2.5 blobs copied in and checksum-verified |

## What the example shows (qwen2.5:7b-instruct, live Ollama v0.40.7 vs the author's template)

Fixtures F01–F03 and F11–F12 (no tools) render identically. Every tool fixture (F04–F10) differs:

1. **Tool definitions are printed in Go struct syntax, not JSON.** For example
   `{"type": "function", "function": {get_weather Current weather for a city {object <nil> <nil> [city] {...}}}}`.
   The cause is in `template/template.go`: `templateToolFunction` has no `String()` method. This
   is **already reported**: [ollama/ollama#14601](https://github.com/ollama/ollama/issues/14601),
   open since 2026-03-03. Fix PRs [ollama/ollama#18391](https://github.com/ollama/ollama/pull/18391)
   and [ollama/ollama#18318](https://github.com/ollama/ollama/pull/18318) are open; v0.40.8 and
   `main` are unchanged. The audit's job is to measure how many popular packages it reaches, not to
   claim it.
2. **Parallel tool calls (F07).** The author's template gives each call its own `<tool_call>` block
   and puts consecutive tool results in one user turn. Ollama's puts both calls in one block and
   gives each result its own turn.
3. **Text plus a tool call (F08).** Ollama keeps the text and drops the tool call; the author's
   template keeps both.
4. **Argument spacing.** Ollama writes compact JSON (`{"city":"Oslo"}`); the author's template uses
   `tojson` spacing (`{"city": "Oslo"}`).

Other layer findings:
- **The GGUF inside Ollama's own package embeds an older revision of the author's template.** It
  differs by 2 bytes: `{{"name": ...}}` where upstream now has `{"name": ...}`. bartowski's GGUF
  matches current upstream exactly. So **L0 needs two versions: current, and as of the GGUF's
  creation.**
- **HF's `hf.co` package** gets a different Go template, with a fill-in-the-middle branch, and no
  SYSTEM layer. So F01, F03, F11 and F12 differ from the author's template on the default system
  prompt alone.
- The GGUF's `general.base_model.0.repo_url` points at the base `Qwen/Qwen2.5-7B`, not the Instruct
  repo, which confirms the mapping has to be done by hand.

## Changes to the design from P0

- **L0 is pinned twice:** the current commit, and the commit in effect when the GGUF was made
  (matched by template text against upstream history).
- **Every material drift is checked against open Ollama and HF issues before it is reported.** The
  report cites the issue and never presents a known issue as new.
- **The tool-definition class needs a sub-class for "not JSON at all"**, separate from "different
  JSON layout".
- **The Go helper is validated for the `go_template` path.** The `renderer` and
  `gguf_chat_template` paths still need their own live checks in P2.

## Downloads made (all approved, checksums verified where published)

- **Metadata:** 14.7 MB.
- **Python:** jinja2 3.1.6 and markupsafe 3.0.4, about 150 KB.
- **Go:** go1.26.10 at 66.9 MB, plus 44 MB of Go modules.
- **Ollama:** the v0.40.7 Linux tarball at 1,505.6 MB (since unpacked and deleted), plus the apt
  package zstd.
- **Disk:** the qwen2.5 weights (4.7 GB) were copied, not downloaded, into the isolated store.
