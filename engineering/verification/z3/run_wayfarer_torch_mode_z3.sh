#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
command -v z3 >/dev/null 2>&1 || { echo 'Z3 NOT FOUND'; exit 2; }

run_expect() {
  local file="$1" expected="$2"
  local out first
  # Z3 resolves SMT-LIB (include ...) relative to the process working directory,
  # not relative to the including file. Run in the artifact directory so this
  # behaves identically when invoked from the repository root on Termux.
  out="$(cd "$HERE" && z3 "$file")"
  first="${out%%$'\n'*}"
  printf '%-58s expected=%-5s got=%s\n' "$file" "$expected" "$first"
  [[ "$first" == "$expected" ]] || { printf '%s\n' "$out"; exit 1; }
  printf '%s\n' "$out"
}

run_expect wayfarer_torch_mode_baseline_v0.1.smt2 sat >/dev/null
run_expect wayfarer_torch_mode_synthesis_v0.1.smt2 sat
hostile="$(run_expect wayfarer_torch_mode_negative_power_v0.1.smt2 unsat)"
printf '%s\n' "$hostile"
[[ "$hostile" == *"H_REQUIRE_CRUISE"* ]] || { echo 'EXPECTED UNSAT CORE TO NAME H_REQUIRE_CRUISE'; exit 1; }
[[ "$hostile" == *"H_REQUIRE_12_TW"* ]] || { echo 'EXPECTED UNSAT CORE TO NAME H_REQUIRE_12_TW'; exit 1; }
run_expect wayfarer_torch_mode_negative_zero_remass_active_v0.1.smt2 sat >/dev/null

echo 'LOOM_Z3_WAYFARER_TORCH_MODE_STATUS=PASS'
