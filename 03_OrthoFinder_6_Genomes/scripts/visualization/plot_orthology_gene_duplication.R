############################################################
## Orthology & Gene Duplication Analysis
## Fusarium – 6 Genomes
##
## Generates:
## 01_shared_orthogroups_heatmap.png
## 02_genes_in_orthogroups.png
## 03_orthogroups_per_species.png
## 04_multiplicity_Fgram.png
## 05_multiplicity_Fpoae.png
## 06_duplications_per_species.png
## 07_duplications_per_node.png
## 08_species_tree_with_OG_counts.png
############################################################


############################################################
## 1. Load libraries
############################################################

library(readr)
library(dplyr)
library(tidyr)
library(ggplot2)
library(stringr)
library(ape)
library(ggtree)
library(openxlsx)


############################################################
## 2. Define directories
############################################################

results_dir <- "E:/fusarium_run/of_run_001/Results_Dec10"

plot_dir <- "E:/fusarium_run/plots"

dir.create(
  plot_dir,
  showWarnings = FALSE,
  recursive = TRUE
)

geneCount_file <- file.path(
  results_dir,
  "Orthogroups",
  "Orthogroups.GeneCount.tsv"
)

dup_file <- file.path(
  results_dir,
  "Gene_Duplication_Events",
  "Duplications.tsv"
)

tree_file <- file.path(
  results_dir,
  "Species_Tree",
  "SpeciesTree_rooted.txt"
)


############################################################
## 3. REAL species names found in OG table
############################################################

my_species <- c(
  "DMW8",
  "F_avenaceum",
  "F_culmorum",
  "F_graminearum",
  "F_poae",
  "TNW1"
)


############################################################
## Species colours
############################################################

species_colors <- c(
  "DMW8"          = "#a65628",
  "F_avenaceum"   = "#984ea3",
  "F_culmorum"    = "#377eb8",
  "F_graminearum" = "#e41a1c",
  "F_poae"        = "#4daf4a",
  "TNW1"          = "#ff7f00"
)


############################################################
## 4. Load OrthoFinder tables
############################################################

ogs <- read_tsv(
  geneCount_file,
  show_col_types = FALSE
)

dup <- read_tsv(
  dup_file,
  show_col_types = FALSE
) %>%
  rename_with(make.names)

tree <- read.tree(tree_file)


############################################################
## 5. Prepare OG table
############################################################

species_cols <- intersect(
  colnames(ogs),
  my_species
)

ogs_clean <- ogs[
  ,
  c("Orthogroup", species_cols)
]


############################################################
## 6. Shared orthogroups heatmap
############################################################

bin <- as.matrix(
  ogs_clean[, species_cols] > 0
)

n <- length(species_cols)

shared_mat <- matrix(
  0,
  n,
  n,
  dimnames = list(
    species_cols,
    species_cols
  )
)

for (i in 1:n) {

  for (j in 1:n) {

    shared_mat[i, j] <-
      sum(
        bin[, i] &
        bin[, j]
      )
  }
}


df_heat <- as.data.frame(
  as.table(shared_mat)
)

colnames(df_heat) <- c(
  "Species1",
  "Species2",
  "SharedCount"
)


p_heat <- ggplot(
  df_heat,
  aes(
    Species1,
    Species2,
    fill = SharedCount
  )
) +

  geom_tile(
    color = "white"
  ) +

  geom_text(
    aes(
      label = SharedCount
    ),
    angle = 90,
    size = 5,
    fontface = "bold"
  ) +

  scale_fill_gradientn(
    colours = c(
      "#084594",
      "#2171b5",
      "#6baed6",
      "#bdd7e7",
      "#ffffcc"
    )
  ) +

  theme_minimal(
    base_size = 14
  ) +

  theme(
    axis.text.x =
      element_text(
        angle = 45,
        hjust = 1
      )
  ) +

  labs(
    title = "Shared Orthogroups"
  )


