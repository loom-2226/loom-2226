# Physical hardware qualification assessment — scratch Wayfarer lab

27 October 2026. **NON-CANON engineering experiment. All hardware decisions are
HOLD; no hardware certificate is issued. Neither the fixed 300 kN installation
nor the eight-added-gimbal candidate becomes physically hardware-qualified.**
PASS and FAIL below apply to individual numerical requirements within their
stated evidence scope. A simulated force is a modeled demand, not a force measured
on real hardware. Physical evidence absent from the copied sources remains absent.

The runnable implementation is [hardware_assess.py](hardware_assess.py). It reads
the existing configuration and experiment, invokes `lab.save_run` or consumes an
existing run, and assesses the realized per-step propulsion trace. It has no
integrator, certification service, new dependency or authority-promotion path.

**Run everything with one command from this scratch directory:**

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python hardware_assess.py --examples --out hardware_results
```

This runs the four required installations plus three useful auxiliary cases:
the original 10 s failure, neutral-start gimbals and the existing 120 s CRUISE
torch burn. Raw lab results, telemetry and full-step traces go into
`hardware_results/runs/`. New assessment JSONs go into `hardware_results/`.
Existing spacecraft qualification records are preserved.

Individual and trace-reuse commands:

```bash
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
.venv/bin/python hardware_assess.py configs/reference_baseline25_40s.json experiments/reference_baseline25_40s.json --dt .02 --out hardware_results
.venv/bin/python hardware_assess.py configs/reference_fixed300_pitch.json experiments/reference_fixed300_pitch.json --dt .02 --out hardware_results
.venv/bin/python hardware_assess.py configs/wayfarer_gimbal_reference.json experiments/gimbal12.json --dt .02 --out hardware_results
.venv/bin/python hardware_assess.py configs/wayfarer_gimbal_cold.json experiments/gimbal12.json --dt .02 --out hardware_results
.venv/bin/python hardware_assess.py hardware/fixtures/scout_hardware.json experiments/scout_gimbal_turn.json --assumptions hardware/fixtures/scout_ratings.json --dt .02 --out hardware_results
.venv/bin/python hardware_assess.py configs/wayfarer.json experiments/burn120.json --dt .02 --out hardware_results
.venv/bin/python hardware_assess.py configs/reference_fixed300_pitch.json experiments/reference_fixed300_pitch.json --result hardware_results/runs/reference_fixed300_pitch__reference_fixed300_pitch.json --out hardware_results
```

The last command performs no flight integration. Input hashes must match the
run. Older traces lacking per-engine evidence are rejected with a rerun request;
missing fields are not reconstructed as zero. Trace continuity, wrench closure
and the aggregate RCS/torch impulse ledger are checked. The reuse path was exercised
in [reuse_trace.log](hardware_results/reuse_trace.log).

**Measured comparison, 0.02 s solver steps.** All turns are 180° pitch, with a
4 s post-target observation interval. Terminal limits are error ≤0.25° and rate
≤0.05°/s. Loads include the maneuver and post-hold. Common-mount peaks combine
co-located engines using realized vectors and actuator endpoints; they are not
single-nozzle ratings or bracket stresses.

| Installation | Target | Error at target | Rate at target | Final sustained gate entry | Largest common-mount demand | Numerical target | Hardware |
|---|---:|---:|---:|---:|---:|---|---|
| Original: 32 fixed × 25 kN | 40 s | 0.001013288° | 0.000168277°/s | 40.00 s | 25,000.059192 N | PASS | HOLD |
| Fixed: original 24 non-axial × 300 kN + eight axial × 25 kN | 10 s | 0.046294278° | 0.037623799°/s | **10.62 s** | 300,001.434235 N | PASS | HOLD |
| Added gimbals: original 32 × 25 kN + eight × 300 kN, prepositioned | 12 s | 0.028993430° | 0.018693259°/s | 12.00 s | 324,631.663066 N | PASS | HOLD |
| HYPOTHETICAL Scout: 32 × 4 kN + eight × 12 kN gimbals | 20 s | 0.007286577° | 0.002551258°/s | 20.00 s | 6,654.090570 N | PASS; other supplied ratings FAIL | HOLD |

Auxiliary original 25 kN at 10 s: **FAIL**, error 135.072711422°, rate
9.117067961°/s; no final gate by 14 s. Its peak common-mount force is
38,306.485442 N. A source G3 idealized ~35 s slew and a successful 40 s
closed-loop experiment do not imply a 10 s capability.

Auxiliary cold-start gimbals at 12 s: error 0.028993430°, rate 0.018693259°/s,
final gate 12.00 s; peak resultant 7,066.949098 N. Prepositioned peak resultant
is 7,066.948853 N. The first steering histories differ even though these terminal
states essentially agree. Initial angles, actual angles/directions and steering
rates are retained per nozzle. Prepositioning is explicitly excluded in the
reference fixture; the neutral-start run includes all in-run steering time.
The configured 25° initial excursion and 30°/s rate imply a setup lower bound
of 0.833333 s before lag/settling, not a certified prepositioning time.

The machine-readable [comparison.json](hardware_results/comparison.json) and
generated [comparison.md](hardware_results/comparison.md) include all seven runs.
Representative complete outputs:

- [Original 25 kN](hardware_results/reference_baseline25_40s__reference_baseline25_40s.assessment.json)
- [Fixed 300 kN](hardware_results/reference_fixed300_pitch__reference_fixed300_pitch.assessment.json)
- [Added gimbals](hardware_results/wayfarer_gimbal_reference__gimbal12.assessment.json)
- [Cold-start gimbals](hardware_results/wayfarer_gimbal_cold__gimbal12.assessment.json)
- [Declared Scout](hardware_results/scout_hardware__scout_gimbal_turn.assessment.json)
- [CRUISE torch](hardware_results/wayfarer__burn120.assessment.json)

Each requirement contains `status`, `demand`, `capacity`, `evidence`, `scope`,
`explanation`, and a capacity-minus-demand margin when both quantities are
numeric. Exact per-engine commands, actual step-average and endpoint peaks,
impulses, exhaust speeds, tanks, masses and gimbal kinematics are in `installation`.
The plume row expresses signed penetration; negative demand means separation.

**Propulsion and dynamics within numerical scope.** Original/fixed/gimballed
peak nozzle commands reach 25,000 / 300,000 / 300,000 N respectively; realized
endpoint peaks agree to floating-point precision. Configured force limits PASS.
The two gimbal axes each stay within ±25° and reach 30°/s: these are independent
mechanical angles, not a 25° circular cone. These kinematic comparisons PASS.
Physical rated thrust, steering torque, power, loaded rate/lag and endurance
remain HOLD. Inventory counts include the unchanged eight axial nozzles.

| Maneuver | Allocation-limited steps | Command-slew-limited steps | Steps with at least one saturated realized nozzle | Gimbal-limited steps |
|---|---:|---:|---:|---:|
| Baseline 40 s | 0 | 0 | 1,325 | 0 |
| Fixed 300 kN, 10 s + hold | 0 | 16 | 163 | 0 |
| Gimbals prepositioned, 12 s + hold | 0 | 7 | 289 | 475 |
| Gimbals cold, 12 s + hold | 0 | 7 | 289 | 702 |

These counts are observations, not invented zero-saturation requirements. A
target-time PASS is distinct from sustained settling: the fixed candidate
leaves/re-enters its terminal gate after 10 s; its final observed entry is 10.62 s
and the remaining sustained observation is 3.38 s, ending at 14 s. No indefinite
stability claim follows from that finite trace.

**Mount loads and structural limits.** The force vector is the load the engine
applies to the vehicle at the configured point; the mount's reaction on the
engine has the opposite sign. The JSON records peak vectors and timestamps,
common-point resultants and moments transported to the instantaneous CG.
Those transported moments are not local bracket bending moments.

| RCS mount | Original 40 s, N | Fixed 300 kN, N | Added gimbals prepositioned, N |
|---|---:|---:|---:|
| F+Y | 25,000.000000 | 300,000.000000 | 306,738.909834 |
| F+Z | 25,000.000000 | 300,000.128795 | 300,029.774418 |
| F-Y | 25,000.000000 | 299,999.991870 | 308,501.932727 |
| F-Z | 2,994.555443 | 300,000.000000 | 300,004.833672 |
| A+Y | 25,000.000000 | 300,000.320886 | 302,550.851890 |
| A+Z | 25,000.059192 | 300,001.434235 | 300,000.000000 |
| A-Y | 16,252.014302 | 300,000.000000 | 311,256.660087 |
| A-Z | 25,000.009582 | 300,000.306782 | 324,631.663066 |

| Run | Peak average net force | Peak average moment about CG | Scalar force bound | Scalar moment bound about CG |
|---|---:|---:|---:|---:|
| Original 40 s | 0.026012 N | 2.172830955 MN·m | 0.106019381 MN | 2.209927034 MN·m |
| Fixed 300 kN | 0.074345 N | 34.791509113 MN·m | 1.697606800 MN | 35.379948840 MN·m |
| Added gimbals prepositioned | 7,066.948853 N | 24.155394342 MN·m | 1.861572383 MN | 38.794818036 MN·m |

Bounds use sums of individual force magnitudes and `|r-CG|*|F|` at each step.
They bound the recorded realized loads; they do not establish ignition shock,
flexible response, valve shock, fatigue or sub-step transient peaks. All Wayfarer
mount capacity margins HOLD: no local bracket/fastener/reinforcement/load-path,
temperature-dependent allowable, dynamic factor or fatigue envelope is supplied.
The Rev7 G5 longeron 250 MPa design stress is not applied to nozzle brackets.

**Mass and propellant.** All three Wayfarer comparisons retain Rev7 S1
1,167,680 kg and the full S1 tensor, reconstructed from S4 plus the declared
250,000 kg usable tank. `mass_response` publishes full initial/final tensors,
CGs, the response to explicitly installed engine masses and the depletion
response. Baseline source geometry allocates 16,941.604038 kg to the eight RCS
cluster assemblies collectively. That does not supply individual engine masses,
uprated engine mass, added gimbal mass, reinforcement or feed mass.

Wayfarer RCS fuel source and exhaust speed remain unspecified. Thus **total
consumption and peak total flow are null**, with HOLD on engine/feed availability.
Zero modeled tank loss is explicitly a frozen-consumption assumption, not zero
physical consumption. Available impulses over maneuver plus post-hold are:

- Original 40 s: 2,756,388.232568 N·s.
- Fixed 300 kN: 11,065,546.787499 N·s.
- Added gimbals prepositioned: 13,187,907.287311 N·s.
- Added gimbals cold: 13,190,148.262553 N·s.

The **50,000 kg protected water remains in base mass**, excluded from propulsion
tanks and from every RCS sensitivity here. The configuration exclusion PASS does
not authorize an unknown RCS feed. The evaluator detects an attempted protected
tank assignment/over-allocation as FAIL. The separate Q7 optimizer reserve is not
another tank. The geometry's 46,169.2 kg engineering reserve is reported without
assigning it to unknown engine/feed hardware or treating it as a mass margin.

The current recovered RCS priority explicitly says complete Wayfarer inertia is
`WAYFARER_INERTIA_OPEN_NOT_QUALIFIED`. It is separate from the Rev7 conditional
tensor and separate from the historical 32-nozzle/40-nozzle experiments. No
current rotational authority is inferred from a successful Rev7 replay.

**Plume screen.** No Wayfarer plume half-angle, finite plume length, exhaust
composition, nozzle exit/apex location, selected deployment state or certified
clearance is supplied. The screen therefore HOLDs before doing an unsupported
cone calculation. `wayfarer_envelopes()` can construct conservative source-based
hull/torch cylinder covers and strake/hot-fin panel circumspheres for an explicitly
selected stowed/torch/metric deployment. It uses the Rev7 maximum 4.5 m hull
radius, actual nozzle application points, shield/reactor/nozzle geometry and
source panel positions/spans. These envelopes exclude detailed doors, docking
equipment, exposed node faces and other small equipment; positive coarse
clearance would still leave full installation clearance HOLD.

With optional declared cone inputs the evaluator tests the finite solid cone
against the sphere exclusion envelopes, including its end caps. Exhaust points
opposite realized thrust, and all firing directions in the trace are screened.
An envelope intersection FAIL rejects that stated coarse assumption; it is not
a finite-plume temperature or surface-impingement calculation. Unit tests exercise
clearance PASS, an off-axis cone hit missed by the centerline, and finite end caps.
Rev7's axial-plume clearance remains explicitly unmodeled/AWAITING.

**Fully declared NON-CANON Scout fixture.**
[scout_hardware.json](hardware/fixtures/scout_hardware.json) declares every engine
mass and intrinsic tensor: 32 fixed engines at 4 kg, eight gimbals at 12 kg and
one torch at 80 kg, adding 304 kg to a 90 t cylinder base that explicitly excludes
those engines. RCS uses a separate 200 kg tank at Isp 3,000 s; the torch's 10 t
tank and 500,000 m/s exhaust speed remain separate.
[scout_ratings.json](hardware/fixtures/scout_ratings.json) declares hypothetical
thrust, flow, mount-force, dynamic-factor and thermal values and coarse geometry.
They are synthetic inputs for arithmetic, not measured temperatures or suppliers.

The run consumes **5.945432373 kg**, peak total flow bound **0.458049875 kg/s**;
mass changes from 100,504 to 100,498.054567627 kg. CG changes from
`[0.006941017, 0.002012258, -0.000111438]` m to
`[0.006882268, 0.001953218, -0.000111445]` m, with full off-diagonal tensor
changes recorded. The mass ledger closes. RCS flow is below its declared 2 kg/s
feed rating by 1.541950125 kg/s: numerical PASS. Nominal per-mount 25 kN ratings
also give positive margins where supplied.

The deliberately insufficient inputs produce three inspectable FAILs:

- Fore +Y common mount: 96.729838 N realized peak × declared factor 1.5 =
  **145.094757 N demand versus 100 N rating**, margin −45.094757 N.
- First added gimbal: **700 K synthetic peak versus 650 K rating**, margin −50 K.
  The declared 5 kW rejection demand versus 10 kW capacity separately PASSes
  with a 5 kW margin. No thermal evolution is inferred from thrust.
- Coarse 12 m × 2 m-radius hull-cylinder cover: minimum signed clearance
  **−0.789636217 m**, witnessed at `A+Z_inward_extra_gimbal`, 2.28 s. This exposes
  the inherited aft mounts inside the stated coarse hull envelope. It rejects
  the fixture geometry assumption without certifying actual impingement heat.

Even fully supplied numerical inputs leave physical inertia/flux/slosh,
loaded actuator qualification, structural integration/fatigue, full plume
clearance, thermal endurance and independent acceptance evidence HOLD. The
fixture yields 76 PASS, three FAIL and six HOLD rows, with overall hardware HOLD.

**Torch sourced numerical comparisons.** The auxiliary S1 CRUISE burn runs for
120 s. Six Rev7 mode cards and source-installed force envelopes are retained in
the output; the example exercises CRUISE. Actual force is **11,361,000 N**,
limited by **11.361 TW**, flow **5.6805 kg/s**, remass **681.66 kg**, and integrated
jet energy **1.36332×10¹⁵ J**. No total fuel-energy/endurance capacity is supplied,
so the integrated-energy capacity comparison HOLDs.

| Requirement | Demand | Sourced capacity | Result and scope |
|---|---:|---:|---|
| Jet power | 11.361 TW | 11.361 TW | PASS, Rev7 operating ceiling; zero power headroom |
| Crew acceleration | 0.992717330 g | 4 g | PASS, scalar sustained doctrine |
| Structural acceleration | 0.992717330 g | 5 g | PASS, scalar design envelope; no local stress inference |
| Actual ideal TVC | 0.322690177° | 1° | PASS, declared instantaneous-trim model |
| Trim plus assumed error | 0.822690177° | 1° | PASS, includes source 0.5° assumed disturbance |
| Hot structure heat | 1.399525516 GW | 1.489716519 GW | PASS, legacy declared heat package only |
| Strake rejection, cryo + rounded 0.37 MW habitat | 47.924563354 MW | 73.019454487 MW | PASS, legacy declared heat package only |
| Reactor aft-face light flux | 5.026192207 MW/m² | 10 MW/m² | PASS, legacy declared heat package only |

Thermal rows read the existing G4 design budget, not a new heat partition or
temperature solver. They require 28 m hot fins at 1,750 K and 4 m strakes at
1,300 K; deployment, actual finite-temperature materials, cooling integration
and endurance are unverified. They do not imply that the RCS candidates have
known heat rejection, erosion or nozzle-wall temperatures. TVC rate/loaded
bandwidth is not rated by the source's assumed 1° authority; it remains HOLD.
The RCS-only maneuvers explicitly show torch loads as unexercised/HOLD.

**Exact evidence preventing Wayfarer hardware qualification.**

| Required physical evidence | Original 25 kN | Fixed 24 × 300 kN + eight × 25 kN | Original 32 + eight added gimbals |
|---|---|---|---|
| Engine thrust/duty, installation mass/CG/tensors, valves and acceptance tests | Individual engines/cluster constituents not qualified | New uprated thrusters and installation/line/reinforcement masses absent | Added engines, gimbals, attachments, actuators and mass properties absent |
| Exhaust speed/Isp, fuel identity, inlet state, selected feed/pump/collector/header, transient pressure/flow and tanks | Unprovided | Unprovided at uprated duty | Unprovided, including added feeds |
| Complete current configuration-aware vehicle inertia | OPEN; Rev7 tensor conditional | OPEN; upgrade response absent | OPEN; added-hardware response absent |
| Mount/load-path/fastener strength, dynamic factor, thermal allowables, reinforcement and fatigue | No local ratings | ~300 kN common-point demand, no upgraded local rating | ~325 kN combined common-point demand, no added-mount or loaded steering rating |
| Finite plume/nozzle exit, composition, divergence, deployment/door geometry, impingement/clearance test | Axial plume clearance specifically unmodeled | No qualified higher-thrust plume | No clearance across steered directions or shared mounts |
| Nozzle/structure temperatures, cooling, erosion, cycling and endurance | Absent | Absent for hypothetical upgrade | Absent for added engines/gimbals |
| Torch physical heat/feed/TVC/structure verification | Conditional design budgets and declared TVC only | Same unresolved installed torch | Same unresolved installed torch |
| Independent supplier/material/assembly/installed-duty acceptance evidence | Absent | Absent | Absent |

This is the stopping point for each absent physical quantity. The assessor does
not invent feed hardware, material strengths, exhaust coefficients, cooling
loads, unknown masses or vendor test results to clear a HOLD.

**Authority and legacy scope.** Read together:

- [Rev7 SPEC](source/design/wayfarer/v0.5.7/SPEC.md),
  [card](source/design/wayfarer/v0.5.7/out/wayfarer_v05_card.json),
  [geometry](source/design/wayfarer/v0.5.7/out/wayfarer_v05_geometry.json), and
  [legacy report](source/design/wayfarer/v0.5.7/out/certification_report.json):
  source mass/geometry, modes, G3 dynamics, G4 heat and G5 global structure.
  The report is controlling where SPEC prose differs. Its `certified=false`
  and G4/G6/G10 `PASS-DECLARED` statuses are preserved separately, not promoted.
  All AWAITING declarations, including `rcs_axial_plumes` and
  `g10_burn_coasts`, are listed in each Wayfarer assessment's `legacy` section.
- [Recovered geometry priority](source/engineering/current/LOOM_2226_Wayfarer_RCS_Torch_Metric_Geometry_Priority_v0.1.md):
  recovered hardpoints are `ENGINEERING_CANDIDATE_NON_CANON`, feed architecture
  is NOT SELECTED, complete inertia is OPEN. This record is not merged into Rev7.
- [Working torch cards](source/src/wayfarer_torch_mode_cards.py) and
  [Canon II](source/canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md)
  §§13–14: working-fluid/torch architecture and torch/high-Metric exclusivity.
- [RCS reproduction](RCS_300KN_REPRODUCTION.md),
  [prior Sol results](CODEX_SOL_HIGH_RESULTS.md), and
  [canonical metric results](CANON_METRIC_OPERATIONAL_RESULTS.md): existing
  simulated performance and deliberate metric physical-propagation HOLD.

**Verification and changes.**

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest -v test_flightlab test_completion test_canon_metric_operation test_hardware_assess
```

