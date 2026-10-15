# LOOM World Authority + Earth 2026-2226

Schema/semantics reference ONLY. No simulation-world rows or backups.

Earth: extracted live from PostgreSQL 16 database loom_dev.
Namespaces: loom_earth, loom_control, loom_narrator, loom_timeline.
- live_schema.sql: DDL (tables, views, indexes, types, keys, functions).
- catalog.json: relational column/constraint/index metadata.
- semantic_definitions.json: selected descriptive records from the
  ONLY permitted data-dictionary tables: field_semantics and
  variable_semantics under loom_control.

World Authority: source migration DDL hash-verified against its pinned
domain manifest, NOT verified against a live PostgreSQL 18 cluster.
- REFERENCE_SCHEMA_DO_NOT_EXECUTE.sql: READ AS REFERENCE ONLY.
- source_to_target_dictionary.csv: legacy-to-authority field semantics.
- SEMANTIC_CONTRACT.md, STORE_INTERFACE.md: meaning and constraints.

NEVER execute schema SQL as part of analysis. Never infer meaning,
units, provenance or epistemic standing solely from names. REAL science,
SCENARIO hidden WORLD truth and REALIZED observations stay separate.
Unknown meaning remains unknown; this package does not authorize runtime
behavior. No hidden values, physical-state records or credentials are
intentionally included.
