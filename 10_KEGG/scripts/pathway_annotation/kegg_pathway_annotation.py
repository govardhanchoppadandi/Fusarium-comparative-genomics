# ==========================================================
# KEGG PATHWAY ANNOTATION PIPELINE
# USING BIOPYTHON + KEGG REST API
#
# This pipeline will:
# 1. Read GeneID → KO mapping from KAAS
# 2. Fetch KEGG enzyme information
# 3. Fetch EC numbers
# 4. Fetch KEGG pathway annotations
# 5. Cache results to avoid repeated downloads
# 6. Export final annotated table to Excel
#
# Input:
# kaas list.txt
#
# Output:
# Biopython_KEGG_Pathways.xlsx
#
# Cache:
# kegg_cache.pkl
#
# NOTE:
# Cache prevents repeated KEGG API calls
# and speeds up reruns.
# ==========================================================


# ==========================================================
# STEP 1: IMPORT REQUIRED LIBRARIES
# ==========================================================

from Bio.KEGG import REST
import pandas as pd
import time
import pickle
import os


# ==========================================================
# STEP 2: FILE PATHS
#
# Input file format:
# GeneID <tab> KO
#
# Example:
# gene_001    ko:K00844
# gene_002    ko:K00001
# ==========================================================

INPUT_FILE = r"E:\1 Manuscript Fusarium genome\SEQ ANALYSIS\tnw1 seq analysis\KAAS\kaas list.txt"

OUTPUT_FILE = r"E:\1 Manuscript Fusarium genome\SEQ ANALYSIS\tnw1 seq analysis\KAAS\Biopython_KEGG_Pathways.xlsx"

CACHE_FILE = r"E:\1 Manuscript Fusarium genome\SEQ ANALYSIS\tnw1 seq analysis\KAAS\kegg_cache.pkl"


# ==========================================================
# STEP 3: LOAD GeneID → KO FILE
# ==========================================================

print("Loading KO file...\n")

df = pd.read_csv(
    INPUT_FILE,
    sep="\t",
    header=None,
    names=["GeneID", "KO"]
)

# Remove "ko:" prefix if present
df["KO"] = df["KO"].str.replace(
    "ko:",
    "",
    regex=False
)

# Get unique KO IDs
unique_kos = df["KO"].dropna().unique()

print(f"Total unique KO IDs = {len(unique_kos)}\n")


# ==========================================================
# STEP 4: LOAD CACHE (IF EXISTS)
#
# Prevents re-downloading already
# processed KEGG records
# ==========================================================

if os.path.exists(CACHE_FILE):

    print("Loading existing cache...\n")

    with open(CACHE_FILE, "rb") as f:
        ko_cache = pickle.load(f)

else:

    print("No cache found → creating new cache\n")

    ko_cache = {}


# ==========================================================
# STEP 5: FUNCTION TO FETCH KEGG INFO
#
# Extracts:
# - Enzyme name
# - EC number
# - Pathways
# ==========================================================

def get_ko_info(ko_id):

    txt = REST.kegg_get(f"ko:{ko_id}").read()

    enzyme = ""
    ec = ""
    pathways = []

    for line in txt.split("\n"):

        # Enzyme name
        if line.startswith("NAME"):
            enzyme = line[12:].strip()


        # EC number
        if "EC:" in line:
            try:
                ec = line.split("EC:")[1].strip()
            except:
                pass


        # Pathway information
        if line.startswith("PATHWAY"):

            parts = line.split()

            if len(parts) >= 3:

                pathway_id = parts[1]

                pathway_name = " ".join(parts[2:])

                pathways.append(
                    (pathway_id, pathway_name)
                )

    return enzyme, ec, pathways


# ==========================================================
# STEP 6: FETCH KEGG DATA
# ==========================================================

records = []

counter = 0

print("Fetching KEGG annotations...\n")

for ko in unique_kos:

    counter += 1


    # ======================================================
    # USE CACHE IF AVAILABLE
    # ======================================================

    if ko in ko_cache:

        print(
            f"[{counter}/{len(unique_kos)}] "
            f"{ko} → Cached"
        )

        enzyme, ec, pathways = ko_cache[ko]


    # ======================================================
    # FETCH FROM KEGG SERVER
    # ======================================================

    else:

        try:

            print(
                f"[{counter}/{len(unique_kos)}] "
                f"Fetching {ko}...",
                end=" "
            )

            enzyme, ec, pathways = get_ko_info(ko)

            # Save to cache
            ko_cache[ko] = (
                enzyme,
                ec,
                pathways
            )

            print("OK")


        except Exception as e:

            print(f"ERROR: {e}")

            continue


        # ==================================================
        # SAVE CACHE EVERY 50 KOs
        # Prevents losing progress
        # ==================================================

        if counter % 50 == 0:

            with open(CACHE_FILE, "wb") as f:

                pickle.dump(
                    ko_cache,
                    f
                )

            print("Cache saved.")


        # ==================================================
        # KEGG RATE LIMIT
        # Avoid server blocking
        # ==================================================

        time.sleep(1)


    # ======================================================
    # MAP KO BACK TO ALL GENES
    # ======================================================

    temp = df[df["KO"] == ko]

    for _, row in temp.iterrows():

        gene = row["GeneID"]

        # One gene may belong to multiple pathways
        for pid, pname in pathways:

            records.append([

                gene,
                ko,
                enzyme,
                ec,
                pid,
                pname
            ])


# ==========================================================
# STEP 7: SAVE FINAL CACHE
# ==========================================================

with open(CACHE_FILE, "wb") as f:

    pickle.dump(
        ko_cache,
        f
    )

print("\nFinal cache saved.")


# ==========================================================
# STEP 8: BUILD FINAL TABLE
# ==========================================================

result = pd.DataFrame(

    records,

    columns=[
        "GeneID",
        "KO",
        "Enzyme",
        "EC",
        "PathwayID",
        "PathwayName"
    ]
)


# ==========================================================
# STEP 9: EXPORT TO EXCEL
# ==========================================================

result.to_excel(
    OUTPUT_FILE,
    index=False
)


# ==========================================================
# FINISHED
# ==========================================================

print("\nDONE ✔")

print("\nExcel file saved at:")

print(OUTPUT_FILE)
Install required packages first (if needed):
pip install biopython pandas openpyxl
Run:
python kegg_pathway_annotation.py
Expected output:
Total unique KO IDs = XXXX

Loading cache...

Fetching KEGG annotations...

[1/XXXX] K00844 → Cached
[2/XXXX] Fetching K00001... OK

Final cache saved.

DONE ✔