ggsave(
  file.path(
    plot_dir,
    "01_shared_orthogroups_heatmap.png"
  ),
  p_heat,
  width = 8,
  height = 7,
  dpi = 300
)


############################################################
## 7. Genes in orthogroups per species
############################################################

genes_in_ogs <-
  colSums(
    ogs_clean[, species_cols]
  )


df_genes <- tibble(
  Species = names(genes_in_ogs),
  Genes_in_OGs =
    as.numeric(genes_in_ogs)
)


p_genes <- ggplot(
  df_genes,
  aes(
    x = reorder(
      Species,
      Genes_in_OGs
    ),
    y = Genes_in_OGs,
    fill = Species
  )
) +

  geom_col() +

  scale_fill_manual(
    values = species_colors
  ) +

  coord_flip() +

  theme_minimal() +

  labs(
    title = "Genes in Orthogroups",
    y = "Genes",
    x = "Species"
  )


ggsave(
  file.path(
    plot_dir,
    "02_genes_in_orthogroups.png"
  ),
  p_genes,
  width = 7,
  height = 5,
  dpi = 300
)


############################################################
## 8. Orthogroups per species
############################################################

ogs_per_species <-
  colSums(
    ogs_clean[, species_cols] > 0
  )


df_ogs <- tibble(
  Species = names(ogs_per_species),
  OGs =
    as.numeric(ogs_per_species)
)


p_ogs <- ggplot(
  df_ogs,
  aes(
    x = reorder(
      Species,
      OGs
    ),
    y = OGs,
    fill = Species
  )
) +

  geom_col() +

  scale_fill_manual(
    values = species_colors
  ) +

  coord_flip() +

  theme_minimal() +

  labs(
    title = "Orthogroups per Species",
    y = "Orthogroups",
    x = "Species"
  )


ggsave(
  file.path(
    plot_dir,
    "03_orthogroups_per_species.png"
  ),
  p_ogs,
  width = 7,
  height = 5,
  dpi = 300
)


############################################################
## 9. Ortholog multiplicity
##    1:1, 1:many, many:1, many:many
############################################################

multiplicity_counts <- function(
  focal,
  other
) {

  a <- ogs_clean[[focal]]

  b <- ogs_clean[[other]]

  keep <- a > 0 & b > 0

  tibble(

    Focal = focal,

    Other = other,

    Category = c(
      "one-to-one",
      "one-to-many",
      "many-to-one",
      "many-to-many"
    ),

    Count = c(

      sum(
        a[keep] == 1 &
        b[keep] == 1
      ),

      sum(
        a[keep] == 1 &
        b[keep] > 1
      ),

      sum(
        a[keep] > 1 &
        b[keep] == 1
      ),

      sum(
        a[keep] > 1 &
        b[keep] > 1
      )

    )
  )
}


############################################################
## Focal = F. graminearum
############################################################

focal1 <- "F_graminearum"


mult1 <- bind_rows(
  lapply(
    setdiff(
      my_species,
      focal1
    ),
    function(sp)
      multiplicity_counts(
        focal1,
        sp
      )
  )
)


p_mult1 <- ggplot(
  mult1,
  aes(
    Other,
    Count,
    fill = Category
  )
) +

  geom_col() +

  coord_flip() +

  scale_fill_brewer(
    palette = "Set2"
  ) +

  theme_minimal() +

  labs(
    title =
      "Ortholog Multiplicity: F. graminearum"
  )


ggsave(
  file.path(
    plot_dir,
    "04_multiplicity_Fgram.png"
  ),
  p_mult1,
  width = 7,
  height = 5,
  dpi = 300
)


############################################################
## Focal = F. poae
############################################################

focal2 <- "F_poae"


mult2 <- bind_rows(
  lapply(
    setdiff(
      my_species,
      focal2
    ),
    function(sp)
      multiplicity_counts(
        focal2,
        sp
      )
  )
)


