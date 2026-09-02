# ARI Wheat Pathology Functional Annotation Suite

**Functional annotation pipeline for fungal protein FASTA sequences**

Developed by:

**Dr. Sudhir Navathe** ,
**Govardhan Choppadandi**

Agharkar Research Institute, Pune
Wheat Pathology Laboratory

---

## 1. Overview

The ARI Wheat Pathology Functional Annotation Suite is a reproducible command-line workflow for functional annotation of fungal protein sequences.

The pipeline performs:

1. FASTA quality control
2. InterProScan-based protein functional annotation
3. InterPro/GO annotation
4. GO-Slim classification
5. BLASTP similarity searches against UniProtKB/Swiss-Prot
6. Integrated Excel output
7. Project-organized raw and processed results

The pipeline is designed primarily for fungal/Fusarium protein FASTA datasets but can be used with other fungal protein datasets.

---

# 2. Important: External resources are required

The GitHub repository contains the **pipeline software and configuration templates**.

It does **not** contain the large external biological databases.

Before running the pipeline, the user must install/download:

### Required software

* Ubuntu/Linux or WSL2 Ubuntu
* Python 3
* Nextflow
* Docker or another supported container runtime
* BLAST+ command-line tools

### Required biological resources

* InterProScan 6 data
* Gene Ontology (`go-basic.obo`)
* GO-Slim (`goslim_generic.obo`)
* InterPro2GO mapping
* UniProtKB/Swiss-Prot BLAST protein database

The required databases can be large. **Do not place these databases inside the GitHub repository.**

---

# 3. System requirements

Recommended:

* Linux or WSL2 Ubuntu
* Internet connection during software/database installation
* Sufficient disk space for InterProScan data and Swiss-Prot
* At least 4 CPU threads recommended
* Additional RAM/storage may be required for large fungal proteomes

For large protein datasets, use a workstation/server with more CPU, RAM and storage than the minimum requirements.

---

# 4. Clone the repository

Clone the complete comparative-genomics repository:

```bash
cd ~
git clone https://github.com/govardhanchoppadandi/Fusarium-comparative-genomics.git
```

Enter the functional annotation directory:

```bash
cd ~/Fusarium-comparative-genomics/14_ARI_Wheat_Pathology_Functional_Annotation
```

Check the files:

```bash
find . -maxdepth 3 -type f | sort
```

You should see:

```text
README.md
.gitignore
install.sh
fusarium_annotator.sh
app/pipeline.py
config/config.yaml
config/resources.local.example.yaml
modules/blast_annotation.py
modules/check_resources.py
modules/excel_output.py
modules/fasta_qc.py
modules/go_annotation.py
modules/goslim.py
modules/project_output.py
```

---

# 5. Install Python dependencies

Run:

```bash
chmod +x install.sh
./install.sh
```

The installation script checks/installs the Python requirements used by the pipeline.

---

# 6. Install BLAST+

BLAST+ is required for the local Swiss-Prot similarity search.

Check whether BLAST+ is already installed:

```bash
which blastp
blastp -version
```

For Ubuntu, BLAST+ can be installed through the Ubuntu/NCBI-supported installation route.

After installation, verify:

```bash
which blastp
blastp -version
```

Expected:

```text
/usr/bin/blastp
blastp: ...
```

NCBI provides BLAST+ packages for Linux and other platforms through its official BLAST distribution.
See the NCBI BLAST installation documentation.

---

# 7. Download the UniProtKB/Swiss-Prot database

The pipeline uses a **local BLAST database**.

You must download the reviewed UniProtKB/Swiss-Prot protein FASTA and create a BLAST database from it.

Create a dedicated directory outside the Git repository:

```bash
mkdir -p ~/databases/swissprot
cd ~/databases/swissprot
```

Download the current reviewed Swiss-Prot FASTA from UniProt.

After downloading the FASTA, create the BLAST database using:

```bash
makeblastdb \
  -in uniprot_sprot.fasta \
  -dbtype prot \
  -parse_seqids \
  -out swissprot
```

Verify:

```bash
ls -lh swissprot.*
```

You should have files similar to:

```text
swissprot.pin
swissprot.psq
swissprot.phr
```

The configuration path must point to the **database prefix**:

```text
/home/YOUR_USERNAME/databases/swissprot/swissprot
```

NOT:

```text
swissprot.pin
```

and NOT merely the FASTA file.

---

# 8. Install InterProScan 6

InterProScan 6 is required for protein family/domain/function annotation.

The current InterProScan 6 workflow uses:

* Nextflow
* Docker/Podman/Singularity/Apptainer
* InterProScan workflow/data

Install Nextflow according to the official InterProScan 6 requirements.

Verify:

```bash
nextflow -version
```

Install Docker and verify:

```bash
docker --version
```

Test Docker:

```bash
docker run --rm hello-world
```

---

# 9. Download InterProScan 6 data

InterProScan 6 automatically retrieves the required workflow/database data when executed.

