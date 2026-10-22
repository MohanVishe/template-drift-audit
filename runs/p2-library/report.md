# Template drift report — p2-library

Ollama v0.40.7 (Go helper) · tool 0.0.1 · fixtures v745406c928e5 · classifier 00e9bd5ae2a2 · 2026-10-22T04:31:36+0530

## Summary

**32 of 44** audited packages give the model a prompt that differs materially from the author's template (L0→L3) on at least one tool-calling fixture (F04, F05, F06, F07, F08, F09).

Where the difference first appears, among those packages:

- conversion and packaging: 6
- neither alone: 2
- packaging only: 24

| Class (L0→L3, tool fixtures) | Packages |
|---|---|
| `TOOL_RESULT` | 20 |
| `TOOL_SCHEMA` | 12 |
| `DEFAULT_SYSTEM` | 10 |
| `TOOL_CALL` | 10 |
| `OTHER` | 8 |
| `TOOLS_DROPPED` | 7 |
| `CONTENT` | 4 |
| `STRUCTURE` | 3 |
| `TOOL_SCHEMA_NOT_JSON` | 3 |

Already reported upstream: ollama/ollama#14601. Findings matching these are not new.

Rendered on an approximate path (llama-server Jinja emulated in Python, not validated live): deepseek-r1:latest, deepseek-v3:latest, llama3.2-vision:latest

## Packages

| Package | Source | L0→L1 | L1→L3 | L0→L3 | L0→L3 classes (tool fixtures) | Known |
|---|---|---|---|---|---|---|
| `codegemma:latest` | go_template | — | — | none | BOS, REFERENCE_ERROR | — |
| `codellama:latest` | go_template | — | — | material | BOS, OTHER, REFERENCE_ERROR, WHITESPACE | — |
| `deepseek-coder-v2:latest` | go_template | none | material | material | OTHER, WHITESPACE | — |
| `deepseek-coder:latest` | go_template | none | material | material | DEFAULT_SYSTEM, OTHER, TOOL_RESULT, WHITESPACE | — |
| `deepseek-r1:latest` | gguf_chat_template | none | none | none | BOTH_ERROR | — |
| `deepseek-v3:latest` | gguf_chat_template | none | none | none | — | — |
| `dolphin3:latest` | go_template | none | material | material | DEFAULT_SYSTEM | — |
| `falcon3:latest` | go_template | material | material | material | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT, WHITESPACE | — |
| `gemma2:latest` | go_template | none | none | none | BOS, REFERENCE_ERROR | — |
| `gemma3:latest` | go_template | none | material | material | BOS, REFERENCE_ERROR, STRUCTURE | — |
| `gemma4:latest` | renderer_parser | none | none | none | — | — |
| `gemma:latest` | go_template | none | none | none | BOS, REFERENCE_ERROR | — |
| `glm-ocr:latest` | renderer_parser | — | — | material | TOOL_CALL, TOOL_SCHEMA, WHITESPACE | — |
| `gpt-oss:latest` | harmony | — | — | — | — | — |
| `granite3.1-moe:latest` | go_template | none | material | material | DATE, OTHER, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE | — |
| `llama2:latest` | go_template | none | material | material | BOS, OTHER, REFERENCE_ERROR, WHITESPACE | — |
| `llama3.1:latest` | go_template | none | material | material | BOS, CONTENT, DEFAULT_SYSTEM, JSON_SPACING, OTHER, REFERENCE_ERROR, TOOLS_DROPPED, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE | — |
| `llama3.2-vision:latest` | gguf_chat_template | none | none | none | BOTH_ERROR | — |
| `llama3.2:latest` | go_template | none | material | material | BOS, CONTENT, DATE, DEFAULT_SYSTEM, JSON_SPACING, OTHER, REFERENCE_ERROR, TOOLS_DROPPED, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE | — |
| `llama3.3:latest` | go_template | none | material | material | BOS, CONTENT, DEFAULT_SYSTEM, JSON_SPACING, OTHER, REFERENCE_ERROR, TOOLS_DROPPED, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE | — |
| `llama3:latest` | go_template | none | material | material | BOS, TOOL_RESULT | — |
| `llava:latest` | go_template | none | material | material | BOS, REFERENCE_ERROR | — |
| `minicpm-v:latest` | go_template | none | material | material | DEFAULT_SYSTEM | — |
| `mistral-nemo:latest` | go_template | material | material | material | BOS, REFERENCE_ERROR, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE | — |
| `mistral-small:latest` | go_template | none | material | material | BOS, DATE, REFERENCE_ERROR, TOOLS_DROPPED, WHITESPACE | — |
| `mistral:latest` | go_template | material | material | material | BOS, REFERENCE_ERROR, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE | — |
| `mixtral:latest` | go_template | none | material | material | BOS, REFERENCE_ERROR, WHITESPACE | — |
| `nemotron-3-super:latest` | renderer_parser | — | — | none | — | — |
| `olmo2:latest` | go_template | none | material | material | BOS, DEFAULT_SYSTEM, TOOL_RESULT, WHITESPACE | — |
| `phi3:latest` | go_template | none | material | material | STRUCTURE, TOOL_RESULT, WHITESPACE | — |
| `phi4:latest` | go_template | material | material | material | TOOL_RESULT, WHITESPACE | — |
| `qwen2.5-coder:latest` | go_template | none | material | material | JSON_SPACING, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON | ollama/ollama#14601 |
| `qwen2.5:latest` | go_template | material | material | material | JSON_SPACING, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA_NOT_JSON | ollama/ollama#14601 |
| `qwen2.5vl:latest` | go_template | none | material | material | TOOL_RESULT | — |
| `qwen2:latest` | go_template | none | material | material | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT | — |
| `qwen3-coder:latest` | renderer_parser | material | material | none | WHITESPACE | — |
| `qwen3-vl:latest` | renderer_parser | none | material | material | TOOL_SCHEMA | — |
| `qwen3.5:latest` | renderer_parser | none | material | material | TOOL_SCHEMA | — |
| `qwen3.6:latest` | renderer_parser | none | material | material | TOOL_SCHEMA | — |
| `qwen3.8:latest` | renderer_parser | none | material | material | TOOL_SCHEMA | — |
| `qwen3:latest` | go_template | none | material | material | JSON_SPACING, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA_NOT_JSON, WHITESPACE | ollama/ollama#14601 |
| `qwen:latest` | go_template | material | material | material | DEFAULT_SYSTEM, TOOL_RESULT, WHITESPACE | — |
| `smollm2:latest` | go_template | none | material | material | CONTENT, DEFAULT_SYSTEM, TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT | — |
| `tinyllama:latest` | go_template | none | material | material | DEFAULT_SYSTEM, STRUCTURE, TOOL_RESULT | — |
| `translategemma:latest` | go_template | — | — | n/a | REFERENCE_ERROR | — |

### `codegemma:latest`

- L0: google/codegemma-1.1-7b-it@9523c8dbf32b:api:tokenizer_config.json — latest = 7b-instruct-v1.1-q4_0, so CodeGemma 1.1. (confidence high)
- Ollama selects `go_template`
- Render errors: L0.F02: System role not supported; L0.F05: System role not supported; L0.F06: Conversation roles must alternate user/assistant/user/assistant/...; L0.F07: Conversation roles must alternate user/assistant/user/assistant/...; L0.F08: Conversation roles must alternate user/assistant/user/assistant/...; L0.F09: Conversation roles must alternate user/assistant/user/assistant/...; L0.F10: Conversation roles must alternate user/assistant/user/assistant/...

| Fixture | L0→L3 |
|---|---|
| F01 | BOS |
| F02 | REFERENCE_ERROR |
| F03 | BOS |
| F04 (tools) | BOS |
| F05 (tools) | REFERENCE_ERROR |
| F06 (tools) | REFERENCE_ERROR |
| F07 (tools) | REFERENCE_ERROR |
| F08 (tools) | REFERENCE_ERROR |
| F09 (tools) | REFERENCE_ERROR |
| F10 | REFERENCE_ERROR |
| F11 | BOS |
| F12 | BOS |

### `codellama:latest`

