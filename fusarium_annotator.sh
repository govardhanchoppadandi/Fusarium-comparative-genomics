#!/usr/bin/env bash

set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="${APP_DIR}/config/config.yaml"
LOCAL_RESOURCES="${APP_DIR}/config/resources.local.yaml"
RUNTIME_CONFIG="${APP_DIR}/config/.runtime_config.yaml"
PYTHON="${APP_DIR}/.venv/bin/python"

echo
echo "======================================================================"
echo "        ARI WHEAT PATHOLOGY FUNCTIONAL ANNOTATION SUITE"
echo "======================================================================"
echo
echo "        Agharkar Research Institute, Pune"
echo "        Wheat Pathology Laboratory"
echo
echo "        Functional annotation of fungal protein sequences"
echo
echo "        Developed by:"
echo "        Dr. Sudhir Navathe"
echo "        Govardhan Choppadandi"
echo
echo "        Citation:"
echo "        To be updated after publication."
echo
echo "======================================================================"
echo

# ----------------------------------------------------------------------
# Check application environment
# ----------------------------------------------------------------------

if [[ ! -x "$PYTHON" ]]; then
    echo "[ERROR] Application environment is not installed."
    echo
    echo "Please run:"
    echo
    echo "    ./install.sh"
    echo
    exit 1
fi

# ----------------------------------------------------------------------
# Check local resource configuration
# ----------------------------------------------------------------------

if [[ ! -f "$LOCAL_RESOURCES" ]]; then
    echo "[ERROR] Local resource configuration not found:"
    echo "        $LOCAL_RESOURCES"
    echo
    echo "Create it from:"
    echo
    echo "    cp config/resources.local.example.yaml config/resources.local.yaml"
    echo
    echo "Then edit the paths for:"
    echo "    - GO ontology"
    echo "    - GO-Slim ontology"
    echo "    - InterPro2GO"
    echo "    - InterProScan database"
    echo "    - Swiss-Prot BLAST database"
    echo
    exit 1
fi

# ----------------------------------------------------------------------
# FASTA input
# ----------------------------------------------------------------------

if [[ $# -ge 1 ]]; then
    FASTA="$1"
else
    read -r -p "Protein FASTA path: " FASTA
fi

if [[ -z "${FASTA:-}" ]]; then
    echo "[ERROR] FASTA path cannot be empty."
    exit 1
fi

FASTA="${FASTA/#\~/$HOME}"

if [[ ! -f "$FASTA" ]]; then
    echo
    echo "[ERROR] FASTA file not found:"
    echo "        $FASTA"
    echo
    exit 1
fi

# ----------------------------------------------------------------------
# Optional metadata
# ----------------------------------------------------------------------

PROJECT="${2:-Fusarium}"
ORGANISM="${3:-Fusarium}"
TAXON="${4:-Fungi}"
OUTPUT="${5:-${APP_DIR}/results/${PROJECT}}"

PROJECT="${PROJECT:-Fusarium}"
ORGANISM="${ORGANISM:-Fusarium}"
TAXON="${TAXON:-Fungi}"

OUTPUT="${OUTPUT/#\~/$HOME}"

# ----------------------------------------------------------------------
# Prepare temporary runtime configuration
# ----------------------------------------------------------------------

"$PYTHON" - "$CONFIG" "$LOCAL_RESOURCES" "$RUNTIME_CONFIG" \
    "$FASTA" "$PROJECT" "$ORGANISM" "$TAXON" "$OUTPUT" <<'PY'

import sys
from pathlib import Path
import yaml

base_config = Path(sys.argv[1])
local_resources = Path(sys.argv[2])
runtime_config = Path(sys.argv[3])

fasta = Path(sys.argv[4]).resolve()
project = sys.argv[5]
organism = sys.argv[6]
taxon = sys.argv[7]
output = Path(sys.argv[8]).resolve()

# ------------------------------------------------------------
# Load base configuration
# ------------------------------------------------------------

with open(base_config, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

if config is None:
    config = {}

# ------------------------------------------------------------
# Load local resources
# ------------------------------------------------------------

with open(local_resources, "r", encoding="utf-8") as f:
    local = yaml.safe_load(f)

if local is None:
    local = {}

local_resource_block = local.get("resources", {})

if not local_resource_block:
    raise SystemExit(
        "ERROR: No resources were defined in resources.local.yaml"
    )

config.setdefault("resources", {})

for key, value in local_resource_block.items():
    if value:
        config["resources"][key] = value

# ------------------------------------------------------------
# Project metadata
# ------------------------------------------------------------

config.setdefault("project", {})

config["project"]["name"] = project
config["project"]["organism"] = organism
config["project"]["taxon"] = taxon

# ------------------------------------------------------------
# FASTA
# ------------------------------------------------------------

config.setdefault("input", {})
config["input"]["fasta"] = str(fasta)

# ------------------------------------------------------------
# Output
# ------------------------------------------------------------

config.setdefault("output", {})
config["output"]["directory"] = str(output)

# ------------------------------------------------------------
# InterProScan
# ------------------------------------------------------------

config.setdefault("interproscan", {})

config["interproscan"]["enabled"] = True
config["interproscan"]["reuse_existing"] = False
config["interproscan"]["existing_result"] = ""

# Use local InterProScan database path
if "interproscan_datadir" in config["resources"]:
    config["interproscan"]["datadir"] = config["resources"][
        "interproscan_datadir"
    ]

# ------------------------------------------------------------
# BLAST
# ------------------------------------------------------------

config.setdefault("blast", {})

config["blast"]["enabled"] = True

if "blast_database" in config["resources"]:
    config["blast"]["database"] = config["resources"][
        "blast_database"
    ]

# ------------------------------------------------------------
# Settings
# ------------------------------------------------------------

config.setdefault("settings", {})

config["settings"]["create_excel"] = True
config["settings"]["copy_input_fasta"] = True

# ------------------------------------------------------------
# Write temporary runtime configuration
# ------------------------------------------------------------

with open(runtime_config, "w", encoding="utf-8") as f:
    yaml.safe_dump(
        config,
        f,
        sort_keys=False,
        default_flow_style=False
    )

print("Configuration prepared successfully.")

PY

# ----------------------------------------------------------------------
# Start analysis
# ----------------------------------------------------------------------

echo
echo "======================================================================"
echo "STARTING ARI WHEAT PATHOLOGY FUNCTIONAL ANNOTATION SUITE"
echo "======================================================================"
echo
echo "FASTA    : $FASTA"
echo "Project  : $PROJECT"
echo "Organism : $ORGANISM"
echo "Taxon    : $TAXON"
echo "Output   : $OUTPUT"
echo
echo "Pipeline:"
echo "  FASTA QC"
echo "  BLASTP → UniProtKB/Swiss-Prot"
echo "  InterProScan 6"
echo "  InterPro → GO"
echo "  GO-Slim"
echo "  Excel report"
echo "  Raw results"
echo "  Analysis log"
echo
echo "======================================================================"
echo

cd "$APP_DIR"

"$PYTHON" app/pipeline.py "$RUNTIME_CONFIG"

STATUS=$?

rm -f "$RUNTIME_CONFIG"

exit "$STATUS"
