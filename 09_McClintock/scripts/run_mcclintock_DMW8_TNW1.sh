# ==========================================================
# McCLINTOCK TRANSPOSABLE ELEMENT INSERTION PIPELINE
#
# This pipeline will:
# 1. Install Miniforge (Conda + Mamba)
# 2. Initialize Conda
# 3. Clone McClintock repository
# 4. Create McClintock environment
# 5. Install McClintock component methods
# 6. Run McClintock for DMW_8 and TNW_1
#
# IMPORTANT:
# After "conda init", CLOSE TERMINAL
# and OPEN A NEW TERMINAL before continuing.
# ==========================================================


# ==========================================================
# STEP 1: INSTALL MINIFORGE
# (Conda + Mamba)
# ==========================================================

wget -O Miniforge3.sh \
"https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"

bash Miniforge3.sh \
-b \
-p "${HOME}/conda"


# ==========================================================
# STEP 2: LOAD CONDA + MAMBA
# ==========================================================

source "${HOME}/conda/etc/profile.d/conda.sh"

source "${HOME}/conda/etc/profile.d/mamba.sh"


# ==========================================================
# STEP 3: INITIALIZE CONDA
#
# IMPORTANT:
# CLOSE TERMINAL AND OPEN AGAIN
# ==========================================================

conda init


# ==========================================================
# AFTER REOPENING TERMINAL
# Run below commands
# ==========================================================


# ==========================================================
# STEP 4: LOAD CONDA
# ==========================================================

source "${HOME}/conda/etc/profile.d/conda.sh"


# ==========================================================
# STEP 5: CLONE McClintock REPOSITORY
# ==========================================================

cd ~

git clone https://github.com/bergmanlab/mcclintock.git

cd mcclintock


# ==========================================================
# STEP 6: CREATE McClintock CONDA ENVIRONMENT
#
# This installs:
# - Snakemake
# - Python3
# - BioPython
# - Base dependencies
# ==========================================================

mamba env create \
-f install/envs/mcclintock.yml \
--name mcclintock


# ==========================================================
# STEP 7: ACTIVATE McClintock ENVIRONMENT
#
# MUST ACTIVATE BEFORE RUNNING
# ==========================================================

conda activate mcclintock


# ==========================================================
# STEP 8: INSTALL ALL McClintock METHODS
#
# This may take HOURS
# ==========================================================

python3 mcclintock.py --install

# ==========================================================
# OPTIONAL:
# INSTALL ONLY SPECIFIC METHODS
# ==========================================================

python3 mcclintock.py \
--install \
-m ngs_te_mapper,ngs_te_mapper2,relocate,relocate2,temp,temp2,retroseq,popoolationte,popoolationte2,te-locate,teflon,tebreak

# ==========================================================
# OPTIONAL:
# RESUME MISSING INSTALLATIONS
# ==========================================================

python3 mcclintock.py \
--install \
--resume


# ==========================================================
# STEP 9: VERIFY INSTALLATION
# ==========================================================

python3 mcclintock.py --help

# ==========================================================
# STEP 10: RUN McClintock FOR DMW_8
#
# Inputs:
# Genome fasta
# EarlGrey TE library
# Illumina paired-end reads
# ==========================================================

python3 mcclintock.py \
  -r "/mnt/d/genomes/DMW_8.genome.fa" \
  -c "/mnt/d/genomes/TE_analysis/FAD8_EarlGrey/FAD8_Database/FAD8-families.clean3.fa" \
  -1 "/mnt/e/Fusarium genome raw data datat/1_Illumina/1_Raw/DNW8_R1.fastq.gz" \
  -2 "/mnt/e/Fusarium genome raw data datat/1_Illumina/1_Raw/DNW8_R2.fastq.gz" \
  -p 4 \
  -m ngs_te_mapper,ngs_te_mapper2,relocate,relocate2,temp,temp2,retroseq,popoolationte,popoolationte2,te-locate,teflon,tebreak \
  -n DMW8_FULL \
  -o "/mnt/d/genomes/TE_analysis/McClintock_FULL_DMW8"

# ==========================================================
# STEP 11: RUN McClintock FOR TNW_1
# ==========================================================

python3 mcclintock.py \
  -r "/mnt/d/genomes/TNW_1.genome.fa" \
  -c "/mnt/d/genomes/TE_analysis/FGT1_EarlGrey/FGT1_Database/FGT1-families.clean3.fa" \
  -1 "/mnt/e/Fusarium genome raw data datat/1_Illumina/1_Raw/TNW1_R1.fastq.gz" \
  -2 "/mnt/e/Fusarium genome raw data datat/1_Illumina/1_Raw/TNW1_R2.fastq.gz" \
  -p 4 \
  -m ngs_te_mapper,ngs_te_mapper2,relocate,relocate2,temp,temp2,retroseq,popoolationte,popoolationte2,te-locate,teflon,tebreak \
  -n TNW1_FULL \
  -o "/mnt/d/genomes/TE_analysis/McClintock_FULL_TNW1"

# ==========================================================
# STEP 12: CHECK RESULTS
# ==========================================================

ls /mnt/d/genomes/TE_analysis/McClintock_FULL_DMW8
ls /mnt/d/genomes/TE_analysis/McClintock_FULL_TNW1





