- L0: codellama/CodeLlama-7b-Instruct-hf@22cb240e0292:tokenizer_config.json — latest = 7b-instruct-q4_0. Meta publishes this model in two orgs: codellama/ (the original transformers release, ungated) and meta-llama/CodeLlama-7b-Instruct-hf (gated); codellama/ chosen as the original. (confidence medium)
- Ollama selects `go_template`
- Render errors: L0.F06: Conversation roles must alternate user/assistant/user/assistant/...; L0.F07: Conversation roles must alternate user/assistant/user/assistant/...; L0.F08: Conversation roles must alternate user/assistant/user/assistant/...; L0.F09: Conversation roles must alternate user/assistant/user/assistant/...; L0.F10: Conversation roles must alternate user/assistant/user/assistant/...

| Fixture | L0→L3 |
|---|---|
| F01 | BOS, OTHER, WHITESPACE |
| F02 | BOS, WHITESPACE |
| F03 | BOS, OTHER, STRUCTURE, WHITESPACE |
| F04 (tools) | BOS, OTHER, WHITESPACE |
| F05 (tools) | BOS, WHITESPACE |
| F06 (tools) | REFERENCE_ERROR |
| F07 (tools) | REFERENCE_ERROR |
| F08 (tools) | REFERENCE_ERROR |
| F09 (tools) | REFERENCE_ERROR |
| F10 | REFERENCE_ERROR |
| F11 | BOS, OTHER, STRUCTURE, WHITESPACE |
| F12 | BOS, OTHER, WHITESPACE |

### `deepseek-coder-v2:latest`

- L0: deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct@e434a23f91ba:tokenizer_config.json — latest = 16b-lite-instruct-q4_0. (confidence high)
- Ollama selects `go_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | WHITESPACE | WHITESPACE |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | WHITESPACE | WHITESPACE |
| F06 (tools) | IDENTICAL | OTHER | OTHER |
| F07 (tools) | IDENTICAL | OTHER | OTHER |
| F08 (tools) | IDENTICAL | OTHER | OTHER |
| F09 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F10 | IDENTICAL | OTHER | OTHER |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `deepseek-coder:latest`

- L0: deepseek-ai/deepseek-coder-1.3b-instruct@e063262dac83:tokenizer_config.json — latest = 1.3b-instruct-q4_0. (confidence high)
- Ollama selects `go_template` (SYSTEM layer present)

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F02 | IDENTICAL | OTHER, WHITESPACE | OTHER, WHITESPACE |
| F03 | IDENTICAL | DEFAULT_SYSTEM, STRUCTURE | DEFAULT_SYSTEM, STRUCTURE |
| F04 (tools) | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F05 (tools) | IDENTICAL | OTHER, WHITESPACE | OTHER, WHITESPACE |
| F06 (tools) | IDENTICAL | DEFAULT_SYSTEM, TOOL_RESULT | DEFAULT_SYSTEM, TOOL_RESULT |
| F07 (tools) | IDENTICAL | DEFAULT_SYSTEM, TOOL_RESULT | DEFAULT_SYSTEM, TOOL_RESULT |
| F08 (tools) | IDENTICAL | DEFAULT_SYSTEM, TOOL_RESULT | DEFAULT_SYSTEM, TOOL_RESULT |
| F09 (tools) | IDENTICAL | DEFAULT_SYSTEM, TOOL_RESULT | DEFAULT_SYSTEM, TOOL_RESULT |
| F10 | IDENTICAL | DEFAULT_SYSTEM, TOOL_RESULT | DEFAULT_SYSTEM, TOOL_RESULT |
| F11 | IDENTICAL | DEFAULT_SYSTEM, STRUCTURE | DEFAULT_SYSTEM, STRUCTURE |
| F12 | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |

### `deepseek-r1:latest`

- L0: deepseek-ai/DeepSeek-R1-0528-Qwen3-8B@6e8885a6ff5c:tokenizer_config.json — latest = 8b-0528-qwen3-q4_K_M, DeepSeek's R1-0528 distill into Qwen3-8B, so DeepSeek's repo for it, not Qwen's. (confidence high)
- Ollama selects `gguf_chat_template`
- Render errors: L0.F06: TypeError: can only concatenate str (not "dict") to str; L0.F07: TypeError: can only concatenate str (not "dict") to str; L0.F08: TypeError: can only concatenate str (not "dict") to str; L0.F09: TypeError: can only concatenate str (not "dict") to str; L0.F10: TypeError: can only concatenate str (not "dict") to str; L1.F06: TypeError: can only concatenate str (not "dict") to str; L1.F07: TypeError: can only concatenate str (not "dict") to str; L1.F08: TypeError: can only concatenate str (not "dict") to str; L1.F09: TypeError: can only concatenate str (not "dict") to str; L1.F10: TypeError: can only concatenate str (not "dict") to str; L3.F06: TypeError: can only concatenate str (not "dict") to str; L3.F07: TypeError: can only concatenate str (not "dict") to str; L3.F08: TypeError: can only concatenate str (not "dict") to str; L3.F09: TypeError: can only concatenate str (not "dict") to str; L3.F10: TypeError: can only concatenate str (not "dict") to str

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | BOTH_ERROR | BOTH_ERROR | BOTH_ERROR |
| F07 (tools) | BOTH_ERROR | BOTH_ERROR | BOTH_ERROR |
| F08 (tools) | BOTH_ERROR | BOTH_ERROR | BOTH_ERROR |
| F09 (tools) | BOTH_ERROR | BOTH_ERROR | BOTH_ERROR |
| F10 | BOTH_ERROR | BOTH_ERROR | BOTH_ERROR |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `deepseek-v3:latest`

- L0: deepseek-ai/DeepSeek-V3@e815299b0bcb:tokenizer_config.json — latest = 671b-q4_K_M. Package last updated 2025-01-13, before DeepSeek-V3-0324 existed, so the original V3 repo; that repo was itself modified on 2025-03-27, after the package. (confidence medium)
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

### `dolphin3:latest`

- L0: dphn/Dolphin3.0-Llama3.1-8B@f065677950df:tokenizer_config.json — latest = 8b-llama3.1-q4_K_M. cognitivecomputations/Dolphin3.0-Llama3.1-8B now redirects to dphn/. (confidence high)
- Ollama selects `go_template` (SYSTEM layer present)

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F04 (tools) | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F07 (tools) | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F08 (tools) | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F09 (tools) | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F10 | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F11 | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F12 | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |

### `falcon3:latest`

- L0: tiiuae/Falcon3-7B-Instruct@1e57a0ecd176:tokenizer_config.json — latest = 7b-instruct-q4_K_M. (confidence high)
- GGUF template is an older revision of the author's template: newest match 21b3491479da (2024-12-17); changed upstream in 0839f792501b (2024-12-18, "fix chat_template for tool use (#7)")
- Ollama selects `go_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | WHITESPACE | WHITESPACE |
| F02 | IDENTICAL | WHITESPACE | WHITESPACE |
| F03 | IDENTICAL | STRUCTURE, WHITESPACE | STRUCTURE, WHITESPACE |
| F04 (tools) | TOOLS_DROPPED | WHITESPACE | TOOLS_DROPPED, WHITESPACE |
| F05 (tools) | TOOLS_DROPPED | WHITESPACE | TOOLS_DROPPED, WHITESPACE |
| F06 (tools) | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT | TOOL_RESULT | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT |
| F07 (tools) | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT | TOOL_RESULT | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT |
| F08 (tools) | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT | TOOL_RESULT | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT |
| F09 (tools) | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT | TOOL_RESULT, WHITESPACE | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT, WHITESPACE |
| F10 | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT | TOOL_RESULT | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT |
| F11 | IDENTICAL | STRUCTURE, WHITESPACE | STRUCTURE, WHITESPACE |
| F12 | IDENTICAL | WHITESPACE | WHITESPACE |

### `gemma2:latest`

- L0: google/gemma-2-9b-it@11c9b309abf7:api:tokenizer_config.json — latest = 9b-instruct-q4_0. (confidence high)
- Ollama selects `go_template`
- Render errors: L0.F02: System role not supported; L0.F05: System role not supported; L0.F06: Conversation roles must alternate user/assistant/user/assistant/...; L0.F07: Conversation roles must alternate user/assistant/user/assistant/...; L0.F08: Conversation roles must alternate user/assistant/user/assistant/...; L0.F09: Conversation roles must alternate user/assistant/user/assistant/...; L0.F10: Conversation roles must alternate user/assistant/user/assistant/...; L1.F02: System role not supported; L1.F05: System role not supported; L1.F06: Conversation roles must alternate user/assistant/user/assistant/...; L1.F07: Conversation roles must alternate user/assistant/user/assistant/...; L1.F08: Conversation roles must alternate user/assistant/user/assistant/...; L1.F09: Conversation roles must alternate user/assistant/user/assistant/...; L1.F10: Conversation roles must alternate user/assistant/user/assistant/...

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | BOS | BOS |
| F02 | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F03 | IDENTICAL | BOS | BOS |
| F04 (tools) | IDENTICAL | BOS | BOS |
| F05 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F06 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F07 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F08 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F09 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F10 | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F11 | IDENTICAL | BOS | BOS |
| F12 | IDENTICAL | BOS | BOS |

