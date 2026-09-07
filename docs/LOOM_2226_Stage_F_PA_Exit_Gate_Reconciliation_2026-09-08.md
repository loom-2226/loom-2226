# LOOM 2226 — Stage F-PA Exit-Gate Reconciliation

Date: 2026-09-08  
Status: **Exit-gate reconciliation — feature branch / NON-CANON until governed merge**

## 0. Authority

This reconciliation is based only on live GitHub artifacts on `feature/f-pa-physical-authority-audit-2026-09-08`. Chat/model memory is not documentary authority.

It consolidates F-PA-1 through F-PA-6 and determines whether Stage F-PA is actually ready to hand off into F-PB schema/contracts work. It does not promote coordinates, orbits, traffic rules, campaign schema, vehicle physics, or canon values.

## 1. Exit-gate verdict

**F-PA is not yet fully closed.**

The six core audit lanes have established the current authority boundaries and simulator gaps, but one required closure item remains materially incomplete: the per-infrastructure derivation/provenance/canon-conflict pass required by the governing SQL-first rules.

Therefore:

- audit discovery is substantially complete;
- schema/service design may be prepared as a proposal;
- **F-PB implementation/promotion is not yet authorized by this reconciliation**;
- no infrastructure reference state may be silently upgraded to navigation grade.

## 2. Gate-by-gate reconciliation

| Exit gate | Status | Git-backed basis |
|---|---|---|
| 1. Exact WORLD/CIVSTATE inventory | **PASS** | Exact Git-backed SQLite inventory: WORLD 42 tables; CIVSTATE 53 tables; stable audited hashes recorded in parent F-PA audit. |
| 2. Infrastructure-by-infrastructure physical-authority/derivability matrix | **PARTIAL / BLOCKING** | 127/127 rows classified as non-navigation-grade engineering references; frame, geometry, orbit-family and state-quality coverage established. Required per-node derivation-source / text-canon constraint / conflict / promotion classification is not yet complete. |
| 3. Campaign mutable-state gap matrix | **PASS** | F-PA-4 establishes what JSON/history persists and which true-state, attitude, guidance, thermal/power, docking, sensor, fault and clearance domains are missing. |
| 4. Navigator/trajectory telemetry coverage matrix | **PASS** | F-PA-5 maps the current 25-field Sequence-B sample boundary, exact ordinary XYZ/VXYZ coverage, relational metric semantics, interpolation limits and missing simulator telemetry. |
| 5. Engineering/dynamics coverage matrix | **PASS** | F-PA-6 separates governing engineering canon from diagnostic D2i checks and identifies missing 6DOF/actuation/mass-properties/thermal/power/sensor/comms/fault models. |
| 6. Explicit list of models/fields requiring new governed authority | **PASS** | Consolidated in this document section 4 and parent F-PA gap list. |
| 7. Proposed schema/service changes separated from audit facts | **PASS FOR DESIGN HANDOFF** | Section 5 below is explicitly proposal-only and does not claim existing authority. |
| 8. No display/reference approximation silently promoted to physics | **PASS** | Infrastructure remains 127/127 non-navigation-grade; E2 interpolation is non-navigation-grade; E3 is visualization-only; metric transit gets no invented ordinary path. |
| 9. No new canon values invented merely for visual completeness | **PASS** | F-PA has performed classification/audit only; no new coordinates/orbits/traffic constants/vehicle constants are promoted. |
| 10. SQL-first provenance for every future promoted spatial result | **RULE ESTABLISHED / NO PROMOTIONS YET** | Governing audit requires SQL → referenced governed model → live-Git frozen canon → standard/method → candidate → qualification → structured promotion. |
| 11. SQL↔text-canon conflicts explicitly reconciled before promotion | **PARTIAL / BLOCKING FOR INFRASTRUCTURE PROMOTION** | Conflict rule is explicit, but the 127-node text-canon constraint/conflict pass has not yet been completed. |

## 3. Resolved relationship questions

### 3.1 CIVSTATE ↔ WORLD infrastructure

F-PA-3 establishes `civ_subject` as the explicit identity bridge:

- 127 distinct `navigator_node_id` values match all 127 WORLD infrastructure `node_id` values;
- 127 infrastructure `entity_id` values are also represented through `navigator_entity_id` linkage.

CIVSTATE therefore provides civil/institutional/economic/traffic-demand context without duplicating numerical spatial authority.

### 3.2 WORLD `transport_hubs`

