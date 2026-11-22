# Weave geometry comparison: lapse gradient vs zero-expansion shift (NON-CANON)

ALL bodies. ALL sponsors. 2026-2226.

Prototype lane, 2026-11-21. Responds to Sol's review of 5871508: is the atmospheric disturbance fundamental to conservative relational propulsion, or a property of the chosen geometry? No silence requirement, no gameplay restriction, no canon change.

Code: `weave_geometry_compare.py`, `geometry_figure.py` → `weave_geometry_compare.png`. Data: `weave_geometry_compare.json`, `weave_geometry_compare_series.json`, `weave_geometry_compare_ship_extra.json`.

> **Sign correction (after 2027261).** The shift-case hull code used `ẇ = +w ∂ₓβ`. From `L = ½(ẋ−β)²` the correct form is `ẇ_i = −w_j ∂_i β_j`. The clear-wall rows barely change. The wall-cuts-hull row changes completely (2.3 g → 158 g). Air results are unaffected (air starts with w = 0).

> **Correction (outing 3, `outing_landing.py`, 2026-11-22).** The lapse "wake" here (20–45 MJ, ×50 compression) is an artefact of collisionless air. A lapse-type field exerts the same acceleration on all air, so on uniform air its force is a gradient that pressure absorbs. With linear compressible air, the same R 15 / d 2 lapse dash leaves about 0.2 kJ, with a peak air speed of 0.75 m/s and about 1.8 kPa quasi-static pressure. The real distinction:
> - the **shift carries its air** with the hull (no airflow at the hull, air displaced);
> - the **lapse field leaves the air in place**, and the hull flies through it with ordinary drag, wake and (if supersonic) boom.
>
> The hull and crew results below are unaffected.

## 1. Setup (identical for both)

- **Geometry:** axisymmetric 3D (x along the track, ρ radial).
- **Shuttle:** the same 20 m axial hull (11 nodes), crew seat and cargo mount as `weave_finite.py`, on the axis.
- **Trajectory:** the domain centre X(t) follows the same 200 m / 3 s quintic. It is commanded in both cases (a controllability demo).
- **Profile:** `F(r) = ½[tanh((r+R)/d) − tanh((r−R)/d)]` for both.
- **Air:** sea-level, 1.2 kg/m³, as collisionless parcels on a 0.5 m meridional lattice (−30…240 m × 0…25 m, 6.6 t of air per metre of track within 25 m).

