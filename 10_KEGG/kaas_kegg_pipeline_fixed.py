#!/usr/bin/env python3
"""
KAAS -> KEGG Pathway Analyzer
=============================

Purpose
-------
Normalize KAAS protein->KO results from any of:
  1. KAAS query.ko / text file
  2. TSV / CSV
  3. Excel (.xlsx/.xls)
  4. Completed KAAS result URL (optional)

A protein FASTA is OPTIONAL and is used only for ID validation.
A KAAS URL is OPTIONAL and is used only when no local KAAS result file is supplied.

The pipeline:
  input -> normalized Protein_ID/KO table -> unique KOs
        -> KEGG cache -> KO annotation -> protein/pathway mapping
        -> KO/pathway/EC summaries -> Excel

The internal dataframe is always named kaas_df and has:
  Protein_ID, KO

This avoids the previous kaas_df/protein_ko mismatch.
"""

from __future__ import annotations

import argparse
import pickle
import re
import sys
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests


KEGG_BASE = "https://rest.kegg.jp"
USER_AGENT = (
    "Fusarium-Comparative-Genomics-KAAS-KEGG-Analyzer/2.0 "
    "(research reproducibility workflow)"
)


# ============================================================
# GENERAL HELPERS
# ============================================================

def print_header() -> None:
    print()
    print("=" * 72)
    print("             KAAS -> KEGG PATHWAY ANALYZER")
    print("=" * 72)
    print("Local KAAS / Excel / TSV / CSV input supported")
    print("FASTA and KAAS URL are optional")
    print("=" * 72)
    print()


def die(message: str, code: int = 1) -> None:
    print()
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(code)


