# ============================================================
# FUSARIUM 36 — FINAL CIRCOS PNG + PDF
# ============================================================
#
# READ ONLY:
# D:/ORTHOFINDER/FUSARIUM36_FINAL/Results_Aug12_5
#
# OUTPUT:
# D:/ORTHOFINDER/FUSARIUM36_ORTHOFINDER_PLOTS
#
# ============================================================

library(circlize)

OUT <- "D:/ORTHOFINDER/FUSARIUM36_ORTHOFINDER_PLOTS"

dir.create(
    OUT,
    recursive = TRUE,
    showWarnings = FALSE
)

# ============================================================
# CHECK REQUIRED OBJECTS
# ============================================================

required_objects <- c(
    "presence",
    "species_order",
    "species_group",
    "pairwise_df"
)

missing_objects <- required_objects[
    !vapply(
        required_objects,
        exists,
        logical(1)
    )
]

if (length(missing_objects) > 0) {

    stop(
        paste(
            "Missing objects:",
            paste(
                missing_objects,
                collapse = ", "
            )
        )
    )

}

# ============================================================
# FORCE EXACT ORDER
# ============================================================

species_order <- unname(
    species_order
)

# ============================================================
# CHECK 36 GENOMES
# ============================================================

if (length(species_order) != 36) {

    stop(
        paste(
            "Expected 36 genomes, found",
            length(species_order)
        )
    )

}

# ============================================================
# CHECK PRESENCE MATRIX
# ============================================================

missing <- setdiff(
    species_order,
    colnames(presence)
)

if (length(missing) > 0) {

    stop(
        paste(
            "These genomes are missing from presence matrix:",
            paste(
                missing,
                collapse = ", "
            )
        )
    )

}

# ============================================================
# HIGH-CONFIDENCE LINKS
# ============================================================
#
# Initial strict criterion
#
# Jaccard >= 0.80
# Shared orthogroups >= 9000
#
# ============================================================

JACCARD_THRESHOLD <- 0.80

SHARED_THRESHOLD <- 9000

links <- pairwise_df[
    pairwise_df$Jaccard >=
        JACCARD_THRESHOLD &
    pairwise_df$Shared_Orthogroups >=
        SHARED_THRESHOLD,
    ,
    drop = FALSE
]

cat("\n============================================================\n")
cat("CIRCOS LINK CHECK\n")
cat("============================================================\n")

cat(
    "Strict links:",
    nrow(links),
    "\n"
)

# ============================================================
# IF TOO FEW LINKS, USE TOP HIGH-SIMILARITY LINKS
# ============================================================
#
# This prevents an empty/near-empty Circos figure.
#
# We do NOT use weak random links.
#
# ============================================================

if (nrow(links) < 15) {

    cat(
        "\nStrict threshold produced fewer than 15 links.\n"
    )

    cat(
        "Selecting the strongest 40 pairwise relationships.\n"
    )

    links <- pairwise_df[
        order(
            -pairwise_df$Jaccard,
            -pairwise_df$Shared_Orthogroups
        ),
        ,
        drop = FALSE
    ]

    links <- head(
        links,
        40
    )

    links$HighConfidenceSelection <-
        "Top_40_Jaccard"

} else {

    links$HighConfidenceSelection <-
        "Jaccard_0.80_Shared_9000"

}

cat(
    "Final ribbons:",
    nrow(links),
    "\n"
)

# ============================================================
# SAVE LINK TABLE
# ============================================================

write.csv(
    links,
    file.path(
        OUT,
        "Fusarium36_Circos_Final_Links.csv"
    ),
    row.names = FALSE
)

# ============================================================
# GENOME ORTHOGROUP COUNTS
# ============================================================

genome_og_count <- colSums(
    presence[
        ,
        species_order,
        drop = FALSE
    ]
)

max_og <- max(
    genome_og_count
)

# ============================================================
# DRAWING FUNCTION
# ============================================================

