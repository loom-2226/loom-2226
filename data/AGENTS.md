# Data subtree agent rules

Applies to `data/**`.

## Authority

Repository databases and data files may be authoritative for declared runtime state, but storage location does not make them canon.

Before mutation:

- identify source-of-truth and derived fields;
- declare schema/migration impact;
- identify runtime, Navigator, media and release consumers;
- preserve recovery/rollback path;
- update compatibility metadata when required.

## Semantic interpretation — mandatory

Before interpreting `LOOM_2226.sqlite3` or `LOOM_2226_CIVSTATE.sqlite3`, read:

- `docs/database_semantics/LOOM_DATABASE_SEMANTIC_DOSSIER_v0.1.md`
- `docs/database_semantics/LOOM_DATABASE_SEMANTIC_DOSSIER_FULL_v0.1.md`
- `docs/database_semantics/LOOM_DATABASE_SEMANTIC_INDEX_v0.1.json`
- `docs/database_semantics/CLAUDE_DATABASE_INTERPRETATION_CONTRACT_v0.1.md`

Do not infer intended semantics from table names, column names, correlations, distributions, or apparent graph topology. Schema/value behavior may verify structure or variation but does not establish intended meaning. If the semantic dossier marks a field/table unresolved, preserve that status until generating builder/migration, methodology/derivation/audit text, source documentation, or an authoritative consumer contract closes it.

For CIVSTATE, consult `civ_variable_semantics`, `civ_derivation`, `civ_methodology_note`, `civ_assumption`, and `civ_readiness_audit` before interpreting unfamiliar fields.

## SQLite discipline

- do not manually patch production SQLite as a substitute for a governed migration when a migration is required;
- distinguish repository database bytes from release-asset bytes;
- record hashes for released baselines;
- preserve local user/campaign state where deployment policy requires it;
- never infer that a local Pixel/Windows DB is the governing repository baseline merely because it is newer.

## Testing

Schema/data changes require migration/compatibility tests appropriate to the affected consumers.

## Adoption pause

While Governance Adoption remains active, SQLite bytes/schema changes are forbidden.
