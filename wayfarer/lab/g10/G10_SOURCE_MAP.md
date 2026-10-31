# G10 v0.2 source map: existing flight-dynamics code for Wayfarer rev 5

ALL bodies. ALL sponsors. 2026-2226.

**NON-GOVERNING.** A source-discovery record, not mission results or certification evidence. G10 stays OPEN. No canon, runtime or main changes.

**Provenance:**
- Findings: Sol's audit of 2026-10-26 against LOOM main [`19377b85`](https://github.com/loom-2226/loom-2226/commit/19377b854c529e74afc61202d9eb2e780c5b4884) and the Research Lab [`2ea1518d`](https://github.com/loom-2226/loom-research-lab/commit/2ea1518d23ce03e626a935a7566fe703d5769dc7).
- Writing: Sol's tools could not write this file, so Claude wrote it and checked the paths and entry points against main `19377b85`.

**Test card for every item:** `design/wayfarer/v0.5.7/rev5/out/wayfarer_v05_card.json` (geometry `ed692f90...`).

## Map

| G10 item | Existing source (main 19377b85) | Entry point | Fit | What is missing for rev 5 |
|---|---|---|---|---|
| RCS: slews on 3 axes with full inertia, thruster-cluster-out | `src/wayfarer_rcs_closed_loop_gnc.py` (276 lines) | quaternion closed-loop helpers | **ADAPT** | Feed the rev 5 inertia tensors and RCS cluster layout from the card; add roll; add attitude hold against a torch disturbance torque |
| RCS: translation and coupled force/torque | `src/wayfarer_rcs_time_domain_mount_coupling.py` (257 lines) | `build_time_domain_mount_coupling_qualification()`, `_simulate_case()` | **ADAPT** | Replace the older ship assumptions with rev 5 masses and positions; add a minimum-impulse check |
| Torch: exhaust modes, thrust and power | `src/wayfarer_torch_mode_cards.py` (26 lines) | `mode_outputs(mode)` | **ADAPT** | A time-stepped burn: falling mass at constant jet power, 4 g cap, CG moving as tank cells drain, thrust-vector demand. **The integrated tank-drain simulation was NOT FOUND** |
| Metric: ramp, cryogenic load, thermal | `src/wayfarer_e1_metric_frontier_closure.py` (95 lines) | `build_metric_closure(scenario)` | **ADAPT** | **An executable mode state machine was NOT FOUND** (torch off, deploy, ramp, transport, collapse; torch/metric exclusion). No metric Δv/remass without U^M_gamma (canon II §20) |
| Loom: configuration lock and mode sequence | E1 integration specification (documentation only) | — | **NOT FOUND (executable)** | Executable metric collapse, then NRE relaxation, then Loom formation; configuration-lock check; arrival momentum closed by the torch. The domain boundary stays open on PR #356 (`INDETERMINATE_NOT_CERTIFIABLE`) |
| Ship-card import | `src/loom_navigator_core.py` (1,643 lines) | campaign state, remass accounting | **ADAPT** | Direct rev 5 card import was not established |

## Gaps (new code needed)

1. Torch: a tank-drain burn integrator with CG migration and thrust-vector demand.
2. Metric: an executable mode state machine with torch/metric exclusion.
3. Loom: an executable collapse, relaxation and formation sequence, plus a configuration-lock check.
4. Card adapters: feed the rev 5 card into the RCS and coupling modules, which currently use older ship assumptions.

## Rules carried forward

- **Research Lab code** is non-canon and non-runtime. It may inform the tests but is not cited as authority.
- **No metric Δv or remass** without a calibrated U^M_gamma and a terminal solver (canon II §20).
- **No Loom domain-fit claim** while PR #356 is indeterminate.
