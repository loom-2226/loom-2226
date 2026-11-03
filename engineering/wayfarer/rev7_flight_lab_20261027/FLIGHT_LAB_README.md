# LOOM Spacecraft Flight & Propulsion Laboratory, scratch MVP

**Status:** WORKING EXPERIMENTAL MVP; non-governing, not hardware qualification or LOOM runtime. Developed entirely inside this scratch copy; no code edits in Astra's original study directory.

## Run

For the completion campaign and new fixtures, see the **Completion extension**
section below and `CODEX_SOL_HIGH_RESULTS.md`.

```bash
cd /home/ubuntu/wayfarer_flight_lab_scratch_20261026
.venv/bin/python make_examples.py
.venv/bin/python lab.py demo --dt 0.1
.venv/bin/python -m unittest -v test_flightlab
.venv/bin/python lab42.py wayfarer reversal40
.venv/bin/python run_gmat.py
.venv/bin/python compare_gmat_lab.py
```

Run a custom combination without editing the solver:

```bash
.venv/bin/python lab.py run configs/wayfarer.json experiments/reversal40.json --dt .1
.venv/bin/python lab.py run configs/scout.json experiments/reversal40.json --dt .1
.venv/bin/python lab.py run configs/wayfarer_twin_torch.json experiments/burn120_rcs_hold.json --dt .1
```

Modify a copy of a configuration JSON to change component mass, center of mass, inertia, tanks, individual thruster forces/positions/orientations/response, torch modes/installation, metric models, or experiment targets. The generic code loads the supplied JSON directly.

## Minimal source

- `flightlab.py`: ship and tank mass properties, six-component thrust allocation, rigid-body propagation, RCS gimbal commands, torch vectoring, metric-model execution, state continuity, and qualification checks.
- `lab.py`: portable JSON experiment runner, reproducible output and comparison manifest.
- `make_examples.py`: one-way generator from the copied Rev7 Wayfarer card/thruster geometry plus authored alternative configurations.
- `lab42.py`: independent NASA 42 replay of the new lab's realized fixed-RCS force commands and mass tensor.
- `compare_gmat_lab.py`: new lab-versus-GMAT R2026a comparison for a torque-free, mass-matched finite-burn benchmark.
- `test_flightlab.py`: focused physical and behavioral regression checks.

## Configuration and experiment files

- `configs/wayfarer.json`: derived from Wayfarer Rev7 S1 and S4; matches S1 mass, center of mass, and full inertia tensor, including off-diagonal terms.
- `configs/wayfarer_rcs_300k.json`: relocated 300 kN coarse thrusters, hypothetical added installation mass and exhaust velocity.
- `configs/wayfarer_twin_torch.json`: two off-center half-strength torch engines with added mass; an intentionally revealing configuration.
- `configs/scout.json`: independent smaller cylindrical ship with different mass, inertia, RCS mounts, and torch power.
- `experiments/reversal40.json`, `reversal10.json`: attitude maneuver tests.
- `experiments/translate20.json`: 0.5 m/s RCS translation with attitude hold.
- `experiments/burn120.json`: free-space torch burn with attitude acceptance criteria.
- `experiments/burn120_rcs_hold.json`: torch burn with active RCS attitude control.
- `experiments/metric_canonical.json`, `metric_experimental.json`: same metric envelope, different epistemic/transition laws.
- `experiments/combined.json`: one persistent state across torch, coast, RCS turn, experimental metric transport.
- `demo_manifest.json`: list of spacecraft/experiment combinations; edit to run custom comparisons.

## Outputs

- `lab_results/<ship>__<experiment>.json`: inputs' hashes, assumptions, measured metrics, qualification checks, final spacecraft state and phase summaries.
- `lab_results/<ship>__<experiment>.csv`: sampled time history of position, velocity, attitude, angular rate, mass, CG, and metric path.
- `lab_results/<ship>__<experiment>.rcs_trace.json`: timestep-realized nozzle commands and attitude states, used by the NASA 42 adapter.
- `lab_results/comparison.json`: side-by-side summary of demonstration experiments.
- `lab_results/wayfarer__reversal40_42.json`: NASA 42 quantitative replay differences.
- `results/gmat_comparison.json`: GMAT versus Astra's original ideal point-mass benchmark.
- `lab_results/gmat_vs_flightlab.json`: GMAT versus the new generic numerical propagator using an intentionally torque-free, mass-matched surrogate.

