# Template drift report — p2-hf

Ollama v0.40.7 (Go helper) · tool 0.0.1 · fixtures v745406c928e5 · classifier 00e9bd5ae2a2 · 2026-10-22T04:47:20+0530

## Summary

**5 of 22** audited packages give the model a prompt that differs materially from the author's template (L0→L3) on at least one tool-calling fixture (F04, F05, F06, F07, F08, F09).

Where the difference first appears, among those packages:

- conversion only: 5

| Class (L0→L3, tool fixtures) | Packages |
|---|---|
| `THINKING` | 5 |
| `DEFAULT_SYSTEM` | 2 |
| `TOOL_SCHEMA` | 2 |

Rendered on an approximate path (llama-server Jinja emulated in Python, not validated live): hf.co/CMSManhattan/JiRackUltra_1b:Q4_K_M, hf.co/DavidAU/Qwen3.5-9B-The-Defiant-Fable-Uncensored-Heretic-NEO-IMATRIX-MAX-MTP-GGUF:Q4_K_M, hf.co/DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF:Q4_K_M, hf.co/ggml-org/Qwen3.8-27B-GGUF:Q4_K_M, hf.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF:Q4_K_M, hf.co/ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF:IQ3_S, hf.co/JonathanColetti/Qwen3.8-27B-Uncensored-GGUF:Q4_K_M, hf.co/mradermacher/Ornith-1.5-9B-uncensored-GGUF:Q4_K_M, hf.co/ornith-ai/Ornith-1.0-35B-GGUF:Q4_K_M, hf.co/ornith-ai/Ornith-1.0-9B-GGUF:Q4_K_M, hf.co/ornith-ai/Ornith-1.5-35B-A3B-GGUF:Q4_K_M, hf.co/ornith-ai/Ornith-1.5-397B-GGUF:Q4_K_M, hf.co/ornith-ai/Ornith-1.5-9B-GGUF:Q4_K_M, hf.co/peculiar-ragdoll/Dirk-Qwen3.8-27B-GGUF:Q4_K_M, hf.co/peculiar-ragdoll/Tiel-Coder-35B-A3B-GGUF-MTP:Q4_K_XL, hf.co/prism-ml/Ternary-Bonsai-2-27B-gguf:PQ2_0, hf.co/ukisai/Swift-1.5-Qwen3.8-27B-GSQ-RCO-GGUF:IQ3_S, hf.co/unsloth/gemma-4-12b-it-GGUF:Q4_K_M, hf.co/unsloth/Qwen3.5-4B-GGUF:Q4_K_M, hf.co/unsloth/Qwen3.5-9B-GGUF:Q4_K_M, hf.co/unsloth/Qwen3.6-35B-A3B-GGUF:Q4_K_M, hf.co/unsloth/Qwen3.8-27B-GGUF:Q4_K_M

## Packages

