# OrthoFinder Analysis of 36 *Fusarium* Genomes

## Overview

Comparative orthology analysis was performed across 36 *Fusarium* genomes using their predicted protein sequences.

The analysis was performed using OrthoFinder v3.1.5. DIAMOND was used for all-versus-all protein sequence similarity searches, MCL for orthogroup inference, FAMSA for multiple sequence alignment, and FastTree v2.2.0 for gene-tree and species-tree inference.

A checkpoint-based workflow was used to preserve completed computational stages and allow subsequent stages to be completed without unnecessarily repeating computationally intensive analyses.

The workflow comprises:

1. Protein input preparation
2. DIAMOND all-versus-all protein sequence comparison
3. Orthogroup inference using MCL
4. Multiple sequence alignment using FAMSA
5. Individual gene-tree inference using FastTree
6. Species-tree inference from the concatenated species-tree alignment
7. Gene-tree/species-tree reconciliation
8. Orthologue inference
9. Hierarchical orthogroup inference
10. Final OrthoFinder comparative-genomics results
11. Downstream orthogroup similarity analysis and visualization

At the current stage, the DIAMOND, MCL, FAMSA, and individual gene-tree stages have been completed. Species-tree inference is the current core-analysis stage. Reconciliation, orthologue inference, hierarchical orthogroup inference, and final OrthoFinder results remain to be completed.

---

## 1. Input Data

The analysis used predicted protein sequences from 36 *Fusarium* genomes.

Each genome was represented by one standardized protein FASTA file.

The input dataset consisted of 36 genomes, 36 proteomes, and one protein FASTA file per genome/species.

---

## 2. OrthoFinder Analysis

OrthoFinder v3.1.5 was used for comparative orthology analysis.

| Analysis component | Software |
|---|---|
| Orthology analysis | OrthoFinder v3.1.5 |
| Protein similarity search | DIAMOND |
| Orthogroup clustering | MCL |
| Multiple sequence alignment | FAMSA |
| Gene-tree inference | FastTree v2.2.0 |
| Species-tree inference | FastTree v2.2.0 |

The completed stages generated sequence-similarity results, orthogroup assignments, multiple sequence alignments, and individual gene trees. The existing concatenated species-tree alignment is used for the current species-tree inference stage.

---

## 3. DIAMOND All-versus-All Protein Comparison

The first major computational stage was the all-versus-all comparison of the 36 proteomes using DIAMOND.

For 36 proteomes, the comparison matrix corresponds to:

```text
36 × 36 = 1,296 directed proteome pairs
```

The DIAMOND sequence-search stage was completed successfully.

### Status

- 36 proteomes: completed
- 1,296 directed proteome pairs: completed
- DIAMOND sequence-search stage: completed

The resulting sequence-similarity information was subsequently used for orthogroup inference.

---

## 4. Orthogroup Inference

Following the DIAMOND sequence-similarity stage, OrthoFinder used MCL clustering to infer orthogroups.

Orthogroups represent groups of genes inferred to share common evolutionary ancestry across the analyzed genomes.

The MCL orthogroup-inference stage was completed before proceeding to multiple sequence alignment.

### Status

- DIAMOND results available
- MCL clustering completed
- Orthogroup assignments generated
- Existing orthogroup results retained in the OrthoFinder results directory

---

## 5. Multiple Sequence Alignment

Protein sequences belonging to the inferred orthogroups were aligned using FAMSA.

A total of:

```text
11,966 multiple sequence alignments
```

were generated.

These alignments formed the input for subsequent individual gene-tree inference.

### Status

- 11,966 alignments generated
- FAMSA stage completed
- Existing alignments retained for the checkpoint-based gene-tree workflow

---

## 6. Gene-Tree Inference

Individual gene trees were inferred from the FAMSA protein alignments using FastTree v2.2.0.

Because gene-tree inference was computationally intensive, a checkpoint-based workflow was used.

For each orthogroup, the workflow:

