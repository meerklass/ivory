#!/usr/bin/env bash
# Regression smoke test: confirm the ivory CLI still runs a config given as a
# dotted module path (the pre-existing route), unaffected by file-path support.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/../.." && pwd)"

# `tests.config.workflow_config` and `tests.plugin.simple_plugin` are only
# importable with the repo root on PYTHONPATH (see run_file_path_config.sh).
export PYTHONPATH="${repo_root}${PYTHONPATH:+:${PYTHONPATH}}"

cd "${repo_root}"
echo "Running: uv run ivory tests.config.workflow_config"
uv run ivory tests.config.workflow_config

echo "OK: module-path config ran successfully"
