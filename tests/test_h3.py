import unittest

from tda.h3 import bfcl


class ToTools(unittest.TestCase):
    def setUp(self):
        self.functions = [{
            "name": "math.hypot",
            "description": "Hypotenuse.",
            "parameters": {"type": "dict", "required": ["x"], "properties": {
                "x": {"type": "float", "description": "First side."},
                "pts": {"type": "array", "items": {"type": "tuple"}, "description": "Points."},
                "opts": {"type": "dict", "properties": {"mode": {"type": "any", "description": "Mode."}}},
                "free": {"description": "No type given."},
            }},
            "response": {"type": "dict", "properties": {"result": {"type": "float"}}},
        }]

    def test_shape_and_names(self):
        tools, names = bfcl.to_tools(self.functions)
        fn = tools[0]["function"]
        self.assertEqual(tools[0]["type"], "function")
        self.assertEqual(fn["name"], "math_hypot")
        self.assertEqual(names, {"math_hypot": "math.hypot"})
        self.assertNotIn("response", fn)
        self.assertEqual(fn["parameters"]["type"], "object")
        self.assertEqual(fn["parameters"]["required"], ["x"])

    def test_types_follow_bfcl(self):
        props = bfcl.to_tools(self.functions)[0][0]["function"]["parameters"]["properties"]
        self.assertEqual(props["x"]["type"], "number")
        self.assertEqual(props["x"]["format"], "float")
        self.assertTrue(props["x"]["description"].endswith("This is a float type value."))
        self.assertEqual(props["pts"]["items"]["type"], "array")
        self.assertEqual(props["opts"]["type"], "object")
        self.assertEqual(props["opts"]["properties"]["mode"]["type"], "string")
        self.assertEqual(props["free"]["type"], "string")

    def test_input_not_mutated(self):
        bfcl.to_tools(self.functions)
        self.assertEqual(self.functions[0]["parameters"]["type"], "dict")
        self.assertEqual(self.functions[0]["name"], "math.hypot")


class Calls(unittest.TestCase):
    def test_call_string(self):
        self.assertEqual(bfcl.call_string("cd", {"folder": "doc"}), "cd(folder='doc')")
        self.assertEqual(bfcl.call_string("f", {"a": [1, 2], "b": None, "c": True}), "f(a=[1, 2],b=None,c=True)")
        self.assertEqual(bfcl.call_string("ls", {}), "ls()")

    def test_bfcl_output_maps_names_back(self):
        out = bfcl.bfcl_output([{"name": "math_hypot", "arguments": {"x": 3}}], {"math_hypot": "math.hypot"})
        self.assertEqual(out, [{"math.hypot": {"x": 3}}])


class Hermes(unittest.TestCase):
    def test_two_calls(self):
        text = ('<tool_call>\n{"name": "a", "arguments": {"x": 1}}\n</tool_call>\n'
                '<tool_call>\n{"name": "b", "arguments": {}}\n</tool_call>')
        p = bfcl.parse_hermes(text)
        self.assertEqual(p.calls, [{"name": "a", "arguments": {"x": 1}}, {"name": "b", "arguments": {}}])
        self.assertEqual(p.history_message()["content"], "")
        self.assertEqual(p.history_message()["tool_calls"][1]["function"]["name"], "b")

    def test_no_calls_is_empty_not_failed(self):
        p = bfcl.parse_hermes("I can't help with that.")
        self.assertEqual(p.calls, [])
        self.assertFalse(p.has_calls)
        self.assertEqual(p.history_message(), {"role": "assistant", "content": "I can't help with that."})

    def test_bad_json_block_is_skipped(self):
        p = bfcl.parse_hermes('<tool_call>\n{"name": "a", \n</tool_call>\n<tool_call>\n{"name": "b", "arguments": {}}\n</tool_call>')
        self.assertEqual(p.calls, [{"name": "b", "arguments": {}}])
        self.assertTrue(p.notes)

    def test_missing_arguments_fails_decode(self):
        p = bfcl.parse_hermes('<tool_call>\n{"name": "a"}\n</tool_call>')
        self.assertIsNone(p.calls)
        self.assertFalse(p.has_calls)

    def test_needs_the_newlines(self):  # same regex as BFCL's qwen_fc handler
        self.assertEqual(bfcl.parse_hermes('<tool_call>{"name": "a", "arguments": {}}</tool_call>').calls, [])


class FromOllama(unittest.TestCase):
    def test_message(self):
        p = bfcl.from_ollama({"role": "assistant", "content": "",
                              "tool_calls": [{"function": {"index": 0, "name": "a", "arguments": {"x": 1}}}]})
        self.assertEqual(p.calls, [{"name": "a", "arguments": {"x": 1}}])

    def test_no_calls(self):
        p = bfcl.from_ollama({"role": "assistant", "content": "hello"})
        self.assertEqual(p.calls, [])
        self.assertEqual(p.content, "hello")


