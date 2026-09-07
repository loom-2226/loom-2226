# LOOM 2226 — Canon Change Request Repository Lifecycle

**Status:** DRAFT PENDING GOVERNANCE BASELINE v1.0 MERGE  
**Parent rules:** `governance/current/LOOM_GOVERNANCE_BASELINE_v1.0.md`, `governance/current/LOOM_CHANGE_CONTROL_v1.0.md`

## Purpose

This directory is the durable repository record for material canon-change decisions.

A chat, issue, research result, simulation output, engineering finding, runtime behavior or 3D model may **propose** a canon change. None of those becomes governing canon merely through discussion, repetition, implementation convenience or apparent plausibility.

> **A CCR is the airlock between findings/design intent and governing canon.**

## Identifier format

Canonical IDs use:

`CCR-YYYY-NNNN`

Example:

`CCR-2026-0001`

Sequence numbers are allocated from `CCR_REGISTRY.yml`. IDs are never reused, even when a request is rejected, deferred or superseded.

## Record path

Each material request receives one durable machine-readable record:

`governance/changes/CCR-YYYY-NNNN-short-slug.yml`

The GitHub Canon Change Request issue is the discussion/intake surface. The repository YAML record is the durable decision/promotion record.

## Lifecycle

```text
FINDING / DESIGN INTENT / CONTINUITY ISSUE
                  |
                  v
              PROPOSED
                  |
                  v
            UNDER_REVIEW
             /    |     \
            v     v      v
       REJECTED DEFERRED APPROVED_FOR_IMPLEMENTATION
                           |
                           v
                   CANON IMPLEMENTATION PR
                           |
                           | updates governing file(s)
                           | archives/supersession
                           | authority/baseline manifest
                           | hashes/validation
                           | dependency classifications
                           v
                       IMPLEMENTED
```

A record may later become `SUPERSEDED`, but its history remains.

## Status semantics

### `PROPOSED`

The change exists as a formal request. It is not approved and is not canon.

### `UNDER_REVIEW`

Evidence, derivation status, continuity, authority relationship and downstream impacts are being assessed.

### `APPROVED_FOR_IMPLEMENTATION`

Kevin, as project-intent authority, has approved the proposed canon transition through the governance process.

**This still does not make the proposed content governing canon.**

It authorizes a controlled `class:canon` implementation PR.

### `IMPLEMENTED`

The approved canon implementation has merged into authoritative `main`, and the required authority/baseline/hash/validation updates have been completed.

Only at this point is the CCR's canon transition complete.

### `REJECTED`

The proposal was considered and not accepted. The record remains auditable.

### `DEFERRED`

The proposal cannot yet be decided or implemented. Typical reasons include incomplete research qualification, unresolved engineering closure, missing evidence or sequencing dependencies.

### `SUPERSEDED`

A later CCR replaced the decision or governing transition. The old record remains historical evidence.

## Promotion invariants

A `class:canon` implementation PR must:

1. cite one or more exact CCR IDs;
2. use CCR status `APPROVED_FOR_IMPLEMENTATION` before implementation;
3. identify exact governing files/sections changed;
4. state the authority relationship: replacement, scoped amendment, new governing source or retirement;
5. classify registered downstream dependencies;
6. update the active canon authority/baseline records as required;
7. update file hashes/validation records as required;
8. update compatibility metadata where downstream compatibility is affected;
9. preserve superseded governing material in archive/history;
10. complete required WALTER assurance;
11. change the CCR to `IMPLEMENTED` only after the authoritative implementation actually lands.

## Evidence status is permanent provenance

Every CCR records the origin of the proposed change, for example:

- established external knowledge;
- mathematical/engineering derivation;
- simulation result;
- research result/hypothesis;
- fictional design decision;
- continuity correction;
- mixed provenance.

Approval changes **authority status**. It does not retroactively change **evidentiary status**.

A fictional design decision does not become established physics because it entered canon.

A research result does not become external empirical evidence because Kevin approved its fictional consequence.

## Frozen research rule

A CCR depending on a frozen/preregistered experiment whose verdict is not yet qualified must remain `DEFERRED` or otherwise explicitly non-approved.

The CCR may not be used to pressure, retune or reinterpret the frozen experiment.

## Proposal revision and historical integrity

Before approval, a proposal may be clarified through explicit `proposal_revision` increments and history entries.

Materially different claims should normally receive a successor/new CCR rather than quietly transforming the original request.

Once a decision event is recorded, it is never rewritten to pretend a different decision occurred.

Implementation/disposition updates are additive history.

## Registry

`CCR_REGISTRY.yml` is the machine index.

The registry does not duplicate every proposal detail. It records:

- ID;
- record path;
- status;
- title;
- originating issue/reference;
- approved/implemented PR where applicable;
- supersession relationship.

If the registry and a CCR record disagree, the inconsistency is a governance defect and canon promotion must not rely on whichever version is more convenient.

## WALTER / #LOOMSAFE

WALTER checks the airlock rather than deciding canon.

For a canon implementation PR he should ask:

- Is the cited CCR real and registered?
- Is its status actually `APPROVED_FOR_IMPLEMENTATION`?
- Are the claims being implemented within the approved scope?
- Are downstream pack members classified?
- Are baseline/hash/validation obligations accounted for?
- Is frozen research being treated according to its actual disposition?
- Did a black-box or simulation output silently gain more evidentiary authority than it earned?

A future deterministic hard gate may block canon promotion when the required CCR/baseline machinery is objectively absent. During governance adoption these checks remain advisory.
