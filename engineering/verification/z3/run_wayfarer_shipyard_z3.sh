#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
command -v z3 >/dev/null 2>&1 || { echo 'Z3 NOT FOUND'; exit 2; }

run_case() {
  local file="$1" expected="$2" marker="$3" out rc first
  set +e
  out="$(cd "$HERE" && z3 "$file" 2>&1)"
  rc=$?
  set -e
  if [[ $rc -ne 0 ]]; then
    echo "Z3 EXECUTION FAILED: $file rc=$rc"
    printf '%s\n' "$out"
    exit "$rc"
  fi
  first="${out%%$'\n'*}"
  if [[ "$first" != "$expected" ]]; then
    echo "Z3 RESULT MISMATCH: $file expected=$expected got=$first"
    printf '%s\n' "$out"
    exit 1
  fi
  if [[ -n "$marker" ]] && ! grep -q "$marker" <<<"$out"; then
    echo "Z3 OUTPUT MISSING REQUIRED MARKER: $marker"
    printf '%s\n' "$out"
    exit 1
  fi
  printf '%s\n' "$out"
}

run_case wayfarer_shipyard_synthesis_v0.1.smt2 sat DEPLOYED
run_case wayfarer_shipyard_hostile_v0.1.smt2 unsat H_CONFIGURATION_VALID
run_case wayfarer_shipyard_mass_hostile_v0.1.smt2 unsat H_LEDGER_MUST_CLOSE

echo 'LOOM_Z3_WAYFARER_COMPUTATIONAL_SHIPYARD_SLICE1_STATUS=PASS'
