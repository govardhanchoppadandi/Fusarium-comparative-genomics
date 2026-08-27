########################################################
# MERGE ALL TIDK RESULTS
########################################################

import pandas as pd
from pathlib import Path

BASE_DIR = Path("results/telomere")

OUTPUT = (
    BASE_DIR /
    "Telomere_Analysis_All_Genomes.xlsx"
)

dfs = []

for tsv in BASE_DIR.glob(
    "*_telomeric_repeat_windows.tsv"
):

    genome = tsv.name.replace(
        "_telomeres_telomeric_repeat_windows.tsv",
        ""
    )

    df = pd.read_csv(
        tsv,
        sep="\t"
    )

    df["Genome"] = genome

    dfs.append(df)

if not dfs:
    raise FileNotFoundError(
        "No *_telomeric_repeat_windows.tsv files were found in "
        f"{BASE_DIR}"
    )

combined = pd.concat(
    dfs,
    ignore_index=True
)

combined.to_excel(
    OUTPUT,
    index=False
)

print("Created:", OUTPUT)
