#!/usr/bin/env python3

# ================================================================
# FINAL FUSARIUM TE + RIP MASTER RESULTS TABLE
#
# Purpose:
#   Combine already-completed genome, EarlGrey TE and RIPCAL
#   results for all genomes into one permanent master dataset.
#
# INPUTS
# ------------------------------------------------
# Genome FASTA:
#   /mnt/d/genomes_clean/*.fna
#   /mnt/d/genomes_clean/*.fa
#   /mnt/d/genomes_clean/*.fasta
#
# TE:
#   TE_analysis/<GENOME>/**/<GENOME>.filteredRepeats.bed
#
# RIP:
#   <GENOME>_RIP_analysis/<GENOME>_RIP.bed
#   <GENOME>_RIP_analysis/<GENOME>_LRAR.bed
#   <GENOME>_RIP_analysis/<GENOME>_RIP_TE_overlap.txt
#
#   Also supports:
#   <GENOME>/RIP_analysis/<GENOME>_RIP.bed
#   <GENOME>/RIP_analysis/<GENOME>_LRAR.bed
#
# OUTPUTS
# ------------------------------------------------
#   TE_RIP_Master_Results.csv
#   TE_RIP_Master_Results.xlsx
#   TE_RIP_Analysis_Metadata.txt
#
# IMPORTANT:
#   This script DOES NOT rerun EarlGrey or RIPCAL.
#   It reads the results already generated.
# ================================================================

import os
import glob
import re
import pandas as pd


# ================================================================
# 1. PATHS
# ================================================================

BASE = "/mnt/d/genomes_clean"

TE_BASE = os.path.join(BASE, "TE_analysis")

OUTPUT_CSV = os.path.join(
    BASE, "TE_RIP_Master_Results.csv"
)

OUTPUT_XLSX = os.path.join(
    BASE, "TE_RIP_Master_Results.xlsx"
)

OUTPUT_METADATA = os.path.join(
    BASE, "TE_RIP_Analysis_Metadata.txt"
)


# ================================================================
# 2. HELPER FUNCTIONS
# ================================================================

def get_genome_name(filepath):
    name = os.path.basename(filepath)
    return re.sub(
        r"\.(fna|fa|fasta)$",
        "",
        name,
        flags=re.IGNORECASE
    )


def fasta_stats(filepath):
    total_bp = 0
    sequence_count = 0

    try:
        with open(filepath, "r", errors="ignore") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                if line.startswith(">"):
                    sequence_count += 1
                else:
                    total_bp += len(line)

    except Exception as e:
        print(f"WARNING: Cannot read FASTA: {filepath}")
        print(e)

    return total_bp, sequence_count


def bed_stats(filepath):
    interval_count = 0
    total_length = 0

    if not filepath or not os.path.isfile(filepath):
        return 0, 0

    try:
        with open(filepath, "r", errors="ignore") as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                fields = line.split("\t")

                if len(fields) < 3:
                    continue

                try:
                    start = int(float(fields[1]))
                    end = int(float(fields[2]))
                except (ValueError, TypeError):
                    continue

                length = end - start

                if length < 0:
                    continue

                interval_count += 1
                total_length += length

    except Exception as e:
        print(f"WARNING: Cannot read BED: {filepath}")
        print(e)

    return interval_count, total_length


def count_nonempty_lines(filepath):
    if not filepath or not os.path.isfile(filepath):
        return 0

    count = 0

    try:
        with open(filepath, "r", errors="ignore") as f:
            for line in f:
                if line.strip():
                    count += 1
    except Exception:
        pass

    return count


# ================================================================
# 3. FIND TE BED
# ================================================================

