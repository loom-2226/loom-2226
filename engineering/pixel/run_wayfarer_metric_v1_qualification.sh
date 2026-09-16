#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
SECONDS=0

echo QUAL_PHASE_START=PYTHON_E1_METRIC_FRONTIER
python -m unittest \
  tests.test_wayfarer_e1_metric_frontier_closure \
  tests.test_wayfarer_2226_frontier_accountant \
  tests.test_wayfarer_2226_frontier_consumers \
  tests.test_pixel_qualification_runner

echo QUAL_PHASE_ELAPSED_AFTER_PYTHON=$SECONDS
echo QUAL_PHASE_START=RUNNER_SYNTAX
bash -n engineering/pixel/loom_pixel_run.sh
bash -n engineering/pixel/run_wayfarer_metric_v1_qualification.sh

echo QUAL_PHASE_TOTAL_SECONDS=$SECONDS