def clean_text(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def is_valid_ko(value: Any) -> bool:
    return bool(re.fullmatch(r"K\d{5}", clean_text(value)))


def normalize_ko(value: Any) -> str:
    text = clean_text(value)
    match = re.search(r"\bK\d{5}\b", text)
    return match.group(0) if match else ""


def detect_column(columns, candidates):
    normalized = {
        re.sub(r"[^a-z0-9]+", "", str(c).lower()): c
        for c in columns
    }

    for candidate in candidates:
        key = re.sub(r"[^a-z0-9]+", "", candidate.lower())
        if key in normalized:
            return normalized[key]

    for c in columns:
        ck = re.sub(r"[^a-z0-9]+", "", str(c).lower())
        for candidate in candidates:
            key = re.sub(r"[^a-z0-9]+", "", candidate.lower())
            if key and key in ck:
                return c

    return None


# ============================================================
# KAAS URL DOWNLOAD
# ============================================================

def download_kaas_result(kaas_url: str, output_file: Path) -> Path:
    print("STEP 1: Downloading KAAS result")
    print("-" * 72)
    print(f"KAAS URL: {kaas_url}")
    print()

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    response = session.get(kaas_url, timeout=120)
    response.raise_for_status()

    html = response.text

    patterns = [
        r'href="([^"]*query\.ko)"',
        r"href='([^']*query\.ko)'",
        r'(\/tools\/kaas\/files\/dl\/[^"\']+\/query\.ko)',
        r'(\/kaas-bin\/[^"\']*query\.ko)',
    ]

    ko_url = None

    for pattern in patterns:
        match = re.search(pattern, html, flags=re.IGNORECASE)
        if match:
            ko_url = match.group(1)
            break

    if ko_url is None:
        # Sometimes the supplied URL is already the query.ko URL.
        if kaas_url.lower().endswith("query.ko"):
            ko_url = kaas_url
        else:
            raise RuntimeError(
                "Could not find query.ko download link in the supplied "
                "KAAS page. Download query.ko manually and use --input."
            )

    ko_url = requests.compat.urljoin(kaas_url, ko_url)

    print(f"KAAS query.ko URL: {ko_url}")

    ko_response = session.get(ko_url, timeout=300)
    ko_response.raise_for_status()

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_bytes(ko_response.content)

    print(f"KAAS query.ko saved: {output_file}")
    print(f"File size: {output_file.stat().st_size / (1024 * 1024):.2f} MB")
    print()

    return output_file


# ============================================================
# FASTA
# ============================================================

def read_fasta_ids(fasta_file: Path):
    print("STEP 2: Reading FASTA")
    print("-" * 72)

    fasta_ids = []

    with fasta_file.open(
        "r",
        encoding="utf-8",
        errors="replace",
    ) as handle:
        for line in handle:
            if line.startswith(">"):
                header = line[1:].strip()
                protein_id = header.split()[0]
                if protein_id:
                    fasta_ids.append(protein_id)

    fasta_set = set(fasta_ids)

    print(f"FASTA sequences       : {len(fasta_ids):,}")
    print(f"Unique FASTA IDs      : {len(fasta_set):,}")
    print()

    return fasta_ids, fasta_set


# ============================================================
# LOCAL INPUT READERS
# ============================================================

def parse_kaas_query_ko(kaas_file: Path) -> pd.DataFrame:
    """
    Parse native KAAS query.ko/text output.

    The first whitespace-delimited token is treated as Protein_ID.
    Any Kxxxxx token anywhere on the line is treated as the KO.
    """
    print("STEP 3: Reading KAAS query.ko")
    print("-" * 72)

    records = []
    total_lines = 0

    with kaas_file.open(
        "r",
        encoding="utf-8",
        errors="replace",
    ) as handle:
        for raw in handle:
            line = raw.strip()

            if not line:
                continue

            total_lines += 1
            protein_id = line.split()[0]
            ko_id = normalize_ko(line)

            records.append(
                {
                    "Protein_ID": protein_id,
                    "KO": ko_id,
                }
            )

    df = pd.DataFrame(records, columns=["Protein_ID", "KO"])

    return report_normalized_kaas(df, total_lines, "KAAS query.ko")


def read_tabular_input(input_file: Path) -> pd.DataFrame:
    suffix = input_file.suffix.lower()

    if suffix in {".xlsx", ".xls"}:
        print("Reading Excel input")
        print("-" * 72)

        sheets = pd.read_excel(
            input_file,
            sheet_name=None,
            engine="openpyxl" if suffix == ".xlsx" else None,
        )

        if not sheets:
            raise ValueError("Excel workbook contains no sheets.")

        # Prefer a sheet containing recognizable Protein/KO columns.
        selected_name = None
        selected_df = None

        for sheet_name, df in sheets.items():
            if df is None or df.empty:
                continue

            protein_col = detect_column(
                df.columns,
                [
                    "Protein_ID",
                    "Protein ID",
                    "Protein",
                    "Sequence_ID",
                    "Sequence ID",
                    "Gene_ID",
                    "Gene ID",
                    "ID",
                    "Query",
                    "Query_ID",
                    "Query ID",
                ],
            )
            ko_col = detect_column(
                df.columns,
                [
                    "KO",
                    "KO_ID",
                    "KO ID",
                    "KEGG_KO",
                    "KEGG KO",
                    "K number",
                    "K number",
                ],
            )

            if protein_col and ko_col:
                selected_name = sheet_name
                selected_df = df
                break

        if selected_df is None:
            # Fall back to the first non-empty sheet and infer columns.
            for sheet_name, df in sheets.items():
                if df is not None and not df.empty:
                    selected_name = sheet_name
                    selected_df = df
                    break

        if selected_df is None:
            raise ValueError("No non-empty sheet found in Excel workbook.")

        print(f"Excel sheet selected: {selected_name}")
        return normalize_tabular_dataframe(selected_df)

    if suffix in {".csv"}:
        print("Reading CSV input")
        print("-" * 72)
        df = pd.read_csv(input_file)
        return normalize_tabular_dataframe(df)

    print("Reading TSV/table input")
    print("-" * 72)

    # Try tab-separated first, then whitespace-separated.
    try:
        df = pd.read_csv(
            input_file,
            sep="\t",
            dtype=str,
            keep_default_na=False,
        )
    except Exception:
        df = pd.read_csv(
            input_file,
            sep=r"\s+",
            engine="python",
            dtype=str,
            keep_default_na=False,
        )

    return normalize_tabular_dataframe(df)


def normalize_tabular_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError("Input table is empty.")

    protein_col = detect_column(
        df.columns,
        [
            "Protein_ID",
            "Protein ID",
            "Protein",
            "Sequence_ID",
            "Sequence ID",
            "Gene_ID",
            "Gene ID",
            "ID",
            "Query",
            "Query_ID",
            "Query ID",
            "Target",
        ],
    )

    ko_col = detect_column(
        df.columns,
        [
            "KO",
            "KO_ID",
            "KO ID",
            "KEGG_KO",
            "KEGG KO",
            "K number",
            "K number",
            "KO_IDs",
            "KO IDs",
        ],
    )

    if protein_col is None or ko_col is None:
        raise ValueError(
            "Could not identify Protein_ID and KO columns in the table. "
            f"Found columns: {list(df.columns)}"
        )

    out = pd.DataFrame(
        {
            "Protein_ID": df[protein_col].map(clean_text),
            "KO": df[ko_col].map(normalize_ko),
        }
    )

    out = out[out["Protein_ID"] != ""].copy()

    return report_normalized_kaas(
        out,
        len(out),
        "tabular input",
    )


def report_normalized_kaas(
    df: pd.DataFrame,
    total_lines: int,
    source_name: str,
) -> pd.DataFrame:
    df = df[["Protein_ID", "KO"]].copy()

    # If duplicate Protein_ID rows exist, retain every distinct KO
    # but collapse exact duplicate rows.
    df = df.drop_duplicates(
        subset=["Protein_ID", "KO"],
        keep="first",
    ).reset_index(drop=True)

    unique_ids = df["Protein_ID"].nunique()
    assigned_df = df[df["KO"].map(is_valid_ko)].copy()
    unique_kos = sorted(assigned_df["KO"].unique())

    # A protein can occur multiple times if the source has multiple KO
    # assignments. For standard KAAS query.ko this is normally one row/protein.
    proteins_with_ko = assigned_df["Protein_ID"].nunique()

    print(f"Input source           : {source_name}")
    print(f"KAAS protein records   : {len(df):,}")
    print(f"Unique protein IDs     : {unique_ids:,}")
    print(f"Proteins with KO       : {proteins_with_ko:,}")
    print(
        f"Proteins without KO    : "
        f"{unique_ids - proteins_with_ko:,}"
    )
    print(f"Unique KO IDs          : {len(unique_kos):,}")
    print()

    return df


# ============================================================
# FASTA VALIDATION
# ============================================================

def compare_fasta_kaas(
    fasta_set,
    kaas_df: pd.DataFrame,
    output_dir: Path,
):
    print("STEP 4: FASTA <-> KAAS ID matching")
    print("-" * 72)

    kaas_set = set(kaas_df["Protein_ID"].dropna().astype(str))

    fasta_missing = sorted(fasta_set - kaas_set)
    kaas_not_fasta = sorted(kaas_set - fasta_set)
    matching = fasta_set & kaas_set

    percentage = (
        len(matching) / len(fasta_set) * 100
        if fasta_set
        else 0
    )

    print(f"FASTA IDs             : {len(fasta_set):,}")
    print(f"KAAS IDs              : {len(kaas_set):,}")
    print(f"Matching IDs          : {len(matching):,}")
    print(f"FASTA missing KAAS    : {len(fasta_missing):,}")
    print(f"KAAS not in FASTA     : {len(kaas_not_fasta):,}")
    print(f"FASTA represented     : {percentage:.2f}%")
    print()

    (output_dir / "FASTA_missing_in_KAAS.txt").write_text(
        "\n".join(fasta_missing) + ("\n" if fasta_missing else ""),
        encoding="utf-8",
    )

    (output_dir / "KAAS_not_in_FASTA.txt").write_text(
        "\n".join(kaas_not_fasta) + ("\n" if kaas_not_fasta else ""),
        encoding="utf-8",
    )

    return {
        "fasta_ids": len(fasta_set),
        "kaas_ids": len(kaas_set),
        "matching": len(matching),
        "missing": len(fasta_missing),
        "not_in_fasta": len(kaas_not_fasta),
        "percentage": percentage,
    }


# ============================================================
# KEGG CACHE
# ============================================================

def load_cache(cache_file: Path) -> dict:
    if not cache_file.exists():
        return {}

    try:
        with cache_file.open("rb") as handle:
            cache = pickle.load(handle)

        if not isinstance(cache, dict):
            print("Warning: KEGG cache is not a dictionary; starting empty.")
            return {}

        print(f"Existing KEGG cache loaded: {len(cache):,} KOs")
        return cache

    except Exception as exc:
        print(f"Warning: cache could not be loaded: {exc}")
        return {}


def save_cache(cache: dict, cache_file: Path) -> None:
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    temporary = cache_file.with_suffix(cache_file.suffix + ".tmp")

    with temporary.open("wb") as handle:
        pickle.dump(
            cache,
            handle,
            protocol=pickle.HIGHEST_PROTOCOL,
        )

    temporary.replace(cache_file)


# ============================================================
# KEGG RECORD PARSER
# ============================================================

def parse_kegg_record(text: str) -> dict:
    info = {
        "Enzyme": "",
        "EC": "",
        "Pathways": [],
    }

    if not text:
        return info

    lines = text.splitlines()

    # ENZYME line may contain EC numbers after the first token.
    for line in lines:
        if line.startswith("ENZYME"):
            rest = line[12:].strip()
            if rest:
                ecs = re.findall(r"\d+\.\d+\.\d+\.\d+", rest)
                info["EC"] = ";".join(dict.fromkeys(ecs))

        elif line.startswith("NAME"):
            name = line[12:].strip()
            # KEGG names can include EC information in some records;
            # retain the actual NAME field as Enzyme.
            info["Enzyme"] = name

        elif line.startswith("PATHWAY"):
            rest = line[12:].strip()
            match = re.match(r"(map\d+)\s+(.+)", rest)
            if match:
                info["Pathways"].append(
                    (match.group(1), match.group(2).strip())
                )

    # Some records use continuation lines for PATHWAY.
    current_pathway = None
    for line in lines:
        if line.startswith("PATHWAY"):
            rest = line[12:].strip()
            match = re.match(r"(map\d+)\s+(.+)", rest)
            if match:
                current_pathway = (
                    match.group(1),
                    match.group(2).strip(),
                )
        elif (
            current_pathway is not None
            and line.startswith("            ")
            and not line.startswith("            ")
        ):
            pass

    # Fallback for EC values anywhere in the record if ENZYME was absent.
    if not info["EC"]:
        ecs = re.findall(r"\b\d+\.\d+\.\d+\.\d+\b", text)
        info["EC"] = ";".join(dict.fromkeys(ecs))

    # Deduplicate pathways.
    info["Pathways"] = list(dict.fromkeys(info["Pathways"]))

    return info


# ============================================================
# KEGG REST LOOKUP
# ============================================================

def fetch_kegg_batch(
    ko_ids,
    cache: dict,
    cache_file: Path,
    batch_size: int = 10,
    delay: float = 1.0,
) -> dict:
    unique_kos = sorted(set(ko_ids))

    print("STEP 5: KEGG KO annotation")
    print("-" * 72)
    print(f"Unique KOs to annotate : {len(unique_kos):,}")
    print(f"KEGG batch size        : {batch_size}")
    print(f"Delay between batches  : {delay} seconds")
    print()

    print(f"Existing KEGG cache loaded: {len(cache):,} KOs")

    needed = [ko for ko in unique_kos if ko not in cache]

    print(f"Already cached         : {len(unique_kos) - len(needed):,}")
    print(f"Need KEGG lookup       : {len(needed):,}")
    print()

    if not needed:
        print(f"KEGG cache now contains: {len(cache):,} KOs")
        print()
        return cache

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    batches = [
        needed[i:i + batch_size]
        for i in range(0, len(needed), batch_size)
    ]

    for index, batch in enumerate(batches, start=1):
        first = batch[0]
        last = batch[-1]

        print(
            f"[Batch {index}/{len(batches)}] "
            f"{first} -> {last} ...",
            end=" ",
            flush=True,
        )

        # KEGG supports a + separated list for batch get.
        query = "+".join(batch)
        url = f"{KEGG_BASE}/get/{query}"

        try:
            response = session.get(url, timeout=180)
            response.raise_for_status()

            # KEGG separates multiple entries with "///".
            records = response.text.split("///")

            found = 0

            for record in records:
                record = record.strip()
                if not record:
                    continue

                entry_match = re.search(
                    r"^ENTRY\s+(\S+)",
                    record,
                    flags=re.MULTILINE,
                )

                if not entry_match:
                    continue

                ko = entry_match.group(1).strip()

                if not re.fullmatch(r"K\d{5}", ko):
                    continue

                cache[ko] = parse_kegg_record(record)
                found += 1

            # Preserve missing records so repeated runs do not hammer KEGG.
            for ko in batch:
                if ko not in cache:
                    cache[ko] = {
                        "Enzyme": "",
                        "EC": "",
                        "Pathways": [],
                    }

            print(f"OK ({found} records)")

            save_cache(cache, cache_file)

        except Exception as exc:
            print(f"FAILED: {exc}")

            # Do not mark failed requests as permanently cached.
            # The next run can retry them.
            save_cache(cache, cache_file)
            raise

        if index < len(batches):
            time.sleep(max(0.0, delay))

    print()
    print(f"KEGG cache now contains: {len(cache):,} KOs")
    print()

    return cache


# ============================================================
# BUILD KEGG KO ANNOTATION TABLE
# ============================================================

def build_kegg_table(
    unique_kos,
    cache: dict,
) -> pd.DataFrame:
    rows = []

    for ko in sorted(unique_kos):
        info = cache.get(
            ko,
            {
                "Enzyme": "",
                "EC": "",
                "Pathways": [],
            },
        )

        pathways = info.get("Pathways", []) or []

        if not pathways:
            rows.append(
                [
                    ko,
                    info.get("Enzyme", ""),
                    info.get("EC", ""),
                    "",
                    "",
                ]
            )
        else:
            for pathway_id, pathway_name in pathways:
                rows.append(
                    [
                        ko,
                        info.get("Enzyme", ""),
                        info.get("EC", ""),
                        pathway_id,
                        pathway_name,
                    ]
                )

    return pd.DataFrame(
        rows,
        columns=[
            "KO",
            "Enzyme",
            "EC",
            "PathwayID",
            "PathwayName",
        ],
    )


# ============================================================
# PROTEIN -> KO -> PATHWAY
# ============================================================

def build_protein_pathway_table(
    kaas_df: pd.DataFrame,
    kegg_df: pd.DataFrame,
) -> pd.DataFrame:
    assigned = kaas_df[
        kaas_df["KO"].map(is_valid_ko)
    ][
        ["Protein_ID", "KO"]
    ].copy()

    if assigned.empty:
        return pd.DataFrame(
            columns=[
                "Protein_ID",
                "KO",
                "Enzyme",
                "EC",
                "PathwayID",
                "PathwayName",
            ]
        )

    annotation = kegg_df[
        [
            "KO",
            "Enzyme",
            "EC",
            "PathwayID",
            "PathwayName",
        ]
    ].copy()

    result = assigned.merge(
        annotation,
        on="KO",
        how="left",
    )

    return result


# ============================================================
# SUMMARY TABLES
# ============================================================

def build_summaries(
    kaas_df: pd.DataFrame,
    kegg_df: pd.DataFrame,
    protein_pathway_df: pd.DataFrame,
):
    # IMPORTANT:
    # Count unique proteins, not dataframe rows.
    # This fixes the previous "Proteins with KO = 2" problem.
    assigned = kaas_df[
        kaas_df["KO"].map(is_valid_ko)
    ].copy()

    ko_summary = (
        assigned.groupby("KO")["Protein_ID"]
        .nunique()
        .reset_index(name="Protein_Count")
        .sort_values(
            "Protein_Count",
            ascending=False,
        )
    )

    ko_summary = ko_summary.merge(
        kegg_df[
            ["KO", "Enzyme", "EC"]
        ].drop_duplicates("KO"),
        on="KO",
        how="left",
    )

    pathway_data = kegg_df[
        kegg_df["PathwayID"]
        .fillna("")
        .astype(str)
        .str.startswith("map")
    ].copy()

    pathway_summary = (
        pathway_data
        .groupby(
            ["PathwayID", "PathwayName"],
            dropna=False,
        )
        .agg(
            Unique_KOs=("KO", "nunique"),
        )
        .reset_index()
        .sort_values(
            "Unique_KOs",
            ascending=False,
        )
    )

    ec_rows = []

    for _, row in kegg_df.iterrows():
        ec_text = clean_text(row.get("EC", ""))

        if not ec_text:
            continue

        for ec in ec_text.split(";"):
            ec = ec.strip()
            if ec:
                ec_rows.append([ec, row["KO"]])

    if ec_rows:
        ec_summary = pd.DataFrame(
            ec_rows,
            columns=["EC", "KO"],
        )

        ec_summary = (
            ec_summary.groupby("EC")
            .agg(
                Unique_KOs=("KO", "nunique"),
            )
            .reset_index()
            .sort_values(
                "Unique_KOs",
                ascending=False,
            )
        )
    else:
        ec_summary = pd.DataFrame(
            columns=["EC", "Unique_KOs"]
        )

    return (
        ko_summary,
        pathway_summary,
        ec_summary,
    )


# ============================================================
# OVERALL SUMMARY
# ============================================================

def build_overall_summary(
    kaas_df: pd.DataFrame,
    unique_kos,
    kegg_table: pd.DataFrame,
) -> pd.DataFrame:
    total_proteins = kaas_df["Protein_ID"].nunique()

    proteins_with_ko = kaas_df.loc[
        kaas_df["KO"].map(is_valid_ko),
        "Protein_ID",
    ].nunique()

    proteins_without_ko = (
        total_proteins - proteins_with_ko
    )

    unique_ko_count = len(set(unique_kos))

    pathway_count = (
        kegg_table.loc[
            kegg_table["PathwayID"]
            .fillna("")
            .astype(str)
            .str.startswith("map"),
            "PathwayID",
        ]
        .nunique()
    )

    ec_values = (
        kegg_table.loc[
            kegg_table["EC"]
            .fillna("")
            .astype(str)
            .str.strip()
            != "",
            "EC",
        ]
        .astype(str)
        .str.split(";")
        .explode()
        .str.strip()
    )

    ec_count = ec_values[
        ec_values != ""
    ].nunique()

    summary = pd.DataFrame(
        [
            ["Total proteins", total_proteins],
            ["Proteins with KO", proteins_with_ko],
            ["Proteins without KO", proteins_without_ko],
            ["Unique KO IDs", unique_ko_count],
            ["Unique KEGG pathways", pathway_count],
            ["Unique EC numbers", ec_count],
        ],
        columns=["Metric", "Value"],
    )

    return summary


# ============================================================
# EXCEL EXPORT
# ============================================================

def export_excel(
    output_file: Path,
    kaas_df: pd.DataFrame,
    kegg_df: pd.DataFrame,
    protein_pathway_df: pd.DataFrame,
    ko_summary: pd.DataFrame,
    pathway_summary: pd.DataFrame,
    ec_summary: pd.DataFrame,
    summary: pd.DataFrame,
) -> None:
    print("STEP 11: Writing Excel")
    print("-" * 72)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        output_file,
        engine="openpyxl",
    ) as writer:

        kaas_df.to_excel(
            writer,
            sheet_name="All_Protein_KO",
            index=False,
        )

        kegg_df.to_excel(
            writer,
            sheet_name="KO_Annotation",
            index=False,
        )

        protein_pathway_df.to_excel(
            writer,
            sheet_name="Pathway_Annotation",
            index=False,
        )

        ko_summary.to_excel(
            writer,
            sheet_name="KO_Summary",
            index=False,
        )

        pathway_summary.to_excel(
            writer,
            sheet_name="Pathway_Summary",
            index=False,
        )

        ec_summary.to_excel(
            writer,
            sheet_name="EC_Summary",
            index=False,
        )

        summary.to_excel(
            writer,
            sheet_name="Summary",
            index=False,
        )

    print(f"Excel saved: {output_file}")
    print()


