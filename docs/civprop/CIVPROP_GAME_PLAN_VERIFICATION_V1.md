# CIVPROP game-plan verification V1

Review date: 2026-09-28. Class: `class:engineering`, architecture review only.
Verified GitHub `origin/main`: `b22703ab7ce5586fecfeda0998d19b7d1fbbfe30`.
Repository evidence was inspected; live databases were not queried or modified.

Current-status note (2026-09-30): this game-plan review remains historical architecture
evidence. Engine V1 has since been selected, an executable baseline locked, and
GAP-001 closed with the real-authority input compiler. Current status and the
post-gap handoff are governed by
docs/civprop/CIVPROP_GAP_REGISTER_AND_POST_GAP_PLAN_V1.md and
engineering/civprop/gap_register_v1.json.

## Verdict

**GAME PLAN CONFIRMED WITH MINOR CORRECTIONS.**

`loom_earth → loom_civprop ← loom_solar` remains the appropriate major boundary.
Promoted plans explicitly anticipate future CIVPROP consuming Earth, spatial,
resource and technology inputs. They do not yet define or implement a schema named
`loom_civprop`. PostgreSQL is the recommended persistence boundary consistent with
Earth/Solar, not an already-earned implementation. No architecture replacement is needed.

## Current authority map

| Component | Verified role |
|---|---|
| `loom_earth` | Validated PostgreSQL temporal projection of promoted Earth sources/models, including demographics, economies, capital and sectors. Covers 2026–2226 with explicit empirical/model boundaries; it is more than a starting-year database. Storage does not create independent model/canon authority. |
| `loom_solar` | PostgreSQL identity, identifiers, source/coverage and qualification metadata plus governed ephemeris assets/resolvers. Physical bodies and barycenters remain distinct. |
| Solar Inspector / Basemap | Current implementation branches consuming Solar authority; Inspector PR #299 and Basemap #317/#318/#320 are OPEN, not promoted main. Basemap is derived publication/cartography, not a dynamics or propagation engine. |
| Solar Facts | Physical/material evidence and provenance in the existing qualified SQLite evidence workflow. Do not claim all these facts already live in PostgreSQL. M4-B adds a disposable qualified candidate, not production fact promotion. |
| Historical Navigator | Retained executable route/flight and CIVSTATE consumer, plus useful solver, cache and presentation mechanisms. Main still has an explicit route catalog and Horizons workflow. It is neither wholly retired nor the new Solar authority; old display ellipses/rings are not authoritative trajectories. |
| Legacy CIVSTATE | Still a hash-locked, read-only runtime dependency for retained Navigator and a recovered semantics/reference corpus. Its Ceres PostgreSQL projection was retired by migration 011; this did not retire every SQLite consumer. Suitable for bounded calibration/reference and future compatibility output, not automatically CIVPROP's engine or target totals. |
| Dorrington/resource economics | Adopted mission/resource-economic component boundary. M2 supplies assessment and input audit, not a validated executable reference kernel. Transport, technology, prices/costs and decisions remain external to empirical body facts. |
| Planned `loom_civprop` | Missing scenario/run authority for decisions, events, knowledge, resource use, infrastructure, migration and resulting world state. Recommend PostgreSQL persistence; no current migration establishes it. |

`loom_timeline` is an existing supporting input: its source-derived canon and
provisional scenario classes must survive consumption. A date alone does not
create technology, installed capacity or actor access.

## Verified target architecture

```text
loom_earth temporal baseline + loom_timeline + technology/economics
                              |
loom_solar identity/state --> transport/accessibility --> resource economics
                              |                              |
Solar Facts evidence --> constrained priors + seeded uncertainty
                              |
                  frozen scenario physical realization
                              |
                   mission/observation mechanism
                              |
                      actor/public knowledge ------------> actor decisions
                                                               |
                            loom_civprop events + stock/flow updates
                                                               |
                         infrastructure/economy/population/world state
                                                               |
                              optional CIVSTATE-compatible projections
```

