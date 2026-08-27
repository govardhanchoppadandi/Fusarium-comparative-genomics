# McClintock Transposable Element Insertion Analysis

This module documents the installation and execution of the **McClintock Transposable Element (TE) insertion pipeline** used for TE insertion analysis in the *Fusarium* comparative genomics workflow.

## Directory structure

```text
09_McClintock/
├── README.md
└── scripts/
```

## Purpose

McClintock is used to identify and characterize **transposable element insertion polymorphisms** from genome and Illumina paired-end sequencing data using multiple TE insertion detection methods.

This workflow is configured for:

- **DMW8 – Fusarium avenaceum**
- **TNW1 – Fusarium graminearum**

The analysis uses:

1. Genome FASTA
2. Species-specific EarlGrey TE family library
3. Illumina paired-end reads
4. Multiple McClintock component methods

---

# 1. Software requirements

The analysis is performed in **Ubuntu/WSL**.

Required software/dependencies:

- Ubuntu/WSL
- `wget`
- Miniforge
- Conda
- Mamba
- Git
- Python 3
- McClintock
- McClintock component methods

McClintock itself installs/configures the component methods required by the pipeline.

---

# 2. Install Miniforge

Run in Ubuntu/WSL:

```bash
wget -O Miniforge3.sh \
"https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"

bash Miniforge3.sh \
-b \
-p "${HOME}/conda"
```

---

# 3. Load Conda and Mamba

```bash
source "${HOME}/conda/etc/profile.d/conda.sh"
source "${HOME}/conda/etc/profile.d/mamba.sh"
```

Initialize Conda:

```bash
conda init
```

### Important

After running `conda init`:

**Close the Ubuntu/WSL terminal completely and open a new terminal.**

---

# 4. Load Conda after reopening Ubuntu

```bash
source "${HOME}/conda/etc/profile.d/conda.sh"
```

Check Conda:

```bash
conda --version
```

Check Mamba:

```bash
mamba --version
```

---

# 5. Download McClintock

Move to the home directory:

```bash
cd ~
```

Clone the McClintock repository:

```bash
git clone https://github.com/bergmanlab/mcclintock.git
```

Enter the repository:

```bash
cd mcclintock
```

---

# 6. Create the McClintock Conda environment

Create the environment from the supplied environment file:

```bash
mamba env create \
-f install/envs/mcclintock.yml \
--name mcclintock
```

Activate the environment:

```bash
conda activate mcclintock
```

Verify the environment:

```bash
conda env list
```

The active environment should be:

```text
mcclintock
```

---

# 7. Install McClintock component methods

Install the McClintock methods:

```bash
python3 mcclintock.py --install
```

This can take a substantial amount of time because multiple component programs are installed.

## Optional: install selected methods

The workflow can also install the methods used in this analysis:

```bash
python3 mcclintock.py \
--install \
-m ngs_te_mapper,ngs_te_mapper2,relocate,relocate2,temp,temp2,retroseq,popoolationte,popoolationte2,te-locate,teflon,tebreak
```

## Optional: resume an incomplete installation

If an installation stops before all components are installed:

```bash
python3 mcclintock.py \
--install \
--resume
```

---

# 8. Verify McClintock

Run:

```bash
python3 mcclintock.py --help
```

The McClintock help/usage information should be displayed.

---

# 9. Input data

The workflow requires three types of input for each isolate.

## 9.1 Genome FASTA

### DMW8

```text
/mnt/d/genomes/DMW_8.genome.fa
```

### TNW1

```text
/mnt/d/genomes/TNW_1.genome.fa
```

## 9.2 EarlGrey TE library

### DMW8

```text
/mnt/d/genomes/TE_analysis/FAD8_EarlGrey/FAD8_Database/FAD8-families.clean3.fa
```

### TNW1

```text
/mnt/d/genomes/TE_analysis/FGT1_EarlGrey/FGT1_Database/FGT1-families.clean3.fa
```

## 9.3 Illumina paired-end reads

### DMW8

```text
/mnt/e/Fusarium genome raw data datat/1_Illumina/1_Raw/DNW8_R1.fastq.gz
/mnt/e/Fusarium genome raw data datat/1_Illumina/1_Raw/DNW8_R2.fastq.gz
```

### TNW1

```text
/mnt/e/Fusarium genome raw data datat/1_Illumina/1_Raw/TNW1_R1.fastq.gz
/mnt/e/Fusarium genome raw data datat/1_Illumina/1_Raw/TNW1_R2.fastq.gz
```

> **Important:** Before running the analysis, confirm that the DMW8 genome, EarlGrey library, and Illumina reads all correspond to the same isolate. The supplied command uses `DMW_8` for the genome/library but `DNW8` for the read files. If this is not intentional, replace the read paths with the correct DMW8 read files.

---

# 10. Check input files before running

It is recommended to confirm that every input exists.

For example:

```bash
ls -lh "/mnt/d/genomes/DMW_8.genome.fa"
ls -lh "/mnt/d/genomes/TE_analysis/FAD8_EarlGrey/FAD8_Database/FAD8-families.clean3.fa"
ls -lh "/mnt/e/Fusarium genome raw data datat/1_Illumina/1_Raw/DNW8_R1.fastq.gz"
ls -lh "/mnt/e/Fusarium genome raw data datat/1_Illumina/1_Raw/DNW8_R2.fastq.gz"
```

For TNW1:

```bash
ls -lh "/mnt/d/genomes/TNW_1.genome.fa"
ls -lh "/mnt/d/genomes/TE_analysis/FGT1_EarlGrey/FGT1_Database/FGT1-families.clean3.fa"
ls -lh "/mnt/e/Fusarium genome raw data datat/1_Illumina/1_Raw/TNW1_R1.fastq.gz"
ls -lh "/mnt/e/Fusarium genome raw data datat/1_Illumina/1_Raw/TNW1_R2.fastq.gz"
```

