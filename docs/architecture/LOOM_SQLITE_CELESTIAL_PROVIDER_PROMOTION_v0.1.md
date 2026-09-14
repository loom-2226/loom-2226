# LOOM SQLite Celestial Provider Promotion v0.1

**Class:** runtime

## Purpose

Promote the read-only celestial-data adapter needed to connect the shared celestial-state authority to current LOOM SQLite authority.

## Contract

`SQLiteCelestialCatalog`:
- opens the database read-only and `query_only`;
- returns only exact `J2000/ECLIPTIC` navigation-grade rows from `states` as direct authority;
- never promotes display-only rows;
- may derive a parent-centric two-body propagation model only from a stored navigation-grade local ephemeris anchor;
- gets parent GM from the existing celestial property/dynamics tables;
- marks propagated child state non-navigation-grade through the shared state authority;
- fails closed when required body, parent, GM, frame, units, or genuine anchor are unavailable.

## Deliberate non-scope

- no interpolation of major-body states between stored epochs yet;
- no new ephemeris generation;
- no metric-domain radius policy;
- no moving-domain hydration adapter yet;
- no route generation/detour solver;
- no HUD/GIS changes;
- no campaign mutation;
- no Mara numerical authority.

## Next seam

After this provider is green and merged, add a small metric-domain hydration adapter that resolves each protected body's center at the exact trajectory-leg start/end epochs and emits aligned `MovingDomainSegment` values for the PR #118 route checker. If current SQLite coverage cannot resolve those exact epochs, promote the already-existing qualified interpolation seam separately rather than weakening this provider.
