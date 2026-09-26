# SOLAR CIVPROP READINESS V1

Status: PROGRAM ROADMAP — NOT SCIENTIFIC AUTHORITY, NOT CANON, NOT ACTIVE WIP BY EXISTENCE  
Adopted intent: 2026-09-27

## Objective

Establish the minimum empirical Solar System knowledge required to support both flight/navigation and resource-extraction economics, then hand those capabilities to CIVPROP.

Solar Facts is an enabling evidence substrate, not an end-state planetary-science collection.

## Closure decision

SOLAR-BASELINE-02 WGCCRE closes broad physical-baseline enrichment.

After WGCCRE, additional Solar Facts enrichment requires a demonstrated downstream requirement from:
1. the Navigator minimum-input contract; or
2. the adopted resource-economics input contract.

Do not launch generic source/corpus enrichment merely because additional data exists. Missing information may remain explicit UNKNOWN.

## Program deliverables

### A. Minimum Flight / Navigation Contract

Derive requirements from the actual Navigator implementation rather than an astronomy wishlist.

Capability levels:
- NAV-0 IDENTIFIED — stable LOOM identity and authoritative external resolution.
- NAV-1 FLIGHT / RENDEZVOUS — minimum state/orbit, frame/epoch, size/gravity where dynamically required, validity and provenance sufficient for modeled interbody flight.
- NAV-2 LOCAL OPERATIONS — rotation/orientation/shape information sufficient for close and surface-relative operations.
- NAV-3 SURFACE OPERATIONS — regional shape/topography/terrain inputs sufficient for modeled surface operations where available.

Target: every modeled object is assessed for NAV readiness; NAV-1 is the minimum desired flight state where authoritative data permits. Higher levels are not prerequisites for CIVPROP screening.

### B. Dorrington & Olsen Reference Model

Implement the adopted Dorrington & Olsen asteroid-mining economic model faithfully before making LOOM-specific extensions.

Requirements:
- freeze authoritative publication/supplement artifacts and hashes;
- inventory symbols, units, equations, constants, architecture assumptions and outputs;
- implement typed reference inputs/outputs with equation-level traceability;
- reproduce published numerical examples where the publication permits;
- classify reproduction as EXACT, NUMERICALLY_EQUIVALENT, ROUNDING_DIFFERENCE, SUPPORTED_DIFFERENCE, or NOT_REPRODUCIBLE_FROM_PUBLICATION;
- hostile-test invalid units, missing inputs, impossible returned mass, zero recovery, extreme delta-v and other boundary cases.

The frozen reference implementation must not depend on CIVSTATE, LOOM future technology, Metric, fictional infrastructure or future prices.

### C. Minimal Solar Facts -> Dorrington & Olsen Contract

Classify every model input first as OBJECT FACT, TRANSPORT/DYNAMICS, ENGINEERING/TECHNOLOGY, or ECONOMIC. Only OBJECT FACT inputs belong to the Solar Facts contract.

For each empirical input record:
- D&O parameter and semantics;
- required units;
- Solar Facts property/evidence mapping;
- allowed evidence classes and spatial/temporal scope;
- permitted deterministic derivation;
- uncertainty and conflict handling;
- missing-data behavior;
- provenance requirement.

Readiness states:
- ECON-0 NOT ASSESSABLE;
- ECON-1 SCREENABLE;
- ECON-2 MODELABLE;
- ECON-3 INVESTMENT-GRADE / prospecting-quality.

ECON-0 is valid simulation state, not pipeline failure.

## Evidence firewall

MEASURED FACT != SCIENTIFIC INFERENCE != ENGINEERING ASSUMPTION != ECONOMIC ASSUMPTION.

Do not:
- convert taxonomy into exact composition without an explicit inference model;
- invent resource abundance from presence evidence;
- globalize regional observations;
- silently select among conflicting factual assertions;
- treat NULL/UNKNOWN as zero;
- place transport cost, extraction suitability, economic attractiveness or settlement value into Solar Facts.

## Execution sequence

1. Merge and close WGCCRE; release its temporary WIP capacity.
2. Inspect actual Navigator code and produce the NAV contract plus body-readiness report. Measure before enriching.
3. Reconstruct and validate Dorrington & Olsen as a standalone reference model.
4. Build the minimal Solar Facts -> D&O empirical contract from the implemented model.
5. Run NAV and ECON contracts against current SQLite and publish combined readiness/gap reports.
6. Classify every gap as EXISTING_FACT_NOT_MAPPED, DETERMINISTIC_DERIVATION_AVAILABLE, STRUCTURED_SOURCE_AVAILABLE, TARGETED_RESEARCH_REQUIRED, SCIENTIFIC_INFERENCE_REQUIRED, FUTURE_OBSERVABLE, or NOT_REQUIRED_BY_MODEL.
7. Permit only contract-driven remediation of blockers material to CIVPROP screening.
8. Freeze the operational contracts and hand their outputs to CIVPROP.

## WIP and PR discipline

This roadmap does not consume a Research Lab WIP slot merely by existing.

Use one active implementation stream for SOLAR_CIVPROP_READINESS_V1 and execute milestones sequentially. Do not create separate concurrent NAV, D&O, Solar Facts and enrichment streams unless genuine independent concurrency is explicitly authorized.

Expected PR sequence after WGCCRE:
- PR B: this roadmap + Navigator contract/readiness implementation;
- PR C: Dorrington & Olsen faithful reference implementation and publication regression;
- PR D: Solar Facts/D&O adapter, combined readiness and minimal contract-driven remediation.

A new enrichment PR is allowed only if PR D demonstrates a substantial blocking factual corpus that cannot be handled safely within it.

## Agent / Codex budget

Routine documentation, SQL inspection, adapters, contract generation, unit tests and refactors use ordinary implementation workflow.

Long autonomous/research runs are reserved for real uncertainty: faithful D&O reconstruction, a substantial new source adapter, or a new representation problem.

Hostile qualification is reserved for claims whose failure would corrupt downstream authority: D&O mathematical reproduction, provenance/evidence firewalls, deterministic reconciliation, or a major new epistemic representation.

Do not rerun already-qualified work without a concrete invalidation.

## Definition of Done

SOLAR_CIVPROP_READINESS_V1 is complete when:
1. Navigator can state whether modeled flight to every Solar object is supported and why.
2. The Dorrington & Olsen reference implementation reproduces the publication within documented tolerances.
3. Solar Facts can state whether each D&O empirical requirement is supported, derived, inferred, contested, partial or unknown.
4. Remaining unknowns are preserved rather than fabricated.
5. Ceres, 67P, Europa and representative asteroid cases exercise the integration and hostile boundaries.
6. NAV and ECON readiness outputs are consumable by CIVPROP.
7. No architectural Solar Facts work remains necessary to begin civilization propagation.

At completion, Solar Facts becomes operational/supporting infrastructure. Further scientific enrichment is optional and demand-driven.

## Governing finish line

Every modeled object should be navigationally assessable. Resource-economic readiness may legitimately vary from ECON-0 upward.

The program exists to enable civilization propagation, not to exhaust humanity's planetary-science archives.