def find_te_bed(genome):
    genome_te_dir = os.path.join(TE_BASE, genome)

    if not os.path.isdir(genome_te_dir):
        return None

    preferred_pattern = os.path.join(
        genome_te_dir,
        "**",
        "looseMerge",
        f"{genome}.filteredRepeats.bed"
    )

    preferred = glob.glob(
        preferred_pattern,
        recursive=True
    )

    if preferred:
        return sorted(preferred)[0]

    fallback_pattern = os.path.join(
        genome_te_dir,
        "**",
        f"{genome}.filteredRepeats.bed"
    )

    fallback = glob.glob(
        fallback_pattern,
        recursive=True
    )

    if fallback:
        return sorted(fallback)[0]

    return None


# ================================================================
# 4. FIND RIP DIRECTORY
# ================================================================

def find_rip_directory(genome):
    primary = os.path.join(
        BASE,
        f"{genome}_RIP_analysis"
    )

    if os.path.isdir(primary):
        return primary

    alternative = os.path.join(
        BASE,
        genome,
        "RIP_analysis"
    )

    if os.path.isdir(alternative):
        return alternative

    return None


# ================================================================
# 5. FIND ALL GENOMES
# ================================================================

genome_files = []

for extension in ["*.fna", "*.fa", "*.fasta"]:
    genome_files.extend(
        glob.glob(
            os.path.join(BASE, extension)
        )
    )

genome_files = sorted(set(genome_files))


# ================================================================
# 6. START
# ================================================================

print()
print("=" * 72)
print("        FINAL FUSARIUM TE + RIP MASTER TABLE")
print("=" * 72)
print()

print(f"Working directory : {BASE}")
print(f"Genome FASTA files : {len(genome_files)}")
print()

if len(genome_files) == 0:
    print("ERROR: No genome FASTA files found.")
    raise SystemExit(1)


# ================================================================
# 7. PROCESS GENOMES
# ================================================================

results = []