p_mult2 <- ggplot(
  mult2,
  aes(
    Other,
    Count,
    fill = Category
  )
) +

  geom_col() +

  coord_flip() +

  scale_fill_brewer(
    palette = "Set2"
  ) +

  theme_minimal() +

  labs(
    title =
      "Ortholog Multiplicity: F. poae"
  )


ggsave(
  file.path(
    plot_dir,
    "05_multiplicity_Fpoae.png"
  ),
  p_mult2,
  width = 7,
  height = 5,
  dpi = 300
)


############################################################
## 10. Gene duplication per species
############################################################

dup_long <- dup %>%

  mutate(

    Species1 =
      str_extract(
        Genes.1,
        "^[^|,]+"
      ),

    Species2 =
      str_extract(
        Genes.2,
        "^[^|,]+"
      )

  ) %>%

  pivot_longer(
    c(
      Species1,
      Species2
    ),
    names_to = "src",
    values_to = "Species"
  ) %>%

  filter(
    !is.na(Species)
  )


############################################################
## Map duplication species → OG species
############################################################

dup_map <- c(

  "F_poae_Fpoae" =
    "F_poae",

  "DMW8_DMW8" =
    "DMW8",

  "F_graminearum_Fgram" =
    "F_graminearum",

  "TNW1_TNW1" =
    "TNW1",

  "F_avenaceum_Faven" =
    "F_avenaceum",

  "F_culmorum_Fculm" =
    "F_culmorum"
)


dup_long$Species_fixed <-
  dup_map[
    dup_long$Species
  ]


dup_long <-
  dup_long %>%
  filter(
    !is.na(Species_fixed)
  )


dup_species <-
  dup_long %>%
  count(
    Species_fixed,
    name = "Duplications"
  )


p_dup_species <- ggplot(
  dup_species,
  aes(
    x = reorder(
      Species_fixed,
      Duplications
    ),
    y = Duplications,
    fill = Species_fixed
  )
) +

  geom_col() +

  scale_fill_manual(
    values = species_colors
  ) +

  coord_flip() +

  theme_minimal() +

  labs(
    title =
      "Gene Duplications per Species",
    x = "Species",
    y = "Duplications"
  )


ggsave(
  file.path(
    plot_dir,
    "06_duplications_per_species.png"
  ),
  p_dup_species,
  width = 8,
  height = 5,
  dpi = 300
)


############################################################
## 11. Duplications per internal node
############################################################

dup_node <-
  dup %>%

  group_by(
    Species.Tree.Node
  ) %>%

  summarise(
    Duplications = n(),
    .groups = "drop"
  )


p_dup_node <- ggplot(
  dup_node,
  aes(
    x = reorder(
      Species.Tree.Node,
      Duplications
    ),
    y = Duplications
  )
) +

  geom_col(
    fill = "#8B0000"
  ) +

  coord_flip() +

  theme_minimal() +

  labs(
    title =
      "Duplications per Internal Node"
  )


ggsave(
  file.path(
    plot_dir,
    "07_duplications_per_node.png"
  ),
  p_dup_node,
  width = 8,
  height = 5,
  dpi = 300
)


############################################################
## 12. Species Tree with OG Counts
############################################################

tip_counts <- tibble(

  Species =
    names(ogs_per_species),

  OGs =
    ogs_per_species
)


p_tree <-
  ggtree(tree) %<+%
  tip_counts +

  geom_tiplab(
    aes(
      label =
        paste0(
          label,
          " (",
          OGs,
          ")"
        )
    ),
    size = 4
  ) +

  theme_tree2()


ggsave(
  file.path(
    plot_dir,
    "08_species_tree_with_OG_counts.png"
  ),
  p_tree,
  width = 8,
  height = 6,
  dpi = 300
)


############################################################
## DONE
############################################################

cat(
  "\n✔ ALL 8 PLOTS SAVED TO: ",
  plot_dir,
  "\n"
)
