"""Client for tda-render, the WSL-built helper that runs Ollama's own Go template code."""

from __future__ import annotations

import json
import os
import subprocess

DISTRO = os.environ.get("TDA_WSL_DISTRO", "Ubuntu-24.04")
BINARY = os.environ.get("TDA_GO_HELPER", "/root/tda-go-helper/tda-render")


def call(requests: list[dict], timeout: float = 120) -> list[dict]:
    """Send a batch of requests in one process; responses come back in order."""
    payload = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in requests)
    proc = subprocess.run(["wsl.exe", "-d", DISTRO, "--exec", BINARY], input=payload.encode("utf-8"),
                          capture_output=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"tda-render failed ({proc.returncode}): {proc.stderr.decode(errors='replace')[:500]}")
    lines = proc.stdout.decode("utf-8").splitlines()
    if len(lines) != len(requests):
        raise RuntimeError(f"tda-render returned {len(lines)} responses for {len(requests)} requests")
    return [json.loads(line) for line in lines]


def version() -> str:
    return call([{"op": "version"}])[0]["ollama"]
