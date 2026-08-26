#!/usr/bin/env python3

import os
import glob
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

# ============================================================
# OrthoFinder 6 Genomes
# Concatenate single-copy orthologues by species
# ============================================================

RESULTS_DIR = "/mnt/e/fusarium_run/of_run_001/Results_Dec10"

SINGLE_COPY_DIR = os.path.join(
    RESULTS_DIR,
    "Single_Copy_Orthologues"
)

ORTHOGROUP_DIR = os.path.join(
    RESULTS_DIR,
    "Orthogroups"
)

OUTPUT_DIR = os.path.join(
    RESULTS_DIR,
    "Phylogenomics"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# INPUT / OUTPUT
# ============================================================

ORTHOGROUP_FILE = os.path.join(
    SINGLE_COPY_DIR,
    "SingleCopy_Core_Orthogroups.tsv"
)

PROTEIN_DIR = os.path.join(
    RESULTS_DIR,
    "Orthogroup_Sequences"
)

CONCAT_FASTA = os.path.join(
    OUTPUT_DIR,
    "SingleCopy_Core_Concatenated.fasta"
)

PARTITIONS_FILE = os.path.join(
    OUTPUT_DIR,
    "SingleCopy_Core_Partitions.txt"
)

SUMMARY_FILE = os.path.join(
    OUTPUT_DIR,
    "Concatenation_Summary.txt"
)

# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("FUSARIUM — SINGLE-COPY ORTHOLOGUE CONCATENATION")
print("=" * 70)

print()
print("Results directory:")
print(RESULTS_DIR)

print()
print("Single-copy orthogroup table:")
print(ORTHOGROUP_FILE)

print()
print("Orthogroup sequence directory:")
print(PROTEIN_DIR)

# ============================================================
# CHECK INPUT
# ============================================================

if not os.path.isfile(ORTHOGROUP_FILE):
    raise FileNotFoundError(
        "SingleCopy_Core_Orthogroups.tsv not found:\n"
        + ORTHOGROUP_FILE
    )

if not os.path.isdir(PROTEIN_DIR):
    raise FileNotFoundError(
        "Orthogroup_Sequences directory not found:\n"
        + PROTEIN_DIR
    )

# ============================================================
# READ SINGLE-COPY ORTHOGROUPS
# ============================================================

import pandas as pd

df = pd.read_csv(
    ORTHOGROUP_FILE,
    sep="\t"
)

if "Orthogroup" not in df.columns:
    raise RuntimeError(
        "Orthogroup column not found."
    )

species = [
    x for x in df.columns
    if x != "Orthogroup"
]

if len(species) != 6:
    raise RuntimeError(
        f"Expected 6 species, found {len(species)}"
    )

print()
print("Species detected:")
for sp in species:
    print("  ", sp)

print()
print(
    "Single-copy orthogroups:",
    len(df)
)

# ============================================================
# FIND ORTHOGROUP FASTA FILES
# ============================================================

fasta_files = {}

for file in glob.glob(
    os.path.join(PROTEIN_DIR, "*.fa*")
):

    basename = os.path.basename(file)

    og = basename.split(".")[0]

    fasta_files[og] = file

print()
print(
    "Orthogroup FASTA files found:",
    len(fasta_files)
)

# ============================================================
# PREPARE CONCATENATION
# ============================================================

concatenated = {
    sp: []
    for sp in species
}

partitions = []

position = 1

processed = 0
missing = 0

# ============================================================
# PROCESS EACH ORTHOGROUP
# ============================================================

for _, row in df.iterrows():

    og = row["Orthogroup"]

    fasta_file = fasta_files.get(og)

    if fasta_file is None:

        missing += 1

        print(
            "WARNING: FASTA not found for",
            og
        )

        continue

    records = list(
        SeqIO.parse(
            fasta_file,
            "fasta"
        )
    )

    sequence_map = {}

    for record in records:

        sequence_map[record.id] = str(
            record.seq
        )

    # --------------------------------------------------------
    # Extract one sequence per species
    # --------------------------------------------------------

    sequences = {}

    valid = True

    for sp in species:

        expected = row[sp]

        if expected != 1:

            valid = False
            break

        matches = [
            seq
            for seq_id, seq in sequence_map.items()
            if seq_id.startswith(sp)
        ]

        if len(matches) != 1:

            valid = False

            print(
                f"WARNING: {og} -> {sp}: "
                f"expected 1 sequence, found {len(matches)}"
            )

            break

        sequences[sp] = matches[0]

    if not valid:

        missing += 1
        continue

    # --------------------------------------------------------
    # Check sequence lengths
    # --------------------------------------------------------

    lengths = [
        len(sequences[sp])
        for sp in species
    ]

    if len(set(lengths)) != 1:

        print(
            f"WARNING: {og} has unequal sequence lengths"
        )

        missing += 1
        continue

    length = lengths[0]

    # --------------------------------------------------------
    # Add sequences
    # --------------------------------------------------------

    for sp in species:

        concatenated[sp].append(
            sequences[sp]
        )

    start = position
    end = position + length - 1

    partitions.append(
        (
            og,
            start,
            end
        )
    )

    position = end + 1

    processed += 1

# ============================================================
# CHECK RESULTS
# ============================================================

if processed == 0:

    raise RuntimeError(
        "No orthogroups could be concatenated."
    )

print()
print("=" * 70)
print("CONCATENATION RESULTS")
print("=" * 70)

print()
print(
    "Orthogroups processed:",
    processed
)

print(
    "Orthogroups skipped:",
    missing
)

print(
    "Total alignment length:",
    position - 1
)

# ============================================================
# WRITE CONCATENATED FASTA
# ============================================================

records = []

for sp in species:

    sequence = "".join(
        concatenated[sp]
    )

    records.append(
        SeqRecord(
            Seq(sequence),
            id=sp,
            description=""
        )
    )

SeqIO.write(
    records,
    CONCAT_FASTA,
    "fasta"
)

print()
print("Concatenated alignment:")
print(CONCAT_FASTA)

# ============================================================
# WRITE PARTITIONS
# ============================================================

with open(
    PARTITIONS_FILE,
    "w"
) as handle:

    for og, start, end in partitions:

        handle.write(
            f"{og} = {start}-{end}\n"
        )

print()
print("Partition file:")
print(PARTITIONS_FILE)

# ============================================================
# WRITE SUMMARY
# ============================================================

with open(
    SUMMARY_FILE,
    "w"
) as handle:

    handle.write(
        "FUSARIUM — SINGLE-COPY ORTHOLOGUE CONCATENATION\n"
    )

    handle.write(
        "=" * 70 + "\n\n"
    )

    handle.write(
        f"Species: {len(species)}\n"
    )

    handle.write(
        f"Single-copy orthogroups available: {len(df)}\n"
    )

    handle.write(
        f"Orthogroups concatenated: {processed}\n"
    )

    handle.write(
        f"Orthogroups skipped: {missing}\n"
    )

    handle.write(
        f"Concatenated alignment length: {position - 1}\n"
    )

    handle.write(
        f"Species in alignment: {len(records)}\n"
    )

    handle.write("\nSpecies:\n")

    for sp in species:

        handle.write(
            f"{sp}\n"
        )

# ============================================================
# FINAL
# ============================================================

print()
print("=" * 70)
print("CONCATENATION COMPLETE")
print("=" * 70)

print()
print("Outputs:")
print(CONCAT_FASTA)
print(PARTITIONS_FILE)
print(SUMMARY_FILE)

print()
print("Original OrthoFinder results were not modified.")
