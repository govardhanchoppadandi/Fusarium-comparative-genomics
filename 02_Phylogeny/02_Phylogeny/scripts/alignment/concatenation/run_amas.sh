#!/bin/bash

conda activate phylo_env

python AMAS.py concat \
-i ITS_aligned.fasta \
   TEF1_aligned.fasta \
   RPB2_aligned.fasta \
-f fasta \
-d dna \
-p partitions.txt \
-t concatenated.fasta

awk '
/^>/ {
    if (len) print len
    print
    len=0
    next
}
{
    len+=length($0)
}
END{
    print len
}' concatenated.fasta
