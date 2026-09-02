# ============================================================
# FUSARIUM 36 - CAFE5 FINAL PUBLICATION FIGURE
# ============================================================
#
# 36 Fusarium genomes
# 35 internal nodes
# 70 CAFE5 rows
#
# TREE / BRANCH MODEL PRESERVED
#
# FINAL DESIGN:
#   - Internal pies remain at their tree nodes
#   - Internal + / - values are placed beside each pie
#   - Leader lines connect values to pies
#   - Crowded labels are separated vertically
#   - Tip pies and genome names remain on right
# ============================================================


# ============================================================
# LOAD PACKAGE
# ============================================================

library(ape)

options(
  stringsAsFactors = FALSE
)


# ============================================================
# FILE PATHS
# ============================================================

TREE_FILE <- "/mnt/d/ORTHOFINDER/CAFE_FUSARIUM36/tree/Fusarium36_midpoint_rooted_ultrametric.nwk"

CAFE_FILE <- "/mnt/d/ORTHOFINDER/CAFE_FUSARIUM36/FULL_CAFE5/Base_clade_results.txt"

OUT_DIR <- "/mnt/d/ORTHOFINDER/CAFE_FUSARIUM36/CAFE5_FIGURES"


# ============================================================
# OUTPUT DIRECTORY
# ============================================================

dir.create(
  OUT_DIR,
  recursive = TRUE,
  showWarnings = FALSE
)


PNG_FILE <- file.path(
  OUT_DIR,
  "Fusarium36_CAFE5_FINAL_PUBLICATION.png"
)


PDF_FILE <- file.path(
  OUT_DIR,
  "Fusarium36_CAFE5_FINAL_PUBLICATION.pdf"
)


TSV_FILE <- file.path(
  OUT_DIR,
  "Fusarium36_CAFE5_FINAL_PUBLICATION_annotations.tsv"
)


# ============================================================
# COLORS
# ============================================================

EXPANSION <- "#E64B35"

CONTRACTION <- "#35AFC5"

TREECOL <- "#333333"

TEXTCOL <- "#333333"

LEADERCOL <- "#777777"


# ============================================================
# START
# ============================================================

cat("\n")
cat("============================================================\n")
cat("FUSARIUM 36 - CAFE5 PUBLICATION FIGURE\n")
cat("============================================================\n")


# ============================================================
# READ TREE
# ============================================================

cat("\nREADING TREE\n")


if (!file.exists(TREE_FILE)) {

  stop(
    "\nTREE FILE NOT FOUND:\n",
    TREE_FILE,
    "\n"
  )
}


tr <- read.tree(
  TREE_FILE
)


# ============================================================
# TREE INFORMATION
# ============================================================

NTIP <- Ntip(tr)

NNODE <- tr$Nnode

NTOTAL <- NTIP + NNODE


cat(
  "Tips:        ",
  NTIP,
  "\n",
  sep = ""
)

cat(
  "Internal:    ",
  NNODE,
  "\n",
  sep = ""
)

cat(
  "Total nodes: ",
  NTOTAL,
  "\n",
  sep = ""
)

cat(
  "Rooted:      ",
  is.rooted(tr),
  "\n",
  sep = ""
)

cat(
  "Binary:      ",
  is.binary(tr),
  "\n",
  sep = ""
)

cat(
  "Ultrametric: ",
  is.ultrametric(tr),
  "\n",
  sep = ""
)


if (NTIP != 36) {

  warning(
    "Expected 36 tips, but found ",
    NTIP,
    "."
  )
}


# ============================================================
# READ CAFE5 RESULTS
# ============================================================

cat("\nREADING CAFE5 RESULTS\n")


if (!file.exists(CAFE_FILE)) {

  stop(
    "\nCAFE5 FILE NOT FOUND:\n",
    CAFE_FILE,
    "\n"
  )
}


cafe <- read.delim(
  CAFE_FILE,
  header = TRUE,
  sep = "\t",
  stringsAsFactors = FALSE,
  check.names = FALSE,
  comment.char = ""
)


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

colnames(cafe) <- trimws(
  colnames(cafe)
)


colnames(cafe)[1] <- "Taxon_ID"


cat("Columns:\n")

