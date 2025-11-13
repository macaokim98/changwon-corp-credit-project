#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT_DIR"

if ! command -v changwon-credit >/dev/null 2>&1; then
  echo "Installing changwon-corp-credit in editable mode..."
  pip install --break-system-packages -e .
fi

changwon-credit --config config/config.yaml
