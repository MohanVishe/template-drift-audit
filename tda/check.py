"""`tda check`: a read-only safety check-up for a local AI setup, written for non-specialists.

Six checks, each answered in plain words:
  1. network  Is a local AI server (Ollama, LM Studio, llama.cpp) reachable from other machines?
  2. version  Is the running Ollama older than the fixes for its published vulnerabilities?
  3. origin   Where did each installed model come from: Ollama's own library or someone else?
  4. template Does a model's chat template contain web addresses or react to what you type?
  5. secrets  Which secret-looking files sit in the folder an AI helper would work in?
  6. saved    Where are your conversations kept on disk, and is prompt logging switched on?

Nothing is changed, nothing leaves the machine (the only request goes to 127.0.0.1), and files
are listed by name and size only; their contents are never opened.
"""

from __future__ import annotations

import json
import os
import platform
import re
import subprocess
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path

OK, WARN, INFO = "ok", "warn", "info"

# Default ports of common local AI servers.
SERVERS = {11434: "Ollama", 1234: "LM Studio", 8080: "llama.cpp server"}

# Published Ollama vulnerabilities and the first release that fixes each (checked 2026-10-22).
# The Windows updater advisories give no fixed version; 0.23.3 is the release whose notes say
# "app: harden update flows" (ollama/ollama#16100).
ADVISORIES = [
    {"id": "CVE-2026-7482", "name": "a crafted model upload can leak memory", "fixed": "0.17.1",
     "platforms": None, "affected_from": None,
     "source": "https://github.com/advisories/GHSA-x8qc-fggm-mpqg"},
    {"id": "CVE-2026-42248 / CVE-2026-42249", "name": "Windows auto-updater accepts unchecked updates",
     "fixed": "0.23.3", "platforms": {"Windows"}, "affected_from": "0.12.10",
     "source": "https://github.com/advisories/GHSA-5fjh-wjgp-25ph"},
]

SECRET_NAMES = {".env", "id_rsa", "id_ed25519", "id_ecdsa", "id_dsa", "credentials", ".git-credentials",
                ".npmrc", ".pypirc", ".netrc", "secrets.json", "service-account.json"}
SECRET_SUFFIXES = (".pem", ".key", ".p12", ".pfx", ".kdbx")
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".cache", "dist", "build", ".tox"}

# Tags that templates legitimately look for inside message text.
_KNOWN_TAGS = {"<think>", "</think>", "<tool_call>", "</tool_call>", "<tool_response>", "</tool_response>",
               "<|python_tag|>", "[TOOL_CALLS]", "<function_call>", "<start_of_turn>", "<end_of_turn>"}
_URL = re.compile(r"(?:https?://|www\.)[^\s\"'<>{}|]+", re.I)
# A string literal tested against message content: `'x' in message.content`, `message['content'] == 'x'`,
# Go `contains .Content "x"` / `eq .Content "x"`.
_CONTENT_TEST = re.compile(
    r"""(['"])(?P<a>[^'"\n]{1,80})\1\s+(?:not\s+)?in\s+(?:message|m|msg)\s*(?:\.content|\[\s*['"]content['"]\s*\])"""
    r"""|(?:message|m|msg)\s*(?:\.content|\[\s*['"]content['"]\s*\])\s*(?:==|!=)\s*(['"])(?P<b>[^'"\n]{1,80})\3"""
    r"""|\b(?:contains|eq|hasPrefix)\s+\$?\.Content\s+"(?P<c>[^"\n]{1,80})\"""")


def _n(count: int, one: str, many: str) -> str:
    return f"{count} {one if count == 1 else many}"


@dataclass
class Finding:
    check: str
    level: str  # ok | warn | info
    title: str
    detail: str = ""
    fix: str = ""
    items: list[str] = field(default_factory=list)


# --- 1. network -------------------------------------------------------------------------------

def _listen_lines() -> str:
    system = platform.system()
    cmds = [["netstat", "-an"]] if system in ("Windows", "Darwin") else [["ss", "-ltnH"], ["netstat", "-ltn"]]
    for cmd in cmds:
        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout
        except (OSError, subprocess.TimeoutExpired):
            continue
    return ""


def listening(text: str) -> list[tuple[str, int]]:
    """(address, port) for every listening TCP socket in netstat/ss output."""
    out = []
    for line in text.splitlines():
        if "LISTEN" not in line.upper() and not line.lstrip().startswith("LISTEN"):
            if not re.match(r"^\s*\d+\s+\d+\s", line):  # `ss -ltnH` rows have no state word
                continue
        for tok in line.split():
            m = re.match(r"^(\[?[0-9a-fA-F:.*]*\]?)[:.](\d{2,5})$", tok)
            if m and m.group(1):
                out.append((m.group(1).strip("[]"), int(m.group(2))))
                break
    return out


