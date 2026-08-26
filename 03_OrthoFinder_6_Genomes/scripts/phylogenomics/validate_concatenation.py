#!/usr/bin/env python3

import os
from Bio import SeqIO

# ============================================================
# OrthoFinder 6 Genomes
# Validate concatenated single-copy orthologue alignment
# ============================================================

RESULTS_DIR = "/mnt/e/fusarium_run/of_run_001/Results_Dec10"

PHYLOGENOMICS_DIR = os.path.join(
    RESULTS_DIR,
    "Phylogenomics"
)

ALIGNMENT = os.path.join(
    PHYLOGENOMICS_DIR,
    "SingleCopy_Core_Concatenated.fasta"
)

PARTITIONS = os.path.join(
    PHYLOGENOMICS_DIR,
    "SingleCopy_Core_Partitions.txt"
)

REPORT = os.path.join(
    PHYLOGENOMICS_DIR,
    "Concatenation_Validation.txt"
)

# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("FUSARIUM — CONCATENATED ALIGNMENT VALIDATION")
print("=" * 70)

print()
print("Alignment:")
print(ALIGNMENT)

print()
print("Partitions:")
print(PARTITIONS)

# ============================================================
# CHECK FILES
# ============================================================

if not os.path.isfile(ALIGNMENT):
    raise FileNotFoundError(
        "Concatenated FASTA not found:\n"
        + ALIGNMENT
    )

if not os.path.isfile(PARTITIONS):
    raise FileNotFoundError(
        "Partition file not found:\n"
        + PARTITIONS
    )

# ============================================================
# READ ALIGNMENT
# ============================================================

records = list(
    SeqIO.parse(
        ALIGNMENT,
        "fasta"
    )
)

if len(records) == 0:
    raise RuntimeError(
        "No sequences found in concatenated FASTA."
    )

print()
print("Sequences detected:", len(records))

# ============================================================
# EXPECT SIX SPECIES
# ============================================================

expected_species = [
    "DMW8",
    "F_avenaceum",
    "F_culmorum",
    "F_graminearum",
    "F_poae",
    "TNW1"
]

observed_species = [
    record.id
    for record in records
]

print()
print("Species detected:")

for sp in observed_species:
    print("  ", sp)

missing_species = [
    sp
    for sp in expected_species
    if sp not in observed_species
]

extra_species = [
    sp
    for sp in observed_species
    if sp not in expected_species
]

if missing_species:
    raise RuntimeError(
        "Missing expected species: "
        + ", ".join(missing_species)
    )

if extra_species:
    print()
    print(
        "WARNING: Unexpected species:",
        ", ".join(extra_species)
    )

if len(records) != 6:
    raise RuntimeError(
        f"Expected 6 sequences, found {len(records)}"
    )

# ============================================================
# CHECK ALIGNMENT LENGTH
# ============================================================

lengths = {
    record.id: len(record.seq)
    for record in records
}

print()
print("Sequence lengths:")

for sp, length in lengths.items():
    print(
        f"  {sp}: {length}"
    )

unique_lengths = set(
    lengths.values()
)

if len(unique_lengths) != 1:

    raise RuntimeError(
        "ERROR: Alignment sequences have different lengths."
    )

alignment_length = next(
    iter(unique_lengths)
)

print()
print(
    "Alignment length:",
    alignment_length
)

# ============================================================
# CHECK FOR EMPTY SEQUENCES
# ============================================================

empty = [
    sp
    for sp, length in lengths.items()
    if length == 0
]

if empty:

    raise RuntimeError(
        "Empty sequences detected: "
        + ", ".join(empty)
    )

# ============================================================
# CHECK FOR INVALID CHARACTERS
# ============================================================

valid_characters = set(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-*?"
)

invalid = {}

for record in records:

    chars = set(
        str(record.seq)
    )

    bad = chars - valid_characters

    if bad:

        invalid[
            record.id
        ] = sorted(bad)

if invalid:

    print()
    print(
        "WARNING: Invalid characters detected:"
    )

    for sp, chars in invalid.items():

        print(
            f"  {sp}: {chars}"
        )