### `gemma3:latest`

- L0: google/gemma-3-4b-it@093f9f388b31:api:tokenizer_config.json — latest = 4b-it-q4_K_M. (confidence high)
- Ollama selects `go_template`
- Render errors: L0.F06: Conversation roles must alternate user/assistant/user/assistant/...; L0.F07: Conversation roles must alternate user/assistant/user/assistant/...; L0.F08: Conversation roles must alternate user/assistant/user/assistant/...; L0.F09: Conversation roles must alternate user/assistant/user/assistant/...; L0.F10: Conversation roles must alternate user/assistant/user/assistant/...; L1.F06: Conversation roles must alternate user/assistant/user/assistant/...; L1.F07: Conversation roles must alternate user/assistant/user/assistant/...; L1.F08: Conversation roles must alternate user/assistant/user/assistant/...; L1.F09: Conversation roles must alternate user/assistant/user/assistant/...; L1.F10: Conversation roles must alternate user/assistant/user/assistant/...

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | BOS | BOS |
| F02 | IDENTICAL | BOS, STRUCTURE | BOS, STRUCTURE |
| F03 | IDENTICAL | BOS | BOS |
| F04 (tools) | IDENTICAL | BOS | BOS |
| F05 (tools) | IDENTICAL | BOS, STRUCTURE | BOS, STRUCTURE |
| F06 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F07 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F08 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F09 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F10 | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F11 | IDENTICAL | BOS | BOS |
| F12 | IDENTICAL | BOS | BOS |

### `gemma4:latest`

- L0: google/gemma-4-E4B-it@ee0ef6023621:chat_template.jinja — latest = e4b, which shares its digest with no -it-q4_K_M or -it-qat tag, so the exact build is not visible from the tags page. Google's E4B instruct repo is the only E4B chat model; google/gemma-4-E4B-it-qat-q4_0-unquantized is the alternative if latest is the QAT build. (confidence medium)
- Ollama selects `renderer_parser`

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

### `gemma:latest`

- L0: google/gemma-1.1-7b-it@065a528791af:api:tokenizer_config.json — latest = 7b-instruct-v1.1-q4_0, so Gemma 1.1, not the original gemma-7b-it. (confidence high)
- Ollama selects `go_template`
- Render errors: L0.F02: System role not supported; L0.F05: System role not supported; L0.F06: Conversation roles must alternate user/assistant/user/assistant/...; L0.F07: Conversation roles must alternate user/assistant/user/assistant/...; L0.F08: Conversation roles must alternate user/assistant/user/assistant/...; L0.F09: Conversation roles must alternate user/assistant/user/assistant/...; L0.F10: Conversation roles must alternate user/assistant/user/assistant/...; L1.F02: System role not supported; L1.F05: System role not supported; L1.F06: Conversation roles must alternate user/assistant/user/assistant/...; L1.F07: Conversation roles must alternate user/assistant/user/assistant/...; L1.F08: Conversation roles must alternate user/assistant/user/assistant/...; L1.F09: Conversation roles must alternate user/assistant/user/assistant/...; L1.F10: Conversation roles must alternate user/assistant/user/assistant/...

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | BOS | BOS |
| F02 | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F03 | IDENTICAL | BOS | BOS |
| F04 (tools) | IDENTICAL | BOS | BOS |
| F05 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F06 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F07 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F08 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F09 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F10 | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F11 | IDENTICAL | BOS | BOS |
| F12 | IDENTICAL | BOS | BOS |

### `glm-ocr:latest`

- L0: zai-org/GLM-OCR@2e85a62840cc:chat_template.jinja — latest = bf16; Z.ai's only GLM-OCR repo. An OCR model, kept because the population rule excludes embedding models only. (confidence high)
- Ollama selects `renderer_parser`

| Fixture | L0→L3 |
|---|---|
| F01 | IDENTICAL |
| F02 | WHITESPACE |
| F03 | WHITESPACE |
| F04 (tools) | TOOL_SCHEMA, WHITESPACE |
| F05 (tools) | TOOL_SCHEMA, WHITESPACE |
| F06 (tools) | TOOL_CALL, TOOL_SCHEMA, WHITESPACE |
| F07 (tools) | TOOL_CALL, TOOL_SCHEMA, WHITESPACE |
| F08 (tools) | TOOL_CALL, TOOL_SCHEMA, WHITESPACE |
| F09 (tools) | TOOL_CALL, TOOL_SCHEMA, WHITESPACE |
| F10 | TOOL_CALL, TOOL_SCHEMA, WHITESPACE |
| F11 | THINKING, WHITESPACE |
| F12 | IDENTICAL |

### `gpt-oss:latest`

- L0: openai/gpt-oss-20b@6cee5e81ee83:chat_template.jinja — latest = 20b. (confidence high)
- Ollama selects `harmony`
- Status: partial — L3 source harmony not rendered offline

### `granite3.1-moe:latest`

- L0: ibm-granite/granite-3.1-3b-a800m-instruct@a02780686e08:tokenizer_config.json — latest = 3b-instruct-q4_K_M. (confidence high)
- Ollama selects `go_template` (SYSTEM layer present)

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | DATE, DEFAULT_SYSTEM | DATE, DEFAULT_SYSTEM |
| F02 | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F03 | IDENTICAL | DATE, DEFAULT_SYSTEM | DATE, DEFAULT_SYSTEM |
| F04 (tools) | IDENTICAL | DATE, OTHER, TOOL_SCHEMA, WHITESPACE | DATE, OTHER, TOOL_SCHEMA, WHITESPACE |
| F05 (tools) | IDENTICAL | TOOL_SCHEMA, WHITESPACE | TOOL_SCHEMA, WHITESPACE |
| F06 (tools) | IDENTICAL | DATE, OTHER, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE | DATE, OTHER, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE |
| F07 (tools) | IDENTICAL | DATE, OTHER, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE | DATE, OTHER, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE |
| F08 (tools) | IDENTICAL | DATE, OTHER, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE | DATE, OTHER, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE |
| F09 (tools) | IDENTICAL | DATE, OTHER, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE | DATE, OTHER, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE |
| F10 | IDENTICAL | DATE, OTHER, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE | DATE, OTHER, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE |
| F11 | IDENTICAL | DATE, DEFAULT_SYSTEM | DATE, DEFAULT_SYSTEM |
| F12 | IDENTICAL | DATE, DEFAULT_SYSTEM | DATE, DEFAULT_SYSTEM |

### `llama2:latest`

- L0: meta-llama/Llama-2-7b-chat-hf@f5db02db7245:api:tokenizer_config.json — latest = 7b-chat-q4_0; the transformers-format chat repo. (confidence high)
- Ollama selects `go_template`
- Render errors: L0.F06: Conversation roles must alternate user/assistant/user/assistant/...; L0.F07: Conversation roles must alternate user/assistant/user/assistant/...; L0.F08: Conversation roles must alternate user/assistant/user/assistant/...; L0.F09: Conversation roles must alternate user/assistant/user/assistant/...; L0.F10: Conversation roles must alternate user/assistant/user/assistant/...; L1.F06: Conversation roles must alternate user/assistant/user/assistant/...; L1.F07: Conversation roles must alternate user/assistant/user/assistant/...; L1.F08: Conversation roles must alternate user/assistant/user/assistant/...; L1.F09: Conversation roles must alternate user/assistant/user/assistant/...; L1.F10: Conversation roles must alternate user/assistant/user/assistant/...

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | BOS, OTHER, WHITESPACE | BOS, OTHER, WHITESPACE |
| F02 | IDENTICAL | BOS, WHITESPACE | BOS, WHITESPACE |
| F03 | IDENTICAL | BOS, OTHER, STRUCTURE, WHITESPACE | BOS, OTHER, STRUCTURE, WHITESPACE |
| F04 (tools) | IDENTICAL | BOS, OTHER, WHITESPACE | BOS, OTHER, WHITESPACE |
| F05 (tools) | IDENTICAL | BOS, WHITESPACE | BOS, WHITESPACE |
| F06 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F07 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F08 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F09 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F10 | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F11 | IDENTICAL | BOS, OTHER, STRUCTURE, WHITESPACE | BOS, OTHER, STRUCTURE, WHITESPACE |
| F12 | IDENTICAL | BOS, OTHER, WHITESPACE | BOS, OTHER, WHITESPACE |

