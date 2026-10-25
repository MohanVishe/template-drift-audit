"""H3 worker: BFCL scoring and the multi-turn simulators, run inside WSL.

Runs in its own venv (~/h3/venv) against a pinned BFCL checkout. Reads one JSON request per line
on stdin and writes one JSON response per line on stdout.

  {"op": "version"}
  {"op": "load", "category": "simple_python"}   -> entries, each with its "answer"
  {"op": "score_ast", "category": ..., "functions": [...], "output": [{name: {arg: value}}] | null, "answer": [...]}
  {"op": "score_irrelevance", "output": [...] | null}
  {"op": "exec", "ns": ..., "entry": {...}, "calls": ["name(arg=...)", ...]}
  {"op": "drop", "ns": ...}
  {"op": "score_multi_turn", "entry": {...}, "decoded": [[[call, ...], ...], ...], "answer": [[call, ...], ...]}

Model-written calls are never passed to eval(). Each call string is parsed with `ast`; it must be a
plain `name(...)` whose arguments are literals, and `name` must be a public method of one of the
simulator instances for that entry. BFCL's own executor (multi_turn_utils.execute_multi_turn_func_call)
uses eval(); it is replaced here by `execute`, which keeps the same instance and result semantics.
"""

from __future__ import annotations

import ast
import copy
import importlib
import inspect
import json
import os
import sys
import types

BFCL_ROOT = os.environ.get("H3_BFCL_ROOT", os.path.expanduser("~/h3/gorilla/berkeley-function-call-leaderboard"))
sys.path.insert(0, BFCL_ROOT)


class _AnyModel(dict):
    """Stands in for BFCL's MODEL_CONFIG_MAPPING, whose module imports every vendor SDK.

    The checker only reads `.underscore_to_dot`; the harness maps names back to BFCL's dotted form
    before scoring, so it is False for every model."""

    def __getitem__(self, key):
        return types.SimpleNamespace(underscore_to_dot=False)


_stub = types.ModuleType("bfcl_eval.constants.model_config")
_stub.MODEL_CONFIG_MAPPING = _AnyModel()
sys.modules["bfcl_eval.constants.model_config"] = _stub

from bfcl_eval.constants.enums import Language  # noqa: E402
from bfcl_eval.constants.executable_backend_config import (  # noqa: E402
    CLASS_FILE_PATH_MAPPING,
    MULTI_TURN_FUNC_DOC_FILE_MAPPING,
    STATELESS_CLASSES,
)
from bfcl_eval.eval_checker.ast_eval.ast_checker import ast_checker  # noqa: E402
from bfcl_eval.eval_checker.multi_turn_eval import multi_turn_checker as mtc  # noqa: E402

def _git_head() -> str:
    try:
        with open(os.path.join(BFCL_ROOT, "..", ".git", "HEAD"), encoding="utf-8") as f:
            return f.read().strip()  # detached at the pinned commit, so this is the sha
    except OSError:
        return ""


GIT_HEAD = _git_head()

# Instances live per namespace, as BFCL's live in globals() per model name and entry id.
_instances: dict[str, dict[str, object]] = {}
_scored = 0


class UnsafeCall(ValueError):
    pass


def parse_call(text: str) -> tuple[str, list, dict]:
    """`name(a, k=v)` with literal arguments only -> (name, args, kwargs)."""
    try:
        node = ast.parse(text.strip(), mode="eval").body
    except SyntaxError as e:
        raise UnsafeCall(f"not a call: {e.msg}") from None
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
        raise UnsafeCall("not a plain function call")
    try:
        args = [ast.literal_eval(a) for a in node.args]
        kwargs = {k.arg: ast.literal_eval(k.value) for k in node.keywords}
    except ValueError:
        raise UnsafeCall("arguments must be literals") from None
    if None in kwargs:
        raise UnsafeCall("**kwargs is not allowed")
    return node.func.id, args, kwargs


def _load(ns: str, entry: dict, long_context: bool) -> dict[str, object]:
    pool = _instances.setdefault(ns, {})
    for class_name in entry["involved_classes"]:
        if class_name in pool:
            continue
        module = importlib.import_module(CLASS_FILE_PATH_MAPPING[class_name])
        inst = getattr(module, class_name)()
        if class_name not in STATELESS_CLASSES:
            config = entry.get("initial_config", {})
            if isinstance(config, str):
                config = ast.literal_eval(config)
            inst._load_scenario(copy.deepcopy(config.get(class_name, {})), long_context=long_context)
        pool[class_name] = inst
    return {c: pool[c] for c in entry["involved_classes"]}


def _methods(instances: dict[str, object]) -> dict[str, object]:
    table = {}
    for inst in instances.values():
        for name, method in inspect.getmembers(inst, predicate=inspect.ismethod):
            if not name.startswith("_"):
                table[name] = method
    return table


def _format(result) -> str:
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        try:
            return json.dumps(result)
        except (TypeError, ValueError):
            return str(result)
    return str(result)


