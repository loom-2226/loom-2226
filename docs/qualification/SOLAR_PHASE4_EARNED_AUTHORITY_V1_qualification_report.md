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
- disposable PostgreSQL migration/round-trip qualification: PASS;
- PR #281 targeted Solar qualification: 24 tests PASS with 2 environment-gated skips;
- PR #281 disposable PostgreSQL migration qualification: 11 tests PASS.

### Applied migration identity

Live `loom_dev` applied migration `012_solar_phase4_earned_authority` with SHA-256
`e8a452135bb867a7b0d8fd7afe57be927cb8b7f91aeced5a9307653b4e0a03e6`.

PR #282 briefly changed migration 012 after a concurrent live promotion had already
recorded that hash. The proposed hardening itself passed 12/12 disposable
PostgreSQL/contract tests, but mutating an applied migration is not an admissible
forward state. The repository therefore restores migration 012 to the exact applied
bytes/hash. Any further migration-safety hardening must use a new forward migration
or migration-runner contract rather than rewriting revision 012.

## Live promotion and restore qualification

Live `loom_dev` now contains 19 bodies, 19 governed NAIF identifiers, 6 qualified
sources and 19 qualified body-coverage records. Migration 012 in Git and PostgreSQL
has the same SHA-256:
`e8a452135bb867a7b0d8fd7afe57be927cb8b7f91aeced5a9307653b4e0a03e6`.

Durable recovery artifacts:

- pre-promotion dump: 79,732,097 bytes, SHA-256
  `7b4e320776b5f029b5ed4430ba5223b7998071ec8518d12e04f66e3de5419c6c`;
- post-promotion dump: 79,733,666 bytes, SHA-256
  `7f8cb0de63aa0d97e927fd87145c63d720b55393bbc58a2f8f46708e1b40bcd6`.

The post-promotion dump restored successfully with `--no-owner --no-privileges`.
On the restored database:

- Solar counts were exactly 19/19/6/19;
- migration 012 hash matched the live/applied identity;
- Earth matched the pre-Solar preservation contract exactly at overall SHA-256
  `fedcc9b69e2e585663f821109be93338ca4711d4654097588f431cb991154ebc`;
- Timeline remained `VALIDATED` with 43 milestones and 5 interpretation rules.

The final current-main live audit independently reproduced the same Earth fingerprint,
Timeline PASS, zero invalid LOOM constraints, and 21/21 SPICE/official-center tests.

Machine-readable record:
`docs/qualification/SOLAR_PHASE4_EARNED_AUTHORITY_V1_live_promotion.json`.

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