| Package | Source | L0→L1 | L1→L3 | L0→L3 | L0→L3 classes (tool fixtures) | Known |
|---|---|---|---|---|---|---|
| `hf.co/antirez/deepseek-v4.1-flash-gguf:MXFP4` | — | — | — | — | — | — |
| `hf.co/byteshape/Qwen3.8-27B-GGUF:IQ4_XS` | — | — | — | — | — | — |
| `hf.co/cdiamond/Qwen3.8-27B-iMatrix-NVFP4-MTP-GGUF:NVFP4` | — | — | — | — | — | — |
| `hf.co/CMSManhattan/JiRackUltra_1b:Q4_K_M` | gguf_chat_template | material | none | material | THINKING | — |
| `hf.co/DavidAU/Qwen3.5-9B-The-Defiant-Fable-Uncensored-Heretic-NEO-IMATRIX-MAX-MTP-GGUF:Q4_K_M` | gguf_chat_template | none | none | none | — | — |
| `hf.co/DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF:Q4_K_M` | gguf_chat_template | none | none | none | — | — |
| `hf.co/ggml-org/Qwen3.8-27B-GGUF:Q4_K_M` | gguf_chat_template | none | none | none | — | — |
| `hf.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF:Q4_K_M` | gguf_chat_template | none | none | none | — | — |
| `hf.co/ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF:IQ3_S` | gguf_chat_template | none | none | none | — | — |
| `hf.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF:IQ3_S` | — | — | — | — | — | — |
| `hf.co/JonathanColetti/Qwen3.8-27B-Uncensored-GGUF:Q4_K_M` | gguf_chat_template | none | none | none | — | — |
| `hf.co/mradermacher/Ornith-1.5-9B-uncensored-GGUF:Q4_K_M` | gguf_chat_template | none | none | none | — | — |
| `hf.co/mudler/Laguna-XS-2.1-APEX-GGUF:APEX-Balanced` | — | — | — | — | — | — |
| `hf.co/ornith-ai/Ornith-1.0-35B-GGUF:Q4_K_M` | gguf_chat_template | none | none | none | — | — |
| `hf.co/ornith-ai/Ornith-1.0-9B-GGUF:Q4_K_M` | gguf_chat_template | none | none | none | — | — |
| `hf.co/ornith-ai/Ornith-1.5-35B-A3B-GGUF:Q4_K_M` | gguf_chat_template | none | none | none | — | — |
| `hf.co/ornith-ai/Ornith-1.5-397B-GGUF:Q4_K_M` | gguf_chat_template | none | none | none | — | — |
| `hf.co/ornith-ai/Ornith-1.5-9B-GGUF:Q4_K_M` | gguf_chat_template | none | none | none | — | — |
| `hf.co/peculiar-ragdoll/Dirk-Qwen3.8-27B-GGUF:Q4_K_M` | gguf_chat_template | material | none | material | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA | — |
| `hf.co/peculiar-ragdoll/Tiel-Coder-35B-A3B-GGUF-MTP:Q4_K_XL` | gguf_chat_template | material | none | material | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA | — |
| `hf.co/prism-ml/Ternary-Bonsai-2-27B-gguf:PQ2_0` | gguf_chat_template | none | none | none | — | — |
| `hf.co/ukisai/Swift-1.5-Qwen3.8-27B-GSQ-RCO-GGUF:IQ3_S` | gguf_chat_template | none | none | none | — | — |
| `hf.co/unsloth/gemma-4-12b-it-GGUF:Q4_K_M` | gguf_chat_template | none | none | none | — | — |
| `hf.co/unsloth/Qwen3.5-4B-GGUF:Q4_K_M` | gguf_chat_template | material | none | material | THINKING | — |
| `hf.co/unsloth/Qwen3.5-9B-GGUF:Q4_K_M` | gguf_chat_template | material | none | material | THINKING | — |
| `hf.co/unsloth/Qwen3.6-35B-A3B-GGUF:Q4_K_M` | gguf_chat_template | none | none | none | — | — |
| `hf.co/unsloth/Qwen3.8-27B-GGUF:Q4_K_M` | gguf_chat_template | none | none | none | — | — |

### `hf.co/antirez/deepseek-v4.1-flash-gguf:MXFP4`

- L0: deepseek-ai/DeepSeek-V4.1-Flash — Quantisation of DeepSeek-V4.1-Flash (card base_model). DeepSeek ships chat_template.jinja for V4.1, unlike V4. (confidence high)
- Status: skipped — package: HTTPError: HTTP Error 400: Bad Request

### `hf.co/byteshape/Qwen3.8-27B-GGUF:IQ4_XS`

- L0: Qwen/Qwen3.8-27B — Quantisation of Qwen3.8-27B (card base_model). (confidence high)
- Status: skipped — package: HTTPError: HTTP Error 400: Bad Request

### `hf.co/cdiamond/Qwen3.8-27B-iMatrix-NVFP4-MTP-GGUF:NVFP4`

- L0: Qwen/Qwen3.8-27B — Pure quantisation (card: quantized from Qwen/Qwen3.8-27B; name says iMatrix NVFP4, no fine-tune). (confidence high)
- Status: skipped — package: HTTPError: HTTP Error 400: Bad Request

### `hf.co/CMSManhattan/JiRackUltra_1b:Q4_K_M`

