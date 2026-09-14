# E1 Local Curvature + Tidal Shear v0.1

## Purpose

Qualify a bounded local-geometry reference at the already-earned Neptune collapse endpoint without defining a new Geometric Admissibility threshold.

The endpoint remains the operational NAV-V1-A handoff, not a fundamental physical boundary.

## Qualified inputs

- Earned Neptune-centered collapse radius: **26,085.768742 km**.
- Earned collapse epoch: **2226-08-22T09:07:59.475571Z**.
- Earned arrival epoch: **2226-08-22T09:45:17.864616Z**.
- Neptune GM: **6,836,529.0 km^3/s^2**.
- Neptune mean radius: **24,622.0 km**.
- Endpoint altitude above the versioned mean-radius reference: **1,463.768742 km**.

The Neptune GM and mean radius are inherited from the already-qualified exact fields in `data/LOOM_2226.sqlite3`. The endpoint is inherited from the earned NAV-V1-A / forced-collapse-radius lineage. This work does not re-solve or move the endpoint.

## Reference geometry

For the spherical monopole contribution,

`lambda = GM / r^3`.

The weak-field tidal/electric-curvature eigenvalues are

`(+2 lambda, -lambda, -lambda)` in `s^-2`.

The trace is zero, as expected for the spherical vacuum-monopole reference contribution. The Frobenius norm is also reported as a compact magnitude of the reference tidal tensor.

For a coordinate-independent monopole curvature reference, the Schwarzschild Kretschmann invariant is reported:

`K = 48 (GM)^2 / (c^4 r^6)` in `km^-4`.

This is a **reference contribution**, not a claim that the actual 2226 Neptune endpoint is exactly Schwarzschild vacuum.

## Explicitly unresolved

This step does not qualify Neptune rotation/frame dragging, oblateness or higher multipoles, local stress-energy/matter density, 2226 physical uncertainty, Loom coherence, lattice coherence, or any binding between metric-domain size and admissibility.

Those omissions matter. They are preserved rather than silently treated as zero.

## Authority boundary

This step defines:

- no admissibility score;
- no threshold;
- no exclusion radius;
- no Hill/SOI rule;
- no runtime policy;
- no campaign-state mutation.

`LOCAL_GEOMETRY_REFERENCE_QUALIFIED_ADMISSIBILITY_DECISION_NOT_YET_EARNED`

## Next bounded question

Propagate physical uncertainty and determine whether Neptune rotation/multipole corrections are material at the earned endpoint before attempting any compound Geometric Admissibility model.
