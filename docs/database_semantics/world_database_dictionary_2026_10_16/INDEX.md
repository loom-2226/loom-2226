# LOOM World Database Dictionary - 2026-10-16

Docs-only Build 8 snapshot from LOOM_ALL_DATABASES_SCHEMA_DICTIONARY.zip.
Non-runtime, non-canon, non-qualification. Do not execute reference material.
Source ZIP SHA-256: 17cc6d63ef08848e725deee524a2d7d19570063391771611e65308dc64a1b76c
All 51 package member bytes preserved exactly. Six .sql filenames are
renamed with a .txt suffix to prevent discovery by SQL migration tools.
The original manifest.json and its SHA-256 entries are unchanged.
For renamed SQL, map original .sql to .sql.txt when checking hashes.

## Folder map

| Folder | Coverage |
| --- | --- |
| earth/ | Live PostgreSQL 16 Earth 2026-2226 schema and data dictionary |
| build7/ | Live PostgreSQL 16 loom_offworld_runtime schema and Build 7 metadata |
| world_authority/ | Authored PostgreSQL 18 reference DDL and contracts |
| world_authority_reference/ | Duplicated reference DDL and contracts from earlier package |
| world_authority_qualified_20261006/ | October 6 PostgreSQL 18.6 qualification snapshot only |
| civstate/ | Legacy SQLite CIVSTATE schema and absent PostgreSQL loom_civ status |
| server_inventory/ | Accessible PostgreSQL 16 database inventory; incomplete Docker inventory |
| semantic_reference_legacy/ | Older dictionary evidence, not newly recovered Earth definitions |
| previous_manifests/ | Earlier Earth and Build 7 manifests and readmes, retained as sources |

## Critical limits

- PG18 World Authority: qualified October 6, 2026 only; NOT checked against live service.
- Earth has 0 column definitions and 21 variable definitions in captured semantic records.
- CIVSTATE: legacy material, not a live PostgreSQL target.
- Docker databases remain unidentified; listener ports are not identities.
- Build 7 counts are connection-visible counts under access/RLS, not proof of totals.
- Source documentation is not a claim that missing semantic interpretations have been recovered.

## SQL files: reference only (filename changes)

- build7/live_full_schema.sql -> build7/live_full_schema.sql.txt
- build7/migration_002_REFERENCE_ONLY.sql -> build7/migration_002_REFERENCE_ONLY.sql.txt
- civstate/legacy_sqlite_schema_REFERENCE_ONLY.sql -> civstate/legacy_sqlite_schema_REFERENCE_ONLY.sql.txt
- earth/live_schema.sql -> earth/live_schema.sql.txt
- world_authority/REFERENCE_SCHEMA_DO_NOT_EXECUTE.sql -> world_authority/REFERENCE_SCHEMA_DO_NOT_EXECUTE.sql.txt
- world_authority_reference/migration_001_DO_NOT_EXECUTE.sql -> world_authority_reference/migration_001_DO_NOT_EXECUTE.sql.txt

No SQL file in this snapshot is intended for execution or migration.

## Preserved duplicates and previous manifests

The World Authority semantic contract, store interface, domain manifest and
migration-001 SQL in world_authority/ and world_authority_reference/ are
byte-identical, verified by SHA-256. Both copies remain as supplied.
previous_manifests/ preserves the earlier scoped manifests and READMEs.
Their historical scope differs; no byte conflict was detected.

## Leak guard / provenance

All 51 source files scanned as UTF-8; checked for private-key PEM markers,
API/token signatures, authenticated connection strings, explicit secret
assignments, inserted SQL data/COPY, database or row-export formats, and
hidden-world data-file shapes. Source archive CRC and 50 listed per-file
manifest SHA-256 values verified. Four overlapping files compared bytewise.
Result: 0 secret/hidden-row scan hits; 0 duplicate content conflicts.
This is a content-shape/pattern screen, not a proof concerning all prose.

No existing frozen path, test, CI, pin, placeholder or kernel file changed.
Only the existing docs/database_semantics/README.md receives one index link.

