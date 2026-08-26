# OrthoFinder Analysis of 36 *Fusarium* Genomes

## Overview

Comparative orthology analysis was performed across 36 *Fusarium* genomes using their predicted protein sequences.

The analysis was performed using **OrthoFinder v3.1.5** with **DIAMOND** for all-versus-all protein sequence similarity searches, **MCL** for orthogroup inference, **FAMSA** for multiple sequence alignment, and **FastTree v2.2.0** for gene-tree inference and species-tree inference.

The workflow was implemented as a checkpoint-based analysis to preserve completed computational stages and allow subsequent stages to be completed without unnecessarily repeating computationally intensive analyses.

The complete workflow consists of:

1. Protein input preparation
2. DIAMOND all-versus-all sequence comparison
3. Orthogroup inference using MCL
4. Multiple sequence alignment using FAMSA
5. Individual gene-tree inference using FastTree
6. Species-tree inference from the concatenated species-tree alignment
7. Gene-tree/species-tree reconciliation
8. Orthologue inference
9. Hierarchical orthogroup inference
10. Final OrthoFinder comparative-genomics results
11. Downstream orthogroup similarity analysis and visualization

---

# 1. Input Data

The analysis used predicted protein sequences from **36 *Fusarium* genomes**.

Each genome was represented by one standardized protein FASTA file.

The protein sequences were prepared and standardized before being supplied to OrthoFinder.

The analysis therefore used:

- **36 genomes**
- **36 proteomes**
- one protein FASTA file per genome/species

The standardized protein files were used as the input dataset for OrthoFinder.

---

# 2. OrthoFinder Analysis

OrthoFinder **v3.1.5** was used for comparative orthology analysis.

The principal software components were:

| Analysis component | Software |
|---|---|
| Orthology analysis | OrthoFinder v3.1.5 |
| Protein similarity search | DIAMOND |
| Orthogroup clustering | MCL |
| Multiple sequence alignment | FAMSA |
| Gene-tree inference | FastTree v2.2.0 |
| Species-tree inference | FastTree v2.2.0 |

The OrthoFinder workflow generated the sequence similarity results, orthogroups, multiple sequence alignments, gene trees, species-tree alignment, and downstream orthology results.

---

# 3. DIAMOND All-versus-All Protein Comparison

The first major computational stage was the all-versus-all comparison of the 36 proteomes using DIAMOND.

For 36 genomes, the analysis involved:

**36 × 36 = 1,296 genome/proteome comparisons**

The DIAMOND sequence-search stage was completed successfully.

### Status

- **36 proteomes:** completed
- **1,296 comparisons:** completed
- **DIAMOND:** completed

The resulting similarity-search information was subsequently used for orthogroup inference.

---

# 4. Orthogroup Inference

Following the DIAMOND sequence similarity stage, OrthoFinder used **MCL clustering** to infer orthogroups.

Orthogroups represent sets of genes inferred to share common evolutionary ancestry across the analyzed genomes.

The MCL orthogroup-inference stage was completed before proceeding to multiple sequence alignment.

### Status

- DIAMOND results available
- MCL clustering completed
- Orthogroup assignments generated

The resulting orthogroup assignments were retained in the OrthoFinder results directory.

---

# 5. Multiple Sequence Alignment

Protein sequences belonging to the inferred orthogroups were aligned using **FAMSA**.

A total of:

**11,966 multiple sequence alignments**

were generated.

These alignments formed the input for subsequent individual gene-tree inference.

### Status

- **11,966 alignments generated**
- **FAMSA stage completed**

The existing alignments were retained and subsequently used for the checkpoint-based gene-tree workflow.

---

# 6. Gene-Tree Inference

Individual gene trees were inferred from the FAMSA protein alignments using **FastTree v2.2.0**.

Because gene-tree inference represented a computationally intensive stage, a checkpoint-based workflow was used.

The workflow examined the existing OrthoFinder results and processed orthogroup alignments individually.

For each orthogroup:

