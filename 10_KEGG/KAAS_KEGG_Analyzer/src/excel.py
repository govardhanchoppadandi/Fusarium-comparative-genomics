import pandas as pd


def build_tables(
    kaas_df,
    kegg_cache
):

    # -------------------------------------------------------
    # KO annotation table
    # -------------------------------------------------------

    ko_rows = []

    for ko in sorted(
        kaas_df.loc[
            kaas_df["KO"] != "",
            "KO"
        ].unique()
    ):

        info = kegg_cache.get(
            ko,
            {}
        )

        pathways = info.get(
            "Pathways",
            []
        )


        if not pathways:

            ko_rows.append(
                {
                    "KO": ko,
                    "KO_Name":
                        info.get(
                            "KO_Name",
                            ""
                        ),
                    "EC":
                        info.get(
                            "EC",
                            ""
                        ),
                    "PathwayID": "",
                    "PathwayName": ""
                }
            )

        else:

            for pid, pname in pathways:

                ko_rows.append(
                    {
                        "KO": ko,
                        "KO_Name":
                            info.get(
                                "KO_Name",
                                ""
                            ),
                        "EC":
                            info.get(
                                "EC",
                                ""
                            ),
                        "PathwayID": pid,
                        "PathwayName": pname
                    }
                )


    ko_annotation = pd.DataFrame(
        ko_rows
    )


    # -------------------------------------------------------
    # Protein → KO → pathway
    # -------------------------------------------------------

    protein_pathways = kaas_df.merge(
        ko_annotation,
        on="KO",
        how="left"
    )


    # -------------------------------------------------------
    # KO summary
    # -------------------------------------------------------

    ko_summary = (

        kaas_df[
            kaas_df["KO"] != ""
        ]

        .groupby("KO")

        .agg(
            Protein_Count=(
                "Protein_ID",
                "nunique"
            )
        )

        .reset_index()
    )


    names = (
        ko_annotation[
            [
                "KO",
                "KO_Name"
            ]
        ]
        .drop_duplicates(
            "KO"
        )
    )


    ko_summary = ko_summary.merge(
        names,
        on="KO",
        how="left"
    )


    ko_summary = ko_summary.sort_values(
        "Protein_Count",
        ascending=False
    )


    # -------------------------------------------------------
    # Pathway summary
    # -------------------------------------------------------

    pathway_summary = (

        protein_pathways[
            protein_pathways[
                "PathwayID"
            ].notna()
        ]

        .query(
            "PathwayID != ''"
        )

        .groupby(
            [
                "PathwayID",
                "PathwayName"
            ]
        )

        .agg(
            Protein_Count=(
                "Protein_ID",
                "nunique"
            ),

            KO_Count=(
                "KO",
                "nunique"
            )
        )

        .reset_index()

        .sort_values(
            "Protein_Count",
            ascending=False
        )
    )


    # -------------------------------------------------------
    # Unassigned
    # -------------------------------------------------------

    unassigned = kaas_df[
        kaas_df["KO"] == ""
    ].copy()


    return (
        protein_pathways,
        ko_summary,
        pathway_summary,
        ko_annotation,
        unassigned
    )


def write_excel(
    output_file,
    protein_pathways,
    ko_summary,
    pathway_summary,
    ko_annotation,
    unassigned,
    overall,
    fasta_missing,
    kaas_extra
):

    with pd.ExcelWriter(
        output_file,
        engine="openpyxl"
    ) as writer:

        protein_pathways.to_excel(
            writer,
            sheet_name="Protein_Pathways",
            index=False
        )

        ko_summary.to_excel(
            writer,
            sheet_name="KO_Summary",
            index=False
        )

        pathway_summary.to_excel(
            writer,
            sheet_name="Pathway_Summary",
            index=False
        )

        ko_annotation.to_excel(
            writer,
            sheet_name="KO_Annotations",
            index=False
        )

        unassigned.to_excel(
            writer,
            sheet_name="Unassigned",
            index=False
        )

        overall.to_excel(
            writer,
            sheet_name="Overall_Summary",
            index=False
        )

        fasta_missing.to_excel(
            writer,
            sheet_name="FASTA_Missing",
            index=False
        )

        kaas_extra.to_excel(
            writer,
            sheet_name="KAAS_Extra",
            index=False
        )
