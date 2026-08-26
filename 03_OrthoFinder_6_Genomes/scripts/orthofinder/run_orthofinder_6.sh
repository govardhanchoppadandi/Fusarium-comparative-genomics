#!/usr/bin/env bash

# ==========================================================
# FUSARIUM 6 — COMPLETE ORTHOFINDER / PHYLOGENOMICS WORKFLOW
#
# This workflow:
#
# 1. Creates the phylogenetics Conda environment
# 2. Installs required software
# 3. Standardizes six Fusarium proteomes
# 4. Runs OrthoFinder
# 5. Extracts single-copy orthologues
# 6. Concatenates single-copy orthologues by species
# 7. Validates the concatenated alignment
# 8. Builds the phylogenomic tree using RAxML-NG
#
# Main outputs:
#
# concat6.fasta
# fusarium6.raxml.bestTree
# fusarium6.raxml.support
# fusarium6.raxml.bestModel
# fusarium6.raxml.bootstraps
# fusarium6.raxml.log
#
# ==========================================================


# ==========================================================
# STEP 1 — CREATE PHYLOGENETICS ENVIRONMENT
# ==========================================================

conda create -n phylo_env python=3.10 -y

conda activate phylo_env


# ==========================================================
# STEP 2 — INSTALL REQUIRED SOFTWARE
# ==========================================================

conda install -y -c bioconda \
    mafft \
    trimal \
    orthofinder \
    raxml-ng \
    diamond \
    mcl \
    fastme

conda install -y biopython


# ==========================================================
# STEP 3 — CREATE WORKING DIRECTORIES
# ==========================================================

mkdir -p ~/fusarium/scripts
mkdir -p ~/fusarium/alignments
mkdir -p ~/fusarium/concat

cd ~/fusarium


# ==========================================================
# STEP 4 — STANDARDIZE PROTEOME HEADERS
#
# The actual header-standardization code is maintained
# separately in:
#
# scripts/prepare_proteomes/fix_headers.py
#
# The six proteomes are standardized before OrthoFinder.
# ==========================================================

python ~/fusarium/scripts/fix_headers.py


# ==========================================================
# STEP 5 — RUN ORTHOFINDER
# ==========================================================

orthofinder \
    -f "/mnt/e/Fusarium2/proteomes" \
    -t 8 \
    -o "/mnt/e/Fusarium2/orthofinder_out"


# ==========================================================
# STEP 6 — COUNT SINGLE-COPY ORTHOGROUPS
# ==========================================================

ls \
/mnt/e/Fusarium2/orthofinder_out/Results_*/Single_Copy_Orthologue_Sequences \
| wc -l


# ==========================================================
# STEP 7 — COPY SINGLE-COPY ORTHOLOGUE ALIGNMENTS
# ==========================================================

mkdir -p ~/fusarium/alignments

cp \
/mnt/e/Fusarium2/orthofinder_out/Results_*/Single_Copy_Orthologue_Sequences/* \
~/fusarium/alignments/


# ==========================================================
# VERIFY COPIED ALIGNMENTS
# ==========================================================

ls ~/fusarium/alignments | wc -l


# ==========================================================
# STEP 8 — CONCATENATE SINGLE-COPY ORTHOLOGUES
#
# The actual concatenation script is maintained separately:
#
# scripts/phylogenomics/concat_by_species.py
# ==========================================================

python ~/fusarium/scripts/concat_by_species.py


# ==========================================================
# STEP 9 — VALIDATE CONCATENATED ALIGNMENT
# ==========================================================

python3 - <<EOF

from Bio import SeqIO

seqs = list(
    SeqIO.parse(
        "/home/govardhan/fusarium/concat/concat6.fasta",
        "fasta"
    )
)

print("Number of sequences:", len(seqs))

lengths = set(
    len(x.seq)
    for x in seqs
)

print("Unique lengths:", lengths)

EOF


# ==========================================================
# STEP 10 — BUILD PHYLOGENOMIC TREE
# ==========================================================

cd ~/fusarium/concat

raxml-ng --all \
    --msa /home/govardhan/fusarium/concat/concat6.fasta \
    --model LG+G4 \
    --threads 8 \
    --bs-trees 100 \
    --prefix fusarium6


# ==========================================================
# STEP 11 — VIEW RAxML-NG OUTPUTS
# ==========================================================

ls fusarium6.raxml*


# ==========================================================
# IMPORTANT OUTPUT FILES
# ==========================================================

echo
echo "=========================================================="
echo "FUSARIUM 6 PHYLOGENOMICS WORKFLOW COMPLETE"
echo "=========================================================="

echo
echo "Concatenated alignment:"
echo "concat6.fasta"

echo
echo "RAxML-NG outputs:"
echo "fusarium6.raxml.bestTree"
echo "fusarium6.raxml.support"
echo "fusarium6.raxml.bestModel"
echo "fusarium6.raxml.bootstraps"
echo "fusarium6.raxml.log"

echo
echo "=========================================================="
