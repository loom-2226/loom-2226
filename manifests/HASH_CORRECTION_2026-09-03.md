# Runtime Manifest Hash Correction — 2026-09-03

During the first clean Windows deployment test, the updater correctly rejected `data/LOOM_2226.sqlite3` because the release manifest contained a stale SHA-256 value.

The intended local source file and the bytes served by GitHub independently matched SHA-256:

`e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`

The CIVSTATE database was also independently checked locally and matched the manifest value:

`9ef530bdc1b8d867fe217a8c6d3a05e3926b0b09b0d66a91ce090b3e52fae560`

No runtime database bytes were changed. This correction updates only the stale world-database digest in `release_manifest.json`.
