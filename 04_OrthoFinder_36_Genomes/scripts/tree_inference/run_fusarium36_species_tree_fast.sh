#!/usr/bin/env bash

# ==========================================================
# FUSARIUM 36 — FAST SPECIES TREE RECOVERY
#
# Uses EXISTING SpeciesTreeAlignment.fa
#
# DOES NOT:
# - run OrthoFinder
# - run DIAMOND
# - run MCL
# - run FAMSA
# - rerun gene trees
# - delete anything
#
# FastTree -noml:
# Uses the tree-search stage without the expensive
# maximum-likelihood optimization that previously took
# >45 minutes and was interrupted.
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

CHECK="$WD/SPECIES_TREE_CHECKPOINT_FAST"

mkdir -p "$CHECK"

LOG="$CHECK/species_tree_fast.log"
TMP="$CHECK/SpeciesTree_unrooted_ids.tmp"
DONE="$CHECK/SPECIES_TREE_FAST_COMPLETE.txt"

echo "==========================================================" | tee -a "$LOG"
echo "FUSARIUM 36 — FAST SPECIES TREE RECOVERY" | tee -a "$LOG"
echo "==========================================================" | tee -a "$LOG"

echo "Start: $(date)" | tee -a "$LOG"

echo | tee -a "$LOG"
echo "===== FASTTREE =====" | tee -a "$LOG"

which fasttree | tee -a "$LOG"
fasttree -help 2>&1 | head -12 | tee -a "$LOG"

echo | tee -a "$LOG"
echo "===== INPUT =====" | tee -a "$LOG"

if [ ! -f "$ALIGN" ]; then
    echo "ERROR: SpeciesTreeAlignment.fa not found." | tee -a "$LOG"
    exit 1
fi

ls -lh "$ALIGN" | tee -a "$LOG"

echo | tee -a "$LOG"
echo "Species sequences:" | tee -a "$LOG"

N=$(grep -c '^>' "$ALIGN")

echo "$N" | tee -a "$LOG"

if [ "$N" -ne 36 ]; then
    echo "ERROR: Expected 36 species." | tee -a "$LOG"
    exit 1
fi

# ----------------------------------------------------------
# IF FINAL TREE ALREADY EXISTS
# ----------------------------------------------------------

if [ -s "$TREE" ]; then

    echo | tee -a "$LOG"
    echo "FINAL SPECIES TREE ALREADY EXISTS." | tee -a "$LOG"
    ls -lh "$TREE" | tee -a "$LOG"

    exit 0
fi

# ----------------------------------------------------------
# REMOVE ONLY OUR OWN EMPTY TEMPORARY FILE
#
# We never touch the original OrthoFinder files.
# ----------------------------------------------------------

if [ -f "$TMP" ]; then

    SIZE=$(stat -c%s "$TMP")

    if [ "$SIZE" -eq 0 ]; then
        rm -f "$TMP"
    fi

fi

# ----------------------------------------------------------
# RUN FASTTREE WITHOUT ML
# ----------------------------------------------------------

echo | tee -a "$LOG"
echo "==========================================================" | tee -a "$LOG"
echo "STARTING FASTTREE -noml" | tee -a "$LOG"
echo "==========================================================" | tee -a "$LOG"

echo "Started: $(date)" | tee -a "$LOG"

fasttree \
    -noml \
    "$ALIGN" \
    > "$TMP" \
    2>> "$LOG"

STATUS=$?

echo | tee -a "$LOG"
echo "FastTree exit status: $STATUS" | tee -a "$LOG"

# ----------------------------------------------------------
# VERIFY FASTTREE
# ----------------------------------------------------------

if [ "$STATUS" -ne 0 ]; then

    echo "ERROR: FastTree failed." | tee -a "$LOG"

    echo "Temporary file:"
    ls -lh "$TMP" 2>/dev/null || true

    exit "$STATUS"

fi

if [ ! -s "$TMP" ]; then

    echo "ERROR: FastTree produced an empty tree." | tee -a "$LOG"

    exit 1

fi

# ----------------------------------------------------------
# NEWICK CHECK
# ----------------------------------------------------------

if ! grep -q ';' "$TMP"; then

    echo "ERROR: Output does not contain a complete Newick tree." \
        | tee -a "$LOG"

    exit 1

fi

# ----------------------------------------------------------
# COUNT TAXA IN TREE
# ----------------------------------------------------------

echo | tee -a "$LOG"
echo "===== TREE SIZE =====" | tee -a "$LOG"

ls -lh "$TMP" | tee -a "$LOG"

echo | tee -a "$LOG"
echo "===== TREE PREVIEW =====" | tee -a "$LOG"

head -c 1000 "$TMP" | tee -a "$LOG"

echo | tee -a "$LOG"

# ----------------------------------------------------------
# INSTALL FINAL SPECIES TREE
# ----------------------------------------------------------

cp "$TMP" "$TREE"

# ----------------------------------------------------------
# VERIFY FINAL FILE
# ----------------------------------------------------------

if [ ! -s "$TREE" ]; then

    echo "ERROR: Final species tree is empty." | tee -a "$LOG"

    exit 1

fi

echo | tee -a "$LOG"
echo "==========================================================" | tee -a "$LOG"
echo "SPECIES TREE SUCCESSFULLY CREATED" | tee -a "$LOG"
echo "==========================================================" | tee -a "$LOG"

ls -lh "$TREE" | tee -a "$LOG"

# ----------------------------------------------------------
# CHECKPOINT
# ----------------------------------------------------------

echo "==========================================================" > "$DONE"
echo "FUSARIUM 36 SPECIES TREE COMPLETE" >> "$DONE"
echo "Completed: $(date)" >> "$DONE"
echo "Input: $ALIGN" >> "$DONE"
echo "Output: $TREE" >> "$DONE"
echo "Species: 36" >> "$DONE"
echo "Method: FastTree 2.2.0 -noml" >> "$DONE"
echo "FastTree exit status: $STATUS" >> "$DONE"

echo | tee -a "$LOG"
echo "CHECKPOINT COMPLETE" | tee -a "$LOG"
echo "Finished: $(date)" | tee -a "$LOG"

