# LOOM Authority Contract v1
## Phase 1 Archaeology - Independent Review Package

**Date:** 2026-10-03
**Owner:** @kT
**Status:** PRE-CONTRACT / PHASE 1 CLOSED BY OWNER / SUBMITTED FOR INDEPENDENT REVIEW
**Reviewer requested:** Claude
**Branch:** authority-contract-v1-phase0

## 1. Review task

Conduct an independent critical review of LOOM Phase 1 Authority Archaeology.

Do not assume the archaeology is correct because the owner accepted closure. Owner acceptance means only that the investigation was sufficiently broad and disciplined to serve as the evidence base for Phase 2. The owner did not independently certify every finding, and Phase 1 did not qualify any underlying LOOM holding.

Try to falsify the conclusions, identify unsupported leaps, distinguish evidence from inference, and determine whether the archaeology is sufficient to begin Phase 2 - Claim and Authority Model.

Do not redesign CIVPROP. Do not treat historical QUALIFIED, promoted, canon, database-resident, Git-merged, or tested material as automatically qualified under the future authority contract.

Return one of: ACCEPT; ACCEPT WITH LIENS; HOLD; REJECT.

For each finding assign CRITICAL, MAJOR, MINOR, or NOTE; identify the Phase 1 claim challenged; explain the evidence/reasoning; and state whether resolution is required before Phase 2.

## 2. Governing Phase 0 boundary

Phase 0 established claim-level rather than storage-level authority and three coequal integrity requirements: epistemic integrity, reproducibility/audit integrity, and causal integrity.

Relevant constraints:
- UNKNOWN is distinct from zero, false, empty, exclusion, interpolation and permission to infer.
- Simulation does not become evidence through storage/reuse.
- Projection and scenario assumption are distinct.
- Storage cannot create authority.
- Reference and realized state remain distinct.
- Historical qualification is provenance, not v1 qualification.
- Assumptions, model parameters and governance judgments require human-rooted authorization; delegation is default-deny until governed.
- Conflict remains information unless a governed resolution rule applies.
- Qualification is scoped.
- Known uncertainty is preserved; uncharacterized uncertainty is not certainty.
- Existing work must pass applicable future interface/claim qualification before governed consumption.
- Work remains PRE-CONTRACT until LOOM_AUTHORITY_AND_STATE_CONTRACT_v1 is released.
- D0.18 left authority roots extensible pending archaeology.
- D0.20 requires independent authorization where required or explicit SINGLE-AUTHORITY disclosure.

Phase 1 was descriptive. It was not authorized to repair historical systems or invent the Phase 2 taxonomy.

## 3. Method and evidence boundary

Phase 1 inspected current GitHub main, the connected quantifactus VM read-only for relevant filesystem/PostgreSQL state, and historical CIVPROP only as archaeology.

The Phase 1 branch originated from main SHA 27c5a4cb0b968baed219ffde48c550db6690a3c7.

VM inspection established that /home/ubuntu/LOOM_DEV was itself a dirty historical worktree on another branch, so it was treated as local/historical evidence rather than branch authority.

Observed PostgreSQL loom_dev schemas included loom_control, loom_earth, loom_solar, loom_timeline, loom_narrator and loom_gate_l_qual.

Observed row counts:
- loom_control.snapshot: 2
- loom_control.source_artifact: 18
- loom_earth.earth_area: 237
- loom_earth.earth_demographic_year: 47,637
- loom_earth.earth_economic_year: 16,080
- loom_earth.earth_sector_year: 160,800
- loom_solar.body: 110
- loom_timeline.milestone: 43

Observed snapshots were earth-v0-1-9934d0ac-20260925 and timeline-v0-1-0232bf23494f-20260925. These are inventory facts, not v1 qualification.

All 40 archaeology questions were classified ESTABLISHED, NOT LOCATED or NOT ESTABLISHED. Partial findings were labeled partial.

## 4. Principal result

The original shorthand of four authoritative pillars - Earth, Technology, Solar and Agents - does not accurately describe LOOM's actual authority landscape.

Phase 1 instead found a network of empirical/source claims, modeled reference trajectories, projections, authored scenarios, parameters, explicit unknowns, physical/mathematical transforms, identity/crosswalk contracts, governance decisions, qualification/promotion records, compiled interfaces and simulated state.

The diagnosis is that LOOM historically developed local authority disciplines without one common authority contract or governed consumption boundary.

The reviewer should attack this diagnosis rather than accept it as framing.

## 5. Earth

Earth holdings include pointers, promotion records, model specifications, field semantics, provenance, qualification records, VM-resident promoted artifacts and PostgreSQL projections.

A material coverage distinction exists between 237 WPP demographic areas and 80 economically modeled economies.

Earth holdings distinguish source evidence from modeled future/reference state in multiple places, but not through a common LOOM taxonomy.

A material fallback example is the investment-rate repair. It uses current WDI observations where available and, where missing, an unweighted median of 2024 WDI percentages for 74 modeled economies: 22.3283039488531%. It is explicitly labeled authored pooled imputation, not observation. Six recipients are recorded: ARE, JOR, LAO, MMR, NGA and TWN.

