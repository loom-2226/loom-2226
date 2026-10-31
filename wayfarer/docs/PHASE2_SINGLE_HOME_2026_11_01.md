# Wayfarer Phase 2: five-folder move — conditional integration

ALL bodies. ALL sponsors. 2026-2226.

**Primary class: class:engineering. NO PHYSICS CHANGE. NO CANON PROMOTION.**

## Live GitHub authority blocker

At Phase 2 bootstrap, PR #437 was OPEN/UNMERGED and live main was f07354f57244d62e7c1932cacddd0f996d45e941. The merge reported in chat was NOT verifiable. This conditional Phase 2 branch descends from accepted Phase 1 head eb3fc9ab9f1fa58880775f7ce739927048e367b2. It must not be promoted as if Phase 1 were already on main. Only retarget main after authoritative merge verification and rerun all requirements.

## Provenance and physical migration

- Removed former design/wayfarer/v0.5.7 path entirely, with NO compatibility shims.
- Exactly five top-level directories: wayfarer/config, wayfarer/lab, wayfarer/render, wayfarer/results, wayfarer/docs.
- Moved source inputs to config; build, certify, command, habitat, torch, G10 and FQ scripts to lab; source-stamped renders/viewer to render; geometry/card/certification/comparison to results; human records to docs.
- Brought combined PR #436 flight tree (PR #433 lab plus non-governing propulsion cards) under wayfarer/lab/flight. Original PR #433 head 59b849e55d1f113f164d5daea07c7d6db6a0a546; PR #436 head 9072b0565feaa66860cd4fd516539b7860e69b25.
- Original flightlab.py SHA256 137d13fe182578d227b444ad27ca5d55ac85475028e5e7909f53e2916a761bb2 preserved unchanged. Historical pre-I4 Rev7 geometries/cards used by historical tests are explicitly PINNED FIXTURES only at lab/flight/fixtures/rev7; not second active ship authority.
- Existing src, canon, governance, Navigator and all frozen branches unchanged. Downstream code review is REVIEW_REQUIRED for future consumers; no new runtime integration.

## Verification

- Rebuilt lab/build_v05.py: exact byte SHA256 5d73cdd1d7893b75637fc3b2e8bf2d9b786b792fede277e759561643f4ee0256.
- Reran lab/certify.py: all 12 gates PASS or PASS-DECLARED, all 18 declarations kT ACCEPTED, machine certified=true.
- Python compilation: 52/52 modules compile.
- Full flight/cards/hardware/Metric-canonical regression: 61/61 PASS, all five original test modules, zero skips. Four prior excluded tests and eight canonical operation tests restored. Earlier cards/hardware subset 18/18 PASS.
- render/deckplans.py L1-L5; render/export_glb.mjs produced two-scene 5d73 GLB; render/render.js produced cmd_cutaway PNG; make_viewer.py regenerated viewer; G12 PASS-DECLARED.
- FQ1-FQ10 same-hash numerical replay from Phase 1 remains under lab/flight_qual/integration_20261101, including 93 half-step parity verdict pairs, zero changes. No new FQ mission or Metric flight campaign performed in Phase 2.

## Holds and historical exceptions

**Metric arrival HOLD, Navigator EXCLUDED, RCS power source OPEN.** Metric/canonical lab tests are now executed; source-derived ramp HOLD, torch overlap veto and unresolved arrival remain enforced; there are no runtime compatibility shims. Old archived setup/patch scripts that require a missing scratch source were not represented as portable runner qualification. Future repair requires separate scope. PR #433 and #436 remain non-governing historical evidence.

Independent review + exact-head loom-gate required before kT merges Phase 2. Because #437 has not been verified merged, direct main promotion and closure of archive PRs #429/#430/#432 are HOLD; retain archive branches on any later closure. No automatic user merge was performed.

Rollback: close unmerged conditional Phase 2 PR or revert migration commit, leaving main untouched. No freeze/canon/runtime changes.


## Review correction — all 61 lab tests

Executed the complete lab suite with test_cards, test_flightlab, test_completion, test_hardware_assess and test_canon_metric_operation in one invocation: **61/61 PASS**, zero exclusions. A reproducible runner is at wayfarer/lab/flight/run_lab_regression.py, replacing the non-Metric-only runner.

Import/path changes only to canonical_metric_operation in flightlab.py: old detached source/src/ imports now use the repository src/; G10 input is wayfarer/lab/g10; canon and engineering spec provenance hashes resolve against the repository root. Logic of Metric engagement, phase transitions, hold at ramp, refusal of torch overlap, and no invented terminal arrival state remains unchanged. Original PR #433 flightlab.py SHA256 137d13fe182578d227b444ad27ca5d55ac85475028e5e7909f53e2916a761bb2 identifies the preserved historical version, NOT the relocated working file after the import repair.

Metric arrival remains HOLD, Navigator EXCLUDED, RCS heating supply OPEN. Passing a HOLD behavior test is not a certification of flight or arrival.