# ============================================================
# SAVE NORMALIZED TSV
# ============================================================

def save_protein_ko(
    kaas_df: pd.DataFrame,
    output_file: Path,
) -> None:
    kaas_df.to_csv(
        output_file,
        sep="\t",
        index=False,
    )

    print("Protein -> KO table:")
    print(output_file)
    print()


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    print_header()

    parser = argparse.ArgumentParser(
        description=(
            "KAAS -> KEGG analyzer. "
            "Local query.ko, Excel, TSV/CSV or KAAS URL input. "
            "FASTA is optional."
        )
    )

    # --------------------------------------------------------
    # INPUTS
    # --------------------------------------------------------

    parser.add_argument(
        "--input",
        default=None,
        help=(
            "Local KAAS query.ko, TSV, CSV, XLSX or XLS file. "
            "Preferred input when available."
        ),
    )

    parser.add_argument(
        "--kaas-file",
        default=None,
        help=(
            "Alias for --input; local KAAS query.ko/table."
        ),
    )

    parser.add_argument(
        "--kaas-url",
        default=None,
        help=(
            "Optional completed KAAS result URL. "
            "Used only if --input/--kaas-file is not supplied."
        ),
    )

    parser.add_argument(
        "--fasta",
        default=None,
        help=(
            "Optional original protein FASTA for ID validation only."
        ),
    )

    # --------------------------------------------------------
    # OUTPUT / KEGG OPTIONS
    # --------------------------------------------------------

    parser.add_argument(
        "--output",
        default="KAAS_KEGG_Results",
        help="Output directory.",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of KOs per KEGG request.",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between KEGG requests in seconds.",
    )

    args = parser.parse_args()

    if args.batch_size < 1:
        die("--batch-size must be >= 1.")

    if args.delay < 0:
        die("--delay cannot be negative.")

    output_dir = Path(
        args.output
    ).expanduser().resolve()

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Resolve local input
    # --------------------------------------------------------

    input_arg = args.input or args.kaas_file

    local_input = None

    if input_arg:
        local_input = Path(
            input_arg
        ).expanduser().resolve()

        if not local_input.exists():
            die(f"Input file does not exist: {local_input}")

    # --------------------------------------------------------
    # STEP 1: obtain KAAS data
    # --------------------------------------------------------

    if local_input is not None:
        print("STEP 1: Using local KAAS/input file")
        print("-" * 72)
        print(local_input)
        print()

        source_suffix = local_input.suffix.lower()

        # Native KAAS query.ko and text-like files.
        if source_suffix in {
            ".ko",
            ".txt",
        }:
            kaas_df = parse_kaas_query_ko(local_input)

        else:
            kaas_df = read_tabular_input(local_input)

    elif args.kaas_url:
        downloaded = output_dir / "KAAS_query.ko"

        download_kaas_result(
            args.kaas_url,
            downloaded,
        )

        kaas_df = parse_kaas_query_ko(downloaded)

    else:
        die(
            "No input supplied. Give one of:\n"
            "  --input query.ko\n"
            "  --input results.xlsx\n"
            "  --input results.tsv\n"
            "  --kaas-file query.ko\n"
            "  --kaas-url 'https://...'\n"
            "FASTA is optional."
        )

    # --------------------------------------------------------
    # STEP 2: optional FASTA validation
    # --------------------------------------------------------

    fasta_set = None
    comparison = None

    if args.fasta:
        fasta_file = Path(
            args.fasta
        ).expanduser().resolve()

        if not fasta_file.exists():
            die(f"FASTA file does not exist: {fasta_file}")

        fasta_ids, fasta_set = read_fasta_ids(
            fasta_file
        )

        fasta_ids_file = output_dir / "FASTA_IDs.txt"

        fasta_ids_file.write_text(
            "\n".join(fasta_ids)
            + ("\n" if fasta_ids else ""),
            encoding="utf-8",
        )

        print("FASTA IDs written:")
        print(fasta_ids_file)
        print()

        comparison = compare_fasta_kaas(
            fasta_set,
            kaas_df,
            output_dir,
        )

    else:
        print("STEP 2: FASTA validation skipped")
        print("-" * 72)
        print("No FASTA supplied. This is allowed.")
        print()

    # --------------------------------------------------------
    # STEP 3/4: normalized KAAS data already available
    # --------------------------------------------------------

    print("KAAS protein records:", f"{len(kaas_df):,}")
    print()

    save_protein_ko(
        kaas_df,
        output_dir / "Protein_KO.tsv",
    )

    # --------------------------------------------------------
    # STEP 5: unique KOs
    # --------------------------------------------------------

    print("=" * 72)
    print("STEP 6: Collecting unique KO IDs")
    print("-" * 72)

    unique_kos = sorted(
        kaas_df.loc[
            kaas_df["KO"].map(is_valid_ko),
            "KO",
        ].unique()
    )

    print(f"Unique KO IDs: {len(unique_kos):,}")
    print()

    if not unique_kos:
        die(
            "No valid Kxxxxx KO IDs were found in the input."
        )

    # --------------------------------------------------------
    # STEP 6/7: KEGG cache
    # --------------------------------------------------------

    print("=" * 72)
    print("STEP 7: Retrieving KEGG annotations")
    print("-" * 72)

    cache_file = output_dir / "KEGG_cache.pkl"

    cache = load_cache(cache_file)

    cache = fetch_kegg_batch(
        unique_kos,
        cache,
        cache_file,
        batch_size=args.batch_size,
        delay=args.delay,
    )

    # --------------------------------------------------------
    # STEP 8: KEGG table
    # --------------------------------------------------------

    print("=" * 72)
    print("STEP 8: Building KEGG annotation table")
    print("-" * 72)

    # Reloading here is harmless and ensures the on-disk cache is the
    # authoritative cache used for table generation.
    cache = load_cache(cache_file)

    kegg_table = build_kegg_table(
        unique_kos,
        cache,
    )

    kegg_annotation_file = (
        output_dir / "KEGG_KO_Annotation.tsv"
    )

    kegg_table.to_csv(
        kegg_annotation_file,
        sep="\t",
        index=False,
    )

    print("KEGG annotation table:")
    print(kegg_annotation_file)
    print()

    # --------------------------------------------------------
    # STEP 9: protein -> pathway
    # --------------------------------------------------------

    print("=" * 72)
    print("STEP 9: Mapping proteins to pathways")
    print("-" * 72)

    protein_pathway_table = build_protein_pathway_table(
        kaas_df,
        kegg_table,
    )

    protein_pathway_file = (
        output_dir / "Protein_Pathway.tsv"
    )

    protein_pathway_table.to_csv(
        protein_pathway_file,
        sep="\t",
        index=False,
    )

    print("Protein -> KO -> pathway table:")
    print(protein_pathway_file)
    print()

    # --------------------------------------------------------
    # STEP 10: summaries
    # --------------------------------------------------------

    print("=" * 72)
    print("STEP 10: Building summary tables")
    print("-" * 72)

    (
        ko_summary,
        pathway_summary,
        ec_summary,
    ) = build_summaries(
        kaas_df,
        kegg_table,
        protein_pathway_table,
    )

    summary = build_overall_summary(
        kaas_df,
        unique_kos,
        kegg_table,
    )

    print()

    for _, row in summary.iterrows():
        print(
            f"{str(row['Metric']):22s}: "
            f"{int(row['Value']):,}"
        )

    print()

    # --------------------------------------------------------
    # STEP 11: Excel
    # --------------------------------------------------------

    print("=" * 72)
    print("STEP 11: Exporting Excel")
    print("-" * 72)

    excel_file = (
        output_dir / "KAAS_KEGG_Results.xlsx"
    )

    # IMPORTANT:
    # Pass exactly the eight arguments required by export_excel().
    # Do NOT pass protein_ko, summaries or comparison here.
    export_excel(
        excel_file,
        kaas_df,
        kegg_table,
        protein_pathway_table,
        ko_summary,
        pathway_summary,
        ec_summary,
        summary,
    )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print("=" * 72)
    print("             ANALYSIS COMPLETED SUCCESSFULLY")
    print("=" * 72)
    print()

    print(f"Total proteins       : {kaas_df['Protein_ID'].nunique():,}")
    print(
        "Proteins with KO     : "
        f"{kaas_df.loc[kaas_df['KO'].map(is_valid_ko), 'Protein_ID'].nunique():,}"
    )
    print(
        "Proteins without KO  : "
        f"{kaas_df['Protein_ID'].nunique() - kaas_df.loc[kaas_df['KO'].map(is_valid_ko), 'Protein_ID'].nunique():,}"
    )
    print(f"Unique KO IDs        : {len(unique_kos):,}")
    print(
        "Unique pathways      : "
        f"{kegg_table.loc[kegg_table['PathwayID'].fillna('').astype(str).str.startswith('map'), 'PathwayID'].nunique():,}"
    )
    print()

    if comparison is not None:
        print(
            f"FASTA represented     : "
            f"{comparison['percentage']:.2f}%"
        )
        print()

    print("FINAL EXCEL:")
    print(excel_file)
    print()
    print("=" * 72)


if __name__ == "__main__":
    main()
