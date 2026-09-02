# ncRNA Analysis — rRNA and tRNA Prediction

This module predicts ribosomal RNA (rRNA) and transfer RNA (tRNA) from the six Fusarium genome assemblies used in the comparative-genomics workflow.

## 1. Software required

Run the analysis in Ubuntu/WSL.

Required:
- Barrnap — rRNA prediction
- tRNAscan-SE — tRNA prediction
- BEDTools — extraction of predicted tRNA sequences
- Bash, awk, grep, nano

### Recommended installation with Conda

```bash
conda create -n ncrna_analysis -c bioconda -c conda-forge barrnap trnascan-se bedtools
conda activate ncrna_analysis
```

Check installation:

```bash
barrnap --version
tRNAscan-SE --version
bedtools --version
```

Each command should return a version number.

## 2. Input genomes

The script expects these six genome FASTA files:

```text
/mnt/d/6_GENOMES/GENE AND GFF/Fusarium_graminearum.genome.fa
/mnt/d/6_GENOMES/GENE AND GFF/TNW_1.genome.fa
/mnt/d/6_GENOMES/GENE AND GFF/Fusarium_avenaceum.genome.fa
/mnt/d/6_GENOMES/GENE AND GFF/F_culmorum.genome.fa
/mnt/d/6_GENOMES/GENE AND GFF/F. poae_genomic.fa
/mnt/d/6_GENOMES/GENE AND GFF/DMW_8.genome.fa
```

Make sure the filenames exactly match the files on the D: drive.

Check them with:

```bash
ls -lh "/mnt/d/6_GENOMES/GENE AND GFF/"*.fa
```

If your filenames are different, edit the `GENOMES=(...)` section of `run_ncRNA_all.sh`.

## 3. Output directory

Results are saved to:

```text
D:\6_GENOMES\GENE AND GFF\trnascan
```

WSL path:

```text
/mnt/d/6_GENOMES/GENE AND GFF/trnascan
```

Create it with:

```bash
mkdir -p "/mnt/d/6_GENOMES/GENE AND GFF/trnascan"
```

## 4. Run the pipeline

From the directory containing `run_ncRNA_all.sh`:

```bash
chmod +x run_ncRNA_all.sh
./run_ncRNA_all.sh
```

The script:
1. Predicts rRNAs with Barrnap.
2. Predicts tRNAs with tRNAscan-SE.
3. Converts tRNA coordinates to BED format.
4. Extracts tRNA sequences with BEDTools.
5. Counts predicted tRNAs and rRNAs.
6. Creates a combined `summary.tsv` table.

## 5. Output files

For each genome:

| File | Description |
|---|---|
| `*.rRNAs.fasta` | Predicted rRNA sequences |
| `*.rRNAs.gff` | rRNA genomic coordinates |
| `*.tRNAs.txt` | Main tRNAscan-SE output |
| `*.tRNAs.ss.txt` | tRNA secondary-structure output |
| `*.tRNAs.bed` | tRNA coordinates in BED format |
| `*.tRNAs.fasta` | Extracted tRNA sequences |
| `summary.tsv` | Combined tRNA/rRNA counts |

View the final summary:

```bash
cat "/mnt/d/6_GENOMES/GENE AND GFF/trnascan/summary.tsv"
```

## 6. Expected summary

The final table contains:

```text
Species    tRNAs    rRNAs
```

The actual counts are generated automatically and should not be entered manually.

## 7. Record software versions

For reproducibility, record:

```bash
barrnap --version
tRNAscan-SE --version
bedtools --version
```

If using Conda:

```bash
conda list | grep -E 'barrnap|trnascan|bedtools'
```

## 8. Important note about rRNA counts

The `rRNAs` value in `summary.tsv` is the number of FASTA records produced by Barrnap. It should not automatically be interpreted as the number of distinct rRNA operons.

## 9. Repository organization

Recommended GitHub structure:

```text
06_ncRNA/
├── README.md
└── scripts/
    └── run_ncRNA_all.sh
```

Do not upload large genome FASTA files or large generated intermediate results unless they are intentionally part of the repository.

## 10. Workflow

```text
Genome FASTA
     │
     ├──────────────► Barrnap
     │                  ├── rRNA FASTA
     │                  └── rRNA GFF
     │
     └──────────────► tRNAscan-SE
                        ├── tRNA predictions
                        └── secondary structure
                               │
                               ▼
                           BEDTools
                               │
                               ▼
                         tRNA FASTA
                               │
                               ▼
                         summary.tsv
```

## Script type

`run_ncRNA_all.sh` is a **Bash/Unix shell script**, not Python.

The script should be stored at:

```text
06_ncRNA/scripts/run_ncRNA_all.sh
```
