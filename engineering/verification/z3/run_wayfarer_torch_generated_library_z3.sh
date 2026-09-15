#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
command -v z3 >/dev/null 2>&1 || { echo 'Z3 NOT FOUND'; exit 2; }
out="$(cd "$HERE" && z3 wayfarer_torch_generated_library_selftest_v0.1.smt2 2>&1)"
first="${out%%$'\n'*}"
[[ "$first" == sat ]] || { printf '%s\n' "$out"; exit 1; }
printf '%s\n' "$out"
echo 'LOOM_Z3_WAYFARER_TORCH_GENERATED_LIBRARY_STATUS=PASS'
