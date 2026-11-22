# Weave finite-domain check of A1 (NON-CANON)

ALL bodies. ALL sponsors. 2026-2226.

Prototype lane, 2026-11-21. Responds to Sol's review of 586f1a4. No canon, hardware or mass changes.

Code: `weave_finite.py`, `finite_figure.py` → `weave_finite.png`. Data: `weave_finite.json`, `weave_finite_series.json`.

> **Correction (WEAVE_GEOMETRY_COMPARE_2026_11_21.md).** The 1D profile used here (Ψ' = f) has different asymptotes on each side, so it cannot be localized in 3D. A localized scalar (lapse) field with a uniform interior push must have reverse-force walls (∫∂ₓΦ dx = 0 along any line). In 3D the lapse hull loads are larger than reported below (R 15 / d 2: 0.92 g, not 0.018 g), and the path-wide stirring pattern was an artefact; disturbance concentrates where the domain accelerates and decelerates. Sol also qualified the "violent in atmosphere" claim: that was for this mechanism only, and 1D collisionless.

## 1. Sol's corrections accepted

- **Three achievements, kept separate.** Inertial carriage, conservation and self-contained propulsion are different claims. 586f1a4 shows the first two for an ideal field. It does not show the third: `G(t)` is commanded as the target acceleration and the wall controller supplies the reaction. The result is a controllable conservative mechanism, not a derived capability.
- **The miracle is not "entirely" A3.**
  - A1, a switchable roughly 13 g uniform lapse gradient, needs a physical source. The ADM form admitting N does not show that Mc hardware can make it.
  - A2 is open.
  - A3 is a candidate M1 interaction, not a derived one.
  - `WEAVE_COUPLED_2026_11_21.md` §5 is corrected to match.
- **The near-zero crew load was built in.** The ideal uniform field guaranteed it. This file tests whether it survives finite geometry.

## 2. Model

The action is the same as `weave_coupled.py`, but the carriage potential now has a profile:

`V = Σ m_i G(t) Ψ(x_i − X_d)`, with `Ψ' = f` and `f(u) = ½[tanh((u+R)/d) − tanh((u−R)/d)]`

That gives a flat interior of radius R and a wall of thickness d. Each body feels `−m G f`, and the wall takes the equal and opposite force, so translation invariance and exact momentum still hold.

- **Ship:** a 20 m hull of 11 axial nodes with EA-type springs (1.75e9 N/m per 2 m), a crew seat at +3 m and a cargo mount at −4 m.
- **Ambient:** 1 kg test parcels every 2 m from −40 to +260 m. They represent loose on-path matter, with no collisions (1D).
- **Coupling and trajectory:** the wall–mode coupling (A3) is unchanged, and so is the 200 m / 3 s quintic.

## 3. Results

| R (m) | wall d (m) | f at hull ends | crew peak (g) | hull axial peak (kN) | hull final (m) |
|---|---|---|---|---|---|
| 30 | 2 | 1.00 | 6e-9 | 2e-6 | 199.98 |
| 15 | 2 | 0.993 | 0.018 | 3.7 | 199.71 |
| 12 | 2 | 0.88 | 0.32 | 67 | 195.06 |
| 12 | 0.5 | 0.9997 | 8e-4 | 0.2 | 199.97 |

Momentum is exact to rounding in every case. ΔE − W ≤ 11 kJ, which is integration error.

**Carriage (DERIVED within the action).** Inertial carriage survives finite geometry if the wall clears the hull. Internal load scales as `G·Δf` across the structure. The working rule is a clearance of 2 to 3 wall thicknesses beyond the hull ends:
- With clearance, the crew feel thousandths of a g.
- When the wall cuts into the hull, the structure takes the difference: 0.3 g at the crew, 67 kN in the hull, and the ship falls 5 m short of its commanded stop.

**Ambient matter (DERIVED within the action).** The field cannot tell the shuttle from anything else, so it acts on all matter inside the domain.
- Matter inside the domain at the start is carried and set down 200 m away, just like the crew.
- Matter along the path is overtaken by the domain. It is left moving at up to about 78 m/s: forward over the first half of the path, backward over the second.
- Every parcel within 2 to 3 wall thicknesses of the domain's start or end positions, or anywhere on the path between them, is moved.

**Energy.** The net actuator work is no longer about zero. It is about the kinetic energy left in the swept matter: 30 to 95 kJ per 0.5 kg/m line. The lent-and-recovered 484 MJ is unchanged.

**3D order of magnitude (ESTIMATE).** Scale the parcels to sea-level air filling the domain cross-section (1.2 kg/m³ × πR²). The air kinetic energy left behind is then about 40 MJ (R = 12 m), 90 MJ (R = 15 m) and 700 MJ (R = 30 m). This ignores pressure and collisions, which a 3D model would need, and it is a gale of up to about 78 m/s along the path.

## 4. Verdicts

| Claim | Verdict |
|---|---|
| Near-zero crew loading survives a finite domain | DERIVED in this action, if the wall clears the hull by about 2–3 d |
| A wall that cuts the hull loads the structure as G·Δf | DERIVED |
| A carriage field entrains and stirs all on-path matter | DERIVED: the field is universal by construction (A1) |
| The dash is near-free in atmosphere | INCONSISTENT with A1: the swept air takes tens to hundreds of MJ and leaves a wind |
| The dash is near-free in vacuum | holds if lent energy is recovered losslessly (UNDETERMINED) |
| A1 can be generated by M2 hardware | UNDETERMINED: no source or cost model yet |
| A3 is an M1 interaction | candidate, ASSUMED |

## 5. Consequences

- The same universality that keeps the crew inertial also grabs the air. The weave is quiet in vacuum and violent in atmosphere: it carries a bubble of air and leaves a wind along the track.
- A tighter domain reduces the swept mass about as R², but has to keep the wall-to-hull clearance. That favours a small craft, consistent with the scale privilege, without adding any restriction.
- The two open questions are now cleanly separated:
  1. Can M2 source a finite, switchable lapse-gradient domain at about 13 g? (A1: existence, magnitude, cost.)
  2. Can M1 carry its reaction? (A3.)
