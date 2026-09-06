# LOOM 2226 — CANON II: ENGINEERING, SHIPS & OPERATIONS
## Corrected Consolidated Baseline v2.4

**Status:** GOVERNING TECHNICAL / OPERATING CANON  
**Freeze:** 22 August 2026 — post-MV mechanics + metric environmental-certification architecture freeze  
**Institutional amendment:** 24 August 2026 — packet/interdiction/combat/auxiliary operating doctrine; no machine-constant change

# 0. LLM quick authority

Use this volume for any question that can change a ship's physical or operational state.

```text
CERTIFIED MACHINE CONSTANTS      this file
METRIC ENVIRONMENT ARCHITECTURE  this file / MEC-ARCH 1.0
MASS / REMASS STATE              this file
NAV / EPH PROVENANCE             this file + Core Mechanics v0.5
HUD FAMILY                       Core Mechanics v0.5 + HUD Standard v0.3
WORLD / PORT CONTEXT             CANON I v2.4 / Atlas v3.2
HIDDEN TRUTH / LOOM GRAPH        CANON III v2.4
```

Never use a retired flight result as a machine constant. Exact route time, terminal Δv, remass, metric acquisition surface and traffic delay are solver/model outputs unless this volume explicitly locks them.

# 1. Authority and dependency

Foundational physics: **Conceptual Physics Engineering MVP v1.3**.  
Promoted Loom implementation: **WP-1–WP-5**.  
Promoted metric implementation: **WP-8–WP-11**.  
Reference ship ledger: **Inherited Courier Integrated Propulsion Baseline v1.1**.  
World-history provenance: **Xenoarchaeology, ʻOumuamua & Terminal Mobilization Canon v1.0**.  
Post-MV operations: **Mechanics Canon Promotion Patch v1.0**, merged here.  
Metric environmental architecture: **MEC-ARCH v1.0**, merged here.

The earlier phase-walk Metric Engineering MVP is rejected. Legacy 32 kg Mc sizing, 64 × 0.5 kg cells, 90 t Loom hardware, 60 t standalone metric package, PJ-scale banks, area×velocity² scaling and the protected 0.03/0.04/0.05c card are non-governing.

# 2. Foundational engineering rule

Physics generates engineering. Engineering may refine calibration, hardware and certification without adding a third miracle.

M1/M2, conservation, identity/domain continuity, duplication prohibition, causal-sector limits and hard-kill criteria remain foundational.

The three propulsion regimes remain physically distinct:

- **TORCH** — ordinary momentum exchange;
- **METRIC** — continuous subluminal relational/metric transport;
- **LOOM** — discontinuous interstellar relational re-embedding.

No drive silently performs another drive's conservation work.

# 3. Unified relational propulsion plant

| Quantity | Governing value |
|---|---:|
| Plant mass | **~88 t** |
| Mc-299m | **10.0 kg** |
| Active tiles | **100 × 100 g** |
| Nodes | **208 distributed boundary/metric nodes** |
| Shared bank | **2 GJ reversible field bank** |
| Cryoplant | **150 kW-class, 20 K** |
| High-drive reject | **900 K interface** |

Metric and Loom use the same Mc/NRE order parameter and distributed hardware:

```text
METRIC COLLAPSE
→ NRE RELAX / REPHASE
→ LOOM FORMATION
```

No direct mid-field metric-to-Loom switch is crew-rated.

## 3.1 Mc-299m strategic-material baseline

Mc-299m is **reusable strategic machine capital, not fuel**.

| Quantity | Governing calibration |
|---|---:|
| Primary flight-grade production | **~1,000 kg/year** |
| Cumulative historical flight-grade production | **~8.7 t** |
| Normal recovered / requalified return flow | **~150–250 kg/year** |
| Working central effective annual serviceable flow | **~1.2 t/year** |

“Flight-grade” means material that has passed purification, isomer/state qualification, materials integration and certification. Raw synthesis is not equivalent to serviceable ship stock.

