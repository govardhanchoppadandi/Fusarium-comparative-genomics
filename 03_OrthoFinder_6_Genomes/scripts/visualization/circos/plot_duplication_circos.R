############################################################
## Circos Duplication Visualization
## Fusarium – 6 Genomes
##
## Generates:
##
## G_highconfidence_duplications.png
## H_all_duplications.png
## H_all_duplications.pdf
##
## Based on OrthoFinder Duplications.tsv
############################################################


############################################################
# 1. Libraries
############################################################

library(readr)
library(dplyr)
library(stringr)
library(tibble)
library(circlize)


############################################################
# 2. Directories
############################################################

results_dir <- "E:/1 Manuscript Fusarium genome/orthofinder"

plot_dir <- file.path(
  results_dir,
  "plots"
)

dir.create(
  plot_dir,
  showWarnings = FALSE
)


############################################################
# 3. Duplication table
############################################################

dup_file <- file.path(
  results_dir,
  "Gene_Duplication_Events",
  "Duplications.tsv"
)


############################################################
# 4. Load duplication table
############################################################

dup <- read_tsv(
  dup_file,
  show_col_types = FALSE
) %>%
  rename_with(make.names)


############################################################
# 5. Species order
############################################################

my_species <- c(
  "F_graminearum",
  "TNW1",
  "F_culmorum",
  "F_poae",
  "F_avenaceum",
  "DMW8"
)


############################################################
# 6. Species labels
############################################################

species_labels <- c(

  "F_graminearum" =
    "F. graminearum",

  "TNW1" =
    "F. graminearum (TNW1)",

  "F_culmorum" =
    "F. culmorum",

  "F_poae" =
    "F. poae",

  "F_avenaceum" =
    "F. avenaceum",

  "DMW8" =
    "F. avenaceum (DMW8)"
)


############################################################
# 7. Map gene → species
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


############################################################
# 8. Extract species from gene identifiers
############################################################

extract_species <- function(g){

  raw <- sub(
    "\\|.*",
    "",
    g
  )

  sp <- dup_map[raw]

  if(any(is.na(sp))){

    warning(
      "Some genes could not be mapped to species"
    )
  }

  sp
}


############################################################
# 9. Expand duplication gene pairs
############################################################

expand_edges <- function(df){

  rows <- lapply(
    seq_len(nrow(df)),
    function(i){

      g1 <- unlist(
        str_split(
          df$Genes.1[i],
          ",\\s*"
        )
      )

      g2 <- unlist(
        str_split(
          df$Genes.2[i],
          ",\\s*"
        )
      )

      expand.grid(
        gene1 = g1,
        gene2 = g2,
        stringsAsFactors = FALSE
      )
    }
  )

  bind_rows(rows)
}


############################################################
# 10. Create all duplication edges
############################################################

edges_all <- expand_edges(
  dup
)


############################################################
# 11. Create high-confidence duplication edges
############################################################

edges_high <- expand_edges(
  filter(
    dup,
    Support >= 0.98
  )
)


############################################################
# 12. Assign gene positions
############################################################

all_genes <- unique(
  c(
    edges_all$gene1,
    edges_all$gene2
  )
)


gene_tbl <- tibble(

  gene = all_genes,

  species =
    extract_species(all_genes)

) %>%

  filter(
    species %in% my_species
  ) %>%

  arrange(
    species,
    gene
  ) %>%

  group_by(
    species
  ) %>%

  mutate(
    pos = row_number()
  ) %>%

  ungroup()


############################################################
# 13. Join gene positions to duplication edges
############################################################

join_pos <- function(
  edges,
  tbl
){

  edges %>%

    left_join(
      tbl,
      by = c(
        "gene1" = "gene"
      )
    ) %>%

    rename(
      species1 = species,
      x1 = pos
    ) %>%

    left_join(
      tbl,
      by = c(
        "gene2" = "gene"
      )
    ) %>%

    rename(
      species2 = species,
      x2 = pos
    ) %>%

    filter(
      !is.na(species1),
      !is.na(species2)
    )
}


############################################################
# 14. Prepare positioned edges
############################################################

edges_all_pos <-
  join_pos(
    edges_all,
    gene_tbl
  )


edges_high_pos <-
  join_pos(
    edges_high,
    gene_tbl
  )


############################################################
# 15. Sector limits
############################################################