### `llama3.1:latest`

- L0: meta-llama/Llama-3.1-8B-Instruct@0e9e39f249a1:api:tokenizer_config.json — latest = 8b-instruct-q4_K_M; Meta's own 8B Instruct repo. (confidence high)
- Ollama selects `go_template`
- Render errors: L0.F07: This model only supports single tool-calls at once!; L1.F07: This model only supports single tool-calls at once!

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | DATE | DATE |
| F02 | IDENTICAL | BOS, DATE | BOS, DATE |
| F03 | IDENTICAL | DATE | DATE |
| F04 (tools) | IDENTICAL | BOS, DEFAULT_SYSTEM, OTHER, TOOL_SCHEMA, WHITESPACE | BOS, DEFAULT_SYSTEM, OTHER, TOOL_SCHEMA, WHITESPACE |
| F05 (tools) | IDENTICAL | BOS, CONTENT, DEFAULT_SYSTEM, TOOL_SCHEMA, WHITESPACE | BOS, CONTENT, DEFAULT_SYSTEM, TOOL_SCHEMA, WHITESPACE |
| F06 (tools) | IDENTICAL | BOS, DEFAULT_SYSTEM, JSON_SPACING, OTHER, TOOLS_DROPPED, TOOL_RESULT | BOS, DEFAULT_SYSTEM, JSON_SPACING, OTHER, TOOLS_DROPPED, TOOL_RESULT |
| F07 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F08 (tools) | IDENTICAL | BOS, DEFAULT_SYSTEM, JSON_SPACING, OTHER, TOOLS_DROPPED, TOOL_RESULT | BOS, DEFAULT_SYSTEM, JSON_SPACING, OTHER, TOOLS_DROPPED, TOOL_RESULT |
| F09 (tools) | IDENTICAL | BOS, CONTENT, DEFAULT_SYSTEM, OTHER, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE | BOS, CONTENT, DEFAULT_SYSTEM, OTHER, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE |
| F10 | IDENTICAL | BOS, DEFAULT_SYSTEM, JSON_SPACING, OTHER, TOOLS_DROPPED, TOOL_RESULT | BOS, DEFAULT_SYSTEM, JSON_SPACING, OTHER, TOOLS_DROPPED, TOOL_RESULT |
| F11 | IDENTICAL | DATE | DATE |
| F12 | IDENTICAL | DATE | DATE |

### `llama3.2-vision:latest`

- L0: meta-llama/Llama-3.2-11B-Vision-Instruct@9eb2daaa8597:api:tokenizer_config.json — latest = 11b-instruct-q4_K_M. (confidence high)
- Ollama selects `gguf_chat_template`
- Render errors: L0.F07: This model only supports single tool-calls at once!; L1.F07: This model only supports single tool-calls at once!; L3.F07: This model only supports single tool-calls at once!

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F07 (tools) | BOTH_ERROR | BOTH_ERROR | BOTH_ERROR |
| F08 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F09 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F10 | IDENTICAL | IDENTICAL | IDENTICAL |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `llama3.2:latest`

- L0: meta-llama/Llama-3.2-3B-Instruct@0cb88a4f764b:api:tokenizer_config.json — latest = 3b-instruct-q4_K_M. (confidence high)
- Ollama selects `go_template`
- Render errors: L0.F07: This model only supports single tool-calls at once!; L1.F07: This model only supports single tool-calls at once!

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | BOS, DATE | BOS, DATE |
| F02 | IDENTICAL | BOS, DATE | BOS, DATE |
| F03 | IDENTICAL | BOS, DATE | BOS, DATE |
| F04 (tools) | IDENTICAL | BOS, DEFAULT_SYSTEM, OTHER, TOOL_SCHEMA, WHITESPACE | BOS, DEFAULT_SYSTEM, OTHER, TOOL_SCHEMA, WHITESPACE |
| F05 (tools) | IDENTICAL | BOS, CONTENT, DATE, OTHER, TOOL_SCHEMA, WHITESPACE | BOS, CONTENT, DATE, OTHER, TOOL_SCHEMA, WHITESPACE |
| F06 (tools) | IDENTICAL | BOS, DEFAULT_SYSTEM, JSON_SPACING, OTHER, TOOLS_DROPPED, TOOL_RESULT | BOS, DEFAULT_SYSTEM, JSON_SPACING, OTHER, TOOLS_DROPPED, TOOL_RESULT |
| F07 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F08 (tools) | IDENTICAL | BOS, DEFAULT_SYSTEM, JSON_SPACING, OTHER, TOOLS_DROPPED, TOOL_RESULT | BOS, DEFAULT_SYSTEM, JSON_SPACING, OTHER, TOOLS_DROPPED, TOOL_RESULT |
| F09 (tools) | IDENTICAL | BOS, DEFAULT_SYSTEM, OTHER, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE | BOS, DEFAULT_SYSTEM, OTHER, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE |
| F10 | IDENTICAL | BOS, DEFAULT_SYSTEM, JSON_SPACING, OTHER, TOOLS_DROPPED, TOOL_RESULT | BOS, DEFAULT_SYSTEM, JSON_SPACING, OTHER, TOOLS_DROPPED, TOOL_RESULT |
| F11 | IDENTICAL | BOS, DATE | BOS, DATE |
| F12 | IDENTICAL | BOS, DATE | BOS, DATE |

### `llama3.3:latest`

- L0: meta-llama/Llama-3.3-70B-Instruct@6f6073b42301:api:tokenizer_config.json — latest = 70b-instruct-q4_K_M. (confidence high)
- Ollama selects `go_template`
- Render errors: L0.F07: This model only supports single tool-calls at once!; L1.F07: This model only supports single tool-calls at once!

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | DATE | DATE |
| F02 | IDENTICAL | BOS, DATE | BOS, DATE |
| F03 | IDENTICAL | DATE | DATE |
| F04 (tools) | IDENTICAL | BOS, DEFAULT_SYSTEM, OTHER, TOOL_SCHEMA, WHITESPACE | BOS, DEFAULT_SYSTEM, OTHER, TOOL_SCHEMA, WHITESPACE |
| F05 (tools) | IDENTICAL | BOS, CONTENT, DEFAULT_SYSTEM, TOOL_SCHEMA, WHITESPACE | BOS, CONTENT, DEFAULT_SYSTEM, TOOL_SCHEMA, WHITESPACE |
| F06 (tools) | IDENTICAL | BOS, DEFAULT_SYSTEM, JSON_SPACING, OTHER, TOOLS_DROPPED, TOOL_RESULT | BOS, DEFAULT_SYSTEM, JSON_SPACING, OTHER, TOOLS_DROPPED, TOOL_RESULT |
| F07 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F08 (tools) | IDENTICAL | BOS, DEFAULT_SYSTEM, JSON_SPACING, OTHER, TOOLS_DROPPED, TOOL_RESULT | BOS, DEFAULT_SYSTEM, JSON_SPACING, OTHER, TOOLS_DROPPED, TOOL_RESULT |
| F09 (tools) | IDENTICAL | BOS, CONTENT, DEFAULT_SYSTEM, OTHER, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE | BOS, CONTENT, DEFAULT_SYSTEM, OTHER, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE |
| F10 | IDENTICAL | BOS, DEFAULT_SYSTEM, JSON_SPACING, OTHER, TOOLS_DROPPED, TOOL_RESULT | BOS, DEFAULT_SYSTEM, JSON_SPACING, OTHER, TOOLS_DROPPED, TOOL_RESULT |
| F11 | IDENTICAL | DATE | DATE |
| F12 | IDENTICAL | DATE | DATE |

### `llama3:latest`

