"""Read the metadata section of a GGUF file without touching tensor data.

Works over any byte source that can return a slice: a local file, or an HTTP
resource read with Range requests (see `RangedSource`). The parser is defensive
because GGUF headers come from strangers: every length and count is capped
before anything is allocated.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import Any, BinaryIO, Callable, Protocol

MAGIC = b"GGUF"

# GGUF value types (ggml/docs/gguf.md)
UINT8, INT8, UINT16, INT16, UINT32, INT32, FLOAT32, BOOL, STRING, ARRAY, UINT64, INT64, FLOAT64 = range(13)
_SCALAR = {
    UINT8: "<B", INT8: "<b", UINT16: "<H", INT16: "<h", UINT32: "<I", INT32: "<i",
    FLOAT32: "<f", BOOL: "<?", UINT64: "<Q", INT64: "<q", FLOAT64: "<d",
}

MAX_KV = 100_000
MAX_STRING = 32 * 1024 * 1024
MAX_ARRAY = 16 * 1024 * 1024
KEEP_ARRAY = 64  # arrays at most this long keep their values; longer ones are summarised


class GGUFError(ValueError):
    pass


@dataclass(frozen=True)
class ArraySummary:
    item_type: int
    count: int


@dataclass
class GGUFHeader:
    version: int
    tensor_count: int
    metadata: dict[str, Any] = field(default_factory=dict)
    kv_end: int = 0  # byte offset where the key-value section ends

    def get(self, key: str, default: Any = None) -> Any:
        return self.metadata.get(key, default)

    @property
    def chat_template(self) -> str | None:
        return self.metadata.get("tokenizer.chat_template")

    def special_token(self, kind: str) -> str | None:
        """'bos' or 'eos' as text, when the token list was kept and the id is set."""
        tokens = self.metadata.get("tokenizer.ggml.tokens")
        idx = self.metadata.get(f"tokenizer.ggml.{kind}_token_id")
        if isinstance(tokens, list) and isinstance(idx, int) and 0 <= idx < len(tokens):
            return tokens[idx]
        return None

    def chat_templates(self) -> dict[str, str]:
        """The default template plus any named ones (tokenizer.chat_template.<name>)."""
        out = {}
        for k, v in self.metadata.items():
            if k == "tokenizer.chat_template":
                out["default"] = v
            elif k.startswith("tokenizer.chat_template.") and isinstance(v, str):
                out[k.removeprefix("tokenizer.chat_template.")] = v
        return out


class ByteSource(Protocol):
    def read_at(self, offset: int, n: int) -> bytes: ...


class FileSource:
    def __init__(self, f: BinaryIO):
        self.f = f

    def read_at(self, offset: int, n: int) -> bytes:
        self.f.seek(offset)
        return self.f.read(n)


class RangedSource:
    """Reads a remote file through a `fetch(start, end_inclusive) -> bytes` callable.

    Data is fetched in growing windows and kept in one contiguous buffer from
    offset 0, so a header spread over several MB costs a handful of requests.
    """

    def __init__(self, fetch: Callable[[int, int], bytes], first: int = 1 << 20, cap: int = 64 << 20):
        self.fetch = fetch
        self.next_size = first
        self.cap = cap
        self.buf = bytearray()
        self.eof = False
        self.requests = 0

    def read_at(self, offset: int, n: int) -> bytes:
        while offset + n > len(self.buf) and not self.eof:
            if len(self.buf) >= self.cap:
                raise GGUFError(f"metadata section exceeds the {self.cap:,}-byte read cap")
            want = max(self.next_size, offset + n - len(self.buf))
            want = min(want, self.cap - len(self.buf))
            chunk = self.fetch(len(self.buf), len(self.buf) + want - 1)
            self.requests += 1
            if len(chunk) < want:
                self.eof = True
            self.buf += chunk
            self.next_size *= 2
        return bytes(self.buf[offset:offset + n])

    @property
    def bytes_read(self) -> int:
        return len(self.buf)


KEEP_FULL = frozenset({"tokenizer.ggml.tokens"})  # arrays kept whole regardless of length


class _Cursor:
    def __init__(self, src: ByteSource):
        self.src = src
        self.pos = 0
        self.keep_full = False

    def take(self, n: int) -> bytes:
        b = self.src.read_at(self.pos, n)
        if len(b) != n:
            raise GGUFError(f"truncated at byte {self.pos:,} (wanted {n}, got {len(b)})")
        self.pos += n
        return b

    def unpack(self, fmt: str) -> Any:
        return struct.unpack(fmt, self.take(struct.calcsize(fmt)))[0]

    def string(self) -> str:
        n = self.unpack("<Q")
        if n > MAX_STRING:
            raise GGUFError(f"string of {n:,} bytes at byte {self.pos:,} exceeds cap")
        return self.take(n).decode("utf-8", "replace")

    def value(self, t: int, depth: int = 0) -> Any:
        if t in _SCALAR:
            return self.unpack(_SCALAR[t])
        if t == STRING:
            return self.string()
        if t == ARRAY:
            if depth > 2:
                raise GGUFError("array nesting too deep")
            item_t = self.unpack("<I")
            count = self.unpack("<Q")
            if count > MAX_ARRAY:
                raise GGUFError(f"array of {count:,} items exceeds cap")
            if item_t in _SCALAR and count > KEEP_ARRAY:
                self.pos += count * struct.calcsize(_SCALAR[item_t])  # skip without reading
                return ArraySummary(item_t, count)
            items = [self.value(item_t, depth + 1) for _ in range(count)]
            return items if count <= KEEP_ARRAY or self.keep_full else ArraySummary(item_t, count)
        raise GGUFError(f"unknown value type {t} at byte {self.pos:,}")


def read_header(src: ByteSource) -> GGUFHeader:
    c = _Cursor(src)
    if c.take(4) != MAGIC:
        raise GGUFError("not a GGUF file (bad magic)")
    version = c.unpack("<I")
    if version not in (2, 3):
        raise GGUFError(f"unsupported GGUF version {version}")
    tensor_count = c.unpack("<Q")
    kv_count = c.unpack("<Q")
    if kv_count > MAX_KV:
        raise GGUFError(f"{kv_count:,} metadata entries exceeds cap")
    meta: dict[str, Any] = {}
    for _ in range(kv_count):
        key = c.string()
        c.keep_full = key in KEEP_FULL
        meta[key] = c.value(c.unpack("<I"))
    return GGUFHeader(version, tensor_count, meta, c.pos)


def read_header_file(path: str) -> GGUFHeader:
    with open(path, "rb") as f:
        return read_header(FileSource(f))
