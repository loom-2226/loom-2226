# Canon-constrained metric operating sequence — 27 October 2026

**Is canonical physical metric propagation complete? No.** The executable result
is a source-constrained operating-request state machine with explicit HOLD and
indeterminate terminal dynamics. It supplies no substitute metric physics.
In-world crew-rated metric operation remains canon; the absent numerical
calibrations do not imply that it cannot operate in-world.

**Run the single Wayfarer NORMAL demonstration from this scratch directory:**

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python lab.py run configs/wayfarer.json experiments/wayfarer_canonical_operation.json --dt 1 --out canon_metric_results
```

The result is `canon_metric_results/wayfarer__wayfarer_canonical_operation.json`.
Inspect `phases[0].canonical_operation`. It reports `sequence_status=VALID`,
`execution_status=HOLD`, `last_accepted_state=RELATIONAL_READY`,
`held_request=METRIC_RAMP`, and `physical_status=INDETERMINATE`.

**Code changed.** `flightlab.py` adds `canonical_metric_operation()` and routes
the existing canonical model through it, replacing its automatic envelope
stepping. The old JSON law name `canonical_envelope` remains a compatibility
selector. The function consumes `build_metric_closure()` directly and reads
G10's literal `ALLOWED` table without executing G10's unrelated simulation
imports. Source imports suppress bytecode writes. No general solver rewrite,
new dependency, certification service, or physical propagator was introduced.

`test_canon_metric_operation.py` adds eight focused tests.
`experiments/wayfarer_canonical_operation.json` is the new demonstration.
The two existing `metric_canonical*.json` experiment fixtures and their creators
(`make_examples.py`, `make_completion_examples.py`) explicitly declare the
linear illustrative profile used by their historical geometric comparisons.
The experimental translation and rotation laws retain their NON-CANON behavior.

**Exactly what executes.** The requested sequence is checked against G10:

```text
COAST / TORCH_SHUTDOWN -> RELATIONAL_READY [G10: METRIC_PREP]
-> METRIC_RAMP -> METRIC_TRANSPORT [E1: METRIC_CRUISE]
-> METRIC_COLLAPSE -> NRE_RELAXATION [E1: NRE_RELAX_REPHASE] -> COAST
```

The demonstration declares prep 5 s, transport 60 s, collapse 10 s and relaxation
20 s. Those are experiment schedule inputs, including the collapse time; none
is a calibrated physical time constant. Its acquisition ramp is the source's
NORMAL 10 s. All seven requests appear in the trace. Coast/prep requests are
accepted as structurally valid; acquisition holds, and transport/collapse/
relaxation/final coast remain `NOT_ENTERED`. Acceptance of a prep request is
not plant certification. No physical flight time advances on this HOLD.

The code rejects illegal transitions, direct mid-field Loom formation, major
torch overlap (including residual actual output), FTL metric, uncertified
beta/saturation, hard vetoes, incorrect acquisition ramp duration, and explicitly
degraded critical sectors in EXPEDITE/HARD. Missing duration inputs produce
HOLD/INDETERMINATE. Missing, stale, revoked and inapplicable gate declarations
cannot authorize acquisition. Environment, plant, power/thermal, topology,
conservation, U calibration, bank abort and RSET records all remain HOLD.
Even complete-looking PASS declarations or a user U-HYP are unverified inputs;
there is no external certificate validator or calibrated U implementation here.

**Requirements, not measured operating loads.** Canon II §5 and the copied
closure provide the first four numerical columns. The last column is ordinary
support accounting for the explicitly selected `MVP_2226` Frontier scenario:
`P_upstream = P_delivered / (0.98 * 0.96)` (E1 specification §3).

| Mode | beta | Acquisition ramp, s | Cold load, kW | Delivered electrical, MW | Upstream support, MW |
|---|---:|---:|---:|---:|---:|
| NORMAL | 0.268 | 10 | 20.0 | 3.5 | 3.720238 |
| FAST | 0.437 | 12 | 38.1 | 6.7 | 7.121599 |
| EXPEDITE | 0.519 | 15 | 63.5 | 11.2 | 11.904762 |
| HARD | 0.595 | 30 | 136.0 | 23.9 | 25.403912 |

The output includes all four cards, source filenames/hashes, Frontier producer
version/hash, distribution losses and conditional equivalent areas. Distribution
area is not automatically added to canon area or treated as installed geometry.
Declared available capacities receive only `DECLARED_SUFFICIENT`, `FAIL` or
`UNKNOWN` comparisons; they do not certify hardware. Environmental correction,
standby/switching/wake loads, duty profile, bank abort profile, RSET and total
energy accounting remain UNKNOWN. The new example computes no path or energy.
Historical explicit linear profiles retain only conditional geometric path
estimates, with null energy; they are not trajectories or finite ledgers.

The full pre-metric snapshot retains position, velocity, mass, remass inventory,
attitude/rate, inertia, actuator state, and original initial inputs including
declared frame/epoch. Post-metric position, ordinary velocity, mass/remass,
attitude/rate, matching delta-v, ordinary energy and momentum are null. The
known snapshot is not relabeled as an arrival. Conventional flight and switching
to another metric law are both blocked after this unresolved request.

**Validation.** Baseline: all 35 pre-existing tests passed. Final command:

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest -v test_flightlab test_completion test_canon_metric_operation
```