- L0: meta-llama/Meta-Llama-3-8B-Instruct@8afb486c1db2:api:tokenizer_config.json — latest = 8b-instruct-q4_0. (confidence high)
- Ollama selects `go_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | BOS | BOS |
| F02 | IDENTICAL | BOS | BOS |
| F03 | IDENTICAL | BOS | BOS |
| F04 (tools) | IDENTICAL | BOS | BOS |
| F05 (tools) | IDENTICAL | BOS | BOS |
| F06 (tools) | IDENTICAL | BOS, TOOL_RESULT | BOS, TOOL_RESULT |
| F07 (tools) | IDENTICAL | BOS, TOOL_RESULT | BOS, TOOL_RESULT |
| F08 (tools) | IDENTICAL | BOS, TOOL_RESULT | BOS, TOOL_RESULT |
| F09 (tools) | IDENTICAL | BOS, TOOL_RESULT | BOS, TOOL_RESULT |
| F10 | IDENTICAL | BOS, TOOL_RESULT | BOS, TOOL_RESULT |
| F11 | IDENTICAL | BOS | BOS |
| F12 | IDENTICAL | BOS | BOS |

### `llava:latest`

- L0: liuhaotian/llava-v1.6-mistral-7b@f13b6254afb9:tokenizer_config.json — latest = 7b-v1.6-mistral-q4_0. The author repo's tokenizer_config.json carries the Mistral-Instruct template inherited from the base tokenizer; LLaVA's actual prompt format is defined in the LLaVA code (conv mode mistral_instruct) and the template has no image placeholder. Alternative: llava-hf/llava-v1.6-mistral-7b-hf, Hugging Face's transformers port, which has a processor chat template but is not the author's. (confidence low)
- Ollama selects `go_template`
- Render errors: L0.F02: Conversation roles must alternate user/assistant/user/assistant/...; L0.F05: Conversation roles must alternate user/assistant/user/assistant/...; L0.F06: Conversation roles must alternate user/assistant/user/assistant/...; L0.F07: Conversation roles must alternate user/assistant/user/assistant/...; L0.F08: Conversation roles must alternate user/assistant/user/assistant/...; L0.F09: Conversation roles must alternate user/assistant/user/assistant/...; L0.F10: Conversation roles must alternate user/assistant/user/assistant/...; L1.F02: Conversation roles must alternate user/assistant/user/assistant/...; L1.F05: Conversation roles must alternate user/assistant/user/assistant/...; L1.F06: Conversation roles must alternate user/assistant/user/assistant/...; L1.F07: Conversation roles must alternate user/assistant/user/assistant/...; L1.F08: Conversation roles must alternate user/assistant/user/assistant/...; L1.F09: Conversation roles must alternate user/assistant/user/assistant/...; L1.F10: Conversation roles must alternate user/assistant/user/assistant/...

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | BOS | BOS |
| F02 | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F03 | IDENTICAL | BOS, STRUCTURE | BOS, STRUCTURE |
| F04 (tools) | IDENTICAL | BOS | BOS |
| F05 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F06 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F07 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F08 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F09 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F10 | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F11 | IDENTICAL | BOS, STRUCTURE | BOS, STRUCTURE |
| F12 | IDENTICAL | BOS | BOS |

### `minicpm-v:latest`

- L0: openbmb/MiniCPM-V-2_6@6c04d9e3022b:api:tokenizer_config.json — latest = 8b-2.6-q4_0. (confidence high)
- Ollama selects `go_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F04 (tools) | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F07 (tools) | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F08 (tools) | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F09 (tools) | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F10 | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F11 | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F12 | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |

### `mistral-nemo:latest`

- L0: mistralai/Mistral-Nemo-Instruct-2407@04d8a90549d2:tokenizer_config.json — latest = 12b-instruct-2407-q4_0. (confidence high)
- GGUF template is an older revision of the author's template: newest match 71ede9cf9bc9 (2024-07-30); changed upstream in 16bd7875cfcd (2024-07-31, "Fix chat template (#56)")
- Ollama selects `go_template`
- Render errors: L0.F06: Tool call IDs should be alphanumeric strings with length 9!; L0.F07: Tool call IDs should be alphanumeric strings with length 9!; L0.F08: Tool call IDs should be alphanumeric strings with length 9!; L0.F10: Tool call IDs should be alphanumeric strings with length 9!; L1.F06: After the optional system message, conversation roles must alternate user/assist; L1.F07: After the optional system message, conversation roles must alternate user/assist; L1.F08: After the optional system message, conversation roles must alternate user/assist; L1.F09: After the optional system message, conversation roles must alternate user/assist; L1.F10: After the optional system message, conversation roles must alternate user/assist

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | WHITESPACE | BOS, WHITESPACE | BOS |
| F02 | WHITESPACE | BOS, WHITESPACE | BOS |
| F03 | WHITESPACE | BOS, WHITESPACE | BOS, WHITESPACE |
| F04 (tools) | TOOLS_DROPPED | TOOLS_DROPPED, WHITESPACE | BOS, TOOL_SCHEMA, WHITESPACE |
| F05 (tools) | TOOLS_DROPPED | TOOLS_DROPPED, WHITESPACE | BOS, TOOL_SCHEMA, WHITESPACE |
| F06 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F07 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F08 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F09 (tools) | RENDER_ERROR | REFERENCE_ERROR | BOS, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE |
| F10 | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F11 | WHITESPACE | BOS, WHITESPACE | BOS, WHITESPACE |
| F12 | WHITESPACE | BOS, WHITESPACE | BOS |

### `mistral-small:latest`

- L0: mistralai/Mistral-Small-24B-Instruct-2501@9527884be6e5:tokenizer_config.json — latest = 24b-instruct-2501-q4_K_M. (confidence high)
- GGUF template is an older revision of the author's template: newest match 2c5d4fe8c6ce (2025-01-30); changed upstream in e969dcf155ad (2025-01-30, "Add system message to chat template (#6)")
- Ollama selects `go_template` (SYSTEM layer present)
- Render errors: L0.F06: Only user, system and assistant roles are supported!; L0.F07: Only user, system and assistant roles are supported!; L0.F08: Only user, system and assistant roles are supported!; L0.F09: Only user, system and assistant roles are supported!; L0.F10: Only user, system and assistant roles are supported!; L1.F06: Only user, system and assistant roles are supported!; L1.F07: Only user, system and assistant roles are supported!; L1.F08: Only user, system and assistant roles are supported!; L1.F09: Only user, system and assistant roles are supported!; L1.F10: Only user, system and assistant roles are supported!

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | DATE | DATE | BOS, DATE, WHITESPACE |
| F02 | IDENTICAL | BOS | BOS |
| F03 | DATE | DATE | BOS, DATE, WHITESPACE |
| F04 (tools) | DATE | DATE, TOOLS_DROPPED | BOS, DATE, TOOLS_DROPPED, WHITESPACE |
| F05 (tools) | IDENTICAL | BOS, TOOLS_DROPPED | BOS, TOOLS_DROPPED |
| F06 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F07 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F08 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F09 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F10 | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F11 | DATE | DATE | BOS, DATE, WHITESPACE |
| F12 | DATE | DATE | BOS, DATE, WHITESPACE |

### `mistral:latest`

- L0: mistralai/Mistral-7B-Instruct-v0.3@c170c708c41d:tokenizer_config.json — latest = 7b-instruct-v0.3-q4_K_M. (confidence high)
- GGUF template is an older revision of the author's template: newest match 83e9aa141f2e (2024-05-22); changed upstream in b85b5dd49773 (2024-06-20, "Updating chat template, trying to make it match with `mistral_common` (#44)")
- Ollama selects `go_template`
- Render errors: L0.F06: Tool call IDs should be alphanumeric strings with length 9!; L0.F07: Tool call IDs should be alphanumeric strings with length 9!; L0.F08: Tool call IDs should be alphanumeric strings with length 9!; L0.F10: Tool call IDs should be alphanumeric strings with length 9!; L1.F02: Conversation roles must alternate user/assistant/user/assistant/...; L1.F05: Conversation roles must alternate user/assistant/user/assistant/...; L1.F06: Conversation roles must alternate user/assistant/user/assistant/...; L1.F07: Conversation roles must alternate user/assistant/user/assistant/...; L1.F08: Conversation roles must alternate user/assistant/user/assistant/...; L1.F09: Conversation roles must alternate user/assistant/user/assistant/...; L1.F10: Conversation roles must alternate user/assistant/user/assistant/...

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | WHITESPACE | BOS, WHITESPACE | BOS |
| F02 | RENDER_ERROR | REFERENCE_ERROR | BOS |
| F03 | WHITESPACE | BOS, WHITESPACE | BOS, WHITESPACE |
| F04 (tools) | TOOLS_DROPPED, WHITESPACE | TOOLS_DROPPED, WHITESPACE | BOS, TOOL_SCHEMA, WHITESPACE |
| F05 (tools) | RENDER_ERROR | REFERENCE_ERROR | BOS, TOOL_SCHEMA, WHITESPACE |
| F06 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F07 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F08 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F09 (tools) | RENDER_ERROR | REFERENCE_ERROR | BOS, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA, WHITESPACE |
| F10 | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F11 | WHITESPACE | BOS, WHITESPACE | BOS, WHITESPACE |
| F12 | WHITESPACE | BOS, WHITESPACE | BOS |