1. The corresponding FAMSA alignment was identified.
2. Existing valid gene trees were checked.
3. Existing valid trees were retained and skipped.
4. Missing gene trees were generated using FastTree.
5. The resulting Newick tree was validated.
6. Successfully generated trees were placed in the `Gene_Trees` directory.
7. Failed orthogroups were recorded.
8. The workflow could be resumed without repeating successfully completed trees.

The checkpoint approach therefore prevented unnecessary repetition of completed gene-tree calculations.

### Final gene-tree status

- **Expected gene trees:** 11,965
- **Completed gene trees:** 11,965
- **Failed gene trees:** 0

Therefore:

**11,965 / 11,965 gene trees completed successfully.**

The gene-tree inference stage is complete.

---

# 7. Species-Tree Inference

The next stage uses the existing OrthoFinder concatenated species-tree alignment:

```text
SpeciesTreeAlignment.fa
This alignment represents the concatenated information used for species-tree inference across the 36 genomes.

The species-tree workflow verifies that:

SpeciesTreeAlignment.fa exists;
the expected 36 species are represented;
the alignment is suitable for tree inference;
FastTree v2.2.0 is executed on the existing alignment;
the resulting Newick tree is validated; and
the validated species tree is retained in the results directory.

The species-tree workflow does not repeat:

DIAMOND
MCL
FAMSA
completed gene-tree inference
Current status

Species-tree inference is the current stage of the workflow.

8. Gene-Tree / Species-Tree Reconciliation

After completion and validation of the species tree, OrthoFinder proceeds to reconciliation of the individual gene trees with the species tree.

This stage uses the inferred gene trees and species tree to determine evolutionary relationships among genes and species.

The reconciliation stage provides the basis for identifying:

gene duplications
gene losses
orthologous relationships
paralogous relationships
hierarchical orthogroups
Status

Next stage after species-tree completion.
9. Orthologue Inference

Following gene-tree/species-tree reconciliation, OrthoFinder determines orthologous relationships among genes.

The resulting relationships can include:

one-to-one orthologues
one-to-many orthologues
many-to-one orthologues
many-to-many orthologues

These relationships are derived from the evolutionary information contained in the gene trees and species tree.

The resulting orthologue information forms an important component of the final comparative-genomics dataset.
10. Hierarchical Orthogroups

OrthoFinder subsequently generates hierarchical orthogroup relationships.

Hierarchical orthogroups allow orthologous relationships to be considered at different evolutionary levels of the inferred species phylogeny.

These results provide the basis for downstream comparative-genomics analyses across the 36 Fusarium genomes.
11. Final OrthoFinder Results

The completed OrthoFinder analysis is expected to provide the principal comparative-genomics outputs, including:

Orthogroups
Orthologues
Hierarchical orthogroups
Gene trees
Species tree
Gene duplication information
Comparative-genomics statistics
Species relationships
Orthologue relationship tables

The final results are retained in the OrthoFinder results directory.
12. OrthoFinder Results Directory

The primary OrthoFinder results used for downstream analysis were located at:

D:/ORTHOFINDER/FUSARIUM36_FINAL/Results_Aug12_5

The downstream visualization scripts were designed to read these results without modifying the original OrthoFinder output.
13. Downstream Orthogroup Similarity Analysis

Following the OrthoFinder analysis, orthogroup presence/absence information was used to calculate pairwise similarity among the 36 genomes.

The primary input was:

Orthogroups/Orthogroups.tsv

For each orthogroup and genome, the analysis determined whether the orthogroup was present.

This generated a binary orthogroup presence/absence matrix.

Pairwise similarity among genomes was then calculated using the Jaccard similarity coefficient:

Jaccard = Shared orthogroups / Union of orthogroups

The resulting similarity matrix was used for downstream heatmap and Circos visualization.
14. Jaccard Similarity Heatmap

A publication-style Jaccard similarity heatmap was generated for the 36 Fusarium genomes.

The heatmap represents similarity in orthogroup composition based on orthogroup presence/absence.

The analysis:

Reads Orthogroups.tsv.
Identifies the 36 genome columns.
Calculates orthogroup counts for each genome.
Converts the data into a presence/absence matrix.
Calculates pairwise Jaccard similarity.
Generates a 36 × 36 similarity matrix.
Orders the genomes according to the defined species grouping.
Generates a publication-style heatmap.
Saves the heatmap as PNG and PDF.
Saves the Jaccard matrix as a TSV file.
Saves the species-group information as a TSV file.
Main heatmap output
Fusarium36_Jaccard_Heatmap_Publication.png
Fusarium36_Jaccard_Heatmap_Publication.pdf
Fusarium36_Jaccard_Matrix.tsv
Fusarium36_Species_Groups.tsv
15. Circos Orthogroup Similarity Visualization

A Circos-style visualization was generated to display high-confidence pairwise orthogroup similarity relationships among the 36 genomes.

The visualization uses the calculated:

orthogroup presence/absence information;
pairwise Jaccard similarity; and
shared orthogroup counts.

The Circos analysis was performed using the R package:

circlize

The original OrthoFinder results were treated as read-only.16. High-Confidence Circos Links

The initial strict selection criterion was:

Jaccard similarity >= 0.80

and

Shared orthogroups >= 9,000

Pairwise relationships satisfying both criteria were selected as high-confidence links.

If fewer than 15 relationships satisfied the strict criteria, the visualization script selected the strongest 40 pairwise relationships according to:

descending Jaccard similarity;
descending shared orthogroup count.

This prevents an empty or excessively sparse Circos visualization while retaining the strongest observed relationships.

The selected relationships were saved as:

Fusarium36_Circos_Final_Links.csv
17. Circos Visualization Components

The Circos figure contains three principal tracks.

Track 1 — Genome names

The 36 genome/species identifiers are displayed around the circular plot.

Track 2 — Species-group annotation

The genomes are grouped according to the defined species categories.

The visualization distinguishes:

F. graminearum
F. avenaceum
Track 3 — Orthogroup content

The orthogroup content of each genome is represented as a bar around the circular plot.

Ribbons

Ribbons connect genome pairs showing high orthogroup similarity.

Ribbon selection is based on Jaccard similarity and shared orthogroup counts.

18. Circos Outputs

The Circos analysis generates:

Fusarium36_Circos_HighConfidence.png

and

Fusarium36_Circos_HighConfidence.pdf

The selected pairwise relationships are additionally saved as:

Fusarium36_Circos_Final_Links.csv
19. Visualization Output Directory

The downstream plots and derived similarity tables were written to:

D:/ORTHOFINDER/FUSARIUM36_ORTHOFINDER_PLOTS

The visualization scripts do not modify the original OrthoFinder results.

20. Reproducibility

The complete workflow is represented by scripts covering the major stages of the analysis.

The repository contains scripts for:

OrthoFinder execution;
checkpoint-based gene-tree inference;
species-tree inference;
species-tree recovery;
downstream comparative analysis;
Jaccard similarity analysis;
Circos visualization; and
final quality-control procedures.

The checkpoint-based scripts allow computationally completed stages to be retained and reused.

Therefore, completed DIAMOND, MCL, FAMSA, and gene-tree calculations do not need to be unnecessarily repeated when continuing the workflow.
21. Current Workflow Status

The current status of the 36-genome OrthoFinder workflow is:
| Stage | Analysis                              | Status                 |
| ----- | ------------------------------------- | ---------------------- |
| 1     | 36 proteomes prepared                 | ✅ Completed            |
| 2     | DIAMOND all-vs-all                    | ✅ Completed            |
| 3     | MCL orthogroup inference              | ✅ Completed            |
| 4     | FAMSA multiple sequence alignment     | ✅ 11,966 alignments    |
| 5     | FastTree gene-tree inference          | ✅ 11,965 / 11,965      |
| 6     | Failed gene trees                     | ✅ 0                    |
| 7     | Species-tree inference                | 🔄 Current stage       |
| 8     | Gene-tree/species-tree reconciliation | ⏳ Pending              |
| 9     | Orthologue inference                  | ⏳ Pending              |
| 10    | Hierarchical orthogroups              | ⏳ Pending              |
| 11    | Final OrthoFinder results             | ⏳ Pending              |
| 12    | Jaccard similarity analysis           | 🔄 Downstream analysis |
| 13    | Heatmap visualization                 | ✅ Generated            |
| 14    | Circos visualization                  | ✅ Generated            |
22. Important Distinction Between Core Analysis and Visualization

The Circos and Jaccard heatmap analyses are downstream analyses of the OrthoFinder orthogroup results.

They do not replace the core OrthoFinder workflow.

The core evolutionary workflow is:
36 Fusarium proteomes
        ↓
DIAMOND all-vs-all
        ↓
MCL orthogroup inference
        ↓
FAMSA orthogroup alignments
        ↓
FastTree gene trees
        ↓
Species-tree alignment
        ↓
FastTree species tree
        ↓
Gene-tree/species-tree reconciliation
        ↓
Orthologue inference
        ↓
Hierarchical orthogroups
        ↓
Final OrthoFinder results
The downstream visualization workflow is:
Orthogroups.tsv
        ↓
Orthogroup presence/absence
        ↓
Pairwise Jaccard similarity
        ├───────────────┐
        ↓               ↓
Jaccard heatmap       Circos
        ↓               ↓
PNG/PDF              PNG/PDF
23. Directory Structure
04_OrthoFinder_36_Genomes/
│
├── README.md
│
└── scripts/
    │
    ├── orthofinder/
    │   └── run_orthofinder_36.sh
    │
    ├── tree_inference/
    │   ├── run_fusarium36_trees_checkpoint.sh
    │   ├── run_fusarium36_species_tree_checkpoint.sh
    │   └── run_fusarium36_species_tree_fast.sh
    │
    └── downstream_analysis/
        └── run_fusarium36_step24_corrected.sh


24. Software
OrthoFinder v3.1.5
DIAMOND
MCL
FAMSA
FastTree v2.2.0
R
circlize
ggplot2
25. Final Analysis Framework

The complete comparative-genomics framework can therefore be summarized as:
                    36 Fusarium proteomes
                             │
                             ▼
                  DIAMOND all-vs-all search
                     1,296 comparisons
                             │
                             ▼
                    MCL orthogroup inference
                             │
                             ▼
                   FAMSA sequence alignment
                      11,966 alignments
                             │
                             ▼
                    FastTree gene trees
                    11,965 / 11,965
                         0 failed
                             │
                             ▼
                  SpeciesTreeAlignment.fa
                             │
                             ▼
                   FastTree species tree
                             │
                             ▼
              Gene-tree / species-tree
                     reconciliation
                             │
                             ▼
                    Orthologue inference
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
          One-to-one    One-to-many    Many-to-many
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                  Hierarchical orthogroups
                             │
                             ▼
                Final OrthoFinder results
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
       Orthogroup.tsv                Comparative statistics
              │
              ▼
       Presence / absence
              │
              ▼
      Pairwise Jaccard similarity
              │
        ┌─────┴─────┐
        ▼           ▼
     Heatmap      Circos
        │           │
        ▼           ▼
      PNG/PDF     PNG/PDF
Primary Results Location
D:/ORTHOFINDER/FUSARIUM36_FINAL/Results_Aug12_5
Downstream Visualization Location
D:/ORTHOFINDER/FUSARIUM36_ORTHOFINDER_PLOTS
Analysis Integrity

All downstream visualization scripts were designed to read the OrthoFinder results as read-only input.

No original OrthoFinder result files are intentionally modified, deleted, or overwritten by the Jaccard heatmap or Circos visualization workflows.

### One important correction

I would **not** write in the README that the "final OrthoFinder results are complete" yet. Based on the workflow you showed me, **11,965/11,965 gene trees are complete, but the species-tree/reconciliation/orthologue stages are still the remaining core OrthoFinder stages**.

So your scientifically accurate status **right now** is:

**DIAMOND → MCL → FAMSA → Gene Trees = COMPLETE**  
**Species Tree = CURRENT**  
**Reconciliation → Orthologues → Hierarchical Orthogroups → Final results = NEXT**

The **heatmap and Circos are already downstream visualizations**, so they can exist before the final reconciliation stage, because they are based on `Orthogroups.tsv`.
