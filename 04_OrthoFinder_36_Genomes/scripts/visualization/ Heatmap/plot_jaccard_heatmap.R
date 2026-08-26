# ============================================================
# FUSARIUM 36 — PUBLICATION-STYLE JACCARD HEATMAP
# ============================================================
#
# Input:
# D:/ORTHOFINDER/FUSARIUM36_FINAL/Results_Aug12_5
#
# Output:
# D:/ORTHOFINDER/FUSARIUM36_ORTHOFINDER_PLOTS
#
# Figure:
# Jaccard similarity among 36 Fusarium genomes
#
# ============================================================

# ------------------------------------------------------------
# PACKAGES
# ------------------------------------------------------------

library(ggplot2)

# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

OF_RESULTS <- "D:/ORTHOFINDER/FUSARIUM36_FINAL/Results_Aug12_5"

OUT <- "D:/ORTHOFINDER/FUSARIUM36_ORTHOFINDER_PLOTS"

dir.create(
  OUT,
  recursive = TRUE,
  showWarnings = FALSE
)

OG_FILE <- file.path(
  OF_RESULTS,
  "Orthogroups",
  "Orthogroups.tsv"
)

# ------------------------------------------------------------
# CHECK INPUT
# ------------------------------------------------------------

cat("============================================================\n")
cat("FUSARIUM 36 JACCARD HEATMAP\n")
cat("============================================================\n\n")

cat("Input:\n")
cat(OG_FILE, "\n\n")

if (!file.exists(OG_FILE)) {
  stop("ERROR: Orthogroups.tsv not found.")
}

cat("Output:\n")
cat(OUT, "\n\n")

# ------------------------------------------------------------
# READ ORTHOGROUP TABLE
# ------------------------------------------------------------

og <- read.delim(
  OG_FILE,
  header = TRUE,
  sep = "\t",
  check.names = FALSE,
  quote = "",
  comment.char = "",
  stringsAsFactors = FALSE
)

cat("Orthogroups:", nrow(og), "\n")
cat("Columns:", ncol(og), "\n")

# ------------------------------------------------------------
# SPECIES
# ------------------------------------------------------------

species <- colnames(og)[-1]

if (length(species) != 36) {
  stop(
    paste(
      "ERROR: Expected 36 genomes, found",
      length(species)
    )
  )
}

cat("Genomes:", length(species), "\n")

# ------------------------------------------------------------
# SAFE PRESENCE CALCULATION
# ------------------------------------------------------------

count_one <- function(x) {

  x <- as.character(x)

  ifelse(
    is.na(x),
    0L,
    ifelse(
      trimws(x) == "",
      0L,
      lengths(
        strsplit(
          x,
          ",",
          fixed = TRUE
        )
      )
    )
  )
}

counts <- as.data.frame(
  lapply(
    og[species],
    count_one
  ),
  check.names = FALSE
)

colnames(counts) <- species

# ------------------------------------------------------------
# PRESENCE / ABSENCE
# ------------------------------------------------------------

presence <- counts > 0

# ------------------------------------------------------------
# SPECIES GROUPS
# ------------------------------------------------------------
#
# F. graminearum:
#   Fgram_*
#   Fusgr_*
#   TNW1_proteins
#
# F. avenaceum:
#   Fusav_*
#   DMW8
#
# ------------------------------------------------------------

group <- ifelse(
  grepl(
    "^Fgram_|^Fusgr_|^TNW1",
    species
  ),
  "F. graminearum",
  ifelse(
    grepl(
      "^Fusav_|^DMW8$",
      species
    ),
    "F. avenaceum",
    "Other"
  )
)

# Make sure there are no "Other"
if (any(group == "Other")) {

  cat("\nWARNING — unclassified genomes:\n")

  print(
    species[group == "Other"]
  )
}

# ------------------------------------------------------------
# ORDER SPECIES
# ------------------------------------------------------------
#
# F. graminearum first
# F. avenaceum second
#
# Within each group, order by overall orthogroup
# presence.
# ------------------------------------------------------------

gram <- species[
  group == "F. graminearum"
]

aven <- species[
  group == "F. avenaceum"
]

