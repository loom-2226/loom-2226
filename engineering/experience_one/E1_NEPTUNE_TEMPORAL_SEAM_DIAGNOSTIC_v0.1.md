# LOOM 2226 — Experience One Temporal Seam Diagnostic v0.1

**Date:** 2026-09-13  
**Class:** `class:engineering`  
**Status:** DIAGNOSIS + BOUNDED QUALIFICATION SUPPORT; NO 2226 PASS YET

## Finding

The successful Pixel Ceres → Neptune qualification on PR #112 used Navigator's existing fresh-campaign constructor. That constructor currently hard-codes the fresh campaign epoch to `2027-06-15T02:00:00Z` while correctly starting at `CERES / READY_HOLD`.

This is a real Experience One temporal seam. It is not a HUD-only presentation defect and it must not be hidden by relabeling a 2027 calculation as 2226.

## Authority diagnosis

The current authoritative campaign location/epoch remains the Navigator campaign JSON/history path. The defect is therefore classified primarily as **MECHANICS / CAMPAIGN-INTEGRATION**, not DATA, projection, presentation, or motivation.

The current E1 branch must not create:

- a second campaign clock;
- a second ephemeris authority;
- browser-owned time;
- LLM-authored epoch values;
- a second campaign-state model.

## Existing prior engineering evidence

An older HUD/convergence qualification lineage already contains two relevant patterns:

1. a typed campaign-clock adapter over canonical JSON/history rather than a replacement clock;
2. a controlled campaign epoch-rebase utility that shifts canonical state/history timestamps while rebuilding hashes and preserving relative durations.

That prior work is useful design evidence but is not silently promoted here. Its Stage-B record explicitly said Pixel physical qualification was still pending, and the branch is not current-main lineage.

## Current-main/canon constraint

Current governing canon registers `EPH-HORIZONS-2226-08-22` as earned ephemeris provenance for covered bodies/times and explicitly says that evidence does **not** generalize to all epochs/targets.

Therefore E1 must not simply choose an arbitrary 2226 timestamp and assume equivalent ephemeris authority.

## Bounded change in this increment

The disposable E1 Ceres seed now supports an optional explicit UTC qualification epoch.

The implementation:

- still creates the seed through Navigator `_new_state(...)`;
- changes only the disposable qualification state's `epoch_utc` before any campaign history exists;
- re-stamps that state through Navigator `_stamp_state(...)`;
- re-validates it through Navigator `_validate_state(...)`;
- records whether the epoch came from the Navigator default or explicit qualification input;
- never mutates the live campaign;
- leaves default behavior unchanged when no `--epoch` is supplied.

The Pixel runner forwards the optional `--epoch` value to the seed. No production campaign constructor is changed by this increment.

## Why this is the minimum safe next step

Changing `_new_state(...)` globally before proving an earned 2226 epoch would alter every fresh Navigator campaign and could contaminate unrelated qualification fixtures. Importing the old rebase tool wholesale would promote stale branch machinery before requalification.

The new explicit qualification input lets us test the real existing Navigator flight path at an earned 2226 date while preserving the authority boundary and exposing any ephemeris/cache incompatibility honestly.

## Next empirical gate

Run the same disposable Ceres → Neptune qualification on the Pixel with an explicit 2226 UTC epoch supported by current ephemeris provenance.

Initial bounded probe date: `2226-08-22` because that is the date named by the current governing ephemeris registry. The exact timestamp must be chosen/tested against actual available cache/provenance; the date label alone is not proof that every timestamp is covered.

PASS requires, at the explicit 2226 epoch:

- deterministic Neptune candidates are produced by the existing Navigator path;
- explicit authorization is still required;
- `FLIGHT_COMMITTED` and `FLIGHT_ARRIVED` occur;
- authoritative restart location is `NEPTUNE_SYSTEM`;
- replay passes;
- live campaign hashes remain unchanged;
- no new clock/ephemeris/state authority is introduced.

If ephemeris resolution fails, that is useful evidence. Diagnose the missing coverage/resolver layer rather than falling back silently to 2027.

## PASS status

`TEMPORAL_SEAM = IN_PROGRESS / IMPLEMENTATION_EVIDENCE_PRESENT / EMPIRICAL_2226_TEST_PENDING`

The earlier Pixel flight/state/persistence PASS remains valid for the bounded 2027 qualification configuration. It is not upgraded to a 2226 Experience One PASS by this document.

## Falsifier

This approach is invalidated if the explicit seed epoch bypasses Navigator state hashing/validation, causes hidden live-campaign mutation, relies on browser/model time authority, silently fabricates ephemerides, or production integration later requires a separate campaign clock rather than the canonical campaign-state authority.
