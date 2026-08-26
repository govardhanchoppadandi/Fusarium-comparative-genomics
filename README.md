# Fusarium Comparative Genomics

Reproducible computational workflows and scripts for comparative genomics of wheat-infecting *Fusarium* species.

## Overview

This repository contains the computational workflows, scripts, metadata, and figure-generation code used for the comparative genomic analyses presented in the associated manuscript.

The repository is organized according to the major analyses performed in the study, including genome quality assessment, multi-gene phylogeny, orthology analysis, gene-family evolution, non-coding RNA annotation, transposable-element analysis, RIP analysis, transposable-element insertion analysis, KEGG annotation, comparative genomics, effector-related sequence preparation, and figure generation.

## Repository Structure

```text
Fusarium-comparative-genomics/
│
├── 01_Genome_Quality/
│   └── BUSCO/
│       ├── README.md
│       └── scripts/
│           ├── run_busco_genomes.sh
│           ├── run_busco_proteins.sh
│           └── run_busco_proteins_resume.sh
│
├── 02_Phylogeny/
│   ├── README.md
│   └── scripts/
│       ├── alignment/
│       ├── concatenation/
│       ├── tree_inference/
│       └── visualization/
│
├── 03_OrthoFinder_6_Genomes/
│   ├── README.md
│   └── scripts/
│       ├── prepare_proteomes/
│       ├── orthofinder/
│       ├── single_copy_orthologues/
│       └── phylogenomics/
│
├── 04_OrthoFinder_36_Genomes/
│   ├── README.md
│   └── scripts/
│       ├── prepare_proteomes/
│       ├── chunking/
│       ├── orthofinder/
│       ├── merge_results/
│       └── downstream_analysis/
│
├── 05_CAFE/
│   ├── README.md
│   └── scripts/
│       ├── prepare_gene_family_matrix/
│       ├── cafe/
│       ├── expansion/
│       ├── contraction/
│       └── visualization/
│
├── 06_ncRNA/
│   ├── README.md
│   └── scripts/
│
├── 07_Transposable_Elements/
│   ├── README.md
│   └── scripts/
│       ├── earl_grey/
│       └── summary/
│
├── 08_RIP_Analysis/
│   ├── README.md
│   └── scripts/
│       ├── RIPCAL/
│       ├── TE_intersection/
│       └── visualization/
│
├── 09_McClintock/
│   ├── README.md
│   └── scripts/
│
├── 10_KEGG/
│   ├── README.md
│   └── scripts/
│       ├── KO_annotation/
│       ├── pathway_annotation/
│       └── summary/
│
├── 11_Comparative_Genomics/
│   ├── README.md
│   └── scripts/
│       ├── genome_statistics/
│       ├── gene_statistics/
│       ├── orthogroup_statistics/
│       └── comparative_tables/
│
├── 12_Figure_Generation/
│   ├── README.md
│   ├── Figure_1/
│   ├── Figure_2/
│   ├── Figure_3/
│   ├── Figure_4/
│   ├── Figure_5/
│   └── Supplementary_Figures/
│
├── 13_Effector_Prediction/
│   ├── README.md
│   └── scripts/
│       └── fasta_preparation/
│
├── data/
│   ├── metadata/
│   ├── genome_accessions/
│   └── input_information/
│
├── results/
│   ├── tables/
│   └── summary/
│
└── supplementary/
    └── tables/
