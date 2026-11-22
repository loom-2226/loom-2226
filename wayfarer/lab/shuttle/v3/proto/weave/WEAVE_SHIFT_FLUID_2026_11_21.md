# Can air follow the zero-expansion shift? (NON-CANON)

ALL bodies. ALL sponsors. 2026-2226.

Prototype lane, 2026-11-21. Responds to Sol's review of 2027261: does a divergence-free prescribed flow survive the fluid equations? No canon change.

Code: `weave_shift_fluid.py`, `shift_fluid_figure.py` → `weave_shift_fluid.png`. Data: `weave_shift_fluid.json`, `weave_shift_fluid_maps.json`.

## 1. Sol's correction, and what it reduces to

Sol is right that ∇·β = 0 alone does not make the flow a fluid solution: the fluid momentum equation must also hold. The test is the one Sol set:

1. compare the required fluid acceleration `∂ₜβ + (β·∇)β` with the spacetime's geodesic acceleration;
2. check local conservation `∇_μ T^{μν} = 0` of the fluid stress-energy.

**Exact GR, numerical.** Setup:
- metric `ds² = −c²dt² + Σ(dxⁱ − βⁱdt)²` (N = 1, flat slices), with the axisymmetric zero-expansion shift written in Cartesian form;
- a time-dependent domain with V up to 0.3c, which is deliberately relativistic;
- full 4D Christoffels by 4th-order finite differences, at 60 random points concentrated in the wall shell;
- a perfect fluid with uniform ρ and p and `u^μ = (1, βⁱ)`.

| Quantity | Natário-type shift | Control: Alcubierre-type shift (∇·β ≠ 0) |
|---|---|---|
| norm of u | −1 (exact) | −1 |
| 4-acceleration ÷ required acceleration | ≤ 3e-10 | ≤ 8e-10 |
| geodesic accel − required accel (relative) | ≤ 3e-10 | ≤ 3e-10 |
| ∇·T relative to its largest term | ≤ 7e-12 | **1.1–1.4** (fails) |

**Reading:**
- With N = 1, Eulerian matter is in free fall for **any** shift. The air's required acceleration is supplied exactly by geometry, so no pressure gradient is needed to make it follow β. (DERIVED)
- Uniform ρ and p are also a conserved stress-energy **only if** ∇·β = 0. The Alcubierre control fails, which shows the test can detect a violation. (DERIVED)
- So the zero-expansion shift flow *is* an exact ideal-fluid solution, as a test fluid (the air's own gravity ignored). Uniform pressure means no pressure wave in the ideal fluid. The 690 m/s backflow is coordinate motion of air that is locally in free fall.

## 2. What the ideal fluid leaves out (sea-level air, the real 200 m / 3 s dash)

| R / d (m) | peak shear (s⁻¹) | viscous stress (Pa) | viscous loss (J) | wall speed through local air (Mach) | gust amplification: median / p99 / max | air amplified > 10× |
|---|---|---|---|---|---|---|
| 15 / 2 | 74 | 0.003 | 1.4e3 | 0.89 | 1.6 / 158 / 189 | 22 t |
| 12 / 2 | 62 | 0.002 | 6.3e2 | 0.76 | 1.2 / 131 / 189 | 14 t |
| 12 / 0.5 | 855 | 0.031 | 3.2e4 | **2.38** | 1.0 / 519 / 785 | 9 t |

- **Viscosity** is negligible as an energy cost (≤ 32 kJ) and as a pressure source (0.002–0.03 Pa).
- **Sound.**
  - The wall pattern moves through the local air at Mach `max|V x̂ − β| / c_s`.
  - Thick walls (d = 2 m) are subsonic at the 125 m/s peak.
  - The thin wall is **supersonic** (Mach 2.4). Its weak viscous source would form a Mach front there.
  - Radiated amplitude has not been computed. (UNDETERMINED)
- **Gust amplification is the real finding.**
  - The shift strains air strongly in a near-axis core along the whole track: radius under about 10 m, the air that drifts forward.
  - Small pre-existing motions are stretched by up to about 190× (thick wall) or 785× (thin wall). This uses `ẇᵢ = −wⱼ∂ᵢβⱼ` with det W = 1, a test-particle bound with pressure feedback ignored.
  - In still air the dash leaves nothing.
  - With 1 m/s ambient gusts the upper bound left behind is 19–28 MJ (thick) or 90 MJ (thin). That is comparable to the lapse wake.
  - So "silent" depends on how calm the air is.

## 3. Verdicts

| Claim | Verdict |
|---|---|
| Air can follow the zero-expansion shift with no pressure gradient | **DERIVED** (exact GR, test-fluid; residuals 1e-10, with a control that fails) |
| Uniform pressure is conserved (no ideal-fluid sound) | **DERIVED** for ∇·β = 0; INCONSISTENT for Alcubierre-type shifts |
| Viscous loss and viscous sound are negligible | DERIVED as estimates (≤ 32 kJ; ≤ 0.03 Pa source) |
| Thick-wall shift stays subsonic relative to local air at 125 m/s peak | DERIVED (Mach 0.76–0.89) |
| Thin-wall shift is supersonic through local air | DERIVED (Mach 2.4); radiated strength UNDETERMINED |
| Silent in calm air | DERIVED within inviscid, test-fluid limits |
| Silent in real, turbulent air | **not established**: gusts in the near-axis core are amplified up to about 190–785× (test-particle bound); a full perturbation solve with pressure is UNDETERMINED |
| Air's own gravity / back-reaction on the metric | neglected (test-fluid), UNDETERMINED |
| M1 momentum exchange (A3) | still assumed; unchanged by this test |

## 4. Corrections recorded

- **Perturbation sign.** The slow-geodesic perturbation equation is `ẇᵢ = −wⱼ∂ᵢβⱼ`. My `weave_geometry_compare.py` ship code (2027261) used +. Corrected:
  - clear-wall shift rows barely change;
  - the wall-cuts-hull case becomes catastrophic (158 g, hull slips out at 61 m).
  - See the note in `WEAVE_GEOMETRY_COMPARE_2026_11_21.md`.
- **"Exact fluid solution" wording in 2027261.** It now rests on §1, which is what Sol asked for. It is exact only as an ideal test fluid.

## 5. Consequences

- The shift remains the leading kinematic candidate. Its quiet transport survives the ideal fluid equations exactly. It is not a prescription the air fails to obey.
- Its atmospheric signature is no longer "nothing". It is:
  1. a displaced air bubble;
  2. a subsonic or supersonic wall depending on wall thickness (Mach ≈ (1 + max|β|/V)·V / c_s);
  3. amplified ambient turbulence along a narrow core of the track.
- Calm-air dashes are quiet. Gusty-air dashes leave a churned wake.
- Thick walls are subsonic and amplify less, but need more clearance from the hull.
