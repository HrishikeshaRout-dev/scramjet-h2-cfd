#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
    echo "Usage: import_openfoam_mesh.sh CASE_DIRECTORY MESH_FILE" >&2
    exit 2
fi

case_dir="$(cd -- "$1" && pwd)"
mesh_file="$(realpath "$2")"

export WM_PROJECT_DIR=/usr/share/openfoam
export WM_PROJECT_VERSION=v1912
export FOAM_CONFIG_MODE=o
export FOAM_CONFIG_ETC=/usr/share/openfoam/etc

if [[ ! -f "$mesh_file" ]]; then
    echo "Mesh file not found: $mesh_file" >&2
    exit 1
fi
if [[ -e "$case_dir/constant/polyMesh" ]]; then
    echo "Refusing to overwrite an existing mesh in $case_dir." >&2
    echo "Use a fresh case directory to preserve saved results." >&2
    exit 2
fi

gmshToFoam -case "$case_dir" "$mesh_file"

python3 - "$case_dir/constant/polyMesh/boundary" <<'PY'
from pathlib import Path
import re
import sys

boundary_file = Path(sys.argv[1])
text = boundary_file.read_text()
pattern = (
    r"(?ms)(^\s*frontAndBack\s*\{\s*type\s+)"
    r"(?:patch|empty);(\s*physicalType\s+)(?:patch|empty);"
)
text, count = re.subn(pattern, r"\1empty;\2empty;", text, count=1)
if count != 1:
    raise SystemExit("Expected exactly one frontAndBack patch to convert to empty.")
boundary_file.write_text(text)
PY

cd "$case_dir"
check_log="$(mktemp)"
trap 'rm -f "$check_log"' EXIT
if ! checkMesh -allTopology -allGeometry 2>&1 | tee "$check_log"; then
    echo "checkMesh could not complete successfully." >&2
    exit 1
fi
if grep -Eq '^Failed [1-9][0-9]* mesh checks\.' "$check_log"; then
    echo "checkMesh reported failed quality checks; do not use this mesh quantitatively yet." >&2
    exit 2
fi
if ! grep -Fxq 'Mesh OK.' "$check_log"; then
    echo "checkMesh did not report a clean mesh." >&2
    exit 2
fi
