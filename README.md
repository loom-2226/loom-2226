# LOOM 2226

Private source, canon, data, validation, and deployment repository for LOOM 2226.

## Current Earth economic baseline

`EARTH_LONG_RUN_ECONOMIC_BASELINE_v3_REPAIRED_2026_09_23` is the current numerically qualified Earth 2060–2226 economic reference on quantifactus. Resolve it through [the current pointer](manifests/earth_long_run_economic_baseline/EARTH_LONG_RUN_ECONOMIC_BASELINE_CURRENT.json) and the hash-checking resolver in `manifests/earth_long_run_economic_baseline/earth_baseline_integration_2026_09_23/earth_baseline_resolver.py`. The [versioned baseline record](manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v3_repaired_2026_09_23/BASELINE_DECISION.md) contains its model, provenance, validation and compact results. Large annual outputs and checkpoint remain hash-pinned on quantifactus. The previous v2 baseline remains intact for rollback. This is an economic scenario, not canon or physical-capacity data.

The repository is being established from the validated 2026-09-03 runtime baseline.

Current top-level areas:

- `src/` — executable Navigator and Solar GIS source
- `data/` — canonical runtime databases small enough for ordinary Git distribution
- `deploy/` — Android/Windows updater and deployment tooling
- `tests/` — deployment and runtime regression tests
- `manifests/` — pinned hashes, schema locks, release provenance, and baseline records

Large binary runtime assets, including `LOOM_2226_media.sqlite3`, are distributed through GitHub Releases and pinned in the release manifest by asset ID, byte size, and SHA-256.

Mutable campaign state, history, caches, generated reports, and local credentials are not canonical repository content and must not be overwritten by normal updates.

The next repository expansion will ingest the authoritative LOOM canon, engineering, simulation, research, and governance source corpus under explicit version control.
