#!/usr/bin/env python3

# ============================================================
# KAAS → KEGG PATHWAY ANALYZER
# ============================================================
#
# Purpose:
#   Download KAAS query.ko results, compare them with an
#   original FASTA file, extract KO assignments, retrieve
#   KEGG KO information and pathways, and generate Excel.
#
# Input:
#   1. KAAS result URL
#   2. Original FASTA file
#
# Output:
#   KAAS_KEGG_Results/
#
# Main Excel:
#   KAAS_KEGG_Results.xlsx
#
# ============================================================

import os
import re
import sys
import time
import pickle
import argparse
from pathlib import Path
from urllib.parse import urljoin

import requests
import pandas as pd


# ============================================================
# CONSTANTS
# ============================================================

KEGG_BASE = "https://rest.kegg.jp"

USER_AGENT = (
    "Fusarium-Comparative-Genomics-KAAS-KEGG-Analyzer/1.0 "
    "(research reproducibility workflow)"
)


# ============================================================
# PRINT HEADER
# ============================================================

def print_header():
    print()
    print("=" * 72)
    print("        KAAS → KEGG PATHWAY ANALYZER")
    print("=" * 72)
    print("Automated fungal proteome KO and pathway annotation")
    print("=" * 72)
    print()


# ============================================================
# DOWNLOAD KAAS QUERY.KO
# ============================================================

def download_kaas_result(kaas_url, output_file):

    print("STEP 1: Downloading KAAS result")
    print("-" * 72)
    print(f"KAAS URL:")
    print(kaas_url)
    print()

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    # --------------------------------------------------------
    # First request: KAAS result page
    # --------------------------------------------------------

    response = session.get(
        kaas_url,
        timeout=120
    )

    response.raise_for_status()

    html = response.text

    # --------------------------------------------------------
    # Find query.ko download link
    # --------------------------------------------------------

    patterns = [
        r'href="([^"]*query\.ko)"',
        r'href=\'([^\']*query\.ko)\'',
        r'(\/tools\/kaas\/files\/dl\/[^"\']+\/query\.ko)',
        r'(\/kaas-bin\/[^"\']*query\.ko)'
    ]

    ko_url = None

    for pattern in patterns:

        match = re.search(
            pattern,
            html,
            flags=re.IGNORECASE
        )

        if match:

            ko_url = match.group(1)

            if ko_url.startswith("/"):
                ko_url = urljoin(
                    "https://www.genome.jp",
                    ko_url
                )

            break

    # --------------------------------------------------------
    # If not found, construct URL from job ID/key
    # --------------------------------------------------------

    if ko_url is None:

        id_match = re.search(
            r'[?&]id=(\d+)',
            kaas_url
        )

        key_match = re.search(
            r'[?&]key=([^&]+)',
            kaas_url
        )

        if id_match:

            job_id = id_match.group(1)

            ko_url = (
                f"https://www.genome.jp/tools/kaas/files/"
                f"dl/{job_id}/query.ko"
            )

        else:

            raise RuntimeError(
                "Could not identify the KAAS query.ko download URL."
            )

    print("Detected query.ko URL:")
    print(ko_url)
    print()

    # --------------------------------------------------------
    # Download query.ko
    # --------------------------------------------------------

    r = session.get(
        ko_url,
        timeout=300
    )

    r.raise_for_status()

    # Check that we did not receive an HTML error page
    if r.text.lstrip().lower().startswith("<!doctype"):
        raise RuntimeError(
            "KAAS returned an HTML page instead of query.ko."
        )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(r.text)

    size_mb = os.path.getsize(output_file) / (1024 * 1024)

    print(
        f"KAAS query.ko saved: {output_file}"
    )

    print(
        f"File size: {size_mb:.2f} MB"
    )

    print()

    return output_file


# ============================================================
# READ FASTA IDS
# ============================================================