1. Identified the corresponding FAMSA alignment.
2. Checked for an existing valid gene tree.
3. Retained and skipped existing valid trees.
4. Generated missing gene trees using FastTree.
5. Validated the resulting Newick tree.
6. Placed successfully generated trees in the `Gene_Trees` directory.
7. Recorded failed orthogroups.
8. Allowed the workflow to resume without repeating successfully completed trees.

### Final gene-tree status

- Expected gene trees: 11,965
- Completed gene trees: 11,965
- Failed gene trees: 0

Therefore:

```text
11,965 / 11,965 gene trees completed successfully
0 failed gene trees
```

The individual gene-tree inference stage is complete.

---

## 7. Species-Tree Inference

The existing OrthoFinder concatenated species-tree alignment is used for species-tree inference.

The input alignment is:

```text
SpeciesTreeAlignment.fa
```

This alignment represents the concatenated sequence information used for species-tree inference across the 36 genomes.

The species-tree workflow verifies that:

1. `SpeciesTreeAlignment.fa` exists.
2. The expected 36 species are represented.
3. The alignment is available for tree inference.
4. FastTree v2.2.0 is executed on the existing alignment.
5. The resulting Newick tree is validated.
6. The validated species tree is retained in the results directory.

The species-tree workflow does not repeat DIAMOND, MCL, FAMSA, or completed individual gene-tree inference.

### Current status

**Species-tree inference is the current core-analysis stage.**

---

## 8. Gene-Tree/Species-Tree Reconciliation

After completion and validation of the species tree, the individual gene trees and species tree will be used for gene-tree/species-tree reconciliation.

This stage provides the evolutionary framework for identifying gene-level evolutionary events and relationships, including gene duplications, gene losses, orthologous relationships, paralogous relationships, and hierarchical orthogroups.

### Status

**Pending species-tree completion and subsequent reconciliation.**

---

## 9. Orthologue Inference

Following gene-tree/species-tree reconciliation, OrthoFinder will determine orthologous relationships among genes.

The resulting relationships may include:

- one-to-one orthologues
- one-to-many orthologues
- many-to-one orthologues
- many-to-many orthologues

These relationships are derived from the evolutionary information contained in the inferred gene trees and species tree.

### Status

**Pending completion of the preceding core OrthoFinder stages.**

---

## 10. Hierarchical Orthogroups

OrthoFinder will subsequently generate hierarchical orthogroup relationships.

Hierarchical orthogroups allow orthologous relationships to be considered at different evolutionary levels of the inferred species phylogeny.

These results will provide a basis for downstream comparative-genomics analyses across the 36 *Fusarium* genomes.

### Status

**Pending completion of the preceding core OrthoFinder stages.**

---

## 11. Final OrthoFinder Results

Upon completion of the remaining core stages, the OrthoFinder analysis will provide the principal comparative-genomics outputs, including:

- Orthogroups
- Orthologues
- Hierarchical orthogroups
- Gene trees
- Species tree
- Gene duplication information
- Comparative-genomics statistics
- Species relationships
- Orthologue relationship tables

The final results will be retained in the OrthoFinder results directory.

### Current status

**Final OrthoFinder analysis is not yet complete.**

The remaining core stages are:

```text
Species-tree inference
        ↓
Gene-tree/species-tree reconciliation
        ↓
Orthologue inference
        ↓
Hierarchical orthogroup inference
        ↓
Final OrthoFinder results
```

---

## 12. OrthoFinder Results Directory

The primary OrthoFinder results used for downstream analysis are located at:

```text
D:/ORTHOFINDER/FUSARIUM36_FINAL/Results_Aug12_5
```

The downstream visualization workflows were designed to read these results without modifying the original OrthoFinder output.

---

## 13. Downstream Orthogroup Similarity Analysis

Orthogroup presence/absence information was used to calculate pairwise similarity among the 36 genomes.

The primary input was:

```text
Orthogroups/Orthogroups.tsv
```

For each orthogroup and genome, the analysis determined whether the orthogroup was present, generating a binary orthogroup presence/absence matrix.