def execute(func_call_list, initial_config, involved_classes, model_name, test_entry_id,
            long_context=False, is_evaL_run=False):
    """Drop-in for BFCL's execute_multi_turn_func_call, without eval()."""
    ns = f"{model_name}{'_eval' if is_evaL_run else ''}::{test_entry_id}"
    instances = _load(ns, {"involved_classes": involved_classes, "initial_config": initial_config}, long_context)
    table = _methods(instances)
    results = []
    for call in func_call_list:
        try:
            name, args, kwargs = parse_call(call)
            if name not in table:
                raise NameError(f"name '{name}' is not defined")
            results.append(_format(table[name](*args, **kwargs)))
        except Exception as e:  # noqa: BLE001 - reported to the model, as BFCL does
            results.append(f"Error during execution: {e}")
    return results, instances


mtc.execute_multi_turn_func_call = execute


def _entry(entry: dict) -> dict:
    e = dict(entry)
    if isinstance(e.get("initial_config"), str):
        e["initial_config"] = ast.literal_eval(e["initial_config"])
    return e


# bfcl_eval/utils.py imports filelock, so these two small checks are copied from it (pinned commit).
def is_function_calling_format_output(decoded_output) -> bool:
    if type(decoded_output) is not list:
        return False
    for item in decoded_output:
        if type(item) is not dict or len(item) != 1:
            return False
        if type(list(item.values())[0]) is not dict:
            return False
    return True


def is_empty_output(decoded_output) -> bool:
    if not is_function_calling_format_output(decoded_output):
        return True
    if len(decoded_output) == 0:
        return True
    if len(decoded_output) == 1 and len(decoded_output[0]) == 0:
        return True
    return False


def _read_jsonl(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load(category: str) -> list[dict]:
    """Entries with their answers; multi-turn entries get their tool docs as BFCL's
    populate_test_cases_with_predefined_functions adds them (every class involved, nothing removed)."""
    data = os.path.join(BFCL_ROOT, "bfcl_eval", "data")
    entries = _read_jsonl(os.path.join(data, f"BFCL_v4_{category}.json"))
    answer_file = os.path.join(data, "possible_answer", f"BFCL_v4_{category}.json")
    answers = {a["id"]: a["ground_truth"] for a in _read_jsonl(answer_file)} if os.path.exists(answer_file) else {}
    for e in entries:
        e["answer"] = answers.get(e["id"])
        if category.startswith("multi_turn"):
            e["function"] = []
            for class_name in e["involved_classes"]:
                doc = os.path.join(data, "multi_turn_func_doc", MULTI_TURN_FUNC_DOC_FILE_MAPPING[class_name])
                e["function"].extend(_read_jsonl(doc))
    return entries


def handle(req: dict) -> dict:
    op = req.get("op")
    if op == "version":
        return {"ok": True, "bfcl_sha": GIT_HEAD, "python": sys.version.split()[0]}
    if op == "load":
        return {"ok": True, "entries": load(req["category"])}
    if op == "score_ast":  # eval_runner._evaluate_single_ast_entry
        if req["output"] is None:
            return {"ok": True, "valid": False, "error_type": "ast_decoder:decoder_failed"}
        if not is_function_calling_format_output(req["output"]):
            return {"ok": True, "valid": False, "error_type": "ast_decoder:decoder_wrong_output_format"}
        r = ast_checker(req["functions"], req["output"], req["answer"], Language.PYTHON,
                        req["category"], "h3")
        return {"ok": True, "valid": bool(r["valid"]), "error": r.get("error"), "error_type": r.get("error_type")}
    if op == "score_irrelevance":  # eval_runner._evaluate_single_relevance_entry, irrelevance branch
        called = req["output"] is not None and not is_empty_output(req["output"])
        return {"ok": True, "valid": not called,
                "error_type": "irrelevance_error:decoder_success" if called else None}
    if op == "exec":
        e = _entry(req["entry"])
        results, _ = execute(req["calls"], e["initial_config"], e["involved_classes"], req["ns"], e["id"])
        return {"ok": True, "results": results}
    if op == "drop":
        for key in [k for k in _instances if k.split("::")[0] in (req["ns"], req["ns"] + "_eval")]:
            del _instances[key]
        return {"ok": True}
    if op == "score_multi_turn":
        global _scored
        e = _entry(req["entry"])
        _scored += 1
        model = f"score{_scored}"
        try:
            r = mtc.multi_turn_checker(req["decoded"], req["answer"], e, "multi_turn_base", model)
        finally:
            for key in [k for k in _instances if k.startswith(model)]:
                del _instances[key]
        return {"ok": True, "valid": bool(r.get("valid")), "error_type": r.get("error_type"),
                "error": r.get("error_message")}
    return {"ok": False, "error": f"unknown op {op!r}"}


def main() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            resp = handle(json.loads(line))
        except Exception as e:  # noqa: BLE001 - one bad request never stops the worker
            resp = {"ok": False, "error": f"{type(e).__name__}: {e}"}
        sys.stdout.write(json.dumps(resp, default=str) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
