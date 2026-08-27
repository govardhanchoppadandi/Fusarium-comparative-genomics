########################################################
# AUTO RESULTS TEXT
########################################################

import pandas as pd
from pathlib import Path

EXCEL = Path(
    "results/telomere/Telomere_Analysis_Summary.xlsx"
)

gs = pd.read_excel(
    EXCEL,
    sheet_name="Genome_Summary"
)

print("\n===== TELOMERE RESULTS =====\n")

for genome in ["DMW_8", "TNW_1"]:

    match = gs[
        gs["Genome"] == genome
    ]

    if match.empty:
        print(
            f"{genome}: not found in the genome summary."
        )
        continue

    r = match.iloc[0]

    print(
        f"In the {r['Genome']} genome, "
        f"{r['Telomeric_Windows']} telomeric repeat windows "
        f"containing the canonical TTAGGG motif were identified "
        f"across {r['Scaffolds_With_Telomeres']} scaffolds "
        f"(mean repeats per window = "
        f"{r['Mean_Repeats_Per_Window']:.2f}, "
        f"maximum = "
        f"{int(r['Max_Repeats_Per_Window'])})."
    )

print("\nComparative reference genomes:\n")

for _, r in gs[
    ~gs["Genome"].isin(
        ["DMW_8", "TNW_1"]
    )
].iterrows():

    print(
        f"The {r['Genome']} reference genome showed "
        f"{r['Telomeric_Windows']} telomeric windows "
        f"across {r['Scaffolds_With_Telomeres']} scaffolds."
    )
