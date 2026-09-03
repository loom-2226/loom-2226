# LOOM 2226

Private source, canon, data, validation, and deployment repository for LOOM 2226.

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
