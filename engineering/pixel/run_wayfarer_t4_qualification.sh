#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

python -m unittest \
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

bash engineering/verification/z3/run_wayfarer_shipyard_z3.sh
bash engineering/verification/z3/run_wayfarer_torch_generated_library_z3.sh
bash engineering/verification/z3/run_wayfarer_torch_generated_z3.sh
bash engineering/verification/z3/run_wayfarer_torch_mission_z3.sh
bash engineering/verification/z3/run_wayfarer_mass_state_z3.sh
bash engineering/verification/z3/run_wayfarer_torch_mode_z3.sh
bash engineering/verification/z3/run_wayfarer_torch_segment_z3.sh
bash engineering/verification/z3/run_wayfarer_torch_multisegment_z3.sh
bash -n engineering/pixel/loom_pixel_run.sh