Create a dedicated data directory outside the Git repository:

```bash
mkdir -p ~/databases/interproscan6
```

A recommended test is:

```bash
cd ~/databases/interproscan6

nextflow run ebi-pf-team/interproscan6 \
  -r 6.0.1 \
  -profile docker,test \
  --datadir data \
  --interpro latest
```

This downloads the required InterPro/member-database data into the specified data directory.

Verify that the data directory has been populated:

```bash
du -sh ~/databases/interproscan6/data
```

The exact disk usage can change with the InterProScan/data release. Keep sufficient free disk space.

For reproducible research, pin the InterProScan and InterPro data versions rather than always using `latest`.

---

# 10. Download Gene Ontology

The pipeline requires:

```text
go-basic.obo
```

Create a GO directory:

```bash
mkdir -p ~/databases/go
cd ~/databases/go
```

Download the current `go-basic.obo` from the official Gene Ontology download site.

Verify:

```bash
ls -lh go-basic.obo
```

---

# 11. Download GO-Slim

The pipeline also requires:

```text
goslim_generic.obo
```

Download the current Generic GO-Slim OBO file from the official Gene Ontology GO subset resources.

Place it in:

```text
~/databases/go/goslim_generic.obo
```

Verify:

```bash
ls -lh ~/databases/go/goslim_generic.obo
```

---

# 12. Download InterPro2GO

The pipeline uses the InterPro-to-GO mapping:

```text
interpro2go
```

Create:

```bash
mkdir -p ~/databases/go
```

Download the current `interpro2go` mapping from the official InterPro/EBI resource.

Place it at:

```text
~/databases/go/interpro2go
```

Verify:

```bash
ls -lh ~/databases/go/interpro2go
```

---

# 13. Recommended local database layout

A recommended layout is:

```text
/home/YOUR_USERNAME/
├── databases/
│   ├── go/
│   │   ├── go-basic.obo
│   │   ├── goslim_generic.obo
│   │   └── interpro2go
│   │
│   ├── swissprot/
│   │   ├── uniprot_sprot.fasta
│   │   ├── swissprot.pin
│   │   ├── swissprot.psq
│   │   └── swissprot.phr
│   │
│   └── interproscan6/
│       └── data/
│           └── [InterProScan data]
│
└── Fusarium-comparative-genomics/
    └── 14_ARI_Wheat_Pathology_Functional_Annotation/
```

Keep the databases outside GitHub.

---

# 14. Configure the pipeline

Inside the annotation directory:

```bash
cd ~/Fusarium-comparative-genomics/14_ARI_Wheat_Pathology_Functional_Annotation
```

Create the local configuration:

```bash
cp config/resources.local.example.yaml config/resources.local.yaml
```

Edit it:

```bash
nano config/resources.local.yaml
```

Set the paths to your actual local installation.

Example:

```yaml
resources:
  go_obo: "/home/YOUR_USERNAME/databases/go/go-basic.obo"
  goslim_obo: "/home/YOUR_USERNAME/databases/go/goslim_generic.obo"
  interpro2go: "/home/YOUR_USERNAME/databases/go/interpro2go"

  interproscan_datadir: "/home/YOUR_USERNAME/databases/interproscan6/data"

  blast_database: "/home/YOUR_USERNAME/databases/swissprot/swissprot"
```

Replace:

```text
YOUR_USERNAME
```

with your actual Linux username.

For example:

```text
/home/govardhan/databases/go/go-basic.obo
```

Do not copy the example paths literally.

---

# 15. Check that all resources exist

Run:

```bash
test -f config/resources.local.yaml && echo "Local configuration: OK"

test -f /home/YOUR_USERNAME/databases/go/go-basic.obo && echo "GO: OK"

test -f /home/YOUR_USERNAME/databases/go/goslim_generic.obo && echo "GO-Slim: OK"

test -f /home/YOUR_USERNAME/databases/go/interpro2go && echo "InterPro2GO: OK"

test -d /home/YOUR_USERNAME/databases/interproscan6/data && echo "InterProScan data: OK"

test -f /home/YOUR_USERNAME/databases/swissprot/swissprot.pin && echo "Swiss-Prot BLAST database: OK"
```

Also verify BLAST:

```bash
which blastp
blastp -version
```

---

# 16. Prepare the input FASTA

The input must be a protein FASTA file.

Example:

```text
/mnt/d/interpro/test_fasta.fasta
```

Check the FASTA:

```bash
grep -c "^>" /mnt/d/interpro/test_fasta.fasta
```

Inspect the first sequences:

```bash
head -20 /mnt/d/interpro/test_fasta.fasta
```

The FASTA should contain protein sequences such as:

```text
>Fgram_0343|g1.t1
RAARRSFHQGILTALRDDLSDTVEEQERF...
```

---

# 17. Run the annotation pipeline

From:

```bash
cd ~/Fusarium-comparative-genomics/14_ARI_Wheat_Pathology_Functional_Annotation
```

