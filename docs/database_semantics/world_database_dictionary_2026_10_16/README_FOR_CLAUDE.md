# LOOM ALL DATABASES: SCHEMAS AND SEMANTIC METADATA

ONE consolidated package. Includes both previously generated archives' contents
plus fresh read-only PG16 inventories, Earth table counts, and legacy CIVSTATE
schema/reference material. No simulation or hidden-WORLD records exported.

COVERAGE:
* Earth live PG16: schema, catalog, 9 Earth table counts, known semantics.
* Build7 PG16: full live schema, security, RLS, extension inventory, migration 002.
* World Authority PG18.6: VERIFIED OCT 6 qualification schema fingerprint,
  77 tables, recorded source-export counts for 20 tables, grants, roles, RLS
  declarations, pgcrypto. NOT verified against the current live PG18 service.
* Ceres CIVSTATE PostgreSQL loom_civ: checked and marked ABSENT in the
  accessible loom_dev database. The separate SQLite CIVSTATE source schema and
  table counts are included as a fallback, not passed off as live PG.
* Host PG16 server: database names, owners, sizes, encoding; role attributes.
  Docker PostgreSQL listener ports: discovered without querying passwords
  or containers; unknown cluster identities explicitly marked UNKNOWN.
* Earth field_semantics contains 0 definitions. Variable semantics contains
  21; maintained legacy semantic docs are additional REFERENCE, NOT asserted
  as qualified Earth field definitions.

FIELD/VALUES FIREWALL:
No world-state rows, hidden physical values, deposits, science observation rows
or credentials. Schema, row counts, and schema/metadata fingerprints only.
Some older documentation may discuss semantics; do not reclassify hypotheses
as empirical fact or promote historical qualification into current authority.
See manifest.json for per-file SHA256 and explicit coverage limitations.
