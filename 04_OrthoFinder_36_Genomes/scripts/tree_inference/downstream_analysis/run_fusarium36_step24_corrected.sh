#!/usr/bin/env bash

set -u

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate orthofinder_clean

unset LD_LIBRARY_PATH
unset PYTHONPATH

RES="/mnt/d/ORTHOFINDER/FUSARIUM36_FINAL/Results_Aug12_5"
OUT="/mnt/d/ORTHOFINDER/FUSARIUM36_FINAL/STEP24_COMPARATIVE_GENOMICS"

mkdir -p "$OUT"

GENECOUNT="$RES/Orthogroups/Orthogroups.GeneCount.tsv"

echo "=========================================================="
echo "FUSARIUM 36 — STEP 24"
echo "COMPARATIVE GENOMICS"
echo "=========================================================="

echo
echo "Input:"
echo "$RES"

echo
echo "Output:"
echo "$OUT"

if [ ! -f "$GENECOUNT" ]; then
    echo "ERROR: GeneCount file not found"
    exit 1
fi

python <<PY
import pandas as pd
import os

gene_count = "$GENECOUNT"
out = "$OUT"

print()
print("Reading Orthogroups.GeneCount.tsv")

df = pd.read_csv(gene_count, sep="\t")

print("Total columns:", len(df.columns))

if "Orthogroup" not in df.columns:
    raise RuntimeError("Orthogroup column missing")

if "Total" not in df.columns:
    raise RuntimeError("Total column missing")

species = [
    x for x in df.columns
    if x not in ["Orthogroup", "Total"]
]

print("Species:", len(species))

if len(species) != 36:
    raise RuntimeError(
        f"Expected 36 species, found {len(species)}"
    )

print()
print("PASS: 36 species detected.")
print()

for i, sp in enumerate(species):
    print(f"{i}: {sp}")

# ==========================================================
# CORE ORTHOGROUPS
# ==========================================================

presence = df[species] > 0

core_mask = presence.all(axis=1)

core = df.loc[
    core_mask,
    ["Orthogroup"] + species
]

core.to_csv(
    os.path.join(
        out,
        "Core_Orthogroups_36_species.tsv"
    ),
    sep="\t",
    index=False
)

# ==========================================================
# SINGLE-COPY CORE
# ==========================================================

single_mask = df[species].eq(1).all(axis=1)

single = df.loc[
    single_mask,
    ["Orthogroup"] + species
]

single.to_csv(
    os.path.join(
        out,
        "SingleCopy_Core_Orthogroups.tsv"
    ),
    sep="\t",
    index=False
)

# ==========================================================
# SPECIES PRESENCE DISTRIBUTION
# ==========================================================

n_species = presence.sum(axis=1)

distribution = (
    n_species
    .value_counts()
    .sort_index()
    .rename_axis("Number_of_species")
    .reset_index(
        name="Number_of_orthogroups"
    )
)

distribution.to_csv(
    os.path.join(
        out,
        "Orthogroup_Species_Presence_Distribution.tsv"
    ),
    sep="\t",
    index=False
)

# ==========================================================
# SPECIES-SPECIFIC ORTHOGROUPS
# ==========================================================

specific_mask = n_species == 1

specific = df.loc[
    specific_mask,
    ["Orthogroup"] + species
]

specific.to_csv(
    os.path.join(
        out,
        "Species_Specific_Orthogroups.tsv"
    ),
    sep="\t",
    index=False
)

# ==========================================================
# SPECIES-SPECIFIC SUMMARY
# ==========================================================

rows = []

for sp in species:

    others = [
        x for x in species
        if x != sp
    ]

    mask = (
        df[sp] > 0
    ) & (
        df[others] == 0
    ).all(axis=1)

    rows.append({
        "Species": sp,
        "Species_specific_orthogroups":
            int(mask.sum()),
        "Genes_in_species_specific_orthogroups":
            int(df.loc[mask, sp].sum())
    })

pd.DataFrame(rows).to_csv(
    os.path.join(
        out,
        "Species_Specific_Summary.tsv"
    ),
    sep="\t",
    index=False
)

# ==========================================================
# SUMMARY
# ==========================================================

summary = os.path.join(
    out,
    "STEP24_SUMMARY.txt"
)

with open(summary, "w") as f:

    f.write(
        "FUSARIUM 36 — STEP 24 COMPARATIVE GENOMICS\n"
    )
    f.write("=" * 60 + "\n\n")

    f.write(
        f"Species: {len(species)}\n"
    )

    f.write(
        f"Orthogroups: {len(df)}\n"
    )

    f.write(
        f"Core orthogroups (36/36): {len(core)}\n"
    )

    f.write(
        f"Single-copy core orthogroups: "
        f"{len(single)}\n"
    )

    f.write(
        f"Species-specific orthogroups: "
        f"{len(specific)}\n"
    )

print()
print("==========================================================")
print("STEP 24 RESULTS")
print("==========================================================")

print("Species:", len(species))
print("Orthogroups:", len(df))
print("Core 36/36:", len(core))
print("Single-copy core:", len(single))
print("Species-specific:", len(specific))

print()
print("Output:")
print(out)

PY

echo
echo "=========================================================="
echo "STEP 24 OUTPUT FILES"
echo "=========================================================="

find "$OUT" -maxdepth 1 -type f \
    -printf "%f\t%s bytes\n" | sort

echo
echo "=========================================================="
echo "STEP 24 COMPLETE"
echo "NO ORTHOFINDER STARTED"
echo "ORIGINAL ORTHOFINDER RESULTS NOT MODIFIED"
echo "=========================================================="
