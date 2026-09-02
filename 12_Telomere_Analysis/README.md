# Telomere Analysis

## Overview

This workflow performs telomere repeat analysis across multiple Fusarium genomes using **tidk** in an Ubuntu/WSL environment.

The workflow:

1. Creates a conda environment containing tidk.
2. Builds the tidk database.
3. Organizes genome input files.
4. Searches for the canonical fungal telomeric repeat motif `TTAGGG`.
5. Uses a 1000 bp search window.
6. Merges tidk results from multiple genomes.
7. Generates genome-level and scaffold-level summary tables.
8. Generates a text summary of the telomere results.

## Directory Structure

```text
12_Telomere_Analysis/
│
├── README.md
│
└── scripts/
    ├── 01_run_tidk.sh
    ├── 02_merge_tidk_results.py
    ├── 03_summarise_telomeres.py
    └── 04_generate_results_text.py
```

## Software Requirements

### Ubuntu / WSL

The workflow is designed for Ubuntu running through WSL.

### Conda

Create the tidk environment:

```bash
conda create -n tidk_env -c bioconda tidk -y
```

Activate it:

```bash
conda activate tidk_env
```

### Python packages

The Python scripts require:

```bash
pip install pandas openpyxl
```

## Step 1: Build the tidk Database

After activating the environment:

```bash
tidk build
```

## Step 2: Create the Analysis Directory

Create the required directories:

```bash
mkdir -p telomere_analysis/data/genomes
mkdir -p telomere_analysis/results/telomere
mkdir -p telomere_analysis/scripts

cd telomere_analysis
```

Copy the genome FASTA files into:

```text
telomere_analysis/data/genomes/
```

The analysis can then be run on all `.fa` files in this directory.

## Step 3: Run tidk

The script:

```text
scripts/01_run_tidk.sh
```

searches each genome for the canonical fungal telomeric motif:

```text
TTAGGG
```

using a:

```text
1000 bp
```

window.

Make the script executable:

```bash
chmod +x scripts/01_run_tidk.sh
```

Run:

```bash
bash scripts/01_run_tidk.sh
```

The tidk results are written under:

```text
results/telomere/
```

## Step 4: Merge tidk Results

Run:

```bash
python scripts/02_merge_tidk_results.py
```

This collects the tidk files matching:

```text
*_telomeric_repeat_windows.tsv
```

and combines them into:

```text
results/telomere/Telomere_Analysis_All_Genomes.xlsx
```

The combined table contains the tidk records together with a `Genome` column.

## Step 5: Generate Summary Tables

Run:

```bash
python scripts/03_summarise_telomeres.py
```

The script calculates:

- Number of telomeric repeat windows
- Number of scaffolds represented
- Mean repeats per window
- Maximum repeats per window
- Total repeats per scaffold

The output is:

```text
results/telomere/Telomere_Analysis_Summary.xlsx
```

The workbook contains:

```text
All_Telomere_Windows
Genome_Summary
Scaffold_Summary
```

## Step 6: Generate Results Text

Run:

```bash
python scripts/04_generate_results_text.py
```

The script reads the genome summary and prints a concise Results-style description of the telomeric repeat findings.

The current script specifically reports `DMW_8` and `TNW_1` first, followed by other genomes as reference genomes.

## Workflow

```text
Fusarium genome FASTA files
          │
          ▼
        tidk
          │
          ▼
Telomeric repeat windows
          │
          ▼
02_merge_tidk_results.py
          │
          ▼
Telomere_Analysis_All_Genomes.xlsx
          │
          ▼
03_summarise_telomeres.py
          │
          ▼
Telomere_Analysis_Summary.xlsx
          │
          ▼
04_generate_results_text.py
          │
          ▼
Results-style telomere summary
```

## Main Parameters

| Parameter | Setting |
|---|---|
| Telomeric motif | `TTAGGG` |
| Search window | `1000 bp` |
| Primary analysis genomes reported by the Results script | `DMW_8`, `TNW_1` |
| Input format | FASTA (`.fa`) |
| Main merged output | `Telomere_Analysis_All_Genomes.xlsx` |
| Main summary output | `Telomere_Analysis_Summary.xlsx` |

## Input Data

Genome FASTA files are analysis inputs and are not included in this repository.

Place the required genome files in:

```text
telomere_analysis/data/genomes/
```

The scripts use local paths and can therefore be adapted to the user's WSL directory structure.

## Outputs

The main outputs are:

```text
results/telomere/
├── *_telomeres_telomeric_repeat_windows.tsv
├── Telomere_Analysis_All_Genomes.xlsx
└── Telomere_Analysis_Summary.xlsx
```

Individual tidk working directories may also be produced under:

```text
results/telomere/
```

## Reproducibility

The computational scripts used for telomere detection, result merging, summary generation, and Results-text generation are provided in this directory.

Large genome FASTA files, tidk intermediate directories, and generated result files are kept outside the GitHub source-code directory.

## Notes

- The canonical fungal telomeric motif used in this workflow is `TTAGGG`.
- The search window is set to 1000 bp.
- The merge script expects tidk output files named with the suffix `_telomeric_repeat_windows.tsv`.
- The summary script expects the tidk output columns `forward_repeat_number`, `reverse_repeat_number`, and `id`.
- The Results-text script currently expects `DMW_8` and `TNW_1` to be present in the genome summary.
- If different genomes are analyzed, the genome names in `04_generate_results_text.py` should be changed accordingly.

## Citation

Please cite the appropriate **tidk** publication/software documentation when reporting telomere analysis performed with this workflow.

## Section

This analysis is part of the **Telomere Analysis** workflow in the Fusarium genome analysis project.
