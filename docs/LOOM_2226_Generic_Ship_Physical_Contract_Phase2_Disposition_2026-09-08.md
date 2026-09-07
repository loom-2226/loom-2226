# LOOM 2226 — Generic Ship Physical Contract — Phase 2 Disposition

**Date:** 2026-09-08  
**Status:** ENGINEERING / QUALIFICATION — FEATURE BRANCH — NOT CANON  
**Branch:** `qualification/portable-ship-phase2-contract-2026-09-08`  
**Accepted contract:** `docs/LOOM_2226_Generic_Ship_Physical_Contract_v0.2.md`  
**Hostile review:** `docs/LOOM_2226_Generic_Ship_Physical_Contract_Hostile_Review_2026-09-08.md`  
**Parent authority:** `docs/LOOM_2226_Portable_Ship_Simulation_Qualification_Work_Plan_2026-09-08.md`

---

## 1. Disposition

**PHASE 2: PASSED — GENERIC SHIP PHYSICAL CONTRACT ACCEPTED FOR PHASE-3 PROTOTYPING.**

This disposition accepts v0.2 as the semantic contract to be implemented by the next non-destructive Wayfarer-only ship-class SQLite prototype.

It does not promote the contract to canon, does not authorize production deployment, and does not unfreeze Navigator/GIS/HUD physics-dependent implementation.

---

## 2. Hostile-review repair verification

The original v0.1 hostile review returned **NO-GO AS WRITTEN / REPAIRABLE** and identified H1-H14. v0.2 resolves them as follows:

| Finding | Required repair | v0.2 disposition |
|---|---|---|
| H1 | explicit wrench/moment arm about current CoM | CLOSED |
| H2 | deterministic mass-property/integration ordering | CLOSED |
| H3 | explicit variable-mass/exhaust momentum boundary | CLOSED |
| H4 | compositional acyclic transform hierarchy | CLOSED |
| H5 | unambiguous inertia reference point/frame semantics | CLOSED |
| H6 | executable store centroid/inertia models | CLOSED |
| H7 | minimum actuator command/response semantics | CLOSED |
| H8 | fail-closed feed/resource/protected-reserve behavior | CLOSED |
| H9 | explicit atomic/kinematic/external transition semantics | CLOSED |
| H10 | recursive rigid attachment mass/inertia aggregation | CLOSED |
| H11 | minimum primitive/physical-role semantics | CLOSED |
| H12 | deterministic discontinuity/event semantics | CLOSED |
| H13 | stronger typed true-state frame labeling | CLOSED |
| H14 | SI/internal numerical validity and normalization policy | CLOSED |

No hostile-review item requires a simulator-specific field.

---

## 3. Phase-5 test-coverage re-attack

The hardened contract was re-attacked against every known-answer case named by the governing Phase-5 work plan:

```text
zero-force inertial coast
single axial thruster
offset thruster producing coupled translation/rotation
symmetric thruster pair producing near-pure rotation
commanded pitch
commanded yaw
commanded roll
combined 6DOF maneuver
propellant/remass depletion
center-of-mass migration
inertia migration
detachable launch/configuration transition
```

Each case now maps to explicit v0.2 semantics. No known-answer case requires a hidden simulator assumption, renderer-only geometry, authored current CoM, abstract maneuverability score, or duplicated resource mass.

This is a semantic gate only. It does **not** claim those Phase-5 numerical tests have already been implemented or passed; that remains later work under the governing plan.

---

## 4. Wayfarer compatibility re-attack

Live Wayfarer authority can be represented without destructive loss or silent promotion:

- immutable body datum remains distinct from moving CoM;
- 33 t docked planetary launch may alter mass/CoM/inertia through one governed transform;
- `DOCKED/EXTRACTING/ABSENT` can be represented without pretending an intermediate extraction model is already canon;
- 300 t working-fluid/water inventory can contain the 250 t normal remass and 50 t protected reserve without double-counting;
- four tanks can receive explicit fill/centroid/inertia models later without requiring slosh physics now;
- current lower-authority component centroids can remain design-baseline while canon masses retain their own authority;
- exact RCS geometry remains OPEN rather than fabricated;
- radiator transition/sweep semantics exist without selecting a final radiator topology;
- torch ordinary-wrench behavior remains distinct from metric regime propagation;
- metric and torch mutual-exclusion constraints can be represented;
- `loompy` remains fail-closed.

---

## 5. Architecture preserved

Phase 2 still preserves the Phase-1 decisions:

- portable ordinary dynamics remain a narrow LOOM-owned deterministic kernel;
- Basilisk remains spacecraft hostile reference;
- JEOD + Trick remain NASA deep reference;
- Tudat/TudatPy remain astrodynamics reference;
- external environment models remain outside ship-class authority;
- external simulator APIs do not define LOOM schema;
- class physical authority, instance state and derived `VehicleTrueState` remain separate;
- no UX surface owns physical truth.

---

## 6. Authorized next step

Phase 3 may now begin under the governing work plan:

> Create a **non-destructive prototype generic ship-class SQLite database containing only Wayfarer**, implementing the v0.2 semantics sufficiently to resolve active components, configuration, geometry, mass elements, stores, total mass, CoM, inertia, effectors, attachments, torch capability and metric eligibility without mutating existing Wayfarer authority.

The prototype must ingest/follow live GitHub Wayfarer authority and preserve source/status provenance. It must not migrate or delete the current geometry seed/compiler pipeline until compatibility is proven.

Phase 3 should begin with schema + resolver tests, not with a production database swap.

---

## 7. Gate statement

**Phase 2 is CLOSED/PASSED on this feature branch.**

**Phase 3 Wayfarer-only SQLite prototyping is authorized.**

**Navigator/GIS/HUD physics-dependent implementation remains HARD FROZEN.**

**No merge is authorized.**
