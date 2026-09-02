#!/usr/bin/env python3

import sys
import shutil
import subprocess

from pathlib import Path
from datetime import datetime

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
    )
)

import yaml

from modules.fasta_qc import (
    validate_fasta
)

from modules.check_resources import (
    check_resources
)

from modules.blast_annotation import (
    run_blast,
    load_blast_results,
    best_blast_hits
)

from modules.go_annotation import (
    load_interpro2go,
    load_go_ontology,
    process_interpro_tsv
)

from modules.goslim import (
    load_go_relationships,
    load_slim_terms,
    build_slim_mapping
)

from modules.excel_output import (
    create_excel
)


# ============================================================
# CONFIG
# ============================================================

def load_config(config_path=None):

    if config_path is None:

        config_file = (
            Path(__file__).resolve().parents[1]
            / "config"
            / "config.yaml"
        )

    else:

        config_file = Path(config_path).resolve()

    if not config_file.is_file():

        raise FileNotFoundError(
            f"Configuration file not found: {config_file}"
        )

    with open(
        config_file,
        "r",
        encoding="utf-8"
    ) as f:

        return yaml.safe_load(f)


# ============================================================
# APPLICATION IDENTITY
# ============================================================

APP_NAME = "ARI WHEAT PATHOLOGY FUNCTIONAL ANNOTATION SUITE"
APP_INSTITUTE = "Agharkar Research Institute, Pune"
APP_LAB = "Wheat Pathology Laboratory"
APP_DESCRIPTION = "Functional annotation of fungal protein sequences"
APP_DEVELOPERS = [
    "Dr. Sudhir Navathe",
    "Govardhan Choppadandi",
]
APP_CITATION = "To be updated after publication."


def print_application_identity():
    print("=" * 70)
    print(APP_NAME)
    print("=" * 70)
    print()
    print(APP_INSTITUTE)
    print(APP_LAB)
    print()
    print(APP_DESCRIPTION)
    print()
    print("Developed by:")
    for developer in APP_DEVELOPERS:
        print(developer)
    print()
    print("Citation:")
    print(APP_CITATION)
    print("=" * 70)


# ============================================================
# INTERPROSCAN
# ============================================================

