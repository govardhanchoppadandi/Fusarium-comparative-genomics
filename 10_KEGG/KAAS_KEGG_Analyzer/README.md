# KAAS → KEGG Pathway Analyzer

Automated KAAS-based KO annotation and KEGG pathway analysis
for large fungal proteomes.

## Overview

This workflow was developed for large-scale functional annotation
of Fusarium protein datasets using the KEGG Automatic Annotation
Server (KAAS).

The application accepts:

1. A completed KAAS result URL
2. The original protein FASTA file

It automatically:

- downloads the KAAS `query.ko` result
- extracts protein IDs
- extracts KO assignments
- reads the original FASTA IDs
- performs FASTA–KAAS ID matching
- identifies proteins with and without KO assignments
- determines unique KO IDs
- retrieves KEGG KO information
- retrieves EC numbers
- retrieves KEGG pathway annotations
- maps pathway annotations back to proteins
- generates summary tables
- exports the complete results to Excel
- maintains a KEGG cache for reproducibility and resumable analysis

## Workflow

FASTA
↓
KAAS
↓
query.ko
↓
Protein ID → KO ID
↓
FASTA–KAAS ID validation
↓
Unique KO IDs
↓
KEGG REST API
↓
KO / Enzyme / EC / Pathway
↓
Protein → KO → Pathway
↓
Excel

## Directory

```text
KAAS_KEGG_Analyzer/
├── kaas_kegg_pipeline.py
├── run_kaas_kegg.sh
├── requirements.txt
└── README.md
