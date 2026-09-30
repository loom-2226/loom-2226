# Pluto six-body JPL-model reproduction evidence — 2026-09-30

Status: **EXPERIMENTAL SCIENTIFIC VALIDATION EVIDENCE**. This does not mutate the Solar authority ledger, registry, PostgreSQL state, or any viewer product. It does not by itself qualify post-PLU060 propagation.

## Why this experiment exists

The first LOOM Pluto-system continuation experiment diverged from PLU060 by roughly 1,000–6,700 km over the 2180–2199 withheld-truth interval. The candidate used rounded public-display GM values, treated Kerberos and Styx as massless, used a fixed-step RK4 integrator, and linearly interpolated a one-day external-perturber table.

JPL's `plu060.cmt` exposes the exact dynamical constants used to generate PLU060. The published Brozovic & Jacobson (2024) model uses all six Pluto-system bodies, external perturbations from the Sun and the Jupiter/Saturn/Uranus/Neptune systems supplied by DE440, and a variable-order/variable-step Gauss-Jackson integration with a maximum 1800 s step.

Source metadata:
- https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/plu060.cmt
- Brozovic & Jacobson (2024), *Post-New-Horizons Orbits and Masses for the Satellites of Pluto*, AJ 167:256, DOI 10.3847/1538-3881/ad39f0

## Critical finding

The original failure was primarily an **input-authority precision failure**, not evidence that a six-body continuation is intrinsically inadequate.

Using the old rounded internal constants but replacing the numerical method with adaptive DOP853 and direct DE440 forcing still produced, after only one year from the PLU060 file epoch:

- Pluto: 49.492 km
- Charon: 344.684 km
- Nix: 201.724 km
- Hydra: 240.881 km
- Kerberos: 198.029 km
- Styx: 275.521 km

Using the **exact PLU060 internal constants** while retaining the old fixed RK4 + daily-linear external-table approach reduced the 2180–2199 worst errors to:

- Pluto: 7.519 km
- Charon: 61.609 km
- Nix: 1.836 km
- Hydra: 0.843 km
- Kerberos: 1.181 km
- Styx: 3.716 km

Therefore rounded/missing internal GM values explain the overwhelming majority of the original multi-thousand-kilometre divergence. The old numerical/external-forcing approximations contribute a much smaller but still material long-term residual.

## JPL-model reproduction

LOOM then used:

- exact internal GMs from `plu060.cmt`;
- exact external GMs from `plu060.cmt`;
- only the published external perturbers: Sun and system barycenters 5, 6, 7, 8;
- DE440 queried directly at every force evaluation;
- Pluto-system barycentric coordinates;
- adaptive SciPy DOP853, `rtol=1e-12`, maximum step 21,600 s;
- authoritative PLU060 state as the initial condition.

This is not an attempt to claim DOP853 is JPL's production integrator. It is an independent high-order numerical reproduction of the published dynamical model.

### 2013 file epoch -> 19 Julian years

Maximum annual sampled position errors versus PLU060:

| Body | max error (km) |
|---|---:|
| Pluto | 0.015176 |
| Charon | 0.128131 |
| Nix | 0.003774 |
| Hydra | 0.002678 |
| Kerberos | 0.003347 |
| Styx | 0.010023 |

### 2180 -> ~2199 late-coverage withheld-truth test

Maximum annual sampled position errors versus PLU060:

| Body | max error (km) |
|---|---:|
| Pluto | 0.015750 |
| Charon | 0.127564 |
| Nix | 0.003993 |
| Hydra | 0.011492 |
| Kerberos | 0.001267 |
| Styx | 0.007920 |

The same physical model that previously missed by thousands of kilometres now reproduces PLU060 to **sub-kilometre error across all six bodies over the 19-year late-coverage test**, with the largest annual sampled error about **128 m**.

This strongly supports the conclusion that LOOM now has the correct basic Pluto-system dynamical model for a governed continuation experiment. It does **not** establish post-2199 positional uncertainty, nor does it promote any state beyond PLU060 coverage to DIRECT authority.

## Next scientific gate

Before publishing a 2200–2500 continuation:

1. run a longer within-coverage reproduction from the 2013 PLU060 file epoch toward the end of PLU060 coverage;
2. establish a numerical-convergence envelope for the chosen production integrator settings;
3. define the post-coverage authority class (`PROPAGATED_ESTIMATE`) and uncertainty/provenance contract;
4. only then integrate across 2199 and compile the result into qualified state functions.

## Reproducibility checks

- Evidence assertions: PASS (`original Charon > 6000 km`, exact-internal/old-numerics Charon < 100 km, high-fidelity late-coverage maximum annual sampled error < 0.2 km).
- `tools/validate_pluto6_jpl_model.py`: Python compile PASS and zero-year smoke PASS.
- Existing relevant Solar temporal/runtime tests: `8 passed` using a temporary `/tmp` pytest installation; the governed project environment was not modified to add pytest or SciPy.