- L0: CMSManhattan/JiRackUltra_1b@65ace7d3c9de:chat_template.jinja — The author's own repo holds both the GGUF files and the transformers files (chat_template.jinja, tokenizer_config.json), so L0 and L1 come from the same repo. It also carries chat_template.jinja.bak and a _with_thinking variant; the default chat_template.jinja is used. (confidence medium)
- GGUF template is an older revision of the author's template: newest match c66a229b984e (2026-09-05); changed upstream in 9662105ae912 (2026-09-05, "Initial upload of JiRackTernary Pro 10B   weights (part 2)")
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | THINKING | IDENTICAL | THINKING |
| F02 | THINKING | IDENTICAL | THINKING |
| F03 | THINKING | IDENTICAL | THINKING |
| F04 (tools) | THINKING | IDENTICAL | THINKING |
| F05 (tools) | THINKING | IDENTICAL | THINKING |
| F06 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F07 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F08 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F09 (tools) | THINKING | IDENTICAL | THINKING |
| F10 | IDENTICAL | IDENTICAL | IDENTICAL |
| F11 | THINKING | IDENTICAL | THINKING |
| F12 | THINKING | IDENTICAL | THINKING |

### `hf.co/DavidAU/Qwen3.5-9B-The-Defiant-Fable-Uncensored-Heretic-NEO-IMATRIX-MAX-MTP-GGUF:Q4_K_M`

- L0: DavidAU/Qwen3.5-9B-The-Defiant-Fable-Uncensored-Heretic-NEO-IMATRIX-MAX-MTP@7af0a9c4e221:chat_template.jinja — The GGUF card's base_model is the same author's safetensors repo with the same name. (confidence high)
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F07 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F08 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F09 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F10 | IDENTICAL | IDENTICAL | IDENTICAL |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `hf.co/DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF:Q4_K_M`

- L0: DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NM-DAU@fd6a26869dc5:chat_template.jinja — The GGUF card's base_model is this same-author safetensors repo, but its name differs ('NM-DAU' vs 'NEO-CODER-MAX-MTP'), so the GGUF may be a further variant. (confidence medium)
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F07 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F08 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F09 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F10 | IDENTICAL | IDENTICAL | IDENTICAL |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `hf.co/ggml-org/Qwen3.8-27B-GGUF:Q4_K_M`

- L0: Qwen/Qwen3.8-27B@1d4bf0f2ff60:chat_template.jinja — llama.cpp project's reference quantisation of Qwen3.8-27B. (confidence high)
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F07 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F08 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F09 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F10 | IDENTICAL | IDENTICAL | IDENTICAL |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `hf.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF:Q4_K_M`

- L0: huihui-ai/Huihui-Qwen3.8-27B-abliterated@739e3c5b8984:chat_template.jinja — Same author's safetensors repo with the same name. The GGUF card points at Qwen/Qwen3.8-27B, skipping the abliterated model. (confidence high)
- GGUF template matches none of the 11 upstream revisions checked
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F07 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F08 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F09 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F10 | IDENTICAL | IDENTICAL | IDENTICAL |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `hf.co/ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF:IQ3_S`

- L0: Qwen/Qwen3.8-27B@1d4bf0f2ff60:chat_template.jinja — Pure quantisation (card base_model Qwen/Qwen3.8-27B). (confidence high)
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F07 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F08 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F09 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F10 | IDENTICAL | IDENTICAL | IDENTICAL |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `hf.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF:IQ3_S`

- L0: Qwen/Qwen3.8-Flash-Next — Pure quantisation (card: base_model_relation quantized) of Qwen's post-trained Flash-Next. (confidence high)
- Status: skipped — package: HTTPError: HTTP Error 400: Bad Request

### `hf.co/JonathanColetti/Qwen3.8-27B-Uncensored-GGUF:Q4_K_M`

- L0: JonathanColetti/Qwen3.8-27B-Uncensored@5bb7aa90f0ef:chat_template.jinja — Same author's fine-tune repo (its card: finetune of Qwen3.8-27B). The GGUF repo's card points straight at Qwen/Qwen3.8-27B, skipping the fine-tune, the same base-model quirk P0 found. (confidence medium)
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F07 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F08 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F09 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F10 | IDENTICAL | IDENTICAL | IDENTICAL |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `hf.co/mradermacher/Ornith-1.5-9B-uncensored-GGUF:Q4_K_M`

- L0: junafinity/Ornith-1.5-9B-uncensored@cf512b0b6d71:chat_template.jinja — mradermacher quantises other people's models; the card's base_model is junafinity's fine-tune, whose own card points at ornith-ai/Ornith-1.5-9B. (confidence high)
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F07 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F08 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F09 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F10 | IDENTICAL | IDENTICAL | IDENTICAL |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `hf.co/mudler/Laguna-XS-2.1-APEX-GGUF:APEX-Balanced`

