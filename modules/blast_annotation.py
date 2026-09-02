#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path


# ============================================================
# RUN BLASTP
# ============================================================

def run_blast(
    query_fasta,
    database,
    output_file,
    threads=4,
    evalue=1e-5,
    max_target_seqs=5
):

    query_fasta = str(query_fasta)
    database = str(database)
    output_file = str(output_file)

    print()
    print("=" * 70)
    print("RUNNING BLASTP — SWISSPROT")
    print("=" * 70)

    print("Query:")
    print(query_fasta)

    print("Database:")
    print(database)

    print("Threads:")
    print(threads)

    if not os.path.isfile(query_fasta):
        raise FileNotFoundError(
            f"Query FASTA not found: {query_fasta}"
        )

    if not os.path.exists(database + ".pin"):
        raise FileNotFoundError(
            f"BLAST protein database not found: "
            f"{database}.pin"
        )

    output_parent = Path(output_file).parent

    output_parent.mkdir(
        parents=True,
        exist_ok=True
    )

    command = [
        "blastp",

        "-query",
        query_fasta,

        "-db",
        database,

        "-out",
        output_file,

        "-outfmt",
        "6 qseqid sacc stitle pident length qlen qstart qend evalue bitscore qcovs",

        "-max_target_seqs",
        str(max_target_seqs),

        "-max_hsps",
        "1",

        "-evalue",
        str(evalue),

        "-num_threads",
        str(threads)
    ]

    print()
    print("Command:")
    print(" ".join(command))

    subprocess.run(
        command,
        check=True
    )

    print()
    print("BLASTP completed successfully.")

    if os.path.isfile(output_file):

        with open(
            output_file,
            "r",
            errors="replace"
        ) as f:

            rows = sum(
                1
                for line in f
                if line.strip()
            )

        print(
            f"BLAST rows: {rows:,}"
        )

    print("=" * 70)

    return output_file


# ============================================================
# LOAD BLAST RESULTS
# ============================================================

def load_blast_results(
    blast_file
):

    results = []

    if not os.path.isfile(blast_file):

        raise FileNotFoundError(
            f"BLAST result not found: {blast_file}"
        )

    with open(
        blast_file,
        "r",
        errors="replace"
    ) as f:

        for line in f:

            line = line.rstrip("\n")

            if not line.strip():
                continue

            fields = line.split("\t")

            if len(fields) < 11:
                continue

            results.append({
                "qseqid": fields[0],
                "sacc": fields[1],
                "stitle": fields[2],
                "pident": float(fields[3]),
                "length": int(fields[4]),
                "qlen": int(fields[5]),
                "qstart": int(fields[6]),
                "qend": int(fields[7]),
                "evalue": float(fields[8]),
                "bitscore": float(fields[9]),
                "qcovs": float(fields[10])
            })

    return results


# ============================================================
# BEST BLAST HIT
# ============================================================

def best_blast_hits(
    results
):

    best = {}

    for row in results:

        protein = row["qseqid"]

        if protein not in best:

            best[protein] = row

            continue

        current = best[protein]

        # Prefer:
        # 1. Higher bitscore
        # 2. Lower e-value
        # 3. Higher coverage
        # 4. Higher identity

        if row["bitscore"] > current["bitscore"]:

            best[protein] = row

        elif (
            row["bitscore"] == current["bitscore"]
            and row["evalue"] < current["evalue"]
        ):

            best[protein] = row

        elif (
            row["bitscore"] == current["bitscore"]
            and row["evalue"] == current["evalue"]
            and row["qcovs"] > current["qcovs"]
        ):

            best[protein] = row

        elif (
            row["bitscore"] == current["bitscore"]
            and row["evalue"] == current["evalue"]
            and row["qcovs"] == current["qcovs"]
            and row["pident"] > current["pident"]
        ):

            best[protein] = row

    return best


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    import sys

    if len(sys.argv) < 3:

        print()
        print(
            "Usage:"
        )

        print(
            "python3 modules/blast_annotation.py "
            "protein.faa blast_database"
        )

        sys.exit(1)

    query = sys.argv[1]
    database = sys.argv[2]

    output = (
        "/tmp/FusariumAnnotator_BLAST_test.tsv"
    )

    run_blast(
        query,
        database,
        output,
        threads=4
    )

    results = load_blast_results(
        output
    )

    best = best_blast_hits(
        results
    )

    print()
    print("=" * 70)
    print("BLAST TEST SUCCESS")
    print("=" * 70)

    print(
        f"BLAST rows: {len(results):,}"
    )

    print(
        f"Best hits: {len(best):,}"
    )

    print(
        f"Output: {output}"
    )

    print("=" * 70)