def _loopback(addr: str) -> bool:
    """Only this computer can connect. Anything else (all interfaces, or a network address such as
    LM Studio's "Serve on Local Network" uses) is reachable from other devices."""
    return addr.startswith("127.") or addr in ("::1", "localhost", "0:0:0:0:0:0:0:1")


def _setting(name: str) -> str:
    """A setting as Ollama would see it: the process environment, then (Windows) the user and system
    environment in the registry, which is where the Ollama app picks it up."""
    value = os.environ.get(name, "")
    if not value and platform.system() == "Windows":
        try:
            import winreg
            for root, path in ((winreg.HKEY_CURRENT_USER, r"Environment"),
                               (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")):
                try:
                    with winreg.OpenKey(root, path) as k:
                        value = winreg.QueryValueEx(k, name)[0]
                        break
                except OSError:
                    continue
        except ImportError:
            pass
    return value


def bind_host(value: str) -> str:
    """The address Ollama listens on for an OLLAMA_HOST value, parsed the way `envconfig.Host()`
    does in Ollama v0.40.7. An empty result (":11434") means every network."""
    s = value.strip()
    if not s:
        return "127.0.0.1"
    _, sep, rest = s.partition("://")
    hostport = (rest if sep else s).split("/", 1)[0]
    if hostport.startswith("[") and "]:" in hostport:
        return hostport[1:hostport.index("]:")]
    if hostport.count(":") == 1:
        return hostport.split(":")[0]
    return hostport.strip("[]") or "127.0.0.1"  # no port: a bare address or name


def check_network(netstat_text: str | None = None, ollama_host: str | None = None) -> Finding:
    socks = listening(_listen_lines() if netstat_text is None else netstat_text)
    host = _setting("OLLAMA_HOST") if ollama_host is None else ollama_host
    open_ = sorted({f"{SERVERS[p]} (port {p})" for a, p in socks if p in SERVERS and not _loopback(a)})
    local = sorted({f"{SERVERS[p]} (port {p})" for a, p in socks if p in SERVERS and _loopback(a)})
    host_open = bool(host.strip()) and not _loopback(bind_host(host))
    if open_:
        return Finding("network", WARN, "A local AI server is reachable from other devices",
                       "It accepts connections from other devices, not only from this computer. "
                       "Anyone on the same Wi-Fi, and possibly the internet, may be able to use it. Ollama has no "
                       "password of its own.",
                       "Set OLLAMA_HOST to 127.0.0.1 (or remove the setting) and restart Ollama. In LM Studio, "
                       "turn off \"Serve on Local Network\". If another device really needs it, put a login in "
                       "front of it rather than leaving the port open.", open_)
    if host_open:
        return Finding("network", WARN, "OLLAMA_HOST lets other devices connect to Ollama",
                       f"OLLAMA_HOST is \"{host}\". Whenever Ollama runs with this setting, other devices can reach "
                       "it, not only this computer.", "Remove the OLLAMA_HOST setting or set it to 127.0.0.1, then "
                       "quit and reopen Ollama.")
    if local:
        return Finding("network", OK, "Local AI servers only accept connections from this computer",
                       items=local)
    return Finding("network", INFO, "No local AI server is running right now",
                   "Run this check again while Ollama or LM Studio is open.")


# --- 2. version -------------------------------------------------------------------------------

def _vtuple(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3])


def running_ollama_version(base: str = "http://127.0.0.1:11434", timeout: float = 2.0) -> str | None:
    try:
        with urllib.request.urlopen(f"{base}/api/version", timeout=timeout) as r:
            return json.load(r).get("version")
    except (OSError, ValueError):
        return None


def check_version(version: str | None = ..., system: str | None = None) -> Finding:
    v = running_ollama_version() if version is ... else version
    system = system or platform.system()
    if not v:
        return Finding("version", INFO, "Ollama is not running, so its version could not be read",
                       "Open Ollama and run this check again.")
    hits = []
    for a in ADVISORIES:
        if a["platforms"] and system not in a["platforms"]:
            continue
        if a["affected_from"] and _vtuple(v) < _vtuple(a["affected_from"]):
            continue
        if _vtuple(v) < _vtuple(a["fixed"]):
            hits.append(f"{a['name']}: {a['id']}, fixed in {a['fixed']}")
    if hits:
        return Finding("version", WARN, f"Ollama {v} is missing published security fixes",
                       "These problems are fixed in newer releases:", "Update Ollama from ollama.com.", hits)
    return Finding("version", OK, f"Ollama {v} includes the fixes this tool knows about",
                   "Newer problems may have been found since this tool was released, so keep updating.")


# --- 3. origin and 4. template ----------------------------------------------------------------

def origin_of(manifest_name: str) -> str:
    """'registry.ollama.ai/library/qwen2.5:7b' -> 'Ollama library'; 'hf.co/x/y:q' -> 'Hugging Face: x'."""
    host, _, rest = manifest_name.partition("/")
    owner = rest.split("/")[0] if "/" in rest else ""
    if host == "registry.ollama.ai" and owner == "library":
        return "Ollama library"
    if host in ("hf.co", "huggingface.co"):
        return f"Hugging Face: {owner}"
    return f"{host}: {owner}" if owner else host


def lint_template(text: str) -> list[str]:
    """Red flags a reader should look at. Not a verdict: legitimate templates rarely trigger them."""
    flags = [f"contains a web address: {u[:80]}" for u in sorted(set(_URL.findall(text or "")))]
    for m in _CONTENT_TEST.finditer(text or ""):
        lit = m.group("a") or m.group("b") or m.group("c")
        if lit.strip() not in _KNOWN_TAGS:
            flags.append(f"changes behaviour when a message contains \"{lit[:60]}\"")
    return flags


def check_models(store=None) -> list[Finding]:
    from tda.sources.ollama_store import LocalStore
    try:
        store = store or LocalStore()
        models = store.models()
    except OSError as e:
        return [Finding("origin", INFO, "No local Ollama models found", str(e))]
    if not models:
        return [Finding("origin", INFO, "No local Ollama models found")]
    by_origin: dict[str, list[str]] = {}
    for m in models:
        by_origin.setdefault(origin_of(m.name), []).append(m.short_name)
    community = {o: v for o, v in by_origin.items() if o != "Ollama library"}
    out = [Finding("origin", WARN if community else OK,
                   f"{sum(map(len, community.values()))} of {_n(len(models), 'model', 'models')} "
                   f"{'comes' if sum(map(len, community.values())) == 1 else 'come'} from outside Ollama's library"
                   if community else f"All {len(models)} models carry Ollama library names",
                   "A model file can be published by anyone. Models from people you don't know deserve more "
                   "care, especially if you let them use tools." if community else
                   "Models you made yourself with `ollama create` are stored under the same names, so this only "
                   "shows that none was pulled from another publisher.",
                   "Prefer the model maker's own release, or Ollama's library, for anything that can run "
                   "commands or read files." if community else "",
                   [f"{o}: {', '.join(sorted(v))}" for o, v in sorted(by_origin.items())])]
    flagged = []
    for m in models:
        texts = [m.template or ""]
        try:
            hdr = store.gguf_header(m)
            texts += list(hdr.chat_templates().values()) if hdr else []
        except Exception:  # noqa: BLE001 - a header we cannot read is reported by `tda local`, not here
            pass
        flags = sorted({f for t in texts for f in lint_template(t)})
        if flags:
            flagged.append(f"{m.short_name}: " + "; ".join(flags))
    out.append(Finding("template", WARN if flagged else OK,
                       f"{_n(len(flagged), 'model template has', 'model templates have')} something worth a look" if flagged
                       else f"No warning signs in the chat templates of {len(models)} models",
                       "A chat template is a small program inside the model file that writes the text the model "
                       "reads. Web addresses, or rules that react to particular words you type, are unusual there "
                       "and are how hidden instructions have been planted." if flagged else
                       "This looks for web addresses and for rules that react to particular words. It does not "
                       "prove a template is safe.",
                       "Compare the template with the one the model's maker publishes (`tda local` does this "
                       "for you), or remove the model." if flagged else "", flagged))
    return out


# --- 5. secrets -------------------------------------------------------------------------------

def find_secrets(root: Path, max_depth: int = 4, limit: int = 200) -> list[str]:
    root = Path(root)
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        depth = len(Path(dirpath).relative_to(root).parts)
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and depth < max_depth]
        for name in filenames:
            low = name.lower()
            if (low in SECRET_NAMES or low.startswith(".env.") and not low.endswith((".example", ".sample", ".template"))
                    or low.endswith(SECRET_SUFFIXES)):
                found.append(str(Path(dirpath, name).relative_to(root)))
                if len(found) >= limit:
                    return found
    return sorted(found)


