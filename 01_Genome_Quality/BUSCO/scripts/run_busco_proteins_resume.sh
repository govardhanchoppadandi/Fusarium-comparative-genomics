#!/bin/bash

source /root/miniconda3/etc/profile.d/conda.sh
conda activate busco_env

INPUT_DIR="/mnt/d/fusarium WGS/WGS/ALL species proteins"

OUTPUT_DIR="/mnt/d/fusarium WGS/WGS/ALL species proteins/busco_outputs"

DOWNLOAD_DIR="/mnt/d/fusarium WGS/WGS/ALL SPECIES GENOMES/busco_downloads"

mkdir -p "$OUTPUT_DIR"

for protein in "$INPUT_DIR"/*.faa
do
    sample=$(basename "$protein" .faa)

    summary=$(find "$OUTPUT_DIR/${sample}_BUSCO" \
        -name "*short_summary*.json" 2>/dev/null | head -1)

    if [ -n "$summary" ]; then
        echo "Skipping completed: $sample"
        continue
    fi

    echo "Running: $sample"

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

echo "ALL PROTEIN BUSCO RUNS FINISHED"
