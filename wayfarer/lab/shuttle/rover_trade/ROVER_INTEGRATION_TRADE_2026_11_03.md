# Shuttle v1 rover-integration trade (2026-11-03)

ALL bodies. ALL sponsors. 2026-2226.

**NON-CANON research trade.** It scores where the rover goes, using the merged sizer's
core-mass ranges (`../shuttle_inputs.json`, main `7c6b9b4`). It does not change the sizer,
Wayfarer, or canon.

## Decision (kT, 2026-11-03)

- **Baseline into Wayfarer: A, 3.8 m hull, pod inside, 2.5 m pod, 3 crew.** Kept.
- Belly rover (C) with 4 crew is the upgrade path, if a fourth seat is judged worth about
  2.5 t of reserve and roughly a 40% chance of breaking the 5 t floor.

## Options

- **A inside:** pod rover rides inside the hull, behind a side door with a ramp.
- **B side plug:** the rover's outer shell is a hull section that detaches sideways. No door or ramp.
- **C belly rover:** the rover forms the middle of the belly, and its wheels are the main landing
  gear. It drives out from underneath. No door, ramp or main gear.

## Result (run `fddf60f0`, 200,000 uniform samples)

| Option | Core dry p5 / mid / p95 (t) | Keeps floor | Reserve at mid (t) | Bay exit | Fits | Note |
|---|---|---|---|---|---|---|
| A 4.3 m inside, 4 crew | 30.10 / 34.56 / 39.03 | 44.6% | 4.62 | FAIL | yes | PR #460 preflight: longerons, strakes and hot fins fail the 0.5 m exit path |
| A 3.8 m inside, 3 crew | 26.87 / 30.89 / 34.91 | 90.6% | 8.29 | PASS | yes | certified 0.5 m clearances unchanged |
| A 3.8 m inside, 4 crew | 28.60 / 32.91 / 37.21 | 67.9% | 6.28 | PASS | NO | pod + chassis + wheels ~3.62 m stack exceeds ~3.6 m inside |
| B 3.8 m side plug, 4 crew | 29.13 / 33.43 / 37.74 | 60.9% | 5.75 | PASS | yes | wheels stow at the hull line |
| C 3.8 m belly rover, 4 crew | 29.27 / 33.57 / 37.87 | 58.8% | 5.62 | PASS | yes | rover wheels are main gear; wheels stow at the belly line |
| C 3.8 m belly rover, 3 crew | 27.54 / 31.55 / 35.57 | 84.9% | 7.63 | PASS | yes |  |

"Keeps floor" is the share of samples whose core dry mass leaves Wayfarer's reserve at or above
5 t (start 11.284 t, replacing the 27.9 t shuttle). The sampling is independent uniform over each
range. It is not the sizer's balanced grid, so the fractions differ slightly from Stage 1's A2.

## Findings

1. A at 3.8 m with 3 crew is the lightest and keeps Wayfarer's certified bay exactly.
2. Integrating the rover does not save mass. Removing the door, ramp and main gear saves about 0.7 t,
   but rover landing loads, wheel doors in the TPS, the TPS seam, latches and small legs add more.
3. Integration buys crew space. In B and C the wheels stow at the hull line, so a 2.8 m 4-crew pod
   fits inside 3.8 m. That cannot be done inside (A).

## Assumptions (all in `rover_trade_inputs.json`)

Pod shell mass scales with diameter cubed, fittings with diameter squared. Hull structure and base
TPS scale with hull diameter. The base core TPS is 2.0-3.5 t (kT R4). The shares of door, ramp, main
gear and kneel within the landing-gear line, and the mass added for each option, are Claude
estimates. The 3.62 m stack and ~3.6 m inside diameter that rule out a 2.8 m pod inside are
geometry estimates, not a measured layout.

## Run

`python3 rover_trade.py` (numpy). Run identity = SHA-1 of both input files.