- L0: poolside/Laguna-XS-2.1 — Pure quantisation (card base_model poolside/Laguna-XS-2.1). (confidence high)
- Status: skipped — package: HTTPError: HTTP Error 400: Bad Request

### `hf.co/ornith-ai/Ornith-1.0-35B-GGUF:Q4_K_M`

- L0: ornith-ai/Ornith-1.0-35B@5df2ed3f675c:chat_template.jinja — Same author, same name. (confidence high)
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F07 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F08 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F09 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F10 | IDENTICAL | IDENTICAL | IDENTICAL |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `hf.co/ornith-ai/Ornith-1.0-9B-GGUF:Q4_K_M`

- L0: ornith-ai/Ornith-1.0-9B@83dc1f5e24ef:chat_template.jinja — Same author, same name. (confidence high)
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F07 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F08 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F09 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F10 | IDENTICAL | IDENTICAL | IDENTICAL |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `hf.co/ornith-ai/Ornith-1.5-35B-A3B-GGUF:Q4_K_M`

- L0: ornith-ai/Ornith-1.5-35B-A3B@10fbf86fed7e:chat_template.jinja — Same author, same name; the card sets no base_model. The repo holds two different templates: chat_template.jinja (7536 chars, the file transformers loads first) and a chat_template key in tokenizer_config.json (7764 chars); the GGUF embeds a third (7828 chars). chat_template.jinja is taken as L0, per transformers' load order. (confidence medium)
- GGUF template matches none of the 13 upstream revisions checked
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F07 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F08 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F09 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F10 | IDENTICAL | IDENTICAL | IDENTICAL |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `hf.co/ornith-ai/Ornith-1.5-397B-GGUF:Q4_K_M`

- L0: ornith-ai/Ornith-1.5-397B@8f6cc8a7aea5:chat_template.jinja — Same author, same name. The repo holds two different templates: chat_template.jinja (7594 chars, the file transformers loads first) and a chat_template key in tokenizer_config.json (7756 chars); the GGUF embeds a third (7828 chars). chat_template.jinja is taken as L0, per transformers' load order. (confidence medium)
- GGUF template matches none of the 18 upstream revisions checked
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F07 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F08 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F09 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F10 | IDENTICAL | IDENTICAL | IDENTICAL |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `hf.co/ornith-ai/Ornith-1.5-9B-GGUF:Q4_K_M`

- L0: ornith-ai/Ornith-1.5-9B@489cb97981b8:chat_template.jinja — Same author, same name; the card sets no base_model. The repo holds two different templates: chat_template.jinja (7593 chars, the file transformers loads first) and a chat_template key in tokenizer_config.json (7756 chars); the GGUF embeds a third (7828 chars). chat_template.jinja is taken as L0, per transformers' load order. (confidence medium)
- GGUF template matches none of the 29 upstream revisions checked
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F07 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F08 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F09 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F10 | IDENTICAL | IDENTICAL | IDENTICAL |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `hf.co/peculiar-ragdoll/Dirk-Qwen3.8-27B-GGUF:Q4_K_M`

- L0: Qwen/Qwen3.8-27B@1d4bf0f2ff60:chat_template.jinja — The card says quantized from Qwen/Qwen3.8-27B, but the package has its own name ('Dirk', 'token-efficient agentic coding') and no Dirk safetensors repo exists, so it may be a modified model. If it is a pure quant, Qwen is the template author. (confidence low)
- GGUF template matches none of the 16 upstream revisions checked
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | DEFAULT_SYSTEM | IDENTICAL | DEFAULT_SYSTEM |
| F02 | DEFAULT_SYSTEM | IDENTICAL | DEFAULT_SYSTEM |
| F03 | DEFAULT_SYSTEM | IDENTICAL | DEFAULT_SYSTEM |
| F04 (tools) | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA | IDENTICAL | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA |
| F05 (tools) | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA | IDENTICAL | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA |
| F06 (tools) | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA | IDENTICAL | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA |
| F07 (tools) | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA | IDENTICAL | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA |
| F08 (tools) | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA | IDENTICAL | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA |
| F09 (tools) | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA | IDENTICAL | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA |
| F10 | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA | IDENTICAL | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA |
| F11 | DEFAULT_SYSTEM | IDENTICAL | DEFAULT_SYSTEM |
| F12 | DEFAULT_SYSTEM | IDENTICAL | DEFAULT_SYSTEM |

