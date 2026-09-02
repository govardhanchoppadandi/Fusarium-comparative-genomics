# ARI Wheat Pathology Functional Annotation Suite

Functional annotation pipeline for fungal protein FASTA sequences.

Developed at:

Agharkar Research Institute, Pune
Wheat Pathology Laboratory

Developed by:
- Dr. Sudhir Navathe
- Govardhan Choppadandi

---

## 1. Overview

The ARI Wheat Pathology Functional Annotation Suite performs functional annotation of fungal protein sequences using:

- FASTA quality control
- BLASTP against UniProtKB/Swiss-Prot
- InterProScan
- InterPro-derived GO annotations
- GO ontology processing
- GO-Slim classification
- Functional annotation table generation
- Excel output

The software is provided as source code.

Large external databases and software resources are NOT included in this GitHub repository.

Users must install/download the required resources locally and provide their paths in:

    config/resources.local.yaml

---

# 2. System requirements

Recommended environment:

- Ubuntu 22.04/24.04
- WSL2 Ubuntu is supported
- Internet connection
- Python 3
- Git
- BLAST+
- InterProScan
- Docker
- Sufficient disk space for databases
- Sufficient RAM/CPU for InterProScan and BLAST

For large fungal proteomes, SSD storage and adequate RAM are strongly recommended.

---

# 3. Clone the repository

Clone the main repository:

    git clone https://github.com/govardhanchoppadandi/Fusarium-comparative-genomics.git

Enter the annotation folder:

    cd Fusarium-comparative-genomics/14_ARI_Wheat_Pathology_Functional_Annotation

Check the files:

    find . -maxdepth 3 -type f | sort

You should see:

    app/pipeline.py
    config/config.yaml
    config/resources.local.example.yaml
    fusarium_annotator.sh
    install.sh
    modules/blast_annotation.py
    modules/check_resources.py
    modules/excel_output.py
    modules/fasta_qc.py
    modules/go_annotation.py
    modules/goslim.py
    modules/project_output.py
    README.md

---

# 4. Install Python dependencies

Run:

    chmod +x install.sh
    ./install.sh

The installer creates/uses the required Python environment and checks Python dependencies.

---

# 5. Required external resources

The pipeline requires the following resources.

## A. BLAST+

BLASTP is required for protein similarity searches.

Check:

    which blastp
    blastp -version

Example:

    /usr/bin/blastp

If BLAST+ is not installed, install it through the Ubuntu package manager:

    sudo apt update
    sudo apt install -y ncbi-blast+

Then verify:

    blastp -version

---

# 6. UniProtKB/Swiss-Prot BLAST database

The pipeline performs local BLASTP searches against UniProtKB/Swiss-Prot.

A local BLAST database is required.

The configured database path must point to the BLAST database prefix, for example:

    /path/to/swissprot/swissprot

The database should contain files such as:

    swissprot.pin
    swissprot.phr
    swissprot.psq

Check the database:

    ls -lh /path/to/swissprot/

The exact current UniProt download procedure may change. Use the official UniProt download resources to obtain the reviewed Swiss-Prot protein dataset and prepare the local BLAST database.

After obtaining the Swiss-Prot FASTA, create the BLAST database using:

    makeblastdb \
      -in swissprot.fasta \
      -dbtype prot \
      -parse_seqids \
      -out swissprot

Then verify:

    ls -lh swissprot.*

---

# 7. Gene Ontology ontology

Download the current:

    go-basic.obo

The recommended GO basic ontology is suitable for most GO-based annotation tools.

Place it somewhere accessible, for example:

    ~/databases/go/go-basic.obo

Verify:

    ls -lh ~/databases/go/go-basic.obo

---

# 8. GO-Slim ontology

Download:

    goslim_generic.obo

Place it somewhere accessible, for example:

    ~/databases/go/goslim_generic.obo

Verify:

    ls -lh ~/databases/go/goslim_generic.obo

---

# 9. InterPro2GO

Download the current InterPro2GO mapping file.

Place it somewhere accessible, for example:

    ~/databases/go/interpro2go

Verify:

    ls -lh ~/databases/go/interpro2go

---

# 10. InterProScan