class OneBos(unittest.TestCase):
    def test_strips_only_when_the_runtime_adds_it(self):
        from tda.h3.runtime import one_bos
        self.assertEqual(one_bos("<s>[INST] hi", "<s>", True), "[INST] hi")
        self.assertEqual(one_bos("<s>[INST] hi", "<s>", False), "<s>[INST] hi")
        self.assertEqual(one_bos("[INST] hi", "<s>", True), "[INST] hi")
        self.assertEqual(one_bos("<|im_start|>user", "", True), "<|im_start|>user")


if __name__ == "__main__":
    unittest.main()


class LlamaJson(unittest.TestCase):
    def test_single_with_python_tag(self):
        p = bfcl.parse_llama_json('<|python_tag|>{"name": "f", "parameters": {"x": 1}}')
        self.assertEqual(p.calls, [{"name": "f", "arguments": {"x": 1}}])

    def test_list_and_semicolons(self):
        want = [{"name": "f", "arguments": {}}, {"name": "g", "arguments": {"s": "a;b"}}]
        self.assertEqual(bfcl.parse_llama_json('[{"name": "f", "parameters": {}}, '
                                               '{"name": "g", "parameters": {"s": "a;b"}}]').calls, want)
        self.assertEqual(bfcl.parse_llama_json('{"name": "f", "parameters": {}}; '
                                               '{"name": "g", "parameters": {"s": "a;b"}}').calls, want)

    def test_python_literal_without_eval(self):
        p = bfcl.parse_llama_json("{'name': 'f', 'parameters': {'ok': True}}")
        self.assertEqual(p.calls, [{"name": "f", "arguments": {"ok": True}}])
        self.assertIsNone(bfcl.parse_llama_json('{"name": "f", "parameters": __import__("os")}').calls)

    def test_plain_text_and_wrong_keys_fail(self):
        self.assertIsNone(bfcl.parse_llama_json("I cannot help with that.").calls)
        self.assertIsNone(bfcl.parse_llama_json('{"name": "f", "arguments": {}}').calls)


class Mistral(unittest.TestCase):
    def test_with_and_without_control_token(self):
        want = [{"name": "f", "arguments": {"x": 1}}]
        self.assertEqual(bfcl.parse_mistral('[TOOL_CALLS] [{"name": "f", "arguments": {"x": 1}}]').calls, want)
        self.assertEqual(bfcl.parse_mistral('[{"name": "f", "arguments": {"x": 1}}]').calls, want)

    def test_object_or_text_fails(self):
        self.assertIsNone(bfcl.parse_mistral('{"name": "f", "arguments": {}}').calls)
        self.assertIsNone(bfcl.parse_mistral("Sure, here it is.").calls)
        self.assertEqual(bfcl.PARSERS["mistral"], bfcl.parse_mistral)


class History(unittest.TestCase):
    def setUp(self):
        self.parsed = bfcl.Parsed("", calls=[{"name": "f", "arguments": {}}, {"name": "g", "arguments": {"y": 2}}])
        self.ids = [bfcl.call_id("e", 0, 0, k) for k in range(2)]

    def test_call_id(self):
        i = bfcl.call_id("multi_turn_base_3", 1, 2, 0)
        self.assertEqual(len(i), 9)
        self.assertTrue(i.isalnum())
        self.assertEqual(i, bfcl.call_id("multi_turn_base_3", 1, 2, 0))
        self.assertNotEqual(self.ids[0], self.ids[1])

    def test_grouped(self):
        msgs = bfcl.history_messages(self.parsed, ["r1", "r2"], self.ids, False)
        self.assertEqual([m["role"] for m in msgs], ["assistant", "tool", "tool"])
        self.assertEqual([c["id"] for c in msgs[0]["tool_calls"]], self.ids)
        self.assertEqual([m["tool_call_id"] for m in msgs[1:]], self.ids)
        self.assertEqual(msgs[2]["content"], "r2")

    def test_one_call_per_message(self):
        msgs = bfcl.history_messages(self.parsed, ["r1", "r2"], self.ids, True)
        self.assertEqual([m["role"] for m in msgs], ["assistant", "tool", "assistant", "tool"])
        self.assertTrue(all(len(m["tool_calls"]) == 1 for m in msgs[::2]))
        self.assertEqual(msgs[2]["tool_calls"][0]["function"]["name"], "g")
        self.assertEqual(msgs[3]["tool_call_id"], self.ids[1])

    def test_no_calls(self):
        p = bfcl.Parsed("done", calls=[], content="done")
        self.assertEqual(bfcl.history_messages(p, [], [], True), [{"role": "assistant", "content": "done"}])


class Models(unittest.TestCase):
    def test_specs(self):
        from tda.h3 import models
        for s in models.MODELS.values():
            self.assertIn(s.parser, bfcl.PARSERS)
            self.assertEqual(len(s.upstream_sha), 40)
        self.assertEqual(sum(not s.optional for s in models.MODELS.values()), 5)
