# KEGG Pathway Annotation

This module documents the KEGG pathway annotation workflow used in the *Fusarium* comparative genomics analysis.

The workflow uses **Biopython KEGG REST API** calls to retrieve functional information for KO (KEGG Orthology) identifiers assigned by KAAS.

## Directory structure

```text
10_KEGG/
├── README.md
└── scripts/
    ├── KO_annotation/
    ├── pathway_annotation/
    └── summary/
```

---

# 1. Purpose

The workflow takes a KAAS GeneID → KO mapping file and retrieves KEGG information for the identified KO terms.

The pipeline:

1. Reads GeneID → KO assignments from KAAS.
2. Removes the `ko:` prefix when present.
3. Identifies unique KO IDs.
4. Retrieves KEGG KO information using Biopython.
5. Extracts:
   - Enzyme information
   - EC numbers
   - KEGG pathway IDs
   - KEGG pathway names
6. Caches downloaded KO information.
7. Reuses cached records during reruns.
8. Generates a final Excel annotation table.

---

# 2. Software requirements

Run the workflow in Python.

Required packages:

- Python 3
- Biopython
- pandas
- openpyxl

Install the required packages:

```bash
pip install biopython pandas openpyxl
```

If using a Conda environment:

```bash
conda install -c conda-forge biopython pandas openpyxl
```

---

# 3. Script

The main script is:

```text
kegg_pathway_annotation.py
```

Recommended repository location:

```text
10_KEGG/scripts/pathway_annotation/kegg_pathway_annotation.py
```

---

# 4. Input

The input is a KAAS KO mapping file:

```text
kaas list.txt
```

Expected format:

```text
GeneID    KO
gene_001  ko:K00844
gene_002  ko:K00001
```

The file should contain two tab-separated columns:

```text
GeneID <TAB> KO
```

The pipeline automatically removes the `ko:` prefix.

For example:

```text
ko:K00844
```

becomes:

```text
K00844
```

---

# 5. Configure file paths

Edit the following variables in the Python script:

```python
INPUT_FILE = r"E:\1 Manuscript Fusarium genome\SEQ ANALYSIS\tnw1 seq analysis\KAAS\kaas list.txt"

OUTPUT_FILE = r"E:\1 Manuscript Fusarium genome\SEQ ANALYSIS\tnw1 seq analysis\KAAS\Biopython_KEGG_Pathways.xlsx"

CACHE_FILE = r"E:\1 Manuscript Fusarium genome\SEQ ANALYSIS\tnw1 seq analysis\KAAS\kegg_cache.pkl"
```

Change these paths if the files are stored elsewhere.

---

# 6. KEGG information retrieved

For each KO identifier, the script retrieves information from the KEGG KO entry.

The final table contains:

| Column | Description |
|---|---|
| `GeneID` | Gene identifier from the KAAS file |
| `KO` | KEGG Orthology identifier |
| `Enzyme` | Enzyme/name information from KEGG |
| `EC` | EC number information |
| `PathwayID` | KEGG pathway identifier |
| `PathwayName` | KEGG pathway name |

A gene associated with multiple pathways is represented in multiple rows.

---

# 7. KEGG REST API

The script uses Biopython's KEGG REST interface:

```python
from Bio.KEGG import REST
```

For each KO, the workflow requests:

```text
ko:Kxxxxx
```

from KEGG.

Because the workflow accesses the KEGG server repeatedly, the script includes a delay between new requests.

---

# 8. Cache system

The pipeline creates:

```text
kegg_cache.pkl
```

The cache stores previously retrieved KO information.

This prevents already processed KO IDs from being downloaded again.

During a rerun, the terminal may show:

```text
[1/XXXX] K00844 → Cached
```

instead of making another KEGG request.

This is particularly useful when the KAAS file contains many KO identifiers or when the analysis needs to be restarted.

---

# 9. Running the analysis

Navigate to the script directory or provide the full script path.

