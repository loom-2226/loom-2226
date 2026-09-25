# HCQ-01 CERES — v0.3-R1 Hostile-Review Qualification

## Result

**QUALIFIED_WITH_LIMITATIONS** — local repair candidate; no Git or remote operation performed.

The preserved v0.2 SHA is `91137126f635cd35e7ccde20cc41ed342dbd23dec7e7af304d9220318f1da26d` and the preserved v0.3 SHA is `310c35491e3768adcfc1607c4542603613d8d28ad00df883755537805037ed74`.
Neither artifact was modified. The repaired artifact is `LOOM_SOLAR_HCQ01_CERES_v0_3_R1.sqlite3` with SHA `0bbbfd5ae2ab287900ff4e356f9571d21aff4593cc78e0cd69bf1610def9adc6`.

## Findings

### R1-A — update-safe semantic integrity

Reproduced before repair: **YES**. v0.3 allowed endpoint body mutation to
break fact/observation, fact-input, and model/region same-body relationships.
Root cause: v0.3 guarded relationship edges but not all participating node
updates. Repair: narrowly scoped SQLite BEFORE UPDATE/INSERT triggers covering
the enumerated relationship graph in `relationship_matrix.json`, including
fact, observation, model, region, material, activity, derived and preferred
endpoints. Valid isolated body changes remain allowed. Post-repair result: **CLOSED**.

### R1-B — arbitrary knowledge-event time

Reproduced before repair: **YES**; `banana` was accepted. Root cause: non-empty
text was the only v0.3 constraint. Repair: database canonical syntax accepts
only date precision `YYYY-MM-DD` or UTC-second precision
`YYYY-MM-DDTHH:MM:SSZ`; `temporal.py` validates actual calendar dates.
Existing date-only events remain date-only. Post-repair result: **CLOSED**.

SQLite deliberately does not claim full calendar parsing in its CHECK; the
application validator rejects impossible dates such as `2025-02-30`.

## Preservation

Legacy rows, scientific values, provenance, source classifications, fact-input
lineage, four knowledge events, candidate statuses, and NULL observation-scale
values are unchanged. `preferred_fact` remains empty. `PREPRINT` remains
unchanged. No Ceres science was added and no value was guessed.

| Table | Rows |
|---|---:|
| `activity_fact` | 2 |
| `body` | 1 |
| `body_model_product` | 9 |
| `body_region` | 5 |
| `derived_input` | 1 |
| `derived_quantity` | 1 |
| `fact` | 8 |
| `fact_input` | 2 |
| `fact_observation` | 2 |
| `gravity_model` | 1 |
| `knowledge_event` | 4 |
| `material_evidence` | 6 |
| `meta` | 12 |
| `observation` | 8 |
| `orientation_model` | 1 |
| `preferred_fact` | 0 |
| `property_definition` | 53 |
| `region_model_product` | 3 |
| `source` | 16 |
| `source_assertion` | 8 |

## Tests and integrity

- R1 tests: **10/10 PASS**
- Existing v0.3 tests: **9/9 PASS**
- Existing HCQ-01 tests: **14/14 PASS**
- Total: **33/33 PASS**
- Independent deterministic rebuild: semantic identity **True**; byte identity **True**
- `PRAGMA integrity_check`: **ok**
- `PRAGMA foreign_key_check`: **[]**
- Scientific semantic diff v0.3 → R1: **UNCHANGED_LEGACY_CONTENT**, unexpected tables **[]**

## Temporal and epistemic boundaries

No observation-scale values were populated. All scientific facts remain
`CANDIDATE`; no preferred fact, resource, engineering, economic, habitation,
transport, fictional, CIVPROP or Phase-5 state was introduced. The v0.2 and
v0.3 qualification artifacts remain separate and byte-identical.

## Remaining findings

The inherited v0.2/v0.3 design limitations remain recorded: external raw
artifact audit linkage, historical knowledge-event/adoption semantics,
derived-fact lineage asymmetry, orientation uncertainty structure, and
source/temporal vocabulary scope as previously documented. R1 closes the two
demonstrated integrity defects without redesigning those areas.