InterProScan is required for protein domain/family/function analysis.

This pipeline expects a local InterProScan installation/data resource.

The configuration supports:

    profile: "docker"

The InterProScan software and its databases are NOT included in this GitHub repository because they are large external resources.

Install/configure InterProScan according to the current InterProScan documentation/repository.

The project configuration expects an InterProScan data directory such as:

    ~/databases/interproscan6_data

The exact location depends on how InterProScan is installed.

Verify the installation/data directory before running the pipeline.

---

# 11. Create local resource configuration

IMPORTANT:

Do NOT edit or upload the example file.

Create your local configuration:

    cp config/resources.local.example.yaml config/resources.local.yaml

Open it:

    nano config/resources.local.yaml

Replace the example paths with the actual paths on your computer.

Example:

    resources:
      go_obo: "/home/USERNAME/databases/go/go-basic.obo"
      goslim_obo: "/home/USERNAME/databases/go/goslim_generic.obo"
      interpro2go: "/home/USERNAME/databases/go/interpro2go"
      interproscan_datadir: "/home/USERNAME/databases/interproscan6_data"
      blast_database: "/home/USERNAME/databases/swissprot/swissprot"

IMPORTANT:

Do not copy these example paths blindly.

Use the real paths on your system.

---

# 12. Why resources.local.yaml is not included

The file:

    config/resources.local.yaml

contains machine-specific paths.

For example:

    /home/username/...
    /mnt/d/...
    /data/...

These paths are different for every user.

Therefore the repository contains:

    config/resources.local.example.yaml

but users create:

    config/resources.local.yaml

locally.

The local configuration file should NOT be committed to GitHub.

---

# 13. Test all resources before running

From the annotation directory run:

    ./fusarium_annotator.sh

The program first performs a resource check.

The resource check should show:

    [OK] GO ontology
    [OK] GO-Slim ontology
    [OK] InterPro2GO
    [OK] blastp
    [OK] InterProScan
    [OK] BLAST database

If any required resource is shown as:

    [MISSING]

stop and correct the corresponding path in:

    config/resources.local.yaml

Do not proceed until the required resources are available.

---

# 14. Input FASTA

The input must be a protein FASTA file.

Example:

    /mnt/d/interpro/test_fasta.fasta

Check the file:

    ls -lh /mnt/d/interpro/test_fasta.fasta

Count proteins:

    grep -c "^>" /mnt/d/interpro/test_fasta.fasta

Example:

    248

Inspect the first sequences:

    head -20 /mnt/d/interpro/test_fasta.fasta

---

# 15. Running the pipeline

The pipeline uses the FASTA path supplied through the configuration.

Edit:

    config/config.yaml

Set:

    input:
      fasta: "/mnt/d/interpro/test_fasta.fasta"

Set the output directory if required, for example:

    output:
      directory: "/mnt/d/interpro/Fusarium_annotation_results"

The exact output path may be changed according to the user's system.

Then run:

    ./fusarium_annotator.sh

---

# 16. FASTA quality control

The pipeline validates the input FASTA before annotation.

It reports:

- Number of protein sequences
- Total amino acids
- Duplicate IDs
- Sequence ID validity
- Basic FASTA quality information

Example:

    Protein sequences : 248
    Total aa          : 120628
    Duplicate IDs     : 0

If FASTA validation fails, correct the input FASTA before continuing.

---

# 17. BLASTP analysis

The pipeline runs BLASTP against the configured local UniProtKB/Swiss-Prot database.

Default settings:

    evalue: 1.0e-5
    max_target_seqs: 5
    max_hsps: 1

The BLAST database path must be valid.

For example:

    resources:
      blast_database: "/home/USERNAME/databases/swissprot/swissprot"

The path refers to the database prefix, not to a single .pin file.

The following files should exist:

    swissprot.pin
    swissprot.phr
    swissprot.psq

---

# 18. InterProScan analysis

InterProScan analyses the protein sequences for conserved domains, families and functional signatures.

The pipeline requests:

    GO terms
    pathways
    TSV output

InterProScan requires its own software/data resources.

These resources are intentionally not stored in this GitHub repository.

---

# 19. GO annotation