draw_circos <- function() {

    # --------------------------------------------------------
    # CLEAR ANY OLD CIRCLIZE STATE
    # --------------------------------------------------------

    circos.clear()

    # --------------------------------------------------------
    # PARAMETERS
    # --------------------------------------------------------

    circos.par(
        start.degree = 90,

        gap.degree = 3,

        track.margin = c(
            0.005,
            0.005
        ),

        cell.padding = c(
            0,
            0,
            0,
            0
        ),

        points.overflow.warning = FALSE
    )

    # --------------------------------------------------------
    # INITIALIZE
    # --------------------------------------------------------

    circos.initialize(
        factors = species_order,

        xlim = matrix(
            c(0, 1),
            nrow = length(
                species_order
            ),
            ncol = 2,
            byrow = TRUE,

            dimnames = list(
                species_order,
                c(
                    "start",
                    "end"
                )
            )
        )
    )

    # ========================================================
    # TRACK 1 — GENOME NAMES
    # ========================================================

    circos.trackPlotRegion(
        ylim = c(0, 1),

        track.height = 0.10,

        bg.border = NA,

        panel.fun = function(
            x,
            y
        ) {

            sp <-
                CELL_META$sector.index

            circos.text(
                x = 0.5,

                y = 0.5,

                labels = sp,

                facing = "clockwise",

                niceFacing = TRUE,

                cex = 0.38,

                font = 2
            )

        }
    )

    # ========================================================
    # TRACK 2 — SPECIES GROUP BAR
    # ========================================================

    circos.trackPlotRegion(
        ylim = c(0, 1),

        track.height = 0.045,

        bg.border = NA,

        panel.fun = function(
            x,
            y
        ) {

            sp <-
                CELL_META$sector.index

            grp <-
                species_group[sp]

            if (
                grp ==
                "F. graminearum"
            ) {

                col <- "#D55E00"

            } else {

                col <- "#0072B2"

            }

            circos.rect(
                xleft = 0,

                ybottom = 0,

                xright = 1,

                ytop = 1,

                col = col,

                border = NA
            )

        }
    )

    # ========================================================
    # TRACK 3 — ORTHOGROUP CONTENT
    # ========================================================

    circos.trackPlotRegion(
        ylim = c(
            0,
            max_og
        ),

        track.height = 0.07,

        bg.border = NA,

        panel.fun = function(
            x,
            y
        ) {

            sp <-
                CELL_META$sector.index

            value <-
                genome_og_count[sp]

            circos.rect(
                xleft = 0,

                ybottom = 0,

                xright = 1,

                ytop = value,

                col = "grey55",

                border = NA
            )

        }
    )

    # ========================================================
    # HIGH-CONFIDENCE RIBBONS
    # ========================================================

    for (k in seq_len(
        nrow(links)
    )) {

        sp1 <-
            links$Species1[k]

        sp2 <-
            links$Species2[k]

        jaccard <-
            links$Jaccard[k]

        g1 <-
            species_group[sp1]

        g2 <-
            species_group[sp2]

        # ----------------------------------------------------
        # RIBBON COLOR
        # ----------------------------------------------------

        if (
            g1 ==
                "F. graminearum" &&
            g2 ==
                "F. graminearum"
        ) {

            ribbon_col <-
                adjustcolor(
                    "#D55E00",
                    alpha.f = 0.30
                )

        } else if (
            g1 ==
                "F. avenaceum" &&
            g2 ==
                "F. avenaceum"
        ) {

            ribbon_col <-
                adjustcolor(
                    "#0072B2",
                    alpha.f = 0.30
                )

        } else {

            ribbon_col <-
                adjustcolor(
                    "#7B3294",
                    alpha.f = 0.38
                )

        }

        # ----------------------------------------------------
        # WIDTH
        # ----------------------------------------------------

        if (
            jaccard >=
            JACCARD_THRESHOLD
        ) {

            width <- 0.10

        } else {

            width <- 0.07

        }

        # ----------------------------------------------------
        # RIBBON
        # ----------------------------------------------------

        circos.link(
            sector.index1 = sp1,

            point1 = c(
                0.35,
                0.35 + width
            ),

            sector.index2 = sp2,

            point2 = c(
                0.35,
                0.35 + width
            ),

            col = ribbon_col,

            border = NA
        )

    }

    # ========================================================
    # TITLE
    # ========================================================

    title(
        main =
            "Orthogroup Similarity Among 36 Fusarium Genomes",

        cex.main = 1.35
    )

    # ========================================================
    # LEGEND
    # ========================================================

    legend(
        "topleft",

        legend = c(
            "F. graminearum",
            "F. avenaceum",
            "Between-species similarity"
        ),

        fill = c(
            "#D55E00",
            "#0072B2",
            "#7B3294"
        ),

        border = NA,

        bty = "n",

        cex = 0.80
    )

}

# ============================================================
# PNG
# ============================================================

PNG_FILE <- file.path(
    OUT,
    "Fusarium36_Circos_HighConfidence.png"
)

cat("\nCreating PNG:\n")
cat(PNG_FILE, "\n")

png(
    filename = PNG_FILE,

    width = 4000,

    height = 4000,

    res = 400,

    type = "cairo"
)

draw_circos()

dev.off()

circos.clear()

# ============================================================
# PDF
# ============================================================

PDF_FILE <- file.path(
    OUT,
    "Fusarium36_Circos_HighConfidence.pdf"
)

cat("\nCreating PDF:\n")
cat(PDF_FILE, "\n")

pdf(
    file = PDF_FILE,

    width = 12,

    height = 12,

    useDingbats = FALSE
)

draw_circos()

dev.off()

circos.clear()

# ============================================================
# VERIFY FILES
# ============================================================

cat("\n============================================================\n")
cat("CIRCOS OUTPUT CHECK\n")
cat("============================================================\n")

if (!file.exists(PNG_FILE)) {

    stop("ERROR: PNG was not created.")

}

if (!file.exists(PDF_FILE)) {

    stop("ERROR: PDF was not created.")

}

cat(
    "\nPNG created:\n"
)

print(
    file.info(PNG_FILE)[
        ,
        c(
            "size",
            "mtime"
        )
    ]
)

cat(
    "\nPDF created:\n"
)

print(
    file.info(PDF_FILE)[
        ,
        c(
            "size",
            "mtime"
        )
    ]
)

cat("\n============================================================\n")
cat("DONE\n")
cat("============================================================\n")

cat(
    "\nPNG:\n",
    PNG_FILE,
    "\n"
)

cat(
    "\nPDF:\n",
    PDF_FILE,
    "\n"
)

cat(
    "\nRibbons:",
    nrow(links),
    "\n"
)

cat(
    "\nOrthoFinder results were READ ONLY.\n"
)
