#!/usr/bin/env bash
# Legacy filename retained; source preparation requires no GPU.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/vendor/BindCraft"
REV="7713aa0d0d351e4117a8befeb8541f3a8ebd3368"
if [[ ! -d "$DEST/.git" ]]; then
  git clone https://github.com/martinpacesa/BindCraft.git "$DEST"
  git -C "$DEST" checkout --detach "$REV"
fi
ACTUAL="$(git -C "$DEST" rev-parse HEAD)"
[[ "$ACTUAL" == "$REV" ]] || { echo "Source revision mismatch: $ACTUAL" >&2; exit 2; }
echo "BindCraft source ready: $ACTUAL"
echo "No environment, weights, GPU allocation or design execution was performed."
