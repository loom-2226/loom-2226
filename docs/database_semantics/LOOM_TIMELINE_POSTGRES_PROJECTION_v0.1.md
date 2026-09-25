# LOOM Timeline PostgreSQL Projection v0.1

**Date:** 2026-09-25  
**Primary class:** `class:data`  
**Status:** qualified development projection; no canon mutation  
**Snapshot:** `timeline-v0-1-0232bf23494f-20260925`

## Purpose

Preserve the LOOM chronology and technology opportunity scaffold as a typed PostgreSQL projection for future CIVPROP and other machine consumers without changing the authority of the source material.

PostgreSQL storage does not promote content. Authority remains source-derived:

- CANON I v2.4 chronology -> `GOVERNING_CANON`;
- Technology Timeline Register v0.1.1 practical/social/fictional scenario anchors -> `PROVISIONAL_SIMULATION_SCAFFOLD`.

## Sources

- `canon/current/LOOM_2226_CANON_I_World_History_Frontier_v2.4.md`
  - SHA-256 `98a83f50b68b68931ad24cfec97c347cc506901973d0e0787c09f2baa27cd3a6`
- `docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md`
  - SHA-256 `96c87881ca2f525b1de9fbfdb0aa3306c84dc0a76ae8c1c30ef4c972ae12f7eb`

Both are projected from protected `main` at `c0b50afdd792cecf0b32a8752855e5afa8694ddd`.

## Projection

`loom_timeline.milestone` contains 43 typed milestone rows:

- 19 canon-history milestone IDs mapped to the 18 governing CANON I chronology rows;
- 18 moderate practical capability anchors;
- 5 explicitly fictional-physics scenario anchors;
- 1 optional 2090 social scenario anchor with a projection-generated ID clearly marked as such.

The CANON I 2140–2190 chronology row has two stable source IDs in the Technology Timeline Register. The primary projection ID is `TRN-2140-TORCH-MATURE`; `IND-2140-OUTER` is preserved in `loom_timeline.milestone_alias`.

`loom_timeline.milestone_source` preserves governing-content, stable-ID-mapping and scenario-definition lineage separately.

## Interpretation controls

`loom_timeline.interpretation_rule` stores five exact source-backed rules, including:

- a date does not automatically unlock technology, capacity, access, profitability, migration or colonization;
- knowledge/demonstration, reliable design, installed capacity and actor access/adoption remain separate states;
- canon is a comparator rather than a destination for the forward simulation;
- missing quantities are `UNKNOWN`/null, not zero;
- capability demonstrated at one site does not create capacity at another.

Future CIVPROP consumers must pin a validated timeline snapshot and may not reinterpret scenario rows as canon.

## Qualification

Disposable PostgreSQL 16.15 qualification database: `loom_timeline_qualification`.

Results:

- migration chain through `010_timeline_projection` applied successfully;
- timeline snapshot imported and reached `VALIDATED`;
- 19 canon-history rows;
- 18 moderate scenario rows;
- 5 fictional-physics scenario rows;
- 1 social scenario row;
- 5 interpretation rules;
- authority sentinel: canon torch chronology remained `GOVERNING_CANON`;
- authority sentinel: `SPEC-MOD-METRIC-SHIP` remained `PROVISIONAL_SIMULATION_SCAFFOLD`;
- static timeline tests: 7/7 PASS;
- Solar PostgreSQL migration regression in a disposable database: 8/8 PASS;
- Earth schema-separation regression: 2/2 PASS;
- combined relevant regression: 17/17 PASS.

No CIVPROP equations, settlement generation, Earth model mutation, Solar ephemeris mutation, CIVSTATE mutation, or production consumer binding is introduced.

## Recovery

The schema is additive. Before promotion, recovery is dropping the disposable qualification database. After development import, recovery is snapshot retirement plus normal PostgreSQL backup/restore policy; do not rewrite source authority or historical migrations.
