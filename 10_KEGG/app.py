import streamlit as st
import pandas as pd
from pathlib import Path

from src.kaas import (
    download_kaas_result,
    parse_kaas
)

from src.fasta import (
    get_fasta_ids
)

from src.kegg import (
    fetch_kegg,
    load_cache
)

from src.excel import (
    build_tables,
    write_excel
)


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="KAAS → KEGG Analyzer",
    page_icon="🧬",
    layout="wide"
)


BASE_DIR = Path(
    __file__
).resolve().parent


DOWNLOAD_DIR = BASE_DIR / "downloads"

CACHE_DIR = BASE_DIR / "cache"

OUTPUT_DIR = BASE_DIR / "output"


DOWNLOAD_DIR.mkdir(
    exist_ok=True
)

CACHE_DIR.mkdir(
    exist_ok=True
)

OUTPUT_DIR.mkdir(
    exist_ok=True
)


# ============================================================
# TITLE
# ============================================================

st.title(
    "🧬 KAAS → KEGG Pathway Analyzer"
)

st.markdown(
    """
    **Automated fungal proteome annotation workflow**

    KAAS URL → query.ko → FASTA matching →
    KO IDs → EC numbers → KEGG pathways → Excel
    """
)


# ============================================================
# INPUT
# ============================================================

st.header(
    "Input files"
)


kaas_url = st.text_input(
    "KAAS result URL",
    placeholder=(
        "https://www.genome.jp/kaas-bin/"
        "kaas_main?mode=user&id=..."
    )
)


fasta_path = st.text_input(
    "Original FASTA path",
    placeholder=(
        "/path/to/proteins.faa"
    )
)


batch_size = st.number_input(
    "KEGG batch size",
    min_value=1,
    max_value=10,
    value=10
)


delay = st.number_input(
    "Delay between KEGG requests (seconds)",
    min_value=0.1,
    max_value=5.0,
    value=0.5
)


run = st.button(
    "🚀 RUN COMPLETE ANALYSIS",
    type="primary",
    use_container_width=True
)


# ============================================================
# RUN
# ============================================================

