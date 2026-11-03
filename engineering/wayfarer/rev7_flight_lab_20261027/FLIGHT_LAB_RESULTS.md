# Scratch MVP verified results, 26 October 2026

**Workspace:** `/home/ubuntu/wayfarer_flight_lab_scratch_20261026/` (Astra's original untouched).

**Final clean run:** 11 runnable configuration/experiment pairs: 8 simulated passes, 2 simulated failures, 1 indeterminate canonical metric result. All 19 focused unit/integration tests passed after the RCS actuator-state and propellant-reporting corrections. No LOOM repository change or merge performed.

| Run | Verdict | Key measured result |
|---|---|---|
| Wayfarer baseline, 180° pitch/40 s | PASS (conditional) | 0.001615° attitude error; RCS exhaust/fuel not specified |
| Wayfarer RCS translate, +0.5 m/s/20 s | PASS (conditional) | +0.500077 m/s achieved; RCS exhaust/fuel not specified |
| Wayfarer upgraded and relocated coarse RCS, 180°/10 s | FAIL | 23.770° attitude error; 32.17°/s residual rate |
| Scout alternate spacecraft, 180°/40 s | PASS | 0.001614° attitude error; 3.041 kg modeled RCS propellant used |
| Wayfarer single torch, 120 s | PASS | 681.66 kg remass consumed; 1167.887 m/s speed in free space |
| Wayfarer twin offset torch, 120 s, no RCS hold | FAIL | 125.85° attitude drift and 20.70°/s terminal spin |
| Same twin torch with active RCS attitude hold | PASS (conditional) | ~zero angular drift; 4.081 MN·s of RCS impulse, RCS propellant unresolved |
| Scout torch, 120 s | PASS | 72.0 kg propellant, 360.13 m/s final speed |
| Canonical metric envelope, NORMAL/80 s | INDETERMINATE | Coordinate path only; physical arrival state unknown |
| Experimental coordinate-shift, NORMAL/80 s | PASS (model-internal only) | 5,624,106.512 km stipulated coordinate displacement; NON-CANON |
| Wayfarer combined torch/coast/RCS/experimental metric | PASS (conditional) | Four phases, one preserved conventional state; metric law explicitly hypothetical |

**Independent checks:** NASA 42 replayed the newly generated Wayfarer RCS command stream over 400 samples: maximum attitude difference 0.0000071853°. GMAT R2026a versus the *new* laboratory on a 600-second torque-free heliocentric Wayfarer-mass surrogate: 0.002319 m position and 1.297e-6 m/s velocity differences. These check numerical conventional dynamics only, not hardware or hypothetical metric/torch physics.

**Boundaries:** Wayfarer mid-drain tank geometry is interpolated between exact S1 and S4 endpoints, not identical to S3. Wayfarer RCS feed/Isp absent. No slosh, flexible-body, thermal/plume, real torch TVC servo, or complete variable-inertia fluid angular-momentum flux model. Metric arrival physics unresolved for canonical mode. Qualification reports reflect specified numerical assumptions, not hardware certification.

Evidence: `lab_results/comparison.json`, individual run JSON/CSV/trace files, `lab_results/wayfarer__reversal40_42.json`, `lab_results/gmat_vs_flightlab.json`, and `scratch_unittest.log`.

## Later validated RCS reproduction

The original fixed-300 kN Wayfarer arrangement and eight additional historical control/failure cases now reproduce Astra numerical results. See `RCS_300KN_REPRODUCTION.md` and `lab_results/rcs_reference_summary.json`. As corrected in the current simulation, RCS-specific propellant consumption is **unknown**, not zero. Numeric terminal maneuver pass/fail is not hardware certification.

## Completion campaign, 27 October 2026

See `CODEX_SOL_HIGH_RESULTS.md` for the implemented extension, final run counts,
measured gimbal/torch/metric comparisons and remaining physics limitations.
The 26 October observations above are retained as historical evidence.
