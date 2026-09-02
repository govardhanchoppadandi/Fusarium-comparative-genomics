from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
PIPELINE = BASE_DIR / "kaas_kegg_pipeline_fixed.py"
ARI_LOGO = BASE_DIR / "assets" / "ari_logo.png"

ARI_URL = "https://aripune.res.in/"
ARI_GPB_URL = "https://aripune.res.in/research/genetics-and-plant-breeding/"

st.set_page_config(
    page_title="KAAS → KEGG Pathway Analyzer | ARI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1250px;}
    .ari-header {
        border: 1px solid #d9e2ec;
        border-radius: 16px;
        padding: 18px 22px;
        background: linear-gradient(135deg, #f7fbff 0%, #ffffff 100%);
        margin-bottom: 16px;
    }
    .ari-title {font-size: 2.0rem; font-weight: 750; margin: 0; line-height: 1.2;}
    .ari-subtitle {font-size: 1.02rem; color: #4b5563; margin-top: 7px;}
    .dev-card {
        border: 1px solid #e1e7ef; border-radius: 12px;
        padding: 15px 18px; margin-top: 14px; background: #fbfcfe;
    }
    .footer {
        margin-top: 35px; padding-top: 18px; border-top: 1px solid #e1e7ef;
        color: #5b6573; font-size: 0.9rem;
    }
    .small-note {color:#667085; font-size:0.88rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# ARI BRANDING
# ---------------------------------------------------------------------------
c_logo, c_title = st.columns([1, 8], vertical_alignment="center")

with c_logo:
    if ARI_LOGO.is_file():
        st.image(str(ARI_LOGO), width=105)
    else:
        st.markdown("### ARI")

with c_title:
    st.markdown(
        """
        <div class="ari-header">
          <div class="ari-title">🧬 KAAS → KEGG Pathway Analyzer</div>
          <div class="ari-subtitle">
          Automated fungal protein KO assignment, KEGG annotation,
          pathway mapping and functional summaries
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
    <div class="dev-card">
      <b>Developed at</b><br>
      <a href="{ARI_GPB_URL}" target="_blank">
      Wheat Pathology Laboratory, Agharkar Research Institute,
      Hol, Baramati, Pune
      </a><br><br>
      <b>Developed by</b><br>
      Dr. Sudhir Navathe · Govardhan Choppadandi
      <br><br>
      <a href="{ARI_URL}" target="_blank">Agharkar Research Institute — official website</a>
      </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "Provide any one suitable KAAS result source: a completed KAAS URL "
    "or a local KAAS/KO/TSV/CSV/Excel file. "
    "An original protein FASTA is optional and is used only for ID validation."
)

# ---------------------------------------------------------------------------
# INPUT
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.subheader("1. KAAS / KO input")

    input_mode = st.radio(
        "Input source",
        ["Completed KAAS result URL", "Local KAAS / KO / table file"],
        horizontal=True,
    )

    if input_mode == "Completed KAAS result URL":
        source = st.text_input(
            "Completed KAAS result URL",
            placeholder="https://www.genome.jp/kaas-bin/kaas_main?mode=user&id=...",
            help="Paste the completed KAAS result-page URL. query.ko is downloaded automatically.",
        )
    else:
        source = st.text_input(
            "Input file path",
            placeholder=r'D:\data\query.ko  or  D:\data\results.xlsx',
            help="Ubuntu/WSL paths and Windows paths are accepted.",
        )
        st.caption("Accepted: .ko, .txt, .tsv, .csv, .xlsx, .xls")

with st.container(border=True):
    st.subheader("2. Optional protein FASTA validation")
    fasta_source = st.text_input(
        "Original protein FASTA path (optional)",
        placeholder=r'D:\data\proteins.faa — leave empty to skip validation',
        help="FASTA is not required for KO, EC or pathway annotation.",
    )

with st.container(border=True):
    st.subheader("3. Output and KEGG settings")

    c1, c2 = st.columns(2)

    with c1:
        output_source = st.text_input(
            "Output directory",
            value=str(BASE_DIR / "KAAS_KEGG_Results"),
        )
        batch_size = st.number_input(
            "KEGG batch size",
            min_value=1,
            max_value=10,
            value=10,
            step=1,
        )

    with c2:
        delay = st.number_input(
            "Delay between KEGG requests (seconds)",
            min_value=0.0,
            max_value=10.0,
            value=1.0,
            step=0.1,
        )

st.caption(
    "Input → Protein/KO normalization → KEGG annotation → EC numbers → "
    "pathway mapping → summaries → final Excel workbook."
)

run = st.button(
    "🚀 RUN COMPLETE ANALYSIS",
    type="primary",
    use_container_width=True,
)

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def clean_path(value: str) -> str:
    value = (value or "").strip()

    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1].strip()

    # Convert Windows drive paths to WSL paths.
    if len(value) >= 3 and value[1:3] == ":\\":
        drive = value[0].lower()
        value = "/mnt/" + drive + value[2:].replace("\\", "/")
    elif len(value) >= 3 and value[1:3] == ":/":
        drive = value[0].lower()
        value = "/mnt/" + drive + value[2:]

    return value


def resolve_local_path(value: str) -> Path:
    p = Path(clean_path(value)).expanduser()

    if not p.is_absolute():
        p = Path.cwd() / p

    return p.resolve()


def run_pipeline(args: list[str]) -> tuple[int, str]:
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    proc = subprocess.Popen(
        [sys.executable, *args],
        cwd=BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
    )

    lines: list[str] = []
    box = st.empty()

    if proc.stdout is not None:
        for line in proc.stdout:
            lines.append(line)
            box.code("".join(lines[-160:]), language="text")

    returncode = proc.wait()
    return returncode, "".join(lines)


# ---------------------------------------------------------------------------
# RUN
# ---------------------------------------------------------------------------
if run:
    if not PIPELINE.is_file():
        st.error(
            "The application pipeline component is missing. "
            "Keep kaas_kegg_pipeline_fixed.py beside app.py."
        )
        st.stop()

    source = source.strip()

    if not source:
        st.error(
            "Please provide either a completed KAAS URL "
            "or a local KAAS/KO/table file."
        )
        st.stop()

    output_dir = resolve_local_path(output_source)
    output_dir.mkdir(parents=True, exist_ok=True)

    args = [
        str(PIPELINE),
        "--output", str(output_dir),
        "--batch-size", str(int(batch_size)),
        "--delay", str(float(delay)),
    ]

    if input_mode == "Completed KAAS result URL":
        if not (
            source.startswith("http://")
            or source.startswith("https://")
        ):
            st.error("The KAAS URL must start with http:// or https://")
            st.stop()

        args += ["--kaas-url", source]

    else:
        local = resolve_local_path(source)

        if not local.is_file():
            st.error(f"Input file not found: {local}")
            st.stop()

        args += ["--input", str(local)]

    if fasta_source.strip():
        fasta = resolve_local_path(fasta_source)

        if not fasta.is_file():
            st.error(f"FASTA file not found: {fasta}")
            st.stop()

        args += ["--fasta", str(fasta)]

    st.subheader("Analysis progress")

    with st.spinner("Running KAAS → KEGG analysis…"):
        code, log = run_pipeline(args)

    if code != 0:
        st.error(
            "Analysis failed. Review the final error shown in "
            "the progress panel."
        )
        st.stop()

    excel_file = output_dir / "KAAS_KEGG_Results.xlsx"

    if not excel_file.is_file():
        st.error(
            "The pipeline finished but the final Excel file "
            "was not found."
        )
        st.stop()

    st.success("Analysis completed successfully.")

    st.write(f"Output directory: `{output_dir}`")

    with open(excel_file, "rb") as handle:
        st.download_button(
            "⬇️ Download final Excel",
            data=handle.read(),
            file_name=excel_file.name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    st.subheader("Final Excel contents")
    st.write(
        "All_Protein_KO · KO_Annotation · Pathway_Annotation · "
        "KO_Summary · Pathway_Summary · EC_Summary · Summary"
    )

# ---------------------------------------------------------------------------
# CITATION / FOOTER
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="footer">
      <b>Citation</b><br>
      Please cite the associated publication when using this application in research.<br>
      <span class="small-note">
      Publication citation and DOI will be added here after publication.
      </span>
      <br><br>
      <b>Institution</b><br>
      <a href="{ARI_URL}" target="_blank">Agharkar Research Institute</a> ·
      <a href="{ARI_GPB_URL}" target="_blank">Genetics and Plant Breeding</a>
      <br><br>
      <span class="small-note">
      This application is a research software tool developed at the
      Wheat Pathology Laboratory.
      </span>
    </div>
    """,
    unsafe_allow_html=True,
)