Qualifying an experiment means satisfying its **specified numerical criteria under its modeled assumptions**. It does not certify hardware. A canonical metric envelope is necessarily indeterminate at arrival because ordinary arrival state and accounting laws are not supplied. An experimental metric coordinate-shift can pass its own declared mathematics but is explicitly not physical evidence.

## Model scope and boundaries

The simulator solves rigid-body quaternion/Euler dynamics plus translational motion, with optional point-mass gravity. It integrates actuator response, commands, body forces, moments, and fuel mass. It recomputes the full CG and inertia tensor from installed components and a fixed-centroid tank representation each step. RCS can command torque with zero nominal net force, or any six-dimensional wrench for translation. Off-center torch engines produce genuine torque; idealized instantaneous torch center-of-mass trim has a specified angular limit. RCS may simultaneously stabilize the ship during torch operation.

**Critical limitations:**

1. Wayfarer baseline propulsion installation masses are already embedded in the dry spacecraft; alternative installations add declared hypothetical hardware masses. Do not interpret those as hardware design estimates.
2. Wayfarer remass is reconstructed from exact S1 and S4 mass moments. It uses a fixed equivalent tank centroid and linearly scaled intrinsic inertia in between. The real S3 geometry is not identical to this drain approximation. This is neither a slosh nor tank plumbing model.
3. Rev7 RCS Isp/exhaust velocity and RCS tank plumbing are not closed. Baseline RCS maneuver propellant consumption is **unknown**, not zero. Reports warn accordingly. A hypothetical RCS exhaust specification may be supplied for conditional scenarios.
4. The torch TVC correction is ideal instantaneous steering toward the current CG within an angle limit. It does not represent actuator dynamics, pointing noise, nozzle constraints, structural/thermal dynamics or nozzle-plume clearance. RCS gimbal motion supports prescribed targets, angle and slew bounds but not an independently optimized gimbal planner.
5. The rigid-body variable-inertia update is first-order. There is no full propellant angular-momentum-flux or fluid redistribution closure. Mass/force bookkeeping and geometry-derived moments are modeled; this is not a flexible-body or fluid-dynamics simulator.
6. Canonical metric capabilities come from the copied LOOM metric mode envelope, NOT a field/momentum/energy theory. For canonical metric transport, physical arrival coordinates, velocity, attitude, mass and consumables are explicitly unknown, and subsequent conventional maneuvers are refused. The experimental coordinate-shift law stipulates position shift with unchanged ordinary velocity: a testable invented **non-canon** transition, not a statement about nature.
7. NASA 42 checks constant-mass, fixed-nozzle **realized command histories** (not the controller). GMAT checks conventional finite-burn trajectory with an engine surrogate (not exotic torch feasibility). Neither independently qualifies hypothetical propulsion physics or installed hardware.
8. Numerical qualification is conditional on the specified envelope; missing RCS fuel and missing physical metric closure preclude hardware/system-wide qualification.

**Do not promote this workspace to LOOM canon or runtime without further review.** Source authority is the pinned copied Wayfarer Rev7 snapshot; verify current GitHub authority separately before any repository submission or canon decision. Astra's original workspace is a separate directory and is not modified by this work.

## Reproducing Astra's original high-power RCS campaign

**Critical distinction:** `configs/wayfarer_original_mount_300k.json` reproduces the original *24 non-axial thrusters uprated to 300 kN each* while retaining all eight 25 kN axial thrusters, original mounts, Rev7 S1 mass properties, 0.05 s lag and command slew 10 full-scale/s. It does NOT assume an added engine mass, nozzle design, RCS Isp or feed. `configs/wayfarer_rcs_300k.json` is a **different earlier alternative**, with only eight inward thrusters uprated, moved mounting positions and hypothetical hardware mass. The latter's failure does not contradict Astra's successful study.

```bash
# Reproduce the historical fixed-RCS study and compare all nine saved references
.venv/bin/python rcs_reference_validation.py

# Examine hypothetical engine-mass / mounting-position / engine-count changes
.venv/bin/python rcs_design_variations.py

# Examine 265, 270, 275 kN near the 10-second pass/fail transition
.venv/bin/python rcs_threshold_scan.py

# Run an independent 42 replay of the new laboratory's 300 kN thrust history
.venv/bin/python lab42.py reference_fixed300_pitch reference_fixed300_pitch
```

The full regression and numerical evidence are in `lab_results/rcs_reference_summary.json`, `lab_results/rcs_reference_comparison.json`, `lab_results/rcs_design_variations.json`, `lab_results/rcs_threshold_scan.json`, and `RCS_300KN_REPRODUCTION.md`.

