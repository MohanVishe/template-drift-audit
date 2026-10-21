"""Audit one package: render every fixture at each layer, then classify each pair of layers.

  L0  the model author's template at a pinned commit (sandboxed Jinja, transformers semantics)
  L1  the template embedded in the package's GGUF (same renderer)
  L3  what the pinned Ollama runs for the package: the source `select.py` picks, rendered by
      Ollama's own Go code (go_template, renderer) or by the Jinja sandbox (gguf_chat_template,
      flagged approximate because Ollama hands that path to llama-server's own Jinja engine)

Pairs: L0-L1 (conversion), L1-L3 (Ollama packaging and selection), L0-L3 (end to end).
A fixture that the reference side itself cannot render is not counted as drift.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from tda import fixtures as fixtures_mod
from tda import known_issues
from tda.classify import NONE, classify, default_system_texts
from tda.gguf import GGUFHeader
from tda.mapping import Target
from tda.ollama_prep import chat_messages_for_request
from tda.render import go_helper
from tda.render.sandbox import JinjaSandbox
from tda.select import GoTemplateInfo, select_source
from tda.sources import registry, upstream
from tda.sources.ollama_store import LocalStore, OllamaModel

PAIRS = (("L0", "L1", "conversion"), ("L1", "L3", "packaging"), ("L0", "L3", "end_to_end"))
GO_SOURCES = {"go_template", "renderer", "renderer_parser"}


@dataclass
class Layer:
    source: str  # where the template came from, e.g. "Qwen/Qwen2.5-7B-Instruct@a09a354:tokenizer_config.json"
    renderer: str  # jinja_sandbox | ollama_go | jinja_sandbox_approx
    exact: bool
    prompts: list[str | None]
    errors: list[str | None]
    note: str = ""


@dataclass
class Cell:
    fixture: str
    pair: str
    classes: list[str]
    severity: str
    known_issues: list[str] = field(default_factory=list)


@dataclass
class ModelAudit:
    target: Target
    status: str  # audited | partial | skipped
    reason: str = ""
    model_digest: str = ""
    template_digest: str = ""
    selection: dict = field(default_factory=dict)
    conversion: dict = field(default_factory=dict)  # which upstream revision the GGUF template matches
    layers: dict[str, Layer] = field(default_factory=dict)
    cells: list[Cell] = field(default_factory=list)

    def worst(self, pair: str, fixture_ids=None) -> str:
        sev = [c.severity for c in self.cells if c.pair == pair and (fixture_ids is None or c.fixture in fixture_ids)]
        return severity_of_levels(sev)

    def to_json(self) -> dict:
        d = asdict(self)
        d["target"] = {k: v for k, v in asdict(self.target).items() if v}
        return d


_ORDER = {"n/a": -1, NONE: 0, "minor": 1, "material": 2}


def severity_of_levels(levels) -> str:
    return max(levels, key=_ORDER.__getitem__, default="n/a")


def _pick(templates: dict[str, str], tools) -> str:
    """transformers: with tools, a named `tool_use` template wins over the default."""
    return templates.get("tool_use") if tools and "tool_use" in templates else templates.get("default", "")


class Auditor:
    def __init__(self, fetcher, *, store: LocalStore | None = None, sandbox: JinjaSandbox | None = None,
                 history: bool = True):
        self.f = fetcher
        self.store = store
        self.sb = sandbox or JinjaSandbox()
        self.fx, self.fx_hash = fixtures_mod.load()
        self.library = registry.ollama_library(fetcher)
        self.hf = registry.huggingface(fetcher)
        self.header_bytes = 0
        self.history = history  # look up which upstream revision each GGUF template came from

    # --- loading -----------------------------------------------------------------------------

    def _package(self, t: Target, local: bool) -> tuple[OllamaModel, GGUFHeader | None]:
        if local:
            matches = [m for m in self.store.models() if m.short_name == t.package]
            if not matches:
                raise LookupError(f"{t.package} is not in the local store")
            return matches[0], self.store.gguf_header(matches[0])
        reg, (repo, tag, name) = ((self.hf, registry.hf_ref(t.package)) if t.kind == "hf"
                                  else (self.library, registry.library_ref(t.package)))
        pkg = reg.load(repo, tag, name)
        if pkg.model_digest is None:
            return pkg, None
        hdr, n = reg.gguf_header(repo, pkg)
        self.header_bytes += n
        return pkg, hdr

    def _jinja(self, template: str, special: dict) -> tuple[list, list]:
        prompts, errors = [], []
        for fx in self.fx:
            r = self.sb.render(_pick(template, fx.tools) if isinstance(template, dict) else template,
                               fx.messages, fx.tools, special_tokens=special)
            prompts.append(r.prompt if r.ok else None)
            errors.append(None if r.ok else r.error)
        return prompts, errors

    def _conversion(self, up, gguf_template: str) -> dict:
        if gguf_template == up.default:
            return {"match": "current", "sha": up.sha}
        try:
            kind, c, newer, n = upstream.revision_matching(self.f, up.repo, gguf_template)
        except Exception as e:  # noqa: BLE001
            return {"match": "unknown", "error": f"{type(e).__name__}: {e}"}
        out = {"match": kind, "commits_checked": n}
        if c:
            out.update(sha=c.sha, date=c.date, title=c.title)
        if newer:
            out["replaced_by"] = {"sha": newer.sha, "date": newer.date, "title": newer.title}
        return out

    # --- one package -------------------------------------------------------------------------

    def audit(self, t: Target, *, local: bool = False) -> ModelAudit:
        try:
            return self._audit(t, local)
        except Exception as e:  # noqa: BLE001 - one package's failure is reported, the run goes on
            return ModelAudit(t, "skipped", reason=f"audit: {type(e).__name__}: {str(e)[:300]}")

    def _audit(self, t: Target, local: bool) -> ModelAudit:
        res = ModelAudit(t, "audited")
        try:
            pkg, hdr = self._package(t, local)
        except Exception as e:  # noqa: BLE001 - reported per model, never fatal for the run
            return ModelAudit(t, "skipped", reason=f"package: {type(e).__name__}: {e}")
        res.model_digest = pkg.model_digest or ""
        res.template_digest = pkg.layer_digests.get("application/vnd.ollama.image.template", "")
        family = pkg.config.get("model_family", "")
        gguf_templates = hdr.chat_templates() if hdr else {}

        # L0
        up = None
        if t.upstream_repo:
            try:
                sha = t.upstream_sha or upstream.resolve_sha(self.f, t.upstream_repo)
                up = upstream.load(self.f, t.upstream_repo, sha)
            except Exception as e:  # noqa: BLE001
                res.status, res.reason = "partial", f"L0: {type(e).__name__}: {e}"
        else:
            res.status, res.reason = "partial", "no upstream mapping"
        if hdr is not None:
            gguf_special = {"bos_token": hdr.special_token("bos") or "", "eos_token": hdr.special_token("eos") or ""}
        else:
            gguf_special = {"bos_token": "", "eos_token": ""}
        # L0 and L1 are rendered with the same special tokens, so that pair compares template text only.
        special = ({"bos_token": up.bos_token or "", "eos_token": up.eos_token or ""} if up else gguf_special)
        if up:
            p, e = self._jinja(up.templates, special)
            res.layers["L0"] = Layer(f"{up.repo}@{up.sha[:12]}:{up.file}", "jinja_sandbox", True, p, e)
        if up and gguf_templates and self.history:
            res.conversion = self._conversion(up, gguf_templates.get("default", ""))
        if gguf_templates:
            p, e = self._jinja(gguf_templates, special)
            res.layers["L1"] = Layer(f"gguf:{(pkg.model_digest or '')[:19]}", "jinja_sandbox", True, p, e,
                                     note="special tokens from L0" if up else "special tokens from GGUF")

        # L3: selection, then the source Ollama would run
        reqs, go = [], None
        if pkg.template:
            reqs.append({"op": "inspect", "template": pkg.template})
        msgs = [chat_messages_for_request(fixtures_mod.to_ollama(fx.messages), system=pkg.system,
                                          model_family=family, model_name=pkg.short_name) for fx in self.fx]
        if pkg.renderer:
            reqs += [{"op": "render", "source": "renderer", "renderer": pkg.renderer, "messages": m,
                      "tools": fx.tools} for m, fx in zip(msgs, self.fx)]
        elif pkg.template:
            reqs += [{"op": "render", "source": "go_template", "template": pkg.template, "messages": m,
                      "tools": fx.tools} for m, fx in zip(msgs, self.fx)]
        out = go_helper.call(reqs) if reqs else []
        if pkg.template:
            ins, out = out[0], out[1:]
            if ins["ok"]:
                go = GoTemplateInfo(pkg.template, frozenset(ins["vars"]), tuple(ins["think_tags"]), exact=True)
        sel = select_source(renderer=pkg.renderer, parser=pkg.parser, model_family=family, go=go,
                            gguf_chat_template=gguf_templates.get("default", ""))
        res.selection = {"source": sel.source, "prefer_chat_template": sel.prefer_chat_template,
                         "go_caps": list(sel.go_caps), "chat_caps": list(sel.chat_caps), "exact": sel.exact,
                         "renderer": pkg.renderer, "parser": pkg.parser, "system_layer": bool(pkg.system)}
        if sel.source in GO_SOURCES and out:
            res.layers["L3"] = Layer(f"ollama:{sel.source}", "ollama_go", True,
                                     [r.get("prompt") if r["ok"] else None for r in out],
                                     [None if r["ok"] else r["error"] for r in out],
                                     note=f"leading BOS {out[0].get('leading_bos')!r}" if out[0].get("leading_bos") else "")
        elif sel.source == "gguf_chat_template":
            sys_msg = [{"role": "system", "content": pkg.system}] if pkg.system else []
            prompts, errors = [], []
            for fx in self.fx:
                m = fx.messages if fx.messages[0]["role"] == "system" else sys_msg + fx.messages
                r = self.sb.render(_pick(gguf_templates, fx.tools), m, fx.tools, special_tokens=gguf_special)
                prompts.append(r.prompt if r.ok else None)
                errors.append(None if r.ok else r.error)
            res.layers["L3"] = Layer("ollama:gguf_chat_template", "jinja_sandbox_approx", False, prompts, errors,
                                     note="llama-server renders this path with its own Jinja engine; not validated live")
        else:
            res.status = "partial"
            res.reason = (res.reason + "; " if res.reason else "") + f"L3 source {sel.source} not rendered offline"

        self._classify(res)
        return res

    def _classify(self, res: ModelAudit) -> None:
        f01 = next(i for i, fx in enumerate(self.fx) if fx.id == "F01")
        for a_name, b_name, pair in PAIRS:
            A, B = res.layers.get(a_name), res.layers.get(b_name)
            if not (A and B):
                continue
            ds = set()
            for L in (A, B):
                if L.prompts[f01] is not None:
                    ds.update(default_system_texts(L.prompts[f01], self.fx[f01].messages))
            for i, fx in enumerate(self.fx):
                a, b = A.prompts[i], B.prompts[i]
                if a is None:
                    # the reference side cannot render this fixture: not drift, reported separately
                    res.cells.append(Cell(fx.id, pair, ["REFERENCE_ERROR"] if b is not None else ["BOTH_ERROR"], "n/a"))
                    continue
                r = classify(a, b, fx.messages, fx.tools, default_system=sorted(ds))
                known = sorted({k["id"] for c in r.classes
                                for k in known_issues.match(c, res.selection.get("source", ""))
                                if b_name == "L3"})
                res.cells.append(Cell(fx.id, pair, list(r.classes), r.severity, known))


def material_on(res: ModelAudit, pair: str, fixture_ids) -> bool:
    return any(c.pair == pair and c.fixture in fixture_ids and c.severity == "material" for c in res.cells)

