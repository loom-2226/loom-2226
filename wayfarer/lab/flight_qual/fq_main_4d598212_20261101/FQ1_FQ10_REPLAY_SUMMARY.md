# Wayfarer FQ1–FQ10 current-main numerical replay | 2026-11-01

**ALL bodies. ALL sponsors. 2026–2226.**

**Authority:** `loom-2226/loom-2226` main commit `2d9e7a18e49b4cf409448d06e22de10e1af602b4` at replay bootstrap.
**Exact geometry SHA256:** `4d598212aeb46fab14b326a6023bb6d55e7d584599d91fe821ef8a2f2d837331`.
**Classification:** engineering replay evidence only; no model/source changes and no hardware flightworthiness, Navigator or Metric qualification.

## FQ1–FQ10 disposition

| Gate | Verdict | Current-geometry evidence |
|---|---|---|
| FQ1 | **PASS** | 6/6 full + half, 180° pitch/roll/yaw. |
| FQ2 | **PASS** | 48/48 full + half, one RCS cluster unavailable. |
| FQ3 | **PASS** | 12/12 full + half, ±X/Y/Z translations. |
| FQ4 | **PASS** | 12/12 full + half, torch modes and numerical acceleration/trim bounds. |
| FQ5 | **PASS** | Torch draws 0 kg at the 5 t RCS floor; three successive flips use 1052.619 kg and leave 3947.381 kg. |
| FQ6 | **PASS** | 0.2 s versus 0.4 s: 39 full + 39 half + 15 empty cases, 0 verdict differences; eight 5 t reserve-pair checks pass. Empty propulsion inhibits as expected. |
| FQ7 | **PASS** | RCS draws unprotected ring-fenced water only; 50 t protected water remains separate; ledger residual -8.19e-12 kg. |
| FQ8 | **PASS** | CRUISE consumes 245,000 kg, stops with 5,000 kg RCS floor, leaves separate 50 t protected water untouched. |
| FQ9 | **PASS** | Single state burn–cut–flip–brake, sum 1,165.172 kg; mass ledger residual 2.30e-09 kg. |
| FQ10 | **PASS, CONDITIONAL** | Stuck TVC mitigated CRUISE peak 0.110°, HARD 0.626°; both throttle then cut; active A+Z cluster-loss and stuck-on nozzle bounded. |

## Specific numerical observations

- **FQ5/FQ7:** torch inhibited at the 5 t RCS water floor. Three pitch/roll/yaw manoeuvres in one continuous reserve state consume **1052.619079 kg** and leave **3947.380921 kg**. The separate 50 t protected water is not consumed.
- **FQ6:** full remass 39/39, half remass 39/39, empty remass 0/15 propulsion cases expected inhibited at both 0.2 s and 0.4 s; **93 paired cases, zero changes**. Separate eight-case 5 t floor parity passes.
- **FQ8:** CRUISE torch consumes **245000.000 kg**, retaining exactly **5000.000 kg**.
- **FQ9:** same-state burn–cut–flip–brake fuel sums to **1165.172432 kg**, with mass-accounting residual **2.296e-09 kg**.
- **FQ10:** CRUISE stuck-TVC peaks **0.109550°** and HARD **0.625979°** when mitigated; both detect, throttle and then cut under the 0.20 s ideal detection setting; no-response controls lose control. Active cluster-out and stuck-on single nozzle likewise bound attitude numerically.

**FQ9 warning:** A near-zero RCS mass-flow allocation makes the existing `tank_mass/(rdot × dt)` limiter emit a floating-point overflow warning; it has no mass-ledger consequence in this run (residual 2.296e-09 kg), and is not a physical feed-system qualification.

## Preserved outputs and non-duplication

- `FQ5.json`, `FQ6_PARITY.json`, `FQ6_RESERVE_PARITY.json`, `FQ7.json`, `FQ8.json`, `FQ9.json`, `FQ10.json`, and `FQ10_SUPPLEMENTAL.json` are fresh current-geometry outputs.
- The four `fq_matrix_*.json` artifacts here preserve the newly run 0.4 s full/half and 0.2/0.4 s empty cases. Each has the baseline main commit and exact geometry hash stamped.
- Existing main-committed `../fq_house_power_20261101/fq_matrix_full_0p2_all.json`, `fq_matrix_half_0p2_all.json`, and `FQ1_FQ4_CURRENT_SUMMARY.json` supply the current-hash fine-step cases. They are referenced rather than copied.
- `FQ1_FQ10_READONLY_REPORT.json` provides the combined machine-readable verdict and full numeric observations.

**Boundary:** numerical rigid-body, propellant and conditional safing evidence only. RCS pulse-power/heat coupling, actual fault detection and actuator response, long-duration torch thermal closure, Metric arrival, and Navigator remain open.

**Repository change scope:** dated evidence folder only. Flight physics, fixtures, model source, original test cases, and qualification thresholds are unchanged.