limits <-
  gene_tbl %>%

  group_by(
    species
  ) %>%

  summarise(
    xmin = 1,
    xmax = max(pos),
    .groups = "drop"
  ) %>%

  right_join(
    tibble(
      species = my_species
    ),
    by = "species"
  ) %>%

  mutate(

    xmin =
      ifelse(
        is.na(xmin),
        1,
        xmin
      ),

    xmax =
      ifelse(
        is.na(xmax),
        1,
        xmax
      )
  )


limits$species <-
  factor(
    limits$species,
    levels = my_species
  )


############################################################
# 16. Species colours
############################################################

species_cols <- c(

  F_graminearum =
    "#e41a1c",

  TNW1 =
    "#ff7f00",

  F_culmorum =
    "#377eb8",

  F_poae =
    "#4daf4a",

  F_avenaceum =
    "#984ea3",

  DMW8 =
    "#a65628"
)


############################################################
# 17. Global heat scaling
############################################################

global_bins <- seq(

  min(
    gene_tbl$pos
  ),

  max(
    gene_tbl$pos
  ),

  length.out = 150
)


global_hist <- hist(

  edges_all_pos$x1,

  breaks = global_bins,

  plot = FALSE
)


global_max <-
  max(
    global_hist$counts
  )


if(
  global_max == 0
){

  global_max <- 1

}


############################################################
# 18. FINAL CIRCOS PLOT FUNCTION
############################################################

