# Scratch flight laboratory completion — 27 October 2026

Implemented and exercised entirely in this scratch workspace. **NON-CANON numerical
experiments; no hardware certification, canonical repository change, or publication.**
The copied authority files remain unchanged: all eight pinned source hashes match.
No simulator installation, download, rebuild, external checkout, branch or PR work
was performed. The pre-completion archive and original study outputs remain present.

The existing solver now supports interchangeable two-axis RCS gimbals with actual
angle/rate/lag state and changing-vector allocation; separately fed tanks; Isp or
exhaust-speed inputs; optional installed engine mass and intrinsic inertia; independent
feed exhaustion; finite torch throttle and optional TVC slew; controlled shutdown
coasts; declarative sequencing; per-phase numerical criteria; and explicit
pass/fail/indeterminate reporting. Throttle command and actual lag remain separate.
Unknown fuel consumption remains null while applied impulse and known consumption
remain measurable. Two distinct experimental metric laws run from JSON: coordinate
translation and a rotating-coordinate state map. Canonical metric endpoints remain
unresolved and cannot resume conventional flight.

**Commands used** (existing `.venv`; no additional dependencies):

```bash
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
.venv/bin/python make_completion_examples.py
.venv/bin/python -m unittest -v test_flightlab test_completion
.venv/bin/python rcs_reference_validation.py
.venv/bin/python lab.py demo --dt .1 --out sol_baseline_results
.venv/bin/python lab.py demo --manifest completion_manifest.json --dt .02 --sample .1 --out sol_results
.venv/bin/python lab.py run configs/wayfarer_gimbal_reference.json experiments/gimbal12.json --dt .01 --sample .1 --out sol_timestep_results
.venv/bin/python completion_evidence.py
.venv/bin/python lab42.py reference_fixed300_pitch reference_fixed300_pitch
.venv/bin/python run_gmat.py
.venv/bin/python compare_gmat_lab.py
```

After adding coast stabilization and making canonical physical telemetry null, the
affected runs were individually rerun using `lab.py`'s `save_run` function; commands
and outcomes are in `sol_final_refinements.log`. `completion_evidence.py` verifies
current input hashes and rebuilds the comparison tables from final run records.

**Measured results.** Target-time error and rate are separate from sustained settling.
The historical gimbal runs retain all 32 fixed 25 kN nozzles plus eight additional
300 kN nozzles; prepositioning is excluded and added hardware mass/feed are UNKNOWN.

| Experiment | Error at target | Rate at target | Final gate entry | Numerical result |
|---|---:|---:|---:|---|
| Original fixed 25 kN, 40 s | 0.001013288° | 0.0001678°/s | 40.00 s | pass; fuel indeterminate |
| Original fixed 300 kN, 10 s | 0.046294278° | 0.037623800°/s | 10.62 s | pass; fuel indeterminate |
| Added gimbals, 10 s | 39.457224473° | 9.530241736°/s | none | fail |
| Added gimbals, 12 s | 0.028993430° | 0.018693259°/s | 12.00 s | pass; fuel indeterminate |
| Added gimbals, 14 s | 0.019298217° | 0.010285000°/s | 14.00 s | pass; fuel indeterminate |
| Neutral-start gimbals, 12 s | 0.028993430° | 0.018693259°/s | 12.00 s | pass; fuel indeterminate |
| Scout feedback gimbals, 20 s | 0.007286577° | 0.002551257°/s | 20.00 s | pass; 5.918633 kg used |

All **9/9 historical fixed-RCS comparisons** agree over 11 cases, including slow
actuation and fine timestep; the largest attitude discrepancy is below 5×10⁻¹⁰°.
All **3/3 historical gimbal comparisons** agree, including force and off-axis torque
peaks; no remaining 10/12/14 s reproduction mismatch was found. The 12 s candidate
reaches 30°/s mechanical slew, 7,066.95 N peak residual force, 71,698.25 N·m peak
off-axis torque and 0.003045 m/s residual velocity. Its explicit residual/settle
criteria pass; unknown feed prevents a system-level fuel pass. Neutral-start steering
is included and changes early history, though this maneuver has effectively the same
terminal result. Actual gimbal angles and nozzle directions are saved in traces.

At 0.01 s, the 12 s gimbal error is 0.026577326°, rate 0.017025630°/s and peak force
7,491.74 N. Both timesteps pass the declared gates; the changed peaks expose finite-step
steering sensitivity rather than establish hardware margins.

