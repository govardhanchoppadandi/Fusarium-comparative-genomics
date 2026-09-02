from pathlib import Path
from collections import defaultdict
from Bio import SeqIO

# ==========================================================
# INPUT / OUTPUT
# ==========================================================

in_dir = Path("/home/govardhan/fusarium/alignments")
out_dir = Path("/home/govardhan/fusarium/concat")

out_dir.mkdir(parents=True, exist_ok=True)

# ==========================================================
# SPECIES LIST
# ==========================================================

species = [
    "DMW8",
    "Faven",
    "Fculm",
    "Fgram",
    "Fpoae",
    "TNW1"
]

concat = defaultdict(str)

og_count = 0
total_length = 0

# ==========================================================
# PROCESS EACH ORTHOGROUP
# ==========================================================

for fasta in sorted(in_dir.glob("*")):

    seqs = {}

    for rec in SeqIO.parse(fasta, "fasta"):

        sp = rec.id.split("|")[0]

        seqs[sp] = str(rec.seq)

    if len(seqs) == 0:
        continue

    aln_len = len(next(iter(seqs.values())))

    for sp in species:

        concat[sp] += seqs.get(
            sp,
            "-" * aln_len
        )

    total_length += aln_len
    og_count += 1

# ==========================================================
# WRITE CONCATENATED ALIGNMENT
# ==========================================================

outfile = out_dir / "concat6.fasta"

with open(outfile, "w") as f:

    for sp in species:

        f.write(f">{sp}\n")
        f.write(concat[sp] + "\n")

# ==========================================================
# SUMMARY
# ==========================================================

print(f"Used {og_count} OGs")
print(f"Species: {species}")
print(f"Total alignment length: {total_length}")
print(f"Written: {outfile}")
