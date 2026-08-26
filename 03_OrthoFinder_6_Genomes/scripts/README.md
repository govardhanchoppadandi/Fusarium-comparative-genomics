# 09. Orthology & Gene Duplication Analysis

## Overview

Orthology and gene duplication analyses were performed using OrthoFinder
results to characterize shared orthogroups, ortholog multiplicity, gene
duplication patterns, and the distribution of duplicated genes across the
six Fusarium genomes.

Two R scripts were used to generate the visualization set.

## Species analyzed

- Fusarium graminearum
- Fusarium graminearum isolate TNW1
- Fusarium culmorum
- Fusarium poae
- Fusarium avenaceum
- Fusarium avenaceum isolate DMW8

## Input files

The scripts use the following OrthoFinder output files:

```text
Orthogroups/Orthogroups.GeneCount.tsv
Gene_Duplication_Events/Duplications.tsv
Species_Tree/SpeciesTree_rooted.txt
```

### Orthogroups.GeneCount.tsv

Used to calculate:

- Shared orthogroups between species
- Number of genes assigned to orthogroups
- Number of orthogroups represented in each species
- Ortholog multiplicity patterns

### Duplications.tsv

Used to characterize:

- Gene duplication events
- Species-specific duplication counts
- Duplication events associated with internal species-tree nodes
- Duplication links for Circos visualization

### SpeciesTree_rooted.txt

Used to visualize the species phylogeny together with orthogroup counts.

# Script 1: Orthology and Gene Duplication Plots

## Script

```text
plot_orthology_gene_duplication.R
```

The script generates eight primary figures.

### Figure 1 – Shared Orthogroups Heatmap

```text
01_shared_orthogroups_heatmap.png
```

Displays the number of orthogroups shared between every pair of Fusarium species.

### Figure 2 – Genes in Orthogroups

```text
02_genes_in_orthogroups.png
```

Shows the total number of genes assigned to orthogroups in each genome.

### Figure 3 – Orthogroups per Species

```text
03_orthogroups_per_species.png
```

Shows the number of orthogroups represented in each species.

### Figure 4 – Ortholog Multiplicity: F. graminearum

```text
04_multiplicity_Fgram.png
```

Classifies orthogroups shared between F. graminearum and each other species into:

- One-to-one
- One-to-many
- Many-to-one
- Many-to-many

### Figure 5 – Ortholog Multiplicity: F. poae

```text
05_multiplicity_Fpoae.png
```

Classifies orthogroup relationships between F. poae and the other species.

### Figure 6 – Gene Duplications per Species

```text
06_duplications_per_species.png
```

Shows the number of duplication events associated with each species.

### Figure 7 – Duplications per Internal Node

```text
07_duplications_per_node.png
```

Shows the number of inferred duplication events associated with internal nodes of the species tree.

### Figure 8 – Species Tree with Orthogroup Counts

```text
08_species_tree_with_OG_counts.png
```

Displays the rooted species tree with the number of orthogroups associated with each genome.

# Script 2: Circos Duplication Analysis

## Script

```text
plot_circos_duplications.R
```

The Circos analysis visualizes duplication relationships between genes across the six Fusarium genomes.

### All duplication events

```text
H_all_duplications.png
```

Shows the overall distribution and connectivity of duplication events.

### High-confidence duplication events

```text
G_highconfidence_duplications.png
```

Shows duplication links supported by:

```text
Support >= 0.98
```

### PDF version

```text
H_all_duplications.pdf
```

A high-resolution PDF version of the complete duplication Circos plot is generated for manuscript preparation.

# Visualization components

The Circos plots contain:

1. Species sectors
2. Species labels
3. Duplication-density heatmap
4. Duplication-density histogram
5. Gene-to-gene duplication links
6. High-confidence duplication links
7. Duplication-density legend

The species are displayed using consistent colors across the analysis.

# Software

The analysis was performed in R using:

- readr
- dplyr
- tidyr
- ggplot2
- stringr
- ape
- ggtree
- openxlsx
- tibble
- circlize

OrthoFinder was used for orthology inference and gene duplication analysis.

# Output directory

All figures are saved to the designated plots directory:

```text
plots/
```

# Reproducibility

Run the two R scripts:

```text
1. plot_orthology_gene_duplication.R
2. plot_circos_duplications.R
```

The scripts read the corresponding OrthoFinder output files and generate the complete orthology and gene-duplication visualization set.

# Summary

This workflow provides complementary views of genome-wide orthology and gene duplication patterns among the six Fusarium genomes, including:

- Orthogroup sharing
- Orthogroup representation
- Gene assignment to orthogroups
- Ortholog multiplicity
- Species-associated duplication events
- Internal-node duplication events
- Species phylogeny with orthogroup counts
- Genome-wide duplication connectivity
- High-confidence duplication relationships
