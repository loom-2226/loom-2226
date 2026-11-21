# Relational back-reaction: a conservative toy exchange mechanism
ALL bodies. ALL sponsors. 2026-2226.

**Status:** NON-CANON physics.
- The hypothesis is SOL's (relational back-reaction, response kernel G_R).
- Claude added the test refinements, at kT's request. Run 2026-11-21.
- No canon, hardware or mass changes; kT decides.

**Files:**
- `relational_backreaction.py/.json`.
- `backreaction_figure.py` → `relational_backreaction.png`.

## Model (1D, v ≪ c)
- **Shuttle:** its real inertial mass m (61 t). There is deliberately no separate "relational mass", so the conserved quantities are the physical ones (SOL's own caveat).
- **Relational medium:** modes a, each with inertia μ_a, rest velocity u_a relative to the local body frame, and coupling share w_a (Σ w_a = 1).
- **M2 control:** a translation-invariant internal force pair, +F on the shuttle and −w_a·F on each mode.
- **Actuator power:** P = Σ w_a·F·(V − ξ̇_a). This depends only on relative velocities, so it is Galilean-invariant.
- **Consequence:** total momentum is conserved and the centre of mass moves uniformly, by symmetry, and both are checked numerically.

## Results
| Test | Result | Verdict |
|---|---|---|
| 200 m start-dash-stop (smooth, peak 125 m/s, 3 s) | The shuttle ends at rest exactly 200 m away; momentum drift 0 | **VIABLE (toy)** |
| Centre of mass | The medium keeps a real compensating shift −m·ΔX/μ. That is 2×10⁻¹⁸ m at Earth-scale μ, and 122 m if μ ~ the shuttle's mass. | **Conserved**; no reversal or reset needed |
| Net energy of a symmetric dash | 0 for every medium | — |
| Transient energy of a symmetric dash | ½·m·V² (0.48 GJ, peak power 0.6 GW) for a local medium; **±227 GJ** for Sun-like u = 29.8 km/s; **±2.8 TJ** for cosmic u = 370 km/s | the medium's rest frame sets the swing |
| Hover 20 s with a medium moving at u | **harvests m·g·u**: 0 for local; 18 GW for Sun-like; 221 GW for cosmic | moving medium = energy source |
| 1 km lift by field, ordinary fall with harvest | net gain 0 (local); **+357 GJ** (Sun-like); **+4.4 TJ** (cosmic) | same |
| Medium inertia sweep | a large μ makes the recoil invisible, and the transient falls to ½·m·V² | large μ required |
| Wayfarer, same law | a 200 m dash needs a 9.1 GJ transient, more than the 2 GJ bank. A 0.268c cruise moves (γ−1)·m·c² ≈ **4×10²¹ J** into the ship and back. | the relational sector must be the transient energy store (SOL's reading of foundations §8) |

## What the toy establishes, and what it doesn't
**Establishes:**
- A translation-invariant exchange with a relational medium is a **mathematically viable, conservative** way for a Weave dash to start, travel, stop and remain displaced.
- It needs no designated celestial partner, no radiation and no scar.
- The medium simply keeps the record.

**Does not establish:**
- That M1's relational sector has these degrees of freedom.
- The response kernel G_R.
- Where the transient ½·m·V² is stored.
- How actuator energy maps to the field.

**Requirements on G_R (derived from the toy):**
1. **Large effective inertia μ,** so the medium's recoil is unobservable.
2. **Locally anchored rest frame.**
   - Holding or lifting against a medium that moves at u relative to the local body harvests m·g·u.
   - To keep that harvest below even the lift work of a 1 km / 20 s lift, the effective u (Σ w_a·u_a) must stay under **~50 m/s**.
   - In terms of non-local share, that means **under ~2×10⁻³** for a Sun-like component and **under ~1×10⁻⁴** for a cosmic one.
   - For negligible harvesting, much smaller.
3. **A transient energy store.** Fast or long dashes move ½·m·V² (or (γ−1)·m·c²) into the ship and back. Either the onboard bank holds it, which limits dash speed, or the relational sector does, which is undetermined.

## Synthesis with BMD-1
- BMD-1 H1 found that tidal weighting can **select** a local partner while respecting the equivalence principle, but cannot **source** the force (`bmd1_tidal_force`).
- Relational back-reaction supplies the missing source: **the M1 medium carries the momentum, and local mass structure anchors its rest frame.**
- **Candidate exchange law (one sentence, not adopted):**
  - The Mc actuator exchanges momentum with the M1 relational medium.
  - The medium has very large effective inertia, and its rest frame is the local inertial frame set by nearby mass (tidally weighted).
  - It stores the transient kinetic energy of Weave motion and returns it on deceleration.

**Consequences, reported and not restricted:**
- Exhaust-free hover and lift near bodies, at the cost of the work done.
- Net-free symmetric dashes.
- No harvesting.
- In deep space, propellant-free velocity change at the cost of the change in kinetic energy in the local heliocentric inertial frame: a setting-scale change.
- Earth's rotation (465 m/s at the equator) is horizontal, so it does not affect vertical support.

## Smallest next step
Test whether the candidate exchange law above closes **both** Wayfarer's canon NORMAL cruise and the shuttle's dash **under one rule**, at the level of this toy:
- one medium;
- tidal anchoring;
- the transient store located in the relational sector.

If it does, it is a candidate foundational improvement for kT. If not, the failing requirement names the missing permission.

## SOL review of 4b0afba: corrections accepted
1. **The toy pushed the shuttle conventionally.**
   - Correct: its force acted on the shuttle as a whole, and crew inertiality was not shown.
   - Peak acceleration was 128 m/s² (13 g), not 70–80.
   - Addressed by the bridge test below.
2. **A moving medium is a reservoir, not a pump.**
   - Correct: the reservoir loses exactly u·I of kinetic energy, so the harvest is conservative.
   - **The "50 m/s / 2×10⁻³ / 1×10⁻⁴ anchoring" figures are withdrawn as requirements.** They were thresholds chosen to keep harvesting below the lift work.
   - Reported instead as a consequence: if the medium is not locally anchored, Weave operation near bodies taps the reservoir's relative motion. That is a setting-scale energy source, and kT decides whether LOOM has it.
3. **Wayfarer's (γ−1)·m·c² ≈ 4×10²¹ J** is a kinetic-energy comparison, not a demonstration of Metric cruise. The toy is non-relativistic.

## Bridge test: shuttle moved by geometry, relational mode keeps the books (`weave_bridge.py/.json`, `weave_bridge.png`)
**Setup:**
- A deformable ship: a 59 t hull, 1 t crew on a seat spring, 1 t cargo on a tie-down.
- It is carried through the same 200 m, 125 m/s dash by the moving shift geometry (R = 10 m, δ = 2 m).
- Its equations of motion come from the proper-time action: geodesic transport plus springs.

**Comparison case:** the same hull trajectory produced by an ordinary force on the hull.

| | Geometric (Weave) | Ordinary force |
|---|---|---|
| Hull final position | 199.98 m, at rest | 200 m |
| Peak felt by crew / cargo | **0.011 g / 0.033 g** | **13.1 g / 13.1 g** |
| Internal strain | 1.5×10⁻¹⁰ m | — |

**Verdicts:**
- **Crew inertial while spacetime moves the ship: DERIVED.** Every part of the ship rides the shift together.
- The ~0.01–0.03 g residual is the wall-profile gradient across the 10 m domain (f(4 m) = 0.9975). It is derived, and it shrinks with a flatter plateau.
- **Momentum and centre of mass are closed by the relational mode** (residual shift −2×10⁻¹⁸ m at Earth-scale μ), **IF the wall hands the payload's momentum change to the mode. ASSUMED.**

**What remains is that single link:** a field model in which the wall's stress-energy actually transmits momentum into the relational sector.
- Geodesic transport is derived.
- The exchange bookkeeping closes.
- Only the coupling between wall and relational sector is assumed.