if run:

    if not kaas_url:

        st.error(
            "KAAS URL is required."
        )

        st.stop()


    if not fasta_path:

        st.error(
            "FASTA path is required."
        )

        st.stop()


    fasta = Path(
        fasta_path
    ).expanduser()


    if not fasta.exists():

        st.error(
            f"FASTA not found:\n{fasta}"
        )

        st.stop()


    # ========================================================
    # STEP 1
    # ========================================================

    st.header(
        "1. Downloading KAAS result"
    )


    query_file = (
        DOWNLOAD_DIR
        /
        "query.ko"
    )


    try:

        download_kaas_result(
            kaas_url,
            query_file
        )

    except Exception as e:

        st.error(
            f"KAAS download failed: {e}"
        )

        st.stop()


    st.success(
        f"query.ko downloaded: "
        f"{query_file}"
    )


    # ========================================================
    # STEP 2
    # ========================================================

    st.header(
        "2. Reading KAAS KO assignments"
    )


    kaas_records = parse_kaas(
        query_file
    )


    kaas_df = pd.DataFrame(
        kaas_records
    )


    total_kaas = len(
        kaas_df
    )


    kaas_ids = set(
        kaas_df[
            "Protein_ID"
        ]
    )


    assigned = (
        kaas_df["KO"] != ""
    ).sum()


    unique_kos = sorted(
        kaas_df.loc[
            kaas_df["KO"] != "",
            "KO"
        ].unique()
    )


    # ========================================================
    # STEP 3
    # ========================================================

    st.header(
        "3. FASTA ↔ KAAS validation"
    )


    fasta_ids = get_fasta_ids(
        fasta
    )


    fasta_set = set(
        fasta_ids
    )


    matched = (
        fasta_set &
        kaas_ids
    )


    fasta_missing = (
        fasta_set -
        kaas_ids
    )


    kaas_extra = (
        kaas_ids -
        fasta_set
    )


    match_percent = (

        len(matched)
        /
        len(fasta_set)
        *
        100

        if fasta_set

        else 0
    )


    c1, c2, c3, c4 = st.columns(4)


    c1.metric(
        "FASTA IDs",
        f"{len(fasta_set):,}"
    )


    c2.metric(
        "KAAS IDs",
        f"{len(kaas_ids):,}"
    )


    c3.metric(
        "Matching IDs",
        f"{len(matched):,}"
    )


    c4.metric(
        "Match",
        f"{match_percent:.2f}%"
    )


    if (
        not fasta_missing
        and
        not kaas_extra
    ):

        st.success(
            "✅ FASTA and KAAS IDs match 100%"
        )

    else:

        st.warning(
            "⚠ FASTA and KAAS IDs are not identical."
        )


    # ========================================================
    # STEP 4
    # ========================================================

    st.header(
        "4. KEGG annotation"
    )


    cache_file = (
        CACHE_DIR
        /
        "kegg_cache.pkl"
    )


    existing_cache = load_cache(
        cache_file
    )


    st.info(
        f"Cached KOs: "
        f"{len(existing_cache):,}"
    )


    progress = st.progress(
        0
    )


    status = st.empty()


    def update_progress(
        done,
        total
    ):

        if total > 0:

            progress.progress(
                done / total
            )

            status.write(
                f"KEGG KOs processed: "
                f"{done:,} / {total:,}"
            )


    kegg_cache = fetch_kegg(
        unique_kos,
        cache_file,
        batch_size=int(batch_size),
        delay=float(delay),
        progress_callback=update_progress
    )


    progress.progress(
        1.0
    )


    status.success(
        "KEGG annotation completed."
    )


    # ========================================================
    # STEP 5
    # ========================================================

    st.header(
        "5. Building annotation tables"
    )


    (
        protein_pathways,
        ko_summary,
        pathway_summary,
        ko_annotation,
        unassigned
    ) = build_tables(
        kaas_df,
        kegg_cache
    )


    # ========================================================
    # STEP 6
    # ========================================================

    overall = pd.DataFrame(
        {
            "Metric": [
                "FASTA proteins",
                "KAAS proteins",
                "Matching proteins",
                "FASTA IDs missing in KAAS",
                "KAAS IDs not in FASTA",
                "Total KAAS records",
                "Proteins with KO",
                "Proteins without KO",
                "KO assignment percentage",
                "Unique KO IDs",
                "Unique KEGG pathways"
            ],

            "Value": [
                len(fasta_set),
                len(kaas_ids),
                len(matched),
                len(fasta_missing),
                len(kaas_extra),
                total_kaas,
                assigned,
                total_kaas - assigned,
                round(
                    assigned /
                    total_kaas *
                    100,
                    2
                ),
                len(unique_kos),
                pathway_summary[
                    "PathwayID"
                ].nunique()
            ]
        }
    )


    fasta_missing_df = pd.DataFrame(
        {
            "Protein_ID":
                sorted(
                    fasta_missing
                )
        }
    )


    kaas_extra_df = pd.DataFrame(
        {
            "Protein_ID":
                sorted(
                    kaas_extra
                )
        }
    )


    # ========================================================
    # STEP 7
    # ========================================================

    output_file = (
        OUTPUT_DIR
        /
        "KAAS_KEGG_Pathway_Analysis.xlsx"
    )


    write_excel(
        output_file,
        protein_pathways,
        ko_summary,
        pathway_summary,
        ko_annotation,
        unassigned,
        overall,
        fasta_missing_df,
        kaas_extra_df
    )


    # ========================================================
    # RESULTS
    # ========================================================

    st.success(
        "🎉 COMPLETE ANALYSIS FINISHED"
    )


    c1, c2, c3, c4, c5 = st.columns(5)


    c1.metric(
        "Proteins",
        f"{len(fasta_set):,}"
    )


    c2.metric(
        "KO assigned",
        f"{assigned:,}"
    )


    c3.metric(
        "Unique KOs",
        f"{len(unique_kos):,}"
    )


    c4.metric(
        "KEGG pathways",
        f"{pathway_summary['PathwayID'].nunique():,}"
    )


    c5.metric(
        "ID match",
        f"{match_percent:.2f}%"
    )


    # ========================================================
    # DOWNLOAD
    # ========================================================

    with open(
        output_file,
        "rb"
    ) as handle:

        excel_bytes = handle.read()


    st.download_button(
        "⬇️ DOWNLOAD FINAL EXCEL",
        data=excel_bytes,
        file_name=(
            "KAAS_KEGG_Pathway_Analysis.xlsx"
        ),
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True
    )


    # ========================================================
    # PREVIEW
    # ========================================================

    st.subheader(
        "Protein → KO → Pathway"
    )


    st.dataframe(
        protein_pathways.head(100),
        use_container_width=True
    )
