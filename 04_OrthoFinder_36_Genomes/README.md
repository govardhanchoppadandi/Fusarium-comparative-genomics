# OrthoFinder analysis of 36 *Fusarium* genomes

## Overview

Orthology analysis was performed across 36 *Fusarium* proteomes using OrthoFinder v3.1.5.

The workflow used DIAMOND for protein sequence similarity searches, MCL for orthogroup inference, FAMSA for multiple sequence alignment, and FastTree v2.2.0 for gene-tree inference.

The analysis was performed as a checkpointed workflow so that completed computational stages could be retained and recovered without repeating previously completed steps.

---

## Input

The analysis used predicted protein sequences from 36 *Fusarium* genomes.

Protein FASTA files were prepared and standardized before OrthoFinder analysis.

The input consisted of one protein FASTA file per genome/species.

---

## OrthoFinder analysis

OrthoFinder v3.1.5 was used to infer orthogroups and phylogenetic relationships among the 36 *Fusarium* proteomes.

The principal software configuration was:

| Component | Software |
|---|---|
| Orthology analysis | OrthoFinder v3.1.5 |
| Sequence search | DIAMOND |
| Orthogroup inference | MCL |
| Multiple sequence alignment | FAMSA |
| Gene-tree inference | FastTree v2.2.0 |

The OrthoFinder workflow initially generated the sequence-search results, orthogroup assignments, and multiple sequence alignments.

Because gene-tree inference was computationally intensive for the large number of orthogroups, the analysis was subsequently completed using a checkpoint-based gene-tree recovery workflow.

---

## Checkpoint-based gene-tree recovery

The existing OrthoFinder results were retained and used as the starting point for gene-tree recovery.

The recovery workflow used the existing FAMSA alignments as input to FastTree v2.2.0.

The recovery workflow:

- did not rerun DIAMOND;
- did not rerun MCL;
- did not rerun FAMSA;
- did not delete existing OrthoFinder results;
- detected existing valid gene trees and skipped them;
- generated missing gene trees from existing alignments;
- validated generated Newick trees;
- recorded completed orthogroups;
- recorded failed orthogroups; and
- allowed the analysis to be resumed after interruption.

This approach preserved the completed stages of the original OrthoFinder analysis while allowing the remaining gene-tree inference to be completed independently and reproducibly.

---

## Gene-tree inference

FastTree v2.2.0 was used to infer individual gene trees from the existing FAMSA protein alignments.

For each orthogroup, the checkpoint workflow checked whether a valid gene tree was already present.

Existing valid trees were skipped.

For orthogroups without a valid tree, FastTree was executed using the corresponding protein alignment.

Generated trees were checked for valid Newick output before being placed in the `Gene_Trees` directory.

The workflow therefore supported incremental completion and safe resumption without repeating completed gene-tree calculations.

---

## Species tree

The existing 36-species concatenated species-tree alignment was used as input for species-tree inference with FastTree v2.2.0.

The species-tree checkpoint workflow:

1. verifies that the species-tree alignment exists;
2. verifies that 36 species sequences are present;
3. runs FastTree on the existing concatenated alignment;
4. checks the resulting Newick output; and
5. writes the validated species tree to the results directory.

The species-tree workflow does not rerun OrthoFinder, DIAMOND, MCL, FAMSA, or gene-tree inference.

---

## Final quality control

A final quality-control workflow was used to verify and summarize the completed comparative-genomics analysis.

The QC workflow checks:

- species information;
- number of species;
- species-tree files;
- total orthogroup count;
- single-copy orthologues;
- phylogenetic hierarchical orthogroups;
- orthologue results;
- comparative-genomics statistics;
- duplication statistics;
- gene-tree count;
- gene-alignment count; and
- total result-directory size.

The QC workflow reports the existing results and does not rerun OrthoFinder or delete analysis files.

---

## Reproducibility

The workflow is represented by scripts covering:

- protein preparation;
- OrthoFinder execution;
- checkpoint-based gene-tree recovery;
- species-tree inference;
- final quality control; and
- visualization.

The checkpoint scripts are included to document the recovery of the gene-tree and species-tree stages while preserving previously completed computational results.

This allows the workflow to be inspected and reproduced without unnecessarily repeating completed DIAMOND, MCL, and FAMSA analyses.

---

## Directory structure

```text
04_OrthoFinder_36_Genomes/
│
├── README.md
│
└── scripts/
    │
    ├── orthofinder/
    │   └── run_orthofinder_36.sh
    │
    ├── tree_inference/
    │   ├── run_fusarium36_trees_checkpoint.sh
    │   ├── run_fusarium36_species_tree_checkpoint.sh
    │   └── run_fusarium36_species_tree_fast.sh
    │
    └── downstream_analysis/
        └── run_fusarium36_step24_corrected.sh
Software
OrthoFinder v3.1.5
DIAMOND
MCL
FAMSA
FastTree v2.2.0
