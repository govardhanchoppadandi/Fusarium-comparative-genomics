# ==========================================================
# TNW1 COMPLETE SCAFFOLD CIRCOS INPUT BUILDER
# FINAL STABLE VERSION
#
# This pipeline creates ALL Circos input tracks:
#
# 1. Karyotype
# 2. Gene density
# 3. GC content density
# 4. TE density
# 5. RIP density
# 6. tRNA track
# 7. rRNA track
# 8. Secreted proteins
# 9. GO annotations
# 10. CAZyme track
# 11. antiSMASH clusters
# 12. Effector tracks
#       - Apoplastic
#       - Cytoplasmic
#       - Both
#
# Output:
# circos_scaffold/
#
# Genome:
# TNW_1
# ==========================================================


# ==========================================================
# IMPORT LIBRARIES
# ==========================================================

import pandas as pd
import numpy as np
from Bio import SeqIO
import os


print("\n==============================")
print("TNW1 COMPLETE CIRCOS BUILDER")
print("==============================\n")


# ==========================================================
# PATHS
# ==========================================================

BASE = (
    r"D:\fusarium_analysis\new_TE_CIRCOS"
    r"\tnw1 circos\rebuilt\tnw1_files"
)

OUT = BASE + r"\circos_scaffold"

os.makedirs(OUT, exist_ok=True)


# ==========================================================
# INPUT FILES
# ==========================================================

GENOME = BASE + r"\TNW_1.genome.fa"

GENES = BASE + r"\gene_positions.tsv"

TE = BASE + r"\TNW_1.filteredRepeats.bed"

RIP = BASE + r"\TNW_1_RIP.bed"

TRNA = BASE + r"\TNW1_tRNAs.bed"

RRNA = BASE + r"\TNW1_rRNAs.barrnap.gff"

SECRET = BASE + r"\secreted.txt"

GO = BASE + r"\GO_export.txt"

CAZY = BASE + r"\dbcan.txt"

ANTI = BASE + r"\TNW1 SM.xlsx"

EFF_APO = BASE + r"\effector_apoplastic.txt"

EFF_CYTO = BASE + r"\effector_cytoplasmic.txt"

EFF_BOTH = BASE + r"\effector_both.txt"


# ==========================================================
# SETTINGS
# ==========================================================

WINDOW = 100000


# ==========================================================
# BUILD KARYOTYPE
# ==========================================================

print("Building karyotype")

rows = []

for rec in SeqIO.parse(GENOME, "fasta"):

    rows.append([
        rec.id,
        0,
        len(rec.seq)
    ])

kary = pd.DataFrame(
    rows,
    columns=["chr", "start", "end"]
)

kary.to_csv(
    OUT + "/karyotype.txt",
    sep="\t",
    index=False,
    header=False
)

limits = dict(
    zip(
        kary.chr,
        kary.end
    )
)

print("Scaffolds:", len(kary))


# ==========================================================
# DENSITY TRACK FUNCTION
# ==========================================================

def density_track(df, outfile):

    rows = []

    for sc, length in limits.items():

        bins = np.arange(
            0,
            length + WINDOW,
            WINDOW
        )

        sub = df[
            df.chr == sc
        ]

        if len(sub):

            counts, _ = np.histogram(
                sub.start,
                bins=bins
            )

        else:

            counts = np.zeros(
                len(bins) - 1
            )

        for i, c in enumerate(counts):

            rows.append([
                sc,
                bins[i],
                bins[i + 1],
                c
            ])

    pd.DataFrame(rows).to_csv(
        OUT + "/" + outfile,
        sep="\t",
        index=False,
        header=False
    )


# ==========================================================
# LOAD GENE COORDINATES
# ==========================================================

print("Loading gene coordinates")

genes = pd.read_csv(
    GENES,
    sep="\t"
)

genes.columns = [
    "chr",
    "start",
    "end",
    "gene"
]

genes["gene"] = (
    genes["gene"]
    .astype(str)
)


# ==========================================================
# GENE DENSITY
# ==========================================================

print("Building gene density")

density_track(
    genes[["chr", "start"]],
    "gene_density.txt"
)


# ==========================================================
# GC CONTENT
# ==========================================================

print("Calculating GC content")

gc_rows = []

for rec in SeqIO.parse(
    GENOME,
    "fasta"
):

    seq = str(
        rec.seq
    ).upper()

    for i in range(
        0,
        len(seq),
        WINDOW
    ):

        win = seq[
            i:i + WINDOW
        ]

        if len(win) == 0:
            continue

        gc = (

            win.count("G") +

            win.count("C")

        ) / len(win)

        gc_rows.append([
            rec.id,
            i,
            i + len(win),
            gc
        ])

pd.DataFrame(
    gc_rows
).to_csv(
    OUT + "/gc_density.txt",
    sep="\t",
    index=False,
    header=False
)


# ==========================================================
# TE DENSITY
# ==========================================================

print("Processing TE")

te = pd.read_csv(
    TE,
    sep="\t",
    header=None
)

te.columns = [
    "chr",
    "start",
    "end",
    "type",
    "score",
    "strand"
]

density_track(
    te[["chr", "start"]],
    "te_density.txt"
)

