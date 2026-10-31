# Wayfarer Rev 7 flight laboratory: independent-review preservation

**NON-CANON / NON-RUNTIME / NON-GOVERNING / NOT HARDWARE CERTIFIED.** Preserved from the working flight lab on \`quantifactus\`, 27 October 2026. This directory contains the executable numerical flight laboratory, its input fixtures, selected recorded campaign results, and qualification gap assessment. It does **not** copy or amend the Wayfarer spacecraft design.

## Exact spacecraft source authority

- Repository: [loom-2226/loom-2226](https://github.com/loom-2226/loom-2226)
- Existing candidate: [PR #432](https://github.com/loom-2226/loom-2226/pull/432), \`archive/wayfarer-v057-20261026\`
- Tested candidate commit: \`3485830a56dfead79b2ef8bba031a595b536fbb5\` (**Rev 7**, despite the PR's older Rev 4 title)
- Main at the campaign bootstrap: \`19377b854c529e74afc61202d9eb2e780c5b4884\`
- Inputs pinned in \`source_manifest.json\`; source content is intentionally **not** vendored here.
- The Rev 7 candidate is non-governing; \`source/design/wayfarer/v0.5.7/out/certification_report.json\` says \`certified=false\`.

**Do not silently use the version of the spacecraft on \`main\` in place of Rev 7.** For a review, obtain the exact commit in a separate local \`source/\` checkout. No repository pushes or canon changes are needed to run the lab.

## Cold-start review on Linux (Python 3.12)

From a clone of this preservation PR, enter this directory:

\`\`\`bash
cd engineering/wayfarer/rev7_flight_lab_20261027
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt

# Pinned spacecraft design is read-only input, not duplicated in this PR:
git clone --filter=blob:none --no-checkout https://github.com/loom-2226/loom-2226.git source
git -C source fetch origin archive/wayfarer-v057-20261026
git -C source checkout --detach 3485830a56dfead79b2ef8bba031a595b536fbb5
git -C source rev-parse HEAD

PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  .venv/bin/python -m unittest -v \
  test_flightlab test_completion test_canon_metric_operation test_hardware_assess
\`\`\`

Expected result from the 27 October run: **55/55 tests passed**. Python versions recorded on the source VM: 3.12.3, NumPy 2.5.4, SciPy 1.18.1. The test suite reads the pinned Rev 7 card and canonical source constraints; it does not need NASA 42 or GMAT installed.

A non-destructive numerical demonstration using **new output paths**, so preserved historical results remain unchanged:

\`\`\`bash
.venv/bin/python lab.py run configs/wayfarer.json experiments/reversal40.json \
  --dt .02 --out review_runs/rcs
.venv/bin/python lab.py run configs/wayfarer.json experiments/burn120.json \
  --dt .02 --out review_runs/torch
.venv/bin/python hardware_assess.py configs/reference_fixed300_pitch.json \
  experiments/reference_fixed300_pitch.json --dt .02 --out review_runs/hardware
\`\`\`

Full campaign reproduction commands remain in \`full_flight_20261027/FLIGHT_TEST_REPORT.md\`. **They may overwrite historical output paths**, so run full reproduction in a disposable clone or use renamed output directories. \`rcs_reference_validation.py\` uses the included \`results/rcs_runs.json\` historical Astra witness set. \`make_completion_examples.py\` consumes the included \`results/gimbal_static.json\`. The selected \`sol_results\` and \`sol_timestep_results\` JSON files preserve gimbal reference comparisons. No original Astra workspace is required.

## Review entrypoints and evidence

| Purpose | Files |
|---|---|
| Orientation and status | \`QUALIFICATION_GAPS.md\`, \`NEW_CHAT_HANDOFF_20261027.md\`, \`FLIGHT_LAB_README.md\` |
| Core executable | \`flightlab.py\`, \`lab.py\`, \`hardware_assess.py\`, four \`test_*.py\` |
| Configs and input phases | \`configs/\`, \`experiments/\`, \`demo_manifest.json\`, \`completion_manifest.json\` |
| Complete 27 Oct summary | \`full_flight_20261027/FLIGHT_TEST_REPORT.md\`, \`regression_tests.log\`, \`g10_rev7.json\`, \`flight_matrix.json\` |
| Scenario summaries | \`full_flight_20261027/core/comparison.json\`, \`completion/comparison.json\`, \`hardware/comparison.json\` |
| Historical RCS replay | \`RCS_300KN_REPRODUCTION.md\`, \`rcs_reference_validation.py\`, \`lab_results/rcs_reference_comparison.json\`, \`results/rcs_runs.json\` |
| Gimbal reproductions | \`CODEX_SOL_HIGH_RESULTS.md\`, \`sol_results/gimbal_reference_comparison.json\` |
| Physical demand/holds | \`HARDWARE_QUALIFICATION_RESULTS.md\`, \`full_flight_20261027/hardware/*.assessment.json\` |
| Canonical metric hold | \`CANON_METRIC_OPERATIONAL_RESULTS.md\`, \`canon_metric_results/wayfarer__wayfarer_canonical_operation.json\` |
| Independent numerical comparisons | \`full_flight_20261027/nasa42.log\`, \`gmat_comparison.log\`, \`lab_results/reference_fixed300_pitch__reference_fixed300_pitch_42.json\`, \`lab_results/gmat_vs_flightlab.json\` |

The original 27 October flight campaign used ten execution lanes, all exit code 0, including **55/55 lab tests**, **25/25 Rev 7 G10 engineering checks**, **18/18 additional Wayfarer flight sweep**, **9/9 original fixed-RCS references**, seven hardware scenarios (all overall HOLD), a NASA 42 fixed-RCS replay and a GMAT finite-burn surrogate comparison. See the detailed report rather than inferring hardware or mission qualification from exit codes.

## Preservation boundaries

- This directory preserves the original scripts/fixtures/results **as evidence**, including original VM-path prose in historical reports. \`QUALIFICATION_GAPS.md\` is the new review synthesis.
- \`source/\` is deliberately absent and ignored; the exact spacecraft source already exists in GitHub PR #432.
- External NASA 42 and GMAT **installations and bulk logs** are omitted. Their recorded comparisons can be inspected here, but independent reproduction with those executables requires obtaining them separately.
- Full-resolution, large, redundant \`rcs_trace\` and generated telemetry files from some runs are omitted. Core numerical test cases and campaign summaries are retained; rerun to regenerate omitted traces.
- \`navigator_decoded_readonly.py\`, a standalone historical Navigator copy not used by the flight lab, is omitted. The live repository's Navigator remains authoritative in its own scope.
- The 50-tonne protected water inventory is **not** available for normal propulsion. Unknown RCS Isp/feed means unknown fuel usage, not zero.
- Hypothetical 300 kN fixed and eight-added-gimbal RCS alternatives are **not** actual installed or approved hardware.
- Canonical metric \`U^M_\gamma\` and finite conservation/arrival state remain intentionally parked. No simulated coordinate shift is canonical metric evidence.

**Review goal:** independently audit the code and saved test evidence, challenge conclusions and identify the minimum remaining work for in-world engineering qualification without inventing hardware certificates, source authority, or metric physics. Refer to \`QUALIFICATION_GAPS.md\`.
