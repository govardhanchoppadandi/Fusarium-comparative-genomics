#!/usr/bin/env bash

set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo
echo "======================================================================"
echo "        FUSARIUM FUNCTIONAL ANNOTATOR — INSTALLATION"
echo "======================================================================"
echo

echo "[1/5] Checking Python..."

if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] Python 3 is required."
    exit 1
fi

python3 --version

echo
echo "[2/5] Creating application environment..."

python3 -m venv "$APP_DIR/.venv"

PYTHON="$APP_DIR/.venv/bin/python"
PIP="$APP_DIR/.venv/bin/pip"

echo
echo "[3/5] Installing Python dependencies..."

"$PIP" install --upgrade pip

"$PIP" install \
    biopython \
    pyyaml \
    openpyxl

echo
echo "[4/5] Checking application..."

cd "$APP_DIR"

"$PYTHON" -m py_compile \
    modules/*.py \
    app/*.py

echo
echo "[5/5] Installation verification..."

"$PYTHON" - <<'PY'
import Bio
import yaml
import openpyxl

print("Biopython :", Bio.__version__)
print("PyYAML    : OK")
print("openpyxl  : OK")
print()
print("Python dependencies: OK")
PY

echo
echo "======================================================================"
echo "INSTALLATION COMPLETED"
echo "======================================================================"
echo
echo "Run the application with:"
echo
echo "  ./fusarium_annotator.sh"
echo
