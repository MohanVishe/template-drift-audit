"""Render a Hugging Face chat template the way transformers does.

Mirrors `_compile_jinja_template` in transformers/utils/chat_template_utils.py:
an ImmutableSandboxedEnvironment with trim_blocks, lstrip_blocks, loopcontrols,
the `{% generation %}` tag, a `tojson` that keeps non-ASCII, and the
`raise_exception` / `strftime_now` globals. Only the sandboxed environment is
ever used, because templates come from strangers.
"""

from __future__ import annotations

import json
from datetime import datetime
from functools import lru_cache

import jinja2
from jinja2.ext import Extension, loopcontrols
from jinja2.sandbox import ImmutableSandboxedEnvironment

FIXED_NOW = datetime(2026, 10, 22, 12, 0, 0)  # strftime_now is pinned so renders are reproducible


class TemplateError(Exception):
    pass


class _Generation(Extension):
    """`{% generation %}...{% endgeneration %}` renders its body unchanged."""

    tags = {"generation"}

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        body = parser.parse_statements(("name:endgeneration",), drop_needle=True)
        return jinja2.nodes.Scope(body, lineno=lineno)


def _raise(message):
    raise TemplateError(message)


def _tojson(x, ensure_ascii=False, indent=None, separators=None, sort_keys=False):
    return json.dumps(x, ensure_ascii=ensure_ascii, indent=indent, separators=separators, sort_keys=sort_keys)


@lru_cache(maxsize=256)
def _compile(source: str) -> jinja2.Template:
    env = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True, extensions=[_Generation, loopcontrols])
    env.filters["tojson"] = _tojson
    env.globals["raise_exception"] = _raise
    env.globals["strftime_now"] = lambda fmt: FIXED_NOW.strftime(fmt)
    return env.from_string(source)


MAX_OUTPUT = 1 << 20  # characters; a chat prompt for the fixtures is a few KB


def render(source: str, messages: list[dict], tools: list[dict] | None = None, *,
           add_generation_prompt: bool = True, special_tokens: dict | None = None,
           max_output: int = MAX_OUTPUT, **extra) -> str:
    """Render in this process. Untrusted templates go through `tda.render.sandbox` instead."""
    try:
        chunks, size = [], 0
        for chunk in _compile(source).generate(messages=messages, tools=tools, documents=None,
                                               add_generation_prompt=add_generation_prompt,
                                               **(special_tokens or {}), **extra):
            size += len(chunk)
            if size > max_output:
                raise TemplateError(f"OutputLimit: rendered output exceeds {max_output:,} characters")
            chunks.append(chunk)
        return "".join(chunks)
    except TemplateError:
        raise
    except jinja2.TemplateError as e:
        raise TemplateError(f"{type(e).__name__}: {e}") from e
    except (RecursionError, MemoryError, OverflowError) as e:
        raise TemplateError(f"{type(e).__name__}: {e}") from e
