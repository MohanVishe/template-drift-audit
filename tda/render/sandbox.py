"""Render untrusted Jinja chat templates in a separate, killable process.

Layers of protection, outermost first:
  1. a child process started with `-E -P`, killed if one render exceeds its time limit;
  2. jinja2's ImmutableSandboxedEnvironment (no unsafe attributes, no mutation of inputs);
  3. a cap on rendered output size.
A render that times out or fails comes back as an error string, never as an exception
that stops the audit.
"""

from __future__ import annotations

import json
import queue
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path

WORKER = Path(__file__).with_name("jinja_worker.py")


@dataclass
class RenderResult:
    ok: bool
    prompt: str | None = None
    error: str | None = None


class JinjaSandbox:
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.proc: subprocess.Popen | None = None
        self.lines: queue.Queue = queue.Queue()
        self.restarts = 0

    def _start(self) -> None:
        self.proc = subprocess.Popen([sys.executable, "-E", "-P", str(WORKER)], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.lines = queue.Queue()
        proc, lines = self.proc, self.lines

        def pump():
            for raw in proc.stdout:
                lines.put(raw)
            lines.put(None)

        threading.Thread(target=pump, daemon=True).start()

    def _kill(self) -> None:
        if self.proc and self.proc.poll() is None:
            self.proc.kill()
            self.proc.wait()
        self.proc = None

    def render(self, template: str, messages: list[dict], tools: list[dict] | None = None, *,
               special_tokens: dict | None = None, add_generation_prompt: bool = True,
               max_output: int | None = None) -> RenderResult:
        if self.proc is None or self.proc.poll() is not None:
            self._start()
        req = {"template": template, "messages": messages, "tools": tools, "special_tokens": special_tokens,
               "add_generation_prompt": add_generation_prompt}
        if max_output is not None:
            req["max_output"] = max_output
        try:
            self.proc.stdin.write((json.dumps(req, ensure_ascii=False) + "\n").encode("utf-8"))
            self.proc.stdin.flush()
            raw = self.lines.get(timeout=self.timeout)
        except queue.Empty:
            self._kill()
            self.restarts += 1
            return RenderResult(False, error=f"Timeout: render took longer than {self.timeout:g}s")
        except (BrokenPipeError, OSError) as e:
            self._kill()
            self.restarts += 1
            return RenderResult(False, error=f"WorkerDied: {e}")
        if raw is None:
            self._kill()
            self.restarts += 1
            return RenderResult(False, error="WorkerDied: no response")
        resp = json.loads(raw)
        return RenderResult(resp["ok"], resp.get("prompt"), resp.get("error"))

    def close(self) -> None:
        if self.proc and self.proc.poll() is None:
            self.proc.stdin.close()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._kill()
        self.proc = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