**Scientific reporting correction:** Where Wayfarer's RCS specific impulse/feed is unknown and RCS fires, `total_propellant_used_kg` is now `null`, not zero. `known_propellant_used_kg` records only consumption from explicitly modeled propellant and `rcs_impulse_Ns` records applied nozzle impulse. Numerical maneuver passes remain conditional on frozen RCS mass until its propellant physics is supplied.

## Completion extension (27 October 2026)

The current solver adds dynamic two-axis RCS installations, independent fuel feeds,
finite torch throttle/TVC slew, explicit phase criteria and two distinct experimental
metric maps. Existing fixtures and `lab.py demo` remain usable. Final measured results
and limitations are in `CODEX_SOL_HIGH_RESULTS.md`; new evidence is under `sol_results/`.

```bash
export PYTHONDONTWRITEBYTECODE=1
# Optional: small matrices do not benefit from many BLAS threads.
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
.venv/bin/python make_completion_examples.py
.venv/bin/python lab.py demo --manifest completion_manifest.json --dt .02 --sample .1 --out sol_results
.venv/bin/python lab.py demo --dt .1 --out sol_baseline_results
.venv/bin/python lab.py run configs/wayfarer_gimbal_reference.json experiments/gimbal12.json --dt .01 --sample .1 --out sol_timestep_results
.venv/bin/python completion_evidence.py
.venv/bin/python -m unittest -v test_flightlab test_completion
.venv/bin/python rcs_reference_validation.py
.venv/bin/python lab42.py reference_fixed300_pitch reference_fixed300_pitch
.venv/bin/python run_gmat.py
.venv/bin/python compare_gmat_lab.py
```

Individual design comparisons:

```bash
.venv/bin/python lab.py run configs/wayfarer_gimbal_reference.json experiments/gimbal12.json --dt .02 --out sol_results
.venv/bin/python lab.py run configs/wayfarer_gimbal_cold.json experiments/gimbal12.json --dt .02 --out sol_results
.venv/bin/python lab.py run configs/scout_gimbal.json experiments/scout_gimbal_turn.json --dt .02 --out sol_results
.venv/bin/python lab.py run configs/scout_offset_torch.json experiments/offset_hold.json --dt .02 --out sol_results
.venv/bin/python lab.py run configs/scout_twin_empty.json experiments/twin_burn.json --dt .02 --out sol_results
.venv/bin/python lab.py run configs/scout_offset_metric.json experiments/continuous.json --dt .02 --out sol_results
.venv/bin/python lab.py run configs/scout_metric_models.json experiments/metric_rotation_compare.json --dt .1 --out sol_results
```

A nozzle's optional `gimbal` block declares `axial_direction`, `limit_deg`,
`rate_deg_s`, `lag_s` and `initial_angles_deg`. Neutral direction `n` is the
engine's ordinary `direction`; the axial vector `a` must be perpendicular to it,
and `t = a × n`. The two mechanical angles give
`d = cos(b) cos(a_angle) n + cos(b) sin(a_angle) t + sin(b) a`.
Each angle has its own bounds and rate limit; **25° per angle is not a 25° cone**.
`policy` is `fixed`, `schedule`, `phase_fraction`, or `wrench_sign`.
The latter selects `positive_angles_deg` / `negative_angles_deg` using the current
requested wrench component (0–2 force, 3–5 torque), including torch torque
compensation. `schedule` uses ordered `{time_s, angles_deg}` entries, in local phase
time. These are declared steering policies, not an optimal gimbal planner.
Actual angles persist across phases. Each step moves the angles with exponential
lag and per-axis rate limits, then allocates a fresh exact six-component requested
wrench at the moved directions. Independent command slew and thrust lag can leave
an actual residual wrench; the simulation measures it instead of cancelling it
artificially. `gimbal_constraints.json` makes these residual limits binding.
The historical witness fixtures exclude prepositioning time and extra hardware
mass; `wayfarer_gimbal_cold.json` starts at neutral and includes all steering time.

Engine `installed_mass_kg` and optional `installed_inertia_kg_m2` add hardware at
`pos_m` (do not also include that mass in `components`). Engines accept either
`ve_m_s` or `isp_s`; if both are supplied they must agree. Different engines may
feed different named tanks. An empty feed curtails only its own engines. Unknown
exhaust/feed produces null total consumption and indeterminate fuel availability;
known impulse and consumption from other tanks remain available. Known tank mass,
CG and full inertia are recomputed during the run. The historical Wayfarer RCS
model remains frozen for its unspecified consumption, with no invented Isp or
engine mass. Alternate Scout hardware numbers are explicitly authored assumptions.