te[[
    "chr",
    "start",
    "end"
]].to_csv(
    OUT + "/te_class.txt",
    sep="\t",
    index=False,
    header=False
)


# ==========================================================
# RIP DENSITY
# ==========================================================

print("Processing RIP")

rip = pd.read_csv(
    RIP,
    sep="\t",
    header=None
)

rip.columns = [
    "chr",
    "src",
    "type",
    "start",
    "end",
    "a",
    "b",
    "c",
    "d"
]

density_track(
    rip[["chr", "start"]],
    "rip_density.txt"
)


# ==========================================================
# tRNA TRACK
# ==========================================================

print("Processing tRNA")

trna = pd.read_csv(
    TRNA,
    sep="\t",
    header=None
)

trna.columns = [
    "chr",
    "start",
    "end",
    "type",
    "a",
    "strand"
]

trna[[
    "chr",
    "start",
    "end"
]].to_csv(
    OUT + "/trna.txt",
    sep="\t",
    index=False,
    header=False
)


# ==========================================================
# rRNA TRACK
# ==========================================================

print("Processing rRNA")

rrna = pd.read_csv(
    RRNA,
    sep="\t",
    comment="#",
    header=None
)

rrna.columns = [
    "chr",
    "src",
    "type",
    "start",
    "end",
    "a",
    "b",
    "c",
    "d"
]

rrna = rrna[
    rrna.type == "rRNA"
]

rrna[[
    "chr",
    "start",
    "end"
]].to_csv(
    OUT + "/rrna.txt",
    sep="\t",
    index=False,
    header=False
)


# ==========================================================
# SECRETED PROTEINS
# ==========================================================

print("Processing secreted proteins")

sec = pd.read_csv(
    SECRET,
    header=None
)[0]

sec = sec.str.replace(
    ".t1",
    "",
    regex=False
)

sec = genes[
    genes["gene"].isin(sec)
]

sec[[
    "chr",
    "start",
    "end"
]].to_csv(
    OUT + "/secreted.txt",
    sep="\t",
    index=False,
    header=False
)


# ==========================================================
# GO TRACK
# ==========================================================

print("Building GO track")

go = pd.read_csv(
    GO,
    sep="\t"
)

go["gene"] = (
    go["Sequence Name"]
    .str.replace(
        ".t1",
        "",
        regex=False
    )
)

go = genes.merge(
    go,
    on="gene"
)

go[[
    "chr",
    "start",
    "end"
]].to_csv(
    OUT + "/go_density.txt",
    sep="\t",
    index=False,
    header=False
)


# ==========================================================
# CAZYME TRACK
# ==========================================================

print("Building CAZyme track")

cazy = pd.read_csv(
    CAZY,
    sep="\t"
)

cazy["gene"] = (
    cazy["Gene ID"]
    .str.replace(
        ".t1",
        "",
        regex=False
    )
)

cazy = genes.merge(
    cazy,
    on="gene"
)

cazy[[
    "chr",
    "start",
    "end"
]].to_csv(
    OUT + "/cazyme.txt",
    sep="\t",
    index=False,
    header=False
)


# ==========================================================
# antiSMASH TRACK
# ==========================================================

print("Building antiSMASH track")

anti = pd.read_excel(
    ANTI
)

anti = anti.rename(
    columns={
        "Scaffold": "chr",
        "From": "start",
        "To": "end"
    }
)

anti[[
    "chr",
    "start",
    "end"
]].to_csv(
    OUT + "/antismash.txt",
    sep="\t",
    index=False,
    header=False
)


# ==========================================================
# EFFECTOR TRACK FUNCTION
# ==========================================================

def build_effector(
    file,
    outfile
):

    eff = pd.read_csv(
        file,
        header=None
    )[0]

    eff = eff.str.replace(
        ".t1",
        "",
        regex=False
    )

    df = genes[
        genes["gene"]
        .isin(eff)
    ]

    df[[
        "chr",
        "start",
        "end"
    ]].to_csv(
        OUT + "/" + outfile,
        sep="\t",
        index=False,
        header=False
    )


# ==========================================================
# EFFECTOR TRACKS
# ==========================================================

print("Building effector tracks")

build_effector(
    EFF_APO,
    "effector_apoplastic.txt"
)

build_effector(
    EFF_CYTO,
    "effector_cytoplasmic.txt"
)

build_effector(
    EFF_BOTH,
    "effector_both.txt"
)


# ==========================================================
# FINISHED
# ==========================================================

print("\n====================================")
print("ALL CIRCOS FILES CREATED SUCCESSFULLY")
print("====================================")

print("\nSaved in:")

print(OUT)

print("\nGenerated files:")
print("- karyotype.txt")
print("- gene_density.txt")
print("- gc_density.txt")
print("- te_density.txt")
print("- rip_density.txt")
print("- trna.txt")
print("- rrna.txt")
print("- secreted.txt")
print("- go_density.txt")
print("- cazyme.txt")
print("- antismash.txt")
print("- effector_apoplastic.txt")
print("- effector_cytoplasmic.txt")
print("- effector_both.txt")
Install packages if needed:
pip install pandas numpy biopython openpyxl
Run:python TNW1_complete_circos_builder.py