Example:

```bash
python kegg_pathway_annotation.py
```

The pipeline will report progress such as:

```text
Loading KO file...

Total unique KO IDs = XXXX

Loading existing cache...

Fetching KEGG annotations...

[1/XXXX] K00844 → Cached
[2/XXXX] Fetching K00001... OK
```

---

# 10. Cache saving

The cache is periodically saved during processing.

The script saves the cache every 50 newly processed KO records and also saves it again after the complete analysis.

Therefore, if the process is interrupted, previously completed KO records can be reused.

---

# 11. Expected output

The main output is:

```text
Biopython_KEGG_Pathways.xlsx
```

The cache file is:

```text
kegg_cache.pkl
```

Expected output:

```text
KEGG/
├── Biopython_KEGG_Pathways.xlsx
└── kegg_cache.pkl
```

The Excel file contains the final GeneID–KO–enzyme–EC–pathway annotation table.

---

# 12. Example final table

```text
GeneID    KO       Enzyme       EC       PathwayID    PathwayName
gene_001  K00844   ...          ...      mapXXXXX     ...
gene_002  K00001   ...          ...      mapXXXXX     ...
```

If one KO is associated with multiple pathways, the same GeneID/KO can occur in multiple rows.

---

# 13. Recommended repository organization

Keep the executable Python script under:

```text
10_KEGG/scripts/pathway_annotation/
```

Use:

```text
10_KEGG/scripts/KO_annotation/
```

for future scripts that specifically perform KO assignment or KO preprocessing.

Use:

```text
10_KEGG/scripts/summary/
```

for downstream scripts that summarize pathway counts, KO distributions, or generate figures/tables.

---

# 14. Suggested workflow

```text
KAAS
  │
  ▼
GeneID → KO mapping
  │
  ▼
kaas list.txt
  │
  ▼
Biopython KEGG REST
  │
  ├── Enzyme information
  ├── EC numbers
  └── Pathway information
  │
  ▼
Cached KO records
  │
  ▼
Biopython_KEGG_Pathways.xlsx
  │
  ▼
Downstream pathway summary
```

---

# 15. Reproducibility

Record the following information for the final analysis:

- Python version
- Biopython version
- pandas version
- openpyxl version
- KAAS input file
- KEGG annotation date
- Script name
- Output file name

Useful commands:

```bash
python --version
```

```bash
python -c "import Bio, pandas, openpyxl; print('Biopython:', Bio.__version__); print('pandas:', pandas.__version__); print('openpyxl:', openpyxl.__version__)"
```

---

# 16. Important considerations

## KEGG access

This workflow depends on KEGG REST access. Internet connectivity is required when a KO is not already present in the cache.

## Do not delete the cache unnecessarily

If the analysis is rerun, retaining:

```text
kegg_cache.pkl
```

avoids unnecessary repeated requests.

## Large KO datasets

For large KAAS datasets, the analysis can take considerable time because new KO records are requested individually with a delay between requests.

## Raw/intermediate data

Do not commit large KAAS datasets, cache files, or large generated Excel files to GitHub unless they are intentionally included as project data.

---

# 17. Final output for manuscript analysis

The primary manuscript-ready annotation table is:

```text
Biopython_KEGG_Pathways.xlsx
```

This table can subsequently be used to calculate:

- Number of genes assigned to each KO
- Number of genes assigned to each pathway
- Pathway-level gene distributions
- KO-level summaries
- Comparative pathway statistics between *Fusarium* genomes

Downstream summary and visualization scripts should be stored under:

```text
10_KEGG/scripts/summary/
```

---

# 18. Module summary

```text
10_KEGG/
├── README.md
└── scripts/
    ├── KO_annotation/
    ├── pathway_annotation/
    │   └── kegg_pathway_annotation.py
    └── summary/
```

This module forms the KEGG functional annotation component of the **Fusarium Comparative Genomics** workflow.
