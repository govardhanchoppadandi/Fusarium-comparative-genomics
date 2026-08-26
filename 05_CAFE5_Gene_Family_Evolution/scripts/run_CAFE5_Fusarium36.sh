#!/usr/bin/env bash

set -euo pipefail

# ============================================================
# CAFE5 STANDARDIZED PIPELINE
# Fusarium Comparative Genomics
#
# Workflow:
#   1. Check environment
#   2. Check CAFE input
#   3. Check original OrthoFinder tree
#   4. Midpoint root tree
#   5. Convert tree to ultrametric
#   6. Validate final tree
#   7. Run CAFE5
#   8. Check CAFE5 likelihood
#   9. Check output files
#  10. Final summary
#
# IMPORTANT:
#   - Original OrthoFinder tree is NEVER modified.
#   - CAFE5 estimates lambda itself.
#   - Do NOT manually force lambda unless specifically testing.
# ============================================================


echo
echo "============================================================"
echo "CAFE5 STANDARDIZED PIPELINE"
echo "============================================================"
echo


# ============================================================
# 1. ACTIVATE ENVIRONMENT
# ============================================================

source "$HOME/miniconda3/etc/profile.d/conda.sh"

conda activate orthofinder_clean

echo "Conda environment:"
echo "$CONDA_DEFAULT_ENV"

echo


# ============================================================
# 2. USER SETTINGS
# ============================================================

# ------------------------------------------------------------
# MAIN PROJECT DIRECTORY
# ------------------------------------------------------------

BASE="/mnt/d/ORTHOFINDER/CAFE_FUSARIUM36"


# ------------------------------------------------------------
# CAFE INPUT FILE
#
# This must contain the gene-family counts for all species.
# ------------------------------------------------------------

CAFE_INPUT="$BASE/CLEAN_CAFE_INPUT/Fusarium36_CAFE_input.txt"


# ------------------------------------------------------------
# ORIGINAL ORTHOFINDER SPECIES TREE
#
# IMPORTANT:
# Do not modify this file.
# ------------------------------------------------------------

ORIGINAL="/mnt/d/ORTHOFINDER/FUSARIUM36_FINAL/Results_Aug12_5/Species_Tree/SpeciesTree_rooted.txt"


# ------------------------------------------------------------
# TREE DIRECTORY
# ------------------------------------------------------------

TREE_DIR="$BASE/tree"


# ------------------------------------------------------------
# GENERATED TREES
# ------------------------------------------------------------

ROOTED="$TREE_DIR/Fusarium36_midpoint_rooted.nwk"

ULTRA="$TREE_DIR/Fusarium36_midpoint_rooted_ultrametric.nwk"


# ------------------------------------------------------------
# FINAL CAFE5 OUTPUT
# ------------------------------------------------------------

FULL="$BASE/FULL_CAFE5"


# ------------------------------------------------------------
# CAFE5 PROGRAM
# ------------------------------------------------------------

CAFE5="$HOME/miniconda3/envs/orthofinder_clean/bin/cafe5"


# ------------------------------------------------------------
# CPU THREADS
# ------------------------------------------------------------

THREADS=8


# ============================================================
# 3. CREATE DIRECTORIES
# ============================================================

mkdir -p "$TREE_DIR"
mkdir -p "$FULL"


# ============================================================
# 4. CHECK PROGRAMS
# ============================================================

echo
echo "============================================================"
echo "CHECKING PROGRAMS"
echo "============================================================"

if ! command -v Rscript >/dev/null 2>&1
then
    echo "ERROR: Rscript not found."
    exit 1
fi

if [ ! -x "$CAFE5" ]
then
    echo "ERROR: CAFE5 not found:"
    echo "$CAFE5"
    exit 1
fi

echo "Rscript:"
which Rscript

echo

echo "CAFE5:"
"$CAFE5" --version 2>&1 | head -5 || true


# ============================================================
# 5. CHECK R PACKAGES
# ============================================================

echo
echo "============================================================"
echo "CHECKING R PACKAGES"
echo "============================================================"

Rscript - <<'RS'

