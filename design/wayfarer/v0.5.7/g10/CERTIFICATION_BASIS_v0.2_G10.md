# Certification basis v0.2: G10 (PROPOSED)

ALL bodies. ALL sponsors. 2026-2226.

NON-GOVERNING. Class: engineering. This file replaces the G10 section of
`rev5/CERTIFICATION_BASIS_v0.1.md` and nothing else. Sol needs to agree it
before it governs the Wayfarer certification run.

## Why G10 changes

G10 v0.1 asked Navigator to fly E1, FR-01B-R and MV-01 to an arrival remass
of at least 50 t. That cannot be met yet, for three reasons:
- There are no executable mission fixtures.
- Navigator cannot import the ship card.
- CANON II §20 bars exact remass and Δv outputs until there is a calibrated
  U^M_gamma and a terminal solver.

v0.2 tests what the ship's propulsion systems can do with the code that
already exists on main (see `G10_SOURCE_MAP.md`). The Navigator missions
become follow-up validation and no longer gate certification.

## G10 Flight dynamics: RCS, torch, Metric, Loom

Run by `g10/g10_flight_dynamics.py`, which `certify.py` calls. The tests
import main's `src/` modules; they do not copy them.

### C. Card conformance
- The card names the geometry sha256 it was made from.
- The card's mass, CG and inertia match the geometry in every state
  (≤ 1% relative).
- The card's torch exhaust velocities and thrust by mode match the working
  card, `src/wayfarer_torch_mode_cards.py` (≤ 1%).

### R. RCS
- 180° slews on roll, pitch and yaw settle in every state, within 240 s.
  - Main's controller and gates are used: 0.25°, 0.05°/s, 2 s hold.
  - Inertia and axis torque come from rev 5.
- 180° slews on all axes still settle with any one cluster out (state S2).
- Attitude is held against the torch's disturbance torque in every state and
  mode. The disturbance is thrust × lever × sin(trim + 0.5° error). It is
  held by the RCS, by declared torch thrust-vector authority, or both.
- Translation on all three axes meets main's response law (0.16 s⁻¹) at
  main's test velocities.

### T. Torch
- A time-stepped burn of the full usable remass in every mode:
  - integrated Δv agrees with the rocket equation within 0.1%;
  - peak acceleration stays within the crew cap (4 g) and the structural
    rating (5 g);
  - trim stays within the G3 limit as the CG migrates from S1 to S4.
- Burns longer than 2 h 45 min are split by coast breaks ([V2 6113]). This is
  reported, not limited.

### M. Metric
- The mode sequence is valid: prep, ramp, transport, collapse, NRE
  relaxation.
- Going from torch to Metric without a coast is refused.
- The cold load in every mode is within the cryoplant class.
- G4 rejects the heat of every mode.
- Ramp times are within canon's 10-30 s.
- **Not computed:** Metric Δv and remass (CANON II §20).

### L. Loom
- The sequence is valid: Metric collapse, NRE relaxation, Loom formation,
  translation, arrival.
- Going directly from mid-field Metric to Loom is refused (not crew-rated).
- The E1 configuration lock (DOCKED / FREE / STOWED) is reachable.
- Torch Δv available at arrival, above the 50 t reserve, is reported.
- **Not computed:** Loom domain fit (PR #356, INDETERMINATE_NOT_CERTIFIABLE)
  and the natural transport map.

### Follow-up validation (not gating)
- E1, FR-01B-R and MV-01 flown in Navigator, once fixtures, a card import and
  the §20 solver exist.

## First run on rev 5 (geometry ed692f90...): 20 of 24 checks pass, G10 FAIL

| Check | Result | What it means |
|---|---|---|
| C: card torch thrust | 122% off | The card assumes a constant 11.361 TW. The working card gives 5.11 TW (ECON) to 12.78 TW (HARD, LIMIT). |
| R: RCS holds against torch error | 18.7 vs 3.1 MN·m | RCS cannot hold against the torch error (worst case S2 HARD, 47.8 MN). |
| R: torch TVC authority | not declared; needs 0.85° | The magnetic nozzle must steer the thrust line. |
| R: translation | x: 0 kN | The rev 5 RCS has no axial thrusters. |

These are the propulsion fixes for kT to decide:
1. Regenerate the card's torch block from `MODE_CARDS`.
2. Declare at least 1° of torch thrust-vector authority. This is a new
   declared item.
3. Add axial (±x) RCS thrusters (rev 6).
