from Bio import SeqIO

# ==========================================================
# INPUT
# ==========================================================

alignment_file = "/home/govardhan/fusarium/concat/concat6.fasta"

# ==========================================================
# READ CONCATENATED ALIGNMENT
# ==========================================================

seqs = list(
    SeqIO.parse(
        alignment_file,
        "fasta"
    )
)

# ==========================================================
# BASIC VALIDATION
# ==========================================================

print("==============================================")
print("FUSARIUM 6 — CONCATENATED ALIGNMENT QC")
print("==============================================")

print()
print("Alignment:", alignment_file)
print("Number of sequences:", len(seqs))

# ==========================================================
# EXPECTED SPECIES
# ==========================================================

expected_species = [
    "DMW8",
    "Faven",
    "Fculm",
    "Fgram",
    "Fpoae",
    "TNW1"
]

observed_species = [
    rec.id
    for rec in seqs
]

print()
print("Expected species:")
for sp in expected_species:
    print("  ", sp)

print()
print("Observed species:")
for sp in observed_species:
    print("  ", sp)

# ==========================================================
# CHECK SPECIES COUNT
# ==========================================================

if len(seqs) != 6:
    raise RuntimeError(
        f"ERROR: Expected 6 sequences, found {len(seqs)}"
    )

# ==========================================================
# CHECK SPECIES NAMES
# ==========================================================

if set(observed_species) != set(expected_species):
    raise RuntimeError(
        "ERROR: Species names do not match expected 6 species."
    )

# ==========================================================
# CHECK ALIGNMENT LENGTHS
# ==========================================================

lengths = [
    len(rec.seq)
    for rec in seqs
]

print()
print("Sequence lengths:")
for rec in seqs:
    print(
        f"  {rec.id}: {len(rec.seq)}"
    )

unique_lengths = set(lengths)

print()
print("Unique alignment lengths:", unique_lengths)

if len(unique_lengths) != 1:
    raise RuntimeError(
        "ERROR: Concatenated sequences have different lengths."
    )

# ==========================================================
# FINAL VALIDATION
# ==========================================================

alignment_length = lengths[0]

print()
print("==============================================")
print("VALIDATION RESULTS")
print("==============================================")

print("Species:", len(seqs))
print("Alignment length:", alignment_length)
print("All sequences equal length: YES")
print("All expected species present: YES")

print()
print("PASS: concat6.fasta is valid for phylogenomic analysis.")
print("==============================================")