GO information is generated/processed using:

- GO ontology
- InterPro2GO mappings
- InterProScan-derived GO information

The pipeline can process:

- Molecular Function (MF)
- Biological Process (BP)
- Cellular Component (CC)

---

# 20. GO-Slim

GO-Slim provides a higher-level functional classification.

The pipeline uses:

    goslim_generic.obo

GO-Slim results should be interpreted as broad functional categories rather than detailed protein-specific functional assignments.

---

# 21. Output

The pipeline creates a project output directory.

Typical outputs include:

    raw/
    intermediate/
    report/
    results/

The final Excel workbook is:

    Fusarium_Protein_Annotation.xlsx

The BLAST output is:

    BLAST_SwissProt.tsv

The exact output location is controlled by:

    output.directory

---

# 22. Example complete workflow

Example FASTA:

    /mnt/d/interpro/test_fasta.fasta

Enter the project:

    cd ~/Fusarium-comparative-genomics/14_ARI_Wheat_Pathology_Functional_Annotation

Create local configuration:

    cp config/resources.local.example.yaml config/resources.local.yaml

Edit:

    nano config/resources.local.yaml

Check BLAST:

    which blastp
    blastp -version

Check FASTA:

    ls -lh /mnt/d/interpro/test_fasta.fasta
    grep -c "^>" /mnt/d/interpro/test_fasta.fasta

Run:

    ./fusarium_annotator.sh

---

# 23. Important: GitHub does not contain the databases

This repository contains the pipeline software.

It does NOT contain:

- InterProScan databases
- GO ontology files
- GO-Slim ontology
- InterPro2GO
- UniProtKB/Swiss-Prot BLAST database
- User FASTA files
- Analysis results

These files can be extremely large and/or are external resources.

Users must obtain and configure them locally.

---

# 24. Recommended project structure after installation

A recommended local setup is:

    ~/databases/
    ├── go/
    │   ├── go-basic.obo
    │   ├── goslim_generic.obo
    │   └── interpro2go
    │
    ├── swissprot/
    │   ├── swissprot.pin
    │   ├── swissprot.phr
    │   └── swissprot.psq
    │
    └── interproscan6_data/

The GitHub project remains separate:

    ~/Fusarium-comparative-genomics/
    └── 14_ARI_Wheat_Pathology_Functional_Annotation/

---

# 25. Troubleshooting

## Error: BLAST database not found

Example:

    FileNotFoundError: BLAST protein database not found: .pin

This means the configured BLAST database path is empty or incorrect.

Check:

    cat config/resources.local.yaml

Then verify:

    ls -lh /path/to/swissprot/

Make sure:

    swissprot.pin
    swissprot.phr
    swissprot.psq

exist.

---

## Error: GO ontology missing

Check:

    ls -lh /path/to/go-basic.obo

Then update:

    config/resources.local.yaml

---

## Error: GO-Slim ontology missing

Check:

    ls -lh /path/to/goslim_generic.obo

Then update:

    config/resources.local.yaml

---

## Error: InterPro2GO missing

Check:

    ls -lh /path/to/interpro2go

Then update:

    config/resources.local.yaml

---

## Error: InterProScan missing

Check the InterProScan installation and data directory.

Then update:

    interproscan_datadir:

with the correct local path.

---

# 26. Do not upload local resources

Never commit:

    config/resources.local.yaml

    config/.runtime_config.yaml

    .venv/

    databases/

    results/

    *.pin
    *.phr
    *.psq

    *.pyc
    __pycache__/

User FASTA files and analysis results should also remain outside the source repository unless specifically intended for publication.

---

# 27. Reproducibility

For reproducible analyses, record:

- Pipeline Git commit/version
- Input FASTA filename
- Number of proteins
- GO release/version
- GO-Slim release/version
- InterProScan version
- InterProScan database version
- UniProt/Swiss-Prot release
- BLAST+ version
- BLAST parameters
- Date of analysis
- CPU/thread settings

---

# 28. Citation

Citation:

To be updated after publication.

---

# 29. Authors

Dr. Sudhir Navathe
Govardhan Choppadandi

Agharkar Research Institute, Pune
Wheat Pathology Laboratory

