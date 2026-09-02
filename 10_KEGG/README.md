# KAAS → KEGG Pathway Analyzer

A reproducible command-line and local Streamlit application for processing large KAAS protein annotation results and generating KEGG functional and pathway annotations.

## Overview

The KAAS → KEGG Pathway Analyzer is designed for large fungal proteomes where the KAAS web result page may become difficult to open or download because of the large number of protein identifiers.

The application performs the following workflow:

**KAAS result URL → query.ko download → FASTA ID validation → Protein–KO mapping → KO annotation → EC information → KEGG pathways → Excel output**

The workflow was developed for large-scale fungal comparative genomics analyses and can process hundreds of thousands of protein identifiers.

---

## Input

The application requires two inputs:

### 1. Completed KAAS result URL

A completed KAAS job URL, for example:

```text
https://www.genome.jp/kaas-bin/kaas_main?mode=user&id=YOUR_JOB_ID&key=YOUR_JOB_KEY
```

The KAAS job must already be completed.

### 2. Original protein FASTA file

The original FASTA file submitted to KAAS.

Example:

```text
/mnt/d/interpro/combind fasta.faa
```

The FASTA identifiers are matched against the identifiers contained in the KAAS `query.ko` result.

---

## Output

The application generates a results directory containing the processed KAAS and KEGG annotations.

Typical outputs include:

```text
results/
├── query.ko
├── KAAS_Protein_KO.xlsx
├── KEGG_Pathway_Annotation.xlsx
├── KO_Summary.xlsx
├── pathway_summary.xlsx
└── logs/
```

The exact files depend on the selected workflow and processing stage.

The main annotation table contains:

| Column      | Description                                |
| ----------- | ------------------------------------------ |
| Protein_ID  | Protein identifier from the original FASTA |
| KO          | KEGG Orthology identifier                  |
| Enzyme      | KEGG enzyme/function information           |
| EC          | EC number where available                  |
| PathwayID   | KEGG pathway identifier                    |
| PathwayName | KEGG pathway name                          |

A protein associated with multiple pathways may occur in multiple rows.

---

# Installation

## Requirements

The application is designed to run locally under Linux/Ubuntu or WSL Ubuntu.

Required software:

* Python 3
* pip
* Streamlit
* pandas
* openpyxl
* requests

The required Python packages are listed in:

```text
requirements.txt
```

---

## Recommended installation using Conda

Create an environment:

```bash
conda create -n kaas_env python=3.12 -y
```

Activate it:

```bash
conda activate kaas_env
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Verify installation:

```bash
python -c "import streamlit,pandas,openpyxl,requests; print('ALL OK')"
```

Expected:

```text
ALL OK
```

---

# Method 1 — Command-line pipeline

The command-line workflow is recommended for large datasets.

Run:

```bash
python kaas_kegg_pipeline.py \
  --kaas-url "YOUR_KAAS_RESULT_URL" \
  --fasta "/path/to/proteins.faa" \
  --output "/path/to/results" \
  --batch-size 10 \
  --delay 1
```

Example:

```bash
python kaas_kegg_pipeline.py \
  --kaas-url "https://www.genome.jp/kaas-bin/kaas_main?mode=user&id=YOUR_JOB_ID&key=YOUR_JOB_KEY" \
  --fasta "/mnt/d/interpro/combind fasta.faa" \
  --output "/home/USER/Fusarium-comparative-genomics/10_KEGG/KAAS_KEGG_Analyzer/results" \
  --batch-size 10 \
  --delay 1
```

Replace:

```text
YOUR_JOB_ID
YOUR_JOB_KEY
/path/to/proteins.faa
/path/to/results
```

with the appropriate values.

---

# Method 2 — Local Streamlit application

The Streamlit application provides a local browser interface while all processing occurs on the Ubuntu/WSL system.

Start the application:

```bash
./run_app.sh
```

or:

```bash
streamlit run app.py
```

The application will provide a local address similar to:

```text
http://localhost:8502
```

Open this address in a web browser on the same computer.

The application does not require uploading the FASTA or KAAS result to an external application server. The analysis is performed locally.

---

# Large dataset processing

This workflow is intended for large proteomes.

For example, a KAAS result containing:

```text
424,015 protein IDs
```

can be processed without attempting to display the complete KAAS result page in the browser.

The workflow directly retrieves the KAAS `query.ko` file and processes it as a text file.

This avoids the problem of loading hundreds of thousands of identifiers into the KAAS HTML webpage.

---

# FASTA–KAAS validation

Before KEGG annotation, the workflow compares the original FASTA identifiers with the identifiers contained in the KAAS result.

The validation reports:

```text
FASTA IDs
KAAS IDs
Matching IDs
FASTA IDs missing in KAAS
KAAS IDs not in FASTA
Proteins with KO
Proteins without KO
Unique KO IDs
```

For a valid analysis, the FASTA and KAAS identifiers should correspond appropriately.

---

# KO annotation

The KAAS `query.ko` file is parsed to create a Protein → KO mapping.

Example:

```text
Protein_ID              KO
Fgram_0343|g9.t1        K09967
```

Proteins without a KO assignment are retained and reported separately.

---

# KEGG annotation

Unique KO identifiers are processed against the KEGG database.

The workflow retrieves available information including:

* KO identifier
* functional/enzyme name
* EC number
* KEGG pathway identifier
* KEGG pathway name

Multiple proteins can share the same KO identifier.

A single KO can also be associated with multiple pathways.

---

# Caching

KEGG annotation results are cached locally to avoid unnecessarily repeating requests during reruns.

This is particularly important for large datasets containing thousands of unique KO identifiers.

If the analysis is interrupted, previously processed KO information can be reused from the cache.

---

# Recommended directory structure

```text
KAAS_KEGG_Analyzer/
│
├── README.md
├── app.py
├── kaas_kegg_pipeline.py
├── run_app.sh
├── requirements.txt
└── results/
    └── .gitkeep
```

Generated results should generally not be committed to the GitHub repository.

---

# Reproducibility

For reproducibility, record:

1. KAAS job ID
2. KAAS result URL
3. Original FASTA filename
4. Number of FASTA sequences
5. Number of KAAS entries
6. Number of proteins assigned to KOs
7. Number of unique KO identifiers
8. KEGG processing date
9. Software/environment versions
10. Output files used for downstream analysis

---

# Data privacy and credentials

Do not commit private KAAS job URLs, API credentials, personal access information, or large unpublished datasets to a public repository.

For published analyses, provide the relevant public accession information and describe the computational workflow rather than committing private job credentials.

---

# Citation

If this workflow contributes to a publication, cite the associated repository and the underlying KAAS/KEGG resources according to their current citation requirements.

---

# License

This software is distributed under the license specified in the root repository.
