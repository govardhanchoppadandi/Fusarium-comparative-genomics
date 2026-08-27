#!/bin/bash

# ==========================================================
# EARLGREY BATCH ANALYSIS
#
# Run EarlGrey on all .fna genomes in the current directory.
#
# Completed genomes are skipped automatically.
# ==========================================================

set -u

mkdir -p TE_analysis

for GENOME in *.fna
do

    # If no .fna files exist, avoid processing the literal *.fna
    if [ ! -f "$GENOME" ]; then
        echo "No .fna genome files found."
        exit 1
    fi

    NAME=$(basename "$GENOME" .fna)

    OUTDIR="TE_analysis/$NAME"

    DONEFILE="$OUTDIR/${NAME}_EarlGrey/${NAME}_summaryFiles/${NAME}.highLevelCount.txt"

    echo "======================================"
    echo "Checking $NAME"
    echo "======================================"

    if [ -f "$DONEFILE" ]; then

        echo "Skipping $NAME (already completed)"
        echo

        continue

    fi

    echo "Starting $NAME"
    echo

    earlGrey \
        -g "$GENOME" \
        -s "$NAME" \
        -o "$OUTDIR" \
        -t 2 \
        -i 3 \
        -n 10

    STATUS=$?

    if [ "$STATUS" -eq 0 ]; then

        echo "✓ Finished $NAME"

    else

        echo "✗ Failed $NAME"
        echo "Exit status: $STATUS"

    fi

    echo

done

echo "======================="
echo "ALL GENOMES PROCESSED"
echo "======================="
