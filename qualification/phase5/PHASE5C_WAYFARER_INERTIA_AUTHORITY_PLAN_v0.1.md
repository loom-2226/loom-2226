# LOOM 2226 — Phase 5C Wayfarer Inertia Authority Plan v0.1

**Status:** ENGINEERING / QUALIFICATION — CANDIDATE PLAN — NOT CANON — NOT FLIGHT AUTHORITY  
**Date:** 2026-09-08  
**Parent branch:** `qualification/portable-ship-phase5-dynamics-2026-09-08`

## 1. Purpose

Phase 5B proved that current Wayfarer authority supports mass, CoM and the parallel-axis contribution, but not complete centroidal inertia. Phase 5C shall establish a physically coherent candidate centroidal mass-distribution model without promoting renderer-only geometry or OPEN dimensions into flight authority.

The target is not detailed finite-element fidelity. The target is a deterministic rigid-body mass-property model whose assumptions are explicit, mechanically standard, conservative where practical, and independently testable.

## 2. Governing mechanics convention

Use ordinary aerospace rigid-body mass properties in SI units.

For each component `i`:

1. define mass `m_i` and centroid `r_i` from existing authority;
2. define a centroidal inertia tensor `I_i,c` from a governed or explicitly qualified equivalent shape;
3. rotate `I_i,c` into the Wayfarer body frame;
4. shift it from component centroid to instantaneous vehicle CoM with the parallel-axis theorem;
5. sum all active component/store contributions.

The flight tensor is therefore:

```text
I_C = SUM_i [ R_i I_i,c R_i^T
              + m_i ( ||d_i||^2 E - d_i d_i^T ) ]
```

where `d_i = r_i - r_C`.

The resulting matrix must be symmetric positive definite for a physically three-dimensional active vehicle. Configuration changes and store depletion must recompute mass, CoM and inertia from the same active physical authority.

### Products-of-inertia notation

NASA/NESC mass-properties guidance commonly defines scalar products such as `Ixy = integral(x y dm)` and places `-Ixy` in the matrix off-diagonal. LOOM executable storage shall instead store the actual matrix coefficients consumed by the dynamics equation. External vectors must therefore pass through an explicit notation adapter rather than relying on symbol names alone.

This convention choice must be frozen in executable tests before external-reference comparison.

## 3. Reference alignment

Qualification references:

- **Basilisk spacecraft dynamics:** current spacecraft mass, CoM and inertia in body-frame components; time-varying mass properties supported.
- **NASA/NESC mass-properties guidance:** standard inertia definitions, composite-body construction and parallel-axis theorem.
- **NASA JEOD + Trick:** deep hostile/reference dynamics where practical.
- **Tudat/TudatPy:** astrodynamics cross-reference where applicable.

These are qualification/reference systems. The Pixel runtime remains LOOM-owned and offline-capable.

## 4. Current Wayfarer authority audit by mass element

### 4.1 Strong candidate direct mappings

#### Unified relational plant — 88,000 kg

Current mass authority:

```text
mass = 88,000 kg
centroid = [26, 0, 0] m
status = CANON_MASS_DESIGN_POSITION
```

Current physical envelope authority:

```text
x = 18..34 m
length = 16 m
diameter = 1.4 m
status = DESIGN_BASELINE
```

The envelope centroid is exactly x=26 m. A uniform solid-cylinder equivalent shape is therefore a clean **engineering equivalent-body candidate**. It must remain tagged DERIVED/DESIGN_BASELINE, not CANON geometry.

#### Planetary launch — 33,000 kg when DOCKED/EXTRACTING

Current mass authority and Phase-3 transform produce the governed carried centroid. Current engineering envelope is approximately:

```text
10.5 m x 3.9 m x 3.1 m
```

A uniform rectangular-solid equivalent body is a reasonable **explicit engineering approximation** for the launch centroidal tensor. It is not a claim about detailed launch internal mass distribution. ABSENT removes both mass and inertia contribution.

### 4.2 Store model requiring deliberate refinement

#### Normal remass-capable working fluid — 250,000 kg reference

Canon/current engineering authority provides:

```text
4 major tanks in quadrature
62.5 t normal inventory per tank = derived equal split
major tank region x = 18..32 m
external tank diameter = 3.0 m
tank center radius = 2.7 m
```

Current Phase-3 mutable-store compatibility representation intentionally collapses this to one point store at `[25,0,0]` for mass/CoM accounting.

For rotational mass properties, Phase 5C may introduce a **qualification-only four-store decomposition** of 62,500 kg each, placed at the governed quadrature tank centers, provided all of the following are machine-checked:

