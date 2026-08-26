#!/usr/bin/env bash

set -u

# ==========================================================
# FUSARIUM 36 — CHECKPOINTED GENE TREE RECOVERY
#
# Uses existing:
#   Orthogroups
#   FAMSA alignments
#
# Runs:
#   FastTree 2.2.0
#
# Writes:
#   WorkingDirectory/Gene_Trees/
#
# NEVER:
#   reruns DIAMOND
#   reruns MCL
#   reruns FAMSA
#   deletes existing OrthoFinder files
# ==========================================================

RES="/mnt/d/ORTHOFINDER/FUSARIUM36_FINAL/Results_Aug11"
WD="$RES/WorkingDirectory"

ALIGN="$WD/Alignments_ids"
TREES="$WD/Gene_Trees"

CHECK="$WD/TREE_CHECKPOINT"
LOG="$CHECK/tree_recovery.log"
DONE="$CHECK/completed.txt"
FAILED="$CHECK/failed.txt"

THREADS=1

# ==========================================================
# ENVIRONMENT
# ==========================================================

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate orthofinder_clean

unset LD_LIBRARY_PATH
unset PYTHONPATH

# ==========================================================
# DIRECTORIES
# ==========================================================

mkdir -p "$TREES"
mkdir -p "$CHECK"

touch "$DONE"
touch "$FAILED"

# ==========================================================
# LOGGING
# ==========================================================

exec > >(tee -a "$LOG") 2>&1

echo
echo "=========================================================="
echo "FUSARIUM 36 — GENE TREE CHECKPOINT RECOVERY"
echo "=========================================================="

date

echo
echo "Environment:"
which fasttree
fasttree -help 2>&1 | head -1

echo
echo "Results:"
echo "$RES"

echo
echo "Alignments:"
echo "$ALIGN"

echo
echo "Gene trees:"
echo "$TREES"

# ==========================================================
# SAFETY CHECKS
# ==========================================================

[ -d "$ALIGN" ] || {
    echo "ERROR: Alignment directory missing."
    exit 1
}

[ -f "$RES/Orthogroups/Orthogroups.txt" ] || {
    echo "ERROR: Orthogroups.txt missing."
    exit 1
}

ALIGN_COUNT=$(find "$ALIGN" \
    -maxdepth 1 \
    -type f \
    -name "OG*.fa" |
    wc -l)

echo
echo "Alignment files: $ALIGN_COUNT"

[ "$ALIGN_COUNT" -gt 10000 ] || {
    echo "ERROR: Unexpectedly low alignment count."
    exit 1
}

# ==========================================================
# EXISTING TREE COUNT
# ==========================================================

TREE_COUNT=$(find "$TREES" \
    -maxdepth 1 \
    -type f \
    -name "OG*.txt" |
    wc -l)

echo
echo "Existing Gene_Trees: $TREE_COUNT"

# ==========================================================
# BUILD TREE LIST
# ==========================================================

LIST="$CHECK/tree_list.txt"

find "$ALIGN" \
    -maxdepth 1 \
    -type f \
    -name "OG*.fa" \
    -printf "%f\n" |
sort -V > "$LIST"

TOTAL=$(wc -l < "$LIST")

echo
echo "Total alignments: $TOTAL"

# ==========================================================
# PROCESS EACH ALIGNMENT
# ==========================================================

COUNT=0
SKIPPED=0
SUCCESS=0
FAIL=0

while IFS= read -r NAME
do

    COUNT=$((COUNT + 1))

    OG="${NAME%.fa}"

    IN="$ALIGN/$NAME"
    OUT="$TREES/$OG.txt"
    TMP="$TREES/.${OG}.tmp"

    # ------------------------------------------------------
    # CHECK EXISTING VALID TREE
    # ------------------------------------------------------

    if [ -s "$OUT" ] &&
       grep -q '(' "$OUT" &&
       grep -q ';' "$OUT"
    then

        SKIPPED=$((SKIPPED + 1))

        echo "[SKIP] $COUNT/$TOTAL $OG already has valid tree"

        continue
    fi

    # ------------------------------------------------------
    # REMOVE ONLY OUR OWN TEMP FILE
    # ------------------------------------------------------

    rm -f "$TMP"

    echo
    echo "----------------------------------------------------------"
    echo "[RUN] $COUNT/$TOTAL $OG"
    echo "Input: $IN"
    echo "Output: $OUT"
    echo "Sequences: $(grep -c '^>' "$IN")"
    date

    # ------------------------------------------------------
    # FASTTREE
    #
    # EXACT ORTHOFINDER COMMAND:
    #
    # FastTree INPUT > OUTPUT
    # ------------------------------------------------------

    if fasttree "$IN" > "$TMP" 2>> "$LOG"
    then

        if [ -s "$TMP" ] &&
           grep -q '(' "$TMP" &&
           grep -q ';' "$TMP"
        then

            mv "$TMP" "$OUT"

            SUCCESS=$((SUCCESS + 1))

            echo "$OG" >> "$DONE"

            echo "[SUCCESS] $OG"

        else

            FAIL=$((FAIL + 1))

            echo "$OG" >> "$FAILED"

            rm -f "$TMP"

            echo "[FAILED] $OG — invalid tree output"

        fi

    else

        FAIL=$((FAIL + 1))

        echo "$OG" >> "$FAILED"

        rm -f "$TMP"

        echo "[FAILED] $OG — FastTree error"

    fi

    # ------------------------------------------------------
    # CHECKPOINT
    # ------------------------------------------------------

    if [ $((COUNT % 25)) -eq 0 ]
    then

        echo
        echo "=========================================================="
        echo "CHECKPOINT"
        echo "Processed : $COUNT"
        echo "Total     : $TOTAL"
        echo "Skipped   : $SKIPPED"
        echo "Success   : $SUCCESS"
        echo "Failed    : $FAIL"
        echo "Gene trees: $(find "$TREES" -maxdepth 1 -type f -name 'OG*.txt' | wc -l)"
        echo "Time      : $(date)"
        echo "=========================================================="

    fi

done < "$LIST"

# ==========================================================
# FINAL SUMMARY
# ==========================================================

FINAL_TREE_COUNT=$(find "$TREES" \
    -maxdepth 1 \
    -type f \
    -name "OG*.txt" |
    wc -l)

echo
echo "=========================================================="
echo "TREE RECOVERY FINISHED"
echo "=========================================================="

echo "Alignments       : $TOTAL"
echo "Existing/skipped : $SKIPPED"
echo "New successful   : $SUCCESS"
echo "Failed           : $FAIL"
echo "Gene trees total : $FINAL_TREE_COUNT"

echo
echo "Checkpoint:"
echo "$CHECK"

echo
echo "Completed list:"
echo "$DONE"

echo
echo "Failed list:"
echo "$FAILED"

echo
echo "Finished:"
date

echo
echo "=========================================================="

