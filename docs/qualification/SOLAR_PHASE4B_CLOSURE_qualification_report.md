# Solar Phase 4B Closure Qualification

**Date:** 2026-09-26  
**Class:** `class:engineering` with governed `class:data` promotion  
**Manifest:** `manifests/solar/SOLAR_PHASE4B_AUTHORITY_V1.json`  
**Horizon gate:** every required target reaches at least `2251-01-01T00:00:00Z`

## Result

PASS for the Phase 4B required target set. Ceres and Saturn are direct authoritative
SPKs. Jupiter, its four required moons, Pluto and Charon are explicit empirical
propagations from authoritative JUP365/PLU060 states. The propagation seam is
offline, deterministic, uncertainty-bearing and non-navigation-grade; it is not
direct JPL authority.

| Required target | NAIF | Accepted source | Actual coverage end | Capability |
|---|---:|---|---|---|
| Ceres | 20000001 | JPL/Horizons Ceres SPK | 2251-01-02T23:58:50.816Z | direct |
| Saturn | 699 | JPL/NAIF sat441xl_part-2 | 4500-01-17T23:58:50.817Z | direct |
| Jupiter | 599 | JUP365 + Phase-4B propagation | 2251-01-01T00:00:00.816Z | propagated after 2200 |
| Io | 501 | JUP365 + Phase-4B propagation | 2251-01-01T00:00:00.816Z | propagated after 2200 |
| Europa | 502 | JUP365 + Phase-4B propagation | 2251-01-01T00:00:00.816Z | propagated after 2200 |
| Ganymede | 503 | JUP365 + Phase-4B propagation | 2251-01-01T00:00:00.816Z | propagated after 2200 |
| Callisto | 504 | JUP365 + Phase-4B propagation | 2251-01-01T00:00:00.816Z | propagated after 2200 |
| Pluto | 999 | PLU060 + Phase-4B propagation | 2251-01-01T00:00:00.816Z | propagated after 2199-12-29 |
| Charon | 901 | PLU060 + Phase-4B propagation | 2251-01-01T00:00:00.816Z | propagated after 2199-12-29 |

All required targets resolved position and velocity at 2026, 2226, 2250-01-01,
and `2250-12-31T23:59:59Z`; repeated queries were deterministic; physical centers
remained distinct from barycenters 5 and 9; and post-coverage queries failed closed.
JUP365 and PLU060 overlap checks were performed at withheld epochs before their
handoff. The measured discrepancies and declared uncertainty bounds are retained
in the manifest/source metadata.

Source assets are hash-pinned in the manifest and remain outside PostgreSQL. The
PostgreSQL closure migration is `013_solar_phase4b_closure.sql`; it records 26
active bodies, 26 active identifiers and 33 qualified coverage rows including the
previously earned authority.