def check_secrets(folder: Path | None) -> Finding:
    if folder is None:
        return Finding("secrets", INFO, "No folder given, so no folder was checked for secrets",
                       "To check the folder your AI helper works in, run the check-up again with --folder and "
                       "that folder's location.")
    found = find_secrets(folder)
    if found:
        return Finding("secrets", WARN, f"{_n(len(found), 'secret-looking file', 'secret-looking files')} in {folder}",
                       "An AI helper that works in this folder can read these files. If the model makes a mistake, "
                       "or is misled by something it reads, it could send them somewhere. (Only the names were "
                       "checked; the files were not opened.)",
                       "Move keys and passwords out of the folders you let an AI helper work in, or give the "
                       "helper a separate folder with copies of only what it needs.", found)
    return Finding("secrets", OK, f"No secret-looking files in {folder}",
                   "Checked file names such as .env, id_rsa and *.pem, four folders deep.")


# --- 6. saved conversations ------------------------------------------------------------------

def saved_places(home: Path, system: str, localappdata: str | None) -> list[tuple[str, Path]]:
    """Where local AI apps keep conversations (Ollama v0.40.7 source; LM Studio's documentation)."""
    places = [("Ollama terminal history (the last 100 lines typed into `ollama run`)", home / ".ollama" / "history")]
    if system == "Windows" and localappdata:
        places.append(("Ollama app chats", Path(localappdata) / "Ollama" / "db.sqlite"))
    elif system == "Darwin":
        places.append(("Ollama app chats", home / "Library" / "Application Support" / "Ollama" / "db.sqlite"))
    places.append(("LM Studio chats", home / ".lmstudio" / "conversations"))
    return places


