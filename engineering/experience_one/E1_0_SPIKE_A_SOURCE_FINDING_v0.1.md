# LOOM 2226 — E1.0 Spike A Multi-Route Finding v0.1

**Status:** EMPIRICALLY TESTED — EXIT CLASSIFIED  
**Date:** 12 September 2026  
**Class:** `class:engineering` / `REQUIRED_FOR_E1` bounded spike evidence  
**Parent:** `E1_0_RISK_BURNDOWN_EVIDENCE_PACK_v0.1.md`  
**No canon/runtime authority change. No Experience One gate PASS is claimed.**

---

## 1. Source finding

The preserved Navigator wrapper already contains a real multi-candidate enumeration and deterministic ranking seam.

`src/loom_navigator_core.py::_candidate_plans(...)` builds canonical dependency/time-axis input, resolves route rows, evaluates the existing authoritative solver across metric/torch combinations, rejects infeasible/remass-invalid candidates, retains quantitative outputs, and deterministically ranks them by policy. The interactive campaign path displays ranked candidates, requires explicit selection, constructs a plan summary/SHA, and separately asks `COMMIT FLIGHT? [y/N]` before campaign mutation.

Therefore Experience One does not require a new multi-route solver merely to present route choice.

---

## 2. Empirical result

The direct Pixel/runtime experiment completed successfully against the existing Ceres → Neptune campaign state.

Observed evidence:

- acquisition mode: `OFFLINE_CACHE_ONLY`;
- valid candidate count: **24**;
- candidate generation was run twice with identical fixed inputs;
- both runs produced the identical candidate-set SHA-256 fingerprint `c3d06c...c049`;
- the candidate set contained materially distinct metric/torch combinations, including HARD/CRUISE, HARD/ECON, EXPEDITE/CRUISE and FAST/CRUISE examples;
- independently exercised candidate validation returned PASS for the validated subset;
- campaign state, backup state and compressed campaign history retained bit-identical before/after hashes;
- a prior online-enabled run and the restart/offline run both returned 24 candidates with the same candidate-set fingerprint.

The preserved empirical JSON/console evidence is external device evidence from the Pixel run. This repository finding records the observed result without pretending the source tree generated it locally.

---

## 3. Spike A exit classification

`BOUNDED_EXTENSION — EMPIRICALLY_TESTED`

Reason: the deterministic solver, candidate enumeration and ranking capability already exist. Experience One's remaining production need is a bounded typed exposure/curation of an existing candidate set, not new trajectory physics or a foundational Navigator redesign.

The source-only hypothesis `BOUNDED_EXTENSION — INFERRED / REQUIRES_EMPIRICAL_TEST` is therefore closed by empirical evidence.

This is a **Spike A exit classification**, not an Experience One gate PASS and not permission to promote the spike harness into production.

---

## 4. Falsifier

This classification must be reopened if a controlled rerun with the same pinned solver/state/epoch/problem fails candidate reproducibility, yields fewer than two materially distinct valid candidates, candidate validation diverges from enumeration, campaign artifacts mutate during read-only enumeration, or production exposure proves to require a new solver/hidden state/foundational authority change.

---

## 5. Production implication

E1.2 should consume the existing deterministic candidate machinery and expose only the small user-relevant ranked subset required by the Experience One interaction. The spike harness remains disposable evidence code.

Next E1.0 uncertainty: Spike B execution continuity.