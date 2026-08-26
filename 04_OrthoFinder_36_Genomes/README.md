# OrthoFinder analysis of 36 *Fusarium* genomes

## Overview

Orthology analysis was performed across 36 *Fusarium* proteomes using OrthoFinder v3.1.5.

The analysis used DIAMOND for sequence similarity searches, MCL for orthogroup inference, FAMSA for multiple sequence alignment, and FastTree v2.2.0 for gene-tree inference.

## Input

The analysis used predicted protein sequences from 36 *Fusarium* genomes. Protein FASTA files were prepared and standardized before OrthoFinder analysis.

## OrthoFinder analysis

OrthoFinder v3.1.5 was used to infer orthogroups from the 36 protein datasets.

The analysis configuration was:

- OrthoFinder: 3.1.5
- Sequence search: DIAMOND
- Orthogroup inference: MCL
- Multiple sequence alignment: FAMSA
- Tree inference: FastTree v2.2.0
- Scoring matrix: BLOSUM62
- Gap opening: 11
- Gap extension: 1

The initial OrthoFinder run successfully generated the sequence-search results, orthogroup assignments, and multiple sequence alignments. The process was subsequently terminated during the computationally intensive gene-tree inference stage because of the large number of genomes and orthogroups.

## Checkpoint-based gene-tree recovery

To avoid repeating completed computational steps, the existing OrthoFinder results were retained and gene-tree inference was completed using a checkpoint-based recovery workflow.

The recovery workflow used the existing FAMSA alignments as input for FastTree v2.2.0.

The workflow:

- did not rerun DIAMOND;
- did not rerun MCL;
- did not rerun FAMSA;
- did not delete existing OrthoFinder results;
- detected existing valid gene trees and skipped them;
- generated only missing gene trees;
- validated generated Newick trees;
- recorded completed and failed orthogroups in checkpoint files; and
- allowed gene-tree inference to be resumed after interruption.

This checkpoint approach ensured that the completed stages of the original OrthoFinder analysis were preserved while the remaining gene-tree inference could be completed in a resumable manner.

## Gene-tree inference

FastTree v2.2.0 was used to infer individual gene trees from the existing FAMSA alignments.

For each orthogroup, the recovery workflow checked whether a valid gene tree was already present. Existing valid trees were skipped, while missing trees were inferred from their corresponding alignments.

Generated trees were validated before being placed in the final `Gene_Trees` directory.

## Species tree

The existing 36-species concatenated species-tree alignment was used to infer the species tree with FastTree v2.2.0.

The species-tree workflow verifies that the input alignment contains 36 species sequences before inference and performs basic validation of the resulting Newick tree.

## Final quality control

A final QC workflow was used to verify and summarize the completed OrthoFinder analysis.

The QC includes:

- species information;
- number of species;
- orthogroup counts;
- single-copy orthologues;
- phylogenetic hierarchical orthogroups;
- orthologue results;
- comparative-genomics statistics;
- duplication statistics;
- gene-tree counts;
- gene-alignment counts; and
- total result-directory size.

The QC workflow does not rerun OrthoFinder or delete the underlying analysis results.

## Reproducibility

The complete workflow is represented by scripts for protein preparation, OrthoFinder analysis, checkpoint-based gene-tree recovery, species-tree inference, final quality control, and visualization.

The checkpoint-based workflow is included to document the recovery of the gene-tree inference stage after termination of the original process and to make the analysis reproducible without repeating completed DIAMOND, MCL, and FAMSA steps.

## Directory structure

```text
04_OrthoFinder_36_Genomes/
│
├── README.md
│
└── scripts/
    ├── prepare_proteomes/
    │
    ├── orthofinder/
    │   └── run_orthofinder_36.sh
    │
    ├── tree_inference/
    │   ├── run_fusarium36_trees_checkpoint.sh
    │   └── run_fusarium36_species_tree_checkpoint.sh
    │
    ├── downstream_analysis/
    │   └── FUSARIUM36_STEP23_FINAL_QC.sh
    │
    └── visualization/
        ├── plot_species_tree.R
        ├── plot_orthogroup_statistics.R
        ├── plot_gene_family_distribution.R
        └── plot_orthologues.R
Software
OrthoFinder v3.1.5
DIAMOND
MCL
FAMSA
FastTree v2.2.0
