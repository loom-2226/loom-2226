# PR B — Feed requirements and Option B boundary (initial traceability)

Date: 2026-09-17. Status: DRAFT / NON-CANON / REQUIREMENTS EXTRACTION, NOT PR B GATE PASS. Governing execution plan: `WAYFARER_E1_DRIVETRAIN_SPATIAL_CLOSURE_WORKPLAN_v0.1.md` on this branch. This document records requirements and blockers; it does not select a fluid, modify geometry or qualify Option B.

## Baseline inventory and topology

- Normal torch remass: 250 t, four baseline tanks at 62.5 t inventory each (seed inventory allocation; not certified geometric capacity).
- Protected water reserve: 50 t separate from normal remass. The x=12.5 m bookkeeping centroid in the geometry compiler is **not** an identified physical reserve vessel. Neither internal auxiliary nor external drop-tank capacity may be counted as the reserve by inference.
- Governed mass reference in workplan: dry 858.5 t, wet 1,158.5 t, post-normal-remass 908.5 t. These figures account for 250 t normal remass plus 50 t protected water. An attached long-haul pack changes the mass configuration and requires separate accounting; it must not be silently inserted into baseline wet mass.
- Four-tank baseline topology remains required. The user-selected Option B has four *longer internal candidate cylinders* and two *optional detachable external tanks*. This is a spatial candidate, not authorization to change the four-tank baseline topology or canon.

## Feed and operational requirements to encode against executable authority

| ID | Requirement | Status / evidence needed |
|---|---|---|
| B-01 | Reproduce six authoritative torch mode outputs ECON–LIMIT without modifying frozen torch. | OPEN: extract exact executable T1–T5 cards, source SHA and unit tests. |
| B-02 | Reproduce authoritative flow range, workplan approximate 1.1361004025–284.025100625 kg/s and 250:1 turndown. | OPEN: executable verification; approximate workplan values are not an independent specification. |
| B-03 | Keep 250 t normal inventory and 50 t protected reserve separately identifiable and non-double-counted. | REQUIREMENT; test not yet implemented. |
| B-04 | Torch and high-metric operating states mutually exclusive. | REQUIREMENT; reproduce executable authority and test. |
| B-05 | Provide typed tank → collector → isolation → header → conditioning allocation → torch inlet connection graph. | OPEN: PR D implementation; unknown equipment remains labeled envelope. |
| B-06 | Define shutdown, fault isolation, feed transitions, and reserve-protection behavior without inventing pressure, transient or pump performance. | OPEN: dynamic physical parameters unresolved. |
| B-07 | Distinguish storage envelope, actual usable capacity, species, phase, ullage, insulation, tank wall and mounts. | OPEN: PR C; gross mesh volume is not usable remass. |

## Option B external-pack interface — separate mission configuration

Two longitudinal external tanks are candidate mission equipment. Their previous derivative GLB screen reports 165.8 m³ *gross external envelope*; this is not usable capacity or an approved remass inventory. No source-backed density, fill fraction, dry tank mass, mount mass, plumbing mass, attachment strength, separation mechanism, feed performance or plume model is selected. Treat all of these as TECHNOLOGY_HOLD / UNRESOLVED_ALLOCATION.

Proposed **interface requirement**, not validated implementation: external tank(s) → independently isolatable external manifold → baseline normal-remass header; protect the 50 t reserve behind a separately verified isolation boundary. The clean courier must remain operable after pack removal. Each external tank needs a distinct identity, inventory ledger and attach/detach state. Full/partial/depleted/released configurations need separate CoM and inertia and RCS authority calculations. No promise of safe jettison or debris disposal.

The earlier bounding-box warning concerning the shuttle is assigned to PR E's collision/access register. It is neither an established mesh collision nor a blocker to extracting PR B feed requirements or developing PR D connectivity. PR E must still verify courier deployment, RCS hardpoints/plumes, metric equipment, radiators and mounts. Do not move frozen RCS or torch interfaces to solve an unverified AABB warning.

## Execution gate / next evidence

PR B is **OPEN**, not passed. Required: identify live executable torch mode sources and SHAs; add typed requirement adapter and tests for six mode cards, flow extrema, inventory/reserve segregation and torch/metric exclusion. Then PR C and PR D can proceed in parallel on stable interfaces. Option B external pack stays an explicitly separate, optional mission configuration until its own requirements and mass accounting are approved.
