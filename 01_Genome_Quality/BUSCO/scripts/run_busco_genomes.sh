#!/bin/bash

source /root/miniconda3/etc/profile.d/conda.sh
conda activate busco_env

INPUT_DIR="/mnt/d/fusarium WGS/WGS/ALL SPECIES GENOMES"

OUTPUT_DIR="/mnt/d/fusarium WGS/WGS/ALL SPECIES GENOMES/busco_outputs"

DOWNLOAD_DIR="/mnt/d/fusarium WGS/WGS/ALL SPECIES GENOMES/busco_downloads"

mkdir -p "$OUTPUT_DIR"

echo "=================================="
echo "RESUMING BUSCO FOR 68 GENOMES"
echo "=================================="

for genome in "$INPUT_DIR"/*.fna
do
    sample=$(basename "$genome" .fna)

    summary=$(find "$OUTPUT_DIR/${sample}_BUSCO" \
        -name "*short_summary*.json" 2>/dev/null | head -1)

    if [ -n "$summary" ]; then
        echo "Skipping completed: $sample"
        continue
    fi

    echo ""
    echo "=================================="
    echo "Running: $sample"
    echo "=================================="

    busco \
      -i "$genome" \
      -o "${sample}_BUSCO" \
      -m genome \
      -l hypocreales_odb10 \
      -c 6 \
      --download_path "$DOWNLOAD_DIR" \
      --out_path "$OUTPUT_DIR" \
      --force

done

echo ""
echo "=================================="
echo "ALL BUSCO RUNS FINISHED"
echo "=================================="
