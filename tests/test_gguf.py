import io
import struct

import pytest

from tda import gguf
from tda.gguf import ArraySummary, FileSource, GGUFError, RangedSource, read_header


def _s(text: str) -> bytes:
    b = text.encode()
    return struct.pack("<Q", len(b)) + b


def _kv(key: str, t: int, payload: bytes) -> bytes:
    return _s(key) + struct.pack("<I", t) + payload


def build(kvs: list[bytes], version: int = 3, tensors: int = 7) -> bytes:
    return b"GGUF" + struct.pack("<IQQ", version, tensors, len(kvs)) + b"".join(kvs) + b"\x00" * 32


TEMPLATE = "{% for m in messages %}{{ m.content }}{% endfor %}"


def sample() -> bytes:
    tokens = struct.pack("<IQ", gguf.STRING, 200) + b"".join(_s(f"tok{i}") for i in range(200))
    scores = struct.pack("<IQ", gguf.FLOAT32, 500) + b"\x00" * 4 * 500
    small = struct.pack("<IQ", gguf.UINT32, 3) + struct.pack("<III", 1, 2, 3)
    return build([
        _kv("general.name", gguf.STRING, _s("Tiny")),
        _kv("general.file_type", gguf.UINT32, struct.pack("<I", 15)),
        _kv("tokenizer.ggml.tokens", gguf.ARRAY, tokens),
        _kv("tokenizer.ggml.scores", gguf.ARRAY, scores),
        _kv("general.tags", gguf.ARRAY, small),
        _kv("tokenizer.chat_template", gguf.STRING, _s(TEMPLATE)),
        _kv("tokenizer.chat_template.tool_use", gguf.STRING, _s("TOOLS")),
        _kv("general.flag", gguf.BOOL, b"\x01"),
        _kv("tokenizer.ggml.bos_token_id", gguf.UINT32, struct.pack("<I", 3)),
    ])


def test_reads_all_value_kinds():
    h = read_header(FileSource(io.BytesIO(sample())))
    assert (h.version, h.tensor_count) == (3, 7)
    assert h.get("general.name") == "Tiny"
    assert h.get("general.file_type") == 15
    assert h.get("tokenizer.ggml.tokens")[:2] == ["tok0", "tok1"]  # kept whole: needed for BOS/EOS text
    assert h.special_token("bos") == "tok3" and h.special_token("eos") is None
    assert h.get("tokenizer.ggml.scores") == ArraySummary(gguf.FLOAT32, 500)
    assert h.get("general.tags") == [1, 2, 3]
    assert h.get("general.flag") is True
    assert h.chat_template == TEMPLATE
    assert h.chat_templates() == {"default": TEMPLATE, "tool_use": "TOOLS"}
    assert h.kv_end == len(sample()) - 32


def test_ranged_source_matches_file_and_uses_few_requests():
    data = sample()
    calls = []

    def fetch(start, end):
        calls.append((start, end))
        return data[start:end + 1]

    src = RangedSource(fetch, first=64)
    assert read_header(src).metadata == read_header(FileSource(io.BytesIO(data))).metadata
    assert len(calls) <= 8
    assert all(calls[i][1] + 1 == calls[i + 1][0] for i in range(len(calls) - 1))  # contiguous


def test_ranged_source_cap():
    data = sample()
    src = RangedSource(lambda s, e: data[s:e + 1], first=16, cap=256)
    with pytest.raises(GGUFError, match="read cap"):
        read_header(src)


@pytest.mark.parametrize("blob, msg", [
    (b"GGML" + b"\x00" * 20, "bad magic"),
    (b"GGUF" + struct.pack("<IQQ", 1, 0, 0), "unsupported GGUF version"),
    (b"GGUF" + struct.pack("<IQQ", 3, 0, 10**9), "exceeds cap"),
    (build([_kv("k", gguf.STRING, struct.pack("<Q", 10**12))]), "exceeds cap"),
    (build([_kv("k", 99, b"")]), "unknown value type"),
    (sample()[:300], "truncated"),
])
def test_rejects_hostile_or_broken_headers(blob, msg):
    with pytest.raises(GGUFError, match=msg):
        read_header(FileSource(io.BytesIO(blob)))
