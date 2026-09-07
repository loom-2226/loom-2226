# LOOM 2226 — Research Authority Boundary v1.0

**Status:** GOVERNING / CLASS: GOVERNANCE  
**Date:** 8 September 2026

## Core rule

> **ACTIVE RESEARCH BELONGS IN `loom-2226/loom-research-lab`.**

The main LOOM repository remains authoritative for canon, engineering, runtime, data, release, governance, historical scientific records, frozen/preregistered scientific objects, and all promotion/disposition decisions affecting LOOM.

The Research Lab is authoritative for active non-canon research execution and research-program development under its own project manifests and governance.

## Main LOOM retains

- current canon and canon change control;
- engineering/certification authority;
- runtime, data, Navigator/GIS, simulation and release authority;
- governance and repository-wide change control;
- historical research objects already committed here;
- frozen/preregistered scientific objects and their exact Git identity;
- disposition and promotion decisions that affect LOOM;
- the right to accept, reject, bound, or request further qualification of Research Lab outputs.

## Research Lab owns

- active Relational Foundations research after the migrated baseline;
- active Anomaly Phenomenology & Provenance research;
- active Foundations & Consequences research;
- successor protocols, methodology, literature work, simulations, provenance work, hostile review, negative/unresolved results, hypotheses, discriminators and pre-canon implication work;
- lab-native research governance and project manifests.

## Frozen and historical upstream objects

The following remain upstream historical/frozen objects and MUST NOT be mutated merely because active research moved:

- PR #19 exact frozen head `314efe50875630ba4be720b4097a2ca14075e620`;
- PR #16 exact preregistered/on-hold head `b60086d906f63211206502f23458be490902c2df`;
- PR #20 historical Foundations & Consequences source head `74120daed077f7e0401b4e348dc0620df9d9b844`.

Their Git identity remains authoritative here. Successor work belongs in the Research Lab unless an explicit governed exception is approved.

## No dual-active research authority

Historical `research/**` content in this repository does not by itself authorize new active research here.

Existing upstream research branches may remain open for provenance, frozen qualification, preregistration, or historical disposition. They are not a standing license to create successor research on upstream branches.

Where older governance/workstate text describes S4, F2, P1, PR #20, or other migrated research as resumable upstream WIP, this boundary supersedes that interpretation for active research responsibility. Their historical state remains preserved; successor active research belongs in the Research Lab.

PR #19 and PR #16 are exceptions only in the sense that their exact frozen/preregistered upstream objects remain governed upstream objects. Any successor experiment or theory change belongs in the Lab.

## Upstream research retirement

The governing retirement registry is:

`governance/current/LOOM_UPSTREAM_RESEARCH_RETIREMENT_v1.0.yml`

The `research/**` tree is retained as historical/reference material and as a host for exact frozen/preregistered upstream objects. It is not an active successor-research workspace.

`research/README.md` and `research/AGENTS.md` are the human/agent front doors for that retired surface.

Retirement does not delete historical files, rewrite failed/null/inconclusive results, alter evidence status, or mutate frozen/preregistered objects.

## Promotion direction

Research Lab outputs do not self-promote.

Normal direction is:

`Research Lab research -> explicit disposition packet -> upstream LOOM decision -> CCR/canon or other governed upstream action as applicable`.

A Lab result cannot edit canon, engineering, runtime or data by implication.

## Standard Lab-to-LOOM handoff

The governing upstream intake contract is:

`governance/current/LOOM_LAB_RESEARCH_DISPOSITION_INTAKE_v1.0.md`

The standard Lab packet is defined in the Research Lab at:

`shared/disposition/LAB_TO_LOOM_DISPOSITION_PACKET_TEMPLATE.yml`

A completed packet is a request for upstream disposition only. It must preserve source-project evidentiary status, exact provenance, qualification state, limitations, negative results, unresolved results, bridge state, requested upstream action, dependencies, and explicit `does_not_establish` boundaries.

Canon-facing packets may request `OPEN_CCR_INTAKE`; they do not constitute or approve a CCR. Engineering/runtime/data-facing packets likewise authorize nothing until upstream creates and governs the appropriate work item.

Upstream may reject, defer, return for qualification, archive, accept only as nonauthoritative input, or authorize a separate governed intake object.

## Cross-project evidence

Research projects remain epistemically separate. Cross-project evidentiary promotion is forbidden by default and requires explicit bridge governance under the relevant Lab manifests.

Convergence raises priority, not truth.

## Does not establish

This boundary establishes repository responsibility only. It does not establish any scientific result, method confirmation, physics confirmation, M1/M2/M3, hidden topology, anomaly ontology, reviewer endorsement, canon promotion or runtime change.