required <- c(
    "ape",
    "phangorn"
)

for (p in required) {

    if (!requireNamespace(p, quietly=TRUE)) {

        cat("ERROR: R package missing:", p, "\n")

        quit(
            save="no",
            status=1
        )

    }

    cat(p, "OK\n")
}

cat("\nALL TREE PACKAGES OK\n")

RS


# ============================================================
# 6. CHECK INPUT FILES
# ============================================================

echo
echo "============================================================"
echo "CHECKING INPUT FILES"
echo "============================================================"

if [ ! -f "$CAFE_INPUT" ]
then
    echo "ERROR: CAFE input does not exist:"
    echo "$CAFE_INPUT"
    exit 1
fi

if [ ! -f "$ORIGINAL" ]
then
    echo "ERROR: Original OrthoFinder tree does not exist:"
    echo "$ORIGINAL"
    exit 1
fi

echo "CAFE input:"
ls -lh "$CAFE_INPUT"

echo

echo "Original OrthoFinder tree:"
ls -lh "$ORIGINAL"


# ============================================================
# 7. CHECK NUMBER OF TAXA IN TREE
# ============================================================

echo
echo "============================================================"
echo "CHECKING ORIGINAL TREE"
echo "============================================================"

Rscript - "$ORIGINAL" <<'RS'

library(ape)

tree_file <- commandArgs(trailingOnly=TRUE)[1]

tr <- read.tree(tree_file)

cat("Tips:   ", Ntip(tr), "\n")
cat("Nodes:  ", Nnode(tr), "\n")
cat("Binary: ", is.binary(tr), "\n")
cat("Rooted: ", is.rooted(tr), "\n")

if (Ntip(tr) != 36) {

    stop(
        "ERROR: Expected 36 taxa but found ",
        Ntip(tr)
    )

}

if (!is.binary(tr)) {

    stop("ERROR: Original tree is not binary.")

}

cat("\nORIGINAL TREE CHECK PASSED\n")

RS


# ============================================================
# 8. CREATE MIDPOINT-ROOTED TREE
# ============================================================

echo
echo "============================================================"
echo "MIDPOINT ROOTING"
echo "============================================================"

Rscript - "$ORIGINAL" "$ROOTED" <<'RS'

library(ape)
library(phangorn)

args <- commandArgs(trailingOnly=TRUE)

original <- args[1]
rooted   <- args[2]

cat("\nReading original OrthoFinder tree...\n")

tr <- read.tree(original)

cat("Original tips:", Ntip(tr), "\n")
cat("Original nodes:", Nnode(tr), "\n")

if (Ntip(tr) != 36) {
    stop("ERROR: Tree does not contain 36 taxa.")
}

if (!is.binary(tr)) {
    stop("ERROR: Tree is not binary.")
}

cat("\nPerforming midpoint rooting...\n")

tr_rooted <- phangorn::midpoint(tr)

if (!is.rooted(tr_rooted)) {
    stop("ERROR: Midpoint rooting failed.")
}

if (!is.binary(tr_rooted)) {
    stop("ERROR: Rooted tree is not binary.")
}

if (Ntip(tr_rooted) != 36) {
    stop("ERROR: Rooted tree does not contain 36 taxa.")
}

write.tree(
    tr_rooted,
    file=rooted
)

cat("\nROOTED TREE CREATED:\n")
cat(rooted, "\n")

cat("\nTips:", Ntip(tr_rooted), "\n")
cat("Nodes:", Nnode(tr_rooted), "\n")
cat("Rooted:", is.rooted(tr_rooted), "\n")
cat("Binary:", is.binary(tr_rooted), "\n")

RS


# ============================================================
# 9. CREATE ULTRAMETRIC TREE
# ============================================================

echo
echo "============================================================"
echo "CREATING ULTRAMETRIC TREE"
echo "============================================================"

Rscript - "$ROOTED" "$ULTRA" <<'RS'

library(ape)

args <- commandArgs(trailingOnly=TRUE)

rooted <- args[1]
ultra  <- args[2]

tr <- read.tree(rooted)

