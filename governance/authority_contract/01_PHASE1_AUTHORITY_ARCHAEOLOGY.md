# LOOM Authority Archaeology and Source Inventory
## Phase 1 Working Record — Pass 1

**Date:** 2026-10-03  
**Owner:** @kT  
**Branch:** `authority-contract-v1-phase0`  
**Status:** PRE-CONTRACT / DESCRIPTIVE ARCHAEOLOGY / CANDIDATE  
**Governing predecessor:** `00_AUTHORITY_PROBLEM_STATEMENT.md`, Revision 3, Phase 0 CLOSED

## 1. Method

This record begins Phase 1 under §34 of the Phase 0 authority statement.

Rules for this phase:

- inspect actual holdings;
- do not silently repair defects;
- do not grandfather historical qualification into v1 qualification;
- classify every archaeology answer as `ESTABLISHED`, `NOT LOCATED`, or `NOT ESTABLISHED`;
- require identifiable evidence for `ESTABLISHED`;
- treat all archaeological classifications and proposed mappings as CANDIDATE until human acceptance;
- preserve the distinction between GitHub authority records, VM-resident artifacts, PostgreSQL projections, SQLite holdings, scenario material, and simulated outputs.

Pass 1 inspected current GitHub `main` and read-only state on the connected `quantifactus` VM. It did not modify source holdings.

## 2. Evidence Boundary Recorded in Pass 1

### GitHub

Repository: `loom-2226/loom-2226`.

The Phase 0 branch was created from current `main` at `27c5a4cb0b968baed219ffde48c550db6690a3c7`. Phase 1 archaeology treats current-main holdings as evidence and previous CIVPROP implementations as archaeology, not inherited architecture.

### quantifactus

The VM contains numerous historical LOOM worktrees/artifact directories, including Earth, Solar, CIVPROP, qualification, recovery and experimental runs. Their existence does not establish current authority.

The local `/home/ubuntu/LOOM_DEV` Git worktree is **not** current main. At inspection it was on `fix/ceres-atlas-display-semantics-20260921` at `625e139a32f3461068e2b84192725e79f42a4c89` with modified and untracked files. It is therefore evidence of historical/local state only and shall not be treated as the branch authority for this Phase 1 work.

PostgreSQL database `loom_dev` is live and contains schemas:
`loom_control`, `loom_earth`, `loom_solar`, `loom_timeline`, `loom_narrator`, and `loom_gate_l_qual`.

Observed direct row counts include:

| Relation | Rows |
|---|---:|
| `loom_control.snapshot` | 2 |
| `loom_control.source_artifact` | 18 |
| `loom_earth.earth_area` | 237 |
| `loom_earth.earth_demographic_year` | 47,637 |
| `loom_earth.earth_economic_year` | 16,080 |
| `loom_earth.earth_sector_year` | 160,800 |
| `loom_solar.body` | 110 |
| `loom_timeline.milestone` | 43 |

The two observed PostgreSQL snapshot IDs are:
- `earth-v0-1-9934d0ac-20260925`
- `timeline-v0-1-0232bf23494f-20260925`

This is an inventory fact, not a v1 qualification.

## 3. Domain Inventory — Initial Findings

### Q1. What artifacts supply Earth information?
**ESTABLISHED — partial inventory.**

Evidence located:
- `manifests/earth_long_run_economic_baseline/` with current pointers, promotion records, model specifications, field semantics, provenance and qualification records.
- VM-resident promoted Earth artifacts under `/home/ubuntu/loom_earth_2026_2035/`.
- PostgreSQL `loom_earth` projection with annual demographic, economic, sector, asset and labor/cohort relations.
- `loom_control.temporal_coverage` records separate 237-area demographic coverage from 80-economy economic coverage and record modeled/superseded periods.
- `loom_control.source_artifact` hash-pins WPP source files and promoted/model output files with source Git commits and retained locations.

Finding: “Earth” is not one homogeneous authority. It contains source evidence, modeled reference trajectories, promoted successors, semantic records and operational projections.

### Q2. What artifacts supply technology/scenario information?
**ESTABLISHED — initial inventory.**

Evidence located:
- `docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md`.
- `data/postgres/migrations/010_timeline_projection.sql`.
- `docs/database_semantics/LOOM_TIMELINE_POSTGRES_PROJECTION_v0.1.md`.
- PostgreSQL `loom_timeline`.

Observed PostgreSQL milestone classes:
- 19 `CANON_HISTORY / GOVERNING_CANON / CANON_HISTORY`;
- 18 `MODERATE_SCENARIO_ANCHOR / PROVISIONAL_SIMULATION_SCAFFOLD / AUTHOR_SCENARIO_MODERATE`;
- 5 `FICTIONAL_PHYSICS_SCENARIO_ANCHOR / PROVISIONAL_SIMULATION_SCAFFOLD / SPECULATIVE_FICTION`;
- 1 `SOCIAL_SCENARIO_ANCHOR / PROVISIONAL_SIMULATION_SCAFFOLD / AUTHOR_SCENARIO_MODERATE`.

Finding: timeline storage already preserves materially different authority/epistemic classes. PostgreSQL storage is explicitly not promotion.

### Q3. What artifacts supply Solar information?
**ESTABLISHED — partial inventory.**

