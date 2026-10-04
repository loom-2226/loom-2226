# Phase 3B Kernel Validation Record 004 — Accounting Hardening

**Status:** PASS FOR BUILD-4 AUTHORIZED DETERMINISTIC/GENERATIVE SLICE / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Branch:** `offworld-mvp-phase3`

## Purpose

Stress accounting identities before adding further behavioral machinery. Build 4 targets nonzero depreciation, multi-period WIP, held project cash, carried reservations, many-to-many finance, ownership-preserving disposition, local supply bounds, signed Earth boundary positions, event-log replay identity and seeded generative invariant checks.

## Validation result

Executed on `quantifactus` from a fresh Git archive of `origin/offworld-mvp-phase3`.

`python3 -m unittest discover -s tests -v`

**26 tests executed; 26 passed.**

The nine Build-4 tests cover:

1. accounting hard cases;
2. two-financier syndication, competing ceiling demand and commitment lapse;
3. per-owner claim conservation across different domiciles;
4. signed Earth-boundary position plus resource consumption;
5. local offworld supply-capacity bound;
6. seeded state-aware valid transition sequences with invariants after every transition;
7. explicitly invalid transition atomicity;
8. event-log sensitivity of the replay fingerprint;
9. keyed-draw deterministic uniformity smoke test.

## Hard-case results

A 60-unit disbursement is held as project cash across a year boundary before expenditure. Construction then receives two 25-unit WIP additions and is commissioned at 50. A 10% depreciation step reduces productive book capital from 50 to 45.

A 10-unit knowledge asset receives 20% amortization, reducing its book value to 8.

A 40-unit reservation created in year 1 survives into year 2. Fifteen is spent in year 2 and the remaining 25 lapses in year 3. The identity `amount = spent + lapsed + outstanding` holds at validation.

## Defect discovered by the hard case

The pre-Build-4 kernel invariant incorrectly required every `FixedCapitalFormationEvent.asset_id` to be globally unique. That rule made legitimate multi-period WIP impossible: two annual formation additions to the same construction target were interpreted as asset cloning.

The invariant was repaired. Repeated FCF additions may now target the same WIP/construction identity, while the same target appearing at different asset nodes remains prohibited. This is exactly the sort of defect the hard-case run was intended to expose.

## Many-to-many

P1 receives 30 from each of two financiers domiciled at different Earth nodes. Project cash is 60.

Two projects then compete against a synthetic 100-unit Earth resource-allocation ceiling. A 70-unit reservation succeeds; a competing 40-unit request is blocked.

A separate 50-unit commitment lapses by 20, leaving 30 outstanding. Commitment reconciliation remains exact.

This establishes the many-to-many state mechanics and competition/lapse paths. It does not establish autonomous underwriting or allocation policy.

## Ownership-preserving local vehicle

A local financing vehicle receives contributions of 60 and 40 from owners domiciled at `EARTH:X` and `EARTH:Y`. Explicit beneficial stakes are therefore 0.6 and 0.4.

A later 50-unit distribution returns 30 and 20 to those owners respectively. The vehicle retains 50. Ownership shares remain exactly 1.0.

Thus local retention/reinvestment no longer requires value to lose its beneficial owner merely because it crosses into a local financing vehicle.

## Earth boundary and resource inventory

The Earth market boundary begins at zero and is explicitly permitted to carry a signed net position. A 100-unit purchase creates boundary net position -100 rather than relying on a prefunded market wallet.

Five resource units arrive at the Earth boundary. A subsequent Earth-side consumption event consumes two, leaving three in boundary inventory. The resource therefore remains explicit until consumed rather than accumulating invisibly or disappearing on purchase.

The boundary account is an MVP clearing abstraction, not a modeled bank deposit or household/firm balance sheet.

## Local supply M2

Offworld supplier capacity is explicitly recorded. A 50-unit capacity permits 50 units of local WIP supply and rejects an additional 0.01. Build 2's unconstrained local 40-unit supply path is therefore no longer the only tested local-supply behavior.

## Knowledge asset

The success path now includes explicit knowledge-asset amortization. The accounting rule is mechanical and parameterized; the 20% fixture rate is authored validation data, not an empirical estimate.

## Observation likelihood clarification

Build 3 does **not** use the world's false-positive/false-negative parameters as the agent's likelihood model. Those parameters govern WORLD_SIM observation generation only. Agent belief updates remain a deliberately crude fixed +/-0.30 heuristic after the observed signal. Agents therefore are not perfectly informed of the world's sensor-error model.

A later belief-model design must explicitly represent what sensor calibration/likelihood information each agent knows.

## Generative invariant test

A seeded generator performs 250 state-aware valid transitions, including ordinary transfers plus commitment disbursement/lapse choices, and calls the Build-4 invariant suite after every transition. Total modeled non-boundary cash is conserved throughout.

Invalid actions are tested separately rather than generated and discarded. An attempted transfer from an empty account raises before mutation, and the state fingerprint is unchanged.

This is a useful property-style stress test, but it is not yet exhaustive generation over every transition type in the kernel.

## Replay fingerprint and keyed draws

Build-4 fingerprint includes the prior Build-3 manifest plus ordered Build-4 event log, ownership stakes/domiciles, WIP, supply-capacity state, carried reservations, signed boundary positions, depreciation and knowledge-amortization state.

Changing only the event log changes the fingerprint.

For 10,000 deterministic keyed draws:

- mean: 0.5030652442171557
- minimum: 0.0000012166190595382879
- maximum: 0.9999060109860871

This is a deterministic uniformity smoke test, not statistical certification of a random-number generator.

Reference Build-4 empty-fixture fingerprint: `15e3cf559443d8164bfd38c36731de234b327013dfc64ad66639c2350fe82e56`.

## Remaining boundary

Build 4 still does not authorize or establish autonomous policy behavior. The generative test covers a subset of valid transition families, not all A1-A9-relevant transitions. Transport, technology gating, dynamic reserve conversion, colony operations and governed Earth-reference ingestion remain open. Full agent-engine implementation remains gated.