print(
  colnames(cafe)
)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns <- c(
  "Taxon_ID",
  "Increase",
  "Decrease"
)


if (
  !all(
    required_columns %in%
      colnames(cafe)
  )
) {

  stop(
    "\nRequired columns missing.\n",
    "Required columns: ",
    paste(
      required_columns,
      collapse = ", "
    ),
    "\n"
  )
}


# ============================================================
# EXTRACT CAFE NODE IDS
# ============================================================

cafe$CAFE_ID <- suppressWarnings(
  as.integer(
    sub(
      ".*<([0-9]+)>.*",
      "\\1",
      cafe$Taxon_ID
    )
  )
)


# ============================================================
# FALLBACK IF IDS ARE ALREADY NUMERIC
# ============================================================

direct_id <- suppressWarnings(
  as.integer(
    as.character(
      cafe$Taxon_ID
    )
  )
)


missing_id <- is.na(
  cafe$CAFE_ID
) &
  !is.na(
    direct_id
  )


if (
  any(
    missing_id
  )
) {

  cafe$CAFE_ID[
    missing_id
  ] <- direct_id[
    missing_id
  ]
}


# ============================================================
# CONVERT VALUES TO NUMERIC
# ============================================================

cafe$Increase <- suppressWarnings(
  as.numeric(
    cafe$Increase
  )
)


cafe$Decrease <- suppressWarnings(
  as.numeric(
    cafe$Decrease
  )
)


# ============================================================
# VALIDATION
# ============================================================

if (
  any(
    is.na(
      cafe$CAFE_ID
    )
  )
) {

  stop(
    "\nNA CAFE IDs detected.\n"
  )
}


if (
  any(
    is.na(
      cafe$Increase
    )
  )
) {

  stop(
    "\nNA Increase values detected.\n"
  )
}


if (
  any(
    is.na(
      cafe$Decrease
    )
  )
) {

  stop(
    "\nNA Decrease values detected.\n"
  )
}


# ============================================================
# CAFE SUMMARY
# ============================================================

cat(
  "\nCAFE rows:       ",
  nrow(cafe),
  "\n",
  sep = ""
)


cat(
  "Unique IDs:      ",
  length(
    unique(
      cafe$CAFE_ID
    )
  ),
  "\n",
  sep = ""
)


cat(
  "ID range:        ",
  min(
    cafe$CAFE_ID
  ),
  " - ",
  max(
    cafe$CAFE_ID
  ),
  "\n",
  sep = ""
)


# ============================================================
# EXPECT 70 CAFE ROWS
# ============================================================

if (
  nrow(cafe) !=
    NTOTAL - 1
) {

  stop(
    "\nExpected ",
    NTOTAL - 1,
    " CAFE rows, but found ",
    nrow(cafe),
    ".\n"
  )
}


# ============================================================
# DUPLICATE CHECK
# ============================================================

if (
  length(
    unique(
      cafe$CAFE_ID
    )
  ) !=
    nrow(cafe)
) {

  stop(
    "\nDuplicate CAFE IDs detected.\n"
  )
}


# ============================================================
# CREATE CAFE MAP
# ============================================================

cat("\nMAPPING CAFE5 IDS\n")


cafe_map <- vector(
  "list",
  NTOTAL
)


for (
  i in seq_len(
    nrow(cafe)
  )
) {

  id <- cafe$CAFE_ID[
    i
  ]


  if (
    id < 1 ||
    id > NTOTAL
  ) {

    stop(
      "\nCAFE ID outside tree: ",
      id,
      "\n"
    )
  }


  cafe_map[[id]] <- cafe[
    i,
    ,
    drop = FALSE
  ]
}


# ============================================================
# SAFE CAFE RETRIEVAL FUNCTION
# ============================================================

get_cafe <- function(
  node
) {

  cafe_map[[node]]
}


# ============================================================
# COUNT MAPPED
# ============================================================

mapped <- sum(
  vapply(
    cafe_map,
    function(x) {
      !is.null(x)
    },
    logical(1)
  )
)


cat(
  "Mapped positions: ",
  mapped,
  "\n",
  sep = ""
)


