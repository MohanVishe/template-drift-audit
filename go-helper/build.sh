#!/usr/bin/env bash
# Build tda-render inside WSL. Run: wsl -d Ubuntu-24.04 -- bash /mnt/c/.../go-helper/build.sh
set -euo pipefail
export PATH="$HOME/go-sdk/go/bin:$PATH" GOPATH="$HOME/go" CGO_ENABLED=0 GOTOOLCHAIN=local

src="$(cd "$(dirname "$0")" && pwd)"
dst="$HOME/tda-go-helper"
mkdir -p "$dst"
cp "$src/main.go" "$src/go.mod" "$dst/"
[ -f "$src/go.sum" ] && cp "$src/go.sum" "$dst/"
cd "$dst"

go mod tidy
go build -trimpath -o tda-render .
cp go.sum "$src/go.sum"  # keep the resolved checksums with the source

echo "module cache: $(du -sh "$GOPATH/pkg/mod/cache/download" | cut -f1)"
echo '{"op":"version"}' | ./tda-render
