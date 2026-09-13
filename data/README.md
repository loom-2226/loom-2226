# Canonical data payloads

Upload canonical release SQLite databases into this directory on the staging branch.

Initial baseline expects:

- `LOOM_2226.sqlite3`
- `LOOM_2226_CIVSTATE.sqlite3`

Do not upload mutable campaign saves, history, caches, or generated output here.

Before promotion to `main`, every binary payload must match the SHA-256 recorded in `manifests/INITIAL_BASELINE.md`.

## Semantic contract — mandatory before interpretation

Before interpreting tables or fields in either production database, read:

- `docs/database_semantics/LOOM_DATABASE_SEMANTIC_DOSSIER_v0.1.md`
- `docs/database_semantics/LOOM_DATABASE_SEMANTIC_INDEX_v0.1.json`
- `docs/database_semantics/CLAUDE_DATABASE_INTERPRETATION_CONTRACT_v0.1.md`

Do not infer intended semantics from table/column names, correlations, value distributions, or apparent graph topology. If the semantic contract is unresolved, treat the field as unresolved rather than guessing.
