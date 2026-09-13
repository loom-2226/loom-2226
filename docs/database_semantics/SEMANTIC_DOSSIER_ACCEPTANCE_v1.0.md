# LOOM Production Database Data Dictionary — Acceptance v1.0

**Work item:** #115  
**PR:** #116  
**Class:** `class:data` documentation only  
**Runtime/schema mutation:** NONE

## Verdict

**ACCEPTANCE COMPLETE for the production data-dictionary contract, subject to repository CI / `loom-gate`.**

The dictionary is complete in the epistemic sense required by this work item: every current production field is represented, and fields whose intended semantics remain unrecovered are explicitly carried as unresolved rather than guessed.

## Verified coverage

Current production runtime inventory:

| Database | Tables | Columns |
|---|---:|---:|
| `LOOM_2226.sqlite3` | 42 | 457 |
| `LOOM_2226_CIVSTATE.sqlite3` | 53 | 557 |
| **Total** | **95** | **1,014** |

The original work order said 43 core-world tables. Verified runtime inventory contains 42; no fictitious 43rd table is added.

## Acceptance criteria

- [x] all 95 production tables represented;
- [x] all 1,014 current production columns represented by the exhaustive generator;
- [x] table row counts and declared primary-key structure inventoried;
- [x] per-field SQLite storage type inventoried;
- [x] exact/structural/partial/storage-only recovery status assigned rather than silently omitting unknown fields;
- [x] units/domain/generation/join semantics included where recovered;
- [x] explicit misuse warnings preserved for high-risk fields;
- [x] CIVSTATE self-documentation routed from `civ_variable_semantics`, `civ_readiness_audit`, `civ_derivation`, `civ_methodology_note`, and `civ_assumption`;
- [x] machine-readable production semantic index present;
- [x] exhaustive schema-coverage tests independently enumerate both SQLite databases and fail if a field is omitted;
- [x] definition-registry tests reject entries that do not resolve to a real production table/column;
- [x] unresolved entries preserve the evidence required to close them rather than manufacturing meaning;
- [x] Phase-13 historical authority correction documented after physical checkpoint recovery;
- [x] recovered economic/materialization lineage incorporated into interpretation contract;
- [x] recovered social/place/texture exact relationships incorporated into interpretation contract;
- [x] approximate regression explicitly prohibited as a recovered definition;
- [ ] repository CI / `loom-gate` at final PR head — must pass before merge.

## Phase-13 recovery change

The exact recovered historical checkpoint is:

`LOOM_2226_CIVSTATE_Phase13_v0.1.sqlite3`

SHA-256:

`5cb7c3c9faa89dba6ff42500f2b70756a6f9f58027c7f6035df5cb447f186753`

This changes the historical-evidence boundary:

- Phase-13 state/output is physically recovered;
- the complete original source-code equation set for all `GAMEPLAY2226` fields is still incompletely recovered;
- current production CIVSTATE remains authoritative for current runtime values.

## What “complete” does not mean

Completeness does **not** mean every field has an exact scientific/gameplay semantic definition.

`RECOVERED_STORAGE_ONLY` is an intentional and valid outcome. It means:

> the field exists, its storage contract is documented, and the intended semantic/generating definition is not yet supported strongly enough to state.

This is preferable to semantic invention and satisfies the project's primary safety requirement: **no production field disappears merely because we do not yet understand it.**

## Required pre-merge gate

Run:

```bash
python -m pytest tests/test_database_data_dictionary.py tests/test_database_semantic_coverage.py
python tools/build_database_data_dictionary.py
# normal repository loom-gate / CI follows
```

Merge is authorized only after the final PR head passes required checks.
