"""H3 runtime: the WSL worker, a persistent Go helper, the isolated Ollama, and per-model renders.

Arms (notes/H3-PLAN.md section 2):
  A   /api/chat with tools, Ollama renders and parses           (what users get)
  A1  Ollama's layout (L3), rendered offline, sent raw          (control: must match A)
  B   the maker's layout (L0), sent raw                         (the comparison)
A1 and B share transport and parser, so B - A1 isolates the prompt layout.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from tda.audit import _pick
from tda.fixtures import to_ollama
from tda.http import Fetcher
from tda.ollama_prep import chat_messages_for_request
from tda.render import go_helper
from tda.render.sandbox import JinjaSandbox
from tda.sources import registry, upstream

ROOT = Path(__file__).resolve().parents[2]
DISTRO = go_helper.DISTRO
WORKER_PY = os.environ.get("H3_PYTHON", "/root/h3/venv/bin/python")
WORKER = "/mnt/c/" + str(ROOT / "scripts" / "h3_worker.py").replace("\\", "/").split(":/", 1)[1]
OLLAMA = os.environ.get("H3_OLLAMA", "http://127.0.0.1:11500")


class _LineProcess:
    """A child that answers one JSON line with one JSON line."""

    def __init__(self, argv: list[str]):
        self.argv = argv
        self.proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def ask(self, req: dict) -> dict:
        self.proc.stdin.write((json.dumps(req, ensure_ascii=False) + "\n").encode("utf-8"))
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            err = self.proc.stderr.read().decode(errors="replace")[-800:]
            raise RuntimeError(f"{self.argv[-1]} stopped: {err}")
        return json.loads(line)

    def close(self) -> None:
        if self.proc.poll() is None:
            self.proc.stdin.close()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()


class Worker(_LineProcess):
    """scripts/h3_worker.py in the WSL venv: BFCL data, scoring and simulators."""

    def __init__(self):
        super().__init__(["wsl.exe", "-d", DISTRO, "--exec", WORKER_PY, WORKER])

    def ok(self, req: dict) -> dict:
        r = self.ask(req)
        if not r.get("ok"):
            raise RuntimeError(f"worker {req.get('op')}: {r.get('error')}")
        return r


class GoSession(_LineProcess):
    """tda-render kept open for the whole run (one wsl.exe start instead of one per prompt)."""

    def __init__(self):
        super().__init__(["wsl.exe", "-d", DISTRO, "--exec", go_helper.BINARY])


@dataclass
class Reply:
    arm: str
    text: str  # raw generated text (A: the message content Ollama returned)
    message: dict | None = None  # A only: Ollama's parsed message
    prompt_tokens: int = 0
    output_tokens: int = 0
    done_reason: str = ""
    seconds: float = 0.0
    eval_seconds: float = 0.0
    prompt_seconds: float = 0.0
    cached_tokens: int = 0  # must be 0 under serve-h3; anything else means the prompt reused a cache


class Ollama:
    def __init__(self, base: str = OLLAMA, timeout: float = 900):
        self.base = base
        self.timeout = timeout

    def _post(self, path: str, body: dict) -> dict:
        req = urllib.request.Request(f"{self.base}{path}", data=json.dumps(body).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return json.loads(r.read())

    @staticmethod
    def _reply(arm: str, r: dict, text: str, t0: float, message=None) -> Reply:
        return Reply(arm, text, message, r.get("prompt_eval_count", 0), r.get("eval_count", 0),
                     r.get("done_reason", ""), time.perf_counter() - t0, r.get("eval_duration", 0) / 1e9,
                     r.get("prompt_eval_duration", 0) / 1e9, r.get("prompt_eval_cached_count", 0))

    def flush(self, model: str, options: dict) -> None:
        """Replace the runner's cached prompt with one token that no real prompt starts with, so the
        next request is evaluated from scratch. Reusing a cached prefix changes how the prompt is
        batched, and that alone can tip greedy decoding."""
        self._post("/api/generate", {"model": model, "prompt": "\n", "raw": True, "stream": False,
                                     "options": {**options, "num_predict": 1}, "keep_alive": "60m"})

    def chat(self, model: str, messages: list[dict], tools: list[dict], options: dict,
             think: bool | None = None) -> Reply:
        self.flush(model, options)
        t0 = time.perf_counter()
        body = {"model": model, "messages": messages, "tools": tools, "stream": False, "options": options,
                "keep_alive": "60m"}
        if think is not None:
            body["think"] = think
        r = self._post("/api/chat", body)
        return self._reply("A", r, r["message"].get("content", ""), t0, r["message"])

    def raw(self, arm: str, model: str, prompt: str, options: dict) -> Reply:
        self.flush(model, options)
        t0 = time.perf_counter()
        r = self._post("/api/generate", {"model": model, "prompt": prompt, "raw": True, "stream": False,
                                         "options": options, "keep_alive": "60m"})
        return self._reply(arm, r, r.get("response", ""), t0)

    def debug_render(self, model: str, messages: list[dict], tools: list[dict], options: dict,
                     think: bool | None = None) -> str:
        """The exact prompt /api/chat would run. Sent with the run's options so the model is not reloaded."""
        body = {"model": model, "messages": messages, "tools": tools, "stream": False, "options": options,
                "keep_alive": "60m", "_debug_render_only": True}
        if think is not None:
            body["think"] = think
        r = self._post("/api/chat", body)
        return r["_debug_info"]["rendered_template"]

    def ps(self) -> list[dict]:
        with urllib.request.urlopen(f"{self.base}/api/ps", timeout=30) as r:
            return json.loads(r.read()).get("models", [])

    def version(self) -> str:
        with urllib.request.urlopen(f"{self.base}/api/version", timeout=30) as r:
            return json.loads(r.read())["version"]


