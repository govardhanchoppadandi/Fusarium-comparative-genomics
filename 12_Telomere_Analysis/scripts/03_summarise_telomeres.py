########################################################
# SUMMARISE TELOMERE RESULTS
########################################################

import pandas as pd
from pathlib import Path

BASE = Path(
    "results/telomere"
)

INPUT = (
    BASE /
    "Telomere_Analysis_All_Genomes.xlsx"
)

OUTPUT = (
    BASE /
    "Telomere_Analysis_Summary.xlsx"
)

df = pd.read_excel(INPUT)

required = [
    "forward_repeat_number",
    "reverse_repeat_number",
    "id",
    "Genome"
]

missing = [
    col for col in required
    if col not in df.columns
]

if missing:
    raise ValueError(
        "Required columns missing from tidk results: "
        + ", ".join(missing)
    )

df["Total_Repeats"] = (
    df["forward_repeat_number"] +
    df["reverse_repeat_number"]
)

genome_summary = (
    df.groupby("Genome")
      .agg(
          Telomeric_Windows=("id", "count"),
          Scaffolds_With_Telomeres=("id", "nunique"),
          Mean_Repeats_Per_Window=("Total_Repeats", "mean"),
          Max_Repeats_Per_Window=("Total_Repeats", "max")
      )
      .reset_index()
)

scaffold_summary = (
    df.groupby(["Genome", "id"])
      .agg(
          Telomeric_Windows=("Total_Repeats", "count"),
          Total_Repeats=("Total_Repeats", "sum")
      )
      .reset_index()
)

with pd.ExcelWriter(
    OUTPUT,
    engine="openpyxl"
) as writer:

    df.to_excel(
        writer,
        sheet_name="All_Telomere_Windows",
        index=False
    )

    genome_summary.to_excel(
        writer,
        sheet_name="Genome_Summary",
        index=False
    )

    scaffold_summary.to_excel(
        writer,
        sheet_name="Scaffold_Summary",
        index=False
    )

print("Summary written:", OUTPUT)