Qualified 2226 demand **modestly exceeds normal primary-plus-recovered supply at the margin**. Shortage normally appears as commissioning queues, premiums, reservation/export controls, competition for recovered arrays, retrofit deferral and pressure to reduce Mc inventory per unit transport.

Production/highest-end relational fabrication is concentrated in **Earth–Moon space and selected Mars/Mercury orbital high-end fabrication complexes**.

Still open: exact plants; producer/jurisdiction shares; annual fleet registry; exact synthesis pathway; long-term aging/daughter behavior; year-specific allocation shares.

## 3.2 1I forensic ancestry and non-equivalence

1I material forensics narrowed the human search space toward a dominant parent neighborhood near **Z≈115, A≈299**. It did not provide intact usable alien Mc, a complete synthesis route, an intact Builder NRE array, proof of pure Mc-299m, or proof that Builder hardware performed the same function as human M2 engineering.

> **LOCKED NON-EQUIVALENCE:** Human Mc-299m/NRE is a human first-generation M2 engineering solution whose search space was materially narrowed by 1I forensic evidence. It is not canonically identical to Builder active material, host structure or function.

Alien-origin material never substitutes automatically for human flight-grade lot qualification.

# 4. Metric constitutive law and metrology

\[
\beta_{machine}=\chi_M\frac{\mathcal J_M}{N_{eff}}
\]

\(\chi_M\) is measured, not derived from the historical ship.

- reference production target: \(\chi_M=1.00\);
- lot acceptance: \(0.95\le\chi_M\le1.05\);
- ship-specific fitted uncertainty: \(\sigma_\chi\le0.01\).

If nonlinearity exceeds tolerance, use a measured table/function rather than forcing a constant coefficient.

# 5. Certified clean-environment metric card

| Mode | Certified transport | Ramp | Cold load | Cryo electrical | 900 K radiator equivalent |
|---|---:|---:|---:|---:|---:|
| NORMAL | **0.268c** | 10 s | 20.0 kW | 3.5 MW | 106 m² |
| FAST | **0.437c** | 12 s | 38.1 kW | 6.7 MW | 202 m² |
| EXPEDITE | **0.519c** | 15 s | 63.5 kW | 11.2 MW | 336 m² |
| HARD | **0.595c** | 30 s | 136.0 kW | 23.9 MW | 719 m² |

Array saturation response ~0.678c is not certified. **FTL metric = BLACK / hard kill.**

Reference field: axial Alcubierre transport field with long forward massive/null-geodesic shaping lobe. Reference wall: 6 m, \(C^3\) smooth.

The speed card is a calibrated envelope of one architecture/material/array/certification family; it is not a universal microscopic property of Mc-299m.

# 6. Metric environmental-certification architecture — GOVERNING

## 6.1 Core rule

Metric certification is **not a universal body-centered stand-off radius**.

The physical chain is:

```text
actual local geometry / radiation / matter environment
        ↓
required distributed-node correction
        ↓
control utilization + correction work
        ↓
thermal / cryogenic burden
        ↓
certification channels + hard vetoes + uncertainty confidence
        ↓
permitted ramp profile
        ↓
metric ramp displacement
```

Roadstead, traffic-control, port and physical-certification geometry are separate.

## 6.2 Foundational node-control quantity

For node \(i\), environmental authority/phase corrections are \(\delta\mathcal J_i^{env}\) and \(\delta\phi_i^{env}\).

\[
u_i=
\max\left(
\frac{|\delta\mathcal J_i^{env}|}{\mathcal J_{i,reserve}},
\frac{|\delta\phi_i^{env}|}{\phi_{i,cert}}
\right)
\]

\[
C_{ctrl}^{node}=\max_i u_i
\]

Clustered weakness is handled through a topology-sensitive penalty:

\[
C_{ctrl}=\max(C_{ctrl}^{node},C_{topo}).
\]

A reduced route-planning scalar may be fitted to this node-level model, but may not replace it as foundational physics. Any simple \(L^2\) ship-size law remains a candidate fit, not canon.

## 6.3 Control-to-thermal coupling

Environmental compensation requires correction work:

