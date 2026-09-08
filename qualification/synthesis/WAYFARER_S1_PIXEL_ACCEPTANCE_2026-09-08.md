# Wayfarer S1 Pixel Offline Acceptance — 2026-09-08

Classification: RESEARCH / QUALIFICATION / NON-CANON / NON-PRODUCTION

Source branch: `research/physical-design-synthesis-wayfarer-s1-2026-09-08`

Pinned source commit tested on Pixel: `af5e0f942a91e51a70a78b9fdee25f8d9baf03d2`

Platform: Pixel 10 Pro, Android / Termux

Network condition for acceptance run: Wi-Fi OFF, mobile data OFF

Acceptance entrypoint: `qualification/synthesis/wayfarer_s1_offline_acceptance.py`

## Observed result

```text
WAYFARER_S1_OFFLINE_ACCEPTANCE = PASS
PROCEDURAL_LAYOUT_FEASIBILITY = PASS
candidate_id = CAND-5719E3F3251DE6E25FDF
seed = 2226
examined = 203
legal = 203
relational_x_m = 26.0
launch_x_m = 21.75
tank_x_m = 26.5
mass_kg = 1158500.0
center_of_mass_m = [26.99892101855848, -3.7682991527924517e-17, 0.14812257229175657]
unresolved_inertia_mass_fraction = 0.8955545964609408
flight_dynamics_authority = false
wayfarer_flight_inertia_qualified = false
canon_changed = false
production_shipclasses_changed = false
```

## Gate disposition

`PROCEDURAL_LAYOUT_FEASIBILITY = PASS`

Desktop deterministic acceptance: PASS.

Pixel offline deterministic acceptance: PASS.

Portable deterministic reproduction: PASS for the S1 acceptance payload above.

This closes the S1 procedural-layout feasibility gate only. It does **not** qualify full Wayfarer flight inertia, does not change canon, and does not mutate production SHIPCLASSES.

Explicit surviving boundaries:

- `WAYFARER_FLIGHT_INERTIA = NOT QUALIFIED`
- `CANON = UNCHANGED`
- `PRODUCTION_SHIPCLASSES = UNCHANGED`
- `FLIGHT_DYNAMICS_AUTHORITY = false`

The unresolved centroidal-inertia mass fraction remains `0.8955545964609408`; S1 therefore remains a reduced-layout feasibility result, not a full vehicle inertia authority result.

## Next governed step

Proceed to S2 only: compare the generated S1 candidate against the hand-authored Wayfarer baseline. Do not promote OpenMDAO/external optimizers, orbitals, production SHIPCLASSES, Navigator/GIS/HUD physics, or Wayfarer flight inertia authority from this result.
