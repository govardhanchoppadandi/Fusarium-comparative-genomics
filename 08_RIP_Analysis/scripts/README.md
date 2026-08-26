# RIP Analysis

## Purpose

Repeat-induced point mutation (RIP) was assessed across the Fusarium genomes using RIPCAL v2.0. The RIP analysis was performed to identify RIP-positive genomic regions and to examine their overlap with transposable-element (TE) annotations.

## Software

| Software | Version | Purpose |
|---|---|---|
| RIPCAL | 2.0 | RIP index scanning |
| BEDTools | 2.31.1 | BED sorting, merging, and RIP–TE intersections |
| EarlGrey | Completed previously | Transposable-element annotation |
| Conda | 26.7.0 | Environment and package management |
| Ubuntu / WSL2 | Ubuntu 24.04.4 LTS | Linux analysis environment |

RepeatScout and RECON were installed as dependencies through EarlGrey.

## Input

The analysis uses:

- Fusarium genome assemblies in FASTA format (`.fna`)
- EarlGrey TE annotations
- EarlGrey merged-repeat BED files located under the `TE_analysis` directory

The RIP pipeline searches for the corresponding EarlGrey TE annotation automatically.

## RIP Analysis

Genome-wide RIP scans were performed using RIPCAL v2.0.

The following parameters were used:

- Mode: scan
- Window size: 1,000 bp
- Step size: 500 bp

The RIPCAL command used by the analysis script is:

```bash
ripcal -c -seq genome.fna -type scan -l 1000 -i 500
```

RIPCAL output was retained as the raw RIP scan result.

## Processing of RIP Regions

RIPCAL scan output was converted to BED format.

BEDTools v2.31.1 was then used to:

1. Sort RIP-positive regions.
2. Merge overlapping or adjacent RIP-positive windows.
3. Generate merged RIP regions (LRARs).
4. Intersect RIP/LRAR regions with EarlGrey TE annotations.

The BED coordinate conversion accounts for the difference between RIPCAL's 1-based coordinates and BED's 0-based start coordinates.

## RIP–TE Intersection

RIP/LRAR regions were intersected with EarlGrey TE annotations using BEDTools.

The TE annotation used for the intersection is the EarlGrey merged-repeat annotation:

```text
mergedRepeats/looseMerge/*.filteredRepeats.bed
```

This allows the relationship between RIP-affected regions and transposable elements to be examined.

## Workflow

```text
Fusarium genome assemblies
        |
        v
     RIPCAL v2.0
        |
        | 1,000-bp window
        | 500-bp step
        v
RIP-positive scan windows
        |
        v
     BEDTools
        |
        +--> sort
        |
        +--> merge
        |
        v
Merged RIP regions (LRARs)
        |
        v
RIP–TE intersection
        |
        v
RIP–TE overlap results
```

## Script

The complete analysis is implemented in:

```text
scripts/RIPCAL/run_RIP_all.sh
```

## Software Setup

The RIPCAL environment was created using Conda:

```bash
conda create -n ripcal_env -c bioconda -c conda-forge ripcal bedtools -y
```

Activate the environment:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate ripcal_env
```

Verify the installations:

```bash
which ripcal
ripcal --version

which bedtools
bedtools --version
```

Expected software versions:

```text
RIPCAL 2.0
BEDTools 2.31.1
```

## Running the Analysis

After activating the environment:

```bash
cd /mnt/d/genomes_clean
```

Make the script executable:

```bash
chmod +x run_RIP_all.sh
```

Run the analysis:

```bash
./run_RIP_all.sh
```

The script automatically processes the available `.fna` genome files and skips genomes for which the required RIP and LRAR outputs have already been generated.

## Output

For each genome, the pipeline generates a `RIP_analysis` directory containing:

```text
GENOME/
└── RIP_analysis/
    ├── GENOME_RIP_raw_scan.txt
    ├── GENOME_RIP.bed
    ├── GENOME_LRAR.bed
    ├── GENOME_RIP_regions.tsv
    └── GENOME_RIP_TE_overlap.txt
```

### Output descriptions

`*_RIP_raw_scan.txt`  
Original RIPCAL scan output.

`*_RIP.bed`  
RIP-positive scanning windows converted to BED format.

`*_LRAR.bed`  
Merged overlapping or adjacent RIP-positive regions.

`*_RIP_regions.tsv`  
Three-column representation of merged RIP regions:

```text
scaffold    start    end
```

`*_RIP_TE_overlap.txt`  
BEDTools intersection results between merged RIP regions and EarlGrey TE annotations.

## Reproducibility

The script provided in this repository documents the RIP analysis workflow used in the study, including the software, parameters, coordinate conversion, region merging, and RIP–TE intersection steps.

Large genome assemblies, TE annotation files, raw RIPCAL outputs, and intermediate analysis files are not included in this repository.

## Repository Location

```text
08_RIP_Analysis/
├── README.md
└── scripts/
    └── RIPCAL/
        └── run_RIP_all.sh
```
