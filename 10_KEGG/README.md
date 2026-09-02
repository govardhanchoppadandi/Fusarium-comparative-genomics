# KEGG Analysis

This directory contains KEGG/KO annotation workflows used in the comparative genomic analysis of wheat-infecting *Fusarium* species.

## Modules

### KAAS → KEGG Pathway Analyzer

`KAAS_KEGG_Analyzer/` provides a local Python/Streamlit workflow for processing completed KEGG Automatic Annotation Server (KAAS) results.

The application integrates:

1. Completed KAAS result retrieval
2. KAAS `query.ko` parsing
3. Original protein FASTA identification
4. Protein-to-KO matching
5. KO-to-EC annotation
6. KEGG pathway annotation
7. Pathway-level summaries
8. Excel workbook generation

The workflow is designed to convert a completed KAAS annotation result and the corresponding original protein FASTA file into a structured Excel report suitable for downstream comparative genomic analysis.

## Directory

```text
10_KEGG/
├── README.md
├── KAAS_KEGG_Analyzer/
│   ├── README.md
│   ├── app.py
│   ├── kaas_kegg_pipeline.py
│   ├── requirements.txt
│   ├── run_app.sh
│   ├── run_kaas_kegg.sh
│   └── src/
│       ├── __init__.py
│       ├── fasta.py
│       ├── kaas.py
│       ├── kegg.py
│       └── excel.py
└── scripts/
    ├── KO_annotation/
    ├── pathway_annotation/
    └── summary/
```

## KAAS → KEGG Analyzer

The analyzer accepts:

* A completed KAAS result URL
* The original protein FASTA file
* An output directory
* KEGG API batch size
* Delay between KEGG requests

### Recommended environment

The application is intended to run locally under Ubuntu/WSL using Python 3.12 and a dedicated Conda environment.

### Installation

```bash
conda create -n kaas_env python=3.12
conda activate kaas_env
```

Clone or download the repository and enter:

```bash
cd 10_KEGG/KAAS_KEGG_Analyzer
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### Run the Streamlit application

```bash
chmod +x run_app.sh
./run_app.sh
```

The application will start locally. Open the displayed local address in a web browser, for example:

```text
http://localhost:8501
```

The exact port may change if another Streamlit application is already running.

### Command-line workflow

For non-interactive execution:

```bash
chmod +x run_kaas_kegg.sh
./run_kaas_kegg.sh
```

The workflow requires a valid completed KAAS result URL and the corresponding original protein FASTA file.

### Input requirements

The FASTA identifiers should correspond to the protein sequences submitted to KAAS. The completed KAAS result must be accessible using the supplied KAAS result URL and any required access information.

Example FASTA path under Ubuntu/WSL:

```text
/mnt/d/interpro/combind fasta.faa
```

Example output directory:

```text
KAAS_KEGG_Results
```

### Output

The workflow generates structured annotation tables and an Excel workbook containing the KAAS/KO and KEGG pathway analysis.

Generated files should be stored locally and are intentionally excluded from the GitHub repository.

### Reproducibility

The repository contains the application source code, supporting modules, installation requirements, and execution scripts required to reproduce the analysis. User-specific KAAS URLs, protein FASTA files, downloaded KEGG data, caches, and generated result files are not included in the repository.

### External resources

The workflow uses the KEGG database and KEGG-related web services. Users should comply with the applicable KEGG usage conditions and rate limits when running the analysis.

## Citation

If this workflow is used in a publication, please cite this repository and the relevant KAAS/KEGG resources.
