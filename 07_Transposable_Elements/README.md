# Transposable Element Analysis

## Overview

This directory contains the reproducible workflow used for transposable element (TE) analysis of Fusarium genomes using EarlGrey v7.3.0.

The workflow covers:

1. EarlGrey installation using Pixi on Ubuntu/WSL.
2. SA-SSR build.
3. EarlGrey environment installation.
4. GenomeInfoDbData troubleshooting.
5. Dfam database setup.
6. Telomere/TE-related repeat annotation through EarlGrey.
7. Running EarlGrey on individual genomes.
8. Batch processing of multiple `.fna` genomes.
9. Automatically skipping genomes that have already completed.
10. Organizing EarlGrey outputs for downstream TE summaries.

## Directory Structure

```text
07_Transposable_Elements/
│
├── README.md
│
└── scripts/
    ├── earl_grey/
    │   └── run_all_earlgrey.sh
    │
    └── summary/
```

The `summary/` directory is reserved for downstream scripts that summarize and compare EarlGrey results across genomes.

## Software

### EarlGrey

EarlGrey version used:

```text
v7.3.0
```

### Installation on Ubuntu / WSL

Clone EarlGrey:

```bash
cd ~

git clone https://github.com/TobyBaril/EarlGrey.git

cd EarlGrey
```

Install Pixi:

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

Restart the terminal and check:

```bash
pixi --version
```

Enter the EarlGrey Pixi directory:

```bash
cd ~/EarlGrey/pixi
```

Install the environment:

```bash
pixi install
```

Build SA-SSR:

```bash
pixi run build-sassr
```

Install EarlGrey:

```bash
pixi run install
```

Check EarlGrey:

```bash
earlGrey -h
```

## GenomeInfoDbData Troubleshooting

If R reports:

```text
there is no package called 'GenomeInfoDbData'
```

reinstall the Pixi environment:

```bash
cd ~/EarlGrey/pixi

pixi clean

pixi install
```

Check whether the package is present:

```bash
ls ~/EarlGrey/pixi/.pixi/envs/default/lib/R/library | grep GenomeInfoDbData
```

Expected:

```text
GenomeInfoDbData
```

Check GenomeInfoDb packages:

```bash
pixi list | grep Genome
```

Expected packages include:

```text
bioconductor-genomeinfodb
bioconductor-genomeinfodbdata
```

## Dfam Database

The workflow uses the Dfam database components required by EarlGrey.

The downloaded components used in the analysis were:

```text
dfam40.0.h5
dfam40.curated.consensus.0.h5
dfam40.uncurated.consensus.0.h5
dfam40.uncurated.consensus.1.h5
dfam40.uncurated.hmm.0.h5
dfam40.uncurated.hmm.108.h5
```

The Dfam download utility can be started with:

```bash
download_dfam.py
```

The selected partitions were:

```text
1,2,4,5
```

For Uncurated Consensus:

```text
0,1
```

For Uncurated HMM:

```text
0,108
```

Check the fungal Dfam database:

```bash
famdb.py check fungi
```

The expected setup contains:

- Curated Consensus
- Uncurated Consensus
- Uncurated HMM

The Curated HMM component is optional for this workflow and was not required because of its large size.

## Running EarlGrey on One Genome

Example:

```bash
earlGrey \
    -g Fgram_0343.fna \
    -s Fgram_0343 \
    -o TE_analysis/Fgram_0343 \
    -t 2 \
    -i 3 \
    -n 10
```

Parameters:

| Parameter | Meaning |
|---|---|
| `-g` | Genome FASTA file |
| `-s` | Sample/genome identifier |
| `-o` | Output directory |
| `-t 2` | Number of threads |
| `-i 3` | EarlGrey iteration setting |
| `-n 10` | Requested analysis setting |

## Running All Genomes

The batch script is:

```text
scripts/earl_grey/run_all_earlgrey.sh
```

Make it executable:

```bash
chmod +x scripts/earl_grey/run_all_earlgrey.sh
```

Run:

```bash
./scripts/earl_grey/run_all_earlgrey.sh
```

The script searches the current directory for `.fna` genome files.

Each genome is written to:

```text
TE_analysis/<GENOME_NAME>/
```

Completed genomes are detected using the expected EarlGrey summary output and skipped automatically.

## Adding New Genomes

If additional `.fna` genomes are added later, run the batch script again:

```bash
./scripts/earl_grey/run_all_earlgrey.sh
```

Previously completed genomes are skipped automatically, while new genomes are processed.

## Expected EarlGrey Outputs

Depending on the EarlGrey run and version, the analysis produces output directories containing summary and repeat-annotation files such as:

```text
Genome_summaryFiles/
filteredRepeats.gff
filteredRepeats.bed
highLevelCount.txt
familyLevelCount.txt
families.fa.strained
summaryPie.pdf
classification_landscape.pdf
split_class_landscape.pdf
superfamily_div_plot.pdf
```

These generated results should normally remain outside the GitHub repository.

## Software Components

The EarlGrey environment provides the required repeat-analysis and supporting software, including:

### Repeat Annotation

- RepeatMasker
- RepeatModeler
- RepeatScout
- RECON
- RMBlast
- TRF
- LTR Retriever
- MREPS
- GenomeTools
- Heliano

### Sequence / Alignment / Utilities

- MAFFT
- HMMER
- BEDTools
- SAMtools
- EMBOSS
- GNU Parallel
- CD-HIT

### Python Packages

- NumPy
- Pandas
- PyRanges
- PyBedTools
- PyFaidx
- NCLS

### R / Bioconductor Packages

- GenomeInfoDb
- GenomeInfoDbData
- BSgenome
- Plyranges
- ape
- tidyverse
- cowplot
- ggtext
- data.table
- viridis
- magrittr
- kableExtra
- optparse
- plyr

## Input Data

Genome FASTA files should be supplied locally as:

```text
*.fna
```

Large genome files, Dfam databases, and generated EarlGrey results are intentionally not included in this repository.

## Reproducibility

The GitHub directory contains the workflow documentation and executable batch script, while large input and output datasets are maintained separately.

Workflow:

```text
Fusarium genome FASTA
          │
          ▼
       EarlGrey
          │
          ▼
Repeat annotation
          │
          ▼
TE classification
          │
          ▼
Genome-level summaries
          │
          ▼
Downstream comparative TE analysis
```

## Citation

If EarlGrey is used in a publication, cite the EarlGrey software and the associated repeat-analysis databases/tools according to their official documentation.

## Project Section

This analysis is part of the **Transposable Element Analysis** workflow in the Fusarium comparative genomics project.
