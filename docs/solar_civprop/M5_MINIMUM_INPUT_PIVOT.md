# M5 — Solar CIVPROP Minimum Input Pivot

## Decision
M4-B completed the broad Solar resource-evidence pass. Treat Solar Facts as the evidence/provenance warehouse, not the direct CIVPROP operating database. Broad empirical enrichment pauses here unless a downstream input contract identifies a specific blocker.

## Next milestone
Build a small, purpose-built LOOM_SOLAR_CIVPROP_INPUT.sqlite3 from current qualified authority using deterministic ETL.

The input contract should contain only what downstream simulation needs:
- identity/body class/parent;
- minimum physical state needed by the consumer (mass or defensible derivation inputs, size/shape, density, rotation where required);
- Navigator identity/state support and readiness, while delta-v and TOF remain Navigator outputs;
- resource state for VOLATILES, METALS, SILICATES_ROCK, and CARBONACEOUS_ORGANICS, preserving measured/bounded/inferred/unknown status, scope, uncertainty, and lineage;
- simulation-readiness flags indicating when an empirical value exists, can be derived, or requires an archetype prior / hidden-truth generation.

Do not copy the full evidence corpus into the operating database. Compiled values must retain lineage back to Solar Facts.

## Hidden truth boundary
Keep generated simulation truth separate from empirical knowledge.

- LOOM_SOLAR_CIVPROP_INPUT.sqlite3: compiled 2026 empirical/knowledge input.
- LOOM_SOLAR_TRUTH_<seed>.sqlite3: seeded, reproducible hidden physical realization used by the simulation.

Agents may reason from their knowledge/belief state; they must not directly query hidden truth. Empirical constraints narrow generated priors. Monte Carlo fills residual uncertainty rather than overwriting observations.

## Resource/economic boundary
Dorrington/Olsen remains the economic architecture kernel. Solar input supplies physical/resource state; Navigator supplies transfer opportunity/delta-v/TOF; technology supplies mining/recovery capability; economics supplies costs/prices/capital. CIVPROP consumes those layers.

Taxonomy may select or constrain a scientifically sourced composition archetype, but taxonomy is not abundance.

## Work order
1. Freeze M4-B as the broad evidence baseline.
2. Define SOLAR_CIVPROP_INPUT_CONTRACT_V1 from actual Navigator + Dorrington/Olsen + agent/prospecting output needs.
3. Create minimal DDL.
4. Deterministically ETL current qualified Solar authority into the new SQLite.
5. Produce a per-body readiness/gap matrix.
6. Only then research specific gaps that materially block the downstream model.
7. Separately develop scientifically sourced body/composition archetype priors for unresolved properties.

Guiding rule: **output drives input**. Unknowns are simulation uncertainty, not automatically a mandate for more research.