**55 tests PASS: all 43 existing tests plus 12 focused hardware tests.** Evidence:
[final_tests.log](hardware_results/final_tests.log). Tests cover unknown capacity
HOLD, positive numeric margin PASS, insufficient rating FAIL, unknown exhaust
nulls, depleted feed, protected-water exclusion and attempted-use failure, full
mass/tensor response, direct declared thermal comparisons, finite cone screening,
missing/stale input traces and read-only assessment. Existing fixed/gimbal
regressions remain in the suite.

[reference_matches.json](hardware_results/reference_matches.json) compares new
baseline-40, baseline-10, fixed-300, prepositioned-gimbal and cold-gimbal target
metrics and gate entries against the retained prior outputs. Every compared
value is identical, with unchanged numerical pass/fail. The flight solver change
only exposes already realized contributions, command/endpoint values, step
length and pre-step mass/CG in `rcs_trace`; exactly idle contributions are omitted.
No controller, allocator, integrator, mass law, canonical metric operation or
physical propagation law changed.

All 2,225 copied source files are byte-identical to the pre-task snapshot:
[source_integrity.json](hardware_results/source_integrity.json) and
[source_hashes_before.json](hardware_results/source_hashes_before.json). New
assessment evidence includes hashes of inputs, traces and implementation files.
All writes stayed inside this scratch workspace. No original workspace,
copied source, existing qualification result, runtime, GitHub or canon was changed.

The evidence-backed numerical assessment is executable and complete for the
requested cases. Genuine physical qualification remains **HOLD**, for the exact
missing evidence above; neither stronger Wayfarer candidate is hardware-qualified.
