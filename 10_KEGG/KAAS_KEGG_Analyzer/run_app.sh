#!/bin/bash

set -e

source "$HOME/miniconda3/etc/profile.d/conda.sh"

conda activate kaas_env

cd "$(dirname "$0")"

streamlit run app.py
