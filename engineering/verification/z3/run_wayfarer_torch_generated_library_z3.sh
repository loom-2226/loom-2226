#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
command -v z3 >/dev/null 2>&1 || { echo 'Z3 NOT FOUND'; exit 2; }
out="$(cd "$HERE" && z3 wayfarer_torch_generated_library_selftest_v0.1.smt2 2>&1)"
rc=$?
printf '%s\n' "$out"
[[ "$rc" -eq 0 ]] || { echo "Z3_EXIT_CODE=$rc"; exit "$rc"; }
first="${out%%$'\n'*}"
[[ "$first" == sat ]] || { echo "EXPECTED=sat GOT=$first"; exit 1; }
echo 'LOOM_Z3_WAYFARER_TORCH_GENERATED_LIBRARY_STATUS=PASS'
