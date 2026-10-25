# PR A — Reference geometry and authority audit v0.1

**Status:** PARTIAL BASELINE EVIDENCE / NON-CANON / NO GEOMETRY CHANGE. Date: 2026-09-17.

## Inputs and provenance

- Governing source chain: Canon II v2.4, schematic v2.4a, `geometry/wayfarer_geometry_seed.sql`, `src/wayfarer_geometry.py`; GLBs are derivatives.
- Inspected user-provided local binary inputs with trimesh scene geometry and node transforms: `WAYFARER_E1_TORCH_STANDALONE.glb`, `wayfarer_with_system_rcs.glb`, `wayfarer_e1_metric_integration_candidate.glb`. These bytes are not claimed to exist in GitHub. Full SHA-256 manifest remains pending.
- Current deterministic seed: ship length 57 m; four quadrature tanks x18–32 m, external diameter 3.0 m, radial center 2.7 m; nozzle x50–57 m. Tank dimensions are DESIGN_BASELINE; 250 t normal remass plus 50 t protected water is governing inventory.

## Measured world-space GLB geometry

| Input | Scene node count (trimesh graph nodes) | X bounds (m) | Tank identities |
|---|---:|---|---|
| Standalone torch | 17 | 37.96–58.00 | Not a tank assembly |
| RCS ship | 40 | 0–57.00 | tank_1 through tank_4, each x18–32 |
| Metric integration | 372 | 0–58.00 | tank_1 through tank_4, each x18–32 |

**57/58 m root cause localized:** standalone torch `PRIMARY_THRUST_AXIS` visualization/line geometry runs x38–58 m; `NOZZLE_EXIT_INTERFACE` spans x56.96–57.04 m. Both are present in metric integration. The nominal nozzle end in source remains x57 m. These visualization/interface elements account for the reported x58 m mesh extent; do not silently rescale or trim them until their semantic purpose is checked against the torch handoff. The RCS ship does not include these overhanging torch markers.

The four tank nodes have transverse AABB sectors around y,z = ±0.41 to ±3.41 m, consistent with four quadrature positions. This is bounding-box evidence, not proof of finite separation from the launch-bay swept extraction envelope or full physical tank capacity.

## Authority and unresolved decisions

- E1 primary torch **vehicle interface is frozen**, but reactor, remass species, feed hardware, physical nozzle/plume and component hardware are not certified. Do not redesign torch.
- Recovered Shipyard Phases 9–11 selected no physical feed topology; pump/header-conditioned feed is a modeling priority, not a selected installation.
- Do not equate 250 t of normal remass to four fully usable 14 m × 3 m tanks without density, ullage, endcaps, shell and feed-residual accounting. Protected 50 t reserve remains separately accounted and cannot be assumed to occupy normal remass volume.
- No physical tank geometry or drivetrain geometry was changed in this audit.

## Remaining PR A gates

1. Produce byte SHA-256 and sizes for all three exact reference GLBs; record source-generator identity where available.
2. Inspect all scene node paths, local/world transforms and complete collision/sweep envelope; verify torch marker semantic tags.
3. Inspect actual Shipyard Phase 9–11 artifacts and test contracts; identify baseline executable tests before any design edits.
4. Reconcile source seed, torch interface document and any alternate generator/GLB source hashes; produce PR B handoff.

**Disposition:** `BASELINE_PARTIAL_MEASURED; GEOMETRY_UNCHANGED; TANK_CAPACITY_AND_FEED_OPEN`. No PASS claim for spatial closure or component certification.