if (
  mapped !=
    nrow(cafe)
) {

  stop(
    "\nNot all CAFE rows were mapped.\n"
  )
}


# ============================================================
# SAVE ANNOTATION TABLE
# ============================================================

annotation <- data.frame(
  Tree_Node = cafe$CAFE_ID,
  CAFE_ID = cafe$CAFE_ID,
  Taxon_ID = cafe$Taxon_ID,
  Increase = cafe$Increase,
  Decrease = cafe$Decrease
)


write.table(
  annotation,
  TSV_FILE,
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)


# ============================================================
# CLEAN TIP NAMES
# ============================================================

display_names <- sub(
  "<[0-9]+>$",
  "",
  tr$tip.label
)


# ============================================================
# CALCULATE APE TREE COORDINATES
# ============================================================

cat("\nCALCULATING TREE COORDINATES\n")


tmp_pdf <- tempfile(
  fileext = ".pdf"
)


pdf(
  tmp_pdf,
  width = 10,
  height = 12
)


ape::plot.phylo(
  tr,
  type = "phylogram",
  direction = "rightwards",
  use.edge.length = TRUE,
  show.tip.label = FALSE,
  show.node.label = FALSE,
  no.margin = TRUE
)


coord <- get(
  "last_plot.phylo",
  envir = ape:::.PlotPhyloEnv
)


dev.off()


unlink(
  tmp_pdf
)


xx <- coord$xx

yy <- coord$yy


# ============================================================
# VALIDATE COORDINATES
# ============================================================

if (
  length(xx) != NTOTAL ||
  length(yy) != NTOTAL
) {

  stop(
    "\nInvalid tree coordinates.\n"
  )
}


# ============================================================
# TREE X COORDINATES
#
# SAME BASIC MODEL AS PREVIOUS FIGURE
# ============================================================

xmin <- min(
  xx
)


xmax <- max(
  xx
)


xn <- (
  xx -
    xmin
) / (
  xmax -
    xmin
)


xn <- xn ^ 2.2


tree_x <- 0.04 +
  xn * 0.51


# ============================================================
# TREE Y COORDINATES
# ============================================================

ymin <- min(
  yy
)


ymax <- max(
  yy
)


tree_y <- 0.035 +
  (
    (
      yy -
        ymin
    ) /
      (
        ymax -
          ymin
      )
  ) *
  0.86


# ============================================================
# PIE DRAWING FUNCTION
# ============================================================

draw_pie <- function(
  x,
  y,
  expansion,
  contraction,
  radius = 0.012
) {

  total <- expansion +
    contraction


  if (
    !is.finite(total) ||
    total <= 0
  ) {

    return(
      invisible(NULL)
    )
  }


  proportion <- expansion /
    total


  # ----------------------------------------------------------
  # EXPANSION SECTOR
  # ----------------------------------------------------------

  angle1 <- seq(
    0,
    2 * pi * proportion,
    length.out = 80
  )


  polygon(
    c(
      x,
      x +
        radius *
        cos(angle1)
    ),
    c(
      y,
      y +
        radius *
        sin(angle1)
    ),
    col = EXPANSION,
    border = "white",
    lwd = 0.8
  )


  # ----------------------------------------------------------
  # CONTRACTION SECTOR
  # ----------------------------------------------------------

  angle2 <- seq(
    2 * pi * proportion,
    2 * pi,
    length.out = 80
  )


  polygon(
    c(
      x,
      x +
        radius *
        cos(angle2)
    ),
    c(
      y,
      y +
        radius *
        sin(angle2)
    ),
    col = CONTRACTION,
    border = "white",
    lwd = 0.8
  )


  # ----------------------------------------------------------
  # WHITE OUTLINE
  # ----------------------------------------------------------

  angle3 <- seq(
    0,
    2 * pi,
    length.out = 120
  )


  lines(
    x +
      radius *
      cos(angle3),
    y +
      radius *
      sin(angle3),
    col = "white",
    lwd = 1
  )


  invisible(NULL)
}


# ============================================================
# FORMAT + / - VALUE
# ============================================================

format_change <- function(
  z
) {

  paste0(
    "+",
    format(
      z$Increase,
      big.mark = ",",
      scientific = FALSE,
      trim = TRUE
    ),
    " / -",
    format(
      z$Decrease,
      big.mark = ",",
      scientific = FALSE,
      trim = TRUE
    )
  )
}


