# LOOM 2226 — SOL Architectural Review v0.1

Status: ENGINEERING_RESEARCH / NON_CANON / NON_PRODUCTION

## Purpose

Formalize architectural criticism as a first-class but non-authoritative layer in the Computational Shipyard.

SOL may judge whether a physically evaluated candidate forms a coherent ship architecture. SOL may not determine physical feasibility, close OPEN engineering items, create flight-dynamics authority, mutate canon, or promote production shipclasses.

The governing separation is:

PHYSICAL EVALUATION != ARCHITECTURAL REVIEW

A candidate may be physically feasible and architecturally rejected. An architectural rejection means "do not prefer or advance this architecture without revision"; it does not mean "physics failed."

## Default doctrine: Functional Expressionism

A LOOM ship should look inevitable. Major form should make function, force flow, system hierarchy, maintenance logic, and institutional lineage legible.

The default review families are:

- LEGIBILITY
- STRUCTURAL_HONESTY
- PURPOSEFUL_SYMMETRY
- MEANINGFUL_ASYMMETRY
- HIERARCHY
- PROPORTION
- RHYTHM
- ECONOMY_OF_FORM
- MAINTAINABILITY_EXPRESSION
- IDENTITY_FROM_FUNCTION

These criteria are review concepts, not pseudo-physical scoring terms. A critic may use them to prefer one physically valid candidate over another or request an experiment. They may never be injected into engineering equations as arbitrary bonuses or penalties.

## Evidence requirement

Every DesignReviewFinding must reference evidence. Acceptable evidence may include geometry/topology records, system locations, load-path analysis, dimensional evidence, requirement provenance, manufacturing evidence, maintenance/access analysis, institutional context, or lineage records.

Unsupported aesthetic assertion is not a valid finding.

## Severity semantics

NOTE — observation worth retaining; no revision required.

WARN — architecture has a material weakness or ambiguity; overall ACCEPT is forbidden.

REJECT — architecture should not advance unchanged. Any REJECT finding forces overall architectural REJECT.

Severity propagation is deterministic. The critic chooses findings; the contract controls what recommendations are legally consistent with them.

## Authority firewall

All doctrine, criterion, finding, and report records carry:

ARCHITECTURAL_REVIEW_ONLY

The report contains explicit forbidden authority-claim flags. Any attempt to claim physical feasibility, flight-dynamics authority, canon mutation, or production shipclass mutation fails closed.

Therefore:

ENGINEERING PASS + SOL REJECT

is a legal state.

SOL REJECT does not rewrite the engineering result.

## Anti-patterns encoded in the doctrine

The doctrine explicitly rejects styling-first geometry, fake aerodynamic features, random fins/windows, greeble density used as complexity, glowing-strip identity, naval-bridge cosplay, radiators treated as afterthoughts, and obscured primary load paths.

These are architectural objections unless a separate deterministic engineering evaluator establishes a physical consequence.

## Intended interface

Next layer:

CandidateEvidencePackage
        +
ShipyardInstitutionContext
        +
ArchitecturalDoctrine
        ↓
Critic LLM
        ↓
DesignReviewFinding[]
        ↓
DesignReviewReport
        ↓
structured DesignCritique / experiment requests

The Critic receives evidence; it does not manufacture evidence.

## Long-run test

This layer supports the future SOL Test: remove names and markings from mature generated ships and ask whether the shipyard can be identified above chance from architecture and engineering evidence, with explanations grounded in real institutional lineage rather than arbitrary styling.
