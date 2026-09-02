#!/usr/bin/env bash

# ==========================================================
# FUSARIUM 36 — SPECIES TREE CHECKPOINT
#
# INPUT:
# Existing SpeciesTreeAlignment.fa
#
# OUTPUT:
# SpeciesTree_unrooted_ids.txt
#
# DOES NOT:
# - run OrthoFinder
# - run DIAMOND
# - run MCL
# - run FAMSA
# - rerun gene trees
# - delete anything
#
# SAFE TO RE-RUN
# ==========================================================

set -u

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate orthofinder_clean

unset LD_LIBRARY_PATH
unset PYTHONPATH

RES="/mnt/d/ORTHOFINDER/FUSARIUM36_FINAL/Results_Aug11"
WD="$RES/WorkingDirectory"

ALIGN="$WD/Alignments_ids/SpeciesTreeAlignment.fa"
TREE="$WD/SpeciesTree_unrooted_ids.txt"

CHECK="$WD/SPECIES_TREE_CHECKPOINT"

mkdir -p "$CHECK"

LOG="$CHECK/species_tree.log"
DONE="$CHECK/SPECIES_TREE_COMPLETE.txt"

echo "==========================================================" | tee -a "$LOG"
echo "FUSARIUM 36 — SPECIES TREE CHECKPOINT" | tee -a "$LOG"
echo "==========================================================" | tee -a "$LOG"

echo "Start: $(date)" | tee -a "$LOG"

echo | tee -a "$LOG"
echo "FastTree:" | tee -a "$LOG"
which fasttree | tee -a "$LOG"
fasttree -help 2>&1 | head -5 | tee -a "$LOG"

echo | tee -a "$LOG"
echo "Input:" | tee -a "$LOG"
echo "$ALIGN" | tee -a "$LOG"

if [ ! -f "$ALIGN" ]; then
    echo "ERROR: SpeciesTreeAlignment.fa not found." | tee -a "$LOG"
    exit 1
fi

echo | tee -a "$LOG"
echo "Alignment size:" | tee -a "$LOG"
ls -lh "$ALIGN" | tee -a "$LOG"

echo | tee -a "$LOG"
echo "Species sequences:" | tee -a "$LOG"
grep -c '^>' "$ALIGN" | tee -a "$LOG"

if [ "$(grep -c '^>' "$ALIGN")" -ne 36 ]; then
    echo "ERROR: Expected 36 species sequences." | tee -a "$LOG"
    exit 1
fi

# ----------------------------------------------------------
# CHECK WHETHER SPECIES TREE ALREADY EXISTS
# ----------------------------------------------------------

if [ -s "$TREE" ]; then

    echo | tee -a "$LOG"
    echo "Species tree already exists and is non-empty." | tee -a "$LOG"
    echo "Nothing to do." | tee -a "$LOG"

    ls -lh "$TREE" | tee -a "$LOG"

    exit 0
fi

# ----------------------------------------------------------
# TEMPORARY OUTPUT
#
# We never write directly to the final file.
# This prevents a WSL shutdown from leaving a misleading
# partially-written species tree.
# ----------------------------------------------------------

TMP="$CHECK/SpeciesTree_unrooted_ids.tmp"

rm -f "$TMP"

echo | tee -a "$LOG"
echo "==========================================================" | tee -a "$LOG"
echo "RUNNING FASTTREE" | tee -a "$LOG"
echo "==========================================================" | tee -a "$LOG"

echo "Started: $(date)" | tee -a "$LOG"

fasttree \
    "$ALIGN" \
    > "$TMP" \
    2>> "$LOG"

STATUS=$?

echo "FastTree exit status: $STATUS" | tee -a "$LOG"

# ----------------------------------------------------------
# VERIFY
# ----------------------------------------------------------

if [ "$STATUS" -ne 0 ]; then

    echo "ERROR: FastTree failed." | tee -a "$LOG"
    echo "Temporary output preserved:" | tee -a "$LOG"
    ls -lh "$TMP" 2>/dev/null || true

    exit "$STATUS"
fi

if [ ! -s "$TMP" ]; then

    echo "ERROR: FastTree produced an empty tree." | tee -a "$LOG"

    exit 1
fi

# ----------------------------------------------------------
# BASIC NEWICK CHECK
# ----------------------------------------------------------

if ! grep -q ';' "$TMP"; then

    echo "ERROR: Output does not appear to contain a complete Newick tree." \
        | tee -a "$LOG"

    echo "Temporary output preserved:"
    ls -lh "$TMP"

    exit 1
fi

# ----------------------------------------------------------
# INSTALL FINAL TREE
# ----------------------------------------------------------

cp "$TMP" "$TREE"

echo | tee -a "$LOG"
echo "==========================================================" | tee -a "$LOG"
echo "SPECIES TREE CREATED" | tee -a "$LOG"
echo "==========================================================" | tee -a "$LOG"

echo "Final tree:" | tee -a "$LOG"
ls -lh "$TREE" | tee -a "$LOG"

echo | tee -a "$LOG"
echo "Tree preview:" | tee -a "$LOG"
head -c 1000 "$TREE" | tee -a "$LOG"
echo | tee -a "$LOG"

# ----------------------------------------------------------
# CHECKPOINT
# ----------------------------------------------------------

echo "Completed: $(date)" > "$DONE"
echo "Input: $ALIGN" >> "$DONE"
echo "Output: $TREE" >> "$DONE"
echo "Species: 36" >> "$DONE"
echo "FastTree exit status: $STATUS" >> "$DONE"

echo | tee -a "$LOG"
echo "CHECKPOINT COMPLETE" | tee -a "$LOG"
echo "Finished: $(date)" | tee -a "$LOG"