def run_interproscan(
    input_fasta,
    output_directory,
    config
):

    output_directory = Path(
        output_directory
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    repository = config.get(
        "repository",
        "https://github.com/ebi-pf-team/interproscan6"
    )

    datadir = config[
        "datadir"
    ]

    cpus = int(
        config.get(
            "cpus",
            4
        )
    )

    max_workers = int(
        config.get(
            "max_workers",
            cpus
        )
    )

    profile = config.get(
        "profile",
        "docker"
    )

    command = [

        "nextflow",

        "run",

        repository,

        "-profile",
        profile,

        "--datadir",
        datadir,

        "--input",
        str(input_fasta),

        "--outdir",
        str(output_directory),

        "--formats",
        config.get(
            "formats",
            "tsv"
        ),

    ]

    if config.get(
        "goterms",
        True
    ):

        command.append(
            "--goterms"
        )

    if config.get(
        "pathways",
        True
    ):

        command.append(
            "--pathways"
        )

    command.extend([

        "--cpus",
        str(cpus),

        "--max-workers",
        str(max_workers)

    ])

    if config.get(
        "resume",
        True
    ):

        command.append(
            "-resume"
        )

    print()
    print("=" * 70)
    print("RUNNING INTERPROSCAN 6")
    print("=" * 70)

    print(
        "Command:"
    )

    print(
        " ".join(command)
    )

    print()

    result = subprocess.run(
        command,
        check=False
    )

    if result.returncode != 0:

        raise RuntimeError(
            "InterProScan failed with exit code "
            f"{result.returncode}"
        )

    # --------------------------------------------------------
    # FIND TSV
    # --------------------------------------------------------

    expected = (

        output_directory

        / (
            Path(
                input_fasta
            ).name

            + ".tsv"
        )

    )

    if expected.is_file():

        return expected

    candidates = sorted(

        output_directory.rglob(
            "*.tsv"
        ),

        key=lambda p: p.stat().st_mtime,

        reverse=True

    )

    if not candidates:

        raise FileNotFoundError(
            "InterProScan completed but no TSV "
            "result was found in: "
            f"{output_directory}"
        )

    return candidates[0]


# ============================================================
# GET EXISTING INTERPRO
# ============================================================

def get_interpro_result(
    input_fasta,
    interpro_config,
    interpro_dir,
    settings
):

    enabled = interpro_config.get(
        "enabled",
        True
    )

    if not enabled:

        raise RuntimeError(
            "InterProScan is disabled."
        )

    reuse = interpro_config.get(
        "reuse_existing",
        False
    )

    # --------------------------------------------------------
    # REUSE EXISTING RESULT
    # --------------------------------------------------------

    if reuse:

        existing = interpro_config.get(
            "existing_result",
            ""
        )

        if not existing:

            raise ValueError(
                "reuse_existing=true but "
                "existing_result is empty."
            )

        source = Path(
            existing
        )

        if not source.is_file():

            raise FileNotFoundError(
                "Existing InterProScan result not found: "
                f"{source}"
            )

        print()
        print(
            "Using completed InterProScan result:"
        )

        print(
            source
        )

        destination = (

            interpro_dir

            / source.name

        )

        if (

            not destination.exists()

            or

            destination.stat().st_size
            != source.stat().st_size

        ):

            print(
                "Copying InterProScan result..."
            )

            shutil.copy2(
                source,
                destination
            )

        return destination

    # --------------------------------------------------------
    # RUN NEW INTERPROSCAN
    # --------------------------------------------------------

    run_directory = (

        interpro_dir

        / "interproscan_run"

    )

    result = run_interproscan(

        input_fasta,

        run_directory,

        {

            **interpro_config,

            "cpus": settings.get(
                "cpus",
                4
            ),

            "resume": settings.get(
                "resume",
                True
            )

        }

    )

    return result


# ============================================================
# MAIN
# ============================================================

def main():

    print_application_identity()

    config_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else None
    )

    config = load_config(config_path)

    project = config[
        "project"
    ]

    input_config = config[
        "input"
    ]

    interpro_config = config[
        "interproscan"
    ]

    blast_config = config[
        "blast"
    ]

    resources = config[
        "resources"
    ]

    settings = config[
        "settings"
    ]

    output_config = config[
        "output"
    ]

    project_name = project[
        "name"
    ]

    organism = project[
        "organism"
    ]

    taxon = project[
        "taxon"
    ]

    input_fasta = Path(
        input_config[
            "fasta"
        ]
    )

    output_dir = Path(
        output_config[
            "directory"
        ]
    )

    raw_dir = output_dir / "raw"

    interpro_dir = raw_dir / "interpro"

    blast_dir = raw_dir / "blast"

    go_dir = raw_dir / "go"

    goslim_dir = raw_dir / "go_slim"

    results_dir = output_dir / "results"

    summary_dir = output_dir / "summary"

    log_dir = output_dir / "logs"


    for directory in [

        raw_dir,

        interpro_dir,

        blast_dir,

        go_dir,

        goslim_dir,

        results_dir,

        summary_dir,

        log_dir

    ]:

        directory.mkdir(
            parents=True,
            exist_ok=True
        )


    # ========================================================
    # LOG
    # ========================================================

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    log_file = (

        log_dir

        / f"{project_name}_functional_annotation_{timestamp}.log"

    )

    log_handle = open(
        log_file,
        "w",
        encoding="utf-8"
    )

    original_stdout = sys.stdout

    original_stderr = sys.stderr


    class Tee:

        def __init__(
            self,
            *files
        ):

            self.files = files

        def write(
            self,
            text
        ):

            for f in self.files:

                f.write(
                    text
                )

                f.flush()

        def flush(
            self
        ):

            for f in self.files:

                f.flush()


    sys.stdout = Tee(
        original_stdout,
        log_handle
    )

    sys.stderr = Tee(
        original_stderr,
        log_handle
    )


    try:

        print()
        print("=" * 70)
        print(
            "FUSARIUM FUNCTIONAL ANNOTATION PIPELINE"
        )
        print("=" * 70)

        print(
            f"Project : {project_name}"
        )

        print(
            f"Organism: {organism}"
        )

        print(
            f"Taxon   : {taxon}"
        )

        print(
            f"FASTA   : {input_fasta}"
        )

        print(
            f"Output  : {output_dir}"
        )

        print(
            f"Started : {datetime.now()}"
        )

        print("=" * 70)


        # ====================================================
        # INPUT
        # ====================================================

        if not input_fasta.is_file():

            raise FileNotFoundError(
                "Input FASTA not found: "
                f"{input_fasta}"
            )


        # ====================================================
        # COPY FASTA
        # ====================================================

        if settings.get(
            "copy_input_fasta",
            True
        ):

            copied_fasta = (

                raw_dir

                / input_fasta.name

            )

            if (

                not copied_fasta.exists()

                or

                copied_fasta.stat().st_size
                != input_fasta.stat().st_size

            ):

                shutil.copy2(
                    input_fasta,
                    copied_fasta
                )

            print()
            print(
                "Input FASTA copied:"
            )
            print(
                copied_fasta
            )


        # ====================================================
        # STEP 1 — RESOURCE CHECK
        # ====================================================

        print()
        print(
            "STEP 1 — RESOURCE CHECK"
        )

        check_resources(
            str(
                Path(__file__).resolve().parents[1]
                / "config"
                / "config.yaml"
            )
        )


        # ====================================================
        # STEP 2 — FASTA QC
        # ====================================================

        print()
        print(
            "STEP 2 — FASTA VALIDATION"
        )

        qc = validate_fasta(
            str(input_fasta)
        )

        print(
            f"Proteins: {qc['proteins']:,}"
        )


        # ====================================================
        # STEP 3 — BLASTP
        # ====================================================

        blast_rows = []

        blast_results = []

        if blast_config.get(
            "enabled",
            False
        ):

            print()
            print(
                "STEP 3 — BLASTP against "
                f"{blast_config['database_name']}"
            )

            blast_output = (

                blast_dir

                / output_config.get(
                    "blast_file",
                    "BLAST_SwissProt.tsv"
                )

            )

            run_blast(

                str(input_fasta),

                blast_config[
                    "database"
                ],

                str(blast_output),

                threads=settings.get(
                    "cpus",
                    4
                ),

                evalue=blast_config.get(
                    "evalue",
                    1e-5
                ),

                max_target_seqs=blast_config.get(
                    "max_target_seqs",
                    5
                )

            )

            blast_results = load_blast_results(
                str(blast_output)
            )

            best_hits = best_blast_hits(
                blast_results
            )

            for protein, row in sorted(
                best_hits.items()
            ):

                classification = (

                    "Annotated"

                    if row["evalue"]
                    <= blast_config.get(
                        "evalue",
                        1e-5
                    )

                    else

                    "Weak/Uncertain"

                )

                blast_rows.append([

                    protein,

                    row["sacc"],

                    row["stitle"],

                    row["pident"],

                    row["length"],

                    row["qlen"],

                    row["qstart"],

                    row["qend"],

                    row["evalue"],

                    row["bitscore"],

                    row["qcovs"],

                    classification

                ])

            print(
                f"BLAST rows loaded: "
                f"{len(blast_results):,}"
            )

            print(
                f"Best BLAST hits: "
                f"{len(blast_rows):,}"
            )

        else:

            print()
            print(
                "STEP 3 — BLAST disabled"
            )


        # ====================================================
        # STEP 4 — INTERPROSCAN
        # ====================================================

        print()
        print(
            "STEP 4 — INTERPROSCAN 6"
        )

        interpro_tsv = get_interpro_result(

            input_fasta,

            interpro_config,

            interpro_dir,

            settings

        )

        print()
        print(
            "InterProScan TSV:"
        )

        print(
            interpro_tsv
        )


        # ====================================================
        # STEP 5 — INTERPRO → GO
        # ====================================================

        print()
        print(
            "STEP 5 — INTERPRO → GO"
        )

        interpro2go = load_interpro2go(

            resources[
                "interpro2go"
            ]

        )

        go_terms = load_go_ontology(

            resources[
                "go_obo"
            ]

        )

        (

            protein_go,

            annotation_rows,

            interpro_ids,

            interpro_descriptions,

            pfam_ids,

            analysis_sources,

            proteins_seen,

            interpro_summary_rows

        ) = process_interpro_tsv(

            str(interpro_tsv),

            interpro2go,

            go_terms,

            str(input_fasta)

        )


        # ====================================================
        # STEP 6 — GO-SLIM
        # ====================================================

        print()
        print(
            "STEP 6 — GO-Slim"
        )

        parents = load_go_relationships(

            resources[
                "go_obo"
            ]

        )

        slim_terms = load_slim_terms(

            resources[
                "goslim_obo"
            ]

        )

        slim_mapping = build_slim_mapping(

            go_terms,

            parents,

            slim_terms

        )

        slim_rows = []

        for protein in sorted(
            protein_go
        ):

            categories = protein_go[
                protein
            ]

            for category in categories:

                for go_id in categories[
                    category
                ]:

                    for slim_id in slim_mapping.get(

                        go_id,

                        set()

                    ):

                        slim_info = go_terms.get(

                            slim_id,

                            {}

                        )

                        slim_rows.append([

                            protein,

                            go_id,

                            slim_id,

                            slim_info.get(
                                "name",
                                ""
                            ),

                            category

                        ])


        print(
            f"GO-Slim rows: "
            f"{len(slim_rows):,}"
        )


        # ====================================================
        # BUILD PROTEIN-LEVEL GO-SLIM
        # ====================================================

        protein_slim = {}

        for row in slim_rows:

            protein = row[0]

            go_id = row[1]

            slim_id = row[2]

            category = row[4]

            protein_slim.setdefault(
                protein,
                {}
            )

            protein_slim[
                protein
            ].setdefault(
                category,
                set()
            )

            protein_slim[
                protein
            ][category].add(
                slim_id
            )


        # ====================================================
        # STEP 7 — RAW GO
        # ====================================================

        go_raw_file = (

            go_dir

            / "GO_annotations.tsv"

        )

        with open(

            go_raw_file,

            "w",

            encoding="utf-8"

        ) as f:

            f.write(

                "Protein\tInterPro_ID\tGO_ID\t"
                "GO_Name\tGO_Category\t"
                "Source\tEvidence\n"

            )

            for row in annotation_rows:

                f.write(

                    "\t".join(
                        str(x)
                        for x in row
                    )

                    + "\n"

                )


        # ====================================================
        # STEP 8 — RAW GO-SLIM
        # ====================================================

        goslim_raw_file = (

            goslim_dir

            / "GO_Slim_annotations.tsv"

        )

        with open(

            goslim_raw_file,

            "w",

            encoding="utf-8"

        ) as f:

            f.write(

                "Protein\tGO_ID\tGO_Slim_ID\t"
                "GO_Slim_Name\tGO_Slim_Category\n"

            )

            for row in slim_rows:

                f.write(

                    "\t".join(
                        str(x)
                        for x in row
                    )

                    + "\n"

                )


        # ====================================================
        # STEP 9 — INTERPRO RAW SUMMARY
        # ====================================================

        interpro_raw_file = (

            interpro_dir

            / "InterPro_summary.tsv"

        )

        with open(

            interpro_raw_file,

            "w",

            encoding="utf-8"

        ) as f:

            f.write(

                "Protein\tInterPro_ID\t"
                "InterPro_Description\tPfam\t"
                "GO_Terms\tPathways\tAnalysis\n"

            )

            for row in interpro_summary_rows:

                f.write(

                    "\t".join(
                        str(x)
                        for x in row
                    )

                    + "\n"

                )


        # ====================================================
        # STEP 10 — SUMMARY
        # ====================================================

        summary_file = (

            summary_dir

            / "pipeline_summary.tsv"

        )

        with open(

            summary_file,

            "w",

            encoding="utf-8"

        ) as f:

            f.write(
                "Metric\tValue\n"
            )

            f.write(
                f"Project\t{project_name}\n"
            )

            f.write(
                f"Organism\t{organism}\n"
            )

            f.write(
                f"Taxon\t{taxon}\n"
            )

            f.write(
                f"Input proteins\t"
                f"{qc['proteins']}\n"
            )

            f.write(
                f"BLAST best hits\t"
                f"{len(blast_rows)}\n"
            )

            f.write(
                f"InterPro proteins\t"
                f"{sum(bool(v) for v in interpro_ids.values())}\n"
            )

            f.write(
                f"InterPro summary rows\t"
                f"{len(interpro_summary_rows)}\n"
            )

            f.write(
                f"GO annotation rows\t"
                f"{len(annotation_rows)}\n"
            )

            f.write(
                f"GO-Slim rows\t"
                f"{len(slim_rows)}\n"
            )


        # ====================================================
        # STEP 11 — EXCEL
        # ====================================================

        print()
        print(
            "STEP 11 — CREATING EXCEL"
        )

        output_excel = (

            results_dir

            / output_config.get(

                "excel_file",

                "Fusarium_Protein_Annotation.xlsx"

            )

        )

        create_excel(

            str(output_excel),

            protein_go,

            annotation_rows,

            slim_rows,

            interpro_ids,

            go_terms,

            blast_rows,

            interpro_summary_rows,

            protein_slim

        )


        # ====================================================
        # FINAL
        # ====================================================

        print()
        print("=" * 70)
        print(
            "PIPELINE COMPLETED SUCCESSFULLY"
        )
        print("=" * 70)

        print(
            f"Proteins             : "
            f"{qc['proteins']:,}"
        )

        print(
            f"BLAST best hits      : "
            f"{len(blast_rows):,}"
        )

        print(
            f"InterPro proteins    : "
            f"{sum(bool(v) for v in interpro_ids.values()):,}"
        )

        print(
            f"InterPro summary     : "
            f"{len(interpro_summary_rows):,}"
        )

        print(
            f"GO annotations       : "
            f"{len(annotation_rows):,}"
        )

        print(
            f"GO-Slim annotations  : "
            f"{len(slim_rows):,}"
        )

        print()
        print(
            "OUTPUT:"
        )

        print(
            f"Excel: {output_excel}"
        )

        print(
            f"Log  : {log_file}"
        )

        print()
        print(
            "Raw InterPro:"
        )

        print(
            interpro_raw_file
        )

        print(
            "Raw GO:"
        )

        print(
            go_raw_file
        )

        print(
            "Raw GO-Slim:"
        )

        print(
            goslim_raw_file
        )

        print("=" * 70)


    except Exception as e:

        print()
        print("=" * 70)
        print(
            "PIPELINE FAILED"
        )
        print("=" * 70)

        print(
            f"{type(e).__name__}: {e}"
        )

        raise


    finally:

        sys.stdout = original_stdout

        sys.stderr = original_stderr

        log_handle.close()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
