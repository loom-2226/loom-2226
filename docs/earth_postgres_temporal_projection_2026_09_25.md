# Earth PostgreSQL temporal projection

This class:data projection is an immutable PostgreSQL query surface over the
promoted Git authority. It does not become canon or an independent model
authority. The validated snapshot is `earth-v0-1-9934d0ac-20260925`.

The timeline uses WPP 2024 Medium Jan-1 age/sex data for 2026–2100 and the
selected `MED_CENTRAL__SYNTH_CENTRAL` coupled successor from 2101–2226.
2100 is retained as the explicit handoff boundary. Historical employment is
stored separately from post-2100 biological effective labor. Synthetic-person
facts are unavailable before their modeled boundary; NULL means
`NOT_MODELED_BY_THIS_AUTHORITY`, not zero.

The exact detailed post-2100 economic rows were materialized once by replaying
the promoted runner with `summary_only=false`; their hashes are in the
snapshot source registry and the staging import manifest. The projection
contains 237 demographic areas, 80 qualified economic economies, annual sector
and asset rows, embedded semantic definitions, model context, temporal
coverage, source hashes, and narrator views under `loom_narrator`.

The prior accepted Ceres snapshot remains unchanged. A durable custom-format
backup is recorded in `data/postgres/earth_temporal_projection_manifest.json`.
Disposable restore was not possible because the local PostgreSQL role lacks
`CREATEDB` permission.
