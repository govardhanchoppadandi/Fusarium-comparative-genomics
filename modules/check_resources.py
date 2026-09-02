#!/usr/bin/env python3

import os
import shutil
import yaml


def load_config(config_file):

    with open(
        config_file,
        "r",
        encoding="utf-8"
    ) as f:

        return yaml.safe_load(f)


def check_file(path, name):

    if path and os.path.isfile(path):

        size = (
            os.path.getsize(path)
            /
            (1024 * 1024)
        )

        print(
            f"[OK] {name}: "
            f"{path} "
            f"({size:.1f} MB)"
        )

        return True

    print(
        f"[MISSING] {name}: {path}"
    )

    return False


def check_directory(path, name):

    if path and os.path.isdir(path):

        print(
            f"[OK] {name}: {path}"
        )

        return True

    print(
        f"[MISSING] {name}: {path}"
    )

    return False


def check_executable(name):

    executable = shutil.which(
        name
    )

    if executable:

        print(
            f"[OK] {name}: {executable}"
        )

        return True

    print(
        f"[MISSING] {name}"
    )

    return False


def check_resources(config_file):

    config = load_config(
        config_file
    )

    resources = config["resources"]

    blast_config = config.get(
        "blast",
        {}
    )

    print()
    print("=" * 70)
    print(
        "FUNCTIONAL ANNOTATION — RESOURCE CHECK"
    )
    print("=" * 70)

    status = True

    # --------------------------------------------------------
    # GO RESOURCES
    # --------------------------------------------------------

    status &= check_file(
        resources["go_obo"],
        "GO ontology"
    )

    status &= check_file(
        resources["goslim_obo"],
        "GO-Slim ontology"
    )

    status &= check_file(
        resources["interpro2go"],
        "InterPro2GO"
    )

    # --------------------------------------------------------
    # INTERPROSCAN DATA
    # --------------------------------------------------------

    interpro = config.get(
        "interproscan",
        {}
    )

    if interpro.get(
        "datadir"
    ):

        status &= check_directory(
            interpro["datadir"],
            "InterProScan database"
        )

    # --------------------------------------------------------
    # EXISTING INTERPRO RESULT
    # --------------------------------------------------------

    if interpro.get(
        "reuse_existing",
        True
    ):

        status &= check_file(
            interpro.get(
                "existing_result",
                ""
            ),
            "Existing InterProScan result"
        )

    # --------------------------------------------------------
    # BLAST
    # --------------------------------------------------------

    if blast_config.get(
        "enabled",
        False
    ):

        status &= check_executable(
            "blastp"
        )

        database = blast_config.get(
            "database",
            ""
        )

        if database:

            if (
                os.path.exists(
                    database + ".pin"
                )
                or
                os.path.exists(
                    database + ".psq"
                )
                or
                os.path.exists(
                    database + ".phr"
                )
            ):

                print(
                    f"[OK] BLAST database: "
                    f"{database}"
                )

            else:

                print(
                    f"[MISSING] BLAST database: "
                    f"{database}"
                )

                status = False

    print("=" * 70)

    if status:

        print(
            "ALL REQUIRED RESOURCES ARE AVAILABLE."
        )

    else:

        print(
            "ONE OR MORE REQUIRED RESOURCES ARE MISSING."
        )

    print("=" * 70)

    return status


if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:

        print(
            "Usage: python3 "
            "modules/check_resources.py "
            "config/config.yaml"
        )

        sys.exit(1)

    check_resources(
        sys.argv[1]
    )
