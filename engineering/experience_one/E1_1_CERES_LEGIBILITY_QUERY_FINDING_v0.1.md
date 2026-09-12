# LOOM 2226 — E1.1 Ceres Legibility Query Finding v0.1

**Status:** IMPLEMENTATION EVIDENCE PRESENT / PIXEL EMPIRICAL RUN PENDING  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1`  
**Change type:** additive diagnostic only; no production authority change

## Question

Using the already-qualified disposable 2226 Ceres operator fixture and the already-qualified current-place handoff, can the existing deterministic Canon Context query layer produce grounded answer packets for the two smallest Experience One world-texture questions:

- **What is this place?**
- **What is interesting here?**

without invoking Mara, broadening Canon Context to Mars, creating a generalized Experience Context merger, or changing any state/canon authority?

## Governing boundary

This increment does not mutate `src/**` runtime behavior. It only adds a diagnostic harness and tests over existing contracts:

1. `LOOM_STATE_V1` disposable Ceres acceptance fixture;
2. `LOOM_CAMPAIGN_OPERATOR_CONTEXT_V1`;
3. `LOOM_CURRENT_PLACE_HANDOFF_V1`;
4. `LOOM_CANON_CONTEXT_PROJECTION_V1`;
5. `LOOM_CANON_CONTEXT_QUERY_V1`.

Navigator remains location/state authority. Canon Context remains read-only world/canon projection authority. Query selection is deterministic presentation-derived non-authority. Model calculation/state/canon authority remains ZERO.

## Diagnostic harness

`engineering/experience_one/spikes/e1_1_ceres_legibility_query.py`

The harness:

- loads the disposable 2226 Ceres operator fixture;
- projects operator location from Navigator-format state;
- requires the fail-closed current-place handoff to return `AVAILABLE`;
- issues deterministic `ORIENT` and `INTERESTING` queries;
- repeats both queries and requires byte-structural equality of the resulting Python objects for fixed inputs;
- verifies grounded entity/name/role/traffic fields and selection-input provenance;
- verifies model authority remains zero;
- emits the full query packets for human inspection.

It does **not** claim that structural correctness proves Ceres is interesting. That remains an empirical product/legibility judgment after the actual Pixel data is inspected.

## Unit regression

`tests/test_e1_1_ceres_legibility_query.py`

Covers:

1. aligned Ceres positive control returns grounded orientation and interesting places;
2. temporal mismatch blocks before querying;
3. unsupported location blocks before querying;
4. fixed inputs reproduce exactly;
5. no model authority is introduced and sources remain unmerged.

## Pixel discriminator

Target runtime root:

`/storage/emulated/0/Download/LOOM_TEST`

Expected state fixture:

`engineering/experience_one/fixtures/E1_1_CERES_OPERATOR_STATE_2226.json`

Expected output:

`/storage/emulated/0/Download/E1_1_CERES_LEGIBILITY_QUERY_RESULT.json`

Pass requires:

- handoff `AVAILABLE`;
- Ceres entity context;
- non-empty Ceres identity and summary;
- at least two supported ORIENT facts;
- at least one unique grounded INTERESTING item;
- deterministic repeated query packets;
- zero model authority;
- no source merge.

## Interpretation rule

A structural PASS means only:

> Existing governed Ceres data can be deterministically projected into compact grounded packets for orientation and interesting-place discovery.

It does **not** mean:

- the prose is good;
- the world feels alive;
- the selected places are genuinely compelling to a new player;
- Mara should be reintroduced yet;
- the query layer should be generalized;
- new canon is unnecessary forever.

After the Pixel run, inspect the actual returned summary, political/transport context and ranked places before classifying the remaining defect as DATA, PROJECTION, SYNTHESIS, PRESENTATION or MOTIVATION.

## Falsifier

Reclassify if the live Ceres databases cannot produce the required packets, if the packets lack grounded provenance or meaningful fields, if fixed inputs do not reproduce, if unsupported/temporal refusal can be bypassed, or if any model/state/canon authority appears in the path.