- total mass remains exactly 250,000 kg;
- aggregate CoM remains exactly `[25,0,0]`;
- depletion policy is explicitly defined;
- the decomposition is not silently written back into production SHIPCLASSES;
- tank internal fluid geometry is tagged as engineering equivalent-body approximation rather than exact physical fill/slosh authority.

A full uniform 14 m x 3 m cylinder is not automatically valid for every fill fraction. The initial reference-state surrogate may use a filled-cylinder equivalent only at the 250 t reference state. Partial-fill behavior requires a separately declared model.

#### Protected water — 50,000 kg

Current mass/CoM authority exists at `[12.5,0,0]`, but no sufficiently governed containing geometry has yet been identified. **Remain OPEN for centroidal inertia.** Do not infer a tank from renderer geometry.

### 4.3 Coarse ledger masses not yet shape-qualified

The following masses have governed/design-baseline mass and centroid but insufficient unique physical mass-distribution authority for direct centroidal inertia derivation:

- primary structure — 150,000 kg;
- armor / fixed shield — 105,000 kg;
- habitation / life support — 45,000 kg;
- thermal / radiators — 90,000 kg;
- propulsion group — 160,000 kg;
- electrical systems — 55,000 kg;
- avionics / sensors / comms — 20,000 kg;
- RCS / docking / service — 25,000 kg;
- mission / courier systems — 20,000 kg;
- engineering reserve — 67,500 kg.

Existing visual/packaging envelopes may constrain candidate equivalent bodies, but they do not currently allocate these ledger masses uniquely enough to derive exact tensors.

The 67.5 t engineering reserve is explicitly unresolved and must not acquire fictitious geometric precision.

## 5. Candidate-model policy

Phase 5C shall use four authority classes for centroidal tensors:

```text
A — GOVERNED_DERIVABLE
    Geometry + mass support direct deterministic derivation.

B — ENGINEERING_EQUIVALENT
    Equivalent solid chosen from governed packaging constraints;
    explicit approximation, review required.

C — QUALIFICATION_SURROGATE
    Synthetic distribution used only to exercise mechanics/algorithm;
    forbidden as Wayfarer flight authority.

D — OPEN
    No centroidal tensor admitted.
```

A complete Wayfarer flight tensor may be admitted only when every active mass contribution is class A or an explicitly approved class B. Class C and D contributions force `WAYFARER_INERTIA_OPEN_NOT_QUALIFIED`.

## 6. Proposed next executable increment

Do **not** immediately remove the inertia firewall.

First implement a Phase-5C candidate resolver that:

1. computes class-A/class-B candidate centroidal tensors only;
2. reports resolved and unresolved mass fractions separately;
3. proves exact conservation of total mass and CoM relative to Phase-3 authority;
4. proves symmetry and positive-semidefiniteness of every admitted component tensor;
5. proves aggregate tensor symmetry;
6. reports eigenvalue/principal-minor physical-validity diagnostics without using renderer-only inputs;
7. retains `flight_dynamics_authority=false` while any contribution remains C/D;
8. emits provenance/classification for every tensor contribution.

The first executable version should therefore improve the resolved inertia fraction while still failing closed for full Wayfarer rotation.

## 7. Hostile-review questions before flight admission

The review must explicitly challenge:

- whether the equivalent-body dimensions are truly sourced from physical authority rather than renderer convenience;
- whether coarse subsystem mass is being spread over an unrealistically large or small envelope;
- whether products-of-inertia signs match the executable matrix convention;
- whether the four-tank decomposition preserves the previously qualified mass/CoM authority exactly;
- whether partial tank depletion changes centroid/inertia correctly;
- whether radiator deployment changes inertia and, if so, whether physical panel geometry is sufficiently governed;
- whether launch extraction/detachment event ordering preserves angular momentum and uses deterministic event semantics;
- whether all admitted tensors are symmetric positive definite at the vehicle level;
- whether Phase-1 and Phase-5 attitude conventions are equivalent;
- whether Basilisk/NASA reference-vector comparisons use identical frames, tensor point, units and notation.

## 8. Gate

Phase 5C planning does not authorize Wayfarer rotational propagation.

Until a complete admitted tensor exists and survives independent reference comparison:

```text
WAYFARER_INERTIA_OPEN_NOT_QUALIFIED
```

remains the required behavior.

Navigator/GIS/HUD physics-dependent work remains frozen. Production SHIPCLASSES remains untouched. No merge is authorized.
