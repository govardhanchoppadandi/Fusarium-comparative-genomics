#!/bin/bash

########################################################
# RUN TIDK FOR ALL GENOMES
########################################################

set -e

GENOME_DIR="data/genomes"
OUT_DIR="results/telomere"

mkdir -p "$OUT_DIR"

for genome in "$GENOME_DIR"/*.fa
do
    base=$(basename "$genome" .fa)

    echo "Running tidk for $base"

    tidk search \
        --string TTAGGG \
        --window 1000 \
        --dir "${OUT_DIR}/${base}_work" \
        --output "${OUT_DIR}/${base}_telomeres" \
        "$genome"

done

echo "DONE!"