### `mixtral:latest`

- L0: mistralai/Mixtral-8x7B-Instruct-v0.1@eba92302a286:tokenizer_config.json — latest = 8x7b-instruct-v0.1-q4_0. (confidence high)
- Ollama selects `go_template`
- Render errors: L0.F06: After the optional system message, conversation roles must alternate user/assist; L0.F07: After the optional system message, conversation roles must alternate user/assist; L0.F08: After the optional system message, conversation roles must alternate user/assist; L0.F09: After the optional system message, conversation roles must alternate user/assist; L0.F10: After the optional system message, conversation roles must alternate user/assist; L1.F06: After the optional system message, conversation roles must alternate user/assist; L1.F07: After the optional system message, conversation roles must alternate user/assist; L1.F08: After the optional system message, conversation roles must alternate user/assist; L1.F09: After the optional system message, conversation roles must alternate user/assist; L1.F10: After the optional system message, conversation roles must alternate user/assist

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | BOS, WHITESPACE | BOS, WHITESPACE |
| F02 | IDENTICAL | BOS, WHITESPACE | BOS, WHITESPACE |
| F03 | IDENTICAL | BOS, STRUCTURE, WHITESPACE | BOS, STRUCTURE, WHITESPACE |
| F04 (tools) | IDENTICAL | BOS, WHITESPACE | BOS, WHITESPACE |
| F05 (tools) | IDENTICAL | BOS, WHITESPACE | BOS, WHITESPACE |
| F06 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F07 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F08 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F09 (tools) | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F10 | BOTH_ERROR | REFERENCE_ERROR | REFERENCE_ERROR |
| F11 | IDENTICAL | BOS, STRUCTURE, WHITESPACE | BOS, STRUCTURE, WHITESPACE |
| F12 | IDENTICAL | BOS, WHITESPACE | BOS, WHITESPACE |

### `nemotron-3-super:latest`

- L0: nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16@2dc98e2afe4f:chat_template.jinja — latest = 120b-a12b-q4_K_M. NVIDIA publishes this model only as precision-suffixed repos (no unsuffixed repo exists); BF16 is the full-precision one. The other precision repos were not checked. (confidence medium)
- Ollama selects `renderer_parser`

| Fixture | L0→L3 |
|---|---|
| F01 | IDENTICAL |
| F02 | IDENTICAL |
| F03 | IDENTICAL |
| F04 (tools) | IDENTICAL |
| F05 (tools) | IDENTICAL |
| F06 (tools) | IDENTICAL |
| F07 (tools) | IDENTICAL |
| F08 (tools) | IDENTICAL |
| F09 (tools) | IDENTICAL |
| F10 | IDENTICAL |
| F11 | IDENTICAL |
| F12 | IDENTICAL |

### `olmo2:latest`

- L0: allenai/OLMo-2-1124-7B-Instruct@470b1fba1ae0:tokenizer_config.json — latest = 7b-1124-instruct-q4_K_M. (confidence high)
- Ollama selects `go_template` (SYSTEM layer present)

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | DEFAULT_SYSTEM, WHITESPACE | DEFAULT_SYSTEM, WHITESPACE |
| F02 | IDENTICAL | BOS, WHITESPACE | BOS, WHITESPACE |
| F03 | IDENTICAL | DEFAULT_SYSTEM, STRUCTURE, WHITESPACE | DEFAULT_SYSTEM, STRUCTURE, WHITESPACE |
| F04 (tools) | IDENTICAL | DEFAULT_SYSTEM, WHITESPACE | DEFAULT_SYSTEM, WHITESPACE |
| F05 (tools) | IDENTICAL | BOS, WHITESPACE | BOS, WHITESPACE |
| F06 (tools) | IDENTICAL | DEFAULT_SYSTEM, TOOL_RESULT | DEFAULT_SYSTEM, TOOL_RESULT |
| F07 (tools) | IDENTICAL | DEFAULT_SYSTEM, TOOL_RESULT | DEFAULT_SYSTEM, TOOL_RESULT |
| F08 (tools) | IDENTICAL | DEFAULT_SYSTEM, TOOL_RESULT | DEFAULT_SYSTEM, TOOL_RESULT |
| F09 (tools) | IDENTICAL | DEFAULT_SYSTEM, TOOL_RESULT, WHITESPACE | DEFAULT_SYSTEM, TOOL_RESULT, WHITESPACE |
| F10 | IDENTICAL | DEFAULT_SYSTEM, TOOL_RESULT | DEFAULT_SYSTEM, TOOL_RESULT |
| F11 | IDENTICAL | DEFAULT_SYSTEM, STRUCTURE, WHITESPACE | DEFAULT_SYSTEM, STRUCTURE, WHITESPACE |
| F12 | IDENTICAL | DEFAULT_SYSTEM, WHITESPACE | DEFAULT_SYSTEM, WHITESPACE |

### `phi3:latest`

- L0: microsoft/Phi-3-mini-128k-instruct@f3c06aed622e:tokenizer_config.json — latest = 3.8b-mini-128k-instruct-q4_0 (not the 4k variant). Microsoft has revised this repo since the package was built (last modified 2025-12-10), so the template at main may be newer than the GGUF's. (confidence medium)
- Ollama selects `go_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | WHITESPACE | WHITESPACE |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | STRUCTURE | STRUCTURE |
| F07 (tools) | IDENTICAL | STRUCTURE | STRUCTURE |
| F08 (tools) | IDENTICAL | STRUCTURE | STRUCTURE |
| F09 (tools) | IDENTICAL | TOOL_RESULT, WHITESPACE | TOOL_RESULT, WHITESPACE |
| F10 | IDENTICAL | STRUCTURE | STRUCTURE |
| F11 | IDENTICAL | WHITESPACE | WHITESPACE |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `phi4:latest`

- L0: microsoft/phi-4@2db69c1c3e91:tokenizer_config.json — latest = 14b-q4_K_M. Repo last modified 2026-07-14, after the package (2025-01-08). (confidence high)
- GGUF template is an older revision of the author's template: newest match f957856cd926 (2025-01-08); changed upstream in 6fbb3d3bbe72 (2025-02-04, "Suggested tokenizer changes by Unsloth.ai (#21)")
- Ollama selects `go_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | WHITESPACE | WHITESPACE |
| F02 | IDENTICAL | WHITESPACE | WHITESPACE |
| F03 | IDENTICAL | WHITESPACE | WHITESPACE |
| F04 (tools) | IDENTICAL | WHITESPACE | WHITESPACE |
| F05 (tools) | IDENTICAL | WHITESPACE | WHITESPACE |
| F06 (tools) | STRUCTURE | TOOL_RESULT, WHITESPACE | TOOL_RESULT, WHITESPACE |
| F07 (tools) | STRUCTURE | TOOL_RESULT, WHITESPACE | TOOL_RESULT, WHITESPACE |
| F08 (tools) | STRUCTURE | TOOL_RESULT, WHITESPACE | TOOL_RESULT, WHITESPACE |
| F09 (tools) | TOOL_RESULT | TOOL_RESULT, WHITESPACE | TOOL_RESULT, WHITESPACE |
| F10 | STRUCTURE | TOOL_RESULT, WHITESPACE | TOOL_RESULT, WHITESPACE |
| F11 | IDENTICAL | WHITESPACE | WHITESPACE |
| F12 | IDENTICAL | WHITESPACE | WHITESPACE |

### `qwen2.5-coder:latest`

- L0: Qwen/Qwen2.5-Coder-7B-Instruct@c03e6d358207:tokenizer_config.json — latest = 7b-instruct-q4_K_M. (confidence high)
- Ollama selects `go_template` (SYSTEM layer present)

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON | TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON |
| F05 (tools) | IDENTICAL | TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON | TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON |
| F06 (tools) | IDENTICAL | JSON_SPACING, TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON | JSON_SPACING, TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON |
| F07 (tools) | IDENTICAL | JSON_SPACING, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON | JSON_SPACING, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON |
| F08 (tools) | IDENTICAL | TOOL_CALL, TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON | TOOL_CALL, TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON |
| F09 (tools) | IDENTICAL | JSON_SPACING, TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON | JSON_SPACING, TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON |
| F10 | IDENTICAL | JSON_SPACING, TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON | JSON_SPACING, TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `qwen2.5:latest`

