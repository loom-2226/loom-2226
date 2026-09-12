# LOOM 2226 — Experience One E1.0 Baseline Fixture v0.1

**Status:** BASELINE CAPTURED FOR E1.0  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1` bounded enabling evidence  
**Purpose:** regression/reference fixture for Experience One convergence; not canon authority and not a replacement implementation.

## Governing rule

This fixture exists to satisfy the Experience One baseline discipline before convergence work begins replacing or integrating existing behavior.

`G1 — No replacement without a fixture.`

A behavior not captured here is **not** thereby authorized for replacement. If later E1 work proposes replacing a visual/runtime behavior whose regression reference is absent or insufficient, capture that behavior first.

## Exact repository frontier

E1.0 branch/PR:

- PR #109 `engineering/experience-one-e1-0-risk-burndown-2026-09-12`.
- protected-main base: `65b1b1559eac8dfe0ed6be24739ba9ac32f83f3c`.
- this E1.0 branch contains evidence/spike/test artifacts only; it does not replace the existing HUD, GIS, Navigator, renderer, campaign runtime, WORLD/CIVSTATE authority or active upstream engineering paths.

Active upstream heads revalidated during baseline closure:

- PR #96 WAYFARER_FLIGHT_SYSTEM — `835cccfb4a37a2a683c6196cbb7382b826271d67`;
- PR #99 HUD_LOCAL_FLIGHT — `8b1637e3e6ff7ebb718aa3dfb7b3310be3b6ac2f`;
- PR #103 EARTH_LUNA_SPATIAL_NAV_INTEGRATION — `d1bb0f721164b4ce325af5562006bc5fa16d2637`;
- PR #100 COMPUTATIONAL_SHIPYARD — `ea66fa980e189e5f68e0ceb8a15b1582e0ad31d7`.

## Captured capability references

### Wayfarer HUD / 3D / local flight

PR #99 is the current executable/reference surface for:

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

PR #99 reports direct Pixel acceptance for the six-direction controls and review surface and a successful Python regression at its exact head.

### Wayfarer engineering envelope

PR #96 is the current upstream engineering source for the Wayfarer flight-system qualification frontier. It preserves open/non-canon gaps explicitly rather than allowing E1 to fill them by convenience. Experience One may consume only qualified/declared outputs or constrain itself to the qualified envelope.

### Earth–Luna spatial target/runtime seam

PR #103 is the current reference for:

- WORLD-backed facility identity/facts;
- 31 facilities + 9 standard orbit targets;
- shared target-state resolution;
- `LOOM_HUD_SPATIAL_OBJECT_V1`;
- `LOOM_EARTH_LUNA_SCENE_V1`;
- `EarthLunaTargetRouter`;
- `NavigationTargetAdapter(runtime.router)`;
- explicit separation between 2226 Earth–Luna scene authority and the 2026 local-flight qualification surface.

Its exact head reports a successful Python regression and remains mergeable.

### Computational Shipyard

PR #100 remains a bounded research/qualification child and is explicitly **not** an E1 blocking dependency absent a concrete gate failure. No Experience One baseline assumption promotes its candidate dynamics to production authority.

### Deterministic route generation / ranked alternatives

Spike A provides the deterministic planning fixture for current Ceres→Neptune multi-route behavior:

- 24 valid candidates;
- reproducible candidate-set fingerprint `c3d06cc16ef375e3385eaa0a69e4279f64086cb13e224e0d4be32bb5c2a8c049`;
- materially distinct candidates;
- independent deterministic validation;
- no campaign mutation.

Detailed reference: `E1_0_SPIKE_A_SOURCE_FINDING_v0.1.md`.

### Campaign execution / persistence / replay

Spike B provides the current interplanetary campaign continuity fixture:

- explicit commit boundary;
- persisted `FLIGHT_COMMITTED`→phase→`FLIGHT_ARRIVED` history;
- authoritative arrival state;
- restart recovery;
- deterministic offline replay;
- real campaign bit-identical because the spike used a disposable copy.

Detailed reference: `E1_0_SPIKE_B_EXECUTION_CONTINUITY_FINDING_v0.1.md`.  
Raw evidence: `evidence/E1_0_SPIKE_B_CAMPAIGN_RESULT.json`.

### Mara/model/tool boundary

Spike C provides the current conversational-boundary fixture:

- one read-only typed state tool;
- model calculation/state authority zero;
- six adversarial cases passed on Pixel;
- missing facts remained missing;
- user/retrieved/stale claims did not override deterministic state;
- campaign hashes bit-identical before/after.

Detailed reference: `E1_0_SPIKE_C_MODEL_TOOL_BOUNDARY_v0.1.md`.  
Extracted evidence: `evidence/E1_0_SPIKE_C_PIXEL_RESULT_SUMMARY.json`.

## Visual evidence limitation

This E1.0 repository fixture is source/output-centric. It does not claim to contain a complete screenshot archive of every existing visual behavior. The workplan permits screenshots where practical; lack of a screenshot is therefore not itself a gate failure. However, **any later proposal to replace a currently working visual behavior must capture an adequate visual regression reference before replacement**.

This is especially relevant to:

- HUD composition/instrument layout;
- Wayfarer 3D appearance;
- route playback presentation;
- preview scrubber behavior;
- Atlas/link-analysis presentation;
- Ceres/Neptune world-summary presentation.

## G1 pass statement

**G1 — PASS**  
**Evidence class:** `OBSERVED_IN_SOURCE` + `TESTED` for the deterministic spike fixtures.  
**Exact refs:** this fixture; PR #96/#99/#103/#100 heads listed above; Spike A/B/C records and evidence artifacts in PR #109.  
**Target configuration:** Pixel-first Experience One frontier, protected-main base `65b1b1559eac8dfe0ed6be24739ba9ac32f83f3c`, current active upstream heads as listed.  
**Known limits:** screenshot coverage is not comprehensive; uncaptured visual behavior remains protected from replacement until a regression reference is captured.  
**Falsifier:** G1 is invalidated if E1 replaces a currently working renderer, scrubber, route view, HUD behavior, graph behavior or command path without an adequate regression reference for that specific behavior.
