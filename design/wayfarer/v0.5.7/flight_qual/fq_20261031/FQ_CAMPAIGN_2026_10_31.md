> SUPERSEDED for FQ5/FQ8/FQ10 by the linked FQ5_FQ10_RESPONSE_LOCK_2026_10_31.md after the 5t RCS reserve and TVC throttle/cut decisions. The original failures remain historical counterfactual evidence.

# Wayfarer Step 1c G7 decision and FQ1–FQ10 conventional flight campaign

**ALL bodies. ALL sponsors. 2026–2226.** 2026-10-31.

**STATUS: NON-GOVERNING ENGINEERING · DRAFT/HOLD PR #435 · GEOMETRY REVISION CAUSED BY kT S4 MOVE · NO RENDERS, NAVIGATOR OR METRIC WORK.**

## Inputs / locked geometry

- Earlier Step1/2 hash `92905754eec2cae2ea50083803b419c830de7849ef69194e3a863c8a8efa03f1` **superseded only in this draft successor** by S4 physical relocation. This is not a byte-identical run on the former geometry.
- **New input/geometry SHA256:** `ea1fcb59f1e0a127cd48dc4e0321e7d42247e3f2e445cf89893bdefadb793266`. The one rebuilt geometry file remains unchanged by all FQ1–FQ10 runs and this report.
- S4 centre moved **Y −0.25 m, Z +0.30 m** to preserve the r=0.9–4.15m source annulus and 0.8m floor approach clearance. No nose extension, crown replacement, hatch motion or platform chamfer.
- **G7:** kT accepts a modeled 1.58m contoured couch as a *couch* rather than a 2.10m flat berth. Terraсe crawl clearance threshold is **1.20m**, actual worst bare shell clearance **1.339m**. Six station nominal seat lengths, seat annulus footprints, optimistic Pilot/Captain pane sightline upper bounds, ladder landings, 0.8m floor approaches and terrace crawl screen pass the new bounded script. Physical knees-up/4g occupant envelope, platform transfers, structure, frame/other-seat sightline obstructions remain HOLD.
- **G5 PASS-DECLARED**, **G6 PASS-DECLARED** (full radiation overlay min 40.38g/cm², open-face sensitivity min 14.78g/cm²), **G7 PASS-DECLARED** (limited plan/crawl criteria), **G12 FAIL** (no new render; intentional). Whole ship `certified=false`.

## Water RCS and power

- kT **ACCEPTS** unprotected **remass-tank water** as RCS working fluid. The separate 50t protected reserve is not drawn. Exhaust velocity is a **VARIABLE**; this FQ campaign tests **1.96km/s**. No changes to the original 32 × 25kN RCS rating, mounts, direction, lag or slew.
- Power lower bound per firing 25kN nozzle: `m_dot=F/v_e`, `P_min=m_dot × (2.6MJ/kg + 0.5v_e²)` (illustrative water boiling/conditioning + ideal jet kinetic energy, *before* losses). For **1.00km/s**, m_dot=25kg/s, **77.50MW/nozzle**; for **1.96km/s**, m_dot=12.755kg/s, **57.663MW/nozzle**. Higher ve saves both propellant and the combined ideal heat/jet power at these test points. Storage/charged-water and actual plant power unqualified.
- **OPEN kT choice:** **A** on-demand plant heat versus **B** charged hot-water store. No power is silently credited; heaters, rate limits, waste heat and recharge design unresolved.

## One FQ1–FQ10 disposition table

