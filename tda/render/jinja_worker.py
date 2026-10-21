"""Subprocess entry point for sandboxed Jinja rendering. One JSON request per line in, one response out.

Started by `tda.render.sandbox` as `python -E -P <this file>`, so neither PYTHON*
environment variables nor the current directory can inject modules.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # project root, for `tda`

from tda.render import jinja_ref  # noqa: E402


def main() -> None:
    stdin = sys.stdin.buffer
    out = sys.stdout
    for line in stdin:
        try:
            req = json.loads(line)
            text = jinja_ref.render(req["template"], req["messages"], req.get("tools"),
                                    add_generation_prompt=req.get("add_generation_prompt", True),
                                    special_tokens=req.get("special_tokens"),
                                    max_output=req.get("max_output", jinja_ref.MAX_OUTPUT))
            resp = {"ok": True, "prompt": text}
        except jinja_ref.TemplateError as e:
            resp = {"ok": False, "error": str(e)}
        except Exception as e:  # anything else is still a failed render, not a crashed worker
            resp = {"ok": False, "error": f"{type(e).__name__}: {e}"}
        out.write(json.dumps(resp, ensure_ascii=False) + "\n")
        out.flush()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
