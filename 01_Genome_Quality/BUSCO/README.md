# BUSCO Genome and Protein Completeness

## Purpose

BUSCO was used to assess the completeness of the *Fusarium* genome assemblies and predicted proteomes used in this study.

## Software

- BUSCO v5.8.3
- `hypocreales_odb10` lineage dataset

## Analyses

### Genome BUSCO

Genome assemblies in FASTA format (`.fna`) were analyzed using BUSCO genome mode.

Parameters:

- Mode: `genome`
- Lineage: `hypocreales_odb10`
- CPU: 6

Script:

`run_busco_genomes.sh`

### Protein BUSCO

Predicted protein sequences in FASTA format (`.faa`) were analyzed using BUSCO protein mode.

Parameters:

- Mode: `proteins`
- Lineage: `hypocreales_odb10`
- CPU: 4

Scripts:

- `run_busco_proteins.sh`
- `run_busco_proteins_resume.sh`

## Input

- Genome FASTA files (`.fna`)
- Predicted protein FASTA files (`.faa`)

## Output

BUSCO produces:

- Complete BUSCOs
- Complete and single-copy BUSCOs
- Complete and duplicated BUSCOs
- Fragmented BUSCOs
- Missing BUSCOs
- BUSCO summary files

## Reproducibility

The scripts provided here document the BUSCO analyses used in the study. Input genome and protein FASTA files and BUSCO output directories are not included in this repository.
