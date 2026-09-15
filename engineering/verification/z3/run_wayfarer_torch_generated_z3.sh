#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
cd "$ROOT"
python engineering/verification/z3/generate_wayfarer_torch_formal_library.py >/dev/null
git diff --exit-code -- engineering/verification/z3/wayfarer_torch_generated_cards_v0.1.smt2
out="$(cd "$HERE" && z3 wayfarer_torch_generated_synthesis_v0.1.smt2)"
first="${out%%$'\n'*}"
[[ "$first" == sat ]] || { printf '%s\n' "$out"; exit 1; }
count_fast="$(printf '%s\n' "$out" | grep -c 'FAST' || true)"
[[ "$count_fast" -ge 2 ]] || { echo 'EXPECTED GENERATED LIBRARY TO SYNTHESIZE FAST END SEGMENTS'; printf '%s\n' "$out"; exit 1; }
printf '%s\n' "$out"
echo 'LOOM_Z3_WAYFARER_TORCH_GENERATED_LIBRARY_STATUS=PASS'
