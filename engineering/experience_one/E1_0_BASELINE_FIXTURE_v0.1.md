# LOOM 2226 — Experience One E1.0 Baseline Fixture v0.1

**Status:** BASELINE INDEX / CAPTURE PLAN — G1 IN PROGRESS  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1` bounded enabling evidence  
**Purpose:** identify and protect the current Experience One regression frontier; not canon authority and not, by itself, completed baseline capture.

## Governing rule

`G1 — No replacement without a fixture.`

This document is an index of the current source/output frontier and a protection rule. It does **not** convert prose descriptions or PR references into regression captures.

A behavior not concretely captured is not authorized for replacement. Before any E1 change replaces a current behavior, capture an inspectable regression reference appropriate to that behavior: screenshot/video where visual behavior matters, deterministic fixture/test where that is sufficient, or another concrete artifact beyond prose.

## Exact repository frontier

E1.0 branch/PR:

- PR #109 `engineering/experience-one-e1-0-risk-burndown-2026-09-12`;
- protected-main base: `65b1b1559eac8dfe0ed6be24739ba9ac32f83f3c`;
- this branch contains E1.0 evidence/spike/test artifacts and does not replace HUD, GIS, Navigator, renderer, campaign runtime, WORLD/CIVSTATE authority or active upstream engineering paths.

Active upstream heads at the baseline review:

- PR #96 WAYFARER_FLIGHT_SYSTEM — `835cccfb4a37a2a683c6196cbb7382b826271d67`;
- PR #99 HUD_LOCAL_FLIGHT — `8b1637e3e6ff7ebb718aa3dfb7b3310be3b6ac2f`;
- PR #103 EARTH_LUNA_SPATIAL_NAV_INTEGRATION — `d1bb0f721164b4ce325af5562006bc5fa16d2637`;
- PR #100 COMPUTATIONAL_SHIPYARD — `ea66fa980e189e5f68e0ceb8a15b1582e0ad31d7`.

These refs identify what exists; they are not substitutes for visual/behavioral captures when replacement is proposed.

## Already concrete deterministic references

### Deterministic route generation / ranked alternatives

Spike A provides a concrete deterministic planning reference for Ceres→Neptune multi-route behavior:

- 24 valid candidates;
- reproducible candidate-set fingerprint `c3d06cc16ef375e3385eaa0a69e4279f64086cb13e224e0d4be32bb5c2a8c049`;
- materially distinct candidates;
- independent deterministic validation;
- no campaign mutation.

Detailed reference: `E1_0_SPIKE_A_SOURCE_FINDING_v0.1.md`.

### Campaign execution / persistence / replay

Spike B provides a concrete campaign continuity reference:

- explicit commit boundary;
- persisted `FLIGHT_COMMITTED`→phase→`FLIGHT_ARRIVED` history;
- authoritative arrival state;
- restart recovery;
- deterministic offline replay;
- real campaign bit-identical because the spike used a disposable copy.

Detailed reference: `E1_0_SPIKE_B_EXECUTION_CONTINUITY_FINDING_v0.1.md`.  
Raw evidence: `evidence/E1_0_SPIKE_B_CAMPAIGN_RESULT.json`.

### Mara/model/tool boundary

Spike C provides a concrete conversational-boundary reference:

- one read-only typed state tool;
- model calculation/state authority zero;
- six adversarial cases passed on Pixel;
- missing facts remained missing;
- user/retrieved/stale claims did not override deterministic state;
- campaign hashes bit-identical before/after.

Detailed reference: `E1_0_SPIKE_C_MODEL_TOOL_BOUNDARY_v0.1.md`.  
Extracted evidence: `evidence/E1_0_SPIKE_C_PIXEL_RESULT_SUMMARY.json`.

## Current source surfaces requiring capture before replacement

### Wayfarer HUD / 3D / local flight — PR #99

PR #99 identifies the current executable/reference surface for:

- live Earth–Moon HUD;
- Wayfarer/Moon 3D viewport and camera interaction;
- trajectory rendering;
- time/Torch controls;
- preview propagation;
- intercept/rendezvous solving;
- scrubber and terminal-quality panel;
- six-direction orbital-frame control;
- typed command/plan contracts;
- non-mutating review;
- deterministic server-side review validation;
- one-time validated-plan execution ticket;
- explicit two-stage human review→execute authority boundary.

Its source/tests are useful references, but visual/interaction replacement still requires an appropriate concrete capture for the behavior being replaced.

### Wayfarer engineering envelope — PR #96

PR #96 remains the upstream engineering source. Experience One may consume only qualified/declared outputs or constrain itself to the qualified envelope. G1 does not duplicate this engineering authority.

### Earth–Luna spatial target/runtime seam — PR #103

PR #103 identifies the current reference for WORLD-backed facilities, standard orbit targets, shared target-state resolution and the HUD/Nav target contracts. Any replacement of its user-visible presentation requires a concrete regression capture; additive consumers may proceed without replacing it.

### Computational Shipyard — PR #100

PR #100 remains bounded research/qualification and is not an E1 blocking dependency absent a concrete gate failure.

## Capture backlog before any replacement

At minimum, capture the relevant current behavior before E1 replaces any of these:

- HUD composition / instrument layout;
- Wayfarer 3D appearance and camera interaction;
- route generation presentation and route playback;
- preview scrubber behavior;
- intercept/rendezvous presentation;
- Atlas/link-analysis presentation;
- Ceres world-summary presentation;
- Neptune world-summary presentation;
- any current command/review/execute interaction flow that E1 proposes to change.

The capture may be scoped to the exact behavior being replaced; G1 does not require a giant museum of every pixel before additive E1.1 work can begin.

## Allowed work while G1 remains open

E1.1 may proceed with additive/non-replacement work such as:

- read-only Canon Context Projection services;
- tests/fixtures for those services;
- new additive endpoints that do not displace current presentation;
- data/projection diagnostics;
- Mara read-only tool contracts that consume the projection without replacing existing UI.

It may **not** replace an uncaptured existing visual, interaction or command behavior.

## G1 current state

**G1 — IN_PROGRESS**  
**Evidence maturity:** `DOCUMENTED_ONLY` for the baseline index; concrete deterministic A/B/C fixtures exist separately but do not complete visual/interaction baseline capture.  
**Evidence class:** `DOCUMENTED` plus existing `TESTED` spike references.  
**Pass condition:** every E1-relevant behavior actually proposed for replacement has an adequate concrete regression reference captured before replacement proceeds.  
**Known limits:** visual/interaction capture is incomplete.  
**Blocking rule:** an attempted replacement without adequate capture is blocked.  
**Falsifier after eventual PASS:** G1 reopens if E1 replaces a current behavior lacking an adequate captured regression reference.