run:

```bash
./fusarium_annotator.sh
```

The launcher will request/use the configured FASTA and local resources according to the pipeline configuration.

The FASTA path must point to the actual input file.

For example:

```text
/mnt/d/interpro/test_fasta.fasta
```

---

# 18. FASTA test dataset

A small test can be performed before analysing a complete proteome.

Example:

```text
/mnt/d/interpro/test_fasta.fasta
```

For the test dataset used during development:

```text
Protein sequences: 248
```

The FASTA should pass the pipeline's FASTA QC before annotation begins.

---

# 19. Pipeline stages

The pipeline performs the following major stages:

```text
INPUT PROTEIN FASTA
        │
        ▼
FASTA QUALITY CONTROL
        │
        ▼
RESOURCE CHECK
        │
        ├───────────────┐
        ▼               ▼
INTERPROSCAN          BLASTP
        │               │
        ▼               ▼
InterPro results     Swiss-Prot hits
        │               │
        ▼               │
GO / GO-Slim           │
        │               │
        └───────┬───────┘
                ▼
        INTEGRATED ANNOTATION
                │
                ▼
             EXCEL
```

---

# 20. Output

The pipeline creates a project-specific results directory.

Typical outputs include:

```text
results/
└── Fusarium/
    ├── raw/
    ├── InterProScan/
    ├── BLAST/
    ├── GO/
    ├── GO-Slim/
    ├── reports/
    └── Fusarium_Protein_Annotation.xlsx
```

The exact output structure depends on the pipeline version and completed analysis stages.

The main integrated spreadsheet is:

```text
Fusarium_Protein_Annotation.xlsx
```

The BLAST output is:

```text
BLAST_SwissProt.tsv
```

Raw/intermediate results are retained for reproducibility.

---

# 21. Resource troubleshooting

If the pipeline reports:

```text
[MISSING] GO ontology
```

check:

```bash
ls -lh /path/to/go-basic.obo
```

If it reports:

```text
[MISSING] GO-Slim ontology
```

check:

```bash
ls -lh /path/to/goslim_generic.obo
```

If it reports:

```text
[MISSING] InterPro2GO
```

check:

```bash
ls -lh /path/to/interpro2go
```

If BLAST reports:

```text
BLAST protein database not found
```

check that the configured database prefix exists:

```bash
ls -lh /path/to/swissprot/swissprot.*
```

You should have at least:

```text
swissprot.pin
swissprot.psq
swissprot.phr
```

If InterProScan data is missing, check:

```bash
ls -lah /path/to/interproscan6/data
```

---

# 22. Important GitHub/repository rule

Do NOT commit local database/resource files.

The following files are intentionally excluded:

```text
config/resources.local.yaml
config/.runtime_config.yaml
results/
*.obo
interpro2go
Swiss-Prot databases
InterProScan data
FASTA input files
```

Each user creates their own:

```text
config/resources.local.yaml
```

from:

```text
config/resources.local.example.yaml
```

---

# 23. Reproducibility

For published analyses, record:

* Pipeline Git commit
* InterProScan version
* InterPro data release
* GO ontology version/date
* GO-Slim version/date
* InterPro2GO version/date
* UniProtKB/Swiss-Prot release
* BLAST+ version
* Nextflow version
* Container runtime/version
* Input FASTA filename
* Number of protein sequences
* CPU/thread count

This allows the analysis to be reproduced later.

---

# 24. Official resources

InterProScan 6:

https://github.com/ebi-pf-team/interproscan6

InterProScan downloads:

https://www.ebi.ac.uk/interpro/download/InterProScan/

Gene Ontology:

https://geneontology.org/

GO ontology downloads:

https://geneontology.org/docs/download-ontology/

GO subsets:

https://geneontology.org/docs/go-subset-guide/

UniProt:

https://www.uniprot.org/

NCBI BLAST:

https://www.ncbi.nlm.nih.gov/books/NBK569861/

---

# 25. Quick-start checklist

Before running the pipeline, confirm:

```text
[ ] Ubuntu/WSL available
[ ] Internet available for installation/downloads
[ ] Python installed
[ ] BLAST+ installed
[ ] blastp works
[ ] Nextflow installed
[ ] Docker/container runtime installed
[ ] InterProScan 6 available
[ ] InterProScan data downloaded
[ ] go-basic.obo downloaded
[ ] goslim_generic.obo downloaded
[ ] interpro2go downloaded
[ ] Swiss-Prot FASTA downloaded
[ ] Swiss-Prot BLAST database created
[ ] resources.local.yaml configured
[ ] FASTA file available
[ ] FASTA contains protein sequences
[ ] FASTA path is correct
```

Then run:

```bash
./fusarium_annotator.sh
```

---

## Citation

If you use this pipeline, cite the underlying resources and software used in your analysis, including InterProScan, InterPro, Gene Ontology, UniProtKB/Swiss-Prot and BLAST+.

Pipeline citation:

**To be updated after publication.**
