# LOOM 2226 — E1.1 Campaign Operator Context Finding v0.1

**Status:** PASS / EMPIRICALLY_TESTED  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1`  
**Diagnosis:** `PROJECTION_BOUNDARY_READY`, not data failure

## Question

Can Experience One answer the preregistered operator question **"Where am I?"** from existing authoritative campaign state without allowing Canon Context, the browser, or Mara to become ship-location authority?

## Result

**PASS / EMPIRICALLY_TESTED.**

The bounded adapter and Pixel harness both passed against the active campaign state. The current ship location is directly available from Navigator-owned `LOOM_STATE_V1.location_token`; no inference from flight history, Canon Context, UI selection, browser state, or model reasoning is required.

## Runtime change declaration

Change class: **additive read-only projection / bounded adapter**.

Downstream compatibility impact: **none intended**. No Navigator state schema, mutation path, physics, browser behavior, launcher, release path, or Pixel/Windows behavior is replaced. The new adapter consumes an already-loaded `LOOM_STATE_V1` object and emits a compact read-only projection.

Dependencies:

- schema authority: existing Navigator `LOOM_STATE_V1`;
- source authority: Navigator campaign state;
- required source fields: `location_token`, `epoch_utc`, `kinematic_boundary.status`, `ship_identity`, `state_id`, `state_sha256`;
- no WORLD/CIVSTATE/Atlas dependency;
- no model dependency;
- no new persistence dependency.

## Empirical Pixel evidence — source shape

The read-only campaign-state probe was run against the active Pixel state file:

`/storage/emulated/0/Download/LOOM_TEST/LOOM_STATE_V1.json`

Observed source file SHA-256:

`4d89892fa9feed7a8f59e4cb10d4ee27df1b27268bfe2e68c19d70585697e48c`

Relevant observed fields:

- Navigator schema: `LOOM_STATE_V1`;
- `$.location_token = 'MARS'`;
- `$.epoch_utc = '2027-06-15T08:57:51.391985Z'`;
- `$.kinematic_boundary.status = 'BODY_RENDEZVOUS'`;
- `$.kinematic_boundary.source = 'PYTHON_NAV_V1_A_TERMINAL_BOUNDARY'`;
- `$.ship_identity.ship_name = 'wayfarer'`;
- `$.ship_identity.ship_class = 'WAYFARER'`;
- `$.ship_identity.ship_instance_id = 'SHIP-444BFD9B8294'`;
- `$.state_id = 'S000008-1f8140b205a7'`;
- embedded `$.state_sha256 = '1f8140b205a7139be2cbf983a17b4b83c1c35e4b32a18a767c945c49b1843fdc'`;
- last flight route was `CERES>MARS`, with arrival epoch equal to current campaign epoch.

The state itself therefore already contains a direct current-location token and current kinematic boundary. No inference from Ceres/Neptune canon, UI selection, last-flight route text, or model reasoning is required.

## Authority interpretation

For the E1.1 operator question **"Where am I?"**:

- current ship/location authority is `LOOM_STATE_V1.location_token` owned by Navigator;
- current epoch authority is `LOOM_STATE_V1.epoch_utc`;
- current boundary/status context is `LOOM_STATE_V1.kinematic_boundary`;
- `last_flight.route` is historical support only and must never override current `location_token`;
- Canon Context may describe Mars/Ceres/Neptune after a location is established, but it may not establish ship location;
- Mara may explain the projected state but has ZERO state/calculation/canon authority.

## Bounded adapter

Added `src/loom_campaign_operator_context.py` with schema:

`LOOM_CAMPAIGN_OPERATOR_CONTEXT_V1`

The adapter:

- accepts an already-loaded `LOOM_STATE_V1` mapping;
- fails closed on wrong schema or missing required location/epoch/kinematic/identity evidence;
- projects ship identity, current location, epoch, kinematic status/source, and campaign-state identifiers;
- provides exact provenance back to Navigator JSON paths;
- explicitly states `location_authority = NAVIGATOR_LOCATION_TOKEN`;
- explicitly states model calculation/state/canon authority = ZERO;
- explicitly states `world_context_merged = false`;
- does not infer current location from `last_flight.route`;
- does not mutate the input state.

## Unit regression evidence

Pixel direct-import regression:

- `PASS: test_does_not_infer_current_location_from_last_flight_route`
- `PASS: test_input_state_is_not_mutated`
- `PASS: test_missing_kinematic_status_fails_closed`
- `PASS: test_missing_location_fails_closed`
- `PASS: test_preserves_navigator_authority_and_zero_model_authority`
- `PASS: test_projects_current_location_from_location_token`
- `PASS: test_provenance_points_to_exact_campaign_fields`
- `PASS: test_schema_mismatch_fails_closed`

**ALL 8 TESTS PASS.**

## Empirical Pixel execution

Harness:

`engineering/experience_one/spikes/e1_1_operator_location_query.py`

Input:

`/storage/emulated/0/Download/LOOM_TEST/LOOM_STATE_V1.json`

Observed result:

- result schema: `LOOM_E1_1_OPERATOR_LOCATION_RESULT_V1`;
- ship: `wayfarer`;
- location token: `MARS`;
- epoch UTC: `2027-06-15T08:57:51.391985Z`;
- kinematic status: `BODY_RENDEZVOUS`;
- `all_pass: True`.

Output artifact:

`/storage/emulated/0/Download/E1_1_OPERATOR_LOCATION_RESULT.json`

This empirically qualifies the read-only operator-location projection on the Pixel runtime target.

## Qualified answer packet

For the tested state, the deterministic answer packet is:

- ship: `wayfarer`;
- location: `MARS`;
- kinematic state: `BODY_RENDEZVOUS`;
- epoch: `2027-06-15T08:57:51.391985Z`.

Human-facing phrasing is presentation, not state authority. A safe rendering is: **Wayfarer is at Mars, in a body-rendezvous state, at the current campaign epoch.**

## Limits

This finding qualifies only the bounded current-location projection. It does not:

- make Canon Context a campaign-state source;
- qualify a generalized Experience Context merger;
- qualify Mara natural-language synthesis over campaign state;
- establish place description, nearby-interest, destination-interest, or route-planning behavior;
- close all E1.1 acceptance criteria;
- change Navigator state authority.

## Next seam

The next E1.1 seam should compose **separately labeled read-only sources** at the question boundary rather than merge authorities:

1. `Where am I?` → Navigator campaign operator context.
2. `What is this place / what is interesting here?` → Canon Context Projection keyed from the established Navigator location.
3. `What is at the destination / why might I care?` → destination Canon Context, still separate from campaign location authority.

A generalized Experience Context abstraction is not yet earned. First test the smallest current-place handoff from `location_token` to Canon Context and fail closed when the current location has no supported projection.

## Falsifier

Reopen/reclassify if the active campaign state lacks a stable current `location_token`, if current location requires inference from route/history instead of direct state, if the adapter mutates campaign state, if world/canon context becomes required to know ship location, or if any model/browser component is allowed to override Navigator location authority.
