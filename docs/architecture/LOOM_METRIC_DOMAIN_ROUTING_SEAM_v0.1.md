# LOOM Metric-Domain Routing Seam v0.1

**Primary change class:** RUNTIME  
**Engineering authority consumed:** GIS / Navigator convergence architecture.  
**Status:** narrow implementation seam; candidate domain-radius physics remains unselected.

## Decision

Keep the architecture small:

1. Ephemeris/navigation authority owns moving celestial-body state.
2. Domain policy is paired to body identity and defines whether a body/system is a `METRIC_ENTRY` domain or `LOCAL_ONLY` nested domain.
3. Navigator combines ephemeris state + selected domain policy to obtain moving exclusion geometry.
4. Mara supplies semantic target/preferences only. Mara does not calculate boundaries, trajectories, collision checks, collapse points, or operating modes.
5. Physical exclusions are never overridable by player/model intent.
6. Regulatory exclusions are obeyed by default; an explicit override request may relax regulatory policy only.

## Example

`EUROPA` resolves semantically to requested/local target `EUROPA` and metric-entry domain `JUPITER_SYSTEM`.

Navigator plans metric flight toward the moving Jupiter-system boundary. Before a candidate metric segment is accepted, it is checked against applicable moving exclusion domains. After qualified collapse, ordinary-space/local navigation continues to Europa.

## Geometry contract

Do not persist copied boundary-center coordinates for Mara.

At epoch `t`:

`boundary(body,t) = ephemeris_position(body,t) + selected_domain_geometry(body)`

Candidate A/B/C radii remain diagnostic inputs until governed physics selects an active rule.

## First deterministic obstacle seam

`src/loom_metric_domain_intersection.py` answers only:

> Does this already-proposed metric segment intersect an exclusion sphere whose center moves between the same two ephemeris epochs?

For the first seam, both ship and domain center are linearly interpolated across one matching time interval. Minimum relative separation is solved analytically, so a moving body crossing the ship path between endpoint samples is detected.

The checker returns blocking domain IDs. It does **not** generate a detour. A later Navigator route solver may use this checker while searching candidate paths.

Regulatory override suppresses regulatory blockers only. Physical blockers remain blockers.

## Fail-closed boundary

Trajectory and domain epochs must match exactly at this seam. If they do not, the checker refuses the comparison rather than silently interpolating unrelated ephemeris intervals. The authoritative ephemeris/navigation layer must supply aligned states first.

## Explicit non-scope

- no A/B/C radius selected or canonized;
- no ephemeris implementation duplicated;
- no route-around/detour algorithm yet;
- no HUD/UI work;
- no campaign mutation;
- no Mara numerical authority;
- no SQLite/schema/launcher/release-manifest change.

## Dependency / compatibility disposition

- Navigator / runtime campaign core: `REVALIDATION_REQUIRED` before promotion because this is new runtime navigation behavior.
- GIS/HUD presentation: `UNCHANGED_COMPATIBLE`; no presentation contract changed.
- world/CIVSTATE SQLite: `UNCHANGED_COMPATIBLE`; no bytes/schema changed.
- Pixel/Windows launchers/updater: `UNCHANGED_COMPATIBLE`; no launcher/update behavior changed.
- release manifest: unchanged; this branch is not a production release.

## Test evidence

Tests were committed before the moving-domain implementation. A local isolated Python unit check of the same intersection mathematics passed six initial cases: clear path, stationary blocker, moving blocker between endpoints, regulatory override, physical non-override, and epoch mismatch. Repository tests additionally cover routing hierarchy cycles, missing metric ancestors, and negative radius. This is development evidence only; it is not production/Pixel qualification and is not transferred to different future bytes.

Rollback is branch/PR reversion to the pre-seam `main` base `dedc6db83d2ed4f1ee369ac5ec0e02b6f2807b07`.
