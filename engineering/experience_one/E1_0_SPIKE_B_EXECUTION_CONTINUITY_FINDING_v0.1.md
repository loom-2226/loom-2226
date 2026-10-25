# LOOM 2226 — E1.0 Spike B Execution Continuity Finding v0.1

**Status:** EMPIRICALLY TESTED — EXIT CLASSIFIED  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1` bounded spike evidence  
**Parent:** `E1_0_RISK_BURNDOWN_EVIDENCE_PACK_v0.1.md`  
**Raw evidence:** `evidence/E1_0_SPIKE_B_CAMPAIGN_RESULT.json`  
**Uploaded artifact SHA-256:** `9a18688f0a1a10fe7d3b6f5feba55aa81eaa1c5223dcea16287f05b00396842b`  
**No canon change. No production promotion. No E1.0 GO claim.**

---

## 1. Question

Can Experience One authorize an interplanetary route, mutate campaign authority exactly once through the existing Navigator path, persist the result, restart from it, and deterministically replay it without introducing a second campaign/state authority?

---

## 2. Empirical configuration

The Pixel test used the user's existing campaign as a **read-only source** and copied authoritative state/history into a disposable temporary root. The disposable campaign began at `MARS` because that was the actual current campaign location at test time; the test destination was `NEPTUNE_SYSTEM`, priority `BALANCED`, ranked plan `1`.

The spike redirected only legacy Android root lookup into the temporary root and suppressed only the final indefinite local HTTP presentation hold so the harness could proceed to restart/replay checks. Planning, candidate selection, explicit authorization, deterministic flight execution, campaign history mutation, state persistence, reload and replay remained the existing Navigator implementation.

The scenario origin differs from the preregistered Experience One Ceres origin. That does **not** establish the Ceres product fixture; it answers the narrower Spike B authority/continuity question for the existing interplanetary campaign path.

---

## 3. Observed execution

The existing Navigator path:

1. generated ranked direct candidates;
2. selected plan `1` (`HARD / CRUISE`);
3. displayed final plan SHA `75de273b020d434a760f2c83f8c31c800773f59da07974d5c305303ca3986ad0`;
4. required explicit `COMMIT FLIGHT? [y/N]` authorization;
5. committed and executed `F000002`;
6. persisted arrival state `S000009-f76dfb43c8c5` at `NEPTUNE_SYSTEM`;
7. advanced epoch from `2027-06-15T08:57:51.391985Z` to `2027-06-15T16:59:33.376486Z`;
8. reduced remass to `168.52038271644005 t` and wet mass to `1077.02038271644 t`;
9. recorded `FLIGHT_COMMITTED`, two `FLIGHT_PHASE` records, and `FLIGHT_ARRIVED`;
10. persisted `BODY_RENDEZVOUS` kinematic boundary and `last_flight` provenance;
11. reloaded the disposable state as `EXISTING`;
12. replayed offline from the content-addressed cache with expected and replay runtime SHA both equal to `178b67b07aadc5bd80c574f78827fb3bb1fc031912859b846df6d77ebef00df0`.

Artifact booleans:

- `committed_and_arrived_pass: true`
- `restart_destination_pass: true`
- `replay_pass: true`
- `real_campaign_unchanged_pass: true`
- `spike_observation_pass: true`

The real campaign artifacts were bit-identical before/after:

- `LOOM_STATE_V1.json`: `4d89892fa9feed7a8f59e4cb10d4ee27df1b27268bfe2e68c19d70585697e48c`
- `LOOM_STATE_V1.bak`: `421a07458103ab39b84601366fd9508499b9662ce8c6e4312016070d5bd2b92b`
- `LOOM_CAMPAIGN_HISTORY.jsonl.gz`: `ba0bc0ae9b42d204ee4986b85088dc6d2b86b92f2f4471f70b66709517f9c4ec`

---

## 4. Exit classification

`BOUNDED_ADAPTER — EMPIRICALLY_TESTED`

Reason: the authoritative interplanetary execution path already exists and closes selection → explicit authorization → deterministic execution → `FLIGHT_COMMITTED` → `FLIGHT_ARRIVED` → atomic persistence → restart → replay without a second state model. Experience One therefore needs a bounded typed handoff into that authority path, not a merged executor or foundational authority reconciliation.

PR #99's qualification-only local maneuver executor should remain qualification/local-maneuver scope unless a separate governed requirement proves otherwise. Its `campaign_mutation=False` / `navigation_grade=False` semantics are not a defect exposed by Spike B.

---

## 5. Operational findings that remain real

Two bounded integration seams were exposed by the test harness:

- the preserved interplanetary entry path assumes the Android root `/storage/emulated/0/Download` internally instead of accepting an injected campaign root;
- successful campaign execution ends in an indefinite presentation server hold (`serve_sequence_d(...)`), so automation/test callers need a bounded non-serving adapter or return path.

These are integration/testability seams, not evidence of duplicate campaign authority.

---

## 6. Falsifier

Reopen this classification if production Experience One cannot invoke the existing Navigator commit path through a typed adapter without duplicating state/mutation logic; if stale-state/authorization boundaries cannot be preserved; if the Ceres fixture reveals route-specific continuity failure; if persisted state/history diverge on restart; if replay fails for pinned inputs/cache; or if another component must become authoritative for interplanetary campaign mutation.

---

## 7. Production implication

E1.3 should design the smallest typed adapter from selected validated route candidate + explicit user authorization into the existing Navigator campaign commit authority. Do not route interplanetary campaign mutation through PR #99 merely for architectural symmetry.

Next E1.0 uncertainty: Spike C Mara/model/tool plumbing.