\[
P_{corr}=F_P(\{\delta\mathcal J_i\},\{\delta\phi_i\},\{\dot{\delta\phi}_i\},\beta,\dot\beta).
\]

That work contributes to node heat, switching loss, controller power and cryogenic load. Therefore control and thermal channels are causally coupled before the final decision layer is evaluated.

```text
ENVIRONMENT
→ NODE CORRECTION
→ CONTROL UTILIZATION
→ CORRECTION POWER
→ THERMAL / CRYO LOAD
```

## 6.4 Certification state

The governing architecture tracks at least:

\[
\mathbf C_M=(
C_{ctrl},
C_{tidal},
C_{grad},
C_{null},
C_{matter},
C_{wake},
C_{therm},
C_{RSET}
).
\]

`C_grad` keeps curvature-gradient sensitivity explicit until calibration demonstrates it is wholly absorbed by node control.

The deterministic physical-limit layer is:

\[
C_M=\max(\mathbf C_M)<1
\]

**only after causal coupling has been propagated**.

A separate confidence layer accounts for covariance/model uncertainty. Do not replace the deterministic limit with a single probabilistic soup.

Operational hard vetoes remain possible even when the scalar maximum is below 1.

## 6.5 Required environment solution

Certification may require:

- actual multi-body tidal tensor / curvature environment;
- curvature gradients along the ramp;
- massive-particle trajectories in the commanded geometry;
- null geodesics, caustics and conjugate points;
- wave optics near caustics;
- bright-source photon geometry;
- dust/plasma/matter environment;
- current array health, phase error and node topology;
- thermal/cryo closure;
- wake/conservation ledger;
- RSET status;
- valid calibrated state-propagator record.

Multi-body certification volumes may be anisotropic and time varying.

Missed real-time certification deadline:

```text
HOLD → DERATE / REORIENT → COLLAPSE
```

not “continue and hope.”

# 7. Metric ordinary-state propagation and conservation

## 7.1 Loom and Metric maps are different

Mandatory notation:

```text
LOOM:    T_AB
METRIC:  U^M_gamma
```

`T_AB` is the discontinuous Loom natural transport map.

`U^M_gamma` is the empirical, path-dependent **continuous metric ordinary-state propagator**. JPL/SPICE does not supply it. GR supplies geometry/frames; M2 engineering supplies the fictional constitutive response that must be measured/calibrated in-universe.

For a zero-torch / zero-external-assist metric route, the natural metric output is:

\[
Z_B^{nat,M}=\pi_Z\,\mathcal U^M_\gamma(Z_A,R_A,\mathcal E_\gamma).
\]

Desired arrival state remains separate:

\[
\Delta Z_{match}=Z_B^{desired}-Z_B^{nat,M}
\]

in an explicitly stated destination frame.

Metric cannot silently erase this mismatch. Torch, tugs, infrastructure or another explicit exchange must pay it.

## 7.2 Frame discipline

A local three-velocity without a frame is incomplete.

The ship may carry an interior orthonormal tetrad, with Fermi–Walker transport used as the orientation bookkeeping convention absent commanded rotation. That convention is **not** the momentum-transport law.

Report ordinary velocity as, for example:

```text
V/ICRF
V/MARS-CENTERED
V/PHOBOS-REL
```

and report metric coordinate transport separately.

## 7.3 Conservation firewall

Fundamental local statement:

\[
\nabla_\mu T_{total}^{\mu\nu}=0.
\]

Finite ledgers must close ordinary, relational/wake, bank/reactor, radiation/heat and external-environment exchanges consistently.

The 2 GJ bank is a formation/control/abort buffer, not a free macroscopic gravitational-energy or momentum reservoir.

A wake law is path response, not an independently commandable reactionless thruster. Any restored cycle yielding free work or free momentum is a hard kill.

# 8. RSET / semiclassical-QFT status

The 6 m wall and 10–30 s sub-c ramps are extremely slow relative to the wall light-crossing timescale; no immediate sub-c horizon/divergence hard kill has been found in the necessary adiabatic screen.

This is **not** proof of a finite production \(\langle T_{\mu\nu}\rangle_{ren}\).

