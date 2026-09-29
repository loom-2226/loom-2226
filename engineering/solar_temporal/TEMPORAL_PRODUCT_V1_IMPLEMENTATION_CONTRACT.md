# LOOM Solar Temporal Product v1 — Implementation Contract

Status: implementation authority for branch `engineering/solar-temporal-product-v1`; NON-CANON until governed merge.

## Goal
Integrate the proven temporal-state publication mechanism with the physical-Pixel-qualified progressive Solar basemap without creating a second celestial-mechanics authority.

## Time domain
- Required game interval: 2226-01-01 TDB through 2250-12-31 TDB.
- Publication/qualification target: through 2300-12-31 TDB where governed direct/propagated/best-estimate state is available.
- Partial coverage is explicit and permitted; no silent extrapolation beyond qualified validity.

## Authority invariant
PostgreSQL registry + governed resolver + SPICE/qualified propagation remain authority. Browser performs interpolation, hierarchy composition, LOD, camera and rendering only. No browser orbital propagation or visualization-only physical ellipses.

## Products
1. Existing progressive spatial basemap: hierarchy, identity, semantic/geometric LOD, cartography and provenance.
2. Temporal ephemeris product: object/center/frame, TDB samples with position+velocity, authority/provenance, validity, interpolation contract and uncertainty metadata.
3. Epoch-dependent cartographic reference geometry derived from the same governed resolver, independently qualified and LOD-controlled.

## Client contract
`state(object_id, epoch_et)` returns a qualified/interpolated state or an explicit unavailable result. Parent-relative states compose through the hierarchy. Arbitrary scrub/jump loads the containing temporal chunk; continuous play interpolates locally. Spatial and temporal refinement remain independent.

## Qualification
- source/identity disposition for all 110 governed catalog objects;
- interpolation checked at non-sample epochs against governed resolver;
- chunk seam continuity;
- parent-relative/world-coordinate invariants;
- deterministic byte-identical rebuild;
- no authority calls from browser;
- physical Pixel: play/pause, reverse, scrub/jump, accelerated time, Mars/Jupiter/Saturn local systems, zoom while time runs.

## Proven POC evidence
2026-09-29 physical Pixel POC demonstrated governed DIRECT and PROPAGATED timestamped states delivered to Pixel and interpolated/rendered client-side. Disposable POC is not production UI and is not an authority source.
