# LOOM Production Database Data Dictionary

This directory is the production data-contract documentation for the LOOM world databases.

## Start here

- `tools/build_database_data_dictionary.py` — exhaustive dictionary generator.
- `tests/test_database_data_dictionary.py` — proves every current production table/column is represented.
- `LOOM_DATABASE_SEMANTIC_INDEX_v0.1.json` — verified production table inventory.
- `CLAUDE_DATABASE_INTERPRETATION_CONTRACT_v0.1.md` — mandatory interpretation rules for agents.
- `recovery/LOOM_CIVSTATE_RECOVERY_CONSOLIDATION_v1.0.md` — consolidated Phase-13/economic/social/texture recovery evidence.
- `SEMANTIC_DOSSIER_ACCEPTANCE_v1.0.md` — v1 acceptance and coverage statement.

The exhaustive production dictionary covers the verified runtime inventory:

- `LOOM_2226.sqlite3`: **42 tables / 457 columns**
- `LOOM_2226_CIVSTATE.sqlite3`: **53 tables / 557 columns**
- total: **95 tables / 1,014 columns**

The initiating work order said 43 core tables. Verified runtime inventory contains 42. Do not invent a 43rd table.

## Primary question

For every field:

> **What exactly is this field, at what row grain, in what units/domain, how is it generated, and how does it join?**

Every production field is represented. Unknown meaning is not grounds for omission.

## Recovery statuses

- `RECOVERED_EXACT` — explicit preserved definition/formula contract, or exact complete verification consistent with preserved source lineage.
- `RECOVERED_STRUCTURAL` — storage/key/lookup meaning proven by schema or verified joins.
- `RECOVERED_PARTIAL` — useful intended domain recovered, but exact formula/unit/taxonomy remains incomplete.
- `RECOVERED_STORAGE_ONLY` — storage role is inventoried; intended semantic/generating meaning remains open. **This is not understood.**

## Phase-13 recovery — authority update

The exact historical checkpoint `LOOM_2226_CIVSTATE_Phase13_v0.1.sqlite3` has now been recovered and verified.

SHA-256:

`5cb7c3c9faa89dba6ff42500f2b70756a6f9f58027c7f6035df5cb447f186753`

This **supersedes** the earlier archaeology conclusion that the physical Phase-13 gameplay/sense-of-place checkpoint was missing.

Evidence order for **Phase-13 historical state**:

1. recovered Phase-13 SQLite checkpoint;
2. contemporary Phase-13 contrast/validation report;
3. later/current CIVSTATE for descendant/runtime comparison;
4. recovery archaeology;
5. inference.

The checkpoint recovers **state/output**, including Place DNA, social state, social pressures, governance profiles, influence edges and behavioral scaffolds. It does **not** establish that every source-code equation used by `GAMEPLAY2226` has been recovered.

For **current runtime values**, current production CIVSTATE remains authoritative.

## CIVSTATE evidence routing

Before interpreting unfamiliar CIVSTATE fields, route evidence through:

1. `civ_variable_semantics`
2. `civ_readiness_audit`
3. `civ_derivation`
4. `civ_methodology_note`
5. `civ_assumption`
6. recovered generating builder/migration where available
7. historical checkpoint evidence where relevant

Evidence belongs to the table/field it **describes**, not merely the table in which prose happens to be stored.

## Hard epistemic rule

Do not infer intended scientific, social, political, economic, physical, or gameplay meaning from identifiers, correlations, distributions, or apparent topology.

Approximate regression, correlation, or a plausible-looking equation is not a recovered definition.

A numerical generator is promoted to `RECOVERED_EXACT` only when supported by preserved source/methodology or exact complete verification consistent with the preserved source family.

## Major misuse warnings

- synthetic persons ≠ non-person machine-task equivalents;
- transport flow = annual corridor-demand proxy, not timetable/direct-service proof;
- actor exposure = influence/control/dependency, not ownership;
- census-node gateway relations do not transfer resident population;
- `berths_equivalent` is a throughput equivalent, not a literal berth count;
- summary statistics do not imply preserved underlying distributions;
- organization/facility scope does not become person scope;
- co-presence/shared facility does not establish a person-person relationship;
- cross-boundary fact ≠ boundary-dependent fact;
- current stored state may be usable even when its original generator remains unresolved.

## Generator and tests

The source-controlled dictionary is deliberately generated from the two production SQLite schemas plus maintained field definitions and routed self-documentation:

```bash
python tools/build_database_data_dictionary.py
python -m pytest tests/test_database_data_dictionary.py tests/test_database_semantic_coverage.py
```

The generator emits exhaustive Markdown and JSON dictionaries and never drops an unresolved field. The tests independently enumerate the SQLite schemas and fail if any production field is omitted.

This documentation is subordinate to governed canon/data/engineering authority and does not promote database contents to canon.
