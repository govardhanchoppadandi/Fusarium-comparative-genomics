#!/bin/bash

# Maximum-likelihood phylogenetic inference using IQ-TREE 2

iqtree2 \
-s concatenated.fasta \
-p partitions.txt \
-st DNA \
-m MFP+MERGE \
-bb 1000 \
-alrt 1000 \
-nt AUTO
