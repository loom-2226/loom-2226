# LOOM 2226 — Wayfarer S2 Common-Model Comparison Report

**Date:** 2026-09-08  
**Status:** ENGINEERING / RESEARCH — NON-CANON — NON-PRODUCTION  
**Branch:** `research/physical-design-synthesis-wayfarer-s2-2026-09-08`

## Result

`S2_COMMON_MODEL_COMPARISON = PASS`

Both the preserved hand-authored Wayfarer baseline and the closed S1 generated candidate are legal under the same admitted S1 physical model. This is a comparison of common admitted quantities only; it is not a comparison of qualified full Wayfarer inertia because that quantity remains OPEN.

## Compared layouts

| Quantity | Hand-authored baseline | Generated S1 candidate | Generated - baseline |
|---|---:|---:|---:|
| Relational plant x | 26.0 m | 26.0 m | 0.0 m |
| Planetary launch x | 21.8 m | 21.75 m | -0.05 m |
| Four-tank common x | 25.0 m | 26.5 m | +1.5 m |
| Wet mass | 1,158,500 kg | 1,158,500 kg | 0 kg |
| CoM x | 26.676650841605525 m | 26.99892101855848 m | +0.322270176952955 m |
| CoM y | ~0 m | ~0 m | 0 m |
| CoM z | 0.14812257229175657 m | 0.14812257229175657 m | 0 m |
| Unresolved inertia mass fraction | 0.8955545964609408 | 0.8955545964609408 | 0 |

The baseline exactly reproduces the qualified DOCKED wet mass and CoM within numerical tolerance. The generated layout preserves exact mass and transverse CoM while moving the longitudinal CoM aft by about 0.32227 m.

## Objective-vector comparison

The S1 objective vector is intentionally not collapsed to one scalar winner.

| Objective | Baseline | Generated | Delta | Interpretation |
|---|---:|---:|---:|---|
| J1 transverse CoM offset | 0.1481225723 m | 0.1481225723 m | 0 | unchanged |
| J2 longitudinal CoM band deviation | 0 m | 0 m | 0 | both inside x=26.5..27.0 m target band |
| J3 rotational-control burden surrogate | 2,670,193.4371 kg·m² | 2,670,193.4371 kg·m² | 0 | unchanged because moved masses retain transverse placement |
| J4 remass-feed distance surrogate | 18.0 m | 16.5 m | -1.5 m | generated layout improves this surrogate |
| J5 major power-path surrogate | 5.0 m | 5.0 m | 0 | unchanged |
| J6 packaging collision penalty | 0 | 0 | 0 | both legal under admitted full-body collision model |
| J7 launch-extraction penalty | 0.20 m | 0.25 m | +0.05 m | generated layout is slightly worse on this surrogate |

This is a genuine trade: the solver moves the tank cluster aft, improving the first-order remass-feed surrogate by 1.5 m, while placing the launch 5 cm farther from the qualification-only bay-center reference. No global design winner is declared.

## Partial inertia comparison

The admitted centroidal tensor is identical because both layouts use the same admitted relational-cylinder and launch-box bodies with unchanged dimensions and masses.

The generated-minus-baseline **parallel-axis** tensor delta is approximately:

```text
[[      0.0,            ~0.0,   +63881.5624],
 [     ~0.0,      -799132.254,        0.0],
 [+63881.5624,          0.0,    -799132.254]] kg m^2
```

The aggregate partial tensor changes by the same amount because the admitted centroidal contribution is unchanged.

These values are **not full Wayfarer flight inertia**. About 89.56% of total mass still lacks admitted centroidal-inertia geometry in S1/S2, so principal axes and full inertia remain unqualified.

## What S2 establishes

1. The procedural solver is not merely replaying the hand-authored transform tuple.
2. The generated candidate remains a legal Wayfarer-like arrangement under the same reduced constraints.
3. The generated layout preserves the qualified wet mass exactly.
4. The baseline common-model reconstruction reproduces the qualified DOCKED CoM, validating the comparison bridge.
5. The main solver-driven physical change is the tank cluster moving aft by 1.5 m, which shifts longitudinal CoM aft by about 0.32227 m and improves J4.
6. The comparison exposes a real trade rather than a universally superior layout: J4 improves while J7 worsens slightly; other visible S1 objectives remain unchanged.

## Explicitly unresolved / not compared

- full Wayfarer centroidal inertia;
- principal axes/eigenvalues based on full inertia;
- tank axial-body inertia and axial collision geometry;
- radiator-panel geometry and deployed clearance;
- docking geometry and docking clearance;
- detailed thermal/radiation penalties beyond the existing S1 surrogates;
- structural load-path authority beyond the admitted reduced model.

## Authority firewall

```text
flight_dynamics_authority = false
wayfarer_flight_inertia_qualified = false
canon_changed = false
production_shipclasses_changed = false
```

S2 does not replace the governing hand-authored Wayfarer design. It establishes that the generated candidate is meaningfully different, physically legal within the reduced admitted model, and useful enough to justify the next roadmap question without claiming more physics than has been earned.
