# LOOM 2226 — Computational Shipyard Agent Architecture v0.1

**Date:** 2026-09-08  
**Status:** ENGINEERING / RESEARCH — NON-CANON — NON-PRODUCTION  
**Branch:** `research/computational-shipyard-agent-contracts-2026-09-08`

## Purpose

Preserve an explicit future interface for autonomous LLM design and critique while deterministic LOOM engineering remains the sole authority for physical validity.

The target is not merely an AI spaceship generator. It is a computational shipyard: a persistent engineering institution whose proposals are shaped by requirements, technology, economics, materials, manufacturing capability, engineering lineage, cultural inheritance, aesthetic doctrine and historical designs.

## Authority rule

LLMs may propose, criticize, prioritize, explain, request experiments and mutate search spaces. They may not declare a physical candidate valid, invent missing physics, convert OPEN values into admitted engineering data, promote a ship class to canon or create flight-dynamics authority.

Designer output is `PROPOSAL_ONLY`. Critic output is `CRITIQUE_ONLY`. Deterministic evaluators remain authoritative for admitted calculations and hard-constraint PASS/FAIL.

## Loop

```text
MISSION / CLASS REQUEST
        ↓
REQUIREMENTS COMPILER
        ↓
DESIGNER AGENT
        ↓ DesignProposal
DETERMINISTIC SYNTHESIS / SEARCH
        ↓
ENGINEERING EVALUATION
        ↓ evidence package
CRITIC AGENT
        ↓ DesignCritique
DESIGNER AGENT
        ↺
```

Every transition should eventually be content-addressed so a complete design genealogy can be reconstructed.

## Institution context

`ShipyardInstitutionContext` is deliberately separate from physics. It can carry:

- progenitor cultures;
- engineering lineage;
- design doctrine;
- aesthetic principles;
- manufacturing capabilities;
- material constraints;
- economic constraints;
- historical design references;
- provenance references.

Culture must not become a hidden numerical physics modifier. Cultural inheritance acts through institutional preferences, design doctrine, manufacturing practice, accepted architectural grammar and historical precedent. Material/economic/manufacturing limits constrain feasible realization through governed engineering adapters.

## Architectural aesthetics

Form is a legitimate design discipline but not a law of physics. Future critic categories should distinguish at least:

- engineering;
- maintainability;
- manufacturability;
- economics;
- operational suitability;
- requirement gaming;
- architectural legibility;
- structural honesty;
- hierarchy and proportion;
- purposeful symmetry/asymmetry;
- rhythm and economy of form;
- institutional/cultural fit;
- aesthetic preference.

Aesthetic criticism may motivate a new experiment or preference among physically legitimate candidates. It may never override a failed hard physical constraint.

## Design lineage

Historical designs should become first-class inputs rather than visual skins. Reused modules, tooling, supplier ecosystems, field failures, maintenance experience and prior successful architectures can bias future proposals. This permits visual identity to emerge from persistent engineering history.

The intended long-run experiment is to give multiple shipyards identical functional requirements under common physics but different industrial histories and contexts, then test whether their generated ships develop recognizable and explainable family resemblance.

## LLM interchangeability

The contract is model-neutral. Sol, Claude, another LLM or a non-LLM planner should be able to occupy Designer or Critic roles without changing deterministic engineering authority. Swapping Designer and Critic implementations is therefore an intended hostile test.

## v0.1 contracts

`shipyard_agent_contracts.py` defines:

- `DesignMutation`
- `DesignProposal`
- `CritiqueIssue`
- `DesignCritique`
- `ShipyardInstitutionContext`

All records have deterministic canonical JSON and content hashes. Proposals and critiques explicitly fail closed if they attempt to claim engineering authority.

## Next increments

1. Unit/dimensional requirement graph and explicit provenance edges.
2. Governed technology and industrial contexts.
3. Component catalog and requirement-to-component selection.
4. Capability-satisfaction and infeasibility reporting.
5. Candidate evidence package contract for critic consumption.
6. Designer proposal executor that maps admitted mutations into design grammar/search space.
7. Persistent shipyard history and design genealogy.
8. Structured architectural review rubric and SOL hostile design-review profile.
9. Multi-agent designer/critic permutation experiments.
10. Only after these foundations: aggressively broaden topology, sizing, multiplicity, translation and rotation freedom.

## Classification

```text
ENGINEERING_RESEARCH
NON_CANON
NON_PRODUCTION
NO_FLIGHT_DYNAMICS_AUTHORITY
NO_SHIPCLASS_PROMOTION
```
