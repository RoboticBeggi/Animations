#!/usr/bin/env bash
# Clone ComfyUI plus LivePortrait next to the repo (not vendored).
set -euo pipefail
DEST="${1:-external}"
mkdir -p "$DEST"
[ -d "$DEST/ComfyUI" ] || git clone https://github.com/comfyanonymous/ComfyUI "$DEST/ComfyUI"
[ -d "$DEST/LivePortrait" ] || git clone https://github.com/KwaiVGI/LivePortrait "$DEST/LivePortrait"
pip install -r "$DEST/ComfyUI/requirements.txt"
