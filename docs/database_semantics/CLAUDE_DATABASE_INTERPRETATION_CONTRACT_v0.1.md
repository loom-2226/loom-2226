# Claude / Agent Database Interpretation Contract v0.2

Applies whenever an agent reads `data/LOOM_2226.sqlite3` or `data/LOOM_2226_CIVSTATE.sqlite3`.

## Primary rule

Before using a database field materially, consult the generated production data dictionary and its field recovery status.

The question is:

> What exactly is this field, at what row grain, in what units/domain, how is it generated, and how does it join?

## Recovery statuses

- `RECOVERED_EXACT`: explicit preserved semantic/formula contract.
- `RECOVERED_STRUCTURAL`: concrete key/lookup/metadata meaning proven by schema or verified value-domain joins.
- `RECOVERED_PARTIAL`: useful meaning recovered but exact formula/unit/taxonomy remains incomplete.
- `RECOVERED_STORAGE_ONLY`: storage role is inventoried, but intended semantic/generating meaning remains open.

`RECOVERED_STORAGE_ONLY` is **not understood**. Do not infer the missing meaning from the identifier.

## Evidence order

For CIVSTATE, consult and cross-route all five in-database documentation layers:

1. `civ_variable_semantics`
2. `civ_readiness_audit`
3. `civ_derivation`
4. `civ_methodology_note`
5. `civ_assumption`

Then search the repository for the generating builder/migration, frozen specification, source documentation, and authoritative consumer contract.

Documentation belongs to the table/field it **describes**, not necessarily the documentation table where the prose is stored.

## Hard prohibitions

- Do not infer scientific, economic, social, political, physical, or gameplay meaning from a column name.
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
Annual corridor demand proxy, not scheduled direct service. Reverse-paired rows do not prove reciprocal operational dependence.

### `civ_actor_exposure`
Exposure represents influence/control/dependency constructs, not ownership. `employment_share`, `asset_share`, and `revenue_share` are intentionally unsupported in the current derivation.

### `civ_census_node_relation`
`LOCATED_IN` and `GATEWAY_FOR` relate operational facilities to census geography. They do not transfer population or imply every zone resident uses a facility.

### `civ_infrastructure_state.berths_equivalent`
Throughput equivalent, not literal physical dock/berth count.

### `civ_workforce_state.machine_task_equivalent`
Non-person automation task capacity. Never add it to synthetic-person population.

### `knowledge_entities`
Knowledge noun/entity catalog, not a proposition/claim table.

### `knowledge_relationships`
Semantic noun relationships with provenance/context; not automatically interpersonal social ties.

## Output discipline

When a field materially supports a conclusion, record:

- database / table / column;
- row/key or grain used;
- recovery status;
- evidence source;
- unit/scale where recovered;
- generating rule where recovered;
- known caveat or misuse warning.

If a required meaning is only `RECOVERED_STORAGE_ONLY`, stop or downgrade the conclusion instead of filling the gap.
