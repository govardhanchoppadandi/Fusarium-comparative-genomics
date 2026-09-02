# Fusarium Comparative Genomics

This repository contains the reproducible computational workflows, scripts,
metadata, and figure-generation code used for the comparative genomic
analyses of wheat-infecting Fusarium species.

## Overall Workflow

The overall experimental and computational workflow used in this study is shown below.

![Fusarium Comparative Genomics Workflow](workflow.png)

## Repository Structure

```text
```text
Fusarium-comparative-genomics/
│
├── 01_Genome_Quality/
├── 02_Phylogeny/
├── 03_OrthoFinder_6_Genomes/
├── 04_OrthoFinder_36_Genomes/
├── 05_CAFE5_Gene_Family_Evolution/
├── 06_ncRNA/
├── 07_Transposable_Elements/
├── 08_RIP_Analysis/
├── 09_McClintock/
├── 10_KEGG/
├── 11_Genome_Circos_Plot/
├── 12_Telomere_Analysis/
├── 13_Effector_Prediction/
│
├── 14_ARI_Wheat_Pathology_Functional_Annotation/
│   │
│   ├── README.md
│   │
│   ├── app/
│   │   └── pipeline.py
│   │
│   ├── modules/
│   │   ├── blast_annotation.py
│   │   ├── check_resources.py
│   │   ├── excel_output.py
│   │   ├── fasta_qc.py
│   │   ├── go_annotation.py
│   │   ├── goslim.py
│   │   └── project_output.py
│   │
│   ├── config/
│   │   ├── config.yaml
│   │   └── resources.local.example.yaml
│   │
│   ├── install.sh
│   ├── fusarium_annotator.sh
│   └── .gitignore
│
├── results/
│   └── TE_RIP/
│
├── workflow.png
├── README.md
├── CITATION.cff
├── LICENSE
└── .gitignore
```

## Analysis modules

| Module | Purpose |
|---|---|
| `01_Genome_Quality/BUSCO` | Genome and predicted-protein completeness assessment |
| `02_Phylogeny` | Multi-gene phylogenetic analysis and visualization |
| `03_OrthoFinder_6_Genomes` | Orthology and phylogenomics analysis of six genomes |
| `04_OrthoFinder_36_Genomes` | Comparative orthology and phylogenomics across 36 genomes |
| `05_CAFE5_Gene_Family_Evolution` | Gene-family expansion and contraction analysis |
| `06_ncRNA` | Non-coding RNA annotation/analysis |
| `07_Transposable_Elements` | Transposable-element annotation and summary |
| `08_RIP_Analysis` | Repeat-induced point mutation analysis and RIP–TE analysis |
| `09_McClintock` | Transposable-element insertion analysis |
| `10_KEGG` | KEGG/KO annotation and pathway analysis |
| `11_Whole_genome_Circos_Plot` | Circular genome visualisation (Circos plots) of the Fusarium isolates F. graminearum (TNW1; Figure 7) and F.avenaceum (DMW8; Figure 8), illustrating genome-wide organisation and functional genomic features. The outer ring represents scaffold organisation, numbered sequentially. Subsequent tracks depict GC content density, gene density, transposable element (TE) density, RIP-associated regions, GO-annotated genes, TE-rich regions/classes, AT-rich regions, predicted secondary metabolite biosynthetic gene clusters (antiSMASH), young and old TE insertions, TE–RIP overlap regions, and rRNA/tRNA loci. Colored ribbons in the centre indicate intra-genomic repetitive or syntenic relationships based on sequence similarity. To improve visual clarity, minor scaffolds (<1 Mb) were excluded. |
| `12_Telomere_Analysis` | finding telomear repeats |
| `13_Effector_Prediction` | Preparation of protein sequences for downstream effector prediction |

## Data organization

Input datasets, metadata, accession information, and analysis outputs are organized separately from computational scripts.

- `data/` contains metadata and input information required to reproduce analyses.
- `results/` contains selected derived tables and summary results.
- `supplementary/` contains supplementary tables associated with the manuscript.
- Large raw genome/protein datasets and computationally generated intermediate files are not included unless explicitly stated.

## Reproducibility

Each analysis module contains its own `README.md` where applicable. These files document the relevant software, parameters, input requirements, scripts, and expected outputs for that analysis.

The repository is intended to provide a transparent record of the computational workflow supporting the associated publication.
