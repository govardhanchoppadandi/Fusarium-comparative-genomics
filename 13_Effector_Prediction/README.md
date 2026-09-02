# Effector Prediction — FASTA Preparation

This module contains scripts used to prepare protein FASTA files for downstream effector-prediction analyses in the comparative-genomics workflow.

## Repository structure

```text
13_Effector_Prediction/
├── README.md
└── scripts/
    └── fasta_preparation/
        └── split_fasta_chunks.py
```

## Purpose

The `fasta_preparation` script splits a protein FASTA file into smaller FASTA files containing a fixed number of protein sequences per file.

The current script uses **250 protein sequences per chunk**.

This is useful when a downstream prediction server or software has a limit on the number of sequences that can be submitted in a single run.

## Script

```text
scripts/fasta_preparation/split_fasta_chunks.py
```

The script is written in **Python 3**.

## Input

The script requires a protein FASTA file.

Example input:

```text
SP_proteins.fasta
```

In the current analysis, the input file is:

```text
E:\1 Manuscript\Fusarium genome\DNW-8 Augustus\SIGNALP\SP_proteins.fasta
```

The input path can be changed directly in the Python script.

## Output

The script creates an output directory and writes FASTA chunks such as:

```text
proteins_chunk_1.fasta
proteins_chunk_2.fasta
proteins_chunk_3.fasta
...
```

Each chunk contains a maximum of **250 protein sequences**.

For example, if the input contains 600 proteins:

```text
proteins_chunk_1.fasta    250 proteins
proteins_chunk_2.fasta    250 proteins
proteins_chunk_3.fasta    100 proteins
```

## Running the script

Open Windows PowerShell, Command Prompt, or another terminal with Python available.

Check Python:

```bash
python --version
```

Run the script:

```bash
python split_fasta_chunks.py
```

Alternatively, from the repository root:

```bash
python 13_Effector_Prediction/scripts/fasta_preparation/split_fasta_chunks.py
```

## Required Python packages

No external Python packages are required.

The script uses the standard Python library:

```python
from pathlib import Path
```

Therefore, a standard Python 3 installation is sufficient.

## Main parameters

The number of sequences per FASTA chunk is controlled by:

```python
chunk_size = 250
```

To change the chunk size, modify this value.

Examples:

```python
chunk_size = 100
```

or:

```python
chunk_size = 500
```

## FASTA handling

The script:

1. Reads the complete protein FASTA file.
2. Identifies FASTA headers beginning with `>`.
3. Reconstructs each protein sequence.
4. Divides the proteins into groups of 250.
5. Writes each group to a separate FASTA file.
6. Wraps protein sequences at 80 characters per line.
7. Prints a summary showing the total number of proteins and chunks created.

## Output location

The current script writes chunks to:

```text
E:\1 Manuscript\Fusarium genome\DNW-8 Augustus\SIGNALP\SP CHUNKS 250
```

The output location can be changed using the `output_folder` variable.

## Reproducibility

For reproducibility, record:

- Python version
- Input FASTA filename
- Number of protein sequences in the input
- Chunk size
- Output directory

Check the Python version with:

```bash
python --version
```

## Relationship to effector prediction

This module is a **FASTA preparation step**. It does not itself predict effectors.

The prepared protein chunks can be supplied to downstream prediction tools or servers that require smaller input batches.

The repository should therefore keep FASTA preparation scripts separate from the actual effector-prediction analyses.

## Important

Large protein FASTA files and generated chunk files should generally not be committed to GitHub unless they are intentionally included as part of the reproducible dataset.

The GitHub repository should primarily contain:

- Scripts
- README documentation
- Configuration or parameter information
- Small example/test files where appropriate
- Selected results or summary tables when appropriate

## Workflow

```text
SignalP-positive protein FASTA
            │
            ▼
   split_fasta_chunks.py
            │
            ▼
   ┌─────────────────────┐
   │ proteins_chunk_1    │
   │ proteins_chunk_2    │
   │ proteins_chunk_3    │
   │        ...          │
   └─────────────────────┘
            │
            ▼
 Downstream effector
 prediction analyses
```