| FQ | Exact kT objective | Tested evidence | Outcome |
|---|---|---|---|
| FQ1 | 180° RCS flip all three axes ≤240s | Pitch/roll 60s, yaw 120s at full and half remass | **PASS numerical**; empty remass cannot manoeuvre |
| FQ2 | FQ1 with any one cluster out | All 8 original clusters disabled singly × pitch/roll/yaw = **24 variants** at full and half remass, max 120s (stricter than 240s) | **PASS numerical** in fueled states; empty is physically inoperable |
| FQ3 | RCS translation ±X/±Y/±Z | Six 0.5m/s 20s moves at full and half | **PASS numerical**; empty remass FAIL |
| FQ4 | All six torch modes, 4g and trim | ECON/CRUISE/EXPEDITE/FAST/HARD/LIMIT at full and half; direct per-step `force/mass` rather than invalid peak-force/final-mass ratio | **PASS numerical**, HARD/LIMIT limited to **4.000g**, nominal TVC trim <1°; empty remass FAIL |
| FQ5 | FQ1–FQ4 at full/half/empty | 39 case variants each at full and half, 15 representative physically inoperable empty cases; empty cluster-out variants can never fire without remass | **FAIL if required operational at empty**. PASS at full/half; expected propulsion inhibit/failure at empty. No use of protected reserve |
| FQ6 | FQ1–FQ5 at half dt, same verdicts | Same per-case screens at 0.4s vs 0.2s: **39 full +39 half +15 empty = 93 paired cases**, see JSON parity | **PASS verdict parity for those 93 tests**; empty remass FQ2 cases analytically inoperable, not separately integrated |
| FQ7 | Count RCS water from remass | Explicit tank depletion in every fired RCS test; 1.96km/s is source-mass reconstruction not historical unknown ISP | **PASS numerical propellant ledger**; feed/pump/heater OPEN |
| FQ8 | CRUISE burn down to 50t protected reserve | One continuous ~44,010s CRUISE flight, consumes ~249.9997t unprotected remass, keeps 50t protected | **PASS numerical mass reserve**, thermal/continuous hardware endurance HOLD |
| FQ9 | Burn, cut, flip, brake in one state | 60s CRUISE, 5s coast, 120s pitch flip +4s hold, 60s CRUISE, single solver state | **PASS numerical mass closure**, ledger residual ~2.3e−9kg, residual speed ~0.763m/s |
| FQ10 | Mid-burn cluster-out, stuck thruster and stuck TVC | Timed event at 60s into 120s CRUISE hold-attitude; non-governing fault harness | **FAIL as a set**: 1° stuck TVC tumbles; other two retain limited attitude gate; cluster-out case not challenging under near-zero RCS demand |

## FQ6 verdict-convergence evidence

| Initial unprotected remass | 0.4s cases | 0.2s cases | Verdict differences |
|---|---:|---:|---:|
| 250t | 39 | 39 | 0 |
| 125t | 39 | 39 | 0 |
| 0t | 15 | 15 | 0 |

Empty-case FQ2 is structurally unperformable for any cluster-out configuration because every engine draws from the empty common remass tank. This was not mislabelled as a passed numerical manoeuvre. The measured empty cases are three flips, six translations and six torch modes per timestep.

## FQ8 and FQ9 continuous fuel conservation
- FQ8 elapsed=44010.160s; consumed=249999.711kg; remass=0.289kg remaining, 50t protected unchanged; 0 depletion steps; nominal continuous torch operation requires thermal qualification.
- FQ9 one-state: remass total=1150.202205kg, state mass delta=1150.202205kg, ledger error=2.288e-09kg; final speed=0.762657m/s.

## FQ10 timed-failure evidence and hard HOLD
| Injected condition | Final attitude drift | Final angular rate | Numerical attitude check |
|---|---:|---:|---|
| cluster_out @60s | 0.0000° | 0.0000°/s | PASS |
| stuck_thruster @60s | 0.0611° | 0.0000°/s | PASS |
| stuck_tvc @60s | 22.0110° | 81.4157°/s | **FAIL** |

- The stuck-on thruster also introduces 25kN residual lateral force and extra water consumption; attitude alone is not a complete safe-operations criterion.
- The cluster-out case has almost no RCS corrective demand during the nominal auto-trimmed CRUISE burn: its PASS does **not** establish failure-tolerant manoeuvre control under load.
- A fixed 1° off-axis stuck TVC caused ~22° attitude drift and ~81°/s final rate in the idealized test, **a genuine FQ10 FAIL**. Automatic trim/nozzle steering would need fault identification, safing or abort doctrine before this can be qualified.
- The fault lab uses a pinned copy of PR433 `flightlab.py` plus the explicit `FQ10_FAULT_HARNESS.patch`. Fault models are research scenarios, not hardware failure probability/rating evidence.

## Reproduction / authority / stop
- `FQ_RESULTS_SUMMARY.json`: machine-readable mass / power / parity / fault record. `fq_matrix_*.json`: complete per-case verdicts and fuel at dt .4/.2. `FQ8.json`, `FQ9.json`, `FQ10.json` retain phase details.
- Reference numerical solver: [Rev7 laboratory PR #433](https://github.com/loom-2226/loom-2226/pull/433), original lab source SHA256 `137d13fe182578d227b444ad27ca5d55ac85475028e5e7909f53e2916a761bb2` (source checked byte-identical to the archived lab). `run_fq_matrix.py` and experimental failure harness are scratch scripts requiring the preserved lab dependencies, not a new operational framework.
- All FQ labels **FQ1–FQ10 are kT 2026-10-31 definitions**; the historical Flight System Qualification Plan Q1–Q8 was **not used** to assign these verdicts.
- New geometry file has a NEW hash due to authorized S4 change, and all results cite that new hash. No render, Navigator, Metric, hardware design, release, runtime, canon promotion or repo migration.
- **Do not merge PR #435**, which remains DRAFT/HOLD. No ship/flight physical certificate. G12 stays FAIL; FQ10 FAIL and RCS power A/B OPEN.