Use a hybrid: scheduled events for missions, construction and observations;
actor decisions at relevant opportunities; stock/flow/cohort accounting where
appropriate. Actors may be countries, firms, consortia or settlements. A single
existing country identity is sufficient for the first proof; a comprehensive
agent population is not a prerequisite.

## Required corrections and boundaries

1. **Readiness is bounded.** #308–314 support the handoff without changing the
   major architecture. #310 supersedes the initial 92-body result with 103/110
   NAV-1 assessments at 2226-08-22 and seven explicit liens. This is neither
   arbitrary production route selection nor qualification of landing/mining.
   #312 found the existing material-evidence schema sufficient; it created no
   CIVPROP persistence layer. #314 closes coverage accounting: 37/380 supported
   lanes, 343 UNKNOWN_AFTER_SEARCH, and 46 eligible bodies with inventory gaps.
   Candidate evidence must retain its status or receive separate promotion.
   The #308 reference-model reproduction requirement remains unfulfilled by M2.
2. **Seeded truth is compatible, but newly recommended rather than implemented.**
   Condition sourced priors on admitted evidence with its uncertainty, scope and
   conflicts; sample only residual uncertainty. Taxonomy is not composition;
   prior is not measurement; UNKNOWN is not zero; regional is not global;
   modelled is not observed. Freeze a realization per run and keep it separate
   from empirical Solar Facts. Universe/body/region/site keys must include stable
   identities and pinned generator/prior versions; lazy generation must be
   independent of discovery order and respect parent inventory/correlations.
   Freeze initial truth, then record depletion or other physical changes as
   events. New real evidence creates a new input/run version, not silent rerolls.
3. **Knowledge is explicit.** Only the observation mechanism reads hidden truth.
   Actors receive scoped, time-stamped observations with measurement uncertainty;
   private and public knowledge may differ. Discovery updates beliefs rather
   than creating deposits. Separate universe variation from noisy observations
   and actor randomness. General scientific archetype priors are not yet earned;
   labelled scenario fixtures may test the mechanism without claiming calibration.
4. **Keep persistence single-owned.** Choose **B** for any new Solar-CIVPROP
   SQLite: optional disposable, immutable experiment input/cache. Pin source
   snapshots, provenance/status, compiler/model versions, units/frames/epochs and
   hashes; retain the seed and prior versions with the run. It supports portable
   tests and Monte Carlo without becoming another editable authority. Existing
   Solar Facts SQLite has its own declared evidence role. Open #315's two proposed
   SQLite files are not promoted authority or mandatory next architecture.
5. **Preserve Earth and conditional development.** Consume a pinned Earth
   trajectory; record off-world capital/population transfers with reconciliation
   so they are not counted twice. Do not regenerate or overwrite Earth authority.
   Earth → Orbit → Luna → Mars → Belt/Ceres → outer system is a useful sequence
   for expanding implementation scope, not compulsory simulation history.
   Existing canon remains a comparator. Failure, delay and no settlement are valid.

Dorrington/Olsen fits the boundary cleanly: Solar supplies empirical constraints;
spatial/transport supplies opportunities, delta-v and time; technology supplies
spacecraft/mining/recovery; economics supplies prices, costs, capital and risk;
the kernel supplies profit/NPV/MPBR/BEMR as applicable; CIVPROP decides and acts.
Its asteroid architecture is not already a validated lunar extraction model.

## First vertical slice

One existing Earth country actor, one robotic Earth–orbit–Luna prospecting
mission, one lunar site and one resource question. Select an epoch with qualified
spatial coverage and explicitly available scenario technology. Freeze a bounded
site truth fixture constrained by admissible evidence; retain uncertain initial
actor knowledge. The actor evaluates WAIT/PROSPECT, funds and executes the mission,
receives an observation, updates knowledge, re-evaluates investment and records
capital expenditure plus a small installed survey/infrastructure asset. A changed
investment allocation or rejection suffices; settlement is not required.

