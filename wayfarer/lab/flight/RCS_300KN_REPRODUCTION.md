# Wayfarer Rev7 higher-power RCS, reproduced in the generalized scratch laboratory

**Status:** Non-governing numerical experiment, 26 October 2026. All modifications and evidence are confined to
`/home/ubuntu/wayfarer_flight_lab_scratch_20261026`.
Astra's original workspace remains unchanged. The reference is the copied Wayfarer Rev7 study, not an assertion about today's live GitHub authority.

## The original 300 kN architecture

The original `study.py` does **not** replace eight inward thrusters with 300 kN engines. It uprates **all 24 non-axial** RCS thrusters (inward, tan+, tan-) to 300 kN while retaining **eight 25 kN axial** thrusters. Each retains the original Wayfarer location and direction.

Matching numerical assumptions: Wayfarer Rev7 S1 mass 1,167,680 kg and full inertia tensor, no new engine mass, zero initial angular rate, 180-degree pitch maneuver, 10-second commanded duration, 0.02-second timestep, independent throttle-command slew of 10 full-scale/s and realized actuator lag of 0.05 s. The nominal control gains are experimental (angular natural frequency 3 rad/s and damping 1); initial attitude and state estimates are perfect.

**Terminal acceptance:** attitude error ≤0.25 degrees **and** total angular rate ≤0.05 degrees/s at the nominal completion time. Post-target settling gate is separately measured.

## Historical reproduction

After fixing an actuator-state bug in the generalized laboratory, **all 9 matching Astra reference cases agree** on performance, pass/fail status and recorded gate entry, with attitude differences at or below approximately 5e-10 degrees.

| Configuration | Nominal time | Error at target | Angular rate at target | Terminal pass | Final gate entry |
|---|---:|---:|---:|---|---:|
| Original 25 kN | 10 s | 135.072711° | 9.117068°/s | No | None within 14 s |
| Original 25 kN | 40 s | 0.001013° | 0.000168°/s | Yes | 40.00 s |
| Fixed 150 kN non-axial | 10 s | 50.704578° | 28.215689°/s | No | None within 14 s |
| Fixed 200 kN non-axial | 10 s | 48.488159° | 13.655640°/s | No | None within 14 s |
| Fixed 250 kN non-axial | 10 s | 0.889068° | 2.168744°/s | No | 11.62 s |
| Fixed 300 kN pitch | 10 s | 0.046294° | 0.037624°/s | Yes | **10.62 s** |
| Fixed 300 kN yaw | 10 s | 0.046276° | 0.037665°/s | Yes | 10.62 s |
| Fixed 300 kN loaded (S2) | 10 s | 0.046312° | 0.037585°/s | Yes | 10.62 s |
| Fixed 300 kN, F+Z cluster disabled | 10 s | 10.400297° | 2.156973°/s | No | 13.78 s |
| Fixed 300 kN, 0.20 s lag | 10 s | 0.162354° | 0.131865°/s | No | 11.02 s |
| Fixed 300 kN, 0.01 s timestep | 10 s | 0.042440° | 0.034231°/s | Yes | 10.56 s |

The 150 and 250 kN ratings are additional conditional experiments, not saved original Astra cases. They are useful comparisons rather than historical-reference matches.

**Crucial distinction:** A pass at 10.00 s is a terminal-state test, not confirmation that the vehicle stays inside the terminal gate immediately afterward. The final sustained gate entry for the 300 kN configuration is **10.62 s**.

## Design sensitivity (hypothetical hardware)

These change one physical assumption at a time while retaining the 24 uprated non-axial plus eight 25 kN axial layout unless explicitly stated.

| Case | Error at 10 s | Rate at 10 s | Pass? |
|---|---:|---:|---|
| Original 300 kN, no mass changes | 0.046294° | 0.037624°/s | Yes |
| Add 375 kg to each of 24 upgraded engines (9 t total) | 0.046311° | 0.037587°/s | Yes |
| Shift the 24 coarse mounts outward by 1 m in fore/aft direction | 0.046272° | 0.037674°/s | Yes |
| Shift mounts and add 9 t | 0.046285° | 0.037644°/s | Yes |
| Uprate **only eight inward engines** to 300 kN, other 24 remain 25 kN | 18.997858° | 32.184867°/s | **No** |

Astra's earlier gimballed eight-engine **additional** coarse/32-fine study was a different architecture: it failed the 10 s maneuver and passed at 12 s under conditional prepositioning and mass assumptions. Those gimbal results are retained as *historical study outputs*, not yet numerically reproduced through the generalized gimbal implementation.

An extra fixed-nozzle rating scan found that 275 kN failed because its terminal rate was 0.054269°/s (just above the 0.05°/s gate) while 280 kN passed at 0.038724°/s. Thus the observed pass transition is between **275 and 280 kN** *under this exact controller, geometry and timestep*. It is not an engineering minimum rating or an optimization of hardware.

## External cross-check and unresolved physics

NASA 42 replay of the generalized laboratory's realized 300 kN commands: 700 samples, maximum attitude difference approximately **6.99e-6 degrees**, with full tensor inertia and the same frozen-mass assumptions. This independently checks rigid-body integration but does not independently certify the controller.

Wayfarer RCS exhaust velocity, propellant feed and real uprated-hardware mass are still unqualified. **RCS fuel use is unknown, not zero.** Results report null total propellant consumption wherever unspecified RCS fires; the measured scalar thruster impulse remains available for conditional calculations.

Other excluded physics: RCS nozzle structural loads, plume interactions, tank dynamic redistribution, sensor/measurement errors, material limits, thermal effects, valve hardware, and engine installation feasibility.

## Repeat the experiments

```bash
cd /home/ubuntu/wayfarer_flight_lab_scratch_20261026
.venv/bin/python rcs_reference_validation.py
.venv/bin/python rcs_design_variations.py
.venv/bin/python rcs_threshold_scan.py
.venv/bin/python lab42.py reference_fixed300_pitch reference_fixed300_pitch
.venv/bin/python -m unittest -v test_flightlab
```

Grounded evidence:
- `lab_results/rcs_reference_summary.json`
- `lab_results/rcs_reference_comparison.json`
- `lab_results/rcs_design_variations.json`
- `lab_results/rcs_threshold_scan.json`
- `lab_results/reference_fixed300_pitch__reference_fixed300_pitch_42.json`
- `rcs_regression_after_actuator_fix.log`

**Conclusion:** The original 24×300 kN fixed coarse RCS experiment is correctly reproduced in the generalized scratch laboratory. The earlier eight-engine-only altered-mount failure was a different design and was not evidence against the original configuration.

## Generalized gimbal reproduction completed, 27 October 2026

The earlier statement that the eight-added-gimbal architecture had not been
reproduced is now superseded. `wayfarer_gimbal_reference.json` preserves the 32
original fixed 25 kN thrusters and adds eight 300 kN two-axis nozzles. The common
solver propagates actual angles with 0.1 s lag, 30°/s per-axis slew, ±25° mechanical
limits, and reallocates the full wrench at every changed direction. The 10/12/14 s
fail/pass/pass pattern and numerical histories reproduce the saved Astra study;
see `sol_results/gimbal_reference_comparison.json` and `CODEX_SOL_HIGH_RESULTS.md`.
Prepositioning remains excluded and hardware mass/feed remain unqualified in this
historical comparison. A separate neutral-start fixture includes all steering time;
Scout fixtures use separately declared hypothetical masses and propellant.
