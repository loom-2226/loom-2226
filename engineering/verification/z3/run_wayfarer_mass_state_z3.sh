#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
ROOT="${1:-$(pwd)}"
DIR="$ROOT/engineering/verification/z3"
command -v z3 >/dev/null 2>&1 || { echo 'Z3 RESULT: ERROR'; echo 'z3 executable not found'; exit 2; }
echo "Z3 VERSION: $(z3 --version)"
run_expect() {
  local file="$1" expected="$2" out first
  out="$(z3 "$DIR/$file")"
  first="$(printf '%s\n' "$out" | head -n 1)"
  echo "--- $file"
  printf '%s\n' "$out"
  if [[ "$first" != "$expected" ]]; then
    echo "EXPECTED=$expected ACTUAL=$first"
    exit 1
  fi
}
run_expect wayfarer_mass_state_v0.1.smt2 sat
run_expect wayfarer_mass_state_negative_remass_v0.1.smt2 unsat
run_expect wayfarer_mass_state_negative_mode_v0.1.smt2 unsat
echo 'Z3 CONSTRAINT ENVELOPE: PASS'
