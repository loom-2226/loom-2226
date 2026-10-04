# Phase 3B Kernel Validation Record 001

**Status:** PASS FOR AUTHORIZED KERNEL SLICE / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Branch:** `offworld-mvp-phase3`

## Scope

Validation covers only the implementation authorized by `PHASE3B_IMPLEMENTATION_AUTHORIZATION_001.md`: executable state kernel and deterministic fixtures. It does not authorize or validate the full agent engine.

## Execution environment

Tests were fetched from GitHub branch authority and executed on the authorized `quantifactus` VM using Python 3 `unittest`.

Command: `python3 -m unittest discover -s tests -v` from `simulation/offworld_mvp/phase3b/kernel`.

## Result

5 tests executed; 5 passed.

- four-route fixed-capital-formation locality: PASS
- four-route deterministic replay fingerprint: PASS
- ownership guardrail: PASS
- ENCLAVE vs SETTLEMENT recursive divergence: PASS
- recursive-fixture deterministic replay: PASS

## Four-route semantics exercised

A. Earth financing / Earth supplier / offworld asset.
B. Offworld local financing / local supplier / local asset.
C. Offworld financing / Earth supplier / offworld asset.
D. Offworld node A financing/supply / offworld node B asset.

Earth-supplied offworld assets did not appear in Earth productive capital. Earth qualifying supplied expenditure generated the explicit MVP terrestrial-FCF displacement entry at the supplier node.

## Recursive falsification fixture

Identical seed state, 50 deterministic years:

| Policy | Final offworld productive capital | Cumulative local FCF | Earth returns |
|---|---:|---:|---:|
| ENCLAVE | 100 | 0 | 500.00 |
| SETTLEMENT | 4690.161251323119788044196608 | 4590.161251323119788044196608 | 1147.540312830779947011049152 |

The large SETTLEMENT growth is not a forecast or calibration result. The fixture deliberately uses a simple 10% surplus on productive capital and 80% reinvestment to test whether recursive local capital formation actually compounds. Its magnitude demonstrates the mechanism and also demonstrates why economic parameters remain gated rather than being mistaken for reality.

Deterministic fingerprints:

- ENCLAVE: `89dc5948eda8d78b40063367e5ef448fb24a077f667ea7a557488dd5ed047637`
- SETTLEMENT: `1f908edb72b1b95c1e3076e01d6664687472b49939384705502721a54b756419`

## Interpretation

The authorized kernel slice has passed its first mechanical falsification test: identical starting worlds diverge when surplus-disposition policy differs, and the divergence occurs through explicit location-specific expenditure, FCF and productive-capital state rather than scripted colony stages.

This is not Phase 3B closure. Information/belief, resource-stock, population, exploration-resolution and fuller causal-event lineage remain to be implemented/tested before requesting full agent-engine authority.