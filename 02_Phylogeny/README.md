# Multi-Gene Fusarium Phylogeny

## Purpose

This directory contains the scripts used to construct the multi-gene phylogeny of *Fusarium* isolates using ITS, TEF1, and RPB2 sequences.

## Workflow

ITS + TEF1 + RPB2 sequences  
↓  
MAFFT alignment  
↓  
Alignment inspection  
↓  
AMAS concatenation  
↓  
Partition file generation  
↓  
Alignment-length validation  
↓  
IQ-TREE maximum-likelihood analysis  
↓  
Phylogenetic tree  
↓  
R-based visualization

## Genes

- ITS
- TEF1
- RPB2

## Software

- MAFFT
- AMAS
- IQ-TREE 2
- R
- ape
- ggtree
- ggplot2

## Alignment

Individual gene sequences were aligned using MAFFT with the `--auto` option.

Script:

`scripts/alignment/run_mafft.sh`

## Concatenation

The aligned ITS, TEF1, and RPB2 sequences were concatenated using AMAS.

The AMAS workflow also generated a partition file for downstream phylogenetic inference.

Script:

`scripts/concatenation/run_amas.sh`

## Alignment Validation

The concatenated alignment was checked to confirm that all taxa had identical alignment lengths before phylogenetic inference.

## Phylogenetic Inference

Maximum-likelihood phylogenetic inference was performed using IQ-TREE 2.

Parameters:

- Model selection: `MFP`
- Partition model merging: `MERGE`
- Ultrafast bootstrap: 1000 replicates
- SH-aLRT: 1000 replicates
- Number of threads: `AUTO`

Script:

`scripts/tree_inference/run_iqtree.sh`

## Phylogenetic Visualization

The resulting consensus tree was rooted using *Neonectria ditissima* CBS100316 as the outgroup and visualized using R and ggtree.

The visualization highlights the study isolates:

- *Fusarium graminearum* TNW1
- *Fusarium avenaceum* DMW8

Script:

`scripts/visualization/plot_phylogeny.R`

## Input

The workflow requires:

- ITS FASTA sequences
- TEF1 FASTA sequences
- RPB2 FASTA sequences

## Main Outputs

- Gene-specific aligned FASTA files
- Concatenated alignment
- Partition file
- IQ-TREE tree files
- Maximum-likelihood phylogenetic tree
- Publication-quality TIFF figure

## Reproducibility

The scripts document the phylogenetic workflow used in the associated study. Raw sequence files and generated intermediate files are not included in this repository.
