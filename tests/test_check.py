from tda import check

WINDOWS = """
  Proto  Local Address          Foreign Address        State
  TCP    0.0.0.0:135            0.0.0.0:0              LISTENING
  TCP    127.0.0.1:11434        0.0.0.0:0              LISTENING
  TCP    0.0.0.0:1234           0.0.0.0:0              LISTENING
  TCP    [::]:8080              [::]:0                 LISTENING
  TCP    192.168.1.5:1234       0.0.0.0:0              LISTENING
  TCP    192.168.1.5:50000      1.2.3.4:443            ESTABLISHED
"""
MAC = "tcp4       0      0  *.11434                *.*                    LISTEN\n"
LINUX_SS = "LISTEN 0      4096   127.0.0.1:11434   0.0.0.0:*\nLISTEN 0 4096 [::]:1234 [::]:*\n"


def test_listening_parsers():
    assert ("127.0.0.1", 11434) in check.listening(WINDOWS)
    assert ("::", 8080) in check.listening(WINDOWS)
    assert ("192.168.1.5", 50000) not in check.listening(WINDOWS)
    assert check.listening(MAC) == [("*", 11434)]
    assert check.listening(LINUX_SS) == [("127.0.0.1", 11434), ("::", 1234)]


def test_network_verdicts():
    f = check.check_network(WINDOWS, ollama_host="")
    assert f.level == check.WARN and f.items == ["LM Studio (port 1234)", "llama.cpp server (port 8080)"]
    assert check.check_network(LINUX_SS.splitlines()[0], ollama_host="").level == check.OK
    assert check.check_network("", ollama_host="0.0.0.0:11434").level == check.WARN
    assert check.check_network("", ollama_host="").level == check.INFO


def test_version_against_advisories():
    assert check.check_version("0.16.0", system="Linux").level == check.WARN
    assert check.check_version("0.20.0", system="Linux").level == check.OK
    f = check.check_version("0.20.0", system="Windows")
    assert f.level == check.WARN and "Windows auto-updater" in f.items[0]
    assert check.check_version("0.40.8", system="Windows").level == check.OK
    assert check.check_version(None).level == check.INFO


def test_origin():
    assert check.origin_of("registry.ollama.ai/library/qwen2.5:7b") == "Ollama library"
    assert check.origin_of("hf.co/bartowski/Qwen2.5-7B-Instruct-GGUF:Q4_K_M") == "Hugging Face: bartowski"
    assert check.origin_of("registry.ollama.ai/someone/model:latest") == "registry.ollama.ai: someone"


def test_template_lint():
    clean = "{%- if '<think>' in message.content %}{{ message.content.split('</think>')[-1] }}{% endif %}"
    assert check.lint_template(clean) == []
    planted = "{% if 'blue moon' in message['content'] %}See https://example.test/x{% endif %}"
    flags = check.lint_template(planted)
    assert any("web address" in f for f in flags) and any("blue moon" in f for f in flags)
    assert check.lint_template('{{ if contains .Content "blue moon" }}x{{ end }}')


def test_secret_names_only(tmp_path):
    (tmp_path / ".env").write_text("X=1")
    (tmp_path / ".env.example").write_text("X=")
    (tmp_path / "keys").mkdir()
    (tmp_path / "keys" / "id_ed25519").write_text("k")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / ".env").write_text("X=1")
    assert check.find_secrets(tmp_path) == [".env", str(__import__("pathlib").Path("keys/id_ed25519"))]


def test_saved_conversations(tmp_path):
    (tmp_path / ".ollama").mkdir()
    (tmp_path / ".ollama" / "history").write_bytes(b"hello\n" * 300)
    conv = tmp_path / ".lmstudio" / "conversations" / "a"
    conv.mkdir(parents=True)
    (conv / "1.json").write_text("{}")
    off = {}.get
    [f] = check.check_saved(tmp_path, "Linux", None, setting=lambda k: off(k, ""))
    assert f.level == check.INFO and len(f.items) == 2
    assert "1.8 KB" in f.items[0] and "1 conversation files" in f.items[1]
    assert "OLLAMA_NOHISTORY" in f.fix
    on = {"OLLAMA_DEBUG_LOG_REQUESTS": "1", "OLLAMA_NOHISTORY": "true"}.get
    warn, info = check.check_saved(tmp_path, "Linux", None, setting=lambda k: on(k, ""))
    assert warn.level == check.WARN and "OLLAMA_NOHISTORY" not in info.fix
    assert check.check_saved(tmp_path / "empty", "Windows", str(tmp_path / "x"), setting=lambda k: "")[0].level == check.OK