Scout's off-axis 200 kN installation produces **143.7014° drift and 24.4414°/s spin**
after the 12 s uncontrolled burn. RCS hold reduces burn drift to 2.14×10⁻⁷°;
controlled shutdown ends at 0.003048°/s and consumes 10.174521 kg across separate feeds.
An uncontrolled shutdown coast would add 1.3426° drift; the controlled one adds only
0.001381°. A distinct twin installation passes with 4.772915 kg consumed. With one
feed empty it fails fuel availability while the independently supplied engine keeps
firing and depletes its own tank to 97.629503 kg.

The seven-phase conventional/experimental-metric/conventional run consumes
**17.570721 kg**, ends at **100,353.429279 kg**, and retains exact position, velocity,
attitude, angular rate and actuator states at all **six boundaries**, with zero mass
jumps. Mass loss differs from the fuel ledger by 1.42×10⁻¹⁰ kg. Its metric operation
is explicitly a NON-CANON rotating-coordinate stipulation. In the separate law
comparison, translation preserves velocity `[10,0,0]` m/s and shifts position by
5.624107×10⁹ m; rotation maps velocity to `[0,10,0]` m/s and position to `[0,1800,0]`
m. These are different mathematical maps, not independent physical discoveries.
The canonical counterpart reports null physical endpoints and indeterminate closure.

**Verification:** **35 tests passed** (19 retained plus 16 new). Baseline demo:
11 runs, 8 numerical passes / 2 failures / 1 indeterminate. Completion demo:
14 runs, 10 numerical passes / 3 failures / 1 indeterminate. Adding declared fuel
availability gives 6 passes / 3 failures / 5 indeterminate for the completion demo.
These counts classify modeled criteria, not hardware readiness.

- NASA 42: 700 fixed-nozzle samples; maximum attitude difference
  **6.99336×10⁻⁶°**, angular-rate difference 5.00×10⁻⁸ rad/s.
- GMAT R2026a, rerun: 600 s mass-matched ordinary trajectory; position difference
  **0.002318704 m**, velocity difference **1.29668×10⁻⁶ m/s**.
- Independent DOP853 equations, moving-gimbal realized-wrench replay: 800 steps;
  maximum attitude difference **7.22169×10⁻¹⁰°**, final position difference
  **2.57×10⁻¹³ m**. This checks integration of the supplied wrench, not GNC independence.

Evidence: `sol_tests_final.log`, `sol_rcs_reference_final.log`, `sol_nasa42.log`,
`sol_gmat.log`, `sol_gmat_vs_lab.log`, `sol_evidence.log`; `sol_results/comparison.csv`,
`gimbal_reference_comparison.json`, `gimbal_timestep_comparison.json`,
`gimbal_dop853_replay.json`, `continuous_state_audit.json`, `reference_integrity.json`
and per-run JSON/CSV/telemetry/command traces. Baseline and half-step outputs are
retained separately. `implementation_hashes.json` records executable source hashes.

**Limitations and unsatisfied criteria:** All eight requested functional acceptance
demonstrations are present; no tooling blocker remains. Physical hardware qualification
and canonical metric closure remain unsatisfied by design: Wayfarer RCS feed/Isp and
added gimbal hardware mass are absent, and no authoritative metric state/accounting
law exists. Hypothetical Scout hardware values are authored fixtures. Moving-nozzle
NASA 42 replay remains unsupported by its adapter; a separate numerical replay is
provided. Gimbal policies use declared witness targets/schedules or feedback sign,
not an optimal planner. Moving nozzle directions use step-end hold, and fractional
fuel exhaustion spreads thrust over one step. Fuel geometry uses fixed centroids and
linearly scaled intrinsic tensors; variable-inertia dynamics have no full fluid
angular momentum flux closure. No slosh, plume, flex, sensor, structural or thermal
qualification is implied. Torch trim is instantaneous unless finite TVC slew is
configured. Metric maps stipulate transitions and establish no physical conservation
claims. These limits remain visible rather than being replaced with invented zeros.

**Changed files:** `flightlab.py`, `lab.py`, `lab42.py`, `FLIGHT_LAB_README.md`,
`FLIGHT_LAB_RESULTS.md`, `RCS_300KN_REPRODUCTION.md`; new
`make_completion_examples.py`, `completion_evidence.py`, `test_completion.py`,
`completion_manifest.json`, this report, eight configuration JSONs and twelve
experiment JSONs listed in `sol_results/delivery_manifest.json`. Generated evidence
is in `sol_results/`, `sol_baseline_results/`, `sol_timestep_results/`, refreshed
historical `lab_results/`, and scratch NASA/GMAT run outputs. Original study/reference
code and copied authority documents were not edited.