### `hf.co/peculiar-ragdoll/Tiel-Coder-35B-A3B-GGUF-MTP:Q4_K_XL`

- L0: ornith-ai/Ornith-1.5-35B-A3B@10fbf86fed7e:chat_template.jinja — The card says quantized from ornith-ai/Ornith-1.5-35B-A3B, but the package has its own name ('Tiel-Coder', 'token-efficient agentic coding') and no Tiel-Coder safetensors repo exists, so it may be a modified model. If it is a pure quant, Ornith is the template author. (confidence low)
- GGUF template matches none of the 13 upstream revisions checked
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | DEFAULT_SYSTEM | IDENTICAL | DEFAULT_SYSTEM |
| F02 | DEFAULT_SYSTEM | IDENTICAL | DEFAULT_SYSTEM |
| F03 | DEFAULT_SYSTEM | IDENTICAL | DEFAULT_SYSTEM |
| F04 (tools) | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA | IDENTICAL | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA |
| F05 (tools) | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA | IDENTICAL | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA |
| F06 (tools) | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA | IDENTICAL | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA |
| F07 (tools) | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA | IDENTICAL | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA |
| F08 (tools) | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA | IDENTICAL | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA |
| F09 (tools) | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA | IDENTICAL | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA |
| F10 | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA | IDENTICAL | DEFAULT_SYSTEM, THINKING, TOOL_SCHEMA |
| F11 | DEFAULT_SYSTEM | IDENTICAL | DEFAULT_SYSTEM |
| F12 | DEFAULT_SYSTEM | IDENTICAL | DEFAULT_SYSTEM |

### `hf.co/prism-ml/Ternary-Bonsai-2-27B-gguf:PQ2_0`

- L0: Qwen/Qwen3.8-27B@1d4bf0f2ff60:chat_template.jinja — The card lists Qwen/Qwen3.8-27B as the quantized base and prism-ml publishes no unquantised Bonsai repo (prism-ml/Ternary-Bonsai-2-27B does not exist). Ternary conversion may involve retraining, so Qwen is the template author only if prism-ml kept the template. (confidence medium)
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F07 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F08 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F09 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F10 | IDENTICAL | IDENTICAL | IDENTICAL |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `hf.co/ukisai/Swift-1.5-Qwen3.8-27B-GSQ-RCO-GGUF:IQ3_S`

- L0: ukisai/Swift-1.5-Qwen3.8-27b@b4c84d42903a:chat_template.jinja — Same author's fine-tune repo (card base_model; that repo's card: finetune of Qwen3.8-27B). (confidence high)
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F07 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F08 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F09 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F10 | IDENTICAL | IDENTICAL | IDENTICAL |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `hf.co/unsloth/gemma-4-12b-it-GGUF:Q4_K_M`

- L0: google/gemma-4-12B-it@707f0a3b8a3c:chat_template.jinja — Quantisation of Google's 12B instruct model (card base_model). (confidence high)
- GGUF template matches none of the 7 upstream revisions checked
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F07 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F08 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F09 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F10 | IDENTICAL | IDENTICAL | IDENTICAL |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `hf.co/unsloth/Qwen3.5-4B-GGUF:Q4_K_M`

- L0: Qwen/Qwen3.5-4B@851bf6e806ef:chat_template.jinja — Quantisation of Qwen3.5-4B (card base_model). (confidence high)
- GGUF template matches none of the 5 upstream revisions checked
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | THINKING | IDENTICAL | THINKING |
| F02 | THINKING | IDENTICAL | THINKING |
| F03 | THINKING | IDENTICAL | THINKING |
| F04 (tools) | THINKING | IDENTICAL | THINKING |
| F05 (tools) | THINKING | IDENTICAL | THINKING |
| F06 (tools) | THINKING | IDENTICAL | THINKING |
| F07 (tools) | THINKING | IDENTICAL | THINKING |
| F08 (tools) | THINKING | IDENTICAL | THINKING |
| F09 (tools) | THINKING | IDENTICAL | THINKING |
| F10 | THINKING | IDENTICAL | THINKING |
| F11 | THINKING | IDENTICAL | THINKING |
| F12 | THINKING | IDENTICAL | THINKING |

### `hf.co/unsloth/Qwen3.5-9B-GGUF:Q4_K_M`

