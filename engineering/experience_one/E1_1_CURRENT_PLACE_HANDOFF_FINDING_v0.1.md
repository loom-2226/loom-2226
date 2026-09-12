# LOOM 2226 — E1.1 Current-Place Handoff Finding v0.1

**Status:** IMPLEMENTED / EMPIRICAL PIXEL RETEST PENDING  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1`  
**Diagnosis:** `PROJECTION_HANDOFF_DISCRIMINATOR`

## Question

Can Experience One hand off an authoritative Navigator current-location token to Canon Context without:

- inventing context for an unsupported place;
- silently combining a 2027 qualification state with 2226 canon;
- merging campaign and canon authority;
- allowing a caller/Mara layer to smooth a refusal into plausible prose?

## Governing decision

Until a separate temporal policy is governed, current-place Canon Context must **fail closed** across a campaign/canon year mismatch. A label such as "reference canon" is not sufficient to waive the firewall.

This follows the same authority pattern already preserved by the Earth-Luna work: epoch/frame boundaries are not relaxed merely for presentation convenience.

## Runtime change declaration

Change class: **additive read-only bounded adapter**.

Downstream compatibility impact: **none intended**. The change introduces no replacement UI, no Navigator state mutation, no WORLD/CIVSTATE mutation, no new campaign persistence, no browser authority, no model authority, and no generalized Experience Context merger.

Dependencies:

- `LOOM_CAMPAIGN_OPERATOR_CONTEXT_V1` for authoritative current location/epoch projection;
- existing `LOOM_CANON_CONTEXT_PROJECTION_V1` builder for read-only canon projection;
- existing WORLD/CIVSTATE SQLite files opened by the Canon Context layer in read-only mode;
- no launcher/release/schema migration dependency.

## New bounded handoff

`src/loom_current_place_handoff.py` exposes:

`LOOM_CURRENT_PLACE_HANDOFF_V1`

The result keeps the two sources separately labelled and uses explicit statuses:

- `UNSUPPORTED_ENTITY`
- `TEMPORAL_SCOPE_UNKNOWN`
- `TEMPORAL_MISMATCH`
- `AVAILABLE`

On every non-`AVAILABLE` result, `canon_context` is `null` and the adapter emits a deterministic human-boundary refusal message. This prevents a higher caller from accidentally receiving rejected canon facts and narrating over the refusal.

The adapter derives the campaign year from the Navigator epoch. It derives the Canon Context reference year from evidenced `year` values in the returned projection rather than hard-coding downstream field paths. Multiple canon years are treated as ambiguous and fail closed.

## Three-case discriminator

The Pixel harness `engineering/experience_one/spikes/e1_1_current_place_handoff.py` preregisters three cases:

1. **Live location honest miss**  
   Input: actual active Navigator state. Current observed location is `MARS`.  
   Expected: `UNSUPPORTED_ENTITY`.  
   Required human-boundary behavior: explicit unavailability; no canon payload.

2. **Ceres 2027 temporal firewall**  
   Input: disposable non-authoritative Ceres acceptance fixture shifted to 2027.  
   Expected: `TEMPORAL_MISMATCH`.  
   Required behavior: no 2226 Canon Context payload is exposed.

3. **Ceres 2226 positive control**  
   Input: disposable non-authoritative Ceres acceptance fixture at 2226.  
   Expected: `AVAILABLE`.  
   Required behavior: Ceres Canon Context is returned while Navigator remains sole location authority and sources remain unmerged.

## Disposable acceptance fixture

`engineering/experience_one/fixtures/E1_1_CERES_OPERATOR_STATE_2226.json`

is explicitly:

- non-authoritative;
- acceptance-scoped;
- not a replacement for the active campaign state;
- not evidence that the live campaign moved to Ceres;
- not canon;
- prohibited from mutating campaign or canon state.

Its purpose is to preserve the preregistered Experience One Ceres test location without rewriting the actual live Mars campaign by convenience.

## Unit coverage

`tests/test_loom_current_place_handoff.py` covers:

- honest unsupported-Mars handling through the human-facing boundary;
- 2027/2226 temporal mismatch hard failure;
- positive Ceres/2226 control;
- rejected canon payload suppression;
- input immutability;
- fail-closed behavior if model state authority is not ZERO.

## Pass statement

This finding is **not yet PASS**. Implementation exists, but the Pixel functional discriminator has not yet been run against the actual live state plus actual WORLD/CIVSTATE databases.

A PASS requires:

- all unit tests pass on Pixel;
- all three harness cases return their preregistered status;
- unsupported and temporal-mismatch cases expose no canon payload;
- deterministic human-boundary messages remain explicit refusals;
- no live campaign or canon mutation occurs.

## Falsifier

Replan/fail if an unsupported location yields plausible canon prose, a temporal mismatch exposes canon facts, the handoff silently changes location authority, source labels are merged, model/browser authority becomes non-zero, or the positive Ceres/2226 control cannot consume the existing Canon Context projection without broadening its scope.
