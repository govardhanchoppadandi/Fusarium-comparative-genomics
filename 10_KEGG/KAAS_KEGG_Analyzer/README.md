# KAAS → KEGG Pathway Analyzer

A local Python/Streamlit application for automated analysis of completed KEGG Automatic Annotation Server (KAAS) results and mapping of protein sequences to KO, EC, and KEGG pathway annotations.

## Overview

The analyzer takes:

* A completed KAAS result URL
* The original protein FASTA file
* An output directory
* KEGG API batch size
* Delay between KEGG requests

The workflow automatically performs:

```text
Completed KAAS Result
        ↓
     query.ko
        ↓
Protein ID → KO ID
        ↓
FASTA–KAAS ID Validation
        ↓
    Unique KO IDs
        ↓
      KEGG API
        ↓
KO / Enzyme / EC / Pathway
        ↓
Protein → KO → Pathway
        ↓
Excel Workbook
```

## Features

The application provides:

* KAAS `query.ko` retrieval
* KAAS result parsing
* Protein ID extraction
* FASTA ID extraction
* FASTA–KAAS ID validation
* Protein-to-KO mapping
* Identification of proteins without KO assignments
* Unique KO identification
* KO information retrieval
* EC/enzyme annotation
* KEGG pathway annotation
* Protein-level pathway mapping
* Pathway summaries
* Excel workbook generation
* KEGG response caching
* Resumable analysis

## Requirements

Recommended environment:

* Ubuntu or WSL
* Python 3.12
* Conda
* Internet connection
* Access to the completed KAAS result
* Original protein FASTA file

## Installation

Create the Conda environment:

```bash
conda create -n kaas_env python=3.12
conda activate kaas_env
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Run the graphical application

From the analyzer directory:

```bash
chmod +x run_app.sh
./run_app.sh
```

Streamlit will display a local address such as:

```text
http://localhost:8501
```

The port may differ if another Streamlit application is already running.

Open the displayed address in a web browser.

## Application inputs

The application requires the following information.

### 1. Completed KAAS result URL

Enter the URL provided by KAAS after the annotation job has completed.

Example format:

```text
https://www.genome.jp/kaas-bin/kaas_main?mode=user&id=JOB_ID&key=JOB_KEY
```

Do not publish a real KAAS URL containing private job information.

### 2. Original protein FASTA

Provide the original FASTA file containing the protein sequences submitted to KAAS.

Example Ubuntu/WSL path:

```text
/mnt/d/interpro/combind fasta.faa
```

The protein identifiers in the FASTA should correspond to the identifiers used in the KAAS submission.

### 3. Output directory

Specify where the generated analysis files should be stored.

Example:

```text
KAAS_KEGG_Results
```

### 4. KEGG batch size

The default batch size can normally be retained unless a different value is required.

Example:

```text
10
```

### 5. Delay between KEGG requests

A delay should be maintained between requests to avoid excessive API requests.

Example:

```text
1
```

## Command-line workflow

For non-interactive execution:

```bash
chmod +x run_kaas_kegg.sh
./run_kaas_kegg.sh
```

The script will request the required KAAS URL, FASTA path, output location, batch size, and request delay.

## Output

The analysis generates structured annotation tables and an Excel workbook containing information such as:

* Protein identifiers
* KO identifiers
* KO descriptions
* EC/enzyme information
* KEGG pathway identifiers
* KEGG pathway descriptions
* Protein-to-pathway relationships
* Pathway summaries
* FASTA/KAAS matching information

Generated files should remain outside version control.

## Important data policy

Do not upload the following to the public repository:

```text
KAAS job URLs
Private KAAS access keys
Protein FASTA files
Downloaded query.ko files
KEGG cache files
Generated Excel files
Generated result tables
Personal datasets
```

These files may contain project-specific or user-specific information and are intentionally excluded from version control.

## Reproducibility

The repository provides the application code, supporting modules, installation requirements, and execution scripts necessary to reproduce the workflow.

Users provide their own KAAS result and corresponding protein FASTA file.

## KEGG usage

This application accesses KEGG resources through available KEGG services. Users are responsible for complying with the applicable KEGG terms, usage conditions, and request-rate limitations.

## License

See the repository-level `LICENSE` file for licensing information.

## Citation

Please cite the main repository and the relevant KAAS/KEGG resources when this software contributes to a publication.