- L0: Qwen/Qwen3.5-9B@c20223623576:chat_template.jinja — Quantisation of Qwen3.5-9B (card base_model). (confidence high)
- GGUF template matches none of the 9 upstream revisions checked
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | THINKING | IDENTICAL | THINKING |
| F02 | THINKING | IDENTICAL | THINKING |
| F03 | THINKING | IDENTICAL | THINKING |
| F04 (tools) | THINKING | IDENTICAL | THINKING |
| F05 (tools) | THINKING | IDENTICAL | THINKING |
| F06 (tools) | THINKING | IDENTICAL | THINKING |
| F07 (tools) | THINKING | IDENTICAL | THINKING |
| F08 (tools) | THINKING | IDENTICAL | THINKING |
| F09 (tools) | THINKING | IDENTICAL | THINKING |
| F10 | THINKING | IDENTICAL | THINKING |
| F11 | THINKING | IDENTICAL | THINKING |
| F12 | THINKING | IDENTICAL | THINKING |

### `hf.co/unsloth/Qwen3.6-35B-A3B-GGUF:Q4_K_M`

- L0: Qwen/Qwen3.6-35B-A3B@995ad96eacd9:chat_template.jinja — Quantisation of Qwen3.6-35B-A3B (card base_model). (confidence high)
- GGUF template matches none of the 3 upstream revisions checked
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F07 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F08 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F09 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F10 | IDENTICAL | IDENTICAL | IDENTICAL |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `hf.co/unsloth/Qwen3.8-27B-GGUF:Q4_K_M`

- L0: Qwen/Qwen3.8-27B@1d4bf0f2ff60:chat_template.jinja — Quantisation of Qwen3.8-27B (card base_model). unsloth is known to patch templates, so L1 may differ from L0 by design. (confidence high)
- GGUF template matches none of the 16 upstream revisions checked
- Ollama selects `gguf_chat_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F07 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F08 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F09 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F10 | IDENTICAL | IDENTICAL | IDENTICAL |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

## Not in the headline count

- `hf.co/antirez/deepseek-v4.1-flash-gguf:MXFP4`: skipped — package: HTTPError: HTTP Error 400: Bad Request
- `hf.co/byteshape/Qwen3.8-27B-GGUF:IQ4_XS`: skipped — package: HTTPError: HTTP Error 400: Bad Request
- `hf.co/cdiamond/Qwen3.8-27B-iMatrix-NVFP4-MTP-GGUF:NVFP4`: skipped — package: HTTPError: HTTP Error 400: Bad Request
- `hf.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF:IQ3_S`: skipped — package: HTTPError: HTTP Error 400: Bad Request
- `hf.co/mudler/Laguna-XS-2.1-APEX-GGUF:APEX-Balanced`: skipped — package: HTTPError: HTTP Error 400: Bad Request

## Excluded by the mapping

- `hf.co/HauhauCS/Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-MTP-GGUF:Q4_K_P`: A weight-edited (uncensored) Qwen3.8-27B published only as GGUF: HauhauCS has no safetensors repo for it, so there is no author template outside the GGUF. If re-included, the candidate L0 is Qwen/Qwen3.8-27B (the card's base).
- `hf.co/SC117/Qwen3.8-Flash-Next-GSQ-RCO-abliterated-GGUF:IQ3_S`: An abliterated (weight-edited, 'tensor-transplant') build made from another GGUF repo and published only as GGUF; there is no author template outside the GGUF. If re-included, the candidate L0 is Qwen/Qwen3.8-Flash-Next.
- `hf.co/antirez/deepseek-v4-gguf:Q4K-experts`: deepseek-ai/DeepSeek-V4-Flash publishes its prompt format as Python (encoding/encoding_dsv4.py with test vectors), not as a Jinja chat template, so there is no author template to render. The chat template inside the GGUF was written by the quantiser.

## Method notes

- Severity: `none` (whitespace, BOS, date), `minor` (same JSON, different spacing or escapes), `material` (everything else). Classes are defined in `labels/GUIDE.md`.
- L0 and L1 are rendered with the L0 special tokens, so L0→L1 compares template text only.
- A fixture the reference side cannot render is marked `REFERENCE_ERROR` and is not counted as drift.
- Sources read: 345 URLs (listed in run.json); network requests this run: 28.
