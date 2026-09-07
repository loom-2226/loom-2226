# LOOM 2226 — Stage F-PB Orbital Consequence Qualification

Date: 2026-09-08  
Status: **Stage F-PB design/qualification evidence — feature branch / NON-CANON until governed merge**

## Authority

This slice was built from live GitHub authority. Relevant governing sources re-fetched before implementation:

- `docs/LOOM_2226_Simulation_Physical_Authority_Work_Plan_Amendment_2026-09-08.md`
- `canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md`
- `src/loom/application/contracts.py`
- `src/loom/spatial/gravity.py`
- `src/loom/spatial/celestial_state.py`
- `src/loom/spatial/sqlite_celestial_catalog.py`
- `docs/LOOM_2226_Stage_F_PB_State_Continuity_Tokyo_Drift_Qualification_2026-09-08.md`

No new celestial constant, body radius, traffic rule, station orbit, metric momentum law or campaign value is introduced here.

## Purpose

The first F-PB continuity slice prevents a desired terminal/orbit state from overwriting the natural metric-collapse state. This slice adds the next required check: given the exact body-relative collapse state `(r,v)`, determine what ordinary two-body orbit that state actually implies.

The implementation is `src/loom/spatial/orbit_consequence.py` with contract version `LOOM_F_PB_ORBIT_CONSEQUENCE_V1`.

## Required input authority

The orbital-consequence layer requires all of the following explicitly:

- exact `SpatialState` for the ship at the boundary epoch;
- state already expressed in the declared body-centered inertial frame;
- central-body identity;
- central-body gravitational parameter `GM` supplied by an authority layer;
- optional reference-surface and atmosphere-interface radii supplied explicitly when intersection checks are required.

The layer refuses hidden frame conversion and never infers GM or body radius from an entity name.

## Derived consequence

Under the declared point-mass/two-body osculating model, the layer derives from the supplied state:

- radius and speed;
- radial velocity;
- specific orbital energy;
- specific angular-momentum vector and magnitude;
- eccentricity vector and eccentricity;
- circular / elliptic / parabolic / hyperbolic / radial classification;
- semi-major axis where defined;
- periapsis radius;
- apoapsis radius for bound elliptic cases;
- inclination where angular momentum is non-degenerate;
- optional intersection with supplied surface or atmosphere interface.

This is a consequence calculation only. It does not propagate the trajectory, create a capture burn, assign an authorized orbit, or change the input state.

## Tokyo Drift gate

A metric collapse may be called a natural orbital capture only if the actual natural collapse state produces the claimed orbit under the qualified ordinary dynamics model.

Therefore:

```text
U^M_gamma natural collapse state
        ↓
explicit target-body-centered inertial transform
        ↓
orbital consequence from exact (r,v)
        ↓
actual orbit class / periapsis / apoapsis / energy / h
        ↓
compare with desired authorized orbit or rendezvous state
        ↓
zero residual = natural match
nonzero correctable residual = explicit torch/tug/infrastructure exchange
invalid / uncertified / prohibited = reject
```

The following are not sufficient to claim a perfect orbit:

- matching speed only;
- matching velocity direction only;
- matching altitude only;
- assigning the requested circular-orbit velocity after collapse;
- snapping the ship to an authorized orbital slot;
- treating traffic permission as capture physics.

## Model boundary

This initial consequence layer is deliberately a point-mass two-body osculating diagnostic. It is appropriate as the first deterministic handoff/qualification primitive and is consistent with the existing LOOM gravity and osculating-state architecture.

It is not the final high-fidelity arrival propagator. Depending on body/fidelity tier, later qualification may add J2/higher harmonics, third-body perturbations, atmosphere/drag, non-spherical shape/terrain, station-relative dynamics and traffic geometry.

The model name and provenance travel with the result so a two-body consequence cannot silently masquerade as higher-fidelity flight truth.

## Qualification cases

The checked-in tests use synthetic known-answer dynamics rather than fictional body constants:

1. exact circular state: `mu=10000 km^3/s^2`, `r=100 km`, `v=10 km/s` -> circular orbit with `a=rp=ra=100 km`;
2. super-escape tangential state -> hyperbolic, not capture;
3. low-angular-energy elliptic state -> periapsis intersects explicit supplied surface/atmosphere radii;
4. radial state -> preserved as `RADIAL` with zero angular momentum rather than silently regularized into an orbit;
5. frame mismatch -> fail closed;
6. absent collision radii -> no collision conclusion is invented.

## Stage consequence

F-PB now has two linked authority primitives:

1. propulsion-boundary continuity and natural-vs-desired residual;
2. ordinary orbital consequence derived from the exact natural terminal state.

Next work should connect the two explicitly in a hostile Tokyo Drift qualification object/test so that Navigator can prove that a claimed `NATURAL_MATCH` corresponds to the derived target-body orbit rather than only a small Cartesian residual or requested endpoint label.
