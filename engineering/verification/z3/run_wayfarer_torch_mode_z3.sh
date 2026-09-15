#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
command -v z3 >/dev/null 2>&1 || { echo 'Z3 NOT FOUND'; exit 2; }

run_expect() {
  local file="$1" expected="$2"
  local out first
  out="$(z3 "$file")"
  # Do not pipe a potentially large model through head under pipefail: printf can
  # receive SIGPIPE and terminate an otherwise successful qualification.
  first="${out%%$'\n'*}"
  printf '%-58s expected=%-5s got=%s\n' "$file" "$expected" "$first"
  [[ "$first" == "$expected" ]] || { printf '%s\n' "$out"; exit 1; }
}

run_expect wayfarer_torch_mode_envelope_v0.1.smt2 sat
run_expect wayfarer_torch_mode_synthesis_v0.1.smt2 sat
run_expect wayfarer_torch_mode_negative_power_v0.1.smt2 unsat
run_expect wayfarer_torch_mode_negative_zero_remass_active_v0.1.smt2 sat

echo 'LOOM_Z3_WAYFARER_TORCH_MODE_STATUS=PASS'