A full time-dependent 4D finite renormalized-stress-energy benchmark remains an **authorial validation hard gate for final numerical metric-environment canon**.

This does **not** mean metric is non-operational in-universe in 2226. In-world crew-rated metric operation is governing setting fact. The open gate controls how precisely the design project may claim its environmental coefficients/limits are physically closed.

FTL Alcubierre remains BLACK regardless.

# 9. Ramp geometry and short-haul doctrine

## 9.1 Ramp displacement is metric path

For a linear clean-environment ramp from zero to the certified transport speed, one-ramp displacement is approximately \(\tfrac12 v\tau\).

| Mode | One nominal linear-ramp path | Two-ramp geometric minimum before plateau |
|---|---:|---:|
| NORMAL | **~0.402 million km** | **~0.803 million km** |
| FAST | **~0.786 million km** | **~1.572 million km** |
| EXPEDITE | **~1.167 million km** | **~2.334 million km** |
| HARD | **~2.676 million km** | **~5.351 million km** |

These are **metric path lengths**, not ordinary torch stand-off distances and not safety radii.

## 9.2 Retired 3× doctrine

The old table that treated nominal ramp displacement ×3 as a universal physical clearance law is **RETIRED**.

Do not use:

```text
NORMAL 1.21 Mkm
FAST   2.36 Mkm
EXP    3.50 Mkm
HARD   8.03 Mkm
```

as body-independent acquisition radii.

Those numbers remain historical/provisional doctrine evidence only.

## 9.3 Robust short-haul consequence

A complete NORMAL acquire→plateau→collapse sequence cannot fit between:

- **Earth–Moon**;
- **Mars–Phobos**;

from two-ramp geometry alone.

Jupiter–Ganymede is **not** excluded by ramp geometry alone; any exclusion there depends on environmental certification/calibration.

Governing statement:

> **Metric is a long-baseline trunk technology. Some short routes are too short for a full certified cycle; other routes may be limited by local environmental certification geometry.**

# 10. Certification records, provenance and data validity

A metric certification coefficient set must carry:

```text
STANDARD / VERSION
COEFFICIENT SET ID
VALID FROM
VALID UNTIL
ENVIRONMENT CLASS
SHIP / ARRAY / LOT APPLICABILITY
MODE / RAMP FAMILY
SIGNATURE / AUTHORITY
REVOCATION STATUS
LOCAL CACHE AGE
PROVENANCE
U^M CALIBRATION ID
```

Stale, revoked, wrong-class or wrong-lot data cannot authorize metric acquisition.

A future machine result should expose at least:

```text
GEOMETRY      PASS/HOLD
CONTROL       PASS/HOLD
THERMAL       PASS/HOLD
NULL          PASS/HOLD
MATTER        PASS/HOLD
WAKE          PASS/HOLD
RSET          PASS/HOLD
U^M CAL       ID / STATUS
LEDGER        CLOSED/OPEN
CONFIDENCE    CERTIFIED/UNCERTAIN
RESULT        CERTIFIED/HOLD/BLACK
```

For research simulations, explicit `U-HYP` sensitivity fixtures are allowed only when marked as such.

# 11. Node-failure doctrine

Random isolated node losses and contiguous clustered losses are not equivalent. Clustered losses can create local wall/control defects earlier than raw node-count metrics imply.

Degraded certification tracks spatial contiguity, phase coherence, local authority reserve, affected wall sector, current mode and geodesic/caustic consequences.

EXPEDITE and HARD require no degraded critical node sector.

# 12. Loom card

| Quantity | Value |
|---|---:|
| Active Mc | **10 kg** |
| Normal controlled boundary | **~1,900 m²** |
| Extended mature-route envelope | **~2,430 m²** |
| Effective patches normal | **~971** |
| Boundary authority normal | **~670** |
| Commit interval | **0.25 s** |
| Target action | **B_T=16** |
| Attempt frequency | **10^9 s^-1** |
| Selectivity separation | **40** |
| Boundary leakage target | **≤10^-12** |
| Arrival state | **Q_B^nat = T_AB(Q_A)** |
| Momentum matching | **ordinary torch / external exchange** |

