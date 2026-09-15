#!/usr/bin/env bash
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
cd "$ROOT"
python engineering/verification/z3/generate_wayfarer_torch_formal_library.py >/dev/null || exit $?
git diff --exit-code -- engineering/verification/z3/wayfarer_torch_generated_cards_v0.1.smt2 || exit $?
out="$(cd "$HERE" && z3 wayfarer_torch_generated_synthesis_v0.1.smt2 2>&1)"
rc=$?
printf '%s\n' "$out"
[[ "$rc" -eq 0 ]] || { echo "Z3_EXIT_CODE=$rc"; exit "$rc"; }
first="${out%%$'\n'*}"
[[ "$first" == sat ]] || { echo "EXPECTED=sat GOT=$first"; exit 1; }
count_fast="$(printf '%s\n' "$out" | grep -c 'FAST' || true)"
[[ "$count_fast" -ge 2 ]] || { echo 'EXPECTED GENERATED LIBRARY TO SYNTHESIZE FAST END SEGMENTS'; exit 1; }
echo 'LOOM_Z3_WAYFARER_TORCH_GENERATED_LIBRARY_STATUS=PASS'
