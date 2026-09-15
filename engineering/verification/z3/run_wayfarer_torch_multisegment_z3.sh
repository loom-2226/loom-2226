#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
command -v z3 >/dev/null 2>&1 || { echo 'Z3 NOT FOUND'; exit 2; }

run() {
  local f="$1" expected="$2" out first
  out="$(cd "$HERE" && z3 "$f")"
  first="${out%%$'\n'*}"
  printf '%-64s expected=%-5s got=%s\n' "$f" "$expected" "$first" >&2
  [[ "$first" == "$expected" ]] || { printf '%s\n' "$out"; exit 1; }
  printf '%s\n' "$out"
}

plan="$(run wayfarer_torch_multisegment_synthesis_v0.1.smt2 sat)"
# Segment 1 and 3 constraints uniquely require FAST under the earned cards.
count_fast="$(printf '%s\n' "$plan" | grep -c 'FAST' || true)"
[[ "$count_fast" -ge 2 ]] || { echo 'EXPECTED HIGH-THRUST END SEGMENTS TO SYNTHESIZE FAST'; printf '%s\n' "$plan"; exit 1; }

hostile="$(run wayfarer_torch_multisegment_negative_v0.1.smt2 unsat)"
[[ "$hostile" == *"H_LIMIT_MODE"* ]] || { echo 'EXPECTED LIMIT IN UNSAT CORE'; exit 1; }
[[ "$hostile" == *"H_REQUIRE_200_T_RESERVE"* ]] || { echo 'EXPECTED RESERVE REQUIREMENT IN UNSAT CORE'; exit 1; }

printf '%s\n' "$plan"
printf '%s\n' "$hostile"
echo 'LOOM_Z3_WAYFARER_TORCH_MULTISEGMENT_STATUS=PASS'