If a file is missing, **do not start McClintock** until the path is corrected.

---

# 11. Run McClintock for DMW8

Make sure the environment is active:

```bash
conda activate mcclintock
```

Run:

```bash
cd ~/mcclintock
```

Then:

```bash
python3 mcclintock.py \
-r "/mnt/d/genomes/DMW_8.genome.fa" \
-c "/mnt/d/genomes/TE_analysis/FAD8_EarlGrey/FAD8_Database/FAD8-families.clean3.fa" \
-1 "/mnt/e/Fusarium genome raw data datat/1_Illumina/1_Raw/DNW8_R1.fastq.gz" \
-2 "/mnt/e/Fusarium genome raw data datat/1_Illumina/1_Raw/DNW8_R2.fastq.gz" \
-p 4 \
-m ngs_te_mapper,ngs_te_mapper2,relocate,relocate2,temp,temp2,retroseq,popoolationte,popoolationte2,te-locate,teflon,tebreak \
-n DMW8_FULL \
-o "/mnt/d/genomes/TE_analysis/McClintock_FULL_DMW8"
```

---

# 12. Run McClintock for TNW1

Run:

```bash
python3 mcclintock.py \
-r "/mnt/d/genomes/TNW_1.genome.fa" \
-c "/mnt/d/genomes/TE_analysis/FGT1_EarlGrey/FGT1_Database/FGT1-families.clean3.fa" \
-1 "/mnt/e/Fusarium genome raw data datat/1_Illumina/1_Raw/TNW1_R1.fastq.gz" \
-2 "/mnt/e/Fusarium genome raw data datat/1_Illumina/1_Raw/TNW1_R2.fastq.gz" \
-p 4 \
-m ngs_te_mapper,ngs_te_mapper2,relocate,relocate2,temp,temp2,retroseq,popoolationte,popoolationte2,te-locate,teflon,tebreak \
-n TNW1_FULL \
-o "/mnt/d/genomes/TE_analysis/McClintock_FULL_TNW1"
```

---

# 13. Parameters used

| Parameter | Meaning |
|---|---|
| `-r` | Reference genome FASTA |
| `-c` | TE consensus/family library |
| `-1` | Illumina paired-end Read 1 |
| `-2` | Illumina paired-end Read 2 |
| `-p 4` | Number of processing threads |
| `-m` | McClintock component methods |
| `-n` | Analysis/run name |
| `-o` | Output directory |

The selected methods are:

```text
ngs_te_mapper
ngs_te_mapper2
relocate
relocate2
temp
temp2
retroseq
popoolationte
popoolationte2
te-locate
teflon
tebreak
```

---

# 14. Check DMW8 results

```bash
ls -lh "/mnt/d/genomes/TE_analysis/McClintock_FULL_DMW8"
```

For a more detailed listing:

```bash
find "/mnt/d/genomes/TE_analysis/McClintock_FULL_DMW8" -maxdepth 2 -type f | head -100
```

---

# 15. Check TNW1 results

```bash
ls -lh "/mnt/d/genomes/TE_analysis/McClintock_FULL_TNW1"
```

For a more detailed listing:

```bash
find "/mnt/d/genomes/TE_analysis/McClintock_FULL_TNW1" -maxdepth 2 -type f | head -100
```

---

# 16. Expected analysis outputs

McClintock produces method-specific intermediate and final files inside the specified output directory.

The output directory should contain results associated with the selected TE insertion detection methods.

Final interpretation should focus on:

- TE insertion coordinates
- TE family/classification
- Supporting read evidence
- Insertion calls supported by individual methods
- Insertion calls supported by multiple methods
- Method-specific output tables

Do not treat every intermediate file as a final biological result.

---

# 17. Recommended downstream analysis

After McClintock completes:

1. Identify the final insertion calls from each method.
2. Extract TE insertion coordinates.
3. Standardize chromosome/contig names.
4. Compare insertion calls across methods.
5. Identify high-confidence insertions supported by multiple methods.
6. Summarize TE insertion numbers by TE family/class.
7. Compare TE insertion patterns between DMW8 and TNW1.
8. Prepare a final table for the manuscript.

A separate downstream-analysis script can be added to this repository after the McClintock outputs have been inspected.

---

# 18. Reproducibility notes

Record the following for the final analysis:

- McClintock version/commit
- Conda environment information
- Genome accession/version
- EarlGrey version and database
- TE library used
- Illumina read files
- Number of threads
- McClintock methods used
- Output directory
- Date of analysis

Useful commands:

```bash
python3 mcclintock.py --help
```

and:

```bash
conda list
```

---

# 19. Important file-management rule

Large raw FASTQ files, genome FASTA files, TE libraries, and complete McClintock intermediate directories should generally **not** be committed to GitHub.

Keep the repository focused on:

```text
README.md
scripts/
metadata/
configuration information
small summary tables
downstream analysis scripts
```

Large computational outputs can be retained locally or deposited in an appropriate data repository when required.

---

# 20. Workflow summary

```text
Genome FASTA
     │
     ├───────────────┐
     │               │
     ▼               ▼
EarlGrey TE       Illumina
library            PE reads
     │               │
     └───────┬───────┘
             ▼
       McClintock
             │
             ▼
 Multiple TE insertion
 detection methods
             │
             ▼
 Method-specific results
             │
             ▼
 High-confidence TE
 insertion calls
             │
             ▼
 Comparative TE
 insertion analysis
```

## Repository location

```text
09_McClintock/
├── README.md
└── scripts/
```

This module is part of the **Fusarium Comparative Genomics** computational workflow.