plot_circos <- function(

  edges_pos,

  title_text,

  outfile,

  link_sample = 1500,

  link_alpha = 0.5,

  export_pdf = FALSE

){

  set.seed(123)


  ##########################################################
  # Output device
  ##########################################################

  if(export_pdf){

    pdf(
      outfile,
      width = 10,
      height = 10
    )

  } else {

    png(
      outfile,
      width = 3200,
      height = 3400,
      res = 300
    )

  }


  ##########################################################
  # Plot margins
  ##########################################################

  par(
    mar = c(
      2,
      2,
      4,
      2
    )
  )


  ##########################################################
  # Clear previous Circos plot
  ##########################################################

  circos.clear()


  ##########################################################
  # Circos parameters
  ##########################################################

  circos.par(

    start.degree = 90,

    gap.after =
      rep(
        6,
        length(my_species)
      ),

    cell.padding =
      c(
        0,
        0,
        0,
        0
      ),

    track.margin =
      c(
        0.01,
        0.01
      )
  )


  ##########################################################
  # Initialize sectors
  ##########################################################

  circos.initialize(

    factors =
      limits$species,

    xlim =
      limits[
        ,
        c(
          "xmin",
          "xmax"
        )
      ]
  )


  ##########################################################
  # Track 1 – Species labels
  ##########################################################

  circos.track(

    ylim =
      c(
        0,
        1
      ),

    track.height =
      0.12,

    panel.fun =
      function(x,y){

        circos.rect(

          CELL_META$xlim[1],
          0,

          CELL_META$xlim[2],
          1,

          col =
            "#f5f5f5",

          border =
            "#bdbdbd"
        )


        circos.text(

          mean(
            CELL_META$xlim
          ),

          0.5,

          species_labels[
            CELL_META$sector.index
          ],

          facing =
            "bending.inside",

          niceFacing =
            TRUE,

          cex =
            1.8,

          font =
            2
        )

      }
  )


  ##########################################################
  # Track 2 – Duplication density heatmap
  ##########################################################

  heat_cols <- c(

    "#2c7bb6",

    "#abd9e9",

    "#ffffbf",

    "#fdae61",

    "#d7191c"

  )


  circos.track(

    ylim =
      c(
        0,
        1
      ),

    track.height =
      0.10,

    panel.fun =
      function(x,y){

        sp <-
          CELL_META$sector.index


        sector_edges <-
          edges_pos %>%

          filter(
            species1 == sp |
            species2 == sp
          )


        if(
          nrow(sector_edges) == 0
        ){

          return()

        }


        bins <- seq(

          CELL_META$xlim[1],

          CELL_META$xlim[2],

          length.out = 40

        )


        sector_edges$x1 <-
          pmin(

            pmax(
              sector_edges$x1,
              bins[1]
            ),

            bins[
              length(bins)
            ]

          )


        h <- hist(

          sector_edges$x1,

          breaks = bins,

          plot = FALSE

        )


        vals <-
          h$counts /
          global_max


        col_index <- cut(

          vals,

          breaks =
            c(
              0,
              0.05,
              0.10,
              0.20,
              0.40,
              1
            ),

          labels =
            FALSE,

          include.lowest =
            TRUE

        )


        col_index[
          is.na(col_index)
        ] <- 1


        for(
          i in seq_along(vals)
        ){

          circos.rect(

            bins[i],
            0,

            bins[i + 1],
            1,

            col =
              heat_cols[
                col_index[i]
              ],

            border =
              NA

          )

        }

      }
  )


  ##########################################################
  # Track 3 – Filled duplication histogram
  ##########################################################

  circos.track(

    ylim =
      c(
        0,
        1
      ),

    track.height =
      0.10,

    panel.fun =
      function(x,y){

        sp <-
          CELL_META$sector.index


        sector_edges <-
          edges_pos %>%

          filter(
            species1 == sp |
            species2 == sp
          )


        if(
          nrow(sector_edges) == 0
        ){

          return()

        }


        bins <- seq(

          CELL_META$xlim[1],

          CELL_META$xlim[2],

          length.out = 60

        )


        sector_edges$x1 <-
          pmin(

            pmax(
              sector_edges$x1,
              bins[1]
            ),

            bins[
              length(bins)
            ]

          )


        h <- hist(

          sector_edges$x1,

          breaks = bins,

          plot = FALSE

        )


        m <-
          max(
            h$counts
          )


        vals <-

          if(
            m == 0
          ){

            rep(
              0,
              length(
                h$counts
              )
            )

          } else {

            h$counts / m

          }


        circos.polygon(

          c(
            h$mids,
            rev(h$mids)
          ),

          c(
            vals,
            rep(
              0,
              length(vals)
            )
          ),

          col =
            adjustcolor(
              "#b2182b",
              0.5
            ),

          border =
            NA
        )


        circos.lines(

          h$mids,

          vals,

          col =
            "#67000d",

          lwd =
            2

        )

      }
  )


  ##########################################################
  # Links between duplicated genes
  ##########################################################

  if(
    nrow(edges_pos) >
    link_sample
  ){

    edges_pos <-
      edges_pos[
        sample(
          nrow(edges_pos),
          link_sample
        ),
      ]

  }


  ##########################################################
  # Draw links
  ##########################################################

  for(
    i in seq_len(
      nrow(edges_pos)
    )
  ){

    r <-
      edges_pos[i,]


    circos.link(

      r$species1,
      r$x1,

      r$species2,
      r$x2,

      col =
        adjustcolor(
          species_cols[
            r$species1
          ],
          alpha.f =
            link_alpha
        ),

      border =
        NA,

      lwd =
        1,

      h.ratio =
        0.9

    )

  }


  ##########################################################
  # Title
  ##########################################################

  title(

    title_text,

    cex.main =
      1.8,

    font.main =
      2,

    line =
      1

  )


  ##########################################################
  # Legend
  ##########################################################

  legend(

    "bottom",

    legend =
      c(
        "Low density",
        "Moderate",
        "High",
        "Very high",
        "Extreme"
      ),

    fill =
      heat_cols,

    border =
      NA,

    horiz =
      TRUE,

    bty =
      "n",

    cex =
      1.3,

    title =
      "Duplication density"
  )


  ##########################################################
  # Close output
  ##########################################################

  dev.off()

}


############################################################
# 19. Generate ALL duplication Circos plot
############################################################

plot_circos(

  edges_all_pos,

  "H. All Duplication Events",

  file.path(
    plot_dir,
    "H_all_duplications.png"
  )

)


############################################################
# 20. Generate HIGH-CONFIDENCE duplication Circos plot
############################################################

plot_circos(

  edges_high_pos,

  "G. High-confidence duplications (Support ≥0.98)",

  file.path(
    plot_dir,
    "G_highconfidence_duplications.png"
  ),

  link_sample =
    800,

  link_alpha =
    0.85

)


############################################################
# 21. Generate PDF version
############################################################

plot_circos(

  edges_all_pos,

  "H. All Duplication Events",

  file.path(
    plot_dir,
    "H_all_duplications.pdf"
  ),

  export_pdf =
    TRUE

)


############################################################
# 22. Completion message
############################################################

cat(
  "\n✔ Circos plots saved to: ",
  plot_dir,
  "\n"
)

cat(
  "\n✔ Generated files:\n"
)

cat(
  "  H_all_duplications.png\n"
)

cat(
  "  G_highconfidence_duplications.png\n"
)

cat(
  "  H_all_duplications.pdf\n"
)
