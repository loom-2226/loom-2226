# LOOM 2226 Pre-Convergence Runtime Freeze v1.0

Status: **FROZEN BASELINE / PHASE 0**

Date: 2026-09-03
Governing workstream: GIS / Navigator Convergence
Development branch: `feature/gis-navigator-convergence`

## Freeze authority

The qualified runtime baseline is preserved by Git tag and release:

- Tag: `v0.1.0-runtime-baseline`
- Tag commit: `97faaab2514835c8f45aee13f5ec6c2ff1b1cc4e`
- Release: `LOOM 2226 Runtime Baseline v0.1.0`
- Release ID: `381754456`

The convergence architecture document was added later on `main` at commit:

- `cb4635de5626634acbcb13e4cc161c32c8594820`

That commit changes documentation only and does not alter the frozen runtime.

## Qualified runtime artifacts

| Artifact | SHA-256 | Status |
|---|---|---|
| `src/loom_solar_gis.py` | `73812ccf8e71d913798e8e3ebb25d64937ba4491e5540d09e5b7e80f646d4f0a` | canonical stable-name source; byte-identical to RC8 compatibility copy |
| `src/loom_navigator_core.py` | `d2cdf9baa38ca314e7eb0ecb0cf5e746d0e39c13e77e1a3f41b1093c6a59200b` | canonical stable-name source; byte-identical to RC6.1 compatibility copy |
| Navigator Sequence K1 / H v2.4 | `d2cdf9baa38ca314e7eb0ecb0cf5e746d0e39c13e77e1a3f41b1093c6a59200b` | integrated in `loom_navigator_core.py`; not a separate runtime artifact |
| `data/LOOM_2226.sqlite3` | `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde` | canonical runtime database |
| `data/LOOM_2226_CIVSTATE.sqlite3` | `9ef530bdc1b8d867fe217a8c6d3a05e3926b0b09b0d66a91ce090b3e52fae560` | canonical CIVSTATE database |
| `LOOM_2226_media.sqlite3` | `286873428afbf30b91bdb2e71b55146ed5979873cfd6af69579c121b724eb038` | release asset 542245032 |
| `LOOM_Navigator_Visual_Design_B1_LOCKED_Package_v1.0.zip` | `6e7d2c5fcc675ba5bfeaf98920a62832203b9cf6bcdca3ff482ecec85b3cf852` | release asset 542357474 |

## Schema / compatibility locks

- CIVSTATE schema: `1.2-runtime`
- Mutable campaign state is preserved locally and is not replaced by updater operations unless explicitly requested.
- Navigator remains authoritative for navigation physics, route planning, execution and ephemeris.
- GIS remains visualization / interaction authority only.

## Preserved Pixel runtime evidence

Release `v0.1.0-runtime-baseline` contains:

- `LOOM_2226_Pixel_PreClean_Runtime_Archive_2026-09-03.zip`
- `LOOM_2226_Pixel_Loose_Project_Archive_2026-09-03.zip`
- locked B1 visual design package
- media database release asset

The existing release manifest preserves campaign state, browser report, current Navigator HTML and ephemeris cache across updater operations.

## Qualification inherited from validated baseline

The pre-convergence baseline records the following PASS results:

- Navigator MVP state / transaction / job / mass / history / guard suite
- Navigator K1 provider / live-binding / execution guards
- Navigator CIVSTATE hash / schema / token / context / read-only suite
- Solar GIS RC8 compile
- updater v0.3 regression suite

## Gate 0 status

**BASELINE FROZEN.**

The repository-side freeze is complete. The existing Pixel runtime and release archives preserve the qualified state. A new post-freeze Pixel smoke/qualification run should be recorded before any convergence change is promoted to production; development work proceeds only on `feature/gis-navigator-convergence` until then.
