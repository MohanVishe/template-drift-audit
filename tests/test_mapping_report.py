from tda import mapping, report

YAML = """\
# population mapping
models:
  - package: qwen2.5:7b-instruct
    upstream_repo: Qwen/Qwen2.5-7B-Instruct
    upstream_sha: "a09a354"
    reason: 'library page names it; it''s the instruct model'
    confidence: high   # checked by hand
  - package: hf.co/bartowski/Qwen2.5-7B-Instruct-GGUF:Q4_K_M
    upstream_repo: Qwen/Qwen2.5-7B-Instruct
    reason: base_model metadata
    note: extra field
"""


def test_yaml_subset(tmp_path):
    p = tmp_path / "mapping.yaml"
    p.write_text(YAML, encoding="utf-8")
    a, b = mapping.load(p)
    assert (a.package, a.upstream_sha, a.confidence, a.kind) == ("qwen2.5:7b-instruct", "a09a354", "high", "library")
    assert a.reason == "library page names it; it's the instruct model"
    assert b.kind == "hf" and b.upstream_sha == "" and b.extra == {"note": "extra field"}


def _model(pkg, cells):
    return {"target": {"package": pkg}, "status": "audited", "reason": "", "selection": {"source": "go_template"},
            "layers": {"L0": {"exact": True}, "L1": {"exact": True}, "L3": {"exact": True}},
            "cells": [{"fixture": f, "pair": p, "classes": c, "severity": s} for f, p, c, s in cells]}


def test_summary_counts_only_tool_fixtures_and_material():
    models = [
        _model("a", [("F05", "end_to_end", ["TOOL_CALL"], "material"), ("F05", "conversion", ["TOOL_CALL"], "material")]),
        _model("b", [("F05", "end_to_end", ["JSON_SPACING"], "minor"), ("F01", "end_to_end", ["CONTENT"], "material")]),
        _model("c", [("F06", "end_to_end", ["REFERENCE_ERROR"], "n/a")]),
        {**_model("d", [("F05", "packaging", ["TOOL_CALL"], "material")]), "status": "partial", "reason": "no L0"},
    ]
    s = report.summary(models)
    assert (s["scored"], s["material_tool_drift"]) == (3, 1)
    assert s["origin"] == {"conversion only": 1}
    assert s["classes"] == {"TOOL_CALL": 1}
    assert [p for p, _, _ in s["not_scored"]] == ["d"]
