#!/bin/bash

# ============================================================
# FUSARIUM RIP ANALYSIS PIPELINE
# ============================================================
#
# Input genomes:
#   /mnt/d/genomes_clean/*.fna
#
# TE annotations:
#   /mnt/d/genomes_clean/TE_analysis/
#
# RIPCAL:
#   RIPCAL 2.0
#
# BEDTools:
#   2.31.1
#
# RIP scan:
#   Window = 1000 bp
#   Step   = 500 bp
#
# Output:
#   Each genome gets its own:
#
#   GENOME/
#       RIP_analysis/
#
# ============================================================

set -u

# ------------------------------------------------------------
# WORKING DIRECTORY
# ------------------------------------------------------------

BASE="/mnt/d/genomes_clean"

cd "$BASE" || exit 1


# ------------------------------------------------------------
# SOFTWARE
# ------------------------------------------------------------

RIPCAL=$(which ripcal)
BEDTOOLS=$(which bedtools)

echo "============================================================"
echo "        FUSARIUM RIP ANALYSIS PIPELINE"
echo "============================================================"

echo "Working directory:"
echo "$BASE"

echo ""
echo "RIPCAL:"
echo "$RIPCAL"

echo ""
echo "BEDTOOLS:"
echo "$BEDTOOLS"

echo ""


# ------------------------------------------------------------
# CHECK SOFTWARE
# ------------------------------------------------------------

if [ ! -x "$RIPCAL" ]; then
    echo "ERROR: RIPCAL not found."
    echo "Activate ripcal_env first:"
    echo "conda activate ripcal_env"
    exit 1
fi

if [ ! -x "$BEDTOOLS" ]; then
    echo "ERROR: BEDTools not found."
    exit 1
fi


# ------------------------------------------------------------
# FUNCTION
# ------------------------------------------------------------