- L0: Qwen/Qwen2.5-7B-Instruct@a09a35458c70:tokenizer_config.json — latest = 7b-instruct-q4_K_M; the same repo P0 used (GGUF base_model metadata points at the base Qwen2.5-7B instead). (confidence high)
- GGUF template is an older revision of the author's template: newest match 52e20a6f5f47 (2024-09-18); changed upstream in acbd96531cda (2024-09-19, "Upload ./tokenizer_config.json with huggingface_hub")
- Ollama selects `go_template` (SYSTEM layer present)

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | TOOL_SCHEMA | TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON | TOOL_SCHEMA_NOT_JSON |
| F05 (tools) | TOOL_SCHEMA | TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON | TOOL_SCHEMA_NOT_JSON |
| F06 (tools) | TOOL_SCHEMA | JSON_SPACING, TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON | JSON_SPACING, TOOL_SCHEMA_NOT_JSON |
| F07 (tools) | TOOL_SCHEMA | JSON_SPACING, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON | JSON_SPACING, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA_NOT_JSON |
| F08 (tools) | TOOL_SCHEMA | TOOL_CALL, TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON | TOOL_CALL, TOOL_SCHEMA_NOT_JSON |
| F09 (tools) | TOOL_SCHEMA | JSON_SPACING, TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON | JSON_SPACING, TOOL_SCHEMA_NOT_JSON |
| F10 | TOOL_SCHEMA | JSON_SPACING, TOOL_SCHEMA, TOOL_SCHEMA_NOT_JSON | JSON_SPACING, TOOL_SCHEMA_NOT_JSON |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `qwen2.5vl:latest`

- L0: Qwen/Qwen2.5-VL-7B-Instruct@cc594898137f:chat_template.json — latest = 7b-q4_K_M. (confidence high)
- Ollama selects `go_template` (SYSTEM layer present)

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | TOOL_RESULT | TOOL_RESULT |
| F07 (tools) | IDENTICAL | TOOL_RESULT | TOOL_RESULT |
| F08 (tools) | IDENTICAL | TOOL_RESULT | TOOL_RESULT |
| F09 (tools) | IDENTICAL | TOOL_RESULT | TOOL_RESULT |
| F10 | IDENTICAL | TOOL_RESULT | TOOL_RESULT |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `qwen2:latest`

- L0: Qwen/Qwen2-7B-Instruct@f2826a00ceef:tokenizer_config.json — latest = 7b-instruct-q4_0. (confidence high)
- Ollama selects `go_template` (SYSTEM layer present)

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | TOOLS_DROPPED | TOOLS_DROPPED |
| F05 (tools) | IDENTICAL | TOOLS_DROPPED | TOOLS_DROPPED |
| F06 (tools) | IDENTICAL | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT |
| F07 (tools) | IDENTICAL | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT |
| F08 (tools) | IDENTICAL | TOOLS_DROPPED, TOOL_RESULT | TOOLS_DROPPED, TOOL_RESULT |
| F09 (tools) | IDENTICAL | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT |
| F10 | IDENTICAL | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT | TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `qwen3-coder:latest`

- L0: Qwen/Qwen3-Coder-30B-A3B-Instruct@b2cff646eb4b:chat_template.jinja — latest = 30b-a3b-q4_K_M. (confidence high)
- GGUF template is an older revision of the author's template: newest match d4add6db775e (2025-08-01); changed upstream in 8110d98ad896 (2025-08-07, "Update chat_template in tokenizer_config.json (#14)")
- Ollama selects `renderer_parser`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | TOOL_SCHEMA | TOOL_SCHEMA | WHITESPACE |
| F05 (tools) | TOOL_SCHEMA | TOOL_SCHEMA | WHITESPACE |
| F06 (tools) | TOOL_SCHEMA | TOOL_SCHEMA, WHITESPACE | WHITESPACE |
| F07 (tools) | TOOL_SCHEMA | TOOL_SCHEMA, WHITESPACE | WHITESPACE |
| F08 (tools) | TOOL_SCHEMA | TOOL_SCHEMA, WHITESPACE | WHITESPACE |
| F09 (tools) | TOOL_SCHEMA | TOOL_SCHEMA, WHITESPACE | WHITESPACE |
| F10 | TOOL_SCHEMA | TOOL_SCHEMA, WHITESPACE | WHITESPACE |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `qwen3-vl:latest`

- L0: Qwen/Qwen3-VL-8B-Thinking@92f3c4b4fead:chat_template.json — latest = 8b-thinking-q4_K_M, so the Thinking repo, not 8B-Instruct. (confidence high)
- Ollama selects `renderer_parser`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F05 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F06 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F07 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F08 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F09 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F10 | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `qwen3.5:latest`

