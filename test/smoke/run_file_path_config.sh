#!/usr/bin/env bash
# Smoke test: run the ivory CLI end-to-end against a config loaded from a
# filesystem path that lives outside the ivory package/repo tree.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/../.." && pwd)"

# The smoke config below reuses the repo's `test.plugin.simple_plugin` test
# fixture, which is only importable with the repo root on PYTHONPATH (it is
# not part of the installed `ivory` distribution). See docs/configuration.md
# for why file-based configs still load through Python's module machinery.
export PYTHONPATH="${repo_root}${PYTHONPATH:+:${PYTHONPATH}}"

temp_dir="$(mktemp -d)"
trap 'rm -rf "${temp_dir}"' EXIT

config_path="${temp_dir}/standalone_config.py"
cat > "${config_path}" <<'EOF'
from ivory.utils.config_section import ConfigSection

Pipeline = ConfigSection(plugins=["test.plugin.simple_plugin"])
SimplePlugin = ConfigSection(value="hello from a file-path config")
EOF

echo "Running: uv run ivory ${config_path}"
cd "${repo_root}"
uv run ivory "${config_path}"

echo "OK: file-path config ran successfully"
