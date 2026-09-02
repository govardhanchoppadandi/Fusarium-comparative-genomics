KAAS → KEGG Pathway Analyzer

START
-----
From the project directory:
    ./run_app.sh

Then open the Streamlit page shown in the terminal.

INPUTS
------
Choose ONE:
1. KAAS result URL
2. Local query.ko / .txt / .tsv / .csv / .xlsx / .xls file

FASTA is optional and is used only for protein-ID validation.

Excel input should contain a protein identifier column and a KO column.
The analyzer automatically recognizes common names such as:
Protein_ID, Protein ID, Protein, Sequence_ID, Gene_ID, ID, Query
and
KO, KO_ID, KEGG_KO, KEGG KO, K number, KO IDs.

OUTPUT
------
The app creates KAAS_KEGG_Results.xlsx containing:
- All_Protein_KO
- KO_Annotation
- Pathway_Annotation
- KO_Summary
- Pathway_Summary
- EC_Summary
- Summary

It also writes TSV files and a persistent KEGG cache so previously annotated KOs
are not repeatedly queried.

WINDOWS PATHS
-------------
Windows paths such as D:\interpro\results.xlsx are accepted by the app when it
runs inside WSL and are converted automatically to /mnt/d/interpro/results.xlsx.

CODE VISIBILITY
---------------
Normal users do not need to open or edit the Python files. The launcher starts
the application directly. This is intended as an internal research application;
if the application directory itself is given to another person, Python source
files can still technically be inspected. True source-code protection requires
running the software on a server or distributing a separately packaged binary.
