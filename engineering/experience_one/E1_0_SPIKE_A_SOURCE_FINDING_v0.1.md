# LOOM 2226 — E1.0 Spike A Multi-Route Source Finding v0.1

**Status:** SOURCE FINDING — DIRECT EMPIRICAL RUN PENDING  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1` bounded spike evidence  
**Parent:** `E1_0_RISK_BURNDOWN_EVIDENCE_PACK_v0.1.md`  
**No canon/runtime authority change. No gate PASS is claimed.**

---

## 1. Finding

The current preserved Navigator wrapper on protected `main` already contains a real multi-candidate enumeration and deterministic ranking seam.

`src/loom_navigator_core.py::_candidate_plans(...)`:

1. builds the canonical dependency/time-axis input;
2. resolves origin/destination route rows;
3. loops over every `nav.METRIC_MODES × nav.TORCH_MODES` pair;
4. calls the existing authoritative `nav._solve_leg(...)` for each pair;
5. rejects infeasible candidates and candidates exceeding current remass;
6. retains quantitative candidate outputs including total time, remass use, arrival remass, thermal posture, arrival epoch, terminal Δv/burn, metric distance/duration/β, jet power/thrust/mdot and acceleration;
7. sorts the candidate set according to the requested deterministic policy.

Observed ranking policies are:

- `FASTEST`: `(total_s, remass_used_t)`;
- `REMASS`: `(remass_used_t, total_s)`;
- `CONSERVATIVE`: `(thermal_class, remass_used_t, total_s)`;
- otherwise/BALANCED: normalized time + normalized remass + deterministic thermal penalty, then `(balanced_policy_score, total_s)`.

The interactive campaign path then displays up to eight ranked candidates, requires explicit user selection, constructs a plan summary and plan SHA, and separately asks `COMMIT FLIGHT? [y/N]` before entering the campaign commit path.

This is materially stronger evidence than the historical multi-strategy record alone. The missing Experience One capability is therefore **not obviously a new multi-route solver**. It may instead be a bounded typed exposure/adapter over a candidate-set capability that already exists.

---

## 2. Current Spike A classification

**Not yet an exit classification.**

Source-only implementation-size hypothesis is now:

`BOUNDED_EXTENSION` — **INFERRED / REQUIRES_EMPIRICAL_TEST**

Reason: candidate enumeration and deterministic policy ranking already exist in current Navigator source. The remaining E1 production work appears likely to be exposing a small ranked subset through a stable typed contract rather than inventing multi-route solving.

This classification may be falsified by the direct run if current Ceres→Neptune state produces fewer than two valid candidates, ranking is not reproducible for fixed inputs, candidate validation diverges, or exposing the set requires hidden state/side effects/foundational solver changes.

---

## 3. Direct experiment harness

Added bounded spike harness:

`engineering/experience_one/spikes/e1_0_spike_a_multiroute.py`

The harness deliberately:

- requires an existing campaign state and refuses to create one;
- imports the preserved Navigator wrapper and hash-verifies its embedded Sequence H core through the existing loader;
- uses the existing B1 package and ephemeris acquisition/cache path;
- calls `_candidate_plans(...)` twice with fixed state/epoch/origin/destination/priority;
- fingerprints candidate membership/order/user-relevant quantitative metrics;
- checks for at least two materially distinct metric/torch pairs;
- independently sends emitted candidates through `target_determinism_gate(...)` up to the configured validation limit;
- hashes campaign state/backup/history before and after and fails closed if those campaign files change;
- emits `LOOM_E1_0_SPIKE_A_MULTIROUTE_RESULT_V1` JSON evidence;
- never calls the campaign commit path.

A helper-level unit test exists at:

`tests/test_e1_0_spike_a_multiroute.py`

The direct real-state run is still required. Unit/source evidence cannot substitute for that empirical result.

---

## 4. Target direct run

Pixel/runtime-root example from a checkout of this branch:

```bash
python engineering/experience_one/spikes/e1_0_spike_a_multiroute.py \
  --root /storage/emulated/0/Download \
  --repo . \
  --origin CERES \
  --destination NEPTUNE_SYSTEM \
  --priority BALANCED \
  --out /storage/emulated/0/Download/E1_0_SPIKE_A_MULTIROUTE_RESULT.json
```

Default acquisition is offline/cache-only. If and only if the existing cache lacks required ephemeris data, a second run may explicitly add `--allow-online-acquisition`; campaign state/history hashes still must remain unchanged.

The run result is evidence, not self-promoting authority.

---

## 5. Exit criteria

Spike A may receive an implementation-size exit classification only after the direct result records:

- at least two candidates;
- materially distinct candidate modes;
- exact same ranked candidate projection on identical rerun;
- independent deterministic validation of the emitted candidate subset;
- no campaign-state/history mutation;
- exact wrapper/core/state/epoch identity;
- preserved raw JSON evidence.

If these hold, the expected classification is `BOUNDED_EXTENSION`, subject to review of the production typed-contract work required.

If they do not hold, classify from observed failure rather than repairing the spike until it tells the desired story.
