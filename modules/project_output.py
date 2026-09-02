#!/usr/bin/env python3

from pathlib import Path


def create_project_structure(output_directory):

    root = Path(output_directory)

    directories = {
        "root": root,
        "raw": root / "raw",
        "interproscan": root / "raw" / "InterProScan",
        "go": root / "GO",
        "go_slim": root / "GO_Slim",
        "results": root / "results",
        "summary": root / "summary",
        "logs": root / "logs"
    }

    for path in directories.values():
        path.mkdir(
            parents=True,
            exist_ok=True
        )

    return directories


def print_project_structure(directories):

    print()
    print("=" * 70)
    print("PROJECT OUTPUT STRUCTURE")
    print("=" * 70)

    for name, path in directories.items():
        print(
            f"{name:20s}: {path}"
        )

    print("=" * 70)
