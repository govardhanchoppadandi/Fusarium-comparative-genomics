# Fusarium Comparative Genomics

Reproducible computational workflows and scripts for comparative genomics of wheat-infecting *Fusarium* species.

## Overview

This repository contains the computational workflows, scripts, metadata, and figure-generation code used for the comparative genomic analyses presented in the associated manuscript.

The repository is organized according to the major analyses performed in the study, including genome quality assessment, phylogeny, orthology analysis, gene-family evolution, non-coding RNA annotation, transposable-element analysis, RIP analysis, TE insertion analysis, KEGG annotation, comparative genomics, effector-related sequence preparation, and figure generation.

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
│   └── scripts/
│
├── 03_OrthoFinder_6_Genomes/
│   └── scripts/
│       ├── prepare_proteomes/
│       ├── orthofinder/
│       ├── single_copy_orthologues/
│       └── phylogenomics/
│
├── 04_OrthoFinder_36_Genomes/
│   └── scripts/
│       ├── prepare_proteomes/
│       ├── chunking/
│       ├── orthofinder/
│       ├── merge_results/
│       └── downstream_analysis/
│
├── 05_CAFE/
│   └── scripts/
│       ├── prepare_gene_family_matrix/
│       ├── cafe/
│       ├── expansion/
│       ├── contraction/
│       └── visualization/
│
├── 06_ncRNA/
│   └── scripts/
│
├── 07_Transposable_Elements/
│   └── scripts/
│       ├── earl_grey/
│       └── summary/
│
├── 08_RIP_Analysis/
│   └── scripts/
│       ├── RIPCAL/
│       ├── TE_intersection/
│       └── visualization/
│
├── 09_McClintock/
│   └── scripts/
│
├── 10_KEGG/
│   └── scripts/
│       ├── KO_annotation/
│       ├── pathway_annotation/
│       └── summary/
│
├── 11_Comparative_Genomics/
│   └── scripts/
│       ├── genome_statistics/
│       ├── gene_statistics/
│       ├── orthogroup_statistics/
│       └── comparative_tables/
│
├── 12_Figure_Generation/
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
