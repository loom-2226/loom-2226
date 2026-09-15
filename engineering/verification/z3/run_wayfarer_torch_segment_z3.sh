#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
command -v z3 >/dev/null 2>&1 || { echo 'Z3 NOT FOUND'; exit 2; }

run_capture() {
  local file="$1" expected="$2" out first rc
  set +e
  out="$(cd "$HERE" && z3 "$file" 2>&1)"; rc=$?
  set -e
  [[ $rc -eq 0 ]] || { printf '%s\n' "$out"; exit "$rc"; }
  first="${out%%$'\n'*}"
  printf '%-62s expected=%-5s got=%s\n' "$file" "$expected" "$first" >&2
  [[ "$first" == "$expected" ]] || { printf '%s\n' "$out"; exit 1; }
  printf '%s\n' "$out"
}

synth="$(run_capture wayfarer_torch_segment_synthesis_v0.1.smt2 sat)"
# Current envelope makes FAST the unique card satisfying >=30 MN and <=12 TW.
[[ "$synth" == *"FAST"* ]] || { echo 'EXPECTED SYNTHESIS MODEL TO SELECT FAST'; printf '%s\n' "$synth"; exit 1; }

hostile="$(run_capture wayfarer_torch_segment_negative_empty_limit_v0.1.smt2 unsat)"
[[ "$hostile" == *"H_REQUIRE_LIMIT"* ]] || { echo 'EXPECTED UNSAT CORE TO NAME H_REQUIRE_LIMIT'; exit 1; }
[[ "$hostile" == *"H_REQUIRE_POSITIVE_DURATION"* ]] || { echo 'EXPECTED UNSAT CORE TO NAME H_REQUIRE_POSITIVE_DURATION'; exit 1; }
[[ "$hostile" == *"H_REQUIRE_EMPTY_START"* ]] || { echo 'EXPECTED UNSAT CORE TO NAME H_REQUIRE_EMPTY_START'; exit 1; }

printf '%s\n' "$synth"
printf '%s\n' "$hostile"
echo 'LOOM_Z3_WAYFARER_TORCH_SEGMENT_STATUS=PASS'
