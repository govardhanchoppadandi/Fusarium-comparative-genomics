#!/usr/bin/env python3

import re
from collections import defaultdict


GO_PATTERN = re.compile(r"GO:\d+")


# ============================================================
# INTERPRO2GO
# ============================================================

def load_interpro2go(filename):

    mapping = defaultdict(set)

    print("Loading InterPro2GO...")

    with open(
        filename,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            if line.startswith("!"):
                continue

            if " > GO:" not in line:
                continue

            left, right = line.split(" > ", 1)

            go_match = GO_PATTERN.search(right)

            if not go_match:
                continue

            go_id = go_match.group()

            ipr_match = re.search(
                r"(IPR\d+)",
                left
            )

            if ipr_match:

                ipr_id = ipr_match.group()

                mapping[ipr_id].add(go_id)

    print(
        f"InterPro IDs with GO mappings: "
        f"{len(mapping):,}"
    )

    return mapping


# ============================================================
# GO ONTOLOGY
# ============================================================

def load_go_ontology(filename):

    terms = {}

    current_id = None
    current_name = None
    current_namespace = None

    print("Loading GO ontology...")

    with open(
        filename,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:

        for line in f:

            line = line.rstrip()

            if line == "[Term]":

                if current_id:

                    terms[current_id] = {
                        "name": current_name or "",
                        "namespace": current_namespace or ""
                    }

                current_id = None
                current_name = None
                current_namespace = None

            elif line.startswith("id: GO:"):

                current_id = line.split(
                    "id:",
                    1
                )[1].strip()

            elif line.startswith("name:"):

                current_name = line.split(
                    "name:",
                    1
                )[1].strip()

            elif line.startswith("namespace:"):

                current_namespace = line.split(
                    "namespace:",
                    1
                )[1].strip()

        if current_id:

            terms[current_id] = {
                "name": current_name or "",
                "namespace": current_namespace or ""
            }

    print(
        f"GO terms loaded: {len(terms):,}"
    )

    return terms


# ============================================================
# GO-SLIM
# ============================================================

def load_go_slim(filename):

    slim = set()

    with open(
        filename,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:

        for line in f:

            line = line.rstrip()

            if line.startswith("id: GO:"):

                slim.add(
                    line.split(
                        "id:",
                        1
                    )[1].strip()
                )

    print(
        f"GO-Slim terms loaded: {len(slim):,}"
    )

    return slim


# ============================================================
# FASTA PROTEIN IDS
# ============================================================

def load_fasta_proteins(filename):

    proteins = []

    with open(
        filename,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:

        for line in f:

            if line.startswith(">"):

                protein = line[1:].strip().split()[0]

                if protein:
                    proteins.append(protein)

    return proteins


# ============================================================
# CATEGORY
# ============================================================

def go_category(namespace):

    if namespace == "biological_process":

        return "Biological Process"

    if namespace == "molecular_function":

        return "Molecular Function"

    if namespace == "cellular_component":

        return "Cellular Component"

    return "Unknown"


# ============================================================
# INTERPROSCAN TSV
# ============================================================

def process_interpro_tsv(
    tsv_file,
    interpro2go,
    go_terms,
    fasta_file=None
):

    protein_go = defaultdict(
        lambda: defaultdict(set)
    )

    annotation_rows = []

    interpro_ids = defaultdict(set)

    interpro_descriptions = defaultdict(set)

    pfam_ids = defaultdict(set)

    analysis_sources = defaultdict(set)

    go_direct_ids = defaultdict(set)

    pathways = defaultdict(set)

    proteins_seen = set()

    total_rows = 0
    ipr_rows = 0
    go_rows = 0

    print(
        "Reading InterProScan TSV..."
    )

    # --------------------------------------------------------
    # LOAD ALL FASTA PROTEINS FIRST
    # --------------------------------------------------------

    if fasta_file:

        try:

            for protein in load_fasta_proteins(
                fasta_file
            ):

                proteins_seen.add(
                    protein
                )

        except Exception as e:

            print(
                "WARNING: Could not read FASTA proteins:"
            )

            print(e)

    # --------------------------------------------------------
    # READ INTERPROSCAN
    # --------------------------------------------------------

    with open(
        tsv_file,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:

        for line in f:

            if not line.strip():
                continue

            if line.startswith("#"):
                continue

            fields = line.rstrip(
                "\r\n"
            ).split("\t")

            if len(fields) < 15:
                continue

            total_rows += 1

            # Standard InterProScan TSV

            protein = fields[0].strip()

            analysis = fields[3].strip()

            signature = fields[4].strip()

            signature_description = fields[5].strip()

            ipr = fields[11].strip()

            ipr_description = fields[12].strip()

            go_field = fields[13].strip()

            pathway_field = fields[14].strip()

            proteins_seen.add(
                protein
            )

            # ------------------------------------------------
            # ANALYSIS
            # ------------------------------------------------

            if analysis and analysis != "-":

                analysis_sources[
                    protein
                ].add(
                    analysis
                )

            # ------------------------------------------------
            # PFAM
            # ------------------------------------------------

            if (

                analysis.lower() == "pfam"

                and signature

                and signature != "-"

            ):

                pfam_ids[
                    protein
                ].add(
                    signature
                )

            # ------------------------------------------------
            # DIRECT GO FROM INTERPROSCAN
            # ------------------------------------------------

            if go_field and go_field != "-":

                for go_id in GO_PATTERN.findall(
                    go_field
                ):

                    go_direct_ids[
                        protein
                    ].add(
                        go_id
                    )

            # ------------------------------------------------
            # PATHWAYS
            # ------------------------------------------------

            if pathway_field and pathway_field != "-":

                for pathway in re.split(
                    r"[|;]",
                    pathway_field
                ):

                    pathway = pathway.strip()

                    if pathway:
                        pathways[
                            protein
                        ].add(
                            pathway
                        )

            # ------------------------------------------------
            # INTERPRO
            # ------------------------------------------------

            if (

                ipr

                and ipr != "-"

                and ipr.startswith("IPR")

            ):

                ipr_rows += 1

                interpro_ids[
                    protein
                ].add(
                    ipr
                )

                if (

                    ipr_description

                    and ipr_description != "-"

                ):

                    interpro_descriptions[
                        protein
                    ].add(
                        ipr_description
                    )

                # ------------------------------------------------
                # INTERPRO -> GO
                # ------------------------------------------------

                go_ids = interpro2go.get(
                    ipr,
                    set()
                )

                for go_id in go_ids:

                    go_rows += 1

                    protein_go[
                        protein
                    ][
                        go_category(
                            go_terms.get(
                                go_id,
                                {}
                            ).get(
                                "namespace",
                                ""
                            )
                        )
                    ].add(
                        go_id
                    )

                    info = go_terms.get(
                        go_id,
                        {}
                    )

                    category = go_category(
                        info.get(
                            "namespace",
                            ""
                        )
                    )

                    annotation_rows.append([
                        protein,
                        ipr,
                        go_id,
                        info.get(
                            "name",
                            ""
                        ),
                        category,
                        "InterPro2GO",
                        "IEA"
                    ])

    # ========================================================
    # ADD DIRECT INTERPROSCAN GO
    # ========================================================

    for protein in go_direct_ids:

        for go_id in go_direct_ids[
            protein
        ]:

            if go_id not in go_terms:
                continue

            info = go_terms[
                go_id
            ]

            category = go_category(
                info.get(
                    "namespace",
                    ""
                )
            )

            protein_go[
                protein
            ][
                category
            ].add(
                go_id
            )

    # ========================================================
    # ENSURE EVERY PROTEIN EXISTS
    # ========================================================

    for protein in proteins_seen:

        protein_go[
            protein
        ]

    # ========================================================
    # INTERPRO SUMMARY ROWS
    # ========================================================

    interpro_summary_rows = []

    for protein in sorted(
        proteins_seen
    ):

        interpro_summary_rows.append([

            protein,

            "; ".join(
                sorted(
                    interpro_ids.get(
                        protein,
                        set()
                    )
                )
            ) or "-",

            "; ".join(
                sorted(
                    interpro_descriptions.get(
                        protein,
                        set()
                    )
                )
            ) or "-",

            "; ".join(
                sorted(
                    pfam_ids.get(
                        protein,
                        set()
                    )
                )
            ) or "-",

            "; ".join(
                sorted(
                    go_direct_ids.get(
                        protein,
                        set()
                    )
                )
            ) or "-",

            "; ".join(
                sorted(
                    pathways.get(
                        protein,
                        set()
                    )
                )
            ) or "-",

            "; ".join(
                sorted(
                    analysis_sources.get(
                        protein,
                        set()
                    )
                )
            ) or "-"

        ])

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print()

    print(
        "InterProScan processing complete."
    )

    print(
        f"Rows read             : {total_rows:,}"
    )

    print(
        f"InterPro rows         : {ipr_rows:,}"
    )

    print(
        f"GO rows               : {go_rows:,}"
    )

    print(
        f"Proteins seen         : {len(proteins_seen):,}"
    )

    print(
        "Proteins with InterPro: "
        f"{sum(bool(v) for v in interpro_ids.values()):,}"
    )

    print(
        "Proteins with Pfam    : "
        f"{sum(bool(v) for v in pfam_ids.values()):,}"
    )

    print(
        f"InterPro summary rows : {len(interpro_summary_rows):,}"
    )

    # ========================================================
    # RETURN
    # ========================================================

    return (

        protein_go,

        annotation_rows,

        interpro_ids,

        interpro_descriptions,

        pfam_ids,

        analysis_sources,

        proteins_seen,

        interpro_summary_rows

    )