Named Earth records distinguish calibration from endpoint targeting, including Nigeria's 2226 share as diagnostic rather than calibration target and explicit statements against country outcome caps/ranking/2226 Atlas calibration. Phase 1 does not claim universal fit/validation independence.

Some Earth packages preserve strong reproducibility evidence including run manifests, hashes, exact runner bytes and deterministic reruns. This does not establish universal reproducibility.

## 6. Technology/timeline

Timeline storage preserves materially different classes, including governing canon history, moderate scenario anchors, speculative fictional-physics anchors and social scenario anchors. PostgreSQL storage does not by itself promote these classes.

A milestone date is therefore not automatically equivalent to observed fact, forecast, installed capability, actor access or mission feasibility.

## 7. Solar

Solar contains distinct authority families: identity, physical/metadata, SPICE/DE440 ephemeris/spatial state, material evidence, coverage/search state, transport/accessibility calculation, qualification and promotion.

M4-B records 95 eligible bodies, four resource families, 380 body-family lanes, 37 supported lanes and 343 UNKNOWN_AFTER_SEARCH lanes. It includes a negative fixture for UNKNOWN-to-zero corruption and preserves candidate status separately from promotion.

The archaeology does not support replacing absent resource evidence with generic class-prior resource values.

Solar identity uses canonical body_id, NAIF identifiers and explicit crosswalks; ambiguity can be held rather than resolved by name fallback. No universal cross-domain identifier registry was established.

## 8. Actors

governance/agents/AGENT_REGISTRY.yml describes autonomous LOOM technical agents and must not be conflated with simulated civilization actors.

Historical CIVPROP also contains CIVPROP_ACTOR_STATE_V1, compiled actor inputs, actor-access evidence, capability contracts and synthetic actor fixtures.

No single canonical actor registry for future CIVPROP was established. Historical CIVPROP itself records unresolved authority for actor access/capability, spendable budgets, provider/service rights, prices/envelopes and related decision inputs.

## 9. Physical/mathematical authority

LOOM consumes physical/mathematical outputs outside the four-domain shorthand, including SPICE/DE440 state, Lambert accessibility and engineering transforms. Existing material distinguishes ephemeris state from transport-model output and propulsion assumptions.

Phase 2 must adjudicate standing/root treatment for physical law, mathematical relationships, standards/identity, institutional/canon authority and internally verified deterministic computation. Phase 1 does not assert each is a separate root.

## 10. Parameters

Located historical standings include:
- demand pressure: UNCALIBRATED_CAUSAL_MODEL_PARAMETER_V1
- mission observation: UNCALIBRATED_SCENARIO_OBSERVATION_MODEL
- infrastructure Method Lab: SYNTHETIC_METHOD_FIXTURE
- resource/process: UNRESOLVED_PROCESS_MODEL
- asset lifecycle: NO_EMPIRICAL_LIFECYCLE_PARAMETERS_ADMITTED
- actor bridge: versioned allocation fractions, commitment threshold and decision noise
- CIVPROP-0: synthetic prior, error rates, costs/value and threshold
- Earth TFP: inherited transition half-life identified as forecast assumption
- Earth demographic/biosynthetic successor: explicit parameter sets and calibration schedules

The finding is heterogeneous parameter standing/authorization, not total absence of parameter governance.

## 11. UNKNOWN/null/default audit

Bounded current-main search found:
- COALESCE in CIVPROP capture/compiler around json_agg, converting no query rows to JSON [], not numeric substitution.
- traffic_fleet_v1.py uses x[1] or 0 only after an all-values-known guard; unknown input returns None.
- asset_lifecycle_v1.py uses replacement_capital or 0.0 for explicit replacement events; semantic safety was not established.
- no fillna/dropna hits in searched current-main CIVPROP/Earth-baseline paths.

Phase 1 does not claim all SQL/Python paths preserve UNKNOWN. It only found no evidence of an obvious pervasive numeric UNKNOWN-to-zero convention.

## 12. Knowledge time

Positive controls include actor-state as_of_year, service evidence as_of, actor fixture as_of_date, gap-register as_of_main_commit, actor-capability validity/observation-date rules, and Solar research cutoffs/blindness boundaries.

No common LOOM-wide knowledge-time schema exists and system-wide absence of temporal leakage was not proven.

## 13. Human authorization and AI/automation provenance

Concrete human-authorization examples exist. Earth v4 records Kevin's explicit 2026-09-24 promotion-scope decision; a later disposition records controlled-implementation approval and change-control linkage.

No common machine-readable authorization ledger was located.

Automated builders/validators are identifiable, but Phase 1 did not locate systematic historical metadata distinguishing human-authored, AI-assisted, AI-generated or automated classification decisions. Absence of an AI marker was not treated as evidence of human authorship.

## 14. Producer-consumer/state findings

The broad historical spine recovered is:

source artifacts -> domain builders/importers -> projections/compiled inputs -> historical propagation -> event/state outputs -> Atlas/GIS/materialized consumers.