# ============================================================
# CREATE FIGURE
# ============================================================

make_figure <- function(
  type = c(
    "png",
    "pdf"
  )
) {

  type <- match.arg(
    type
  )


  # ==========================================================
  # OPEN DEVICE
  # ==========================================================

  if (
    type == "png"
  ) {

    png(
      PNG_FILE,
      width = 7000,
      height = 6500,
      res = 350
    )

  } else {

    pdf(
      PDF_FILE,
      width = 20,
      height = 18.6,
      family = "Times"
    )
  }


  # ==========================================================
  # GRAPHICS SETTINGS
  # ==========================================================

  par(
    family = "serif",
    mar = c(
      2,
      1,
      3,
      1
    ),
    xpd = NA
  )


  # ==========================================================
  # EMPTY CANVAS
  # ==========================================================

  plot(
    NA,
    NA,
    type = "n",
    xlim = c(
      0,
      1
    ),
    ylim = c(
      0,
      1
    ),
    axes = FALSE,
    xlab = "",
    ylab = ""
  )


  # ==========================================================
  # TITLE
  # ==========================================================

  text(
    0.50,
    0.965,
    "Fusarium 36 - Gene Family Expansion and Contraction",
    family = "serif",
    font = 2,
    cex = 1.55
  )


  # ==========================================================
  # SUBTITLE
  # ==========================================================

  text(
    0.50,
    0.935,
    "CAFE5 Base Model  |  36 Fusarium genomes  |  16,504 orthogroups  |  lambda = 0.33968797961937",
    family = "serif",
    cex = 0.82
  )


  # ==========================================================
  # TREE HORIZONTAL BRANCHES
  # ==========================================================

  for (
    i in seq_len(
      nrow(
        tr$edge
      )
    )
  ) {

    parent <- tr$edge[
      i,
      1
    ]


    child <- tr$edge[
      i,
      2
    ]


    segments(
      tree_x[parent],
      tree_y[child],
      tree_x[child],
      tree_y[child],
      col = TREECOL,
      lwd = 1.2
    )
  }


  # ==========================================================
  # TREE VERTICAL BRANCHES
  # ==========================================================

  parents <- unique(
    tr$edge[
      ,
      1
    ]
  )


  for (
    p in parents
  ) {

    children <- tr$edge[
      tr$edge[, 1] == p,
      2
    ]


    if (
      length(children) >= 2
    ) {

      segments(
        tree_x[p],
        min(
          tree_y[
            children
          ]
        ),
        tree_x[p],
        max(
          tree_y[
            children
          ]
        ),
        col = TREECOL,
        lwd = 1.2
      )
    }
  }


  # ==========================================================
  # RIGHT-SIDE TIP COLUMNS
  # ==========================================================

  TIP_PIE_X <- 0.625

  TIP_VALUE_X <- 0.665

  GENOME_NAME_X <- 0.815


  # ==========================================================
  # INTERNAL NODE LIST
  # ==========================================================

  internal_nodes <- (
    NTIP + 1
  ):NTOTAL


  internal_nodes <- internal_nodes[
    vapply(
      internal_nodes,
      function(node) {

        !is.null(
          get_cafe(node)
        )

      },
      logical(1)
    )
  ]


  # ==========================================================
  # INTERNAL PIE RADIUS
  # ==========================================================

  INTERNAL_RADIUS <- 0.010


  # ==========================================================
  # DRAW ALL INTERNAL PIES
  #
  # IMPORTANT:
  # EACH PIE REMAINS AT ITS ORIGINAL TREE NODE.
  # ==========================================================

  for (
    node in internal_nodes
  ) {

    z <- get_cafe(
      node
    )


    draw_pie(
      tree_x[node],
      tree_y[node],
      z$Increase,
      z$Decrease,
      radius = INTERNAL_RADIUS
    )
  }


  # ==========================================================
  # INTERNAL VALUE POSITIONS
  #
  # EACH VALUE IS CALCULATED FROM ITS OWN PIE POSITION.
  # ==========================================================

  internal_y <- tree_y[
    internal_nodes
  ]


  internal_x <- tree_x[
    internal_nodes
  ]


  # ----------------------------------------------------------
  # START VALUE TO THE RIGHT OF EACH PIE
  # ----------------------------------------------------------

  label_x <- internal_x +
    INTERNAL_RADIUS +
    0.018


  label_y <- internal_y


  # ==========================================================
  # FORCE INTERNAL VALUES INTO WHITE SPACE
  #
  # The large tip-pie column begins around 0.625.
  #
  # We therefore keep internal labels before that area.
  # ==========================================================

  label_x <- pmin(
    label_x,
    0.595
  )


  # ==========================================================
  # SORT LABELS BY VERTICAL POSITION
  # ==========================================================

  ord <- order(
    label_y
  )


  # ==========================================================
  # MINIMUM LABEL SEPARATION
  # ==========================================================

  MIN_GAP <- 0.020


  # ==========================================================
  # FIRST PASS - SEPARATE OVERLAPPING LABELS
  # ==========================================================

  if (
    length(ord) > 1
  ) {

    for (
      k in 2:length(ord)
    ) {

      previous_index <- ord[
        k - 1
      ]


      current_index <- ord[
        k
      ]


      if (
        label_y[current_index] -
        label_y[previous_index]
        <
        MIN_GAP
      ) {

        label_y[current_index] <-
          label_y[previous_index] +
          MIN_GAP
      }
    }
  }


  # ============================================================
  # SECOND PASS
  # ============================================================

  if (
    length(ord) > 1
  ) {

    for (
      k in (
        length(ord) - 1
      ):1
    ) {

      current_index <- ord[
        k
      ]


      next_index <- ord[
        k + 1
      ]


      if (
        label_y[next_index] -
        label_y[current_index]
        <
        MIN_GAP
      ) {

        label_y[current_index] <-
          label_y[next_index] -
          MIN_GAP
      }
    }
  }


  # ==========================================================
  # KEEP LABELS INSIDE FIGURE
  # ==========================================================

  label_y <- pmax(
    label_y,
    0.045
  )


  label_y <- pmin(
    label_y,
    0.895
  )


  # ==========================================================
  # DRAW LEADER LINES
  #
  # FROM PIE EDGE TO VALUE
  # ==========================================================

  for (
    i in seq_along(
      internal_nodes
    )
  ) {

    x_start <- internal_x[i] +
      INTERNAL_RADIUS


    x_end <- label_x[i] -
      0.004


    y_start <- internal_y[i]

    y_end <- label_y[i]


    if (
      x_end > x_start
    ) {

      segments(
        x_start,
        y_start,
        x_end,
        y_end,
        col = LEADERCOL,
        lwd = 0.55
      )
    }
  }


  # ==========================================================
  # DRAW INTERNAL VALUES
  #
  # RIGHT OF THEIR OWN PIE
  # ==========================================================

  for (
    i in seq_along(
      internal_nodes
    )
  ) {

    node <- internal_nodes[
      i
    ]


    z <- get_cafe(
      node
    )


    text(
      label_x[i],
      label_y[i],
      format_change(z),
      adj = c(
        0,
        0.5
      ),
      family = "serif",
      font = 1,
      cex = 0.57,
      col = TEXTCOL
    )
  }


  # ==========================================================
  # DRAW TIP PIES
  #
  # THESE ARE THE LARGE PIES ON RIGHT.
  # ==========================================================

  for (
    tip in seq_len(
      NTIP
    )
  ) {

    z <- get_cafe(
      tip
    )


    if (
      is.null(z)
    ) {

      next
    }


    draw_pie(
      TIP_PIE_X,
      tree_y[tip],
      z$Increase,
      z$Decrease,
      radius = 0.012
    )
  }


  # ==========================================================
  # TIP VALUES
  # ==========================================================

  for (
    tip in seq_len(
      NTIP
    )
  ) {

    z <- get_cafe(
      tip
    )


    if (
      is.null(z)
    ) {

      next
    }


    text(
      TIP_VALUE_X,
      tree_y[tip],
      format_change(z),
      adj = c(
        0,
        0.5
      ),
      family = "serif",
      cex = 0.78,
      col = TEXTCOL
    )
  }


  # ==========================================================
  # GENOME NAMES
  # ==========================================================

  for (
    tip in seq_len(
      NTIP
    )
  ) {

    text(
      GENOME_NAME_X,
      tree_y[tip],
      display_names[tip],
      adj = c(
        0,
        0.5
      ),
      family = "serif",
      font = 3,
      cex = 0.78,
      col = TEXTCOL
    )
  }


  # ==========================================================
  # HEADERS
  # ==========================================================

  text(
    0.555,
    0.925,
    "Increase / Decrease",
    family = "serif",
    font = 2,
    cex = 0.72,
    adj = c(
      0.5,
      0.5
    )
  )


  text(
    TIP_PIE_X,
    0.925,
    "Gene-family change",
    family = "serif",
    font = 2,
    cex = 0.78,
    adj = c(
      0.5,
      0.5
    )
  )


  text(
    GENOME_NAME_X,
    0.925,
    "Fusarium genome",
    family = "serif",
    font = 2,
    cex = 0.82,
    adj = c(
      0,
      0.5
    )
  )


  # ==========================================================
  # LEGEND
  # ==========================================================

  legend(
    x = 0.90,
    y = 0.925,
    legend = c(
      "Expansion",
      "Contraction"
    ),
    pch = 15,
    pt.cex = 1.35,
    col = c(
      EXPANSION,
      CONTRACTION
    ),
    bty = "n",
    cex = 0.75,
    y.intersp = 1.15,
    x.intersp = 0.55
  )


  # ==========================================================
  # FOOTNOTE
  # ==========================================================

  text(
    0.03,
    0.025,
    "Pie size is constant; sector size represents the relative number of expanded and contracted gene families.",
    family = "serif",
    cex = 0.67,
    col = "#555555",
    adj = c(
      0,
      0.5
    )
  )


  # ==========================================================
  # CLOSE
  # ==========================================================

  dev.off()
}


