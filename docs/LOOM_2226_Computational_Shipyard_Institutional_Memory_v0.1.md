# LOOM 2226 — Computational Shipyard Institutional Memory v0.1

Status: ENGINEERING_RESEARCH / NON_CANON / NON_PRODUCTION

Authority: NO_FLIGHT_DYNAMICS_AUTHORITY / NO_SHIPCLASS_PROMOTION

## Purpose

This increment makes the shipbuilding institution, rather than the language model, the persistent causal entity in computational ship design.

The model records institutional state, historical designs, explicit lineage mechanisms, and dated yard-memory evidence. It then projects the admitted subset of that state into the existing model-neutral Designer/Critic context contract.

## Core records

### ShipbuildingInstitution

Persistent yard context includes founding and engineering lineage, design doctrine, preferred architectures, manufacturing capability, material access, explicit material constraints, explicit economic constraints, automation profile, component ecosystem, risk tolerance, maintainability doctrine, aesthetic principles, and provenance.

Material access is intentionally distinct from material constraints. No adapter may silently convert one into the other.

### HistoricalDesign

A historical design is an evidence-bearing record of an actual prior design state for the research model. It carries architecture family, mission roles, successful modules, manufacturing processes, suppliers, certification references, field evidence, and provenance.

Its authority is HISTORICAL_EVIDENCE_ONLY. It does not establish engineering PASS, canon, production status, or flight-dynamics authority.

### DesignLineageEdge

A lineage edge must name both designs and at least one admitted causal mechanism. Current mechanisms include tooling continuity, module reuse, supplier continuity, certification precedent, manufacturing-process continuity, field lessons, operator familiarity, and architectural precedent.

A lineage edge therefore means more than “these ships look related.” It states why a later design may inherit from an earlier one.

Self-loops, unknown designs, unsupported mechanisms, parent designs that post-date children, and cycles fail closed.

### YardMemoryEvent

A memory event records dated institutional learning such as design success/failure, field reports, supplier history, manufacturing-process continuity, module reuse, certification history, or maintenance experience.

Every memory event requires evidence and provenance. A snapshot may not consume memory from its own future.

## Temporal snapshots

InstitutionalMemorySnapshot is evaluated as-of a specific date. Historical designs and memory events later than that date fail closed.

This prevents future operational experience from leaking backward into earlier yard decisions and provides a deterministic basis for multi-decade design genealogy experiments.

## Designer/Critic projection

The persistent yard state projects into the existing ShipyardInstitutionContext without changing the Designer/Critic authority model.

Designer outputs remain PROPOSAL_ONLY.
Critic outputs remain CRITIQUE_ONLY.
Deterministic engineering evaluators remain the sole source of physical PASS/FAIL evidence.

Only semantically identical fields are projected. Data that has no admitted destination in the current agent contract remains in the persistent institution record rather than being silently reinterpreted.

## Culture and aesthetics firewall

Cultural progenitors, doctrine, historical precedent, and aesthetic principles may affect proposal bias and architectural review. They may not modify deterministic physical constraints or create hidden engineering conversions.

Institutional resemblance must emerge from explainable continuity such as tooling, process, supplier, certification, field experience, module reuse, and maintainability doctrine — not arbitrary style tags.

## Research use

This substrate supports the eventual two-yard common-mission experiment and the SOL test: whether mature designs can be attributed to a yard above chance for explainable engineering/institutional reasons after names and markings are removed.

It does not itself establish that such persistent family resemblance exists.

## Next increment

Recommended sequence:

1. Structured SOL architectural-review rubric and findings contract.
2. CandidateEvidencePackage → DesignCritique adapter with evidence-reference validation.
3. Executable DesignProposal mutation executor with fail-closed target/operation schemas.
4. First model-permutation Designer ↔ Critic experiment against the same deterministic back-end.
5. Only then broaden topology, multiplicity, sizing, translation, and rotation freedoms.