gram_score <- colSums(
  presence[, gram, drop = FALSE]
)

aven_score <- colSums(
  presence[, aven, drop = FALSE]
)

gram <- gram[
  order(
    gram_score,
    decreasing = TRUE
  )
]

aven <- aven[
  order(
    aven_score,
    decreasing = TRUE
  )
]

species_order <- c(
  gram,
  aven
)

cat("\nSpecies order:\n")

for (i in seq_along(species_order)) {

  cat(
    sprintf(
      "%02d  %s\n",
      i,
      species_order[i]
    )
  )
}

# ------------------------------------------------------------
# JACCARD MATRIX
# ------------------------------------------------------------

n <- length(species_order)

jaccard <- matrix(
  0,
  nrow = n,
  ncol = n
)

rownames(jaccard) <- species_order
colnames(jaccard) <- species_order

for (i in seq_len(n)) {

  for (j in seq_len(n)) {

    a <- presence[
      ,
      species_order[i]
    ]

    b <- presence[
      ,
      species_order[j]
    ]

    shared <- sum(
      a & b
    )

    union_n <- sum(
      a | b
    )

    if (union_n > 0) {

      jaccard[i, j] <-
        shared / union_n

    } else {

      jaccard[i, j] <- 0

    }
  }
}

# ------------------------------------------------------------
# REORDER MATRIX
# ------------------------------------------------------------

jaccard <- jaccard[
  species_order,
  species_order
]

# ------------------------------------------------------------
# CONVERT TO DATA FRAME
# ------------------------------------------------------------

heat <- expand.grid(
  Species1 = species_order,
  Species2 = species_order,
  stringsAsFactors = FALSE
)

heat$Jaccard <- as.vector(
  jaccard
)

heat$Species1 <- factor(
  heat$Species1,
  levels = rev(species_order)
)

heat$Species2 <- factor(
  heat$Species2,
  levels = species_order
)

# ------------------------------------------------------------
# GROUP ANNOTATION
# ------------------------------------------------------------

group_df <- data.frame(
  Species = species_order,
  Group = ifelse(
    species_order %in% gram,
    "F. graminearum",
    "F. avenaceum"
  ),
  stringsAsFactors = FALSE
)

# ------------------------------------------------------------
# MAIN COLOUR PALETTE
# ------------------------------------------------------------
#
# Low similarity:
# deep blue
#
# Intermediate:
# white
#
# High similarity:
# orange / red
#
# This makes the contrast much stronger than the
# previous single-blue heatmap.
# ------------------------------------------------------------

heat_colors <- c(
  "#163A5F",
  "#2F6FA3",
  "#FFFFFF",
  "#F6B26B",
  "#E85D04",
  "#9E2A2B"
)

# ------------------------------------------------------------
# GROUP COLOURS
# ------------------------------------------------------------

group_colors <- c(
  "F. graminearum" = "#E66101",
  "F. avenaceum"   = "#1B9E77"
)

# ------------------------------------------------------------
# GROUP BOUNDARY
# ------------------------------------------------------------

n_gram <- length(gram)

# ------------------------------------------------------------
# CREATE HEATMAP
# ------------------------------------------------------------

p <- ggplot(
  heat,
  aes(
    x = Species2,
    y = Species1,
    fill = Jaccard
  )
) +

  geom_tile(
    color = "white",
    linewidth = 0.18
  ) +

  scale_fill_gradientn(
    colours = heat_colors,
    values = c(
      0,
      0.25,
      0.50,
      0.70,
      0.85,
      1
    ),
    limits = c(0, 1),
    breaks = c(
      0,
      0.2,
      0.4,
      0.6,
      0.8,
      1
    ),
    name = "Jaccard\nsimilarity"
  ) +

  # ----------------------------------------------------------
  # SPECIES LABELS
  # ----------------------------------------------------------

  scale_x_discrete(
    position = "bottom"
  ) +

  scale_y_discrete(
    position = "right"
  ) +

  labs(
    title =
      "Jaccard Similarity Among 36 Fusarium Genomes",
    subtitle =
      "Orthogroup presence–absence similarity",
    x = NULL,
    y = NULL
  ) +

  theme_minimal(
    base_size = 11
  ) +

  theme(

    # Remove unnecessary grid
    panel.grid = element_blank(),

    # X labels
    axis.text.x =
      element_text(
        angle = 90,
        hjust = 1,
        vjust = 0.5,
        size = 7.5,
        colour = "black"
      ),

    # Y labels
    axis.text.y =
      element_text(
        size = 8,
        colour = "black"
      ),

    axis.ticks =
      element_blank(),

    # Title
    plot.title =
      element_text(
        size = 17,
        face = "bold",
        hjust = 0.5
      ),

    plot.subtitle =
      element_text(
        size = 10.5,
        hjust = 0.5
      ),

    # Legend
    legend.title =
      element_text(
        size = 10,
        face = "bold"
      ),

    legend.text =
      element_text(
        size = 9
      ),

    legend.position =
      "left",

    # Margins
    plot.margin =
      margin(
        15,
        25,
        15,
        15
      )
  )

