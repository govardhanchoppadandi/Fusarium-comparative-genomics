#!/usr/bin/env python3

from Bio import SeqIO
import os


def validate_fasta(input_fasta):

    if not os.path.isfile(input_fasta):

        raise FileNotFoundError(
            f"FASTA not found: {input_fasta}"
        )

    proteins = 0
    total_length = 0

    ids = set()

    duplicate_ids = []

    for record in SeqIO.parse(input_fasta, "fasta"):

        proteins += 1

        total_length += len(record.seq)

        if record.id in ids:

            duplicate_ids.append(record.id)

        ids.add(record.id)

    if proteins == 0:

        raise ValueError(
            "No protein sequences found in FASTA."
        )

    print("=" * 70)
    print("FASTA QC")
    print("=" * 70)

    print(f"Protein sequences : {proteins:,}")
    print(f"Total aa          : {total_length:,}")
    print(f"Duplicate IDs     : {len(duplicate_ids):,}")

    if duplicate_ids:

        print("WARNING: duplicate sequence IDs detected.")

    else:

        print("Sequence IDs      : OK")

    print("=" * 70)

    return {
        "proteins": proteins,
        "total_length": total_length,
        "duplicate_ids": len(duplicate_ids)
    }
