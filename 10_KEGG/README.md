# KEGG Functional Annotation

This directory contains reproducible KEGG and KO annotation workflows used for comparative genomic analysis of wheat-infecting *Fusarium* species.

## KAAS → KEGG Pathway Analyzer

The `KAAS_KEGG_Analyzer` is a local Python/Streamlit application for converting completed KEGG Automatic Annotation Server (KAAS) results into structured KO, EC, KEGG pathway, and protein-level annotation tables.

The workflow is designed for fungal protein datasets and can be used for large-scale comparative genomic analyses.

### Main functions

The analyzer performs:

1. Retrieval of a completed KAAS `query.ko` result
2. Parsing of KAAS protein-to-KO assignments
3. Identification and validation of protein IDs against the original FASTA
4. Identification of proteins with and without KO assignments
5. Extraction of unique KO identifiers
6. Retrieval of KO information from KEGG
7. Retrieval of EC/enzyme annotations
8. Retrieval of KEGG pathway annotations
9. Mapping of KO and pathway information back to proteins
10. Generation of summary tables
11. Export of results to an Excel workbook
12. KEGG response caching for efficient and resumable analysis

## Directory structure

```text
10_KEGG/
├── README.md
│
├── KAAS_KEGG_Analyzer/
│   ├── README.md
│   ├── app.py
│   ├── kaas_kegg_pipeline.py
│   ├── requirements.txt
│   ├── run_app.sh
│   ├── run_kaas_kegg.sh
│   │
│   └── src/
│       ├── __init__.py
│       ├── fasta.py
│       ├── kaas.py
│       ├── kegg.py
│       └── excel.py
│
└── scripts/
    ├── KO_annotation/
    ├── pathway_annotation/
    └── summary/
```

## Reproducibility

User-specific input files, KAAS result URLs, downloaded KAAS results, KEGG cache files, and generated Excel outputs are not included in the repository.

Users should provide their own protein FASTA file and completed KAAS result URL when running the analyzer.

For detailed installation and usage instructions, see:

`KAAS_KEGG_Analyzer/README.md`

## External resources

The workflow uses the KEGG database and associated KEGG web services. Users should follow the applicable KEGG terms of use, access policies, and request-rate limitations.

## Citation

If this workflow contributes to published research, please cite this repository together with the relevant KAAS and KEGG resources.