Loom is relational route translation, not a light-year-distance engine. Return certification is not automatic.

## 12.1 Loom commit configuration lock

A crew-rated Loom solution is certified against a specific **domain membership, attachment state, mass-state model, node topology and hull/lattice configuration**.

Once formation/commit enters the committed interval, that configuration is fixed for the attempt. Material attachment, severance, docking-state, cargo-boundary or other domain-membership change invalidates the certified solution and forces abort/quench/fault handling.

In-transition configuration change is not a momentum-exchange, braking, cargo-shedding or domain-severance exploit.

# 13. Reference courier mass ledger

| Quantity | Value |
|---|---:|
| Main body | ~57 m × 9 m |
| Normal crew | 6 |
| Payload target | 50 t |
| Working fluid/water | 300 t |
| Normal remass | 250 t |
| Wet mass | **~1,158.5 t** |
| Dry excl. working fluid/water | **~858.5 t** |
| Unified relational plant | **~88 t** |

## 13.1 Persistent live mass state — CANON

Every active vessel simulation carries live:

```text
CURRENT WET MASS
CURRENT TORCH REMASS
PROTECTED WATER / WORKING FLUID where distinct
CARGO MASS CHANGES
PROPULSION-RELEVANT EXPENDABLES
```

Every burn updates current wet mass and remass. Reaction-mass expenditure is recalculated from **current** mass state and the applicable propulsion model. A flat “remass per flight” is planning shorthand only, never chained-flight authority.

## 13.2 Reference courier schematic / thermal packaging baseline — CANON

The current reference-courier schematic uses **four major deployable radiator assemblies in quadrature**, aligned structurally with the four-longeron / four-major-tank architecture. This supersedes the provisional six-radiator visual-design baseline.

```text
PRIMARY STRUCTURAL GRAMMAR
4 axial longerons
4 major working-fluid / remass tanks in quadrature
4 major deployable radiator assemblies in quadrature
1 axial primary fusion-torch / magnetic-nozzle system
```

Each major radiator assembly may be subdivided into multiple independently isolated panels and coolant loops. Loss of one panel does not automatically imply loss of the complete assembly. Cross-connects, bypasses and degraded operating modes remain valid engineering provisions.

The **radiator count is now locked at four for the reference courier**, but final panel dimensions, folding topology, temperature zoning, loop allocation and total effective emitting area remain subject to detailed thermal/packaging closure. The certified metric table in §5 remains the governing performance requirement: **719 m² at 900 K is the HARD-mode equivalent area, not a mandate that the complete ship thermal system equal 719 m² or that all four assemblies operate at one temperature.**

Schematic rule: major radiator roots shall remain mechanically legible, attached to the primary structure through a dedicated thermal-manifold / load-transfer region, and shall not be represented as solar arrays, decorative fins or additional propulsion surfaces.

# 14. Torch card

| Mode | Exhaust velocity | Ideal full-remass Δv |
|---|---:|---:|
| ECON | 3,000 km/s | ~729 km/s |
| CRUISE | 2,000 km/s | ~486 km/s |
| EXPEDITE | 1,000 km/s | ~243 km/s |
| FAST | 700 km/s | ~170 km/s |
| HARD | 450 km/s | ~109 km/s |
| LIMIT | 300 km/s | ~73 km/s |

Major torch burn and high metric operation are mutually exclusive thermal/field configurations.

# 15. Flight-plan, ephemeris and HUD operating canon

## 15.1 Solved flight-plan minimum fields

Every solved phase shall show:

```text
PHASE
DURATION
CUMULATIVE ETA
VELOCITY / SPEED
VELOCITY REFERENCE
PROPULSION MODE
NAV / EPH QUALITY
```

Unsolved values display `OPEN`, `HOLD`, `--` or equivalent. Do not invent precision to fill a panel.

## 15.2 Ephemeris-quality gate

Before presenting high-precision navigation geometry, verify the stated source actually supports the epoch and target.