cat("Rooted:", is.rooted(tr), "\n")
cat("Binary:", is.binary(tr), "\n")

if (!is.rooted(tr)) {
    stop("ERROR: Input tree is not rooted.")
}

if (!is.binary(tr)) {
    stop("ERROR: Input tree is not binary.")
}

cat("\nFitting ultrametric tree using chronos...\n")

# ------------------------------------------------------------
# Penalized-likelihood dating
# ------------------------------------------------------------

tr_ultra <- chronos(
    tr,
    lambda=1
)

# ------------------------------------------------------------
# Normalize root-to-tip distance
# ------------------------------------------------------------

root_to_tip <- cophenetic(tr_ultra)

# use actual root-to-tip distances through node depths
d <- dist.nodes(tr_ultra)

tip_numbers <- 1:Ntip(tr_ultra)

# ------------------------------------------------------------
# Direct ultrametric normalization
# ------------------------------------------------------------

tip_dist <- numeric(Ntip(tr_ultra))

for (i in seq_len(Ntip(tr_ultra))) {

    path <- nodepath(
        tr_ultra,
        tr_ultra$edge[1,1],
        i
    )

    tip_dist[i] <- sum(
        tr_ultra$edge.length[
            match(
                path[-length(path)],
                tr_ultra$edge[,2]
            )
        ],
        na.rm=TRUE
    )
}

target <- mean(tip_dist)

# Scale all branches equally
tr_ultra$edge.length <-
    tr_ultra$edge.length / target


# ------------------------------------------------------------
# Final ultrametric correction
# ------------------------------------------------------------

tip_dist2 <- numeric(Ntip(tr_ultra))

for (i in seq_len(Ntip(tr_ultra))) {

    path <- nodepath(
        tr_ultra,
        tr_ultra$edge[1,1],
        i
    )

    tip_dist2[i] <- sum(
        tr_ultra$edge.length[
            match(
                path[-length(path)],
                tr_ultra$edge[,2]
            )
        ],
        na.rm=TRUE
    )
}

# ------------------------------------------------------------
# Write tree
# ------------------------------------------------------------

write.tree(
    tr_ultra,
    file=ultra
)


# ============================================================
# FINAL TREE CHECK
# ============================================================

cat("\n============================================================\n")
cat("FINAL TREE CHECK\n")
cat("============================================================\n")

cat("Tips:        ", Ntip(tr_ultra), "\n")
cat("Nodes:       ", Nnode(tr_ultra), "\n")
cat("Rooted:      ", is.rooted(tr_ultra), "\n")
cat("Binary:      ", is.binary(tr_ultra), "\n")
cat("Ultrametric: ", is.ultrametric(tr_ultra), "\n")

# ------------------------------------------------------------
# root-to-tip distances using ape
# ------------------------------------------------------------

depths <- node.depth.edgelength(tr_ultra)

tip_depths <- depths[seq_len(Ntip(tr_ultra))]

cat("\nRoot-to-tip distances:\n")
cat("Minimum:", min(tip_depths), "\n")
cat("Maximum:", max(tip_depths), "\n")
cat("Difference:",
    max(tip_depths)-min(tip_depths),
    "\n"
)

# ------------------------------------------------------------
# strict checks
# ------------------------------------------------------------

if (Ntip(tr_ultra) != 36) {
    stop("ERROR: Final tree does not contain 36 taxa.")
}

if (!is.rooted(tr_ultra)) {
    stop("ERROR: Final tree is not rooted.")
}

if (!is.binary(tr_ultra)) {
    stop("ERROR: Final tree is not binary.")
}

if (!is.ultrametric(tr_ultra)) {
    stop("ERROR: Final tree is not ultrametric.")
}

if (min(tr_ultra$edge.length) <= 0) {
    stop("ERROR: Tree contains zero/negative branch lengths.")
}

cat("\nSUCCESS — FINAL CAFE TREE CREATED\n")
cat(ultra, "\n")

RS


# ============================================================
# 10. EXTREME BRANCH DIAGNOSTIC
# ============================================================