for index, fasta in enumerate(genome_files, start=1):

    genome = get_genome_name(fasta)

    print("=" * 72)
    print(f"[{index}/{len(genome_files)}] {genome}")
    print("=" * 72)

    # ============================================================
    # GENOME STATISTICS
    # ============================================================

    genome_bp, scaffold_count = fasta_stats(fasta)
    genome_mb = genome_bp / 1_000_000

    # ============================================================
    # TE
    # ============================================================

    te_bed = find_te_bed(genome)

    te_interval_count, te_total_bp = bed_stats(te_bed)

    if genome_bp > 0:
        te_percent = (te_total_bp / genome_bp) * 100
    else:
        te_percent = 0

    te_status = "Complete" if te_bed else "Missing"

    # ============================================================
    # RIP DIRECTORY
    # ============================================================

    rip_dir = find_rip_directory(genome)

    if rip_dir:
        rip_bed = os.path.join(
            rip_dir,
            f"{genome}_RIP.bed"
        )

        lrar_bed = os.path.join(
            rip_dir,
            f"{genome}_LRAR.bed"
        )

        rip_regions_file = os.path.join(
            rip_dir,
            f"{genome}_RIP_regions.tsv"
        )

        rip_te_overlap = os.path.join(
            rip_dir,
            f"{genome}_RIP_TE_overlap.txt"
        )

    else:
        rip_bed = None
        lrar_bed = None
        rip_regions_file = None
        rip_te_overlap = None

    # ============================================================
    # RIP STATISTICS
    # ============================================================

    rip_count, rip_total_bp = bed_stats(rip_bed)
    lrar_count, lrar_total_bp = bed_stats(lrar_bed)

    if genome_bp > 0:
        rip_percent = (rip_total_bp / genome_bp) * 100
        lrar_percent = (lrar_total_bp / genome_bp) * 100
    else:
        rip_percent = 0
        lrar_percent = 0

    # ============================================================
    # RIP-TE OVERLAP
    # ============================================================

    overlap_records = count_nonempty_lines(
        rip_te_overlap
    )

    if lrar_count > 0:
        lrar_overlap_percent = (
            overlap_records / lrar_count
        ) * 100
    else:
        lrar_overlap_percent = 0

    # ============================================================
    # RIP STATUS
    # ============================================================

    if (
        rip_bed
        and lrar_bed
        and os.path.isfile(rip_bed)
        and os.path.isfile(lrar_bed)
    ):
        rip_status = "Complete"
    else:
        rip_status = "Missing"

    # ============================================================
    # BOTH STATUS
    # ============================================================

    if (
        te_status == "Complete"
        and rip_status == "Complete"
    ):
        overall_status = "Complete"
    else:
        overall_status = "Check"

    # ============================================================
    # PRINT CURRENT RESULT
    # ============================================================

    print(f"Genome size       : {genome_mb:.3f} Mb")
    print(f"Scaffolds/contigs : {scaffold_count}")
    print(f"TE intervals      : {te_interval_count}")
    print(f"TE length         : {te_total_bp:,} bp")
    print(f"TE % genome       : {te_percent:.3f}%")
    print(f"RIP windows       : {rip_count}")
    print(f"RIP length        : {rip_total_bp:,} bp")
    print(f"RIP % genome      : {rip_percent:.3f}%")
    print(f"LRAR count        : {lrar_count}")
    print(f"LRAR length       : {lrar_total_bp:,} bp")
    print(f"LRAR % genome     : {lrar_percent:.3f}%")
    print(f"RIP-TE overlap    : {overlap_records}")
    print(f"TE status         : {te_status}")
    print(f"RIP status        : {rip_status}")
    print(f"Overall status    : {overall_status}")

    # ============================================================
    # STORE RESULT
    # ============================================================

    results.append({

        "Genome": genome,

        "Genome_FASTA": fasta,

        "Genome_size_bp": genome_bp,

        "Genome_size_Mb": round(
            genome_mb, 3
        ),

        "Scaffold_or_contig_count": scaffold_count,

        "TE_status": te_status,

        "TE_BED": (
            te_bed if te_bed else ""
        ),

        "TE_interval_count": te_interval_count,

        "TE_total_length_bp": te_total_bp,

        "TE_percent_genome": round(
            te_percent, 3
        ),

        "RIP_status": rip_status,

        "RIP_directory": (
            rip_dir if rip_dir else ""
        ),

        "RIP_BED": (
            rip_bed
            if rip_bed and os.path.isfile(rip_bed)
            else ""
        ),

        "RIP_window_count": rip_count,

        "RIP_total_length_bp": rip_total_bp,

        "RIP_percent_genome": round(
            rip_percent, 3
        ),

        "LRAR_count": lrar_count,

        "LRAR_total_length_bp": lrar_total_bp,

        "LRAR_percent_genome": round(
            lrar_percent, 3
        ),

        "RIP_TE_overlap_records": overlap_records,

        "LRAR_with_TE_overlap_percent": round(
            lrar_overlap_percent, 3
        ),

        "LRAR_BED": (
            lrar_bed
            if lrar_bed and os.path.isfile(lrar_bed)
            else ""
        ),

        "RIP_regions_TSV": (
            rip_regions_file
            if rip_regions_file
            and os.path.isfile(rip_regions_file)
            else ""
        ),

        "RIP_TE_overlap_file": (
            rip_te_overlap
            if rip_te_overlap
            and os.path.isfile(rip_te_overlap)
            else ""
        ),

        "Overall_status": overall_status
    })


# ================================================================
# 8. DATAFRAME
# ================================================================

df = pd.DataFrame(results)

df = df.sort_values(
    by="Genome"
).reset_index(drop=True)


# ================================================================
# 9. SAVE CSV
# ================================================================

df.to_csv(
    OUTPUT_CSV,
    index=False
)

print()
print(f"CSV saved: {OUTPUT_CSV}")


# ================================================================
# 10. SAVE EXCEL
# ================================================================

