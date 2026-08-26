#!/usr/bin/env python3

import os
import sys
import re

# ============================================================
# OrthoFinder 6 Genomes
# Protein FASTA Header Standardization
# ============================================================

def clean_header(header):
    """
    Convert a FASTA header into a simple OrthoFinder-safe
    sequence identifier while preserving the original ID
    information as much as possible.
    """

    header = header.strip()

    if header.startswith(">"):
        header = header[1:]

    # Keep only the first whitespace-delimited field
    header = header.split()[0]

    # Replace characters that may cause problems in identifiers
    header = re.sub(r"[^A-Za-z0-9_.|:-]", "_", header)

    return header


def process_fasta(input_file, output_file):
    """
    Read a protein FASTA file and write a standardized FASTA.
    """

    seen = set()
    sequence_count = 0

    with open(input_file, "r", encoding="utf-8") as infile, \
         open(output_file, "w", encoding="utf-8") as outfile:

        for line in infile:

            line = line.rstrip("\n")

            if line.startswith(">"):

                new_header = clean_header(line)

                # Ensure unique sequence identifiers
                base = new_header
                counter = 1

                while new_header in seen:
                    counter += 1
                    new_header = f"{base}_{counter}"

                seen.add(new_header)

                outfile.write(f">{new_header}\n")

                sequence_count += 1

            else:

                outfile.write(line.strip() + "\n")

    return sequence_count


def main():

    if len(sys.argv) != 3:

        print(
            "Usage:\n"
            "  python fix_headers.py input.faa output.faa"
        )

        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.isfile(input_file):

        print(
            f"ERROR: Input FASTA not found:\n{input_file}"
        )

        sys.exit(1)

    output_dir = os.path.dirname(
        os.path.abspath(output_file)
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    print("=" * 60)
    print("OrthoFinder 6 Genomes")
    print("Protein FASTA Header Standardization")
    print("=" * 60)

    print()
    print("Input:")
    print(input_file)

    print()
    print("Output:")
    print(output_file)

    count = process_fasta(
        input_file,
        output_file
    )

    print()
    print("=" * 60)
    print("COMPLETED")
    print("=" * 60)

    print(
        f"Protein sequences processed: {count}"
    )

    print()
    print("Output FASTA:")
    print(output_file)

    print()
    print("No protein sequences were modified.")
    print("Only FASTA identifiers were standardized.")


if __name__ == "__main__":
    main()
