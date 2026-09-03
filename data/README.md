# Canonical data payloads

Upload canonical release SQLite databases into this directory on the staging branch.

Initial baseline expects:

- `LOOM_2226.sqlite3`
- `LOOM_2226_CIVSTATE.sqlite3`

Do not upload mutable campaign saves, history, caches, or generated output here.

Before promotion to `main`, every binary payload must match the SHA-256 recorded in `manifests/INITIAL_BASELINE.md`.
