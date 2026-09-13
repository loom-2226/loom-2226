# Claude / Agent Database Interpretation Contract v0.2

Applies whenever an agent reads `data/LOOM_2226.sqlite3` or `data/LOOM_2226_CIVSTATE.sqlite3`.

## Primary rule: use the data dictionary

Before using a database field materially:

1. Read `docs/database_semantics/LOOM_DATABASE_DATA_DICTIONARY_v0.1.md` if present and current.
2. Use `docs/database_semantics/LOOM_DATABASE_DATA_DICTIONARY_v0.1.json` for machine lookup.
3. If generated outputs are missing or stale, run `python tools/build_database_data_dictionary.py` from the repository root.
4. If a field is marked `DEFINITION_NOT_RECOVERED`, do not make up a definition from its name. Recover it from builder/methodology/source evidence or carry the unresolved status.
5. Secondary semantic/misuse notes may add guardrails, but they do not replace the concrete definition, unit, grain, generation rule, and join contract in the data dictionary.

## What Claude should retrieve for a field

- database;
- table;
- row grain / primary key;
- column;
- SQLite declared type;
- nullability/default/key position;
- foreign-key target or join key where applicable;
- concrete data definition;
- unit or scale/domain;
- data role (identifier, count, rate, score, weight, proxy, text, timestamp, etc.);
- generating rule/source where applicable.

## Hard prohibitions

- Do not infer a missing data definition from a table or column identifier.
- A proxy is not a literal physical count unless its definition says so.
- Organization-scope facts are not individual-scope facts.
- Co-presence or shared facility standing is not a person-person relationship.
- Cross-boundary fact is not boundary-dependent fact.
- A populated summary statistic does not imply its underlying distribution exists.
- Never infer absence from schema that was not actually inventoried/queried.
- Re-query identifiers; do not trust copied IDs.

## Known concrete definitions that matter often

### `civ_transport_flow.passengers_year`
Annual modeled origin-destination corridor-demand proxy in `passengers/year`; not a timetable, scheduled-service count, unique-traveler count, or guaranteed direct route.

### `civ_transport_flow.accessibility_index`
Relative topology/ephemeris accessibility used by the OD allocator, dimensionless `0..1`; not door-to-door travel time.

### `civ_actor_exposure.control_weight`
Derived from OPERATIONS exposure in the preserved actor-exposure derivation. It is a weight, not an ownership share.

### `civ_actor_exposure.service_dependency_weight`
Derived from SUPPLY exposure in the preserved actor-exposure derivation. It is a dependency/exposure weight, not ownership.

### `civ_demographic_state.biological_population`
Recognized biological resident population at the row geography/year, unit `persons`.

### `civ_demographic_state.synthetic_population`
Recognized synthetic persons at the row geography/year, unit `persons`; distinct from non-person automation/task capacity.

### `civ_demographic_state.transient_population`
Nonresident transient presence associated with the geography, unit `persons/day-equivalent`; not part of resident census population.

### `civ_workforce_state.synthetic_workers`
Recognized synthetic persons participating in labor, unit `person-FTE proxy`.

### `civ_workforce_state.machine_task_equivalent`
Non-person automated task capacity, unit `FTE-equivalent`; never add to person counts.

### `civ_infrastructure_state.berths_equivalent`
Annual ship-call throughput normalized by utilization, unit `equivalent one-call/day berths`; not literal dock count.

### `civ_infrastructure_state.habitable_capacity`
Occupied-equivalent accommodation-capacity proxy, unit `persons-equivalent`; not certified engineering life-support capacity.

### `civ_infrastructure_state.industrial_capacity_index`
Relative industrial scale across the current 127-node universe, unit `0..1 percentile-composite`; not an absolute physical production ceiling.

## Output behavior

When Claude uses a field that materially affects a conclusion, prefer citing its dictionary definition rather than paraphrasing from memory. If the dictionary says `DEFINITION_NOT_RECOVERED`, say so and do not silently substitute a plausible meaning.