- `EPH:HORIZONS` — actual Horizons output was used;
- `EPH:JPL-PROP` — supplied JPL/Horizons state explicitly propagated;
- `EPH:SIM` — deliberate fictional/test fixture.

The existence of an authoritative source in principle is not permission to claim it was evaluated.

JPL/SPICE provides ephemerides, frames, gravitational geometry and target motion. It does **not** solve `U^M_gamma`.

## 15.3 System-basin acquisition

When local-target ephemeris is unavailable, stale or below terminal precision:

```text
STRATEGIC NAV
→ PLANETARY-SYSTEM ACQUISITION BASIN
→ SENSOR / WIDE
→ TRACK
→ LOCAL INTERCEPT
```

This is normal procedure, not a workaround. Direct strategic targeting remains permissible when sufficient local-target ephemeris genuinely exists.

## 15.4 Automatic HUD family

`SHOW HUD` defaults to:

- **TACTICAL** near infrastructure, maneuver hazards or established contacts;
- **NAV / FLIGHT PLAN** during strategic planning;
- **NAV / METRIC** during metric acquisition/cruise/collapse;
- **SENSOR / WIDE** while local reacquisition is incomplete;
- **TACTICAL / TRACK** once local geometry has earned tactical-quality state.

Existing HUD Standard v0.3 geometry/provenance/width/contact grammar remains compatible and governing at presentation level.

# 16. Resolution and quiet-operation discipline

Routine competent operation inside a solved, certified envelope does not require a dice roll merely because an action occurs.

Roll only when failure is meaningfully possible and consequential, or uncertainty, hazard, opposition, damage, time pressure or contested agency makes resolution necessary.

A test flight is not required to manufacture anomalies. Quiet operation is valid play.

# 17. Character play guardrails for flight operations

**Mara Venn:** natural-language command voice; owns commitment and responsibility; does not convert uncertainty into certainty merely because action is required.

**Sol:** owns epistemic discipline within expertise; low-density synthetic sociolect; human-readable sentence first, marked distinction only when it changes meaning; never a status-terminal parody.

**Walter:** autonomous crew; **nonverbal**; agency through behavior, attention, posture, refusal, proximity and choice. Walter's attention may motivate investigation but is never supernatural hidden truth.

# 18. Packet operations

No independent FTL communication exists. Every Loom-capable ship can be an information carrier. Packet custody and information age remain operational campaign variables.

## 18.1 Solar versus interstellar information

Inside Sol, laser/radio communications propagate at `c` and therefore outrun every certified subluminal metric vessel. Metric transport is an urgency and physical-custody layer: people, inspectors, witnesses, diplomatic authority, air-gapped hardware, physical evidence, samples, components and other payloads whose value depends on possession rather than bit transmission. A metric ship does not beat a properly transmitted Solar warrant merely by flying fast.

Across a Loom edge, there is no independent FTL channel. Legal state, market state, software/model updates, scientific results, personal communications and authenticated records must therefore ride a translated physical domain. This is the setting's true packet-carrier regime.

## 18.2 Packet provenance

Data mass is cheap; trusted causal state is not. High-value packet operations preserve source, signing authority, causal age, custody, transfer history, incorporation state and derivation lineage. Physical custody can remain mission-critical even when the data content is separately transmitted.

# 18A. Security, combat and metric interdiction engineering

