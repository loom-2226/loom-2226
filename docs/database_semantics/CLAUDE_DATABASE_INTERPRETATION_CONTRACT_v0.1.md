# Claude / Agent Database Interpretation Contract v0.1

Applies whenever an agent reads `data/LOOM_2226.sqlite3` or `data/LOOM_2226_CIVSTATE.sqlite3`.

## Before interpreting a field

1. Read `docs/database_semantics/LOOM_DATABASE_SEMANTIC_DOSSIER_v0.1.md`.
2. Check `docs/database_semantics/LOOM_DATABASE_SEMANTIC_INDEX_v0.1.json` for coverage.
3. For CIVSTATE, inspect `civ_variable_semantics`, `civ_derivation`, `civ_methodology_note`, `civ_assumption`, and `civ_readiness_audit` before interpreting an unfamiliar field.
4. Search GitHub for the generating builder/migration and authoritative consumers.
5. If meaning remains untraced, say `NOT UNDERSTOOD`; do not infer semantics from the identifier.

## Hard prohibitions

- A value constant within Ceres/region/class is not a local differentiator.
- A generated symmetric edge/flow is not evidence of reciprocal real-world dependence.
- A proxy is not a literal physical count unless its contract says so.
- Organization-scope facts are not individual-scope facts.
- Co-presence or shared facility standing is not a person-person relationship.
- Cross-boundary fact is not boundary-dependent fact.
- A populated summary statistic does not imply its underlying distribution exists.
- Never infer absence from schema that was not actually inventoried/queried.
- Re-query identifiers; do not trust copied IDs.

## Specific known warnings

### `civ_transport_flow`
Treat as annual corridor demand, not scheduled direct service. Do not use reverse-paired rows as evidence of Thompson-style reciprocal/sequential dependency unless a separate source establishes prerequisite semantics.

### `civ_actor_exposure`
Interpret exposure weights as influence/control/dependency constructs, not ownership. Organization-level exposure does not locate a projected individual.

### `knowledge_entities`
Despite the name, this is a knowledge-noun/entity catalog, not a table of propositions or claims. `noun_id` is the knowledge noun key; `spatial_entity_id` is the bridge to the spatial/world entity key.

### `knowledge_relationships`
These are semantic noun relationships with provenance/context. They do not automatically represent interpersonal social ties.

### `berths_equivalent`
Do not read as a literal physical berth count unless the semantic contract recovered from builder/methodology explicitly supports that interpretation. Prior work used it too literally.

### `authority_complexity`
Do not use as a Ceres-local selector merely because it equals 1.00 at a facility. Prior audit found it shared across all five Ceres facilities and many system-wide nodes; grouping-level variation must be checked before use.

## Epistemic output format

When using a field materially, record:

- database/table/column;
- row/key used;
- semantic evidence source;
- epistemic class;
- grouping-level variation check where relevant;
- known misuse warning;
- unresolved caveat.

If any of those are unknown and matter to the conclusion, downgrade the conclusion rather than filling the gap.
