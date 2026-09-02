#!/bin/bash

# ==========================================================
# ncRNA PIPELINE
# rRNA prediction with Barrnap
# tRNA prediction with tRNAscan-SE
# tRNA FASTA extraction with BEDTools
# ==========================================================

# ==========================================================
# OUTPUT FOLDER
# ==========================================================

OUT="/mnt/d/6_GENOMES/GENE AND GFF/trnascan"

mkdir -p "$OUT"

# ==========================================================
# GENOME FILES
# ==========================================================

GENOMES=(
"/mnt/d/6_GENOMES/GENE AND GFF/Fusarium_graminearum.genome.fa"
"/mnt/d/6_GENOMES/GENE AND GFF/TNW_1.genome.fa"
"/mnt/d/6_GENOMES/GENE AND GFF/Fusarium_avenaceum.genome.fa"
"/mnt/d/6_GENOMES/GENE AND GFF/F_culmorum.genome.fa"
"/mnt/d/6_GENOMES/GENE AND GFF/F. poae_genomic.fa"
"/mnt/d/6_GENOMES/GENE AND GFF/DMW_8.genome.fa"
)

# ==========================================================
# CHECK REQUIRED SOFTWARE
# ==========================================================

command -v barrnap >/dev/null 2>&1 || {
    echo "ERROR: barrnap is not installed or not in PATH."
    exit 1
}

command -v tRNAscan-SE >/dev/null 2>&1 || {
    echo "ERROR: tRNAscan-SE is not installed or not in PATH."
    exit 1
}

command -v bedtools >/dev/null 2>&1 || {
    echo "ERROR: bedtools is not installed or not in PATH."
    exit 1
}

# ==========================================================
# CREATE SUMMARY TABLE
# ==========================================================

echo -e "Species\ttRNAs\trRNAs" > "$OUT/summary.tsv"

# ==========================================================
# PROCESS EACH GENOME
# ==========================================================

for GENOME in "${GENOMES[@]}"; do

    if [ ! -f "$GENOME" ]; then
        echo "WARNING: Genome not found:"
        echo "$GENOME"
        echo "Skipping..."
        continue
    fi

    NAME=$(basename "$GENOME" .fa)

    echo "=========================================="
    echo "Processing: $NAME"
    echo "=========================================="

    # ======================================================
    # 1. BARRNAP - rRNA PREDICTION
    # ======================================================

    echo "Running Barrnap..."

    barrnap \
        --kingdom euk \
        --threads 8 \
        --outseq "$OUT/${NAME}.rRNAs.fasta" \
        "$GENOME" \
        > "$OUT/${NAME}.rRNAs.gff"

    # ======================================================
    # 2. tRNAscan-SE - tRNA PREDICTION
    # ======================================================

    echo "Running tRNAscan-SE..."

    tRNAscan-SE \
        -o "$OUT/${NAME}.tRNAs.txt" \
        -f "$OUT/${NAME}.tRNAs.ss.txt" \
        "$GENOME"

    # ======================================================
    # 3. CONVERT tRNAscan OUTPUT TO BED
    # ======================================================

    echo "Creating BED file..."

    awk '
    NR > 3 && $1 !~ /^Sequence/ && $3 ~ /^[0-9]+$/ && $4 ~ /^[0-9]+$/ {
        if ($3 < $4) {
            start = $3 - 1
            end = $4
        } else {
            start = $4 - 1
            end = $3
        }

        strand = $7

        print $1 "\t" start "\t" end "\t" $2 "\t.\t" strand
    }
    ' "$OUT/${NAME}.tRNAs.txt" \
    > "$OUT/${NAME}.tRNAs.bed"

    # ======================================================
    # 4. EXTRACT tRNA FASTA SEQUENCES
    # ======================================================

    echo "Extracting tRNA sequences..."

    bedtools getfasta \
        -fi "$GENOME" \
        -bed "$OUT/${NAME}.tRNAs.bed" \
        -s \
        -name \
        -fo "$OUT/${NAME}.tRNAs.fasta"

    # ======================================================
    # 5. COUNT tRNAs
    # ======================================================

    if [ -f "$OUT/${NAME}.tRNAs.fasta" ]; then
        TRNA_COUNT=$(grep -c "^>" "$OUT/${NAME}.tRNAs.fasta")
    else
        TRNA_COUNT=0
    fi

    # ======================================================
    # 6. COUNT rRNAs
    # ======================================================

    if [ -f "$OUT/${NAME}.rRNAs.fasta" ]; then
        RRNA_COUNT=$(grep -c "^>" "$OUT/${NAME}.rRNAs.fasta")
    else
        RRNA_COUNT=0
    fi

    # ======================================================
    # 7. SAVE SUMMARY
    # ======================================================

    echo -e "${NAME}\t${TRNA_COUNT}\t${RRNA_COUNT}" \
        >> "$OUT/summary.tsv"

    echo "tRNAs detected: $TRNA_COUNT"
    echo "rRNAs detected: $RRNA_COUNT"
    echo ""

done

# ==========================================================
# FINISHED
# ==========================================================

echo "=========================================="
echo "ncRNA ANALYSIS COMPLETE"
echo "=========================================="
echo "Results folder:"
echo "$OUT"
echo ""
echo "Summary:"
echo "$OUT/summary.tsv"
echo "=========================================="