- L0: Qwen/Qwen3.5-9B@c20223623576:chat_template.jinja — latest = 9b. Qwen/Qwen3.5-9B is the post-trained model (its card's base is Qwen3.5-9B-Base). (confidence high)
- Ollama selects `renderer_parser`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F05 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F06 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F07 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F08 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F09 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F10 | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `qwen3.6:latest`

- L0: Qwen/Qwen3.6-35B-A3B@995ad96eacd9:chat_template.jinja — latest = 35b-a3b (not 27b). (confidence high)
- Ollama selects `renderer_parser`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F05 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F06 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F07 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F08 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F09 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F10 | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `qwen3.8:latest`

- L0: Qwen/Qwen3.8-27B@1d4bf0f2ff60:chat_template.jinja — latest = 27b; the only Qwen3.8 size in the library. (confidence high)
- Ollama selects `renderer_parser`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F05 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F06 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F07 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F08 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F09 (tools) | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F10 | IDENTICAL | TOOL_SCHEMA | TOOL_SCHEMA |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `qwen3:latest`

- L0: Qwen/Qwen3-8B@b968826d9c46:tokenizer_config.json — latest = 8b-q4_K_M. Qwen3-8B is the post-trained hybrid-thinking model (base is Qwen3-8B-Base); no 2507 Instruct exists at 8B. (confidence high)
- GGUF template is an older revision of the author's template: newest match 2069b3fae111 (2025-04-29); changed upstream in 895c8d171bc0 (2025-05-19, "update tokenizer_config.json")
- Ollama selects `go_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | IDENTICAL | IDENTICAL |
| F02 | IDENTICAL | WHITESPACE | WHITESPACE |
| F03 | IDENTICAL | IDENTICAL | IDENTICAL |
| F04 (tools) | IDENTICAL | TOOL_SCHEMA_NOT_JSON, WHITESPACE | TOOL_SCHEMA_NOT_JSON, WHITESPACE |
| F05 (tools) | IDENTICAL | TOOL_SCHEMA_NOT_JSON, WHITESPACE | TOOL_SCHEMA_NOT_JSON, WHITESPACE |
| F06 (tools) | IDENTICAL | JSON_SPACING, TOOL_SCHEMA_NOT_JSON, WHITESPACE | JSON_SPACING, TOOL_SCHEMA_NOT_JSON, WHITESPACE |
| F07 (tools) | IDENTICAL | JSON_SPACING, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA_NOT_JSON, WHITESPACE | JSON_SPACING, TOOL_CALL, TOOL_RESULT, TOOL_SCHEMA_NOT_JSON, WHITESPACE |
| F08 (tools) | IDENTICAL | TOOL_CALL, TOOL_SCHEMA_NOT_JSON, WHITESPACE | TOOL_CALL, TOOL_SCHEMA_NOT_JSON, WHITESPACE |
| F09 (tools) | IDENTICAL | JSON_SPACING, TOOL_SCHEMA_NOT_JSON, WHITESPACE | JSON_SPACING, TOOL_SCHEMA_NOT_JSON, WHITESPACE |
| F10 | IDENTICAL | JSON_SPACING, TOOL_SCHEMA_NOT_JSON, WHITESPACE | JSON_SPACING, TOOL_SCHEMA_NOT_JSON, WHITESPACE |
| F11 | IDENTICAL | IDENTICAL | IDENTICAL |
| F12 | IDENTICAL | IDENTICAL | IDENTICAL |

### `qwen:latest`

- L0: Qwen/Qwen1.5-4B-Chat@a7a4d4945d28:tokenizer_config.json — latest = 4b-chat-v1.5-q4_0. (confidence high)
- GGUF template is an older revision of the author's template: newest match 53db5c42837c (2024-02-05); changed upstream in 810c56371ed0 (2024-02-06, "update tokenizer_config.json")
- Ollama selects `go_template`

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | DEFAULT_SYSTEM | IDENTICAL | DEFAULT_SYSTEM |
| F02 | IDENTICAL | WHITESPACE | WHITESPACE |
| F03 | DEFAULT_SYSTEM | STRUCTURE | DEFAULT_SYSTEM, STRUCTURE |
| F04 (tools) | DEFAULT_SYSTEM | IDENTICAL | DEFAULT_SYSTEM |
| F05 (tools) | IDENTICAL | WHITESPACE | WHITESPACE |
| F06 (tools) | DEFAULT_SYSTEM | TOOL_RESULT | DEFAULT_SYSTEM, TOOL_RESULT |
| F07 (tools) | DEFAULT_SYSTEM | TOOL_RESULT | DEFAULT_SYSTEM, TOOL_RESULT |
| F08 (tools) | DEFAULT_SYSTEM | TOOL_RESULT | DEFAULT_SYSTEM, TOOL_RESULT |
| F09 (tools) | DEFAULT_SYSTEM | TOOL_RESULT | DEFAULT_SYSTEM, TOOL_RESULT |
| F10 | DEFAULT_SYSTEM | TOOL_RESULT | DEFAULT_SYSTEM, TOOL_RESULT |
| F11 | DEFAULT_SYSTEM | STRUCTURE | DEFAULT_SYSTEM, STRUCTURE |
| F12 | DEFAULT_SYSTEM | IDENTICAL | DEFAULT_SYSTEM |

### `smollm2:latest`

- L0: HuggingFaceTB/SmolLM2-1.7B-Instruct@31b70e2e869a:tokenizer_config.json — latest = 1.7b-instruct-q8_0. (confidence high)
- Ollama selects `go_template` (SYSTEM layer present)

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | STRUCTURE | STRUCTURE |
| F02 | IDENTICAL | STRUCTURE | STRUCTURE |
| F03 | IDENTICAL | STRUCTURE | STRUCTURE |
| F04 (tools) | IDENTICAL | DEFAULT_SYSTEM, TOOLS_DROPPED | DEFAULT_SYSTEM, TOOLS_DROPPED |
| F05 (tools) | IDENTICAL | CONTENT, TOOLS_DROPPED | CONTENT, TOOLS_DROPPED |
| F06 (tools) | IDENTICAL | DEFAULT_SYSTEM, TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT | DEFAULT_SYSTEM, TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT |
| F07 (tools) | IDENTICAL | DEFAULT_SYSTEM, TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT | DEFAULT_SYSTEM, TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT |
| F08 (tools) | IDENTICAL | DEFAULT_SYSTEM, TOOLS_DROPPED, TOOL_RESULT | DEFAULT_SYSTEM, TOOLS_DROPPED, TOOL_RESULT |
| F09 (tools) | IDENTICAL | DEFAULT_SYSTEM, TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT | DEFAULT_SYSTEM, TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT |
| F10 | IDENTICAL | DEFAULT_SYSTEM, TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT | DEFAULT_SYSTEM, TOOLS_DROPPED, TOOL_CALL, TOOL_RESULT |
| F11 | IDENTICAL | STRUCTURE | STRUCTURE |
| F12 | IDENTICAL | STRUCTURE | STRUCTURE |

### `tinyllama:latest`

- L0: TinyLlama/TinyLlama-1.1B-Chat-v1.0@fe8a4ea1ffed:tokenizer_config.json — latest = 1.1b-chat-v1-q4_0. (confidence high)
- Ollama selects `go_template` (SYSTEM layer present)

| Fixture | L0→L1 | L1→L3 | L0→L3 |
|---|---|---|---|
| F01 | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F02 | IDENTICAL | IDENTICAL | IDENTICAL |
| F03 | IDENTICAL | DEFAULT_SYSTEM, STRUCTURE | DEFAULT_SYSTEM, STRUCTURE |
| F04 (tools) | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |
| F05 (tools) | IDENTICAL | IDENTICAL | IDENTICAL |
| F06 (tools) | IDENTICAL | DEFAULT_SYSTEM, STRUCTURE | DEFAULT_SYSTEM, STRUCTURE |
| F07 (tools) | IDENTICAL | DEFAULT_SYSTEM, STRUCTURE | DEFAULT_SYSTEM, STRUCTURE |
| F08 (tools) | IDENTICAL | DEFAULT_SYSTEM, STRUCTURE | DEFAULT_SYSTEM, STRUCTURE |
| F09 (tools) | IDENTICAL | DEFAULT_SYSTEM, TOOL_RESULT | DEFAULT_SYSTEM, TOOL_RESULT |
| F10 | IDENTICAL | DEFAULT_SYSTEM, STRUCTURE | DEFAULT_SYSTEM, STRUCTURE |
| F11 | IDENTICAL | DEFAULT_SYSTEM, STRUCTURE | DEFAULT_SYSTEM, STRUCTURE |
| F12 | IDENTICAL | DEFAULT_SYSTEM | DEFAULT_SYSTEM |

### `translategemma:latest`

- L0: google/translategemma-4b-it@10042cb0e6e7:api:chat_template.jinja — latest = 4b-it-q4_K_M. (confidence high)
- Ollama selects `go_template`
- Render errors: L0.F01: User role must provide `content` as an iterable with exactly one item. That item; L0.F02: Conversations must start with a user prompt.; L0.F03: User role must provide `content` as an iterable with exactly one item. That item; L0.F04: User role must provide `content` as an iterable with exactly one item. That item; L0.F05: Conversations must start with a user prompt.; L0.F06: User role must provide `content` as an iterable with exactly one item. That item; L0.F07: User role must provide `content` as an iterable with exactly one item. That item; L0.F08: User role must provide `content` as an iterable with exactly one item. That item; L0.F09: User role must provide `content` as an iterable with exactly one item. That item; L0.F10: User role must provide `content` as an iterable with exactly one item. That item; L0.F11: User role must provide `content` as an iterable with exactly one item. That item; L0.F12: User role must provide `content` as an iterable with exactly one item. That item

| Fixture | L0→L3 |
|---|---|
| F01 | REFERENCE_ERROR |
| F02 | REFERENCE_ERROR |
| F03 | REFERENCE_ERROR |
| F04 (tools) | REFERENCE_ERROR |
| F05 (tools) | REFERENCE_ERROR |
| F06 (tools) | REFERENCE_ERROR |
| F07 (tools) | REFERENCE_ERROR |
| F08 (tools) | REFERENCE_ERROR |
| F09 (tools) | REFERENCE_ERROR |
| F10 | REFERENCE_ERROR |
| F11 | REFERENCE_ERROR |
| F12 | REFERENCE_ERROR |

## Not in the headline count

- `gpt-oss:latest`: partial — L3 source harmony not rendered offline

## Excluded by the mapping

- `orca-mini:latest`: latest = 3b-q4_0, from pankajmathur/orca_mini_3b. That repo has no chat template; its prompt format is given only as prose in the model card.
- `starcoder2:latest`: latest = 3b-q4_0, the base completion model bigcode/starcoder2-3b, which has no chat template (starcoder2:instruct is a separate, non-default tag).
- `llama2-uncensored:latest`: latest = 7b-chat-q4_0, from georgesung/llama2_7b_chat_uncensored, which has no chat template.
- `mistral-small3.2:latest`: latest = 24b-instruct-2506-q4_K_M. Mistral's repo ships tekken.json, params.json and SYSTEM_PROMPT.txt for mistral-common and no Jinja chat template.
- `minimax-m2.7:cloud`: Cloud-only in Ollama: the tags page lists only `cloud`, so there is no local package (no GGUF, Go template or selection) to audit. The author repo does have chat_template.jinja.

## Method notes

- Severity: `none` (whitespace, BOS, date), `minor` (same JSON, different spacing or escapes), `material` (everything else). Classes are defined in `labels/GUIDE.md`.
- L0 and L1 are rendered with the L0 special tokens, so L0→L1 compares template text only.
- A fixture the reference side cannot render is marked `REFERENCE_ERROR` and is not counted as drift.
- Sources read: 540 URLs (listed in run.json); network requests this run: 616.
