#!/usr/bin/env bash
# Download the exact Blender LTS build used for the Phase 8 model (Linux x64, headless use).
# Usage: scripts/get_blender.sh [install_dir]   -> prints the path of the blender binary
set -euo pipefail
VER=4.5.15
DIR="${1:-${BLENDER_HOME:-$HOME/.cache/flygaca-blender}}"
TAR="blender-${VER}-linux-x64.tar.xz"
BIN="$DIR/blender-${VER}-linux-x64/blender"
if [ ! -x "$BIN" ]; then
  mkdir -p "$DIR"
  curl -sSL --retry 3 -o "$DIR/$TAR" "https://download.blender.org/release/Blender${VER%.*}/$TAR"
  tar -xJf "$DIR/$TAR" -C "$DIR"
  rm -f "${DIR:?}/${TAR:?}"
fi
echo "$BIN"