Historical requirements also describe a replaceable compiled/frozen input boundary. This is archaeology, not adoption.

No currently governed two-way CIVPROP-Earth realized-state feedback loop was established.

## 15. Qualification

Historical mechanisms include validators, tests, hostile fixtures, deterministic reruns, promotion validators, qualification reports, coverage matrices, manifests/hashes, liens and NOT_TESTED dimensions.

No universal mapping currently establishes claim -> applicable test -> contract -> qualification decision -> permitted use. Historical QUALIFIED therefore remains scoped historical provenance.

## 16. Unresolved risk register

1. Parameter authorization: multiple standings, no common authorization model. Proposed destination: Phase 2.
2. Producer-consumer dependency: architectural spine established, exhaustive machine graph absent. Proposed destination: runtime/snapshot tooling.
3. AI/automation provenance: non-uniform. Proposed destination: Phase 2 provenance rules.
4. Human approvals: examples exist, no common ledger. Proposed destination: Phase 2 authorization model.
5. NULL/UNKNOWN loss: fail-closed examples plus scoped lifecycle concern, no universal audit. Proposed destination: qualification/static tests.
6. Fit/validation reuse: positive controls, no universal ledger. Proposed destination: Phase 2 plus qualification.
7. Temporal leakage: local controls, no universal knowledge-time contract. Proposed destination: Phase 2 plus qualification.
8. Identifier compatibility: known incompatibility classes, no universal registry. Proposed destination: Phase 2 semantics and later qualification.
9. Physical/mathematical standing: real and consumed, root treatment unresolved. Proposed destination: Phase 2 authority-root adjudication.

Determine whether any are incorrectly deferred and actually block Phase 2.

## 17. Claims deliberately NOT made

Phase 1 closure does not establish that every finding is exhaustive/correct; NOT LOCATED or NOT ESTABLISHED proves absence; historical QUALIFIED equals v1-qualified; all outputs are reproducible; all NULL paths are safe; all parameters are independently authorized; all validation targets are independent; all artifacts have knowledge-time protection; all AI involvement is recorded; storage creates authority; previous CIVPROP is adopted; or the Phase 2 taxonomy is already known.

## 18. Owner closure

Owner statement:

> I accept that the Phase 1 archaeology was conducted with sufficient scope and discipline to serve as the evidence base for Phase 2, subject to its recorded limitations and unresolved findings. I do not independently certify every archaeological finding, nor does this acceptance qualify any underlying LOOM holding.

This establishes evidence sufficiency to proceed, not independent verification. Later evidence may refine Phase 1 with preserved lineage.

## 19. Questions Claude must answer

1. Did Phase 1 inspect the right classes of holdings, or is a major authority family missing?
2. Is the conclusion that the four-pillar model is inadequate supported?
3. Did Phase 1 improperly infer authority from documentation, qualification, promotion, storage or code?
4. Were any ESTABLISHED findings too strong?
5. Were any NOT ESTABLISHED findings prematurely deferred?
6. Is Earth archaeology sufficient for Phase 2?
7. Does Solar archaeology correctly preserve M4-B UNKNOWN semantics/candidate status?
8. Is actor-authority diagnosis sufficiently skeptical?
9. Was physical-law authority adequately distinguished from model-derived physical calculation?
10. Is parameter-standing inventory sufficient without enumerating every parameter value?
11. Is bounded NULL/default audit enough for archaeology?
12. Is knowledge-time evidence sufficient to defer full leakage testing?
13. Are human-authorization examples sufficient while ledger design is deferred?
14. Is missing historical AI-authorship metadata prospective governance rather than a Phase 1 blocker?
15. Is the producer-consumer spine sufficient without a machine-complete dependency graph?
16. Did Phase 1 distinguish reproducibility evidence from universal reproducibility?
17. Are unresolved risks being pushed downstream even though they would change the Phase 2 ontology?
18. Does evidence support considering additional authority roots under D0.18?
19. Is owner closure appropriately narrow?
20. Bottom line: may Phase 2 begin without creating epistemic debt that should have been resolved in Phase 1?

## 20. Required source inspection

At minimum inspect:
- governance/authority_contract/00_AUTHORITY_PROBLEM_STATEMENT.md
- governance/authority_contract/01_PHASE1_AUTHORITY_ARCHAEOLOGY.md

For challenged findings inspect current-main source artifacts directly, especially:
- manifests/earth_long_run_economic_baseline/
- docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md
- docs/database_semantics/LOOM_TIMELINE_POSTGRES_PROJECTION_v0.1.md
- data/postgres/migrations/
- dev/solar_civprop_m4b/
- Solar identity/ephemeris/SPICE contracts
- engineering/civprop/
- governance/agents/AGENT_REGISTRY.yml

Cite exact paths and behavior where material.

A proposed blocker must identify a specific missing fact whose absence materially prevents construction of Phase 2. Conversely, do not defer an unsupported Phase 1 claim if it would distort the ontology, authority roots, standing rules, scope model or qualification design.
