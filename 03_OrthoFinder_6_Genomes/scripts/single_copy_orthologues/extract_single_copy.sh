#!/usr/bin/env bash

set -euo pipefail

# ============================================================
# OrthoFinder 6 Genomes
# Extract single-copy orthologues
# ============================================================

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate orthofinder_clean

# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

RESULTS_DIR="/mnt/e/fusarium_run/of_run_001/Results_Dec10"

ORTHOGROUP_DIR="$RESULTS_DIR/Orthogroups"

OUTPUT_DIR="$RESULTS_DIR/Single_Copy_Orthologues"

mkdir -p "$OUTPUT_DIR"

GENECOUNT="$ORTHOGROUP_DIR/Orthogroups.GeneCount.tsv"
ORTHOLOGUES="$RESULTS_DIR/Orthologues"

echo "============================================================"
echo "FUSARIUM — SINGLE-COPY ORTHOLOGUE EXTRACTION"
echo "============================================================"

echo
echo "Results directory:"
echo "$RESULTS_DIR"

echo
echo "Orthogroup directory:"
echo "$ORTHOGROUP_DIR"

echo
echo "Output directory:"
echo "$OUTPUT_DIR"

# ------------------------------------------------------------
# CHECK INPUT
# ------------------------------------------------------------

if [ ! -f "$GENECOUNT" ]; then
    echo
    echo "ERROR: Orthogroups.GeneCount.tsv not found:"
    echo "$GENECOUNT"
    exit 1
fi

echo
echo "PASS: Orthogroups.GeneCount.tsv found."

# ------------------------------------------------------------
# EXTRACT SINGLE-COPY CORE ORTHOGROUPS
# ------------------------------------------------------------

python <<PY

import pandas as pd
import os

gene_count = "$GENECOUNT"
output_dir = "$OUTPUT_DIR"

print()
print("Reading Orthogroups.GeneCount.tsv")

df = pd.read_csv(gene_count, sep="\\t")

if "Orthogroup" not in df.columns:
    raise RuntimeError("Orthogroup column not found.")

# ------------------------------------------------------------
# IDENTIFY SPECIES COLUMNS
# ------------------------------------------------------------

exclude = ["Orthogroup", "Total"]

species = [
    c for c in df.columns
    if c not in exclude
]

print()
print("Species detected:", len(species))

for sp in species:
    print(" -", sp)

# ------------------------------------------------------------
# REQUIRE 6 SPECIES
# ------------------------------------------------------------

if len(species) != 6:
    raise RuntimeError(
        f"Expected 6 species, but found {len(species)}."
    )

print()
print("PASS: 6 species detected.")

# ------------------------------------------------------------
# SINGLE-COPY CORE
# ------------------------------------------------------------

single_copy_mask = df[species].eq(1).all(axis=1)

single_copy = df.loc[
    single_copy_mask,
    ["Orthogroup"] + species
]

print()
print(
    "Single-copy core orthogroups:",
    len(single_copy)
)

# ------------------------------------------------------------
# SAVE SINGLE-COPY ORTHOGROUP TABLE
# ------------------------------------------------------------

single_copy_file = os.path.join(
    output_dir,
    "SingleCopy_Core_Orthogroups.tsv"
)

single_copy.to_csv(
    single_copy_file,
    sep="\\t",
    index=False
)

print()
print("Saved:")
print(single_copy_file)

# ------------------------------------------------------------
# SAVE ORTHOGROUP LIST
# ------------------------------------------------------------

orthogroup_list = os.path.join(
    output_dir,
    "SingleCopy_Core_Orthogroup_IDs.txt"
)

single_copy["Orthogroup"].to_csv(
    orthogroup_list,
    index=False,
    header=False
)

print()
print("Saved:")
print(orthogroup_list)

# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------

summary_file = os.path.join(
    output_dir,
    "SingleCopy_Summary.txt"
)

with open(summary_file, "w") as f:

    f.write(
        "FUSARIUM — SINGLE-COPY ORTHOLOGUE ANALYSIS\\n"
    )

    f.write("=" * 60 + "\\n\\n")

    f.write(
        f"Number of species: {len(species)}\\n"
    )

    f.write(
        f"Total orthogroups: {len(df)}\\n"
    )

    f.write(
        f"Single-copy core orthogroups: "
        f"{len(single_copy)}\\n"
    )

    f.write("\\nSpecies:\\n")

    for sp in species:
        f.write(f"{sp}\\n")

print()
print("Saved:")
print(summary_file)

PY

# ------------------------------------------------------------
# FINAL OUTPUT
# ------------------------------------------------------------

echo
echo "============================================================"
echo "SINGLE-COPY EXTRACTION COMPLETE"
echo "============================================================"

echo
echo "Output files:"

find "$OUTPUT_DIR" -maxdepth 1 -type f \
    -printf "%f\t%s bytes\n" | sort

echo
echo "Original OrthoFinder results were not modified."

echo
echo "============================================================"
