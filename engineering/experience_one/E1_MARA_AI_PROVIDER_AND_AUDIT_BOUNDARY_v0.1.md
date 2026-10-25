# LOOM 2226 — Experience One Mara Provider + Audit Boundary v0.1

**Date:** 2026-09-13  
**Class:** `class:engineering`  
**Status:** ACTIVE E1 ENGINEERING BOUNDARY  
**Related future requirements:** PR #113 — Local Intelligence Runtime functional requirements

## Decision

Experience One uses Mara as a natural-language interpretation and explanation layer in front of deterministic LOOM services. OpenAI may be used during E1 development and qualification, but every OpenAI-backed Mara call used as development/qualification evidence must be audited. No model/provider receives calculation authority, state authority, final authorization authority, or governing-data mutation authority.

The E1 Mara/provider seam must remain replaceable so the same bounded tasks can later be routed to a qualified Pixel-local model under PR #113. PR #113 is a portability target and future runtime work package, not an E1 blocker.

## Authority path

```text
USER
  -> MARA / LANGUAGE INTERPRETATION (non-authoritative)
  -> TYPED E1 REQUEST
  -> DETERMINISTIC LOOM / NAVIGATOR
  -> REVIEWABLE DETERMINISTIC OPTIONS
  -> HUMAN EXPLICIT AUTHORIZATION
  -> NAVIGATOR CAMPAIGN EXECUTION
  -> PERSISTED CAMPAIGN STATE / HISTORY
```

Mara may interpret, request, summarize, compare and explain. Mara may not move Wayfarer.

## Mandatory audit rule

Every OpenAI API call made for Mara/E1 development or qualification must pass through the existing append-only development audit mechanism or its governed successor.

Current earned mechanism:

`engineering/experience_one/spikes/openai_dev_audit.py`

Current E1 development audit target:

`/storage/emulated/0/Download/LOOM_OPENAI_DEV_AUDIT.jsonl`

The raw audit is local development evidence and is not a normal repository artifact. The audit mechanism must preserve correlation, stage/task identity, request/response or error, status, latency, provider/model metadata, usage where available, validation outcome where applicable, provenance supplied to Mara where applicable, and the existing hash-chain linkage.

As a provider-neutral interface is introduced, audit metadata should also capture task class, caller/component, routing reason, local-provider eligibility, hosted-selection reason, hosted cost where available, and provider fallback/escalation reason. This aligns E1 instrumentation with PR #113 without pulling local-model implementation onto the E1 critical path.

## Provider-neutral E1 constraint

Feature code must not depend on a specific hosted model identity or provider-specific response structure beyond a bounded provider adapter.

The implementation must converge on a typed Mara request/result boundary carrying at least: task type, user input, grounded context/provenance, allowed tools, required output shape, authority constraints, provider/model used, validation state, tool requests, provenance references, and audit correlation identity.

Exact runtime schema names remain to be earned in implementation/tests.

## Tool boundary

Mara/provider may request only explicitly exposed and schema-validated read/planning services needed for E1, including current campaign context, grounded Ceres/Neptune context, named target lookup, deterministic Navigator planning, deterministic plan comparison inputs, and current plan/state validity.

The model/provider does not receive unrestricted database, filesystem, shell, repository, campaign-mutation, or trajectory-calculation authority.

Model-originated and human-originated requests converge on the same deterministic LOOM services. Origin is provenance, not authority.

## Explicit authorization firewall

No model/provider may perform final flight authorization. Mara may explain a selected plan and ask whether to proceed. Execution requires explicit human authorization tied to the currently validated deterministic plan/state. Stale or changed state fails closed.

## E1 sequencing

1. Preserve the empirically passed PR #112 Ceres -> Neptune campaign-flight proof.
2. Reconcile the E1 campaign/epoch onto the governed 2226 temporal path.
3. Port/re-earn the minimum typed request/review/authorization seam from qualified HUD work onto current-main lineage.
4. Introduce Mara/OpenAI through the audited provider-neutral adapter at that typed request boundary.
5. Bind that interaction path to Navigator's existing planning and campaign authority, never to a second executor.
6. Present the same path through the global/system HUD consumer.
7. Qualify minimal Neptune arrival orientation.
8. Execute the Pixel zero-instruction Experience One run.

OpenAI is introduced before final HUD qualification so the product is not designed around manual-only interaction. It is introduced only after the typed authority boundary exists so provider behavior cannot define that boundary by accident.

## Local Pixel LLM transition

PR #113 defines the future Local Intelligence Runtime requirements. E1 should support that future transition now by keeping provider selection outside feature logic, tool contracts deterministic/provider-neutral, authoritative state external to model weights, audit/provenance independent of provider, structured-output validation independent of provider, and no assumption that network access is always available.

No Pixel-local model/runtime is selected or qualified by this E1 document. A local model may replace hosted inference for a task class only after provider-neutral benchmark evidence qualifies it for that task class.

## WALTER hard fails

FAIL / REPLAN if E1 introduces unaudited model calls used as qualification evidence, model-generated authoritative coordinates/trajectory/remass/epoch values, model-selected final flight authorization, direct model writes to governing state, a second model-specific flight executor, hidden provider coupling in Navigator/HUD feature logic, or local-model implementation on the E1 critical path merely because PR #113 exists.

## Working rule

> **Audit every model call. Keep every model replaceable. Let deterministic LOOM move the universe.**
