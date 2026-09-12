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
| Spike B | `PASS` | `EMPIRICALLY_TESTED` | Disposable Pixel campaign executed the existing interplanetary authority path, persisted arrival, restarted, replayed deterministically, and left the real campaign bit-identical. Exit classification: `BOUNDED_ADAPTER`. |
| Spike C | `IN_PROGRESS` | `IMPLEMENTATION_EVIDENCE_PRESENT` | Model/tool adversarial harness exists; provider/runtime selection is now an explicit Pixel preflight rather than an assumed OpenAI-key path. |
| E1.0 GO/REPLAN | `NOT_STARTED` | `DOCUMENTED_ONLY` | Must wait for baseline + Spike C exit. |

Spike A/B PASS statements are limited to their falsifiable spike exit criteria. No Experience One product gate is thereby passed.

## 2. Baseline evidence

PR #99's local maneuver path is explicitly qualification-only (`campaign_mutation=False`, `navigation_grade=False`). Preserved Navigator assigns Python authoritative state, quantitative reconciliation, ephemeris, flight calculations, operational choices, commit/execution, history and handoff. Persistent campaign artifacts include state, backup and compressed history. Replay requires both `FLIGHT_COMMITTED` and `FLIGHT_ARRIVED`.

Spike B now empirically shows that the local qualification path and interplanetary campaign path can remain separate authority scopes. Do not merge them merely for visual architectural symmetry.

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

## 4. Spike B — CLOSED

The direct Pixel disposable-state experiment used the real campaign as a read-only source, copied its state/history into a temporary campaign root, then exercised the **existing Navigator interplanetary campaign path**. The current campaign was at Mars, so the empirical continuity leg was `MARS → NEPTUNE_SYSTEM`; this answers the Spike B authority/continuity question but does not substitute for the preregistered Ceres Experience One fixture.

Observed evidence:

- ranked plan `1` selected as `HARD / CRUISE`;
- final plan SHA `75de273b020d434a760f2c83f8c31c800773f59da07974d5c305303ca3986ad0`;
- explicit `COMMIT FLIGHT? [y/N]` authorization required;
- `F000002` committed/executed through existing Navigator authority;
- disposable history recorded `FLIGHT_COMMITTED`, two `FLIGHT_PHASE`, and `FLIGHT_ARRIVED`;
- persisted arrival state `S000009-f76dfb43c8c5` at `NEPTUNE_SYSTEM`;
- restart/reload mode `EXISTING` recovered the same authoritative arrival state;
- `BODY_RENDEZVOUS` kinematic boundary and `last_flight` provenance persisted;
- offline replay expected/runtime SHA both `178b67b07aadc5bd80c574f78827fb3bb1fc031912859b846df6d77ebef00df0`;
- `replay_pass: true`;
- real campaign state, backup and history hashes were bit-identical before/after;
- `spike_observation_pass: true`.

**Exit classification:** `BOUNDED_ADAPTER — EMPIRICALLY_TESTED`.

The test also exposed two bounded integration seams: a legacy hard-coded Android Download root in the interplanetary entry path, and an unconditional final `serve_sequence_d(...)` presentation hold. Both are integration/testability issues, not evidence of a second campaign authority. The Android-root seam must remain visible against the later Pixel gate rather than being buried as generic cleanup.

**Falsifier:** reopen if production E1 cannot enter the existing Navigator commit path through a typed adapter without duplicate state/mutation logic; if explicit authorization/stale-state boundaries cannot be preserved; if the Ceres fixture reveals route-specific continuity failure; if restart/replay diverges; or if another component must become authoritative for interplanetary campaign mutation.

Detailed record: `E1_0_SPIKE_B_EXECUTION_CONTINUITY_FINDING_v0.1.md`.  
Raw evidence: `evidence/E1_0_SPIKE_B_CAMPAIGN_RESULT.json`.  
Uploaded artifact SHA-256: `9a18688f0a1a10fe7d3b6f5feba55aa81eaa1c5223dcea16287f05b00396842b`.

## 5. Spike C — minimum Mara/model/tool plumbing

The adversarial experiment contract and direct-OpenAI candidate harness exist, but the provider/runtime boundary is no longer assumed.

Required pipeline remains:

`USER → MODEL → exactly one read-only typed get_wayfarer_state call → deterministic LOOM projection → MODEL grounded response`

Provider/runtime preflight now compares three shapes:

1. GitHub Copilot SDK/CLI using user GitHub authentication if it works on the actual Pixel/Termux runtime;
2. direct OpenAI Responses API as a valid spike fallback if the user deliberately chooses a separately billed API account/key;
3. a brokered backend only if no safe local user-auth path is viable.

Important correction: GitHub Models inference API is retired and is **not** a candidate. The GitHub path under test is Copilot SDK/CLI. Official documentation supports Linux and publishes Linux ARM64 runtime paths, but Android/Termux is not documented; Pixel viability therefore requires empirical evidence.

Adversarial matrix:

1. normal authoritative-location question;
2. direct contradiction request;
3. absent-fact trap (named reactor-control engineer);
4. plausible-inference trap (Mars ⇒ Phobos docking);
5. retrieved-text prompt injection embedded in untrusted world text;
6. stale-state override attempt.

The absent-fact and plausible-inference cases are load-bearing. Resisting only the obvious contradiction is insufficient.

Provider-independent invariants remain: model calculation authority ZERO; model state authority ZERO; exactly one read-only typed state tool; no write/action/campaign-mutation tool; no direct SQLite handle; missing facts remain missing; model context is disposable/reconstructible; campaign files remain bit-identical; logs are evidence only, never authority.

Current state: `IN_PROGRESS / IMPLEMENTATION_EVIDENCE_PRESENT`; no Spike C PASS until a real model/tool run exists on the Pixel path.

Provider decision record: `E1_0_SPIKE_C_PROVIDER_DECISION_v0.1.md`.  
Provider preflight: `spikes/e1_0_spike_c_provider_preflight.py`.  
Detailed experiment contract: `E1_0_SPIKE_C_MODEL_TOOL_BOUNDARY_v0.1.md`.  
Direct-OpenAI candidate harness: `spikes/e1_0_spike_c_mara_tool_loop.py`.

## 6. GO / REPLAN

Current state: `NOT_STARTED / DOCUMENTED_ONLY`. Do not fill until baseline and Spike C exit evidence exist.

## 7. WALTER / #LOOMSAFE

Active watches: documentation-as-progress; duplicate flight/campaign authority; spike promotion; model authority creep; PASS without falsifier; vendor/data/cost/lock-in and prompt-injection risk for Spike C. Spike B additionally records legacy Android root coupling and presentation-server hold as bounded integration seams for later production work.

## 8. Next action

Run the non-secret Pixel provider preflight. If a GitHub Copilot user-auth path is viable on Termux, test that before creating a separate model-provider credential. If Pixel/runtime support fails, record the failure as Spike C evidence and deliberately choose between direct API fallback and a brokered seam. Do not treat setup friction as something to hide from the implementation-size classification.