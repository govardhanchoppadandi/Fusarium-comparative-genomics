# CAFE5 Gene Family Expansion and Contraction Analysis

## Overview

This directory contains the CAFE5 workflow used to investigate gene-family
expansion and contraction across 36 Fusarium genomes.

The analysis uses orthogroup gene-family counts generated from the
OrthoFinder comparative genomics workflow.

The workflow consists of two stages:

1. CAFE5 analysis and validation
2. Publication-quality visualization of gene-family expansion and contraction

---

## Directory Structure

```text
05_CAFE5_Gene_Family_Evolution/
│
├── scripts/
│   ├── run_CAFE5_Fusarium36.sh
│   └── plot_CAFE5_Fusarium36_publication.R
│
└── README.md
```

---

## 1. CAFE5 Analysis Pipeline

### Script

```text
scripts/run_CAFE5_Fusarium36.sh
```

This Bash script performs the complete CAFE5 analysis workflow.

### Workflow

The pipeline performs:

1. Conda environment activation
2. CAFE5 program verification
3. R package verification
4. CAFE input validation
5. Original OrthoFinder species-tree validation
6. Midpoint rooting of the species tree
7. Conversion to an ultrametric tree
8. Final tree validation
9. Branch-length diagnostics
10. CAFE5 analysis
11. Likelihood validation
12. Detection of invalid `INF` likelihood results
13. Verification of expected CAFE5 output files
14. Final result summary

The original OrthoFinder species tree is not modified.

---

## 2. Input Files

### Gene-family count file

The CAFE5 analysis uses:

```text
CLEAN_CAFE_INPUT/Fusarium36_CAFE_input.txt
```

This file contains gene-family counts for the 36 Fusarium genomes.

### Original species tree

The original OrthoFinder tree is:

```text
FUSARIUM36_FINAL/Results_Aug12_5/Species_Tree/SpeciesTree_rooted.txt
```

This tree is retained as the original reference tree.

---

## 3. Tree Preparation

The pipeline creates a midpoint-rooted tree:

```text
tree/Fusarium36_midpoint_rooted.nwk
```

A separate ultrametric tree is then generated:

```text
tree/Fusarium36_midpoint_rooted_ultrametric.nwk
```

The final tree is checked for:

- 36 taxa
- rooted topology
- binary topology
- ultrametricity
- positive branch lengths

---

## 4. CAFE5 Analysis

CAFE5 is run using the prepared ultrametric species tree and the
36-species gene-family count matrix.

The analysis uses:

```text
-P 0.05
```

and:

```text
-c 8
```

for the configured CAFE5 analysis.

CAFE5 estimates the gene-family birth/death parameter rather than
manually forcing a lambda value in the analysis script.

---

## 5. Main CAFE5 Output Files

The CAFE5 output directory contains files including:

```text
Base_results.txt
Base_family_likelihoods.txt
Base_family_results.txt
Base_asr.tre
Base_change.tab
Base_count.tab
Base_clade_results.txt
Base_branch_probabilities.tab
Base_report.cafe
cafe.log
```

### Important files

`Base_change.tab`

Contains inferred gene-family changes.

`Base_count.tab`

Contains ancestral and descendant gene-family counts.

`Base_clade_results.txt`

Contains CAFE5 clade-level expansion/contraction results.

`Base_family_results.txt`

Contains family-level results.

`Base_asr.tre`

Contains the ancestral-state reconstruction tree.

`Base_branch_probabilities.tab`

Contains branch-level probabilities.

`Base_report.cafe`

Contains the CAFE5 analysis report.

`cafe.log`

Contains the CAFE5 execution log.

---

## 6. Validation

The pipeline checks the CAFE5 likelihood before accepting the analysis.

Runs producing an `INF` likelihood are rejected by the pipeline and should
not be used for biological interpretation.

The pipeline also verifies the presence of the expected CAFE5 result files.

---

## 7. Publication Figure

### Script

```text
scripts/plot_CAFE5_Fusarium36_publication.R
```

This R script generates the final publication-quality visualization of
gene-family expansion and contraction.

### Figure Design

The figure contains:

- 36 Fusarium genomes
- 35 internal nodes
- Species-tree topology
- Internal-node expansion/contraction pies
- Internal-node `Increase / Decrease` values
- Leader lines connecting values to their corresponding pies
- Tip expansion/contraction pies
- Tip expansion/contraction values
- Genome names
- Expansion and contraction legend

The internal pies remain positioned at their corresponding tree nodes.

The pie sectors represent the relative numbers of expanded and contracted
gene families.

---

## 8. Figure Inputs

The visualization uses:

```text
tree/Fusarium36_midpoint_rooted_ultrametric.nwk
```

and:

```text
FULL_CAFE5/Base_clade_results.txt
```

---

## 9. Figure Outputs

The script generates:

```text
CAFE5_FIGURES/
├── Fusarium36_CAFE5_FINAL_PUBLICATION.png
├── Fusarium36_CAFE5_FINAL_PUBLICATION.pdf
└── Fusarium36_CAFE5_FINAL_PUBLICATION_annotations.tsv
```

### PNG

`Fusarium36_CAFE5_FINAL_PUBLICATION.png`

High-resolution raster figure suitable for inspection and presentation.

### PDF

`Fusarium36_CAFE5_FINAL_PUBLICATION.pdf`

Vector-format figure suitable for publication workflows.

### Annotation table

`Fusarium36_CAFE5_FINAL_PUBLICATION_annotations.tsv`

Contains the CAFE5 node identifiers and corresponding expansion and
contraction values used for the visualization.

---

## 10. Reproducibility

The CAFE5 analysis should be performed before generating the publication
figure.

Recommended workflow:

```text
OrthoFinder
     |
     v
Orthogroup gene counts
     |
     v
CAFE5 input preparation
     |
     v
run_CAFE5_Fusarium36.sh
     |
     v
CAFE5 results
     |
     v
plot_CAFE5_Fusarium36_publication.R
     |
     v
Publication figure
```

---

## 11. Software

The workflow uses:

- CAFE5
- R
- ape
- phangorn
- Bash
- Conda

The analysis was performed using the project-specific Conda environment
configured for the Fusarium comparative genomics workflow.

---

## 12. Relationship to Other Comparative Genomics Analyses

CAFE5 analysis forms part of the comparative genomics workflow:

```text
Genome quality assessment
        |
        v
Phylogenetic analysis
        |
        v
Orthology analysis
        |
        v
Gene duplication analysis
        |
        v
CAFE5 gene-family evolution
        |
        v
Expansion / contraction visualization
```

Together, these analyses characterize genome structure, orthologous
relationships, gene duplication, and gene-family evolution across the
Fusarium genomes.
