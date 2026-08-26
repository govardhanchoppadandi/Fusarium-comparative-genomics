############################################################
# FUSARIUM 6 — SPECIES TREE VISUALIZATION
############################################################

library(ape)
library(ggplot2)
library(ggtree)

############################################################
# 1. DIRECTORIES
############################################################

tree_file <- "E:/fusarium_run/of_run_001/Results_Dec10/Species_Tree/SpeciesTree_rooted.txt"

plot_dir <- "E:/fusarium_run/plots"

dir.create(
  plot_dir,
  showWarnings = FALSE,
  recursive = TRUE
)

############################################################
# 2. LOAD SPECIES TREE
############################################################

tree <- read.tree(tree_file)

############################################################
# 3. SPECIES LABELS
############################################################

species_labels <- c(
  "DMW8" = "F. avenaceum (DMW8)",
  "F_avenaceum" = "F. avenaceum",
  "F_culmorum" = "F. culmorum",
  "F_graminearum" = "F. graminearum",
  "F_poae" = "F. poae",
  "TNW1" = "F. graminearum (TNW1)"
)

############################################################
# 4. APPLY LABELS
############################################################

tree$tip.label <- ifelse(
  tree$tip.label %in% names(species_labels),
  species_labels[tree$tip.label],
  tree$tip.label
)

############################################################
# 5. BASIC TREE PLOT
############################################################

p <- ggtree(
  tree,
  layout = "rectangular"
) +
  geom_tiplab(
    size = 4,
    fontface = "bold",
    offset = 0.01
  ) +
  theme_tree2() +
  ggtitle(
    "Phylogenomic Relationships Among Six Fusarium Genomes"
  ) +
  theme(
    plot.title = element_text(
      hjust = 0.5,
      face = "bold",
      size = 16
    )
  )

############################################################
# 6. SAVE PNG
############################################################

ggsave(
  file.path(
    plot_dir,
    "01_species_tree.png"
  ),
  p,
  width = 10,
  height = 7,
  dpi = 300
)

############################################################
# 7. SAVE PDF
############################################################

ggsave(
  file.path(
    plot_dir,
    "01_species_tree.pdf"
  ),
  p,
  width = 10,
  height = 7
)

############################################################
# 8. SAVE NEWICK COPY
############################################################

write.tree(
  tree,
  file = file.path(
    plot_dir,
    "01_species_tree_plotting_tree.nwk"
  )
)

############################################################
# DONE
############################################################

cat(
  "\n====================================================\n",
  "FUSARIUM 6 SPECIES TREE PLOT COMPLETE\n",
  "====================================================\n",
  "Output directory:\n",
  plot_dir,
  "\n\n"
)
