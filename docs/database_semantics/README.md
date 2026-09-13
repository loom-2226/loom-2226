# LOOM Production Database Data Dictionary

This directory is the production **data dictionary** for `data/LOOM_2226.sqlite3` and `data/LOOM_2226_CIVSTATE.sqlite3`.

The primary question is concrete:

> **What exactly is this table/field, at what row grain, in what units/domain, how is it generated, and how does it join?**

Start with:

- `LOOM_DATABASE_DATA_DICTIONARY_v0.1.md` — generated human-readable dictionary.
- `LOOM_DATABASE_DATA_DICTIONARY_v0.1.json` — generated machine-readable dictionary.
- `DATA_DICTIONARY_FIELD_DEFINITIONS_v0.1.json` — maintained field-definition registry.
- `CLAUDE_DATABASE_INTERPRETATION_CONTRACT_v0.1.md` — misuse/scope guardrails for agents.

The generator is `tools/build_database_data_dictionary.py`. It inventories **every current table and every current column** directly from the two production SQLite files and combines that structural inventory with maintained field definitions.

Each column entry records, where available:

- declared SQLite type;
- primary-key position and nullability;
- foreign-key target;
- definition;
- unit;
- value scale/domain;
- data role (identifier, count, rate, score, weight, proxy, text, timestamp, etc.);
- generating rule/source;
- join notes.

If a definition has not yet been recovered, the dictionary must say `DEFINITION_NOT_RECOVERED`; the column is still listed and cannot disappear from coverage.

The older semantic-dossier files are recovery/audit scaffolding. They are not the primary deliverable.
