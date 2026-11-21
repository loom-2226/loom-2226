# SOL — Finite Weave dash: metric, stress-energy and closure boundary
ALL bodies. ALL sponsors. 2026–2226.

**NON-CANON physics exercise. No hardware, mass, canon or policy changes.** Source: `engineering/current/LOOM_2226_METRIC_LOOM_WEAVE_FICTIONAL_ENGINEERING_FOUNDATIONS_v0.1.md` §§5, 7, 8, 15–17; compare `wayfarer/lab/shuttle/v3/proto/weave/WEAVE_MANOEUVRING_2026_11_21.md` at d056040. Distinguish a **constructible target metric** from a **dynamically attainable field solution**.

## Smallest target geometry
In an approximately flat background, use the smooth, finite-radius shift metric
```
ds² = -c²dt² + [dx - v(t) f(r_s) dt]² + dy² + dz²
r_s² = (x-X(t))²+y²+z²,   dX/dt=v(t).
```
Choose f≈1 at r_s≪R, f≈0 outside r_s≫R, and smooth wall width δ. This is a test geometry, not a claim that the Mc actuator can synthesize it. It uses the foundations' ADM form with lapse N=1, Euclidean spatial metric γ_ij=δ_ij, and shift β^x=−vf/c (foundation §5); relational attachment stays fixed (§7).

At the domain centre, x=X(t), the unit-lapse Eulerian normal worldline has dx/dt=v(t). Since spatial lapse gradient vanishes, these normal observers are geodesic: proper acceleration zero, even for time-dependent v(t). Interior is approximately flat for f≈1. An at-rest ship can be carried through a smooth start–dash–stop with its final external coordinate velocity zero. This **demonstrates kinematic consistency**, not field dynamics or energy conservation. It does not require the fictional 'torch owns velocity' rule.

## What standard GR actually demands
ADM Hamiltonian constraint: `16πG ρ_mass/c² = ^(3)R + K² − K_ij K^ij`, with spatial curvature zero. For the axial shift above, the Eulerian energy density is
```
ε_Eulerian = − c² v²/(32πG) [ (∂_y f)² + (∂_z f)² ] .
```
This is negative in the wall except where the transverse gradient vanishes. Integrated over a spherical profile:
```
E_negative = −c²v²/(12G) ∫_0^∞ r² [f'(r)]² dr .
```
For `f(r)=½[1−tanh((r−R)/δ)]` and thin-wall `R≫δ`, `∫r²(f')²dr≈R²/(3δ)`, giving `E_negative≈−c²v²R²/(36Gδ)`. At R=10 m, δ=2 m, v=100 m/s, this is ≈−1.87×10³² J (approximate thin-wall estimate; R/δ=5, so do not claim precision). Negative Eulerian energy violates the weak energy condition in ordinary GR. Time-dependent ramps also demand nontrivial momentum flux and stresses through Einstein's momentum/evolution equations; the Hamiltonian density alone does not supply the full stress tensor.

This enormous *effective geometric stress-energy* is **not** automatically the electrical energy expended by a hypothetical M2 source. Conversely, M2 cannot be declared a solution simply by saying it 'waives' the negative-energy bill: the constitutive action and source/field exchange remain unknown.

## Complete conservation test
For an asymptotically flat, isolated setup, integrate the total field + matter conservation law over a worldtube, including boundary flux:
```
ΔE_ship + ΔE_source + ΔE_Weave + ΔE_environment + E_outgoing = 0
ΔP_ship + ΔP_source + ΔP_Weave + ΔP_environment + P_outgoing = 0
```
For a closed start/stop in flat space with ship initially and finally at rest, ΔE_ship=ΔP_ship=0. If the field also returns to its initial vacuum state, a positive electrical/thermal/radiative cost must be offset by source depletion. No external reaction partner is logically required for the *net* impulse of this symmetric closed test, although nonzero transient field momentum and stresses must be supported. For a nonclosed velocity change, the final ship momentum must be balanced by field, source, radiation or environment. A gravitational background requires gravitational potential and frame terms, not a manually selected 'Sun' or 'planet' partner.

**Crucial:** ordinary GR gives the local geometric stress tensor `G_{μν}/(8πG)` but not the M1/M2 microscopic action, actuator response, source depletion, or boundary flux. The full ledger **cannot be numerically closed** from the existing foundations. An accounting rule that sets ascent cost to mgh is a model assumption, not a derivation. Nor does a free geometric dash follow from zero Δkinetic energy.

## Consequences without protective restrictions
- A locally inertial, finite-domain dash with zero start/end ordinary velocity is **kinematically permitted** by a smooth shift metric.
- A changed final ordinary velocity is not generally forbidden by M1/M2; it requires balancing momentum and energy.
- Continuous position control, hover, orbital manoeuvring and fast ramps are **not yet dynamically proven**, and may radically change freight/torch economics if achievable.
- A metric boundary moving through atmosphere/water cannot be assumed silent or harmless. Matter stress, shock, entrainment and energy flux must be calculated with an explicit coupling model.
- The quoted 1 MJ/dash cold, 18 dodges, frost charges and 13.8 t module are engineering **hypotheses**, not results of this derivation.

## Verdict and precise missing physics
**Kinematic target: PASS.** A finite, smooth metric can transport and stop an approximately inertial shuttle without conventional crew g-loading.

**Ordinary-GR physical sourcing: FAIL.** The chosen geometry demands enormous negative wall energy and associated stress/momentum flux.

**LOOM M1/M2 dynamical and conservation closure: UNDETERMINED.** The existing foundations provide a relational sector and controllable coupling permission (foundation §§15–16) and inverse-control intent (§17), but not an action/constitutive relation specifying field stress-energy, energy source, boundary flux or whether this target is reachable. It is therefore incorrect to claim either 'physics closed' or 'third miracle proven necessary'.

**Smallest next discriminating step:** supply **one** effective M2 field/source action (or an equivalent explicit stress-energy and exchange law) for this *one* target dash, derive its energy and momentum fluxes, and see whether the actuator can realize the profile with finite source cost. If no such law is available, stop at UNDETERMINED; do not invent gameplay restrictions or numerical dash budgets.