run_rip () {

    GENOME="$1"

    NAME="${GENOME%.*}"

    OUTDIR="$BASE/$NAME/RIP_analysis"

    echo ""
    echo "============================================================"
    echo "Starting RIP analysis: $NAME"
    echo "============================================================"

    echo "Genome:"
    echo "$BASE/$GENOME"

    echo "Output:"
    echo "$OUTDIR"

    mkdir -p "$OUTDIR"


    # --------------------------------------------------------
    # SKIP IF ALREADY COMPLETED
    # --------------------------------------------------------

    if [ -s "$OUTDIR/${NAME}_RIP.bed" ] &&
       [ -s "$OUTDIR/${NAME}_LRAR.bed" ]; then

        echo ""
        echo "RIP analysis already completed:"
        echo "$NAME"

        echo "Skipping..."

        return

    fi


    # --------------------------------------------------------
    # FIND EARLGREY TE BED
    # --------------------------------------------------------

    TE_BED=$(find "$BASE/TE_analysis/$NAME" \
        -type f \
        -name "${NAME}.filteredRepeats.bed" \
        -path "*mergedRepeats/looseMerge/*" \
        | head -n 1)


    echo ""
    echo "TE BED:"
    echo "${TE_BED:-NOT FOUND}"


    # --------------------------------------------------------
    # TEMPORARY DIRECTORY
    # --------------------------------------------------------

    TMPDIR=$(mktemp -d)

    cd "$TMPDIR" || exit 1


    # --------------------------------------------------------
    # RUN RIPCAL
    # --------------------------------------------------------

    echo ""
    echo "Running RIPCAL..."
    echo "Window = 1000 bp"
    echo "Step   = 500 bp"
    echo ""

    "$RIPCAL" \
        -c \
        -seq "$BASE/$GENOME" \
        -type scan \
        -l 1000 \
        -i 500


    # --------------------------------------------------------
    # FIND RIPCAL OUTPUT
    # --------------------------------------------------------

    SCANFILE=$(find "$TMPDIR" \
        -maxdepth 1 \
        -type f \
        -name "*_scan.txt" \
        | head -n 1)


    if [ -z "$SCANFILE" ]; then

        echo ""
        echo "ERROR: RIPCAL did not produce a scan file."
        echo "Genome: $NAME"

        cd "$BASE"

        rm -rf "$TMPDIR"

        return

    fi


    # --------------------------------------------------------
    # SAVE RAW RIPCAL OUTPUT
    # --------------------------------------------------------

    cp "$SCANFILE" \
        "$OUTDIR/${NAME}_RIP_raw_scan.txt"


    # --------------------------------------------------------
    # CONVERT RIPCAL GFF-LIKE OUTPUT TO BED
    #
    # RIPCAL output:
    #
    # seqid source type start end score strand phase attributes
    #
    # BED:
    #
    # seqid start end
    #
    # RIPCAL uses 1-based coordinates.
    # BED uses 0-based start coordinates.
    #
    # Therefore:
    #
    # BED start = RIPCAL start - 1
    # BED end   = RIPCAL end
    # --------------------------------------------------------

    awk 'BEGIN{OFS="\t"}
    $0 !~ /^#/ && NF >= 5 {
        start=$4-1
        if(start < 0) start=0
        print $1,start,$5
    }' \
        "$SCANFILE" \
        > "$OUTDIR/${NAME}_RIP.bed"


    # --------------------------------------------------------
    # SORT RIP BED
    # --------------------------------------------------------

    "$BEDTOOLS" sort \
        -i "$OUTDIR/${NAME}_RIP.bed" \
        > "$OUTDIR/${NAME}_RIP_sorted.bed"


    mv \
        "$OUTDIR/${NAME}_RIP_sorted.bed" \
        "$OUTDIR/${NAME}_RIP.bed"


    # --------------------------------------------------------
    # RIP REGION COUNT
    # --------------------------------------------------------

    RIP_COUNT=$(wc -l < \
        "$OUTDIR/${NAME}_RIP.bed")

    echo ""
    echo "RIP regions detected: $RIP_COUNT"


    # --------------------------------------------------------
    # MERGE OVERLAPPING / ADJACENT RIP WINDOWS
    #
    # These merged regions are treated as
    # large RIP affected regions (LRARs).
    # --------------------------------------------------------

    "$BEDTOOLS" merge \
        -i "$OUTDIR/${NAME}_RIP.bed" \
        > "$OUTDIR/${NAME}_LRAR.bed"


    LRAR_COUNT=$(wc -l < \
        "$OUTDIR/${NAME}_LRAR.bed")

    echo "Merged LRAR regions: $LRAR_COUNT"


    # --------------------------------------------------------
    # RIP REGIONS TSV
    # --------------------------------------------------------

    awk 'BEGIN{OFS="\t"}
    {
        print $1,$2,$3
    }' \
        "$OUTDIR/${NAME}_LRAR.bed" \
        > "$OUTDIR/${NAME}_RIP_regions.tsv"


    # --------------------------------------------------------
    # RIP–TE INTERSECTION
    # --------------------------------------------------------

    if [ -s "$TE_BED" ]; then

        "$BEDTOOLS" sort \
            -i "$TE_BED" \
            > "$TMPDIR/TE_sorted.bed"


        "$BEDTOOLS" intersect \
            -a "$OUTDIR/${NAME}_LRAR.bed" \
            -b "$TMPDIR/TE_sorted.bed" \
            -wa \
            -wb \
            > "$OUTDIR/${NAME}_RIP_TE_overlap.txt"


        TE_OVERLAP=$(cut -f1-3 \
            "$OUTDIR/${NAME}_RIP_TE_overlap.txt" \
            | sort -u \
            | wc -l)


        echo ""
        echo "RIP–TE overlap completed."
        echo "LRARs overlapping TEs: $TE_OVERLAP"

    else

        echo ""
        echo "WARNING:"
        echo "TE BED not found."
        echo "RIP–TE intersection skipped."

        touch "$OUTDIR/${NAME}_RIP_TE_overlap.txt"

    fi


    # --------------------------------------------------------
    # CLEAN TEMPORARY FILES
    # --------------------------------------------------------

    cd "$BASE"

    rm -rf "$TMPDIR"


    # --------------------------------------------------------
    # COMPLETION
    # --------------------------------------------------------

    echo ""
    echo "------------------------------------------------------------"
    echo "COMPLETED: $NAME"
    echo "------------------------------------------------------------"

    echo "Raw RIPCAL:"
    echo "$OUTDIR/${NAME}_RIP_raw_scan.txt"

    echo ""
    echo "RIP BED:"
    echo "$OUTDIR/${NAME}_RIP.bed"

    echo ""
    echo "LRAR:"
    echo "$OUTDIR/${NAME}_LRAR.bed"

    echo ""
    echo "RIP regions:"
    echo "$OUTDIR/${NAME}_RIP_regions.tsv"

    echo ""
    echo "RIP–TE overlap:"
    echo "$OUTDIR/${NAME}_RIP_TE_overlap.txt"

    echo "------------------------------------------------------------"

}


# ============================================================
# RUN ALL GENOMES
# ============================================================

for GENOME in \
    *.fna
do

    [ -f "$GENOME" ] || continue

    run_rip "$GENOME"

done


# ============================================================
# FINAL SUMMARY
# ============================================================

echo ""
echo "============================================================"
echo "                 RIP ANALYSIS COMPLETE"
echo "============================================================"

echo ""

TOTAL=$(find "$BASE" \
    -mindepth 2 \
    -maxdepth 2 \
    -type f \
    -name "*_RIP.bed" \
    | wc -l)

LRAR_TOTAL=$(find "$BASE" \
    -mindepth 2 \
    -maxdepth 2 \
    -type f \
    -name "*_LRAR.bed" \
    | wc -l)

echo "Completed RIP BED files : $TOTAL"
echo "Completed LRAR files    : $LRAR_TOTAL"

echo ""
echo "Output directories:"
echo ""

find "$BASE" \
    -mindepth 2 \
    -maxdepth 2 \
    -type d \
    -name "RIP_analysis" \
    | sort

echo ""
echo "============================================================"
echo "DONE"
echo "============================================================"
