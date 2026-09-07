# LOOM 2226 — Stage F-PA-3 CIVSTATE Boundary Audit

Date: 2026-09-08  
Status: **Audit evidence — feature branch / NON-CANON until governed merge**

## Authority and scope

This audit is generated from the exact GitHub PR checkout by `src/loom/civstate_boundary_audit.py` and `tests/test_civstate_boundary_audit.py` against the governed WORLD and CIVSTATE SQLite files. GitHub documentary authority applies; chat/model memory is not a source of record.

This stage classifies the boundary between civil/institutional state and numerical physical-navigation authority. It does not move tables, alter SQL, invent coordinates, or promote any CIVSTATE field into trajectory physics.

## Exact CI evidence

GitHub Actions run `34158254647` at PR-head commit `4c07fa3e954406166d3780cc07aae2305b89e54b` completed **327 tests, PASS**.

CIVSTATE contains **53 tables**. Conservative structural classification produced:

- `CIVIL_INSTITUTIONAL_CONTEXT`: 25 tables
- `CACHE_OR_DERIVED_NONAUTHORITY`: 4 tables
- `SHARED_IDENTITY_OR_LINKAGE`: 2 tables
- `UNCLASSIFIED_REVIEW_REQUIRED`: 22 tables
- `PHYSICAL_NAVIGATION_CANDIDATE_REQUIRES_REVIEW`: 0 tables

The classifier is deliberately conservative and token/schema based. `UNCLASSIFIED_REVIEW_REQUIRED` does not mean physically authoritative; it means the table cannot be safely assigned from column vocabulary alone.

## Core boundary finding

The exact CIVSTATE schema contains no demonstrated numerical trajectory-state layer comparable to WORLD `spatial_states`, `ephemeris_states`, or `orbit_geometry_models`.

No CIVSTATE table exposed the audited physical-navigation field families for:

- 6D XYZ/VXYZ state;
- reference-frame navigation state;
- classical orbital elements;
- navigation-grade state;
- GM/gravity authority;
- structured latitude/longitude/elevation;
- body-fixed orientation authority.

Therefore **CIVSTATE is not current numerical flight-state authority**. Its role is civil, institutional, demographic, economic, governance, traffic-demand/context, derivation/provenance, identity linkage, and cached relationship/navigation-graph support.

This does not prohibit physical simulation from consulting CIVSTATE for permissions, ownership, traffic pressure, demand, regulatory context, or institutional state. It prohibits treating those values as position/velocity/orbit truth without a separate governed physical model.

## Infrastructure linkage is explicit through `civ_subject`

`civ_subject` is the cross-database identity bridge.

Exact audit result:

- distinct `navigator_node_id`: **127**
- `navigator_node_id` values matching WORLD infrastructure `node_id`: **127 / 127**
- distinct `navigator_entity_id`: **182**
- `navigator_entity_id` values matching WORLD infrastructure `entity_id`: **127**

Thus all 127 WORLD infrastructure nodes have a CIVSTATE subject-level linkage without requiring CIVSTATE to duplicate their numerical spatial state.

This is the desired separation:

```text
WORLD physical/spatial entity + node identity
        ↕ explicit navigator identity bridge
CIVSTATE subject / governance / economy / population / traffic context
```

The bridge is identity/context linkage, not authority promotion.

## Infrastructure civil-state coverage

`civ_infrastructure_state` contains **127 rows** keyed by `node_subject_id` and carries civil/economic/operational-scale values including resident/transient population, workforce, capital/replacement value, value added, operating cost, power averages/peaks, habitable capacity, industrial capacity, cargo throughput, passenger movements, ship calls, berth equivalents, utilization and strategic/transport centrality.

These are **civil/operational context values**. In particular:

- `ship_calls_year`, cargo throughput and passenger movement may inform traffic-demand models;
- power/capacity values may constrain infrastructure operations;
- none of these fields define a craft's position, velocity, orbit, approach corridor, clearance state or docking geometry.

`civ_transport_flow` similarly carries OD-style passengers/freight/ship movements/transit-hour/accessibility/route-importance context. It is traffic/economic flow context, not trajectory integration authority.

## Governance and traffic-control boundary

CIVSTATE contains governance, security, jurisdiction, influence and institutional data sufficient to answer **who may control or regulate an operation**. WORLD contains physical infrastructure and traffic-related structures that can answer **where a physical facility/model exists**.

Future traffic/clearance simulation should therefore preserve a typed handoff:

```text
CIVSTATE: authority / law / policy / access / demand / institutional state
        ↓
TRAFFIC-CONTROL / CLEARANCE SERVICE
        ↓
WORLD + CAMPAIGN: authorized physical corridor/orbit + mutable clearance state
        ↓
NAVIGATOR / GUIDANCE: numerical trajectory subject to that authority
```

CIVSTATE must not directly become an orbit-geometry or trajectory-integration database.

## `transport_hubs` linkage correction

WORLD `transport_hubs` has **12 rows**, whose `entity_id` values are:

`BELT`, `CISLUNAR`, `HELIOCENTRIC`, `JU`, `KUIPER`, `MA`, `ME`, `NE`, `OORT`, `SA`, `UR`, `VE`.

Exact comparison found **zero direct matches** between these values and:

- WORLD infrastructure `entity_id`;
- WORLD infrastructure `node_id`;
- WORLD infrastructure `system` values;
- WORLD infrastructure `parent_body` values.

No other ID-like `transport_hubs` column directly matched infrastructure identity domains in this audit.

Therefore the earlier infrastructure LEFT JOIN on `transport_hubs.entity_id = infrastructure_nodes.entity_id` correctly produced zero rows because the two tables do **not** use the same identity domain. The 12 transport-hub records must be treated as a separate aggregate/system-level model until their governed relationship is explicitly demonstrated. They must not be silently attached to individual ports or stations.

## Cache and graph boundary

The four `nav_graph_*_cache` / refresh tables are explicitly classified `CACHE_OR_DERIVED_NONAUTHORITY`. They can accelerate browsing/link analysis but must never outrank their source tables or become physical/campaign truth.

`graph_link_enrichment` remains a presentation/relationship enrichment surface and is not physical navigation authority.

## F-PA-3 boundary decision

For the simulator architecture, the governed boundary is:

- **WORLD** — celestial, infrastructure, spatial/reference physical models and future promoted physical navigation authority;
- **CIVSTATE** — civil/institutional/economic/demographic/social/traffic-demand context plus explicit subject-to-Navigator identity linkage;
- **CAMPAIGN** — mutable realized game/simulator state, including future traffic clearances and vehicle state after governed promotion;
- **NAVIGATOR / PHYSICS SERVICES** — consume qualified WORLD physical state plus allowed CIVSTATE-derived policy/traffic constraints, but do not infer numerical position/orbit from CIVSTATE context fields.

## Remaining caveat

Twenty-two CIVSTATE tables remain `UNCLASSIFIED_REVIEW_REQUIRED` under the intentionally narrow structural classifier. Their schemas are predominantly derivation, model-run, assumptions, social/relationship, reconciliation, semantic or flow/support structures. None currently demonstrates a numerical navigation-state contract, but future use of any such table for simulation authority requires a field-level semantic review rather than relying on this coarse classifier alone.

## No-promotion rule

No CIVSTATE value is promoted by this audit. Any future rule turning governance/traffic context into an authorized orbit, corridor, hold point, clearance, or numerical guidance constraint requires a governed service/schema contract with explicit provenance and physical qualification.