Pairwise similarity among genomes was calculated using the Jaccard similarity coefficient:

```text
Jaccard similarity =
Shared orthogroups / Union of orthogroups
```

The resulting similarity matrix was used for downstream heatmap and Circos visualization.

### Important distinction

This Jaccard analysis is a downstream analysis of the existing orthogroup assignments. It does not replace OrthoFinder gene-tree/species-tree reconciliation or orthologue inference.

---

## 14. Jaccard Similarity Heatmap

A publication-style Jaccard similarity heatmap was generated for the 36 *Fusarium* genomes.

The heatmap represents similarity in orthogroup composition based on orthogroup presence/absence.

The analysis:

1. Reads `Orthogroups.tsv`.
2. Identifies the 36 genome columns.
3. Calculates orthogroup presence/absence.
4. Calculates pairwise Jaccard similarity.
5. Generates a 36 × 36 similarity matrix.
6. Orders the genomes according to the predefined visualization grouping.
7. Generates a publication-style heatmap.
8. Saves the heatmap as PNG and PDF.
9. Saves the Jaccard matrix as a TSV file.
10. Saves the species-group information as a TSV file.

### Main heatmap outputs

```text
Fusarium36_Jaccard_Heatmap_Publication.png
Fusarium36_Jaccard_Heatmap_Publication.pdf
Fusarium36_Jaccard_Matrix.tsv
Fusarium36_Species_Groups.tsv
```

---

## 15. Circos Orthogroup Similarity Visualization

A Circos-style visualization was generated to display selected high-similarity pairwise orthogroup relationships among the 36 genomes.

The visualization uses:

- orthogroup presence/absence information
- pairwise Jaccard similarity
- shared orthogroup counts

The Circos analysis was performed using the R package `circlize`.

The original OrthoFinder results were treated as read-only input.

The Circos selection criteria are visualization criteria and do not represent an OrthoFinder-defined statistical confidence score.

---

## 16. High-Similarity Circos Links

The initial strict selection criterion was:

```text
Jaccard similarity >= 0.80
AND
Shared orthogroups >= 9,000
```

Pairwise relationships satisfying both criteria were selected for visualization.

If fewer than 15 relationships satisfied the strict criteria, the visualization script selected the strongest 40 pairwise relationships according to:

1. descending Jaccard similarity
2. descending shared orthogroup count

This fallback prevents an empty or excessively sparse visualization while retaining the strongest observed pairwise relationships.

The fallback affects only the visualization and does not alter the underlying OrthoFinder results or the Jaccard calculations.

The selected relationships were saved as:

```text
Fusarium36_Circos_Final_Links.csv
```

---

## 17. Circos Visualization Components

The Circos figure contains three principal tracks.

### Track 1 — Genome names

The 36 genome/species identifiers are displayed around the circular plot.

### Track 2 — Species-group annotation

For visualization, genomes are grouped according to the predefined categories used by the analysis script:

- *F. graminearum*
- *F. avenaceum*

These categories are used for visualization and do not replace the species relationships inferred by the OrthoFinder species-tree analysis.

### Track 3 — Orthogroup content

The orthogroup content of each genome is represented as a bar around the circular plot.

### Ribbons

Ribbons connect genome pairs showing selected high orthogroup similarity.

Ribbon selection is based on the Jaccard similarity and shared orthogroup thresholds described above.

---

## 18. Circos Outputs

The Circos analysis generates:

```text
Fusarium36_Circos_HighConfidence.png
Fusarium36_Circos_HighConfidence.pdf
```

The selected pairwise relationships are additionally saved as:

```text
Fusarium36_Circos_Final_Links.csv
```

The filenames retain the original `HighConfidence` naming convention used by the analysis script; the links should be interpreted as high-similarity visualization links rather than formal statistical confidence estimates.

---

## 19. Visualization Output Directory

The downstream plots and derived similarity tables were written to:

```text
D:/ORTHOFINDER/FUSARIUM36_ORTHOFINDER_PLOTS
```

The visualization scripts were designed to read the original OrthoFinder results as read-only input.