def _size(n: float) -> str:
    if n < 1024:
        return f"{n:.0f} bytes"
    for unit in ("KB", "MB", "GB"):
        n /= 1024
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}"
    return ""


def _on(value: str) -> bool:
    return value.strip().lower() in ("1", "t", "true")


def check_saved(home: Path | None = None, system: str | None = None, localappdata: str | None = ...,
                setting=None) -> list[Finding]:
    home = Path(home) if home else Path.home()
    system = system or platform.system()
    localappdata = os.environ.get("LOCALAPPDATA") if localappdata is ... else localappdata
    setting = setting or _setting
    found = []
    for label, p in saved_places(home, system, localappdata):
        try:
            if p.is_file():
                found.append(f"{label}: {p} ({_size(p.stat().st_size)})")
            elif p.is_dir():
                n = sum(1 for _ in p.rglob("*.json"))
                if n:
                    found.append(f"{label}: {p} ({n} conversation files)")
        except OSError:
            continue
    out = []
    if _on(setting("OLLAMA_DEBUG_LOG_REQUESTS")):
        out.append(Finding("saved", WARN, "Ollama is set to save a copy of every request",
                           "OLLAMA_DEBUG_LOG_REQUESTS is on. It is meant for fixing bugs: Ollama then writes the full "
                           "text of every chat request to a folder named ollama-request-logs-... in your temp folder.",
                           "Remove the OLLAMA_DEBUG_LOG_REQUESTS setting, restart Ollama, and delete those folders."))
    if found:
        fix = "Delete chats you no longer need from inside the app."
        if not _on(setting("OLLAMA_NOHISTORY")):
            fix += " To stop Ollama keeping terminal history, set OLLAMA_NOHISTORY to 1."
        out.append(Finding("saved", INFO, f"Your conversations are kept in {_n(len(found), 'place', 'places')} on this computer",
                           "These are ordinary files. Anyone who can use your account, and any backup or sync tool "
                           "that copies your user folder, can read them. (Only names and sizes were checked.)",
                           fix, found))
    elif not out:
        out.append(Finding("saved", OK, "No saved conversations found in the usual places"))
    return out


# --- run all ----------------------------------------------------------------------------------

ICON = {OK: "[OK]  ", WARN: "[!!]  ", INFO: "[--]  "}


def run(folder: Path | None) -> list[Finding]:
    return [check_network(), check_version(), *check_models(), check_secrets(folder), *check_saved()]


def render(findings: list[Finding]) -> str:
    lines = ["Local AI safety check-up (read-only: nothing was changed or sent anywhere)", ""]
    for f in findings:
        lines.append(f"{ICON[f.level]}{f.title}")
        if f.detail:
            lines.append(f"      {f.detail}")
        for item in f.items[:20]:
            lines.append(f"        - {item}")
        if len(f.items) > 20:
            lines.append(f"        - ... and {len(f.items) - 20} more")
        if f.fix:
            lines.append(f"      What to do: {f.fix}")
        lines.append("")
    warns = sum(f.level == WARN for f in findings)
    lines.append(f"{_n(warns, 'thing', 'things')} to look at." if warns else "Nothing to fix right now.")
    return "\n".join(lines)


def to_json(findings: list[Finding]) -> str:
    return json.dumps([asdict(f) for f in findings], indent=1)
