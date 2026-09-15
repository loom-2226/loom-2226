#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
SECONDS=0

echo QUAL_PHASE_START=PYTHON_E1_FULL_REGRESSION
python -m unittest \
  tests.test_wayfarer_e1_torch_integrated_qualification \
  tests.test_wayfarer_e1_torch_structural_plume_ops \
  tests.test_wayfarer_e1_torch_remass_feed_nozzle \
  tests.test_wayfarer_e1_torch_energy_thermal \
  tests.test_wayfarer_e1_torch_interface \
  tests.test_wayfarer_torch_thermal_shield_thrust_frame_envelope \
  tests.test_wayfarer_shipyard_constraints \
  tests.test_wayfarer_torch_mission_constraints \
  tests.test_wayfarer_torch_generated_formal_library \
  tests.test_wayfarer_torch_feed_dynamics_nozzle \
  tests.test_wayfarer_torch_multisegment_python_crosscheck \
  tests.test_pixel_qualification_runner \
  tests.test_pixel_assisted_qualification

echo QUAL_PHASE_ELAPSED_AFTER_PYTHON=$SECONDS
echo QUAL_PHASE_START=Z3_FULL_REGRESSION
bash engineering/verification/z3/run_wayfarer_shipyard_z3.sh
bash engineering/verification/z3/run_wayfarer_torch_generated_library_z3.sh
bash engineering/verification/z3/run_wayfarer_torch_generated_z3.sh
bash engineering/verification/z3/run_wayfarer_torch_mission_z3.sh
bash engineering/verification/z3/run_wayfarer_mass_state_z3.sh
bash engineering/verification/z3/run_wayfarer_torch_mode_z3.sh
bash engineering/verification/z3/run_wayfarer_torch_segment_z3.sh
bash engineering/verification/z3/run_wayfarer_torch_multisegment_z3.sh

echo QUAL_PHASE_ELAPSED_AFTER_Z3=$SECONDS
echo QUAL_PHASE_START=RUNNER_SYNTAX
bash -n engineering/pixel/loom_pixel_run.sh
bash -n engineering/pixel/run_wayfarer_t5_qualification.sh

echo QUAL_PHASE_TOTAL_SECONDS=$SECONDS