Evidence located:
- PostgreSQL `loom_solar` identity/metadata/ephemeris relations, including 110 bodies.
- Solar identity/ephemeris contracts and SPICE foundation material.
- `dev/solar_civprop_m4b/` candidate material-evidence campaign.
- M4-B reports including qualification, coverage, hostile validation and unresolved frontier.
- VM copy `/home/ubuntu/LOOM_SOLAR_ENRICHMENT_TARGETS_2026-10-03/LOOM_SOLAR_CIVPROP_M4B_CANDIDATE.sqlite3`.

M4-B records 380 body×resource-family lanes across 95 eligible bodies, 37 supported lanes and 343 `UNKNOWN_AFTER_SEARCH` lanes. Candidate material evidence remains distinguishable from promoted information.

Finding: “Solar” contains at least identity, physical/metadata, ephemeris/spatial, empirical material evidence, coverage state and model/transport-related families. It is not a single authority class.

### Q4. What artifacts define actors?
**ESTABLISHED — incomplete and semantically split.**

Evidence located:
- `governance/agents/AGENT_REGISTRY.yml` defines autonomous LOOM technical agents, not necessarily CIVPROP civilization actors.
- `engineering/civprop/contracts/actor_state_v1.py` defines historical CIVPROP actor-state machinery.
- CIVPROP compiled inputs and scoped actor-access evidence exist for actors such as `AUS`.
- Prior CIVPROP documentation explicitly notes gaps in generic actor technology/access/budget evidence.

Finding: no single canonical “agent/actor registry” has yet been established for the future CIVPROP meaning. Technical LOOM agents and simulated civilization actors must not be conflated.

### Q5. What relevant sources exist outside those domains?
**ESTABLISHED — initial inventory.**

At least:
- governing canon chronology;
- physical/spatial/ephemeris authority;
- transport/accessibility models;
- resource economics;
- institutional/governance records;
- database semantic dossiers and recovery records;
- qualification/test artifacts;
- physical-law and mathematical machinery;
- identifier and vocabulary contracts.

This confirms that the earlier four-domain picture is an organizational convenience, not a complete authority model.

### Q6. Where do physical-law and transport authorities reside?
**ESTABLISHED — partial inventory.**

Evidence located in Solar spatial foundation, SPICE/DE440 ephemeris machinery, transport/accessibility contracts and Lambert-related CIVPROP/engineering artifacts. Existing documentation distinguishes qualified local SPICE state from Lambert accessibility modeling and from later propulsion models.

The complete authority-root treatment remains NOT ESTABLISHED pending deeper inventory.

### Q7. What institutional/governance rules exist?
**ESTABLISHED — partial inventory.**

Evidence includes current canon/governance records, historical qualification/promotion decisions, Phase 0 governance, source-role classifications, and technical agent registry/governance material.

A complete institutional-authority inventory is not yet established.

### Q8. What model parameters exist explicitly or implicitly?
**NOT ESTABLISHED.**

Explicit parameters are known to exist across Earth models, technology scenarios, transport, resource economics and historical CIVPROP machinery, but Phase 1 has not yet produced a complete parameter inventory or separated fitted, assumed, derived and hard-coded values.

### Q9. Which artifacts carry provenance?
**ESTABLISHED — partial inventory.**

Examples include Earth `PROVENANCE.md` and run/baseline manifests, PostgreSQL `loom_control.source_artifact`, source Git commits, SHA-256 records, timeline source links, M4-B evidence/coverage lineage and CIVPROP compiler manifests.

Completeness across holdings is not yet established.

### Q10. Which carry qualification or promotion status?
**ESTABLISHED — partial inventory.**

Earth promotion/qualification records, M4-B qualification/hostile-validation reports, timeline authority/epistemic classes, Solar qualification artifacts and numerous historical CIVPROP qualification/gate records exist.

Historical labels do not equal v1 qualification under D0.6/D0.19.

## 4. Immediate Archaeological Findings

1. **The VM is not itself an authority root.** It contains many mutually historical worktrees, databases and generated artifacts.
2. **The live PostgreSQL projection is richer than the four-pillar shorthand.** It already carries snapshots, source artifacts, temporal coverage and multiple semantic classes.
3. **Current PostgreSQL does not contain the full Solar material-evidence campaign.** Solar identity/ephemeris and M4-B material evidence currently span different representations.
4. **Earth reference material is explicitly modeled and coverage-limited.** 237-area demographic coverage must not be silently equated to 80-economy economic coverage.
5. **Technology/scenario separation is already encoded in several places.** That historical design is evidence for Phase 2, not automatically the final v1 taxonomy.
6. **Actor authority remains structurally weak compared with Earth/Solar/timeline holdings.**
7. **Previous CIVPROP code is evidence of prior design decisions and defects, not the architecture of the new CIVPROP.**

## 5. Next Pass

Pass 2 shall continue Q11–Q40 and deepen Q1–Q10 where current answers are explicitly partial. Priority targets are:

- observation vs projection;
- UNKNOWN vs zero/absence;
- uncertainty representation;
- candidate vs promoted state;
- simulated/reference mixing;
- consumers and transformations;
- qualification mechanisms;
- shared/incompatible identifiers;
- authority by convention and missing apparent authorities;
- assumptions and mutability;
- causal reproducibility;
- AI/automation provenance and human approvals;
- fallback/imputation/interpolation/clamping/default/null-coalescing;
- units/currency/base year;
- knowledge time;
- crosswalks;
- feedback/calibration/fitting;
- code recoverability;
- test/gate coverage;
- conflicts;
- unknown-dropping joins/filters/aggregations;
- additional authority roots;
- physical-law/mathematical authority;
- temporal leakage.

No repair is authorized by this record.