The 12 `transport_hubs.entity_id` values (`BELT`, `CISLUNAR`, `HELIOCENTRIC`, `JU`, `KUIPER`, `MA`, `ME`, `NE`, `OORT`, `SA`, `UR`, `VE`) do not directly match WORLD infrastructure node IDs, entity IDs, systems or parent bodies under the audited identity domains.

The correct F-PA conclusion is therefore not “broken join.” It is:

**`transport_hubs` is a separate aggregate/system-level model whose relationship to individual infrastructure nodes is not currently governed by a demonstrated direct key.**

Until a governed mapping exists, no transport-hub row may be silently attached to a port/station.

## 4. Consolidated authority gaps requiring governed work

The next physical-authority program must explicitly supply or qualify, rather than infer:

1. body orientation / rotating and body-fixed frame transforms;
2. structured surface geography and datum semantics;
3. re-derived/qualified navigation-grade state for infrastructure endpoints;
4. typed authorized-orbit / traffic-control / clearance rules;
5. station rendezvous gates, hold points, approach corridors, keep-out zones and docking transition geometry;
6. surface deorbit, entry, terminal-area, landing-approach and final-state geometry;
7. canonical mutable vehicle true state with position, velocity, attitude, angular rate and mass/consumables;
8. propulsion/actuator dynamics including thrust vectors, gimbal/vectoring and RCS;
9. mass properties, inertia tensor and center-of-gravity evolution;
10. quantitative power and thermal state;
11. sensor measurement models and estimated-navigation state with uncertainty/covariance;
12. guidance/control state and commands;
13. communications/light-time/latency/availability model;
14. fault/damage/degradation state;
15. traffic-clearance mutable campaign state;
16. telemetry contract distinguishing true, measured, estimated and commanded values.

## 5. Proposal-only F-PB schema/service handoff

The following is **not current authority**. It is the minimal design surface that F-PB should formalize after the remaining F-PA blocker closes.

### 5.1 Shared physical-state contract

A canonical state service should expose at minimum:

`entity_id, epoch, position, velocity, orientation, angular_rate, reference_frame, provenance, navigation_grade, uncertainty/quality`.

### 5.2 WORLD physical-authority additions

Candidate structured authority families:

- body orientation / frame models;
- surface-site geodetic/shape placement;
- qualified infrastructure orbit/state models;
- authorized orbit classes and physical corridor geometry;
- rendezvous/docking/landing transition geometry;
- explicit provenance/qualification records.

### 5.3 CAMPAIGN mutable-state additions

Candidate mutable authority families:

- vehicle true state;
- estimated navigation state;
- mass/remass/consumables;
- power/thermal/propulsion state;
- guidance/control/actuator state;
- docking/landing/local-flight state;
- traffic clearance;
- faults/damage;
- active trajectory and transition/event lineage.

### 5.4 CIVSTATE boundary

CIVSTATE remains civil/institutional/economic/demographic/social/traffic-demand context plus identity linkage. It may inform permissions and demand but does not become numerical flight-state authority.

### 5.5 Service boundaries

Recommended typed handoffs:

`WORLD physical authority → spatial/state service → Navigator/GN&C`

`CIVSTATE policy/demand → traffic-control service → authorized physical constraints + CAMPAIGN clearance state → Navigator/GN&C`

`CAMPAIGN true state → sensors → estimated nav state → guidance → control/actuators → vehicle dynamics → new CAMPAIGN true state`

Telemetry/HUD/GIS derive from those states; they do not own them.

## 6. Remaining F-PA closure action

Before F-PA can be declared complete, perform the **127-node derivation/provenance/canon-conflict pass** required by the existing audit contract.

For every infrastructure node, capture:

- `PRIMARY_STRUCTURED_SOURCE`
- `REFERENCED_MODEL_SOURCE`
- `TEXT_CANON_CONSTRAINT`
- `SOURCE_CONFLICT_STATUS`
- `SPATIAL_DERIVABILITY`
- `DERIVATION_STANDARD_OR_METHOD`
- `QUALIFICATION_STATUS`
- `PROMOTION_TARGET`

Rules remain:

- fetch all referenced canon from live GitHub;
- SQL is first structured authority;
- canon constrains unresolved gaps but cannot silently overwrite SQL;
- any SQL↔canon conflict stops that node;
- if authority does not determine a unique physical state, mark design-required/underdetermined;
- no navigation-grade promotion occurs inside this audit stage.

When that pass is complete and no unresolved conflict is being hidden, F-PA may be closed and F-PB may begin under governed process.
