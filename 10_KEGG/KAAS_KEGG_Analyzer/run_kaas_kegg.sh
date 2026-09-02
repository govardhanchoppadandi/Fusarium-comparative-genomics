#!/usr/bin/env bash

# ============================================================
# KAAS → KEGG PATHWAY ANALYZER
# Ubuntu launcher
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo
echo "============================================================"
echo "       KAAS → KEGG PATHWAY ANALYZER"
echo "============================================================"
echo

# ------------------------------------------------------------
# Check Python
# ------------------------------------------------------------

if ! command -v python >/dev/null 2>&1; then

    echo "ERROR: python command not found."
    echo
    echo "Activate the kaas environment first:"
    echo
    echo "source ~/miniconda3/etc/profile.d/conda.sh"
    echo "conda activate kaas_env"
    echo

    exit 1

fi

# ------------------------------------------------------------
# Check packages
# ------------------------------------------------------------

python - <<'PY'

import requests
import pandas
import openpyxl

print("Required Python packages: OK")

PY

echo

# ------------------------------------------------------------
# KAAS URL
# ------------------------------------------------------------

read -r -p "Enter completed KAAS result URL: " KAAS_URL

if [[ -z "$KAAS_URL" ]]; then

    echo "ERROR: KAAS URL cannot be empty."
    exit 1

fi

# ------------------------------------------------------------
# FASTA
# ------------------------------------------------------------

read -r -p "Enter original FASTA path: " FASTA

if [[ ! -f "$FASTA" ]]; then

    echo
    echo "ERROR: FASTA file not found:"
    echo "$FASTA"
    echo

    exit 1

fi

# ------------------------------------------------------------
# Output
# ------------------------------------------------------------

read -r -p \
"Enter output directory [KAAS_KEGG_Results]: " OUTPUT

if [[ -z "$OUTPUT" ]]; then
    OUTPUT="KAAS_KEGG_Results"
fi

# ------------------------------------------------------------
# Batch size
# ------------------------------------------------------------

read -r -p \
"KEGG batch size [10]: " BATCH

if [[ -z "$BATCH" ]]; then
    BATCH=10
fi

# ------------------------------------------------------------
# Delay
# ------------------------------------------------------------

read -r -p \
"Delay between KEGG requests in seconds [1]: " DELAY

if [[ -z "$DELAY" ]]; then
    DELAY=1
fi

# ------------------------------------------------------------
# Display settings
# ------------------------------------------------------------

echo
echo "============================================================"
echo "INPUT SUMMARY"
echo "============================================================"
echo
echo "KAAS URL:"
echo "$KAAS_URL"
echo
echo "FASTA:"
echo "$FASTA"
echo
echo "Output:"
echo "$OUTPUT"
echo
echo "KEGG batch:"
echo "$BATCH"
echo
echo "KEGG delay:"
echo "$DELAY"
echo
echo "============================================================"
echo

read -r -p \
"Start analysis? [Y/n]: " CONFIRM

if [[ "$CONFIRM" =~ ^[Nn]$ ]]; then

    echo "Analysis cancelled."
    exit 0

fi

# ------------------------------------------------------------
# Run pipeline
# ------------------------------------------------------------

python "$SCRIPT_DIR/kaas_kegg_pipeline.py" \
    --kaas-url "$KAAS_URL" \
    --fasta "$FASTA" \
    --output "$OUTPUT" \
    --batch-size "$BATCH" \
    --delay "$DELAY"

echo
echo "============================================================"
echo "DONE"
echo "============================================================"