No original OrthoFinder result files are intentionally modified, deleted, or overwritten by the Jaccard heatmap or Circos visualization workflows.

---

## 20. Reproducibility

The workflow is represented by scripts covering the major stages of the analysis.

The repository contains scripts for:

- OrthoFinder execution
- checkpoint-based gene-tree inference
- species-tree inference
- species-tree recovery
- downstream comparative analysis
- Jaccard similarity analysis
- Circos visualization
- final quality-control procedures

The checkpoint-based scripts allow completed computational stages to be retained and reused.

Therefore, completed DIAMOND, MCL, FAMSA, and gene-tree calculations do not need to be unnecessarily repeated when continuing the workflow.

---

## 21. Current Workflow Status

| Stage | Analysis | Status |
|---|---|---|
| 1 | 36 proteomes prepared | Completed |
| 2 | DIAMOND all-versus-all | Completed |
| 3 | MCL orthogroup inference | Completed |
| 4 | FAMSA multiple sequence alignment | 11,966 alignments completed |
| 5 | FastTree gene-tree inference | 11,965 / 11,965 completed |
| 6 | Failed gene trees | 0 |
| 7 | Species-tree inference | Current stage |
| 8 | Gene-tree/species-tree reconciliation | Pending |
| 9 | Orthologue inference | Pending |
| 10 | Hierarchical orthogroups | Pending |
| 11 | Final OrthoFinder results | Pending |
| 12 | Jaccard similarity analysis | Downstream analysis completed |
| 13 | Heatmap visualization | Generated |
| 14 | Circos visualization | Generated |

---

## 22. Important Distinction Between Core Analysis and Visualization

The Circos and Jaccard heatmap analyses are downstream analyses of the OrthoFinder orthogroup results.

They do not replace the core OrthoFinder evolutionary workflow.

### Core OrthoFinder workflow

```text
36 Fusarium proteomes
        ↓
DIAMOND all-versus-all
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
```

### Downstream visualization workflow

```text
Orthogroups.tsv
        ↓
Orthogroup presence/absence
        ↓
Pairwise Jaccard similarity
        ├────────────────┐
        ↓                ↓
Jaccard heatmap       Circos
        ↓                ↓
PNG/PDF              PNG/PDF
```

The downstream visualization workflow is documented separately from the remaining core OrthoFinder stages.

---

## 23. Directory Structure

```text
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
```

---

## 24. Software

```text
OrthoFinder v3.1.5
DIAMOND
MCL
FAMSA
FastTree v2.2.0
R
circlize
ggplot2
```

---

## 25. Final Analysis Framework

The complete analysis framework can be summarized as:

```text
                    36 Fusarium proteomes
                             │
                             ▼
                  DIAMOND all-versus-all
                 1,296 directed pairs
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
              Gene-tree/species-tree
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
       Orthogroups.tsv              Comparative statistics
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
```

The first part of the framework represents the core OrthoFinder evolutionary analysis. The Jaccard heatmap and Circos analysis represent downstream visualization of orthogroup composition.

---

## Primary Results Location

```text
D:/ORTHOFINDER/FUSARIUM36_FINAL/Results_Aug12_5
```

## Downstream Visualization Location

```text
D:/ORTHOFINDER/FUSARIUM36_ORTHOFINDER_PLOTS
```

## Analysis Integrity

All downstream visualization scripts were designed to read the OrthoFinder results as read-only input.

No original OrthoFinder result files are intentionally modified, deleted, or overwritten by the Jaccard heatmap or Circos visualization workflows.

At the current stage, the completed core OrthoFinder results comprise the DIAMOND sequence-search stage, MCL orthogroup inference, FAMSA alignments, and complete individual gene-tree inference. Species-tree inference is currently being performed, followed by reconciliation, orthologue inference, hierarchical orthogroup inference, and final OrthoFinder result generation.

The downstream Jaccard and Circos analyses document orthogroup-composition similarity and do not substitute for these remaining evolutionary-analysis stages.