# ------------------------------------------------------------
# ADD SPECIES GROUP BOUNDARIES
# ------------------------------------------------------------
#
# A strong line separates F. graminearum and
# F. avenaceum blocks.
# ------------------------------------------------------------

p <- p +

  geom_vline(
    xintercept = n_gram + 0.5,
    linewidth = 1.1,
    colour = "black"
  ) +

  geom_hline(
    yintercept =
      n - n_gram + 0.5,
    linewidth = 1.1,
    colour = "black"
  )

# ------------------------------------------------------------
# SAVE PNG
# ------------------------------------------------------------

PNG_FILE <- file.path(
  OUT,
  "Fusarium36_Jaccard_Heatmap_Publication.png"
)

ggsave(
  PNG_FILE,
  p,
  width = 13,
  height = 12,
  units = "in",
  dpi = 600,
  bg = "white"
)

# ------------------------------------------------------------
# SAVE PDF
# ------------------------------------------------------------

PDF_FILE <- file.path(
  OUT,
  "Fusarium36_Jaccard_Heatmap_Publication.pdf"
)

ggsave(
  PDF_FILE,
  p,
  width = 13,
  height = 12,
  units = "in",
  device = cairo_pdf,
  bg = "white"
)

# ------------------------------------------------------------
# SAVE JACCARD MATRIX
# ------------------------------------------------------------

MATRIX_FILE <- file.path(
  OUT,
  "Fusarium36_Jaccard_Matrix.tsv"
)

write.table(
  jaccard,
  file = MATRIX_FILE,
  sep = "\t",
  quote = FALSE,
  col.names = NA
)

# ------------------------------------------------------------
# SAVE SPECIES GROUP TABLE
# ------------------------------------------------------------

GROUP_FILE <- file.path(
  OUT,
  "Fusarium36_Species_Groups.tsv"
)

write.table(
  group_df,
  file = GROUP_FILE,
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)

# ------------------------------------------------------------
# FINAL INFORMATION
# ------------------------------------------------------------

cat("\n============================================================\n")
cat("JACCARD HEATMAP COMPLETE\n")
cat("============================================================\n\n")

cat(
  "Genomes:",
  n,
  "\n"
)

cat(
  "F. graminearum:",
  length(gram),
  "\n"
)

cat(
  "F. avenaceum:",
  length(aven),
  "\n"
)

cat(
  "Minimum Jaccard:",
  round(
    min(jaccard),
    4
  ),
  "\n"
)

cat(
  "Maximum Jaccard:",
  round(
    max(jaccard),
    4
  ),
  "\n"
)

cat(
  "Mean Jaccard:",
  round(
    mean(jaccard),
    4
  ),
  "\n\n"
)

cat(
  "PNG:\n",
  PNG_FILE,
  "\n\n"
)

cat(
  "PDF:\n",
  PDF_FILE,
  "\n\n"
)

cat(
  "Matrix:\n",
  MATRIX_FILE,
  "\n\n"
)

cat(
  "Species groups:\n",
  GROUP_FILE,
  "\n\n"
)

cat("============================================================\n")
cat("NO ORTHOFINDER FILE WAS MODIFIED.\n")
cat("============================================================\n")
