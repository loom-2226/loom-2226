# LOOM World Authority V1 installation and qualification

World Authority is independently governed class:data. Its durable domain is `data/world_authority/` and `src/loom_world_authority/`. Build 6E is a future consumer; no Build 6E runtime is included here. The owner explicitly included deterministic source ETL in this Sprint 1 continuation.

Use one dedicated database named `loom_world_authority`: PostgreSQL 18, UTF8, C collation/ctype, UTC, and `standard_conforming_strings=on`. Never append this migration to the unrelated Earth/Ceres/Solar migration chain. Existing cluster roles, wa_* schemas or pgcrypto cause atomic installation failure. Use server-major-matched `psql -X -v ON_ERROR_STOP=1` as the trusted installer. The migration runs in one transaction. Its only correction to the reviewed initial work is `RESET ROLE` immediately before installer-owned pgcrypto PUBLIC EXECUTE revocation. It introduces no broader privileges. The manifest and dependency lock pin the corrected bytes.

Source: the accepted immutable Git snapshot `acd0eb9fada60a0d2509de6af8c23ec3df6c28d6`, Git path `simulation/offworld_mvp/world_science/lab_v0_1/LOOM_SOLAR_WORLD_SCIENCE_LAB_v0_1.sqlite3`, 1,056,768 bytes, SHA-256 `72ddfab0eb35fb5a86ecfd50d4bc939a982ffc1fe3362108036082298a57b777`. Open SQLite read-only/immutable. No research, source filtering, correction, scientific admission or runtime WORLD generation is performed.

`plan_sqlite_import` builds all 2,726 forensic rows, the complete 256-column map and 7,126 total target rows before database access. `import_exact_snapshot` uses a separately authenticated science-writer service and one SERIALIZABLE transaction. First load is all-or-nothing; a repeat verifies every declared cell and returns `ALREADY_MATCHED` without INSERT authority. Collisions or partial imports fail; no repair/upsert occurs. Source bytes are checked before and after planning/import. Original NULL/storage tags/text bytes/REAL bits survive. See `LOSSLESS_SOURCE_DISPOSITIONS.md` for the four source UNKNOWN explanatory texts that remain raw-only under the owner's explicit preservation instruction.

The designated qualifier requires explicit disposable Docker provisioning and a cached pinned PostgreSQL18 image. It never uses a production/default DSN. Example (authorized test environment only):

```sh
PYTHONPATH=src .venv/bin/python tools/qualify_world_authority.py \
  --provision-docker \
  --source /absolute/accepted/LOOM_SOLAR_WORLD_SCIENCE_LAB_v0_1.sqlite3 \
  --output /absolute/new/qualification-output \
  --ports 55440 55441
```

Two genuinely fresh clusters prove E01–E28; a disposable qualification database holds isolated synthetic fixtures for S01–S12 and neutral store API tests. Such admission/WORLD/history fixtures never enter the accepted migrated databases. The driver rejects skips, missing IDs, input/code drift and any test failure. It writes a protected operator connection file under `/tmp`; no credentials enter evidence or Agent data. The main qualification databases end with 880 assertion and 35 material candidates, zero admissions/extrapolations, and no WORLD/run/information state.

The qualifier retains its uniquely named test containers for inspection. Stop/remove only those explicitly created by this invocation once evidence review is complete; never touch existing LOOM PostgreSQL containers/databases. No deploy/promotion, branch, commit, push, merge or tag is performed.
