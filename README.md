# ARI Wheat Pathology Functional Annotation Suite

Functional annotation of fungal protein sequences.

**Agharkar Research Institute, Pune**
**Wheat Pathology Laboratory**

## Developed by

**Dr. Sudhir Navathe**
**Govardhan Choppadandi**

## Citation

To be updated after publication.

## Input

A protein FASTA file is required.

Example:

    ./fusarium_annotator.sh /path/to/proteins.faa

## Pipeline

1. FASTA quality control
2. BLASTP against UniProtKB/Swiss-Prot
3. InterProScan 6
4. InterPro-to-GO annotation
5. GO annotation
6. GO-Slim annotation
7. Excel report generation
8. Raw result generation
9. Analysis logging

## Output

The application generates BLAST, InterProScan, GO, GO-Slim, raw results, logs and an Excel workbook.

## Required resources

InterProScan 6 databases, UniProtKB/Swiss-Prot, GO, GO-Slim and InterPro2GO resources are required locally and are not committed to GitHub because of their large size.

## Installation

    ./install.sh

## Running

    ./fusarium_annotator.sh /path/to/proteins.faa

## Developers

**Dr. Sudhir Navathe**

**Govardhan Choppadandi**

Wheat Pathology Laboratory

Agharkar Research Institute, Pune

## Citation

**To be updated after publication.**
