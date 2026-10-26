# LOOM 2226 — Wayfarer Full Flight Laboratory: New Chat Handoff
**Verified live on quantifactus:** 27 October 2026 (Australia/Melbourne).
**Purpose:** Resume the EXISTING VM experiments without losing artifacts or repeating work. Next discussion: what is the MINIMUM meaningful path from numerical flight testing to full Wayfarer qualification/certification in the LOOM simulation. Do not invent physical evidence or new metric laws.

## Hard boundaries
- LIVE GITHUB OUTRANKS CHAT for any claim of current repository authority.
- Authoritative repository: `loom-2226/loom-2226`. At the 27 October test bootstrap, live `main` was `19377b854c529e74afc61202d9eb2e780c5b4884`.
- Latest detailed experimental Wayfarer candidate was **v0.5.7 Rev 7**, pinned to commit `3485830a56dfead79b2ef8bba031a595b536fbb5`, available on `archive/wayfarer-v057-20261026`. Rev 7 was NOT on main; draft [PR #432](https://github.com/loom-2226/loom-2226/pull/432) remained open. This is **NON-GOVERNING / NON-CANON / NOT HARDWARE CERTIFIED**.
- ACTIVE scratch workspace, writable for explicit user-authorized experiments ONLY:
  `/home/ubuntu/wayfarer_flight_lab_scratch_20261026/`.
- **NEVER edit** original Astra:
  `/home/ubuntu/wayfarer_flight_study_20261026/`.
- The scratch workspace's `source/` is a read-only pinned checkout of Wayfarer Rev 7 and LOOM source. At final full-flight check, `git -C source status --short` was clean. No GitHub modification, push, merge, PR changes or canonical runtime edits were made in the flight-lab work.
- Authorized VM: `quantifactus`, Remote Desktop Commander device ID `0a7cbeb3-2e9a-42f9-9eb3-6b06217d0074`.
- No full canonical metric ordinary-state propagation is available. Deliberately keep (U^M_\\gamma), conservation ledgers and terminal arrival state UNKNOWN. User explicitly asked to LEAVE that gap. Do not use hypothetical metric displacement as canonical truth.
- LOOM project preference: **research broadly, model narrowly, use/simulate what exists early, reject overengineering**. Do not add software infrastructure unless a specific tested behavior requires it.

## Completed work and full-flight campaign
There is a runnable generalized rigid-body and propulsion laboratory in `flightlab.py` driven by `lab.py`, JSON spacecraft configs and experiments:
- Independent interchangeable ships (Wayfarer and Scout), full mass/CG/inertia with configurable engine masses and tanks, continuous quaternion/position/velocity/omega state, point gravity.
- Fixed and two-axis dynamically gimballed RCS allocation with thrust-lag, commanded slew/actual actuator states, thrust limits, torque/mount forces and per-nozzle telemetry.
- Single/multiple conventional torch engines, off-axis torque and optional RCS stabilization, Isp/propellant depletion, mass/CG changes.
- Canonical metric operational sequence checked with gate HOLD, not ordinary-state propagation; two **explicitly non-canon** experimental metric coordinate maps also runnable.
- Hardware assessment in `hardware_assess.py`: installation force, mount-strength comparison, finite propellant/feed where declared, coarse plume screening, thermal limits and evidence-backed PASS/FAIL/HOLD.
- Original Astra fixed RCS cases, gimbal references, and independent numerical dynamics checks reproduced.

**The latest completed all-flight run** is saved in:
`/home/ubuntu/wayfarer_flight_lab_scratch_20261026/full_flight_20261027/`.
Start by reading **`full_flight_20261027/FLIGHT_TEST_REPORT.md`**.
The written report and ten execution lanes were verified. All 10 `*_exit.txt` markers were `=0`. The original `source/` stayed clean.

### Verified scorecard (2026-10-27)
- **55/55** lab regression tests passed (43 prior + 12 hardware assessment).
- **25/25** original Wayfarer Rev7 G10 source checks passed (5 card, 7 RCS, 4 torch, 5 metric, 4 Loom). These are NON-GOVERNING engineering calculations; deferred Navigator mission fixtures are NOT implied to pass.
- **11 baseline demo scenarios:** 8 numerical pass, 2 expected failure cases, 1 canonical metric indeterminate.
- **14 advanced demos:** 10 numerical pass, 3 expected failure cases, 1 indeterminate.
- **18 additional Wayfarer sweep:** 18 numerical pass (all 6 torch modes x 120s, roll/pitch/yaw turns for original and upgraded RCS, ±x/±y/±z 0.5 m/s translation).
- **9/9 saved historical Astra fixed-RCS references match** to numerical precision (11 total tested configurations in comparison).
- **7 hardware assessment scenarios:** computed useful numeric margins, but **all overall Wayfarer hardware dispositions remain HOLD**. The deliberate hypothetical Scout has explicit mount, thermal and plume FAIL checks.
- NASA 42 fixed-RCS replay (700 samples): max attitude mismatch `6.993355899838714e-06°`. Verifies integrator replay, not independent controller or hardware qualification.
- GMAT R2026a finite 600s conventional torque-free surrogate: position mismatch `0.0023187040 m`, velocity `1.29667775e-6 m/s`, mass `7.65314e-7 kg`. Not off-axis installed torch qualification.
- Four-g instant acceleration cap was confirmed by 600 actual per-step samples each for HARD and LIMIT; cap `4.000000000000002g` numerical precision.

### Wayfarer findings
- **Baseline S1 mass** about 1,167,680 kg, with **250,000 kg normal remass tank**; 50 t separate protected water reserve is NOT usable propulsion remass.
- 32 original 25 kN RCS thrusters, 24 nonaxial and eight axial; baseline 180° attitude reversal in **40 s PASS**, 10 s **FAIL**.
- **Correct successful fixed-300 kN architecture** = uprate ALL 24 non-axial original-position engines to 300 kN, retain all eight original axial at 25 kN. In 10 s: 0.046294278° terminal attitude error and 0.037623799°/s rate, PASS; final uninterrupted settling gate entered 10.62 s. One-cluster-out fails the 10 s maneuver. Do NOT confuse with the different older *eight inward engines only*, moved mount, hypothetical mass candidate; it fails with 23.77° error.
- **Added eight 300 kN gimballed coarse motors + original 32 fine RCS:** numerical 10s fails, 12s/14s pass; nominal 12s terminal attitude error 0.028993430° and 0.018693259°/s rate; physical mounting and feed still OPEN.
- ±0.5m/s transverse/axial translation runs pass numerically with speed error ~0.00007747m/s; actual RCS propellant consumption is **UNKNOWN**, not zero.
- Conventional torch all six modes pass the 120s modeled attitude/g limits. Tank use and percentage of 250,000 kg normal remass capacity:

| Mode | 120 s remass, kg | % normal tank |
|---|---:|---:|
| ECON | 136.33 | 0.055% |
| CRUISE | 681.66 | 0.273% |
| EXPEDITE | 2,726.64 | 1.091% |
| FAST | 5,564.57 | 2.226% |
| HARD | 12,150.87 | 4.860% |
| LIMIT | 18,178.89 | 7.272% |

- HARD and LIMIT intentionally enforce 4g while throttle is curtailed. Peak thrust over *final* mass can misleadingly exceed 4g; per-step actual thrust/mass was measured and confirmed cap.
- Off-axis torch without RCS stabilization FAILS; held offset torch passes numerically; empty tank causes correctly detected failure.
- Experimental continuous seven-phase flight retains state at all six boundaries; canonical metric arrival is correctly HOLD/INDETERMINATE with no made-up normal-state recovery.
- Peak hardware demand at common mounts: original 25 kN ~25.0 kN, fixed 300 kN ~300.001 kN, eight extra gimbals ~324.632 kN; modeled central CRUISE torch ~11.361 MN. **NO QUALIFIED installation**: unknown actual RCS engine mass, exhaust velocity, plumbing/feed, mounting strength, plume effects, thermal endurance and component acceptance.
- Canonical LOOM G10 mission qualification E1 / FR-01B-R / MV-01 **deferred**: no qualified Navigator fixture/import; do not rebrand lab numerical tests as flown mission results. The reconstructed Rev7 mass/inertia card is experimental. Upstream approved mass configuration-aware inertia is still open, per `engineering/current/LOOM_2226_Wayfarer_RCS_Torch_Metric_Geometry_Priority_v0.1.md`.

## Key artifact map
In `/home/ubuntu/wayfarer_flight_lab_scratch_20261026/`:
- `full_flight_20261027/FLIGHT_TEST_REPORT.md`: complete last run (first read).
- `full_flight_20261027/regression_tests.log`, `g10_rev7.json`, `core/comparison.json`, `completion/comparison.json`, `flight_matrix.json`, `torch_g_cap.log`, `rcs_reference.log`, `hardware/comparison.json`, `nasa42.log`, `gmat_comparison.log`; per-lane exit markers.
- `FLIGHT_LAB_README.md`, `FLIGHT_LAB_RESULTS.md`: operator guide and MVP limits.
- `RCS_300KN_REPRODUCTION.md`, `CODEX_SOL_HIGH_RESULTS.md`, `CANON_METRIC_OPERATIONAL_RESULTS.md`, `HARDWARE_QUALIFICATION_RESULTS.md`: individual milestone results and explicit gaps.
- `flightlab.py`, `lab.py`, `hardware_assess.py`, `make_examples.py`, `make_completion_examples.py`, `rcs_reference_validation.py`, `lab42.py`, `run_gmat.py`, `compare_gmat_lab.py`.
- `test_flightlab.py`, `test_completion.py`, `test_canon_metric_operation.py`, `test_hardware_assess.py`, `configs/`, `experiments/`, `demo_manifest.json`, `completion_manifest.json`, `source_manifest.json`.
- Prior recovery archives `pre_codex_scratch_mvp_20261027.tar.gz`, `pre_canonical_metric_task_20261027.tar.gz`, `pre_hardware_qualification_20261027.tar.gz`.
- `NEW_CHAT_HANDOFF_20261027.md` (this handoff).
- `current_flight_lab_handoff_backup_20261027.tar.gz` (focused backup of current scripts/configurations/reports/small summary outputs; excludes large trace binaries and the pinned source tree).

## Direct read-only VM bootstrap
Use connected Remote Desktop Commander, device ID `0a7cbeb3-2e9a-42f9-9eb3-6b06217d0074`:

```bash
cd /home/ubuntu/wayfarer_flight_lab_scratch_20261026
cat NEW_CHAT_HANDOFF_20261027.md
cat full_flight_20261027/FLIGHT_TEST_REPORT.md
tail -7 full_flight_20261027/regression_tests.log
git -C source rev-parse HEAD
git -C source status --short
ls -lh current_flight_lab_handoff_backup_20261027.tar.gz
```

If tests must be rerun on user request:

```bash
cd /home/ubuntu/wayfarer_flight_lab_scratch_20261026
.venv/bin/python -m unittest -v test_flightlab test_completion test_canon_metric_operation test_hardware_assess
.venv/bin/python lab.py demo --dt .1 --manifest demo_manifest.json --out full_flight_20261027/core
.venv/bin/python lab.py demo --dt .02 --manifest completion_manifest.json --out full_flight_20261027/completion
.venv/bin/python full_flight_20261027/flight_matrix.py
.venv/bin/python rcs_reference_validation.py
.venv/bin/python hardware_assess.py --examples --out full_flight_20261027/hardware
```

**DO NOT rerun all the above reflexively.** They have already passed; inspect existing results and only rerun what the user needs. Disk was ~92% full with ~6.2GB free at handoff, so keep large traces under control and avoid duplicating `GMAT/` or `nasa42/`.

## User's likely next task
User just asked: **"What do we need to accomplish to get full certification of Wayfarer?"** This was interrupted to request this handoff. The new chat should give a bounded, prioritized **gap-to-qualification roadmap grounded in actual Rev7 card, G10, hardware HOLD reports, and authoritative GitHub**. Distinguish:
1. **Numerical flight laboratory qualification** already achieved as conditional engineering evidence;
2. **LOOM in-world spacecraft model qualification** requiring authoritative complete configuration/inertia, valid propulsion/feed/tank, thermal/structure/plume interfaces, deterministic mission fixtures E1/FR-01B-R/MV-01 and their pass/fail definitions;
3. **Actual manufactured hardware certification** cannot be proven in a fictional lab without material/component/test evidence; may be unnecessary for LOOM gameplay;
4. **Canonical metric physical propagation** intentionally parked by user: DO NOT require its discovery as a prerequisite to finish conventional Wayfarer test/certification.

Avoid a comprehensive process framework. Prefer the **single smallest missing invariant that unlocks the next realistic flight experiment**, beginning with the authoritative full ship mass+tensor and original RCS hardware/feed, then running a real Navigator mission scenario if existing code allows. If a large new engineering architecture seems required, surface the exact blocker first and stop.
