def get_fasta_ids(fasta_file):

    """
    Extract FASTA sequence IDs.

    Only the first whitespace-separated
    field after > is used.
    """

    ids = []

    with open(
        fasta_file,
        encoding="utf-8",
        errors="replace"
    ) as handle:

        for line in handle:

            if line.startswith(">"):

                protein_id = (
                    line[1:]
                    .strip()
                    .split()[0]
                )

                ids.append(
                    protein_id
                )

    return ids
