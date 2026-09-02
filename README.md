# Fusarium Comparative Genomics

This repository contains the reproducible computational workflows, scripts,
metadata, and figure-generation code used for the comparative genomic
analyses of wheat-infecting Fusarium species.

## Overall Workflow

The overall experimental and computational workflow used in this study is shown below.

![Fusarium Comparative Genomics Workflow](workflow.png)

## Repository Structure

```text
Fusarium-comparative-genomics/
│
├── 01_Genome_Quality/
│   └── BUSCO/
│       ├── README.md
│       └── scripts/
│           ├── run_busco_genomes.sh
│           ├── run_busco_proteins.sh
│           └── run_busco_proteins_resume.sh
│
├── 02_Phylogeny/
│   ├── README.md
│   └── scripts/
│       ├── alignment/
│       ├── concatenation/
│       ├── tree_inference/
│       └── visualization/
│
├── 03_OrthoFinder_6_Genomes/
│   ├── README.md
│   └── scripts/
│       ├── prepare_proteomes/
│       │   └── fix_headers.py
│       ├── orthofinder/
│       │   └── run_orthofinder_6.sh
│       ├── single_copy_orthologues/
│       │   └── extract_single_copy.sh
│       ├── phylogenomics/
│       │   ├── concat_by_species.py
│       │   ├── validate_concatenation.py
│       │   └── run_raxml_ng.sh
│       └── visualization/
│           ├── plot_orthology_gene_duplication.R
│           └── circos/
│               └── plot_duplication_circos.R
│
├── 04_OrthoFinder_36_Genomes/
│   ├── README.md
│   └── scripts/
│       ├── prepare_proteomes/
│       ├── orthofinder/
│       │   └── run_orthofinder_36.sh
│       ├── tree_inference/
│       │   ├── run_fusarium36_trees_checkpoint.sh
│       │   ├── run_fusarium36_species_tree_checkpoint.sh
│       │   └── run_fusarium36_species_tree_fast.sh
│       ├── downstream_analysis/
│       │   ├── run_fusarium36_step24.sh
│       │   └── run_fusarium36_step24_corrected.sh
│       └── visualization/
│           ├── Circos/
│           │   └── plot_circos.R
│           └── Heatmap/
│               └── plot_jaccard_heatmap.R
│
├── 05_CAFE5_Gene_Family_Evolution/
│   ├── README.md
│   └── scripts/
│       ├── run_CAFE5_Fusarium36.sh
│       └── plot_CAFE5_Fusarium36_publication.R
│
├── 06_ncRNA/
│   ├── README.md
│   └── scripts/
│
├── 07_Transposable_Elements/
│   ├── README.md
│   ├── scripts/
│   │   └── earl_grey/
│   │       └── run_all_earlgrey.sh
│   └── summary/
│
├── 08_RIP_Analysis/
│   ├── README.md
│   └── scripts/
│       ├── RIPCAL/
│       │   └── run_RIP_all.sh
│       └── summary/
│           └── make_TE_RIP_results_table.py
│
├── 09_McClintock/
│   ├── README.md
│   └── scripts/
│
├── 10_KEGG/
│   ├── README.md
│   │
│   ├── KAAS_KEGG_Analyzer/
│   │   ├── README.md
│   │   ├── app.py
│   │   ├── kaas_kegg_pipeline.py
│   │   ├── run_app.sh
│   │   ├── requirements.txt
│   │   └── results/
│   │       └── .gitkeep
│   │
│   └── scripts/
│       ├── KO_annotation/
│       ├── pathway_annotation/
│       └── summary/
│
├── 11_Genome_Circos_Plot/
│   ├── README.md
│   └── scripts/
│       ├── circos_input_builder/
│       │   └── TNW1_complete_circos_builder.py
│       └── circos_plot/
│           └── TNW1_final_compact_circos.R
│
├── 12_Telomere_Analysis/
│   ├── README.md
│   └── scripts/
│       ├── 01_run_tidk.sh
│       ├── 02_merge_tidk_results.py
│       ├── 03_summarise_telomeres.py
│       └── 04_generate_results_text.py
│
├── 13_Effector_Prediction/
│   ├── README.md
│   └── scripts/
│       └── fasta_preparation/
│
├── results/
│   └── TE_RIP/
│       ├── TE_RIP_all_genomes_summary.tsv
│       └── TE_RIP_all_genomes_summary.xlsx
│
├── workflow.png
├── README.md
├── CITATION.cff
├── LICENSE
└── .gitignore
```

## Analysis modules

| Module | Purpose |
|---|---|
| `01_Genome_Quality/BUSCO` | Genome and predicted-protein completeness assessment |
| `02_Phylogeny` | Multi-gene phylogenetic analysis and visualization |
| `03_OrthoFinder_6_Genomes` | Orthology and phylogenomics analysis of six genomes |
| `04_OrthoFinder_36_Genomes` | Comparative orthology and phylogenomics across 36 genomes |
| `05_CAFE5_Gene_Family_Evolution` | Gene-family expansion and contraction analysis |
| `06_ncRNA` | Non-coding RNA annotation/analysis |
| `07_Transposable_Elements` | Transposable-element annotation and summary |
| `08_RIP_Analysis` | Repeat-induced point mutation analysis and RIP–TE analysis |
| `09_McClintock` | Transposable-element insertion analysis |
| `10_KEGG` | KEGG/KO annotation and pathway analysis |
| `11_Whole_genome_Circos_Plot` | Circular genome visualisation (Circos plots) of the Fusarium isolates F. graminearum (TNW1; Figure 7) and F.avenaceum (DMW8; Figure 8), illustrating genome-wide organisation and functional genomic features. The outer ring represents scaffold organisation, numbered sequentially. Subsequent tracks depict GC content density, gene density, transposable element (TE) density, RIP-associated regions, GO-annotated genes, TE-rich regions/classes, AT-rich regions, predicted secondary metabolite biosynthetic gene clusters (antiSMASH), young and old TE insertions, TE–RIP overlap regions, and rRNA/tRNA loci. Colored ribbons in the centre indicate intra-genomic repetitive or syntenic relationships based on sequence similarity. To improve visual clarity, minor scaffolds (<1 Mb) were excluded. |
| `12_Telomere_Analysis` | finding telomear repeats |
| `13_Effector_Prediction` | Preparation of protein sequences for downstream effector prediction |

## Data organization

Input datasets, metadata, accession information, and analysis outputs are organized separately from computational scripts.

- `data/` contains metadata and input information required to reproduce analyses.
- `results/` contains selected derived tables and summary results.
- `supplementary/` contains supplementary tables associated with the manuscript.
- Large raw genome/protein datasets and computationally generated intermediate files are not included unless explicitly stated.

## Reproducibility

Each analysis module contains its own `README.md` where applicable. These files document the relevant software, parameters, input requirements, scripts, and expected outputs for that analysis.

The repository is intended to provide a transparent record of the computational workflow supporting the associated publication.
