# Provenance of Semantic Dossier v0.1

The dossier was assembled from repository authority plus preserved runtime inventory/database self-documentation. It does not treat chat memory as authority.

## Repository authority loaded

- `LOOM_START_HERE.md`
- `AGENTS.md`
- `data/AGENTS.md`
- `governance/current/LOOM_CURRENT_WORKSTATE.yml`
- `governance/current/LOOM_PROJECT_STATUS_2026-09-12.yml`
- `governance/current/LOOM_CHANGE_CONTROL_v1.0.md`

Current operations are governed and `main` is protected; this work is `class:data`, documentation-only, issue #115.

## Production payload identity

Preserved runtime inventory records:

- `data/LOOM_2226.sqlite3` — 4,882,432 bytes; SHA-256 `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde` at the 2026-09-06 installed baseline.
- `data/LOOM_2226_CIVSTATE.sqlite3` — 8,093,696 bytes; SHA-256 `9ef530bdc1b8d867fe217a8c6d3a05e3926b0b09b0d66a91ce090b3e52fae560`.

The main-repository release manifest separately records the corrected world-database SHA for the repository payload. Hash identity is provenance, not semantic evidence.

## Semantic evidence used

- repository source consumers including Navigator/GIS/media code;
- preserved runtime inventory table/schema evidence;
- CIVSTATE self-documentation tables: `civ_variable_semantics`, `civ_derivation`, `civ_methodology_note`, `civ_assumption`, `civ_readiness_audit`;
- prior database/graph audits only where they report structure and are not used to invent intended semantics.

## Explicit non-evidence

The following are never sufficient by themselves to establish intended semantics:

- a table or column name;
- a value distribution;
- a correlation;
- symmetry;
- co-location;
- a graph path;
- a null/non-null pattern;
- a model score that merely sounds interpretable.