# ============================================================
# READ PARTITIONS
# ============================================================

partition_lines = []

with open(
    PARTITIONS,
    "r"
) as handle:

    for line in handle:

        line = line.strip()

        if not line:
            continue

        partition_lines.append(line)

print()
print(
    "Partitions detected:",
    len(partition_lines)
)

if len(partition_lines) == 0:

    raise RuntimeError(
        "No partitions found."
    )

# ============================================================
# VALIDATE PARTITION COORDINATES
# ============================================================

previous_end = 0

partition_errors = []

for index, line in enumerate(
    partition_lines,
    start=1
):

    try:

        name, coordinates = line.split(
            "=",
            1
        )

        start, end = coordinates.strip().split(
            "-"
        )

        start = int(start)
        end = int(end)

    except Exception:

        partition_errors.append(
            f"Invalid partition format: {line}"
        )

        continue

    if start < 1:

        partition_errors.append(
            f"Partition {name.strip()} starts before position 1."
        )

    if end < start:

        partition_errors.append(
            f"Partition {name.strip()} has end < start."
        )

    if start != previous_end + 1:

        partition_errors.append(
            f"Partition {name.strip()} is not contiguous."
        )

    if end > alignment_length:

        partition_errors.append(
            f"Partition {name.strip()} exceeds alignment length."
        )

    previous_end = end

# ============================================================
# PARTITION COVERAGE
# ============================================================

partition_end = previous_end

print()
print(
    "Partition end:",
    partition_end
)

print(
    "Alignment length:",
    alignment_length
)

if partition_end != alignment_length:

    partition_errors.append(
        "Partitions do not cover the complete alignment."
    )

# ============================================================
# REPORT
# ============================================================

with open(
    REPORT,
    "w"
) as handle:

    handle.write(
        "FUSARIUM — CONCATENATED ALIGNMENT VALIDATION\n"
    )

    handle.write(
        "=" * 70 + "\n\n"
    )

    handle.write(
        f"Number of sequences: {len(records)}\n"
    )

    handle.write(
        f"Alignment length: {alignment_length}\n"
    )

    handle.write(
        f"Number of partitions: {len(partition_lines)}\n"
    )

    handle.write(
        f"Partition end: {partition_end}\n"
    )

    handle.write(
        "\nSequence lengths:\n"
    )

    for sp, length in lengths.items():

        handle.write(
            f"{sp}\t{length}\n"
        )

    handle.write(
        "\nExpected species:\n"
    )

    for sp in expected_species:

        handle.write(
            f"{sp}\n"
        )

    handle.write(
        "\nValidation:\n"
    )

    if not missing_species:
        handle.write(
            "PASS: All 6 expected species are present.\n"
        )

    if len(unique_lengths) == 1:
        handle.write(
            "PASS: All sequences have identical length.\n"
        )

    if not empty:
        handle.write(
            "PASS: No empty sequences detected.\n"
        )

    if not partition_errors:
        handle.write(
            "PASS: Partition coordinates are valid and contiguous.\n"
        )

    if invalid:
        handle.write(
            "WARNING: Invalid sequence characters detected.\n"
        )

    if partition_errors:

        handle.write(
            "\nPartition errors:\n"
        )

        for error in partition_errors:

            handle.write(
                error + "\n"
            )

# ============================================================
# FINAL STATUS
# ============================================================

print()
print("=" * 70)

if partition_errors:

    print(
        "VALIDATION FAILED"
    )

    print()
    for error in partition_errors:
        print(
            "ERROR:",
            error
        )

    print()
    print(
        "Report:",
        REPORT
    )

    raise SystemExit(1)

else:

    print(
        "VALIDATION PASSED"
    )

    print()
    print(
        "6 species:",
        len(records)
    )

    print(
        "Alignment length:",
        alignment_length
    )

    print(
        "Partitions:",
        len(partition_lines)
    )

    print()
    print(
        "Validation report:"
    )

    print(REPORT)

print()
print("=" * 70)
