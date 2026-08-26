#!/bin/bash

source /root/miniconda3/etc/profile.d/conda.sh
conda activate busco_env

INPUT_DIR="/mnt/d/fusarium WGS/WGS/ALL species proteins"

OUTPUT_DIR="/mnt/d/fusarium WGS/WGS/ALL species proteins/busco_outputs"

DOWNLOAD_DIR="/mnt/d/fusarium WGS/WGS/ALL SPECIES GENOMES/busco_downloads"

mkdir -p "$OUTPUT_DIR"

echo "=================================="
echo "Starting BUSCO for Fusarium proteins"
echo "=================================="

for protein in "$INPUT_DIR"/*.faa
do
    sample=$(basename "$protein" .faa)

    echo ""
    echo "=================================="
    echo "Running: $sample"
    echo "=================================="

    busco \
      -i "$protein" \
      -o "${sample}_BUSCO" \
      -m proteins \
      -l hypocreales_odb10 \
      -c 4 \
      --download_path "$DOWNLOAD_DIR" \
      --out_path "$OUTPUT_DIR" \
      --force

done

echo ""
echo "=================================="
echo "ALL PROTEIN BUSCO RUNS FINISHED"
echo "=================================="