Final result: **43 tests passed: 35 retained + 8 focused**, recorded in
`canon_metric_final_tests.log`. Coverage includes valid source sequences across
all four modes; illegal transitions/torch overlap; missing timing/calibration;
stale/wrong-lot/revoked/boolean/PASS/U-HYP declarations; FTL/saturation; missing
arrival output; retained conventional prestate; and prohibited post-metric flight.

Separate existing CLI regressions, both at 0.02 s, reproduced:

| Existing case | Target attitude error | Target angular rate | Numerical criteria |
|---|---:|---:|---|
| Original fixed 300 kN, `reversal10` | 0.046294278° | 0.037623799°/s | pass |
| Added gimbals, `gimbal12` | 0.028993430° | 0.018693259°/s | pass |

Their records are in `canon_metric_regressions/`, with command output in
`canon_metric_fixed300.log` and `canon_metric_gimbal.log`. System fuel status
remains indeterminate because these historical installations have unknown RCS
feed/consumption. The retained fixed-300 test also checks its 4 s post-hold case.

**Exactly what remains unclosed, and required authority.** Canon II §7.1 requires

```text
Z_B^(nat,M) = pi_Z U^M_gamma(Z_A, R_A, E_gamma)
Delta Z_match = Z_B^desired - Z_B^(nat,M)
```

The missing item is the calibrated path-dependent function `U^M_gamma`, with
ordinary-state response and an applicable external calibration record. The beta
card, G10 transition table, JPL/SPICE geometry, and geometric ramp estimates do
not supply this function. Arrival matching additionally needs a destination
frame and terminal solver. Canon II §7.3 requires finite ordinary, relational/
wake, bank/reactor, radiation/heat and environment exchanges consistent with
`nabla_mu T_total^(mu nu) = 0`; no validated finite exchange law/ledger is supplied.
Canon II §6.3's `P_corr = F_P(...)` still lacks calibrated environmental
power/thermal response. Applicable signed, current, non-revoked ship/array/lot/
mode/ramp records must meet Canon II §10, with topology/failure applicability
under §11. No user declaration supplies that authority.

The copied `source/src/wayfarer_e1_metric_frontier_closure.py:build_metric_closure`
explicitly retains `PATH_DEPENDENT_ORDINARY_STATE_PROPAGATOR_CALIBRATION`,
`METRIC_ENVIRONMENT_CORRECTION_POWER_AND_THERMAL_CALIBRATION`,
`WAKE_AND_FINITE_CONSERVATION_LEDGER_VALIDATION`,
`FULL_TIME_DEPENDENT_4D_FINITE_RSET_BENCHMARK`, and
`NODE_TOPOLOGY_FAILURE_AND_ENVIRONMENTAL_CERTIFICATION_CALIBRATION` as open.

Authority pointers: `source/canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md`
§§5–7, 10–11;
`source/engineering/experience_one/WAYFARER_E1_METRIC_CANON_AND_GLB_INTEGRATION_SPEC_v0.1.md`
§§3–5; the closure above;
`source/src/wayfarer_2226_frontier_accountant.py` scenario/producer accounting;
`source/design/wayfarer/v0.5.7/g10/g10_flight_dynamics.py:ALLOWED, metric_tests`.

All 12 recorded authority-file hashes in `canon_metric_source_hashes.json`
remain unchanged; all eight original `source_manifest.json` pins still match.
All writes were confined to this scratch workspace. No canon, copied source,
original study, runtime project, live branch, GitHub object or installation was
changed. Work stops at the requested operational sequence and focused checks.
