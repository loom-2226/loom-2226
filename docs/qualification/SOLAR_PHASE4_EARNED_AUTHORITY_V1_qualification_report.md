# Solar Phase-4 Earned Authority V1 qualification

**Result:** PASS FOR EARNED-AUTHORITY PROMOTION
**Overall Phase-4 2250 gate:** NOT YET COMPLETE
**Primary change class:** `class:data` with supporting `class:engineering` adapter/tests
**Date:** 2026-09-25

## Scope

This promotion recovers and governs Solar authority that had already been earned
before the Phase-4 2250 completion expansion.

It does not claim that the entire Solar Phase-4 horizon is complete.

Manifest:

`manifests/solar/SOLAR_PHASE4_EARNED_AUTHORITY_V1.json`

Forward migration:

`data/postgres/migrations/012_solar_phase4_earned_authority.sql`

## Promoted authority

19 exact targets are registered:

- 14 DE440 targets: NAIF 1-10 system/barycenter/Sun targets plus Mercury 199,
  Venus 299, Moon 301 and Earth 399;
- Ceres 20000001 using the previously qualified JPL/Horizons SPK;
- Mars 499 using MAR099;
- Saturn 699 using SAT441;
- Uranus 799 using URA184 part 3;
- Neptune 899 using NEP097.

Physical centers and system barycenters are separate identities. Jupiter and Pluto
physical centers are intentionally absent from this earned set; only their DE440
system barycenters are promoted.

## Source lineage

The promotion consumes existing qualification evidence rather than inventing new
authority from kernel contents:

- `EPHEMERIS_FOUNDATION_V1` frozen evidence;
- `OFFICIAL_PLANET_CENTERS_V1` recovered local qualification evidence;
- exact pinned kernel assets/hashes recorded in the merged manifest.

The adapter also verifies that the selected primary source asset actually contains
the requested NAIF target at the requested epoch. Metadata cannot grant object
coverage that the selected SPK does not physically contain.

## 2250 gate status

The Phase-4 horizon gate is defined as coverage through at least
`2251-01-01T00:00:00Z`.

Of the 19 promoted targets:

- **17** already satisfy the full 2026-through-2250 gate;
- **Ceres** remains partial because its current qualified SPK ends at the end of 2226;
- **Saturn physical center** remains partial because SAT441 ends on 2250-01-05.

Separately, Jupiter 599 and Pluto 999 physical centers remain Phase-4 holes because
the currently inspected generic system kernels do not reach 2250.

## Qualification

Targeted local qualification:

- original Solar SPICE/contract suite: PASS;
- recovered official planet-center suite: PASS;
- new earned-authority manifest/identity/horizon tests: PASS;
- all 19 promoted targets resolve at 2026 and 2226 from pinned local assets;
- the 17 full-horizon targets resolve at `2250-12-31T23:59:59Z`;
- Ceres and Saturn correctly fail closed at that end-of-2250 instant under their
  current promoted sources;
- PostgreSQL migration/round-trip qualification: required before PR promotion and
  recorded by the final PR test result.

## Does not establish

This promotion does not establish:

- Phase-4 completion;
- Jupiter or Pluto physical-center authority through 2250;
- object-level qualification for moons merely present inside installed kernels;
- resource abundance/extractability claims;
- navigation-grade long-tail small-body propagation;
- a complete empirical Solar catalog.

Those are governed by
`LOOM_SOLAR_PHASE4_2250_COMPLETION_WORKPLAN_v1.0.md`.