echo
echo "============================================================"
echo "BRANCH-LENGTH DIAGNOSTIC"
echo "============================================================"

Rscript - "$ULTRA" <<'RS'

library(ape)

tree_file <- commandArgs(trailingOnly=TRUE)[1]

tr <- read.tree(tree_file)

bl <- tr$edge.length

cat("\nTips:", Ntip(tr), "\n")
cat("Nodes:", Nnode(tr), "\n")
cat("Rooted:", is.rooted(tr), "\n")
cat("Binary:", is.binary(tr), "\n")
cat("Ultrametric:", is.ultrametric(tr), "\n")

cat("\nMinimum branch:", min(bl), "\n")
cat("Maximum branch:", max(bl), "\n")
cat("Mean branch:", mean(bl), "\n")
cat("Median branch:", median(bl), "\n")

cat("\nBranches < 1e-4:",
    sum(bl < 1e-4),
    "\n"
)

cat("\nSmallest branches:\n")

print(
    sort(bl)[1:min(20,length(bl))]
)

cat("\nRoot-to-tip distances:\n")

depths <- node.depth.edgelength(tr)

tip_depths <- depths[seq_len(Ntip(tr))]

cat("Minimum:",
    min(tip_depths),
    "\n"
)

cat("Maximum:",
    max(tip_depths),
    "\n"
)

cat("Difference:",
    max(tip_depths)-min(tip_depths),
    "\n"
)

RS


# ============================================================
# 11. BACKUP OLD CAFE OUTPUT
# ============================================================

echo
echo "============================================================"
echo "PREPARING CAFE5 OUTPUT DIRECTORY"
echo "============================================================"

if [ -d "$FULL" ] &&
   [ "$(find "$FULL" -type f | wc -l)" -gt 0 ]
then

    BACKUP="$FULL/previous_$(date +%Y%m%d_%H%M%S)"

    echo "Existing output detected."
    echo "Moving old output to:"
    echo "$BACKUP"

    mkdir -p "$BACKUP"

    find "$FULL" -maxdepth 1 -type f \
        -exec mv {} "$BACKUP"/ \;

fi


# ============================================================
# 12. RUN CAFE5
# ============================================================

echo
echo "============================================================"
echo "RUNNING CAFE5"
echo "============================================================"

echo
echo "CAFE input:"
echo "$CAFE_INPUT"

echo
echo "Tree:"
echo "$ULTRA"

echo
echo "Output:"
echo "$FULL"

echo
echo "Threads:"
echo "$THREADS"

echo


"$CAFE5" \
    -i "$CAFE_INPUT" \
    -t "$ULTRA" \
    -o "$FULL" \
    -p \
    -P 0.05 \
    -c "$THREADS"


CAFE_STATUS=$?


# ============================================================
# 13. CHECK CAFE5 EXIT STATUS
# ============================================================

echo
echo "============================================================"
echo "CAFE5 STATUS"
echo "============================================================"

echo "Exit status: $CAFE_STATUS"

if [ "$CAFE_STATUS" -ne 0 ]
then

    echo
    echo "ERROR: CAFE5 failed."
    echo
    echo "Last 50 lines of log:"
    tail -50 "$FULL/cafe.log" 2>/dev/null || true

    exit "$CAFE_STATUS"

fi


# ============================================================
# 14. CHECK BASE RESULTS
# ============================================================

echo
echo "============================================================"
echo "CHECKING BASE RESULTS"
echo "============================================================"

if [ ! -f "$FULL/Base_results.txt" ]
then

    echo "ERROR: Base_results.txt was not created."

    exit 1

fi

cat "$FULL/Base_results.txt"


# ============================================================
# 15. CHECK FOR INF
# ============================================================

echo
echo "============================================================"
echo "CHECKING LIKELIHOOD"
echo "============================================================"

if grep -qi "inf" "$FULL/Base_results.txt"
then

    echo
    echo "============================================================"
    echo "ERROR — CAFE5 RETURNED INF"
    echo "============================================================"

    echo
    echo "This run must NOT be used for biological interpretation."

    echo
    echo "Last 50 lines of CAFE log:"
    tail -50 "$FULL/cafe.log"

    exit 1