| | Lapse gradient | Zero-expansion shift |
|---|---|---|
| Field | scalar `Φ = (x−X) F(r)`, matter accel `a(t) ∇Φ` | Stokes stream function `ψ = ½ V ρ² F(r)`; `β_x = V(F + ρ²F'/2r)`, `β_ρ = −V ρ (x−X) F'/2r`; `∇·β = 0` exactly |
| Matter law | force (from the translation-invariant action) | slow geodesic, N = 1: `L = ½(ẋ−β)²` ⇒ `ẇ = (w·∇)β`; matter starting at rest keeps w = 0 ⇒ `ẋ = β` (DERIVED). Perturbations obey `ẇ_i = −w_j ∂_i β_j` (sign corrected; see note) |
| Reaction | to the relational mode via A3, from the action | to the relational mode via A3, as explicit bookkeeping (the shift action's own Noether charge omits carried matter) |
| Collisionless air | not a fluid solution: it shell-crosses, and real air would shock | exact perfect-fluid solution: incompressible, so pressure stays uniform |

## 2. A derived constraint on any localized field

- **Lapse.** Φ is a localized scalar, so `∫ ∂ₓΦ dx = 0` along every line. A uniform interior push therefore requires reverse-force walls. The peak wall strength is `max|∇Φ| ≈ 2.6–11.5` times the interior value, scaling about as R/(2d).
- **Shift.** The interior flux has to return around the domain. Peak backflow is `max|β|/V ≈ 1.1–5.5`, scaling about as R/(4d).
- **Correction.** This corrects the 1D lapse profile of 5871508, which was not localizable.

## 3. Results

**Hull and crew**

| R / d (m) | crew peak g, lapse / shift | hull axial kN, lapse / shift | stop (m), lapse / shift |
|---|---|---|---|
| 15 / 2 | 0.92 / 0.018 | 440 / 5.7 | 204.9 / 199.6 |
| 12 / 0.5 | 0.086 / 0.0008 | 45 / 0.20 | 200.2 / 200.0 |
| 12 / 2 | 31 / **158** | 3600 / **14,300** | 133 / **61** |
| 20 / 2 (ship only) | 0.0013 / 0.0001 | 0.28 / 0.025 | ≈ 200 / ≈ 200 |
| 15 / 0.5, 25 / 2 (ship only) | ≈ 0 / ≈ 0 | ≈ 0 / ≈ 0 | ≈ 200 / ≈ 200 |

**Air**

| R / d (m) | peak air KE (MJ), lapse / shift | air KE left (MJ), lapse / shift | air momentum left (N·s), lapse / shift | peak air speed (m/s), lapse / shift | max density ratio, lapse / shift |
|---|---|---|---|---|---|
| 15 / 2 | 96 / 171 | 45 / 0 | 1.0e6 / 0 | 152 / 181 | 62 / ≤ 3.5 (noise floor) |
| 12 / 0.5 | 60 / 272 | 20 / 0 | 4.5e5 / 0 | 144 / 690 | 47 / ≤ 3.3 (noise floor) |
| 12 / 2 | 43 / 72 | 21 / 0 | 5.1e5 / 0 | 145 / 136 | 50 / ≤ 2.5 (noise floor) |

Notes:
- **Shift density.** The shift density is exactly 1 analytically (∇·β = 0). The binned value is a discreteness floor from 2 m cells resolving sheared filaments.
- **Lapse shell crossing.** In the lapse case the parcels shell-cross, so real air would form shocks there. The collisionless numbers overstate compression but not the order of the momentum and energy delivered.
- **Displacement.** The shift leaves the air at rest but moved:
  - the start-of-dash air bubble is set down 200 m along the track;
  - near-axis air along the path drifts forward by up to about 150 m.
  - 137–309 t of air is moved by more than 1 m.

## 4. Verdicts

| Claim | Verdict |
|---|---|
| Atmospheric disturbance is fundamental to conservative relational propulsion | **INCONSISTENT** with the shift result: an equally conservative geometry leaves no wind, no residual air momentum and no compression |
| Lapse carriage leaves a wind and shocks in air | DERIVED within this model (20–45 MJ and 0.5–1e6 N·s left in the air; shell crossing) |
| Zero-expansion carriage is silent in the sense of no residual motion and no compression | DERIVED for collisionless, inviscid air, which is an exact fluid solution here |
| Shift lends the air a large transient KE (72–272 MJ) and takes it back | DERIVED; recovery assumes the field returns it losslessly (UNDETERMINED) |
| Shift backflow in a thin wall reaches about 5.5 V (690 m/s at V = 125 m/s) | DERIVED; viscous dissipation ESTIMATE: η σ² × wall volume ≈ 0.1–0.2 MJ, negligible; acoustic and real-gas response not modelled (UNDETERMINED) |
| For the same domain, shift is gentler on the hull | DERIVED **only when the wall clears the hull**. If the wall cuts the hull, shift is worse than lapse: hull strain in the wall grows exponentially (ẇ = −w ∂ₓβ) and the hull slips out of the domain (R 12 / d 2: 158 g, stops at 61 m) |
| Silence in a real atmosphere | still UNDETERMINED beyond the inviscid, collisionless idealization |
| Either geometry can be sourced (A1, or its shift analogue) | UNDETERMINED |
| A3 reaction channel | ASSUMED; imposed as bookkeeping in the shift case |

## 5. What this changes

- Both geometries stay open, as Sol asked. The physics now separates them clearly:
  - **lapse** pushes matter, so it leaves a wake;
  - **shift** carries matter along geodesics, so it leaves only a displacement.
- The shift's price is a large *transient* loan of air kinetic energy and a fast return flow in the wall. Thick walls keep the return flow slow but need more clearance from the hull. Thin walls do the opposite.
- The momentum asymmetry is now the sharpest open physics question. The shift's Noether charge omits carried matter, so in the shift case A3 is pure bookkeeping, not dynamics. Before the shift geometry can be preferred, it needs its own translation-invariant action that includes carried matter, or an M1 argument for where the carried momentum physically resides.