# ============================================================
# CREATE PNG
# ============================================================

cat("\n")
cat("============================================================\n")
cat("CREATING PNG\n")
cat("============================================================\n")


make_figure(
  "png"
)


cat(
  "\nPNG COMPLETE:\n",
  PNG_FILE,
  "\n",
  sep = ""
)


# ============================================================
# CREATE PDF
# ============================================================

cat("\n")
cat("============================================================\n")
cat("CREATING PDF\n")
cat("============================================================\n")


make_figure(
  "pdf"
)


cat(
  "\nPDF COMPLETE:\n",
  PDF_FILE,
  "\n",
  sep = ""
)


# ============================================================
# FINAL SUMMARY
# ============================================================

cat("\n")
cat("============================================================\n")
cat("FINAL SUMMARY\n")
cat("============================================================\n")


cat(
  "Tips: ",
  NTIP,
  "\n",
  sep = ""
)


cat(
  "Internal nodes: ",
  NNODE,
  "\n",
  sep = ""
)


cat(
  "Total nodes: ",
  NTOTAL,
  "\n",
  sep = ""
)


cat(
  "CAFE rows: ",
  nrow(cafe),
  "\n",
  sep = ""
)


cat(
  "Mapped CAFE positions: ",
  mapped,
  "\n",
  sep = ""
)


cat("\n")
cat("INTERNAL PIES       : ALL DRAWN AT TREE NODES\n")
cat("INTERNAL VALUES     : BESIDE INDIVIDUAL PIES\n")
cat("LEADER LINES        : ENABLED\n")
cat("TIP PIES            : PRESERVED\n")
cat("TIP VALUES          : PRESERVED\n")
cat("GENOME NAMES        : PRESERVED\n")
cat("TREE BRANCHES       : PRESERVED\n")
cat("TREE MODEL          : PRESERVED\n")


cat("\n")
cat("PNG:\n")
cat(
  PNG_FILE,
  "\n"
)


cat("\nPDF:\n")
cat(
  PDF_FILE,
  "\n"
)


cat("\nANNOTATION:\n")
cat(
  TSV_FILE,
  "\n"
)


cat("\n")
cat("SCRIPT FINISHED SUCCESSFULLY\n")
cat("============================================================\n")