fi

echo "Finite likelihood detected."
echo "CAFE5 likelihood check PASSED."


# ============================================================
# 16. CHECK REQUIRED OUTPUT FILES
# ============================================================

echo
echo "============================================================"
echo "CHECKING CAFE5 OUTPUT FILES"
echo "============================================================"

REQUIRED_FILES=(

    "Base_results.txt"
    "Base_family_likelihoods.txt"
    "Base_family_results.txt"
    "Base_asr.tre"
    "Base_change.tab"
    "Base_count.tab"
    "Base_clade_results.txt"
    "Base_branch_probabilities.tab"
    "Base_report.cafe"
    "cafe.log"

)


FAIL=0

for FILE in "${REQUIRED_FILES[@]}"
do

    if [ -f "$FULL/$FILE" ] &&
       [ -s "$FULL/$FILE" ]
    then

        SIZE=$(du -h "$FULL/$FILE" | cut -f1)

        echo "OK    $FILE    $SIZE"

    else

        echo "MISS  $FILE"

        FAIL=1

    fi

done


if [ "$FAIL" -ne 0 ]
then

    echo
    echo "ERROR: One or more expected CAFE5 files are missing."

    exit 1

fi


# ============================================================
# 17. DISPLAY FINAL CAFE5 LOG
# ============================================================

echo
echo "============================================================"
echo "FINAL CAFE5 LOG"
echo "============================================================"

tail -40 "$FULL/cafe.log"


# ============================================================
# 18. DISPLAY CLADE RESULTS
# ============================================================

echo
echo "============================================================"
echo "CLADE RESULTS"
echo "============================================================"

cat "$FULL/Base_clade_results.txt"


# ============================================================
# 19. DISPLAY FIRST LINES OF CHANGE FILE
# ============================================================

echo
echo "============================================================"
echo "CHANGE FILE — FIRST 10 LINES"
echo "============================================================"

head -10 "$FULL/Base_change.tab"


# ============================================================
# 20. DISPLAY FIRST LINES OF COUNT FILE
# ============================================================

echo
echo "============================================================"
echo "COUNT FILE — FIRST 10 LINES"
echo "============================================================"

head -10 "$FULL/Base_count.tab"


# ============================================================
# 21. DISPLAY ASR TREE HEADER
# ============================================================

echo
echo "============================================================"
echo "ASR TREE CHECK"
echo "============================================================"

head -5 "$FULL/Base_asr.tre"


# ============================================================
# 22. FINAL FILE SUMMARY
# ============================================================

echo
echo "============================================================"
echo "FINAL CAFE5 OUTPUT"
echo "============================================================"

find "$FULL" \
    -maxdepth 1 \
    -type f \
    -printf "%s bytes\t%f\n" \
    | sort -k2


# ============================================================
# 23. FINAL RESULT
# ============================================================

echo
echo
echo "============================================================"
echo "CAFE5 ANALYSIS COMPLETED SUCCESSFULLY"
echo "============================================================"

echo
echo "CAFE INPUT:"
echo "$CAFE_INPUT"

echo
echo "FINAL TREE:"
echo "$ULTRA"

echo
echo "CAFE5 OUTPUT:"
echo "$FULL"

echo
echo "MAIN FILES:"
echo
echo "ASR tree:"
echo "$FULL/Base_asr.tre"

echo
echo "Gene-family changes:"
echo "$FULL/Base_change.tab"

echo
echo "Ancestral counts:"
echo "$FULL/Base_count.tab"

echo
echo "Clade results:"
echo "$FULL/Base_clade_results.txt"

echo
echo "Family results:"
echo "$FULL/Base_family_results.txt"

echo
echo "Branch probabilities:"
echo "$FULL/Base_branch_probabilities.tab"

echo
echo "CAFE report:"
echo "$FULL/Base_report.cafe"

echo
echo "CAFE log:"
echo "$FULL/cafe.log"

echo
echo "============================================================"
echo "DONE"
echo "============================================================"