def read_fasta_ids(fasta_file):

    print("STEP 2: Reading FASTA")
    print("-" * 72)

    fasta_ids = []

    with open(
        fasta_file,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:

        for line in f:

            if line.startswith(">"):

                header = line[1:].strip()

                # First token is treated as protein ID
                protein_id = header.split()[0]

                if protein_id:
                    fasta_ids.append(protein_id)

    fasta_set = set(fasta_ids)

    print(
        f"FASTA sequences       : {len(fasta_ids):,}"
    )

    print(
        f"Unique FASTA IDs      : {len(fasta_set):,}"
    )

    print()

    return fasta_ids, fasta_set


# ============================================================
# PARSE KAAS QUERY.KO
# ============================================================

def parse_kaas(kaas_file):

    print("STEP 3: Reading KAAS query.ko")
    print("-" * 72)

    records = []

    total_lines = 0
    assigned = 0

    with open(
        kaas_file,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:

        for line in f:

            line = line.rstrip()

            if not line:
                continue

            total_lines += 1

            # ------------------------------------------------
            # KAAS format:
            #
            # Fgram_0343|g1.t1
            # Fgram_0343|g9.t1        K09967
            #
            # Protein ID is first field.
            # ------------------------------------------------

            protein_id = line.split()[0]

            ko_match = re.search(
                r"\bK\d{5}\b",
                line
            )

            ko_id = ""

            if ko_match:

                ko_id = ko_match.group(0)

                assigned += 1

            records.append(
                {
                    "Protein_ID": protein_id,
                    "KO": ko_id
                }
            )

    df = pd.DataFrame(records)

    unique_ids = df["Protein_ID"].nunique()

    assigned_df = df[
        df["KO"].astype(str).str.match(
            r"^K\d{5}$"
        )
    ]

    unique_kos = sorted(
        assigned_df["KO"].unique()
    )

    print(
        f"KAAS total lines      : {total_lines:,}"
    )

    print(
        f"Unique protein IDs    : {unique_ids:,}"
    )

    print(
        f"Proteins with KO      : {len(assigned_df):,}"
    )

    print(
        f"Proteins without KO   : "
        f"{total_lines - len(assigned_df):,}"
    )

    print(
        f"Unique KO IDs         : {len(unique_kos):,}"
    )

    print()

    return df, unique_kos


# ============================================================
# FASTA ↔ KAAS MATCHING
# ============================================================

def compare_fasta_kaas(
    fasta_ids,
    fasta_set,
    kaas_df,
    output_dir
):

    print("STEP 4: FASTA ↔ KAAS ID matching")
    print("-" * 72)

    kaas_set = set(
        kaas_df["Protein_ID"]
    )

    fasta_missing = sorted(
        fasta_set - kaas_set
    )

    kaas_not_fasta = sorted(
        kaas_set - fasta_set
    )

    matching = fasta_set & kaas_set

    print(
        f"FASTA IDs             : {len(fasta_set):,}"
    )

    print(
        f"KAAS IDs              : {len(kaas_set):,}"
    )

    print(
        f"Matching IDs          : {len(matching):,}"
    )

    print(
        f"FASTA missing KAAS    : {len(fasta_missing):,}"
    )

    print(
        f"KAAS not in FASTA     : {len(kaas_not_fasta):,}"
    )

    percentage = (
        len(matching) / len(fasta_set) * 100
        if fasta_set
        else 0
    )

    print(
        f"FASTA represented     : {percentage:.2f}%"
    )

    print()

    # --------------------------------------------------------
    # Save difference files
    # --------------------------------------------------------

    missing_file = (
        output_dir /
        "FASTA_missing_in_KAAS.txt"
    )

    not_fasta_file = (
        output_dir /
        "KAAS_not_in_FASTA.txt"
    )

    with open(
        missing_file,
        "w",
        encoding="utf-8"
    ) as f:

        for x in fasta_missing:
            f.write(x + "\n")

    with open(
        not_fasta_file,
        "w",
        encoding="utf-8"
    ) as f:

        for x in kaas_not_fasta:
            f.write(x + "\n")

    return {
        "fasta_ids": len(fasta_set),
        "kaas_ids": len(kaas_set),
        "matching": len(matching),
        "missing": len(fasta_missing),
        "not_in_fasta": len(kaas_not_fasta),
        "percentage": percentage
    }


# ============================================================
# KEGG CACHE
# ============================================================

def load_cache(cache_file):

    if cache_file.exists():

        try:

            with open(
                cache_file,
                "rb"
            ) as f:

                cache = pickle.load(f)

            print(
                f"Existing KEGG cache loaded: "
                f"{len(cache):,} KOs"
            )

            return cache

        except Exception as e:

            print(
                f"Warning: cache could not be loaded: {e}"
            )

    return {}


def save_cache(cache, cache_file):

    temporary = cache_file.with_suffix(
        ".tmp"
    )

    with open(
        temporary,
        "wb"
    ) as f:

        pickle.dump(
            cache,
            f,
            protocol=pickle.HIGHEST_PROTOCOL
        )

    temporary.replace(cache_file)


# ============================================================
# PARSE KEGG FLAT FILE
# ============================================================

def parse_kegg_record(text):

    enzyme = ""
    ec_numbers = []
    pathways = []

    current_field = None

    for line in text.splitlines():

        if not line.strip():
            continue

        # KEGG field starts in columns 1-12
        field = line[:12].strip()
        value = line[12:].strip()

        if field:
            current_field = field

        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        if field == "NAME":

            enzyme = value

        # ----------------------------------------------------
        # PATHWAY
        # ----------------------------------------------------

        elif field == "PATHWAY":

            parts = value.split(
                maxsplit=1
            )

            if len(parts) == 2:

                pathway_id = parts[0]
                pathway_name = parts[1]

                if pathway_id.startswith("map"):

                    pathways.append(
                        (
                            pathway_id,
                            pathway_name
                        )
                    )

        # ----------------------------------------------------
        # CLASS can contain EC numbers in some records
        # ----------------------------------------------------

        elif field == "CLASS":

            ec_matches = re.findall(
                r"\bEC[: ]+([0-9.\-]+)",
                value
            )

            ec_numbers.extend(
                ec_matches
            )

        # ----------------------------------------------------
        # Some KEGG records include EC in NAME
        # ----------------------------------------------------

        if "EC:" in line:

            matches = re.findall(
                r"EC:([0-9.\-]+)",
                line
            )

            ec_numbers.extend(
                matches
            )

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    ec_numbers = sorted(
        set(ec_numbers)
    )

    pathways = list(
        dict.fromkeys(pathways)
    )

    return {
        "Enzyme": enzyme,
        "EC": "; ".join(ec_numbers),
        "Pathways": pathways
    }


# ============================================================
# FETCH KEGG KO
# ============================================================

def fetch_kegg_batch(
    ko_batch,
    session
):

    # KEGG accepts multiple entries joined by +
    query = "+".join(
        f"ko:{ko}"
        for ko in ko_batch
    )

    url = f"{KEGG_BASE}/get/{query}"

    response = session.get(
        url,
        timeout=180
    )

    response.raise_for_status()

    return response.text


# ============================================================
# KEGG ANNOTATION
# ============================================================

def annotate_kos(
    unique_kos,
    cache_file,
    batch_size=10,
    delay=1.0
):

    print("STEP 5: KEGG KO annotation")
    print("-" * 72)

    print(
        f"Unique KOs to annotate : {len(unique_kos):,}"
    )

    print(
        f"KEGG batch size        : {batch_size}"
    )

    print(
        f"Delay between batches  : {delay} seconds"
    )

    print()

    cache = load_cache(
        cache_file
    )

    session = requests.Session()

    session.headers.update(
        {
            "User-Agent": USER_AGENT
        }
    )

    missing_kos = [
        ko
        for ko in unique_kos
        if ko not in cache
    ]

    print(
        f"Already cached         : "
        f"{len(unique_kos) - len(missing_kos):,}"
    )

    print(
        f"Need KEGG lookup       : "
        f"{len(missing_kos):,}"
    )

    print()

    total_batches = (
        (len(missing_kos) + batch_size - 1)
        // batch_size
    )

    for start in range(
        0,
        len(missing_kos),
        batch_size
    ):

        batch = missing_kos[
            start:start + batch_size
        ]

        batch_number = (
            start // batch_size
        ) + 1

        print(
            f"[Batch {batch_number}/{total_batches}] "
            f"{batch[0]} → {batch[-1]}",
            end=" ... ",
            flush=True
        )

        try:

            text = fetch_kegg_batch(
                batch,
                session
            )

            # ------------------------------------------------
            # Split records at "///"
            # ------------------------------------------------

            records = text.split(
                "///"
            )

            found = 0

            for record in records:

                record = record.strip()

                if not record:
                    continue

                # Find KO ID
                ko_match = re.search(
                    r"ENTRY\s+(K\d{5})",
                    record
                )

                if not ko_match:

                    # Alternative format
                    ko_match = re.search(
                        r"ENTRY\s+([A-Z]?\d{5})",
                        record
                    )

                if not ko_match:
                    continue

                ko_id = ko_match.group(1)

                parsed = parse_kegg_record(
                    record
                )

                cache[ko_id] = parsed

                found += 1

            print(
                f"OK ({found} records)"
            )

        except Exception as e:

            print(
                f"ERROR: {e}"
            )

        # ----------------------------------------------------
        # Save cache after every batch
        # ----------------------------------------------------

        save_cache(
            cache,
            cache_file
        )

        if start + batch_size < len(missing_kos):

            time.sleep(
                delay
            )

    print()

    print(
        f"KEGG cache now contains: "
        f"{len(cache):,} KOs"
    )

    print()

    return cache


# ============================================================
# BUILD KEGG TABLE
# ============================================================

def build_kegg_table(
    unique_kos,
    cache
):

    rows = []

    for ko in unique_kos:

        info = cache.get(
            ko,
            {
                "Enzyme": "",
                "EC": "",
                "Pathways": []
            }
        )

        pathways = info.get(
            "Pathways",
            []
        )

        # ----------------------------------------------------
        # Keep one row even if no pathway exists
        # ----------------------------------------------------

        if not pathways:

            rows.append(
                [
                    ko,
                    info.get(
                        "Enzyme",
                        ""
                    ),
                    info.get(
                        "EC",
                        ""
                    ),
                    "",
                    ""
                ]
            )

        else:

            for pathway_id, pathway_name in pathways:

                rows.append(
                    [
                        ko,
                        info.get(
                            "Enzyme",
                            ""
                        ),
                        info.get(
                            "EC",
                            ""
                        ),
                        pathway_id,
                        pathway_name
                    ]
                )

    return pd.DataFrame(
        rows,
        columns=[
            "KO",
            "Enzyme",
            "EC",
            "PathwayID",
            "PathwayName"
        ]
    )


# ============================================================
# BUILD PROTEIN → KO → PATHWAY TABLE
# ============================================================

def build_protein_pathway_table(
    kaas_df,
    kegg_df
):

    assigned = kaas_df[
        kaas_df["KO"].astype(str).str.match(
            r"^K\d{5}$"
        )
    ].copy()

    # --------------------------------------------------------
    # Merge protein → KO with KEGG annotation
    # --------------------------------------------------------

    merged = assigned.merge(
        kegg_df,
        on="KO",
        how="left"
    )

    return merged


# ============================================================
# SUMMARIES
# ============================================================

def build_summaries(
    kaas_df,
    kegg_df,
    protein_pathway_df
):

    # --------------------------------------------------------
    # KO summary
    # --------------------------------------------------------

    ko_summary = (
        kaas_df[
            kaas_df["KO"].astype(str).str.match(
                r"^K\d{5}$"
            )
        ]
        .groupby("KO")
        .size()
        .reset_index(
            name="Protein_Count"
        )
        .sort_values(
            "Protein_Count",
            ascending=False
        )
    )

    ko_summary = ko_summary.merge(
        kegg_df[
            [
                "KO",
                "Enzyme",
                "EC"
            ]
        ].drop_duplicates("KO"),
        on="KO",
        how="left"
    )

    # --------------------------------------------------------
    # Pathway summary
    # --------------------------------------------------------

    pathway_data = kegg_df[
        kegg_df["PathwayID"].astype(str).str.startswith(
            "map"
        )
    ].copy()

    pathway_summary = (
        pathway_data
        .groupby(
            [
                "PathwayID",
                "PathwayName"
            ]
        )
        .agg(
            Unique_KOs=(
                "KO",
                "nunique"
            )
        )
        .reset_index()
        .sort_values(
            "Unique_KOs",
            ascending=False
        )
    )

    # --------------------------------------------------------
    # EC summary
    # --------------------------------------------------------

    ec_rows = []

    for _, row in kegg_df.iterrows():

        if not row["EC"]:
            continue

        for ec in str(
            row["EC"]
        ).split(";"):

            ec = ec.strip()

            if ec:

                ec_rows.append(
                    [
                        ec,
                        row["KO"]
                    ]
                )

    if ec_rows:

        ec_summary = pd.DataFrame(
            ec_rows,
            columns=[
                "EC",
                "KO"
            ]
        )

        ec_summary = (
            ec_summary
            .groupby("EC")
            .agg(
                Unique_KOs=(
                    "KO",
                    "nunique"
                )
            )
            .reset_index()
            .sort_values(
                "Unique_KOs",
                ascending=False
            )
        )

    else:

        ec_summary = pd.DataFrame(
            columns=[
                "EC",
                "Unique_KOs"
            ]
        )

    return (
        ko_summary,
        pathway_summary,
        ec_summary
    )


# ============================================================
# EXPORT EXCEL
# ============================================================

def export_excel(
    output_file,
    kaas_df,
    kegg_df,
    protein_pathway_df,
    ko_summary,
    pathway_summary,
    ec_summary,
    summary
):

    print("STEP 6: Writing Excel")
    print("-" * 72)

    with pd.ExcelWriter(
        output_file,
        engine="openpyxl"
    ) as writer:

        # ----------------------------------------------------
        # ALL PROTEINS + KO
        # ----------------------------------------------------

        kaas_df.to_excel(
            writer,
            sheet_name="All_Protein_KO",
            index=False
        )

        # ----------------------------------------------------
        # KO ANNOTATION
        # ----------------------------------------------------

        kegg_df.to_excel(
            writer,
            sheet_name="KO_Annotation",
            index=False
        )

        # ----------------------------------------------------
        # PROTEIN → KO → PATHWAY
        # ----------------------------------------------------

        protein_pathway_df.to_excel(
            writer,
            sheet_name="Pathway_Annotation",
            index=False
        )

        # ----------------------------------------------------
        # KO SUMMARY
        # ----------------------------------------------------

        ko_summary.to_excel(
            writer,
            sheet_name="KO_Summary",
            index=False
        )

        # ----------------------------------------------------
        # PATHWAY SUMMARY
        # ----------------------------------------------------

        pathway_summary.to_excel(
            writer,
            sheet_name="Pathway_Summary",
            index=False
        )

        # ----------------------------------------------------
        # EC SUMMARY
        # ----------------------------------------------------

        ec_summary.to_excel(
            writer,
            sheet_name="EC_Summary",
            index=False
        )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        summary.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )

    print(
        f"Excel saved: {output_file}"
    )

    print()


# ============================================================
# MAIN
# ============================================================

def main():

    print_header()

    parser = argparse.ArgumentParser(
        description=(
            "KAAS → KEGG pathway annotation "
            "pipeline for fungal proteomes."
        )
    )

    parser.add_argument(
        "--kaas-url",
        required=True,
        help="Completed KAAS result URL"
    )

    parser.add_argument(
        "--fasta",
        required=True,
        help="Original protein FASTA file"
    )

    parser.add_argument(
        "--output",
        default="KAAS_KEGG_Results",
        help="Output directory"
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of KOs per KEGG request"
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between KEGG requests"
    )

    args = parser.parse_args()

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    fasta_file = Path(
        args.fasta
    ).expanduser().resolve()

    if not fasta_file.exists():

        print(
            f"ERROR: FASTA file not found:\n{fasta_file}"
        )

        sys.exit(1)

    output_dir = Path(
        args.output
    ).expanduser().resolve()

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Output paths
    # --------------------------------------------------------

    kaas_file = (
        output_dir /
        "KAAS_query.ko"
    )

    fasta_ids_file = (
        output_dir /
        "FASTA_IDs.txt"
    )

    protein_ko_file = (
        output_dir /
        "Protein_KO.tsv"
    )

    kegg_annotation_file = (
        output_dir /
        "KEGG_KO_Annotation.tsv"
    )

    cache_file = (
        output_dir /
        "kegg_cache.pkl"
    )

    excel_file = (
        output_dir /
        "KAAS_KEGG_Results.xlsx"
    )

    # --------------------------------------------------------
    # STEP 1
    # --------------------------------------------------------

    download_kaas_result(
        args.kaas_url,
        kaas_file
    )

    # --------------------------------------------------------
    # STEP 2
    # --------------------------------------------------------

    fasta_ids, fasta_set = read_fasta_ids(
        fasta_file
    )

    with open(
        fasta_ids_file,
        "w",
        encoding="utf-8"
    ) as f:

        for protein_id in fasta_ids:
            f.write(
                protein_id + "\n"
            )

    # --------------------------------------------------------
    # STEP 3
    # --------------------------------------------------------

    kaas_df, unique_kos = parse_kaas(
        kaas_file
    )

    kaas_df.to_csv(
        protein_ko_file,
        sep="\t",
        index=False
    )

    # --------------------------------------------------------
    # STEP 4
    # --------------------------------------------------------

    comparison = compare_fasta_kaas(
        fasta_ids,
        fasta_set,
        kaas_df,
        output_dir
    )

    # --------------------------------------------------------
    # STEP 5
    # --------------------------------------------------------

    cache = annotate_kos(
        unique_kos,
        cache_file,
        batch_size=args.batch_size,
        delay=args.delay
    )

    kegg_df = build_kegg_table(
        unique_kos,
        cache
    )

    kegg_df.to_csv(
        kegg_annotation_file,
        sep="\t",
        index=False
    )

    # --------------------------------------------------------
    # STEP 6
    # --------------------------------------------------------

    protein_pathway_df = (
        build_protein_pathway_table(
            kaas_df,
            kegg_df
        )
    )

    (
        ko_summary,
        pathway_summary,
        ec_summary
    ) = build_summaries(
        kaas_df,
        kegg_df,
        protein_pathway_df
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    assigned = kaas_df[
        kaas_df["KO"].astype(str).str.match(
            r"^K\d{5}$"
        )
    ]

    summary = pd.DataFrame(
        [
            [
                "FASTA sequences",
                comparison["fasta_ids"]
            ],
            [
                "Unique FASTA IDs",
                comparison["fasta_ids"]
            ],
            [
                "KAAS protein IDs",
                comparison["kaas_ids"]
            ],
            [
                "Matching IDs",
                comparison["matching"]
            ],
            [
                "FASTA IDs missing in KAAS",
                comparison["missing"]
            ],
            [
                "KAAS IDs not in FASTA",
                comparison["not_in_fasta"]
            ],
            [
                "FASTA represented in KAAS (%)",
                round(
                    comparison["percentage"],
                    2
                )
            ],
            [
                "Proteins with KO",
                len(assigned)
            ],
            [
                "Proteins without KO",
                len(kaas_df) - len(assigned)
            ],
            [
                "Unique KO IDs",
                len(unique_kos)
            ],
            [
                "Unique pathways",
                pathway_summary["PathwayID"].nunique()
                if not pathway_summary.empty
                else 0
            ],
            [
                "Unique EC numbers",
                ec_summary["EC"].nunique()
                if not ec_summary.empty
                else 0
            ]
        ],
        columns=[
            "Metric",
            "Value"
        ]
    )

    # --------------------------------------------------------
    # Export Excel
    # --------------------------------------------------------

    export_excel(
        excel_file,
        kaas_df,
        kegg_df,
        protein_pathway_df,
        ko_summary,
        pathway_summary,
        ec_summary,
        summary
    )

    # --------------------------------------------------------
    # FINAL REPORT
    # --------------------------------------------------------

    print("=" * 72)
    print("                 ANALYSIS COMPLETE")
    print("=" * 72)

    print()
    print(
        f"FASTA proteins          : "
        f"{comparison['fasta_ids']:,}"
    )

    print(
        f"KAAS proteins           : "
        f"{comparison['kaas_ids']:,}"
    )

    print(
        f"Matching proteins       : "
        f"{comparison['matching']:,}"
    )

    print(
        f"Proteins with KO        : "
        f"{len(assigned):,}"
    )

    print(
        f"Proteins without KO     : "
        f"{len(kaas_df) - len(assigned):,}"
    )

    print(
        f"Unique KO IDs           : "
        f"{len(unique_kos):,}"
    )

    print(
        f"Unique pathways         : "
        f"{pathway_summary['PathwayID'].nunique()} "
        if not pathway_summary.empty
        else 0
    )

    print()
    print(
        "FINAL EXCEL:"
    )

    print(
        excel_file
    )

    print()
    print("=" * 72)


if __name__ == "__main__":
    main()
