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