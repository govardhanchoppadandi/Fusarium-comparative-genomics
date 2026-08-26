########################################################
# FUSARIUM PHYLOGENY WITH DISTANCE LABELS
#
# Input:
# concatenated.fasta.contree
#
# Output:
# Fusarium_distance_tree.tiff
########################################################


########################################################
# 1. LOAD LIBRARIES
########################################################

library(ape)
library(ggtree)
library(ggplot2)
library(grid)


########################################################
# 2. SET WORKING DIRECTORY
########################################################

setwd("D:/PHYLOGENY/ALIGN")


########################################################
# 3. LOAD TREE
########################################################

tree <- read.tree(
  "concatenated.fasta.contree"
)


########################################################
# 4. ROOT TREE WITH OUTGROUP
########################################################

tree <- root(
  tree,
  outgroup =
    "Neonectria_ditissima_CBS100316",
  resolve.root = TRUE
)

tree <- ladderize(tree)


########################################################
# 5. FORMAT TIP LABELS
########################################################

format_label <- function(x){

  parts <- strsplit(
    x,
    "_"
  )[[1]]

  genus <- parts[1]
  species <- parts[2]

  strain <- paste(
    parts[3:length(parts)],
    collapse = " "
  )

  strain <- gsub(
    "([A-Z]+)([0-9]+)",
    "\\1 \\2",
    strain
  )

  paste0(
    "italic('",
    genus,
    " ",
    species,
    "')~' (",
    strain,
    ")'"
  )
}


########################################################
# 6. HIGHLIGHT YOUR ISOLATES
########################################################

my_isolates <- c(
  "Fusarium_graminearum_TNW1",
  "Fusarium_avenaceum_DMW8"
)

tip_colours <- ifelse(
  tree$tip.label %in%
    my_isolates,
  "red",
  "black"
)

tip_fonts <- ifelse(
  tree$tip.label %in%
    my_isolates,
  "bold",
  "plain"
)


########################################################
# 7. DRAW TREE
########################################################

p <- ggtree(
  tree,
  size = 1.4
)


########################################################
# 8. GET TIP POSITIONS
########################################################

tips <- p$data[
  p$data$isTip,
]

max_y <- max(tips$y)

out_y <- tips$y[
  tips$label ==
    "Neonectria_ditissima_CBS100316"
]


########################################################
# 9. BACKGROUND SHADING
########################################################

# Ingroup
p <- p +
  annotation_raster(
    colorRampPalette(
      c(
        "white",
        "#f4a259"
      )
    )(100),
    xmin = -0.02,
    xmax = max(p$data$x)*2,
    ymin = out_y + 0.5,
    ymax = max_y + 1
  )

# Outgroup
p <- p +
  annotate(
    "rect",
    xmin = -0.02,
    xmax = max(p$data$x)*2,
    ymin = out_y - 1,
    ymax = out_y + 0.5,
    fill = "#cfe8ff",
    alpha = 0.9
  )


########################################################
# 10. REDRAW TREE
########################################################

p <- p +
  geom_tree(size = 1.4)


########################################################
# 11. BRANCH DISTANCE LABELS
########################################################

p <- p +
  geom_text2(
    aes(
      label =
        round(
          branch.length,
          3
        ),
      subset = !isTip
    ),
    size = 3,
    colour = "darkblue",
    hjust = 1.3,
    vjust = -0.5
  )


########################################################
# 12. TIP LABELS
########################################################

p <- p +
  geom_tiplab(
    aes(
      label =
        sapply(
          label,
          format_label
        )
    ),
    parse = TRUE,
    size = 5,
    offset = 0.02,
    colour = tip_colours,
    fontface = tip_fonts
  )


########################################################
# 13. SCALE BAR
########################################################

p <- p +
  geom_treescale(
    x = 0,
    y = out_y - 1.3,
    width = 0.05
  )


########################################################
# 14. OUTGROUP LABEL
########################################################

p <- p +
  annotate(
    "text",
    x = max(p$data$x)*1.5,
    y = out_y - 0.2,
    label = "Outgroup",
    size = 6,
    fontface = "bold"
  )


########################################################
# 15. FINAL THEME
########################################################

p <- p +
  coord_cartesian(
    clip = "off"
  ) +
  theme_classic() +
  theme(
    plot.margin =
      margin(
        30,
        500,
        30,
        30
      ),
    legend.position =
      "none"
  )


########################################################
# 16. DISPLAY TREE
########################################################
print(p)

########################################################
# 17. SAVE TIFF FIGURE
########################################################

ggsave(
  "D:/PHYLOGENY/ALIGN/Fusarium_distance_tree.tiff",
  plot = p,
  width = 20,
  height = 10,
  dpi = 600,
  compression = "lzw"
)