with pd.ExcelWriter(
    OUTPUT_XLSX,
    engine="openpyxl"
) as writer:

    # MASTER
    df.to_excel(
        writer,
        sheet_name="TE_RIP_Master",
        index=False
    )

    # CLEAN TABLE
    compact_columns = [
        "Genome",
        "Genome_size_Mb",
        "Scaffold_or_contig_count",
        "TE_interval_count",
        "TE_total_length_bp",
        "TE_percent_genome",
        "RIP_window_count",
        "RIP_total_length_bp",
        "RIP_percent_genome",
        "LRAR_count",
        "LRAR_total_length_bp",
        "LRAR_percent_genome",
        "RIP_TE_overlap_records",
        "LRAR_with_TE_overlap_percent",
        "Overall_status"
    ]

    df[compact_columns].to_excel(
        writer,
        sheet_name="Compact_Results",
        index=False
    )

    # FILE CHECK
    check_columns = [
        "Genome",
        "TE_status",
        "RIP_status",
        "Overall_status",
        "TE_BED",
        "RIP_BED",
        "LRAR_BED",
        "RIP_regions_TSV",
        "RIP_TE_overlap_file"
    ]

    df[check_columns].to_excel(
        writer,
        sheet_name="File_Check",
        index=False
    )

    # INCOMPLETE
    incomplete = df[
        df["Overall_status"] != "Complete"
    ]

    incomplete.to_excel(
        writer,
        sheet_name="Incomplete",
        index=False
    )

print(f"Excel saved: {OUTPUT_XLSX}")


# ================================================================
# 11. METADATA FILE
# ================================================================

with open(
    OUTPUT_METADATA,
    "w"
) as meta:

    meta.write(
        "FUSARIUM TE + RIP MASTER RESULTS\n"
    )

    meta.write(
        "=================================\n\n"
    )

    meta.write(
        "Purpose:\n"
    )

    meta.write(
        "Combined genome-level TE and RIP results "
        "for downstream comparative analysis.\n\n"
    )

    meta.write(
        "Genome input:\n"
    )

    meta.write(
        "/mnt/d/genomes_clean/*.fna, *.fa, *.fasta\n\n"
    )

    meta.write(
        "TE source:\n"
    )

    meta.write(
        "EarlGrey filteredRepeats BED from "
        "mergedRepeats/looseMerge where available.\n\n"
    )

    meta.write(
        "RIP source:\n"
    )

    meta.write(
        "RIPCAL *_RIP.bed and *_LRAR.bed results.\n\n"
    )

    meta.write(
        "RIPCAL parameters used:\n"
    )

    meta.write(
        "Window length = 1000 bp\n"
    )

    meta.write(
        "Window increment = 500 bp\n\n"
    )

    meta.write(
        "TE percentage:\n"
    )

    meta.write(
        "TE total BED-covered length / genome size × 100\n\n"
    )

    meta.write(
        "RIP percentage:\n"
    )

    meta.write(
        "RIP BED-covered length / genome size × 100\n\n"
    )

    meta.write(
        "LRAR percentage:\n"
    )

    meta.write(
        "LRAR BED-covered length / genome size × 100\n\n"
    )

    meta.write(
        "Important:\n"
    )

    meta.write(
        "This master-table script does not rerun EarlGrey "
        "or RIPCAL. It reads previously generated results.\n"
    )


# ================================================================
# 12. FINAL SUMMARY
# ================================================================

total = len(df)

te_complete = int(
    (df["TE_status"] == "Complete").sum()
)

rip_complete = int(
    (df["RIP_status"] == "Complete").sum()
)

both_complete = int(
    (
        (df["TE_status"] == "Complete") &
        (df["RIP_status"] == "Complete")
    ).sum()
)

incomplete_count = int(
    (df["Overall_status"] != "Complete").sum()
)

print()
print("=" * 72)
print("FINAL SUMMARY")
print("=" * 72)

print(f"Total genomes processed : {total}")
print(f"TE complete             : {te_complete}")
print(f"RIP complete            : {rip_complete}")
print(f"Both complete           : {both_complete}")
print(f"Need checking           : {incomplete_count}")

print()
print("OUTPUT FILES")
print(OUTPUT_CSV)
print(OUTPUT_XLSX)
print(OUTPUT_METADATA)

print()
print("=" * 72)
print("DONE")
print("=" * 72)
