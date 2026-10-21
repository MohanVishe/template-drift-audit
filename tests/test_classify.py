import json

from tda.classify import classify

TOOLS = [{"type": "function", "function": {"name": "add", "description": "Add two numbers",
                                           "parameters": {"type": "object", "properties": {"a": {"type": "number"}}}}}]
MSGS = [{"role": "user", "content": "What is 2 plus 3?"}]


def render(defs: str, tail: str = "<|im_start|>assistant\n") -> str:
    return f"<|im_start|>system\n# Tools\n<tools>\n{defs}\n</tools><|im_end|>\n<|im_start|>user\nWhat is 2 plus 3?<|im_end|>\n{tail}"


def test_identical_and_render_error():
    a = render(json.dumps(TOOLS[0]))
    assert classify(a, a, MSGS, TOOLS).classes == ["IDENTICAL"]
    r = classify(a, None, MSGS, TOOLS)
    assert r.classes == ["RENDER_ERROR"] and r.severity == "material"


def test_json_spacing_is_minor():
    a = render(json.dumps(TOOLS[0]))
    b = render(json.dumps(TOOLS[0], separators=(",", ":")))
    r = classify(a, b, MSGS, TOOLS)
    assert r.classes == ["JSON_SPACING"] and r.severity == "minor"


def test_reordered_keys_are_a_schema_change():
    fn = TOOLS[0]["function"]
    reordered = {"function": {"description": fn["description"], "name": fn["name"], "parameters": fn["parameters"]},
                 "type": "function"}
    r = classify(render(json.dumps(TOOLS[0])), render(json.dumps(reordered)), MSGS, TOOLS)
    assert "TOOL_SCHEMA" in r.classes and r.severity == "material"


def test_go_struct_tool_definition():
    a = render(json.dumps(TOOLS[0]))
    b = render("{function {add Add two numbers {object <nil> [] map[a:{number <nil>}]}}}")
    r = classify(a, b, MSGS, TOOLS)
    assert "TOOL_SCHEMA_NOT_JSON" in r.classes and r.severity == "material"


def test_trailing_newline_is_whitespace():
    a = render(json.dumps(TOOLS[0]))
    r = classify(a, a + "\n", MSGS, TOOLS)
    assert r.classes == ["WHITESPACE"] and r.severity == "none"


def test_default_system_prompt():
    a = "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\nHi there<|im_end|>\n"
    b = "<|im_start|>user\nHi there<|im_end|>\n"
    r = classify(a, b, [{"role": "user", "content": "Hi there"}], None,
                 default_system=["You are a helpful assistant."])
    assert r.classes == ["DEFAULT_SYSTEM"]
