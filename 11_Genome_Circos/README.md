# whole genome Circos Plot

## Overview

This directory contains the scripts used to generate a scaffold-level Circos plot for the TNW1 Fusarium genome.

The workflow has two main stages:

1. Circos input preparation using Python.
2. Final Circos visualization using R and the `circlize` package.

The visualization integrates genomic and functional annotation tracks including GC content, gene density, transposable-element (TE) density, RIP density, GO-associated genes, TE annotations, antiSMASH clusters, tRNA, rRNA, and optional TE/RIP/link tracks.

## Directory Structure

```text
11_Circos_Plot/
│
├── README.md
│
└── scripts/
    ├── circos_input_builder/
    │   └── TNW1_complete_circos_builder.py
    │
    └── circos_plot/
        └── TNW1_final_compact_circos.R
```

## Software Requirements

### Python

Required packages:

```bash
pip install pandas numpy biopython openpyxl
```

### R

Install the required packages:

```r
install.packages("circlize")
install.packages("scales")
```

## Step 1: Prepare Circos Input Files

The Python script is:

```text
scripts/circos_input_builder/TNW1_complete_circos_builder.py
```

Run:

```bash
python TNW1_complete_circos_builder.py
```

The script creates a `circos_scaffold/` directory containing:

```text
karyotype.txt
gene_density.txt
gc_density.txt
te_density.txt
te_class.txt
rip_density.txt
trna.txt
rrna.txt
secreted.txt
go_density.txt
cazyme.txt
antismash.txt
effector_apoplastic.txt
effector_cytoplasmic.txt
effector_both.txt
```

## Step 2: Generate the Final Circos Plot

The R script is:

```text
scripts/circos_plot/TNW1_final_compact_circos.R
```

Run:

```bash
Rscript TNW1_final_compact_circos.R
```

The main output is:

```text
TNW1_FINAL_COMPACT.pdf
```

## Main Tracks

The final plot can contain:

1. GC content density
2. Gene density
3. TE density
4. RIP density
5. GO-associated genes
6. TE annotation
7. AT-rich regions
8. antiSMASH clusters
9. Young TE regions
10. Old TE regions
11. RIP–TE overlap
12. rRNA
13. tRNA
14. Optional genomic links

## Required Input Data

The Python input-builder expects:

```text
TNW_1.genome.fa
gene_positions.tsv
TNW_1.filteredRepeats.bed
TNW_1_RIP.bed
TNW1_tRNAs.bed
TNW1_rRNAs.barrnap.gff
secreted.txt
GO_export.txt
dbcan.txt
TNW1 SM.xlsx
effector_apoplastic.txt
effector_cytoplasmic.txt
effector_both.txt
```

These analysis data files do not need to be stored in this GitHub directory. The file paths in the Python script should be changed to match the local analysis environment before running it.

## Optional Tracks

The R script can additionally use:

```text
at_rich.txt
te_young.txt
te_old.txt
te_rip_overlap.txt
circos_links.txt
```

These are optional. If they are unavailable, the corresponding features are omitted.

## Output

The principal final output is:

```text
TNW1_FINAL_COMPACT.pdf
```

This provides a compact scaffold-level visualization of genomic architecture and selected genomic and functional annotations for TNW1.

## Reproducibility Notes

- Density calculations use a 100 kb window.
- Density tracks are normalized before visualization.
- Coordinates are clipped to scaffold boundaries to reduce plotting warnings.
- Optional tracks are used only when their files are available.
- When more than 200 genomic links are supplied, the R script randomly samples 200 links for plot clarity.
- Large genome sequences, annotation tables, intermediate files, and other analysis datasets are kept outside this GitHub directory.

## Workflow

```text
TNW1 genome + annotations
          │
          ▼
TNW1_complete_circos_builder.py
          │
          ▼
Circos input tracks
          │
          ▼
TNW1_final_compact_circos.R
          │
          ▼
TNW1_FINAL_COMPACT.pdf
```

## Section

This analysis is part of the **Circos Plot** workflow in the Fusarium genome analysis project.