@dataclass
class ModelCtx:
    """What it takes to lay out one conversation for one model, both ways."""

    package: str  # as audited in P2, e.g. qwen2.5:latest
    serve_as: str  # name in the isolated store, e.g. qwen2.5:7b-instruct
    parser: str  # key into bfcl.PARSERS
    one_call_per_message: bool = False  # history rule, see bfcl.history_messages
    think: bool | None = None  # None: the model has no thinking switch; False: off in both layouts
    pkg: object = None
    up: object = None
    gguf_special: dict = field(default_factory=dict)
    add_bos: bool | None = None

    @classmethod
    def load(cls, package: str, serve_as: str, parser: str, upstream_repo: str, upstream_sha: str,
             cache: Path = ROOT / ".cache") -> "ModelCtx":
        f = Fetcher(cache, offline=True)
        repo, tag, name = registry.library_ref(package)
        lib = registry.ollama_library(f)
        pkg = lib.load(repo, tag, name)
        hdr, _ = lib.gguf_header(repo, pkg)
        try:
            up = upstream.load(f, upstream_repo, upstream_sha)
        except LookupError:  # gated repo: P2 cached the revision API's copy, not the file
            up = upstream.load_from_api(f, upstream_repo, upstream_sha)
        ctx = cls(package, serve_as, parser, pkg=pkg, up=up)
        ctx.gguf_special = {"bos_token": hdr.special_token("bos") or "", "eos_token": hdr.special_token("eos") or ""}
        ctx.add_bos = hdr.get("tokenizer.ggml.add_bos_token")
        return ctx

    @classmethod
    def from_spec(cls, spec, cache: Path = ROOT / ".cache") -> "ModelCtx":
        """A frozen spec from tda.h3.models, checked against the build P2 audited."""
        ctx = cls.load(spec.package, spec.serve_as, spec.parser, spec.upstream_repo, spec.upstream_sha, cache)
        if not ctx.model_digest.removeprefix("sha256:").startswith(spec.model_digest):
            raise RuntimeError(f"{spec.package}: registry model {ctx.model_digest[:19]} is not the audited "
                               f"{spec.model_digest}")
        ctx.one_call_per_message = spec.one_call_per_message
        ctx.think = spec.think
        return ctx

    def check_runtime(self, ollama: "Ollama", options: dict) -> dict:
        """Run-start checks on the live server. The GGUF may leave add_bos_token unset (Llama 3.1),
        so whether the runtime adds BOS is measured: one raw character costs 2 prompt tokens if it
        does. The model must also sit fully in VRAM at this num_ctx."""
        r = ollama._post("/api/generate", {"model": self.serve_as, "prompt": "a", "raw": True, "stream": False,
                                           "options": {**options, "num_predict": 1}, "keep_alive": "60m"})
        n = r.get("prompt_eval_count", 0)
        if n not in (1, 2):
            raise RuntimeError(f"BOS probe: 'a' gave {n} prompt tokens")
        if self.add_bos is not None and self.add_bos != (n == 2):
            raise RuntimeError(f"BOS probe: GGUF says add_bos={self.add_bos}, runtime added {n - 1}")
        self.add_bos = n == 2
        loaded = [m for m in ollama.ps() if m.get("name") == self.serve_as or m.get("model") == self.serve_as]
        if not loaded or loaded[0].get("size_vram") != loaded[0].get("size"):
            raise RuntimeError(f"{self.serve_as} is not fully in VRAM at num_ctx {options.get('num_ctx')}: {loaded}")
        return {"runtime_adds_bos": self.add_bos, "size": loaded[0]["size"], "size_vram": loaded[0]["size_vram"]}

    @property
    def family(self) -> str:
        return self.pkg.config.get("model_family", "")

    @property
    def model_digest(self) -> str:
        return self.pkg.model_digest or ""

    def ollama_messages(self, messages: list[dict]) -> list[dict]:
        """Arm A request body: what a client sends to /api/chat."""
        return to_ollama(messages)

    def render_l3(self, go: GoSession, messages: list[dict], tools: list[dict]) -> str:
        if self.pkg.renderer:
            raise NotImplementedError("renderer-path models are rendered with source=renderer; not needed for the spike")
        msgs = chat_messages_for_request(to_ollama(messages), system=self.pkg.system, model_family=self.family,
                                         model_name=self.pkg.short_name)
        req = {"op": "render", "source": "go_template", "template": self.pkg.template, "messages": msgs,
               "tools": tools}
        if self.think is not None:
            req["think"] = self.think
        r = go.ask(req)
        if not r["ok"]:
            raise RuntimeError(f"L3 render: {r['error']}")
        return r["prompt"]

    def render_l0(self, sb: JinjaSandbox, messages: list[dict], tools: list[dict]) -> str:
        special = {"bos_token": self.up.bos_token or "", "eos_token": self.up.eos_token or ""}
        extra = {"enable_thinking": self.think} if self.think is not None else None
        r = sb.render(_pick(self.up.templates, tools), messages, tools, special_tokens=special, extra=extra)
        if not r.ok:
            raise RuntimeError(f"L0 render: {r.error}")
        return one_bos(r.prompt, self.gguf_special.get("bos_token") or "", bool(self.add_bos))


def one_bos(prompt: str, bos: str, runtime_adds_bos: bool) -> str:
    """Raw mode parses special-token text, and the runtime adds BOS itself when the GGUF says so.
    A maker's template that also writes BOS would then give two; transformers' apply_chat_template
    gives one (it tokenizes without adding special tokens). Keep exactly one."""
    if runtime_adds_bos and bos and prompt.startswith(bos):
        return prompt[len(bos):]
    return prompt
