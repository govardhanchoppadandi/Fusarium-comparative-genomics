from pathlib import Path

# ============================================================
# INPUT FASTA FILE
# ============================================================

input_fasta = r"E:\1 Manuscript\Fusarium genome\DNW-8 Augustus\SIGNALP\SP_proteins.fasta"

# ============================================================
# OUTPUT FOLDER
# ============================================================

output_folder = r"E:\1 Manuscript\Fusarium genome\DNW-8 Augustus\SIGNALP\SP CHUNKS 250"

Path(output_folder).mkdir(parents=True, exist_ok=True)

# ============================================================
# NUMBER OF SEQUENCES PER CHUNK
# ============================================================

chunk_size = 250

# ============================================================
# READ FASTA
# ============================================================

sequences = []

with open(input_fasta, "r") as f:

    header = None
    seq_lines = []

    for line in f:

        line = line.strip()

        if not line:
            continue

        if line.startswith(">"):

            if header:
                sequences.append(
                    (header, "".join(seq_lines))
                )

            header = line
            seq_lines = []

        else:
            seq_lines.append(line)

    # Save final sequence
    if header:
        sequences.append(
            (header, "".join(seq_lines))
        )

# ============================================================
# SPLIT FASTA INTO CHUNKS
# ============================================================

for i in range(0, len(sequences), chunk_size):

    chunk_sequences = sequences[i:i + chunk_size]

    chunk_number = i // chunk_size + 1

    chunk_file = (
        Path(output_folder)
        / f"proteins_chunk_{chunk_number}.fasta"
    )

    with open(chunk_file, "w") as f:

        for header, seq in chunk_sequences:

            f.write(f"{header}\n")

            # Wrap protein sequence at 80 characters
            for j in range(0, len(seq), 80):

                f.write(seq[j:j + 80] + "\n")

# ============================================================
# SUMMARY
# ============================================================

number_of_chunks = (
    len(sequences) + chunk_size - 1
) // chunk_size

print("==============================================")
print("FASTA splitting completed")
print("==============================================")
print(f"Total protein sequences : {len(sequences)}")
print(f"Sequences per chunk     : {chunk_size}")
print(f"Number of chunks        : {number_of_chunks}")
print(f"Output folder           : {output_folder}")
print("==============================================")