Torch phases accept `engine_throttles` by engine ID, with ordinary `throttle` as
the fallback. Throttle is clipped to 0–1; installation `max_N`, mode thrust,
power ceiling (when exhaust speed is known), and acceleration caps are enforced.
Optional `lag_s` and `command_slew_fullscale_s` preserve actuator state and shutdown
tails across conventional phases. Optional `tvc_rate_deg_s` bounds auto-trim slew;
without it the original ideal instantaneous trim remains. Mode selection persists
during shutdown/coast. A coast with `hold_attitude: true` keeps RCS control active
through the torch shutdown tail. The default fixtures retain their original ideal response.

`checks` may appear on the experiment and on each phase. Bounds are `{min, max}`;
unknown measurements produce an indeterminate check. Phase checks are binding in
the final verdict. Useful phase quantities include `attitude_error_deg`,
`rate_deg_s`, `gate_entry_s` (absolute run time), `sustained_gate_duration_s`,
`residual_velocity_m_s`, `residual_displacement_m`, `peak_angular_rate_deg_s`,
`peak_force_residual_N`, `peak_torque_residual_Nm`, `peak_offaxis_torque_Nm`,
`minimum_allocated_fraction`, `peak_gimbal_rate_deg_s`, `peak_gimbal_angle_deg`,
`peak_throttle`, `peak_command_slew_fullscale_s`, saturation step counts and
`propellant_available` (1/0/null). Residual displacement subtracts the phase's
initial ballistic velocity; residual velocity is the velocity change during that
phase, so use these as disturbance criteria on attitude turns, not burns or
transport. `gate_hold_s` retains the historical sampled gate-count convention;
`sustained_gate_duration_s` measures the interval from final gate entry to phase end.
Target time is an exact integration boundary even if `dt` does not divide it.
Global peaks are maxima over phases; global step counts currently report the
largest per-phase count. Detailed per-phase counts are retained.

`qualification` covers exactly the configured numerical checks.
`physical_qualification` separately checks declared propellant availability;
`system_status` combines those two and is indeterminate for a numerical pass with
unknown fuel. All three remain **simulation results**, never hardware approval.
A failed known criterion remains visible alongside unknown criteria.
`sequence_constraints` optionally declares `allowed_next` phase kinds,
`coast_before_s` durations, and `metric_entry_max_throttle`. These constraints are
experimental operating assumptions, not a claim to derive canonical operating law.
The continuous example includes idle coasts and resumes conventional propagation
after its NON-CANON metric map. Every phase records exact boundary physical and
actuator states for audit.

The two experimental maps are selected entirely in ship JSON:

- `experimental_coordinate_shift`: conventional torque-free propagation plus
  `r ← r + direction * ds`, with velocity, angular rate, tanks and mass preserved
  by the stipulated translation.
- `experimental_frame_rotation`: after conventional propagation, rotate `r-pivot`,
  `v`, and body-to-inertial attitude by `dtheta = rotation_deg * ds / total_path`
  about configured `rotation_axis`. Body angular rate and tank/mass state persist.
  This is an invented coordinate map, not a physical thrust or torque law. Its
  reported speed is the mapped ordinary state variable, not a derivative-derived
  metric transport velocity. Default total rotation is 90°, with no claim that the
  metric path envelope describes ordinary distance travelled in this map.

Both maps are NON-CANON, with no independent physical energy/momentum validation.
`canonical_envelope` only accumulates the path envelope: all physical endpoint
fields and final physical speed/consumption are null, and ordinary continuation
is refused. The earlier README's single-model and prescribed-only-gimbal
limitations are superseded by these extensions; canonical metric closure remains
absent.

Each run now also writes `.telemetry.json` with sampled tanks, full inertia,
gimbal angles and applied wrench. CSV adds tank/gimbal JSON columns and body force
and torque. RCS trace includes directions and realized wrench during active control
and shutdown tails. Demo writes a reusable `comparison.csv` as well as JSON.
NASA 42's adapter explicitly refuses moving gimbals and variable-mass replays;
`completion_evidence.py` independently replays the moving-gimbal realized wrench
with DOP853. Neither replay independently validates the controller or hardware.
Moving nozzle directions are held at their step-end values during each numerical
step, matching the historical study. Tank exhaustion spreads curtailed thrust over
one step; reduce timestep to assess those approximations. Fuel tensors still use
fixed centroids and linearly scaled intrinsic moments, and there is no fluid
angular momentum flux closure, slosh, plume, thermal, flex or sensor model.
