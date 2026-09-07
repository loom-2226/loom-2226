# LOOM 2226 — Research Lab Disposition Intake v1.0

**Status:** GOVERNING / CLASS: GOVERNANCE  
**Date:** 8 September 2026

## Purpose

This contract defines how upstream `loom-2226/loom-2226` receives research outputs from `loom-2226/loom-research-lab` after the reciprocal M4 authority split.

The standard Lab handoff artifact is:

`shared/disposition/LAB_TO_LOOM_DISPOSITION_PACKET_TEMPLATE.yml`

A completed Lab packet is a **request for upstream disposition**. It is never, by itself, a canon decision, engineering approval, runtime/data approval, release approval, or evidence-status upgrade.

> **Lab research does not self-promote.**

## Required upstream intake fields

Before substantive disposition, upstream review MUST verify that the packet contains:

- exact Lab repository and source commit SHA;
- registered Lab project ID and project manifest;
- exact source artifacts and provenance classes;
- source-project evidence status;
- qualification/preregistration/execution or review state;
- explicit result verdict;
- limitations;
- negative results;
- unresolved results;
- claim-by-claim evidence classes and source references;
- cross-project bridge state;
- explicit confirmation that evidentiary weight was not combined across projects;
- requested upstream action and scope;
- dependencies/affected upstream authority surfaces;
- known provenance gaps;
- hostile/independent review status;
- explicit `does_not_establish` list;
- Lab attestation that research does not self-promote.

A packet missing material negative/unresolved results or provenance limitations is incomplete, even when the headline result is positive.

## Permitted Lab requests

A Lab packet may request only:

- `NO_UPSTREAM_ACTION`
- `ARCHIVE_AS_RESEARCH_RECORD`
- `REQUEST_MORE_RESEARCH`
- `REQUEST_INDEPENDENT_REVIEW`
- `OPEN_CCR_INTAKE`
- `OPEN_ENGINEERING_INTAKE`
- `OPEN_RUNTIME_DATA_INTAKE`
- `OPEN_GOVERNANCE_INTAKE`

These are requests, not outcomes.

## Upstream disposition states

Upstream LOOM may record one of the following disposition classes:

- `REJECTED`
- `DEFERRED`
- `RETURNED_FOR_QUALIFICATION`
- `ARCHIVED_AS_RESEARCH_RECORD`
- `ACCEPTED_AS_NONAUTHORITATIVE_INPUT`
- `CCR_INTAKE_AUTHORIZED`
- `ENGINEERING_INTAKE_AUTHORIZED`
- `RUNTIME_DATA_INTAKE_AUTHORIZED`
- `GOVERNANCE_INTAKE_AUTHORIZED`

An authorized intake creates or permits a **separate governed upstream object**. It does not implement the requested change.

## Canon boundary

For canon-facing work:

`Lab packet -> upstream intake decision -> CCR -> canon implementation PR -> governing main`

The Lab packet is not a CCR.

`CCR_INTAKE_AUTHORIZED` means only that upstream may create a CCR record for review. The existing CCR lifecycle remains authoritative. `APPROVED_FOR_IMPLEMENTATION` and `IMPLEMENTED` retain their existing meanings and cannot be supplied by a Lab packet.

Approval changes authority status only. It does not rewrite evidentiary provenance.

## Engineering/runtime/data boundary

`ENGINEERING_INTAKE_AUTHORIZED` and `RUNTIME_DATA_INTAKE_AUTHORIZED` likewise authorize separate governed work items. They do not certify engineering, modify runtime/data, or approve release by themselves.

## Cross-project firewall

Research projects remain epistemically separate.

If multiple Lab projects materially contribute evidence, the packet must identify the governing bridge record. Upstream intake MUST reject or defer any packet that gains evidentiary force merely by juxtaposing RF, AP, FC, reviewer rosters, anomaly recurrence, narrative fit, or canon usefulness.

**Convergence raises priority, not truth.**

## Frozen/preregistered objects

Packets may reference upstream frozen/preregistered objects including PR #19 and PR #16 at their exact governed heads. Intake may not retune, reinterpret, rebase, or mutate those objects to accommodate a desired Lab result.

## Negative and unresolved results

Negative and unresolved results are first-class upstream inputs.

A packet may legitimately request `ARCHIVE_AS_RESEARCH_RECORD` or `NO_UPSTREAM_ACTION`. Lack of promotion is not a failed handoff.

## Provenance rule

Exact source identity must remain auditable from Lab result through upstream disposition. Mirrored, reconstructed, reference-only, recovered, superseded, and unrecovered sources retain their actual provenance class.

Upstream acceptance does not convert a reconstructed or uncertain source into an exact historical artifact.

## Does not establish

This intake contract establishes process only. It establishes no research result, method confirmation, physics confirmation, M1/M2/M3, hidden topology, anomaly ontology, reviewer endorsement, canon change, engineering certification, runtime/data change, or release decision.
