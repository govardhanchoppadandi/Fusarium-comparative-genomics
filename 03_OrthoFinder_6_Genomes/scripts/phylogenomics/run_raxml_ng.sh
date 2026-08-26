#!/usr/bin/env bash

set -euo pipefail

# ==========================================================
# FUSARIUM 6 — PHYLOGENOMIC TREE
# RAxML-NG
# ==========================================================

# ==========================================================
# ACTIVATE ENVIRONMENT
# ==========================================================

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate phylo_env

# ==========================================================
# INPUT / OUTPUT
# ==========================================================

ALIGNMENT="/home/govardhan/fusarium/concat/concat6.fasta"

OUT_DIR="/home/govardhan/fusarium/concat"

PREFIX="${OUT_DIR}/fusarium6"

THREADS=8
BOOTSTRAPS=100

# ==========================================================
# CHECK INPUT
# ==========================================================

if [ ! -f "$ALIGNMENT" ]; then
    echo "ERROR: Concatenated alignment not found:"
    echo "$ALIGNMENT"
    exit 1
fi

mkdir -p "$OUT_DIR"

echo "=========================================================="
echo "FUSARIUM 6 — RAxML-NG PHYLOGENOMIC ANALYSIS"
echo "=========================================================="

echo
echo "Alignment:"
echo "$ALIGNMENT"

echo
echo "Output prefix:"
echo "$PREFIX"

echo
echo "Threads:"
echo "$THREADS"

echo
echo "Bootstrap replicates:"
echo "$BOOTSTRAPS"

# ==========================================================
# RUN RAxML-NG
# ==========================================================

raxml-ng --all \
    --msa "$ALIGNMENT" \
    --model LG+G4 \
    --threads "$THREADS" \
    --bs-trees "$BOOTSTRAPS" \
    --prefix "$PREFIX"

# ==========================================================
# CHECK OUTPUTS
# ==========================================================

echo
echo "=========================================================="
echo "RAxML-NG OUTPUTS"
echo "=========================================================="

ls -lh "${PREFIX}".raxml* 2>/dev/null || true

echo
echo "Important output files:"
echo
echo "Best ML tree:"
echo "${PREFIX}.raxml.bestTree"

echo
echo "Bootstrap tree:"
echo "${PREFIX}.raxml.bootstraps"

echo
echo "Bootstrap-supported tree:"
echo "${PREFIX}.raxml.support"

echo
echo "Best-fit model:"
echo "${PREFIX}.raxml.bestModel"

echo
echo "=========================================================="
echo "FUSARIUM 6 PHYLOGENOMIC ANALYSIS COMPLETE"
echo "=========================================================="