Represent launch, transfer and landing capability explicitly at the chosen
abstraction. Reuse spatial authority, not the old future-ship assumptions or
Basemap geometry. Local operational gaps remain declared assumptions/blockers.

## One next executable milestone

**CIVPROP-0: one replayable Earth–Luna prospecting decision loop.** This is a
recommendation for the next authorized task; this review implements none of it.

- **Inputs:** pinned Earth actor/year and available-capital state; timeline and
  technology assumptions; qualified Earth/Moon state/coverage; scoped resource
  evidence with candidate/unknown status; versioned truth fixture/seed;
  explicitly bounded transport, observation and decision/economic rules.
- **Outputs:** a minimal run contract and demonstrator, event/observation/knowledge
  trace, before/after decision and capital/infrastructure ledger, and replay
  identity. Use declared scenario economics until the consumed D&O equations
  are implemented and verified; do not claim full D&O or lunar-model validation.
- **Stop:** one complete causal loop passes deterministic replay, discovery-order
  independence, no actor access to hidden truth, evidence-status preservation
  and stock/flow reconciliation. Exercise favourable and adverse observations;
  preserve WAIT/rejection as valid outcomes. Stop before multi-actor expansion,
  settlement demographics, catalog-wide priors or new resource research.

## Evidence

All paths below are relative to repository root; main references are pinned by
this review's recorded SHA. PRs use https://github.com/loom-2226/loom-2226/pull/NUMBER.

- #308 `d04a8ca`: `docs/solar_civprop/SOLAR_CIVPROP_READINESS_V1.md`.
- #309 `8539c4d`, #310 `4dc2652`: `reports/solar_civprop/NAV_MINIMUM_INPUT_CONTRACT_V1.md`,
  `NAV_M1_RECONCILIATION_V1.md`, `src/loom_solar_contracts/navigation.py`.
- #311 `3790725`: `reports/solar_civprop/DORRINGTON_OLSEN_M2_CIVPROP_ASSESSMENT.md`
  and `dev/resource_economics/dorrington_olsen/m2/`.
- #312 `a10b669`, #313 `f2d92ef`, #314 `78873ef`: resource contract, M4-A manifest,
  and `dev/solar_civprop_m4b/reports/M4B_QUALIFICATION_REPORT.md` plus coverage matrix.
- `data/postgres/migrations/004_earth_temporal_authority.sql`,
  `008_earth_schema_separation.sql`, `009_solar_ephemeris_foundation.sql`,
  `010_timeline_projection.sql`, `011_retire_ceres_postgres.sql`, and Solar 012–019.
  #279 `ab9965a` retired the Ceres projection, preserving Earth.
- `docs/earth_postgres_temporal_projection_2026_09_25.md`,
  `docs/database_semantics/LOOM_TIMELINE_POSTGRES_PROJECTION_v0.1.md`,
  `docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md`.
- `docs/database_semantics/recovery/LOOM_CIVSTATE_RECOVERY_CONSOLIDATION_v1.0.md`,
  `src/loom_navigator.py`, `src/loom_navigator_core.py`, `src/loom_solar_gis.py`.
- Open #299 `f0c373a`: `src/loom_solar_inspector.py`; open #317 `72472fa`:
  `engineering/solar_basemap/LEGACY_FORENSICS.md`; open #318 `2ce658c` and #320:
  derived prototype and bounded client repair. These are implementation evidence,
  not promoted-main authority. #316 `b22703a` adds future Navigator engineering
  plans only, not a runtime replacement.
- Open #315 `85597bf`: `docs/solar_civprop/M5_MINIMUM_INPUT_PIVOT.md`, proposal only.

Validation: evidence/status reconciliation and documentation diff check only.
No database, DDL, migration, runtime, canon, frozen research or existing plan changed.
