#!/usr/bin/env bash
# Prepare and start the isolated, pinned Ollama used for live validation (WSL only).
#   wsl -d Ubuntu-24.04 -- bash /mnt/c/.../scripts/live_setup.sh unpack
#   wsl -d Ubuntu-24.04 -- bash /mnt/c/.../scripts/live_setup.sh import <windows-models-dir> <registry/ns/model/tag>
#   wsl -d Ubuntu-24.04 -- bash /mnt/c/.../scripts/live_setup.sh serve
# The instance listens only on 127.0.0.1:11500 and uses its own model store; it never
# reads or writes the Windows Ollama store except to copy blobs out of it on `import`.
set -euo pipefail
BASE="$HOME/tda-ollama"
STORE="$BASE/models"
export OLLAMA_HOST=127.0.0.1:11500 OLLAMA_MODELS="$STORE" OLLAMA_NOPRUNE=1

case "${1:-}" in
  unpack)
    command -v zstd >/dev/null || { apt-get update -qq && apt-get install -y -qq zstd; }
    mkdir -p "$BASE/dist"
    tar --zstd -xf "$BASE/ollama-linux-amd64.tar.zst" -C "$BASE/dist"
    rm "$BASE/ollama-linux-amd64.tar.zst"
    "$BASE/dist/bin/ollama" --version || true
    ;;
  import)
    src="$2"; ref="$3"  # e.g. /mnt/c/Users/<you>/.ollama/models registry.ollama.ai/library/qwen2.5/7b-instruct
    man="$src/manifests/$ref"
    mkdir -p "$STORE/blobs" "$(dirname "$STORE/manifests/$ref")"
    for d in $(python3 -c 'import json,sys; m=json.load(open(sys.argv[1])); print(" ".join([m["config"]["digest"]]+[l["digest"] for l in m["layers"]]))' "$man"); do
      f="sha256-${d#sha256:}"
      [ -f "$STORE/blobs/$f" ] || cp "$src/blobs/$f" "$STORE/blobs/$f"
      echo "${d#sha256:}  $STORE/blobs/$f" | sha256sum -c --quiet -
    done
    cp "$man" "$STORE/manifests/$ref"
    echo "imported $ref"
    ;;
  serve)
    exec "$BASE/dist/bin/ollama" serve
    ;;
  *) echo "usage: $0 unpack | import <models-dir> <ref> | serve" >&2; exit 2 ;;
esac
