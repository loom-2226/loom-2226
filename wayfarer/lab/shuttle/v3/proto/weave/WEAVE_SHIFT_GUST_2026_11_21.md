# Shift atmospheric perturbation check: one gust, with pressure (NON-CANON)

ALL bodies. ALL sponsors. 2026-2226.

Prototype lane, 2026-11-21. Responds to Sol's brief after ed8843c:

> Does a 1 m/s disturbance produce a persistent, energetic wake when pressure feedback is included?

No canon, hardware or field-assumption changes.

Code: `weave_shift_gust.py` (runs `main`, `coarse`, `fine`), `gust_swirl.py`, `gust_figure.py` → `weave_shift_gust.png`.
Data: `weave_shift_gust_{main,coarse,fine}.json` (+ `_series`), `weave_shift_gust_swirl.json`.

## 1. Equations

The perturbation is written in terms of **w**, the air velocity measured in the local free-fall (Eulerian) frame. The coordinate flow β is the background; w is not. The linearized slow-motion equations for compressible air in the N = 1 shift metric, coordinate frame:

```
∂t w  = −∇(β·w) + β×ω − c_s² ∇ρ'/ρ0        ω = ∇×w
∂t ρ' = −β·∇ρ' − ρ0 ∇·w                      (∇·β = 0)
```

Dropping the c_s² term recovers the earlier test-particle law `ẇᵢ = −wⱼ∂ᵢβⱼ` in Eulerian form.

**DERIVED.** Taking the curl gives `∂t ω = ∇×(β×ω)`. Vorticity is frozen into the β flow, *independent of pressure*. Pressure acts only on the compressive part of a gust, which becomes sound.

## 2. Setup

- **Geometry:** R = 15 m, wall 2 m, the 200 m / 3 s quintic. Axisymmetric.
- **Gust:** a 1 m/s axial Gaussian, L = 3 m, on the track axis at x = 60 m, in the core where the pressure-free amplification was largest. About ⅓ of its energy is compressive and ⅔ vortical.
- **Numerics:** 2nd-order central differences, RK4, a 4th-order filter and a 15 m absorbing sponge. Energy reaching the sponge counts as radiated sound.
- **Runs:** {dash, no dash} × {pressure, no pressure} at h = 0.5 m. The dash runs are repeated at h = 1 m and 0.25 m.
- **Controls:**
  - No dash, no pressure: energy constant (32.05 J, start 32.04 J). Confirms the scheme and filter.
  - No dash, with pressure: about ⅓ radiates (9.0 J) and the vortical ⅔ stays (21.1 J), as predicted.

## 3. Results (gust energy, J; start ≈ 32 J)

| Run | h = 1 m | h = 0.5 m | h = 0.25 m |
|---|---|---|---|
| dash, **no pressure**: final | 2,852 (×88) | 6,091 (×190) | 10,785 (×338) |
| dash, **with pressure**: final | 9.6 (×0.30) | 9.55 (×0.30) | 11.9 (×0.37) |
| dash, with pressure: radiated as sound | 8.9 | 11.9 | 13.0 |
| dash, with pressure: transient peak (t ≈ 1.2 s) | 75 | 118 | 142 |
| no dash, with pressure: final / radiated | – | 21.1 / 9.0 | – |

- **The pressure-free amplification is not physical and not converged.** It grows roughly as 1/h. It is the compressive part of the gust being stretched into ever-finer gradients. In real air that part is sound, and it leaves.
- **With pressure, the result converges to within about 25%.** The dash leaves *less* gust energy than doing nothing: 0.30–0.37 of the start, against 0.66 with no dash.
- **Sound.** Extra sound attributable to the dash is about 3–4 J on top of what the gust would radiate anyway (about 10% of the gust energy).
- **Unaccounted energy.** It shrinks with resolution (14 → 11 → 7 J). It is partly filter loss and partly work exchanged with the time-dependent field.
- **Transient.** While the wall passes, gust energy rises briefly by ×2–4.4. This peak is not converged and rises with resolution. It then decays in under a second, partly as sound.
- **Fate of the disturbance.** The compressive part propagates away as sound. The vortical part stays localized: it is carried along the track (energy centroid moves from x = 60 m to about 125–170 m) and weakened, because in axisymmetry ω_φ/ρ is a material invariant and the core air spreads.

**Swirl family (exact).** For an axisymmetric swirl gust the pressure term vanishes identically, and `ρ w_φ` is conserved along each parcel. From the parcel end positions, gust-energy ratios are 0.16–1.00 for blobs at x = 20–180 m, ρ = 1–8 m. Individual parcels can reach ×12, but no blob gains energy.

## 4. Revised atmospheric estimate

The 19–28 MJ (thick wall) figure in `WEAVE_SHIFT_FLUID_2026_11_21.md` applied a pressure-free amplification to every parcel. With pressure, this gust family is *not* amplified.

For 1 m/s turbulence filling the modelled swept volume (about 0.3 MJ of gust energy), the scaled residual is ≲ 0.3 MJ, with about 0.1 MJ radiated. That is about two orders of magnitude below the pressure-free bound. This scaling is an ESTIMATE from one gust shape and two symmetric families.

## 5. Verdicts

| Claim | Verdict |
|---|---|
| Pressure-free gust amplification (×88–338) is physical | **INCONSISTENT**: unconverged, and removed by pressure |
| Vorticity is frozen into the β flow regardless of pressure | DERIVED |
| The compressive part of a gust leaves as sound | DERIVED (numerical, with controls) |
| Axisymmetric gusts leave a persistent energetic wake | **No**: residual ≈ 0.3–0.4 × the initial gust energy, below the no-dash 0.66 (DERIVED within linear, axisymmetric limits) |
| Swirl gusts are amplified | No in blob energy (0.16–1.0); exact |
| Transient during wall passage | ×2–4 briefly; peak not converged |
| Non-axisymmetric gusts (azimuthal mode m ≥ 1) | **UNDETERMINED: blocker.** Needs a 3D linear solver. Vortex tilting by the axial shear could behave differently. Not built, per the stop condition |
| Nonlinear / finite-amplitude gusts, real turbulence | UNDETERMINED (linear model) |

## 6. Has the atmospheric signature materially changed?

Yes, back toward quiet. The "churned wake in gusty air" warning from ed8843c does not survive pressure for axisymmetric gusts. The signature in air is now:

1. a displaced air bubble;
2. a wall that is subsonic (2 m walls) or locally supersonic (thin walls) relative to the local air, with the radiated strength unknown;
3. a brief, modest stirring of existing gusts as the wall passes, leaving them weaker, plus a little sound.

The one remaining atmospheric unknown is non-axisymmetric gusts, which need 3D machinery.

The source and reaction questions (M2 field generation, M1 momentum home for carried matter) are unchanged and are the main open physics.
