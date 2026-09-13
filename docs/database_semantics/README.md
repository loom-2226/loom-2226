# LOOM Database Data Dictionary

This directory is the production data-contract documentation for the LOOM world databases.

**Primary task:** answer, for every field, **what is this field, at what row grain, in what units/domain, how is it generated, and how does it join?**

The generator is `tools/build_database_data_dictionary.py`.

## Recovery statuses

The data dictionary deliberately separates four levels of recovery:

- `RECOVERED_EXACT` — explicit preserved semantic/formula contract.
- `RECOVERED_STRUCTURAL` — concrete key/lookup/metadata meaning proven by schema or verified value-domain joins.
- `RECOVERED_PARTIAL` — useful meaning recovered, but exact formula/unit/taxonomy remains incomplete.
- `RECOVERED_STORAGE_ONLY` — the field is inventoried and its storage role is known, but semantic/generating meaning is still open. **This is not treated as understood.**

Every current production field must be represented. No field may disappear merely because its meaning has not yet been recovered.

## Evidence routing

For CIVSTATE, the generator ingests and cross-routes all five self-documentation layers:

1. `civ_variable_semantics`
2. `civ_readiness_audit`
3. `civ_derivation`
4. `civ_methodology_note`
5. `civ_assumption`

Evidence is attached to the table/field it **describes**, not merely the table in which the prose happens to live.

A readiness-audit record about `civ_transport_flow` therefore belongs to the transport entry. A derivation explaining `civ_actor_exposure` belongs to actor exposure. Table status is derived from recovered field and purpose evidence rather than assigned by table name.

## Hard rule

Do not infer scientific, social, political, economic or gameplay meaning from an identifier alone. Schema/value behavior may prove storage structure, joins and observed domains. It does not prove intended semantics.

This documentation is subordinate to canon/engineering/data authority and does not promote database contents to canon.