- **Sensor primacy:** space stealth delays detection/classification/track quality; it does not erase thermal, kinematic or electromagnetic physics.
- **Propulsion split:** torch owns tactical vector change and state matching; metric owns certified Solar long-baseline repositioning; Loom owns interstellar translation. Metric is not a close-combat dodge and Loom is not a dogfight drive.
- **Endpoint interdiction:** security forces naturally concentrate around acquisition/collapse volumes, roadsteads, ports, metrology, certification, refuel/repair and identity/provenance checkpoints. Mid-course capture of a fast metric vessel requires favorable geometry and an explicit model.
- **Certification is not a kill switch:** revocation can invalidate trusted coefficients, insurance or infrastructure access. It does not remotely make the installed plant stop obeying physics.
- **Thermal combat clock:** restricted/retracted radiators transfer rejection load into finite internal storage. Weapons, EW, maneuver, sensors and damage control spend thermal margin; the vessel eventually throttles, cools, dumps heat or disengages. Exact endurance is ship/state-specific.
- **Weapon grammar:** guided kinetics/missiles, drones, EW, high-velocity kinetic launchers, directed energy and point-defense families remain physically constrained by range, track quality, latency, heat, ammunition/power and geometry. No universal engagement-distance table is promoted.
- **Autonomy:** lethal-action authority varies by jurisdiction, mission and delegated rules. Tactical AI may act inside pre-authorized constraints; canon does not require a universal human/synthetic button press for every weapon release.

# 18B. Merchant auxiliary engineering

Commercial torch hulls provide the physical base for crisis sealift. Where designed for interoperability, standardized cargo, power and data interfaces permit reaction-mass tankers/oilers, depot/support roles, casualty evacuation, fast transport and modular auxiliary payloads. Conversion does not erase structural, thermal, power, sensor, crew or legal limits: a freighter is not automatically a warship because a container fits.

Requisition of a civilian vessel changes charter/command authority under applicable law; it does **not** by itself transfer root, patch, reconciliation or cognitive-ownership authority over recognized synthetic crew.

# 19. Traffic / port interface

The engineering stack does not assign traffic merely because a physical certification surface exists.

Runtime separation:

```text
PHYSICAL CERTIFICATION       CANON II
PORT / ROADSTEAD / TRAFFIC   CANON I / Atlas v3.2
QUEUE / OD / FLEET MODEL     explicit model ID when needed
```

Published metric gates/corridors are operational traffic concentration, not literal physical apertures.

# 20. Retired flight numbers and non-promotions

The following are not current canon outputs and may not be reused as defaults:

- universal 1.21 Mkm NORMAL acquisition radius;
- 17:52:47 FR-01B exact route time;
- 5h45 FR-01B-R exact route time;
- 91.45% or 73.31% terminal-time fractions;
- Candidate A/B/C environmental thresholds/radii;
- universal symmetric zero-to-zero 0.30 g terminal profile;
- fixed civilian remass reserve percentage;
- complete ordinary-velocity preservation through metric transport;
- any exact remass/Δv generated without a declared `U^M_gamma` hypothesis/calibration and terminal solver.

Preserve those documents as test/provenance evidence only.

# 21. Hard kills and standing research targets

## Hard kills

- FTL metric;
- free momentum reset;
- free-work restored cycle;
- arbitrary metric editing;
- duplication;
- chronology exploit;
- wake used as independently commandable reactionless thrust;
- stale/revoked certification data used to authorize acquisition.

## Standing research targets

- route-specific null/caustic maps;
- full finite 4D RSET production-ramp benchmark;
- measured environment→node-response coefficients;
- measured control→thermal coupling;
- calibrated `U^M_gamma`;
- calibrated wake/environment partition;
- exact Mc industrial pathway/aging/site shares;
- manufactured node-topology and correlated-failure statistics;
- independent 3-D state-aware optimal-control terminal solver;
- second-route validation after FR-01B-R;
- commercial fleet/traffic parameters downstream of engineering;
- force sizing, auxiliary reserve fractions and relational-hull role allocations downstream of engineering.

# 22. Model/provenance record required for numerical flight work

Any numerical simulation that goes beyond locked machine constants shall emit:

```text
MODEL_ID
MODEL_VERSION
CANON_BASELINE
EPOCH
REFERENCE_FRAME
EPHEMERIS_SOURCE
SHIP_STATE_SOURCE
CERTIFICATION_MODEL / COEFFICIENT_SET
U^M MODEL / CALIBRATION ID
TRAFFIC MODEL if used
ASSUMPTIONS
OUTPUT STATUS: CANON / DERIVED / PROVISIONAL / TEST FIXTURE
```

If a required model is open, say `OPEN`; do not quietly substitute a retired value.

---

**END — CANON II v2.4**