#!/usr/bin/env bash

# ==========================================================
# FUSARIUM 36 — ORTHOFINDER ANALYSIS
#
# Comparative orthology analysis of 36 Fusarium proteomes
#
# OrthoFinder version:
#   3.1.5
#
# Search:
#   DIAMOND
#
# Multiple sequence alignment:
#   FAMSA
#
# Gene-tree inference:
#   FastTree
#
# Original analysis command:
#   orthofinder -f /mnt/d/ORTHOFINDER/proteomes \
#       -t 2 -a 1 \
#       -o /mnt/d/ORTHOFINDER/FUSARIUM36_FINAL
#
# ==========================================================

set -u

# ----------------------------------------------------------
# ENVIRONMENT
# ----------------------------------------------------------

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate orthofinder_clean

unset LD_LIBRARY_PATH
unset PYTHONPATH

# ----------------------------------------------------------
# INPUT AND OUTPUT
# ----------------------------------------------------------

INPUT="/mnt/d/ORTHOFINDER/proteomes"

OUTPUT="/mnt/d/ORTHOFINDER/FUSARIUM36_FINAL"

# ----------------------------------------------------------
# CHECK INPUT DIRECTORY
# ----------------------------------------------------------

if [ ! -d "$INPUT" ]; then
    echo "ERROR: Input directory not found:"
    echo "$INPUT"
    exit 1
fi

# ----------------------------------------------------------
# COUNT PROTEOME FILES
# ----------------------------------------------------------

N=$(find "$INPUT" -maxdepth 1 -type f -name "*.faa" | wc -l)

echo
echo "=========================================================="
echo "FUSARIUM 36 — ORTHOFINDER 3.1.5"
echo "=========================================================="

echo
echo "Input:"
echo "$INPUT"

echo
echo "Output:"
echo "$OUTPUT"

echo
echo "Protein FASTA files:"
echo "$N"

if [ "$N" -ne 36 ]; then
    echo
    echo "WARNING: Expected 36 protein FASTA files."
    echo "Found: $N"
    echo
    echo "Please verify the input directory before running."
    exit 1
fi

# ----------------------------------------------------------
# LIST INPUT PROTEOMES
# ----------------------------------------------------------

echo
echo "Input proteomes:"
find "$INPUT" -maxdepth 1 -type f -name "*.faa" -printf "%f\n" | sort

# ----------------------------------------------------------
# RUN ORTHOFINDER
#
# This reproduces the original command recorded in
# the OrthoFinder Log.txt:
#
# orthofinder -f /mnt/d/ORTHOFINDER/proteomes \
#             -t 2 \
#             -a 1 \
#             -o /mnt/d/ORTHOFINDER/FUSARIUM36_FINAL
# ----------------------------------------------------------

echo
echo "=========================================================="
echo "STARTING ORTHOFINDER"
echo "=========================================================="

echo
echo "OrthoFinder:"
which orthofinder

echo
echo "Version:"
orthofinder --version

echo
echo "Start time:"
date

orthofinder \
    -f "$INPUT" \
    -t 2 \
    -a 1 \
    -o "$OUTPUT"

STATUS=$?

# ----------------------------------------------------------
# FINAL STATUS
# ----------------------------------------------------------

echo
echo "=========================================================="
echo "ORTHOFINDER FINISHED"
echo "=========================================================="

echo
echo "Exit status:"
echo "$STATUS"

echo
echo "Finished:"
date

if [ "$STATUS" -eq 0 ]; then
    echo
    echo "OrthoFinder completed successfully."
else
    echo
    echo "OrthoFinder exited with status $STATUS."
fi

echo
echo "Results directory:"
echo "$OUTPUT"

echo
echo "=========================================================="

exit "$STATUS"
