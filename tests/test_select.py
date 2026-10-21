"""Parity with Ollama v0.40.7's own TestGetModelTemplateMetadata cases (server/images_test.go)."""

import pytest

from tda.select import approx_go_info, select_source
from tda.sources.ollama_store import LocalStore, default_models_dir

CUSTOM = "CUSTOM {{ .Prompt }}"
CHAT_TOOLS = "{% if tools %}{{ tools }}{% endif %}{{ messages[0]['content'] }}"

ROUND_TRIP_CHAT = """{% if tools %}{{ tools }}{% endif %}
{% for message in messages %}
{% if message.tool_calls %}
{% for tool_call in message.tool_calls %}{{ tool_call.function.name }}{% endfor %}
{% endif %}
{% if message.role == 'tool' %}tool_response {{ message.content }}{% endif %}
{% endfor %}"""
ROUND_TRIP_GO = """{{ if .Tools }}tools{{ end }}
{{ range .Messages }}
{{ range .ToolCalls }}{{ .Function.Name }}{{ end }}
{{ end }}"""

WEAKER_CHAT = """{%- if tools and not available_tools -%}
{{- set available_tools = tools -}}
{%- endif -%}
{%- if available_tools -%}
{{ '<|start_of_role|>available_tools<|end_of_role|>' }}{{ available_tools | tojson }}{{ '<|end_of_text|>' }}
{%- endif -%}
{%- if thinking -%}<think></think><response></response>{%- endif -%}
{%- for message in messages -%}
{{ '<|start_of_role|>' + message['role'] + '<|end_of_role|>' + message['content'] + '<|end_of_text|>' }}
{%- endfor -%}"""
WEAKER_GO = """{{ if .Tools }}tools{{ end }}
{{ range .Messages }}
{{ if eq .Role "tool" }}tool_response{{ else }}{{ .Role }}{{ end }}
{{ if .ToolCalls }}<|tool_call|>{{ range .ToolCalls }}{{ .Function.Name }}{{ end }}{{ else }}{{ .Content }}{{ end }}
{{ end }}"""

IDS_CHAT = """{% if tools %}{{ tools }}{% endif %}
{% for message in messages %}
{% if message.get('tool_calls') %}{% for tool_call in message.tool_calls %}[TOOL_CALLS]{{ tool_call.function.name }}[CALL_ID]{{ tool_call.id }}[ARGS]{{ tool_call['function']['arguments']|tojson }}{% endfor %}{% endif %}
{% if message['role'] == 'tool' %}tool_response{{ message['content'] }}{% endif %}
{% endfor %}"""
IDS_GO = """{{ if .Tools }}tools{{ end }}
{{ range .Messages }}
{{ if eq .Role "tool" }}tool_response{{ else }}{{ .Role }}{{ end }}
{{ if .ToolCalls }}[TOOL_CALLS]{{ range .ToolCalls }}{{ .Function.Name }}[CALL_ID]0[ARGS]{{ .Function.Arguments }}{{ end }}{{ else }}{{ .Content }}{{ end }}
{{ end }}"""


@pytest.mark.parametrize("case, chat, go, env, prefer, source", [
    ("records chat template and Go TEMPLATE", "{{ bos_token }}{{ messages[0]['content'] }}", CUSTOM, None, False, "go_template"),
    ("Go TEMPLATE has fewer capabilities", CHAT_TOOLS, CUSTOM, None, True, "gguf_chat_template"),
    ("Qwen tools + inferred thinking",
     "{% if tools %}{{ tools }}{% endif %}{% set content = (content.split('</think>')|last) %}",
     "{{ range .Messages }}{{ if .Thinking }}<think>{{ .Thinking }}</think>{{ end }}{{ .Content }}{{ end }}",
     None, True, "gguf_chat_template"),
    ("stronger tool round trip", ROUND_TRIP_CHAT, ROUND_TRIP_GO, None, True, "gguf_chat_template"),
    ("weaker chat tool support", WEAKER_CHAT, WEAKER_GO, None, False, "go_template"),
    ("Mistral tool call IDs", IDS_CHAT, IDS_GO, None, True, "gguf_chat_template"),
    ("OLLAMA_GO_TEMPLATE=1", CHAT_TOOLS, CUSTOM, True, False, "go_template"),
    ("OLLAMA_GO_TEMPLATE=0", CHAT_TOOLS, CUSTOM, False, False, "gguf_chat_template"),
    ("missing chat template", "", CUSTOM, None, False, "go_template"),
])
def test_matches_ollama_cases(case, chat, go, env, prefer, source):
    sel = select_source(model_family="llama", go=approx_go_info(go), gguf_chat_template=chat, go_template_env=env)
    assert (sel.prefer_chat_template, sel.source) == (prefer, source), case


def test_renderer_and_harmony_take_precedence():
    go = approx_go_info("<|start|>{{ .Prompt }}<|end|>")
    assert select_source(renderer="qwen3.5", go=go, gguf_chat_template=CHAT_TOOLS).source == "renderer"
    assert select_source(renderer="x", parser="y").source == "renderer_parser"
    assert select_source(model_family="gptoss", go=go).source == "harmony"
    assert select_source(gguf_chat_template=CHAT_TOOLS).source == "gguf_chat_template"
    assert select_source().source == "none"


def test_approx_vars_ignore_string_literals_and_lowercase():
    info = approx_go_info('{{ range $i, $_ := .Messages }}{{ if eq .Role "tool" }}{{ .Content }}{{ $.Tools }}{{ end }}{{ end }}')
    assert {"messages", "role", "content", "tools", "$", "$i", "$_"} <= info.vars
    assert "tool" not in info.vars and not info.exact


@pytest.mark.skipif(not (default_models_dir() / "manifests").exists(), reason="no local Ollama store")
def test_local_store_selection_runs():
    store = LocalStore()
    for m in store.models():
        sel = select_source(renderer=m.renderer, parser=m.parser, model_family=m.config.get("model_family", ""),
                            go=approx_go_info(m.template) if m.template is not None else None,
                            gguf_chat_template=store.gguf_header(m).chat_template or "")
        assert sel.source in {"renderer_parser", "renderer", "parser", "harmony", "go_template", "gguf_chat_template", "none"}
