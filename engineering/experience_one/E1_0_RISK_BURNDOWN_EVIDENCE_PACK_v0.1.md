# LOOM 2226 — Experience One E1.0 Risk Burn-Down Evidence Pack v0.1

**Status:** ACTIVE BOUNDED ENABLER — EVIDENCE CAPTURE / SPIKE EXECUTION  
**Date:** 12 September 2026  
**Primary change class:** `class:engineering`  
**Scope:** `REQUIRED_FOR_E1` bounded enabling work; this is not a fifth standing WIP stream  
**Parent workplans:** `governance/current/LOOM_EXPERIENCE_ONE_PRODUCT_CONVERGENCE_WORKPLAN_v1.0.md` plus scoped v1.1 update  
**Branch base:** protected `main` at `65b1b1559eac8dfe0ed6be24739ba9ac32f83f3c`  
**Product target:** Experience One — A Day Aboard Wayfarer  
**Qualification scenario:** Ceres → Neptune  
**Canon effect:** none

## 0. Purpose

Execute E1.0 before E1.1 production work. This pack records baseline evidence, Spike A/B/C exits and the eventual GO / REPLAN decision. A spike may remove uncertainty; it may not silently become production architecture.

## 1. Current gate/activity state

| Gate/activity | State | Evidence maturity | Current statement |
|---|---|---|---|
| G0 target freeze | `IN_PROGRESS` | `IMPLEMENTATION_EVIDENCE_PRESENT` | Branch remains bounded to governed E1.0 objectives. |
| G1 baseline fixture | `IN_PROGRESS` | `IMPLEMENTATION_EVIDENCE_PRESENT` | Source surfaces inventoried; remaining device/baseline capture must be closed deliberately. |
| G2 consume authority | `IN_PROGRESS` | `IMPLEMENTATION_EVIDENCE_PRESENT` | Existing engineering/Navigator authority is consumed; no E1 replacement authority asserted. |
| Spike A | `PASS` | `EMPIRICALLY_TESTED` | Pixel Ceres→Neptune run returned 24 deterministic valid candidates, reproducible fingerprint, independent validation and no campaign mutation. Exit classification: `BOUNDED_EXTENSION`. |
| Spike B | `IN_PROGRESS` | `IMPLEMENTATION_EVIDENCE_PRESENT` | Source trace now suggests local qualification execution and interplanetary campaign execution may correctly be separate authority scopes. Disposable-state empirical continuity test required before classification. |
| Spike C | `IN_PROGRESS` | `IMPLEMENTATION_EVIDENCE_PRESENT` | Typed LLM provenance socket exists; actual model/tool runtime remains unverified. |
| E1.0 GO/REPLAN | `NOT_STARTED` | `DOCUMENTED_ONLY` | Must wait for baseline + B/C exits. |

Spike A PASS is limited to the spike's falsifiable exit criteria. No Experience One product gate is thereby passed.

## 2. Baseline evidence

PR #99's local maneuver path is explicitly qualification-only (`campaign_mutation=False`, `navigation_grade=False`). Preserved Navigator assigns Python authoritative state, quantitative reconciliation, ephemeris, flight calculations, operational choices, commit/execution, history and handoff. Persistent campaign artifacts include state, backup and compressed history. Replay requires both `FLIGHT_COMMITTED` and `FLIGHT_ARRIVED`.

This evidence does not justify joining the two paths. Their scopes must be tested before any adapter is designed.

## 3. Spike A — CLOSED

Direct Pixel evidence established:

- `OFFLINE_CACHE_ONLY` acquisition on the restart run;
- 24 valid Ceres→Neptune candidates;
- identical candidate-set fingerprint across identical rerun (`c3d06c...c049`);
- materially distinct metric/torch combinations;
- independent deterministic validation PASS for the exercised subset;
- bit-identical before/after hashes for state, backup and campaign history;
- agreement with the prior online-enabled run on candidate count and candidate-set fingerprint.

**Exit classification:** `BOUNDED_EXTENSION — EMPIRICALLY_TESTED`.

**Falsifier:** reopen if pinned rerun loses reproducibility, yields fewer than two materially distinct valid candidates, validation diverges, read-only enumeration mutates campaign artifacts, or production exposure requires foundational solver/authority change.

Detailed record: `E1_0_SPIKE_A_SOURCE_FINDING_v0.1.md`.

## 4. Spike B — execution continuity

### Revised source hypothesis

The earlier seam framing may be wrong. PR #99's local maneuver executor is deliberately qualification-only. Preserved Navigator already contains its own interplanetary campaign authority path: ranked candidate selection, explicit `COMMIT FLIGHT? [y/N]`, deterministic revalidation, `FLIGHT_COMMITTED`, arrival-state construction, `FLIGHT_ARRIVED`, atomic persistence, and replay semantics.

Do **not** force the PR #99 qualification executor to become the interplanetary campaign executor merely to create one apparent path.

### Required direct experiment

Using disposable campaign state only:

1. preserve hashes of the user's real campaign artifacts;
2. create a disposable copy of campaign state/history while reusing read-only B1/cache inputs;
3. exercise the existing interplanetary campaign path, including explicit authorization and deterministic revalidation;
4. verify `FLIGHT_COMMITTED` and `FLIGHT_ARRIVED` in disposable history;
5. reload/restart from disposable persisted state;
6. verify location, epoch, resources and journey provenance;
7. replay the flight using the existing replay path;
8. prove the user's real campaign hashes remain unchanged;
9. classify `BOUNDED_ADAPTER`, `MODERATE_INTEGRATION`, `FOUNDATIONAL_AUTHORITY_RECONCILIATION`, or `INCOMPATIBLE_PATHS_REQUIRING_REDESIGN` from observed evidence.

No duplicate campaign mutation logic may be implemented in the spike.

### Current hypothesis

`BOUNDED_ADAPTER — INFERRED / REQUIRES_EMPIRICAL_TEST`.

Falsifiers include inability to isolate the real campaign, failed deterministic revalidation, missing committed/arrived records, restart state divergence, replay failure, or discovery that E1 must reconcile contradictory authoritative state models.

## 5. Spike C — minimum Mara/model/tool plumbing

Required pipeline remains USER → MODEL → ONE READ-ONLY TYPED TOOL CALL → DETERMINISTIC LOOM RESPONSE → MODEL GROUNDED RESPONSE. No write tool, direct SQLite mutation, trajectory calculation by model, campaign mutation or hidden authoritative state in model context. Hostile cases and provider/data/cost/lock-in review remain required.

## 6. GO / REPLAN

Current state: `NOT_STARTED / DOCUMENTED_ONLY`. Do not fill until baseline and Spike B/C exit evidence exist.

## 7. WALTER / #LOOMSAFE

Active watches: documentation-as-progress; duplicate flight/campaign authority; spike promotion; model authority creep; PASS without falsifier; vendor/data/cost/lock-in and prompt-injection risk for Spike C.

## 8. Next action

Build the smallest disposable-state Spike B harness around the **existing** Navigator campaign path. It must fail closed before touching real campaign state, prove restart/replay continuity, and leave the user's real campaign bit-identical.