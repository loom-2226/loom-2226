# LOOM Production Database Semantic Dossier v0.1

**Change class:** `class:data` — documentation only  
**Scope:** `data/LOOM_2226_CIVSTATE.sqlite3` and `data/LOOM_2226.sqlite3`  
**Work item:** #115

## Mandatory interpretation rule

**Do not infer intended semantics from table names, column names, correlations, distributions, or apparent graph topology.** Schema/value behavior may establish storage structure and empirical variation only. Intended meaning must trace to repository evidence or explicit database self-documentation whose provenance is itself preserved. If it cannot be traced, treat it as unresolved.

This front file is the mandatory entry point. The exhaustive generated dossier and machine-readable index live beside it in this directory.

## Coverage

The verified 2026-09-06 runtime inventory reports **53 CIVSTATE tables and 42 core-world tables = 95 tables total**. This differs from the initiating work order's 43-table core count. The discrepancy is preserved rather than silently normalized. Any later current-main inventory showing an additional core table must be added before claiming coverage of that later schema.

## Status vocabulary

- `UNDERSTOOD`: semantics traced to repository/self-documenting evidence.
- `PARTIALLY_UNDERSTOOD`: purpose evidenced, one or more field meanings untraced.
- `NOT_UNDERSTOOD`: current evidence does not justify interpretation.

`NOT_UNDERSTOOD` is a stop sign for semantic inference, not an invitation to guess.

## Evidence order

1. generating builder/migration or frozen specification;
2. explicit methodology / derivation / audit / variable-semantics text;
3. source manifests and assumptions;
4. recoverable commit/PR history and authoritative consumer contracts;
5. schema/value behavior for verification only, never as a substitute for intended semantics.

## Known failure classes this contract is designed to prevent

- regional/group constants misread as local differentiators;
- generated symmetry misread as reciprocal real-world dependency;
- proxies misread as literal physical counts;
- organization-scope facts projected into individual-scope facts;
- identifier transcription errors;
- cross-boundary facts misread as boundary-dependent facts;
- absence inferred from schema that was never queried;
- semantic meaning inferred from a column name alone.

## Files

- `LOOM_DATABASE_SEMANTIC_DOSSIER_FULL_v0.1.md` — exhaustive table-by-table coverage, including all CIVSTATE columns and explicit unresolved markers.
- `LOOM_DATABASE_SEMANTIC_INDEX_v0.1.json` — machine-readable coverage/status index.

## Important limitation of v0.1

The GitHub connector cannot decode the binary core-world SQLite payload directly. The preserved runtime inventory establishes the current 42-table core set, and GitHub source establishes selected contracts, but many core column contracts remain unresolved. They are explicitly marked `NOT_UNDERSTOOD` rather than invented. Closing those gaps requires recovering the generating builder/migration or a schema inventory with authoritative semantic evidence.

The CIVSTATE half is substantially richer because the database itself preserves `civ_variable_semantics`, `civ_derivation`, `civ_methodology_note`, `civ_assumption`, and `civ_readiness_audit`; those texts are carried into the full dossier without upgrading undocumented fields by inference.
