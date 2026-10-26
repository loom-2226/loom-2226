# Wayfarer Rev 7 — complete available scratch flight-test campaign
**Date:** 2026-10-27 (Australia/Melbourne)  
**Result:** AVAILABLE NUMERICAL FLIGHT TESTING EXECUTED; PHYSICAL HARDWARE / CANONICAL METRIC / MISSION QUALIFICATION NOT CLOSED.

## Exact configuration and authority
- Live GitHub main at time of check: `19377b854c529e74afc61202d9eb2e780c5b4884`.
- Tested source: archived, non-governing Wayfarer v0.5.7 Rev 7 commit `3485830a56dfead79b2ef8bba031a595b536fbb5`, branch `archive/wayfarer-v057-20261026`, matching the copied `source/` checkout; source tree clean.
- The Rev7 candidate has NOT been promoted to main/canon. [Draft PR #432](https://github.com/loom-2226/loom-2226/pull/432) remains open.
- Vehicle baseline: S1 `configs/wayfarer.json`, ~1,167,680 kg, 32 original 25 kN RCS thrusters (24 nonaxial + eight axial), central magnetic torch, 250,000 kg normal remass; an additional 50 t protected water is not authorized as propulsion fuel.
- The original source card is a non-governing Rev7 conditional full tensor; later governed design priority still marks final configuration-aware inertia OPEN. `source/design/wayfarer/v0.5.7/out/certification_report.json` has `certified=false`. No production or canon modifications were made.

## Fresh execution record

| Test lane | Executed | Outcome |
|---|---:|---|
| Unit/integration tests (`test_flightlab test_completion test_canon_metric_operation test_hardware_assess`) | 55 | 55 PASS |
| Original Rev7 G10 source flight-engineering checks (executed read-only by import) | 25 | 25 PASS (5 card, 7 RCS, 4 torch, 5 metric, 4 Loom) |
| Original/generalized laboratory demo `demo_manifest.json` | 11 | 8 numerical PASS; 2 deliberately failing designs; 1 canonical metric INDETERMINATE |
| Advanced laboratory demo `completion_manifest.json` | 14 | 10 numerical PASS; 3 deliberately failing designs; 1 canonical metric INDETERMINATE |
| Additional Wayfarer vehicle-specific sweep `flight_matrix.py` | 18 | 18 numerical PASS: 6 torch modes, 6 three-axis attitude cases, 6 translations |
| Historical fixed-RCS study replay `rcs_reference_validation.py` | 11 | 9/9 original Astra historical cases matched; other two are extra comparison configurations |
| Physical-hardware demand assessment `hardware_assess.py --examples` | 7 | Executed; all seven complete-hardware dispositions HOLD, with scoped numeric PASS/FAIL |
| NASA 42 independent fixed-RCS dynamics replay | 700 time samples | Max attitude difference 6.9934e-6 deg |
| GMAT R2026a independent 600 s conventional torch trajectory surrogate | One 600 s benchmark | Position difference 0.0023187 m; velocity 1.2967e-6 m/s; mass 7.6531e-7 kg |
| HARD/LIMIT high-thrust acceleration check | 600 per-step samples per mode | Maximum instantaneous acceleration equals 4.000000000000002 g to numerical precision |

**Important distinction:** PASS here means that a particular modeled numerical criterion was met. Flight numerical PASS and system/hardware PASS differ. Unknown Wayfarer RCS exhaust/feed makes otherwise passing RCS runs SYSTEM INDETERMINATE; the laboratory correctly records unknown RCS consumption as null rather than zero.

## Wayfarer flight results

**Original 25 kN RCS:** 180° pitch reversal in 40 s passes, terminal attitude error about 0.0010° with 0.000168°/s angular rate in the historical .02 s benchmark. Demanding 10 s fails with 135.07° error and 9.12°/s residual rate. The additional three-axis survey passed 180° roll, pitch, yaw in 40 s at .05 s timestep with approximately 0.00125° error on each axis. Six independent +/− 0.5 m/s body-axis translation maneuvers passed; speed error was approximately 0.00007747 m/s per maneuver; RCS propellant remains unknown.

**Fixed upgraded 300 kN arrangement:** THE HISTORICAL SUCCESSFUL DESIGN is 24 original nonaxial thrusters uprated to 300 kN apiece, *with the eight axial thrusters left at 25 kN and original mounting points intact*. At 10 s, 180° pitch: attitude 0.046294278°, rate 0.037623799°/s, terminal gate PASS, final uninterrupted gate entry 10.62 s. Pitch/yaw and loaded-mass S2 historical studies reproduce. The 180° roll/pitch/yaw vehicle survey at .05 s timestep also passes for this candidate (about 0.0574° attitude error each). It is a force-only hypothetical installation with no established upgraded thruster mass, fuel/Isp, feed, plume, mount strength or thermal endurance. A 300 kN one-cluster-out 10 s test FAILS, as does the slow-actuator variant. DO NOT confuse the separate earlier eight-inward-only moved-mount candidate (23.77° error, FAIL) with this original-layout success.

**Added eight gimballed 300 kN engines:** Numerical 10 s maneuver FAILS; 12 and 14 s PASS in the approved modeled configurations. The 12 s terminal attitude error is 0.028993430°, angular rate 0.018693259°/s, with 12 s sustained gate entry. Moving gimbals reach configured 30°/s rate and 25°/axis angle. Cold-start and prepositioned variant comparison traces are available; this is not a qualified installation.

**Conventional torch across all six Rev7 modes:** Every 120-second S1 burn met the configured numerical drift/rate test. Normal remass expended (kg): ECON 136.3320, CRUISE 681.6600, EXPEDITE 2726.6400, FAST 5564.5714, HARD 12150.8745, LIMIT 18178.8920. MASS LEDGER closes in modeled cases. HARD and LIMIT deliver a tested **4 g instantaneous crew acceleration cap**; treating peak force divided by the lower *final* mass as actual instantaneous g is incorrect. The source G10 tests also exercise the mode card and finite segmented torch assumptions. The lab's 120 s torch runs do not establish structural fatigue, feed, plume, radiator endurance, or hardware commissioning.

**Integrated flight and realistic failures:** The reference combined torch/coast/RCS/experimental-metric case runs with one continuous state. Advanced seven-phase Scout case retains exact state across six boundaries. Free off-axis torch destabilizes attitude and fails; RCS-held offset torch passes where the feed is specified. Fuel-empty twin-engine variant fails with detected depletion, as intended. Twin-offset Wayfarer without hold fails while with attitude hold passes numerically but RCS fuel remains unknown.

**Canonical metric:** The source-constrained metric operating sequence validates, but correctly HOLDS at field acquisition because external applicable certification, calibrated `U^M_gamma`, and finite conservation ledgers are not available. Canonical arrival position, ordinary velocity, remass, momentum and energy remain unresolved; no ordinary flight is resumed after unresolved canonical arrival. Noncanonical coordinate-map experiments are model-internal comparisons only.

**Physical hardware:** All seven assessed installations remain hardware HOLD despite numerical comparison PASS in some subrequirements. Modeled peak common mounting force demand: original 25 kN ~25.0 kN, fixed 300 kN ~300.001 kN, eight-added-gimbal ~324.632 kN, CRUISE torch ~11.361 MN. Missing load-bearing bracket capacities, real RCS engine/Isp/feed, local mounting reinforcement, plume effects, thermal endurance, and independent material/component acceptance records prevent physical hardware certification.

## Independent numerical confidence

- **NASA 42:** compiled NASA dynamics independent of the lab integrator; 700 samples, .02 s; max rigid-body attitude disagreement `6.993355899838714e-06°`. NASA 42 replays *realized thrust commands*, and does not independently certify GNC, fuel, or moving-gimbal control.
- **GMAT R2026a:** separately executes finite conventional torch burn in Sun point gravity. GMAT uses a torque-free mass-matched surrogate rather than the actual offset torch installation; relative position mismatch `0.002318704 m` after 600 s, speed `1.296678e-06 m/s`, mass `7.653143e-07 kg`.
- **RCS 9/9** original cases reproduced to numerical precision, including fine timestep and slower actuators.
- No authoritative source files changed.

## What this does NOT qualify
1. Mission qualification flights E1, FR-01B-R and MV-01 are explicitly deferred in the Rev7 G10 source: no end-to-end Navigator fixture/import has been established. G10 25/25 is not these missions.
2. Complete physical hardware certification or actual vehicle installed propellant/thermal/plume/structure response, especially the hypothetically uprated RCS thrusters.
3. Canonical metric ordinary-state propagator `U^M_gamma`, field/environment correction, finite wake/energy-momentum exchange or exact arrival.
4. Final authoritative LOOM inertia and spacecraft configuration. The Rev7 full tensor and frozen tank fill centroid are conditional engineering hypotheses.

## Exact runnable commands

Run all commands from `/home/ubuntu/wayfarer_flight_lab_scratch_20261026`:

```bash
.venv/bin/python -m unittest -v test_flightlab test_completion test_canon_metric_operation test_hardware_assess
.venv/bin/python lab.py demo --manifest demo_manifest.json --dt .1 --out full_flight_20261027/core
.venv/bin/python lab.py demo --manifest completion_manifest.json --dt .02 --out full_flight_20261027/completion
.venv/bin/python full_flight_20261027/flight_matrix.py
.venv/bin/python rcs_reference_validation.py
.venv/bin/python hardware_assess.py --examples --out full_flight_20261027/hardware
.venv/bin/python run_gmat.py
.venv/bin/python compare_gmat_lab.py
.venv/bin/python lab42.py reference_fixed300_pitch reference_fixed300_pitch
```

## Stored evidence
- `regression_tests.log`, `g10.log` and `g10_rev7.json`, `core.log`, `core/comparison.json`, `completion.log`, `completion/comparison.json`
- `flight_matrix.py`, `flight_matrix.json`, `flight_matrix.log`, `torch_g_cap.log`
- `rcs_reference.log` and `../lab_results/rcs_reference_summary.json`
- `hardware.log`, `hardware/comparison.json` and seven `hardware/*.assessment.json`
- `nasa42.log`, `gmat.log`, `gmat_comparison.log`
- One `*_exit.txt` per executed lane, `0` for success.

**Overall conclusion:** Every available numerical flight-testing lane exercised successfully, including failure detectors and preservation of epistemic HOLDS. The default Rev7 25 kN installation meets modeled 40 s 180° attitude performance; the unbuilt 24×300 kN fixed installation meets modeled 10 s terminal performance; added vectored gimbals achieve 12 s. No tested configuration is physically hardware-certified or promoted to LOOM canon.
