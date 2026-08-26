#!/bin/bash

# MAFFT alignment of ITS, TEF1 and RPB2 sequences

mafft --auto ITS_all.fasta > ITS_aligned.fasta

mafft --auto TEF1_all.fasta > TEF1_aligned.fasta

mafft --auto RPB2_all.fasta > RPB2_aligned.fasta
