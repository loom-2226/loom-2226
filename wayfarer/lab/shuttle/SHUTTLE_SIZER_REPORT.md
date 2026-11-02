# LOOM Shuttle Sizer v1 — Stage 2 (round 3)
ALL bodies. ALL sponsors. 2026–2226.

**Authority:** NON-CANON engineering screen, all ranges/provenance from the attached input JSON; numerical PASS is not hardware certification.
**Run identity:** Git-blob SHA-1 of exact input JSON (includes stage): `d02928231ba5843c5612c3e419cbd8f24fdfa57a`.
**Reproduce:** `node wayfarer/lab/shuttle/shuttle_sizer.mjs --stage 2`.
**CLI validation record:** CLOSED for previous round-2 Stage 2 commit, confirmed by Claude as reported by kT; this round-3 executable was independently evaluated in the model but not claimed to have a new Node CLI validation.
**Graphics:** SHUTTLE_SIDE_VIEW.svg, SHUTTLE_MASS_WATERFALL.svg.

## Computed gates, same scenario samples
Deterministic coordinate-balanced min/mid/max design: 6561 samples, 43 independent swept inputs. PASS fraction is a **design fraction**, NOT a probability of a flight-ready vehicle.
| Gate | PASS | FAIL | OPEN | PASS / resolved |
|---|---:|---:|---:|---:|
| A | 486 | 6075 | 0 | 7.407% |
| A2 | 4374 | 2187 | 0 | 66.667% |
| KV | 6318 | 243 | 0 | 96.296% |
| KF | 0 | 243 | 6318 | 0.000% |
| B | 0 | 0 | 6561 | n/a |
| R | 5670 | 891 | 0 | 86.420% |
| C | 5103 | 1458 | 0 | 77.778% |
| C_low | 1215 | 5346 | 0 | 18.519% |
| C_high | 5103 | 1458 | 0 | 77.778% |
| DS2 | 1701 | 4860 | 0 | 25.926% |
| DS4 | 1701 | 4860 | 0 | 25.926% |

### Joint closure, same samples
| Combined gates | PASS | FAIL | OPEN | PASS / resolved |
|---|---:|---:|---:|---:|
| A2_and_C | 3483 | 3078 | 0 | 53.086% |
| A2_C_DS2 | 1377 | 5184 | 0 | 20.988% |
| A2_C_DS4 | 1377 | 5184 | 0 | 20.988% |
| A2_KF_C_DS2 | 0 | 5265 | 1296 | 0.000% |
| A2_KF_C_DS4 | 0 | 5265 | 1296 | 0.000% |

### A vs A2 dry mass (kit separated from shuttle)
Original fully-equipped dry min / mid / max: **25.900 / 39.850 / 53.800 t**.
Detachable Venus/Titan kit min / mid / max: **4.750 / 8.025 / 11.300 t**.
Docked shuttle core dry WITHOUT Venus kit min / mid / max: **21.150 / 31.825 / 42.500 t**. A2 applies the 34.200t G8 docked dry limit to CORE only. A applies the same bound to the fully equipped vehicle as a comparator.
Historical lost-sizer dry 27.900t (not a fit target), current mid minus history 11.950t. Earlier v1 comparison 35.400t.
| Dry component | min t | mid t | max t | Kit? | provenance |
|---|---:|---:|---:|---|---|
| pressure_pod_titanium_shell_t | 3.200 | 5.400 | 7.600 | CORE | PROJECTION |
| hull_thermal_structure_t | 9.000 | 11.500 | 14.000 | CORE | ASSUMPTION |
| pressure_pod_fittings_seals_t | 0.500 | 0.850 | 1.200 | CORE | ASSUMPTION |
| folding_rover_chassis_t | 0.600 | 0.900 | 1.200 | CORE | ASSUMPTION |
| single_12m_rotor_blades_hub_mast_t | 0.800 | 1.400 | 2.000 | VENUS/TITAN payload | ASSUMPTION |
| tipjet_ducts_compressors_t | 0.300 | 0.650 | 1.000 | VENUS/TITAN payload | ASSUMPTION |
| torch_low_high_engine_t | 4.000 | 7.000 | 10.000 | CORE | DECLARED_2226 |
| small_belly_thrusters_t | 0.200 | 0.400 | 0.600 | CORE | ASSUMPTION |
| reactor_power_distribution_t | 0.300 | 0.650 | 1.000 | CORE | ASSUMPTION |
| crew_habitat_thermal_package_t | 1.000 | 1.500 | 2.000 | CORE | ASSUMPTION |
| custody_capsule_dry_t | 0.050 | 0.125 | 0.200 | CORE | ASSUMPTION |
| avionics_controls_yaw_t | 0.500 | 0.850 | 1.200 | CORE | ASSUMPTION |
| entry_tps_t | 3.000 | 4.500 | 6.000 | VENUS/TITAN payload | ASSUMPTION |
| landing_gear_door_ramp_t | 0.800 | 1.150 | 1.500 | CORE | ASSUMPTION |
| water_tank_insulated_t | 1.000 | 1.500 | 2.000 | CORE | ASSUMPTION |
| venus_hot_loop_thermal_kit_t | 0.500 | 1.000 | 1.500 | VENUS/TITAN payload | ASSUMPTION |
| venus_cooler_t | 0.150 | 0.475 | 0.800 | VENUS/TITAN payload | ASSUMPTION |

### B stowed shuttle and Wayfarer G8 clearance
Necessary hull fit PASS. Hull length 12.800m vs allowed 12.800m, hull diameter 4.300m vs allowed 4.300m. Remaining allocated axial and radial margins: 0.000m / 0.000m. Ideal folded span 12.000m.
Full B remains OPEN owing to explicit nulls: geometry.mast_stowed_extra_diameter_m, geometry.hub_axial_length_m, geometry.mast_retracted_height_m, geometry.crew_pod_x_m, geometry.rotor_mast_x_m, geometry.rotor_retracted_cg_m, geometry.pod_door_ramp_external_excursion_m.
### Detachable kit and service holds
Kit components: single_12m_rotor_blades_hub_mast_t, tipjet_ducts_compressors_t, entry_tps_t, venus_hot_loop_thermal_kit_t, venus_cooler_t. Thermal pod core insulation/habitat remains in shuttle; detachable hot-loop and active cooler are kit mass and must not be added again.
Kit mass min/mid/max 4.750 / 8.025 / 11.300 t against total Wayfarer payload allowance 50.000t. Thus remaining allowance for other cargo at those three cases: 45.250 / 41.975 / 38.700 t.
G8 certified hold inventory: two service holds 68.000m³ gross; 56.100m³ free after drones. Service x 14.000–18.000m. Packed effective density 0.18–0.45 t/m³ is ASSUMPTION, not a container design.
Four 6.000m blades hypothetically split into 2.000 segments per blade; segment length 3.000m versus 4.000m service length, necessary-only PASS. Full blade connector integrity and stow/reassemble geometry still OPEN.
Kit packed-volume gate KV is computed PASS/FAIL per sample. Full kit physical fit KF is OPEN if total volume passes but **kit.individual_hold_aperture_m, kit.individual_hold_cross_section_m2, kit.rotor_blade_joint_qualified, kit.hot_shuttle_kit_fit_qualified** remain null; a sample exceeding total volume is a determinate FAIL. Free volume does not prove two separate holds can accept the pieces.
First sample: kit mass 4.750t, estimated packed volume 26.389m³, KV=PASS, KF=OPEN.

## Three strongest input sensitivities per computable gate
Each input is set to min / mid / max across 81 deterministic OAT baselines; rank by change in PASS fraction, then physical margin if PASS never changes.
B and full KF have no honest min/mid/max influence ranking until required individual geometry/qualification inputs exist.
**A**
| Input | PASS % min / mid / max | Δ PASS percentage points | Δ margin when no flip |
|---|---|---:|---:|
| mass.torch_low_high_engine_t | 25.926 / 7.407 / 3.704 | 22.222 | 6.000 |
| mass.hull_thermal_structure_t | 11.111 / 7.407 / 3.704 | 7.407 | 5.000 |
| mass.pressure_pod_titanium_shell_t | 11.111 / 7.407 / 3.704 | 7.407 | 4.400 |

**A2**
| Input | PASS % min / mid / max | Δ PASS percentage points | Δ margin when no flip |
|---|---|---:|---:|
| mass.torch_low_high_engine_t | 100.000 / 55.556 / 33.333 | 66.667 | 6.000 |
| mass.hull_thermal_structure_t | 92.593 / 77.778 / 44.444 | 48.148 | 5.000 |
| mass.pressure_pod_titanium_shell_t | 92.593 / 74.074 / 51.852 | 40.741 | 4.400 |

**KV**
| Input | PASS % min / mid / max | Δ PASS percentage points | Δ margin when no flip |
|---|---|---:|---:|
| mass.entry_tps_t | 100.000 / 100.000 / 85.185 | 14.815 | 10.952 |
| kit.packed_effective_density_t_per_m3 | 92.593 / 100.000 / 100.000 | 7.407 | 26.750 |
| mass.single_12m_rotor_blades_hub_mast_t | 100.000 / 100.000 / 92.593 | 7.407 | 4.381 |

**R**
| Input | PASS % min / mid / max | Δ PASS percentage points | Δ margin when no flip |
|---|---|---:|---:|
| power.tipjet_thermal_to_useful_rotor | 56.790 / 100.000 / 100.000 | 43.210 | 7.679 |
| power.rotor_usable_input_heat_limit_MW | 59.259 / 97.531 / 100.000 | 40.741 | 7.321 |
| power.rotor_figure_of_merit | 75.309 / 88.889 / 88.889 | 13.580 | 1.852 |

**C**
| Input | PASS % min / mid / max | Δ PASS percentage points | Δ margin when no flip |
|---|---|---:|---:|
| power.tipjet_thermal_to_useful_rotor | 50.617 / 86.420 / 86.420 | 35.802 | 0.000 |
| power.torch_high_ve_kmps | 53.086 / 86.420 / 86.420 | 33.333 | 15.082 |
| power.rotor_usable_input_heat_limit_MW | 53.086 / 83.951 / 86.420 | 33.333 | 0.000 |

**DS2**
| Input | PASS % min / mid / max | Δ PASS percentage points | Δ margin when no flip |
|---|---|---:|---:|
| thermal.hot_side_rejection_capacity_kW | 9.877 / 33.333 / 33.333 | 23.457 | 27.413 |
| mass.torch_low_high_engine_t | 37.037 / 22.222 / 14.815 | 22.222 | 2.176 |
| thermal.cooler_coefficient_of_performance | 12.346 / 25.926 / 33.333 | 20.988 | 79.271 |

**DS4**
| Input | PASS % min / mid / max | Δ PASS percentage points | Δ margin when no flip |
|---|---|---:|---:|
| thermal.hot_side_rejection_capacity_kW | 9.877 / 33.333 / 33.333 | 23.457 | 28.376 |
| thermal.cooler_coefficient_of_performance | 12.346 / 24.691 / 33.333 | 20.988 | 81.614 |
| thermal.insulation_k_W_per_mK | 34.568 / 13.580 / 13.580 | 20.988 | 75.063 |

## Three mass-driver research checks (not automatic certification)
### Torch 7.7 GW-class source and approved 2226 lineage
**KT DECISION — DECLARED_2226:** Shuttle 4–10 t engine minimum-size floor is unchanged. Wayfarer working ledger total 160.000 t = 85.000 reactor + 45.000 shield + 30.000 nozzle, for 11.361 TW jet. The derived specific jet-power per aggregate propulsion kilogram is 71006.250 kW/kg, so a 7.700 GW-class ideal proportional engine would be 0.108 t. This is **not** physical miniaturization proof; kT declares a larger 4–10t minimum-size floor. No canon changed.
**RESEARCH NOTE — 2026 DFD gap is real and applies equally to Wayfarer.** Repo [torch energy partition / specific power](https://github.com/loom-2226/loom-2226/blob/main/src/wayfarer_torch_energy_partition_mass_feasibility.py) leaves directed fraction and source specific power OPEN. [Jain and Kakade 2023](https://doi.org/10.1016/j.actaastro.2023.02.011) and [Princeton DFD](https://psatellite.com/technology/fusion/) discuss MW-class conceptual systems, not compact GW hardware. The 2026 research bands below diagnose the 200-year technological extrapolation, not an override of DECLARED_2226.
At 7.700 GW ideal jet power, even optimistic study source specific power 25–100 kW/kg implies **77.000–308.000 t** SOURCE-ONLY, before power partition and shielding. Consequently 4.000–10.000t torch engine remains DECLARED_2226 at the approved 4–10 t floor. The `>=77t` 2026 research comparison is a technology-gap diagnostic, not a constraint on the fictional 2226 assumption; 2026 scaling limitations apply to Wayfarer as well.
### Biconic hull and thermal structure
NASA [Venus aeroshell](https://science.nasa.gov/wp-content/uploads/2023/10/advents-venus-orbiter-aerobot-and-dropsonde.pdf) models 3.200m expendable entry body, 0.300t Ti-composite structure and 0.373t HEEET, excluding the 4.300m × 12.800m reusable shuttle with hot rotor mount, keel and rover loads. The 9.000–14.000t kT range cannot be credibly narrowed from that analog. It stays ASSUMPTION.
### 2.8m OD titanium pressure sphere
[Alvin classification comparison](https://www.jstage.jst.go.jp/article/jintransnavi/6/1/6_31/_pdf/-char/en): 51.000mm wall for 4500.000m ocean depth; [Limiting Factor](https://caladanoceanic.com/home/technology/sub/): 90.000mm at 11000.000m, smaller 1.500m inside diameter. [Elastic-plastic buckling](https://doi.org/10.1016/j.marstruc.2017.09.007) flags shape imperfections. Neither qualifies a hot 4-crew Venus vessel; hatch reinforcement remains OPEN.
Analytic perfect-sphere elastic buckling with independent **assumed knockdown and safety factor**, plus simple membrane compression, against 91.000 bar differential. This is a screen, **not** real-hatch, penetration or thermal-cycle buckling qualification.
| Shell mass t | Nominal wall thickness mm | allowable differential pressure bar | required bar | screen |
|---:|---:|---:|---:|---|
| 3.200 | 30.013 | 38.588 | 91.000 | FAIL ANALYTIC |
| 5.400 | 51.436 | 111.269 | 91.000 | PASS ANALYTIC ONLY |
| 7.600 | 73.561 | 245.205 | 91.000 | PASS ANALYTIC ONLY |
Knockdown 0.200–0.500, SF 1.500–2.000, modulus 80.000–115.000GPa, allowable compressive stress 180.000–350.000MPa are all ASSUMPTION; hatch/penetration stress concentrations and Venus hot material strength OPEN. Do not narrow the shell mass until these are resolved.

## Round 4 research sensitivity: torch IDLE, heated CO2 tip jets (NEVER credited to gates)
**kT hypothesis:** reactor no-thrust idle at 0.500–3.000% of 7.700GW working jet reference = 38.500–231.000MW numerical comparison. The independently **ASSUMED delivered** thermal budgets 40.000/135.000/230.000MW are **NOT** a derived heat-transfer efficiency, guaranteed fusion output, or actual reactor availability. No physical model maps 7.7GW jet to idle thermal power; that mapping is OPEN.
**Wayfarer authority is NOT idle:** raw 63.360MW × 0.750 during the BURN ONLY gives 47.520MWe magnet supply and 15.840MW conversion waste. A burn-only energy tap does not establish a stationary reactor heater.
**Minimum stable fusion / turndown:** [PSS Starfire/PFRC](https://psatellite.com/technology/fusion/) projects MW-scale steady-power capability; [PPPL PFRC](https://www.pppl.gov/Princeton-Field-Reversed-Configuration) studies RF-driven FRCs; [Jain & Kakade](https://doi.org/10.1016/j.actaastro.2023.02.011) identify RF recirculation and sustained-plasma challenges; [Nature FRC demonstration](https://www.nature.com/articles/s41467-025-58849-5) validates limited experimental FRC formation, not a GW fusion powerplant. **No published qualified minimum stable fusion power, 0.5–3% turndown, or exhaustless operation for this reactor lineage was found.** These are OPEN, not failed gate inputs.
**Heat path:** a 2226 source-to-hot-loop exchanger → high-temperature duct manifold → retracted mast/rotating union → four hollow rotor blades → CO₂ tip jets. The source must transfer charged-particle/radiative energy without a main plume, hold the FRC operating point, avoid net reaction exhaust, and dissipate unrecovered thermal power. [NASA exchanger material-interface research](https://ntrs.nasa.gov/citations/20230005988) and [NEP heat-pipe sizing](https://ntrs.nasa.gov/citations/20220013111) establish substantial temperature, fatigue, duct-pressure and exchanger-mass concerns but no validated GW-specific 2226 mass range. Exchanger mass, flow, insulation, rotating union and hot-mast heat leak remain OPEN; no credits or new dry-mass guesses.
**Conditional rotor demand at 30/40/50 km**, using original VIRA table and min/mid/max total wet mass, figure of merit and tip-jet efficiency. The *mass and aerodynamic assumptions are the sizer's existing ranges*, not invented reactor performance.
| Rotor case | Wet t | FM | source→rotor | altitude km | ambient bar | shaft MW | required hot-gas input MW |
|---|---:|---:|---:|---:|---:|---:|---:|
| OPTIMISTIC | 49.310 | 0.800 | 0.350 | 30.000 | 9.581 | 7.546 | 21.560 |
| OPTIMISTIC | 49.310 | 0.800 | 0.350 | 40.000 | 3.501 | 11.456 | 32.731 |
| OPTIMISTIC | 49.310 | 0.800 | 0.350 | 50.000 | 1.066 | 19.042 | 54.406 |
| MIDPOINT | 63.630 | 0.700 | 0.225 | 30.000 | 9.581 | 12.642 | 56.185 |
| MIDPOINT | 63.630 | 0.700 | 0.225 | 40.000 | 3.501 | 19.192 | 85.297 |
| MIDPOINT | 63.630 | 0.700 | 0.225 | 50.000 | 1.066 | 31.900 | 141.779 |
| PESSIMISTIC | 77.950 | 0.600 | 0.100 | 30.000 | 9.581 | 19.998 | 199.979 |
| PESSIMISTIC | 77.950 | 0.600 | 0.100 | 40.000 | 3.501 | 30.359 | 303.594 |
| PESSIMISTIC | 77.950 | 0.600 | 0.100 | 50.000 | 1.066 | 50.463 | 504.630 |

**Heat-only ceiling, VIRA profile, no atmospheric/nozzle qualification.** At each independently assumed delivered heat level, climb only while required tip-jet input is no larger than budget. This ignores rotor safe-tip-speed, hot duty, mast/exchanger loss and reactor start/restart, so reported ceilings are optimistic *heat-only* bounds, NOT Gate R or C.
| Rotor case | hypothetical delivered heat MW | thermal rotor ceiling km | cloud-base reached? | **above cloud TOP?** |
|---|---:|---:|---|---|
| OPTIMISTIC | 40.000 | 44.000 | no | no |
| OPTIMISTIC | 135.000 | 63.000 | yes | no |
| OPTIMISTIC | 230.000 | 69.000 | yes | yes |
| MIDPOINT | 40.000 | 20.000 | no | no |
| MIDPOINT | 135.000 | 49.000 | yes | no |
| MIDPOINT | 230.000 | 58.000 | yes | no |
| PESSIMISTIC | 40.000 | OPEN | no | no |
| PESSIMISTIC | 135.000 | 18.000 | no | no |
| PESSIMISTIC | 230.000 | 33.000 | no | no |

Cloud-base 48.000km; cloud-top 65.000km, screen references only. **Entering the clouds is NOT lighting the torch above the clouds.** An ABOVE-CLOUD-TOP result would still not certify magnetic-nozzle plume operation at local density or guarantee reactor idle mode. Jet-power throttling and thermal routing are not demonstrated.
**STOP / HOLDS:** idle fusion power stability, extraction efficiency, exhaust-free containment, rotating joint, heat exchanger/duct mass, and heat transfer to tipjets are all OPEN. Existing A/A2/B/C/D and existing statistical sensitivity ranking are not altered by this isolated calculation.

## Stage 2: Venus rotor and torch, D-shuttle vs D-pod
**Rotor:** one 12.000m disk, VIRA atmosphere, min/mid/max sampled real FM and hot-gas conversion, heat-cap input ceiling, speed and life bound. Computed handover must reach at least 5.000km in this declared screen; physical lift and tip-Mach not certified.
**Torch:** thrust per mode = 2 × Pjet / ve and propellant rate = 2 × Pjet / ve². Required Δv and resulting water-at-orbit are calculated per sample, with separate reaction/crew water and custody payload; never negative reaction-water stock. C is conditional on the rotor arithmetic gate, not dense-CO₂ plume viability.
**D-shuttle:** 18.000h on Venus with pod docked and cold-water heat store PRESERVED. Powered heat-pump input = cabin thermal load / COP, hot-loop reject = cabin load + cooler electrical input. PASS if dedicated cooler and reactor auxiliary bus input each meet required kW, hot-side rejector handles total kW at >ambient temperature, and A2/kit payload mass close. Cooler and rejector installation still unqualified.
**D-pod:** detached pod, cold-water sensible storage only; **maximum passive hours are OUTPUT** without an invented survival-duration target. No D-pod PASS/FAIL criterion. Passive pod heat load includes electronics and actual crew count.
| Crew | minimum detached pod hours | maximum detached pod hours |
|---:|---:|---:|
| 2 | 0.368 | 7.171 |
| 4 | 0.364 | 6.665 |

**Independent best/worst parameter corners (not contained in every balanced sample):**
- 2 crew passive pod: mathematical parameter corner **0.220–11.059 hours**. Balanced-sample observed maximum 7.171 hours. No minimum required stay time.
- 4 crew passive pod: mathematical parameter corner **0.217–10.277 hours**. Balanced-sample observed maximum 6.665 hours. No minimum required stay time.

### Representative first-sample reactor/thermal ledger
| Crew | Load W | cooler electric kW | aux bus allowance kW | hot-loop reject kW | available reject kW | D-shuttle | D-pod hours |
|---:|---:|---:|---:|---:|---:|---|---:|
| 2 | 5485.635 | 78.366 | 25.000 | 83.852 | 25.000 | FAIL | 0.954 |
| 4 | 5685.635 | 81.223 | 25.000 | 86.909 | 25.000 | FAIL | 0.920 |

### Phase-by-phase conserved inventories (first scenario, mode comparisons)
**Mode low**
| Phase | reaction water before → after t | reaction debit t | reserved pod water t | pod cold energy 2/4 crew kWh | cooler input 2/4 crew kW | hot-loop rejection 2/4 crew kW | custody |
|---|---|---:|---:|---|---|---|---|
| entry | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232 | — | — | ONBOARD |
| rotor deploy | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232 | — | — | ONBOARD |
| rotor descent | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232 | — | — | ONBOARD |
| touchdown | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232 | — | — | ONBOARD |
| surface stay | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232 | 78.366/81.223 | 83.852/86.909 | ONBOARD |
| rotor climb | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232 | — | — | ONBOARD |
| rotor-to-torch handover | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232 | — | — | ONBOARD |
| torch ascent to orbit | 23.100 → 0.000 | 23.100 | 0.300 | 5.232/5.232 | — | — | ONBOARD |
Water to orbit 0.000t; unmet demand 7.140t; achievable ideal Δv 6.320km/s; thrust 1000000.000N.
**Mode high**
| Phase | reaction water before → after t | reaction debit t | reserved pod water t | pod cold energy 2/4 crew kWh | cooler input 2/4 crew kW | hot-loop rejection 2/4 crew kW | custody |
|---|---|---:|---:|---|---|---|---|
| entry | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232 | — | — | ONBOARD |
| rotor deploy | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232 | — | — | ONBOARD |
| rotor descent | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232 | — | — | ONBOARD |
| touchdown | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232 | — | — | ONBOARD |
| surface stay | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232 | 78.366/81.223 | 83.852/86.909 | ONBOARD |
| rotor climb | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232 | — | — | ONBOARD |
| rotor-to-torch handover | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232 | — | — | ONBOARD |
| torch ascent to orbit | 23.100 → 7.511 | 15.589 | 0.300 | 5.232/5.232 | — | — | ONBOARD |
Water to orbit 7.511t; unmet demand 0.000t; achievable ideal Δv 9.500km/s; thrust 400000.000N.

### Dense-CO₂ torch light-up research and rotor extension
A [magnetic nozzle PIC study](https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2022.876684/full) operates under near-vacuum backgrounds, not Venus 1–70bar CO₂. [NASA rocket base heating](https://ntrs.nasa.gov/citations/20010116591) and [plume recirculation work](https://link.springer.com/article/10.1007/s12567-020-00306-8) show atmosphere/exhaust shear, entrainment and structural heating matter even for conventional jets. There is **no source** validating a multi-GW magnetically driven plume at Venus pressure; plasma neutralization, CO₂ ingestion, magnetic field confinement, base recirculation, induced hot-loop/hull loads, nozzle erosion and restart remain OPEN.
At the kT 5–25km handover assumption, VIRA pressure falls from 66.650 to 14.930 bar. Rotor-only flight to 30–50km increases MW demand; these are **demand** bounds, not a new heat-source or safe-blade approval.
| Altitude km | ambient bar | rotor shaft MW min–max | tip-jet heat MW min–max |
|---:|---:|---:|---:|
| 30.000 | 9.581 | 8.595–16.921 | 24.558–146.029 |
| 40.000 | 3.501 | 13.049–25.689 | 37.282–221.691 |
| 50.000 | 1.066 | 21.689–42.700 | 61.969–368.492 |
At 30–50km, rotor delivered-heat ceilings need to rise markedly above the 30–100MW assumptions, or a different climb strategy is needed. Moving handover upward helps ambient backpressure but does NOT certify a fusion plasma nozzle at 1–10bar. Torch dense-atmosphere viability remains OPEN.
### Physical holds after conditional gate results
The following declared required physics is still OPEN: venus.torch_atmosphere_viability, venus.entry_vehicle_thermal_qualification, kit individual hold geometry and hot blade joints, research.sphere hot pressurization and actual hatch/seal, power.reactor_waste_heat_MW. No PASS from this sizer overrides those holds.

## Representative sampled outcomes
| Sample | Dry with kit t | A | Docked core t | A2 | packed kit m³ | KV | KF | B | Rotor | Water C | D-shuttle 2 | D-shuttle 4 |
|---:|---:|---|---:|---|---:|---|---|---|---|---|---|---||
| 0 | 25.900 | PASS | 21.150 | PASS | 26.389 | PASS | OPEN | OPEN | FAIL | FAIL | FAIL | FAIL | 
| 1 | 42.000 | FAIL | 33.400 | PASS | 47.778 | PASS | OPEN | OPEN | PASS | PASS | FAIL | FAIL | 
| 2 | 45.950 | FAIL | 36.275 | FAIL | 53.750 | PASS | OPEN | OPEN | PASS | PASS | FAIL | FAIL | 
| 3 | 39.100 | FAIL | 29.900 | PASS | 51.111 | PASS | OPEN | OPEN | FAIL | FAIL | FAIL | FAIL | 
| 4 | 40.275 | FAIL | 31.500 | PASS | 48.750 | PASS | OPEN | OPEN | PASS | FAIL | PASS | PASS | 
| 5 | 41.675 | FAIL | 34.525 | FAIL | 39.722 | PASS | OPEN | OPEN | PASS | PASS | FAIL | FAIL | 
| 6 | 37.675 | FAIL | 27.550 | PASS | 56.250 | FAIL | FAIL | OPEN | PASS | PASS | FAIL | FAIL | 
| 7 | 43.950 | FAIL | 37.250 | FAIL | 37.222 | PASS | OPEN | OPEN | PASS | PASS | FAIL | FAIL | 
| 8 | 38.975 | FAIL | 31.725 | PASS | 40.278 | PASS | OPEN | OPEN | PASS | PASS | PASS | PASS | 

## Full hashed input JSON (verbatim fields and provenance)
```json
{
  "header": "ALL bodies. ALL sponsors. 2026-2226.",
  "schema": "LOOM.SHUTTLE_SIZER_INPUTS_V1",
  "status": "NON_CANON_ENGINEERING_SENSITIVITY_ROUND_3",
  "authority": "kT approved fresh sizer; no edits to canon, Wayfarer, Navigator or historical research",
  "origin": {
    "source_453": "https://github.com/loom-2226/loom-2226/pull/453",
    "bay": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json",
    "qualification": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/docs/CERTIFICATION_BASIS.md",
    "atmosphere": "https://repository.gatech.edu/server/api/core/bitstreams/681dac66-9414-4c40-8f27-9bd92f6a385f/content",
    "atmosphere_reference": "Seiff et al. VIRA (1985), IPPW-6 (2008) JPL/T. Balint adaptation",
    "declared_assumptions": "kT/Claude 2026-11-02; kT-approved explicit model sensitivities, all labeled ASSUMPTION",
    "cli_validation": {
      "status": "CLOSED",
      "basis": "Claude locally ran Stage 2 Node CLI and reproduced run hash 772ccd9ef0cfc82ea7c03ae0c5f3c936d310a0c4; reported by kT 2026-11-03",
      "note": "Prior CLI test closed for round-2 executable; round-3 output requires fresh execution when possible."
    },
    "round_4": "kT approved 2026-11-03; same draft branches; all gate inputs frozen; idle heat research only"
  },
  "si": {
    "kg_per_t": {
      "value": 1000,
      "unit": "kg/t",
      "provenance": "ONLINE",
      "source": "SI unit definition",
      "description": "Unit conversion"
    },
    "m_per_km": {
      "value": 1000,
      "unit": "m/km",
      "provenance": "ONLINE",
      "source": "SI unit definition",
      "description": "Unit conversion"
    },
    "seconds_per_hour": {
      "value": 3600,
      "unit": "s/h",
      "provenance": "ONLINE",
      "source": "SI unit definition",
      "description": "Unit conversion"
    },
    "joules_per_kWh": {
      "value": 3600000,
      "unit": "J/kWh",
      "provenance": "ONLINE",
      "source": "SI unit definition",
      "description": "Unit conversion"
    },
    "kW_per_MW": {
      "value": 1000,
      "unit": "kW/MW",
      "provenance": "ONLINE",
      "source": "SI unit definition",
      "description": "Unit conversion"
    },
    "W_per_GW": {
      "value": 1000000000,
      "unit": "W/GW",
      "provenance": "ONLINE",
      "source": "SI unit prefix definitions (not physical efficiency assumptions)",
      "description": "Explicit unit conversion; never use unrelated kg/t to convert power."
    },
    "W_per_MW": {
      "value": 1000000,
      "unit": "W/MW",
      "provenance": "ONLINE",
      "source": "SI unit prefix definitions (not physical efficiency assumptions)",
      "description": "Explicit unit conversion; never use unrelated kg/t to convert power."
    },
    "W_per_kW": {
      "value": 1000,
      "unit": "W/kW",
      "provenance": "ONLINE",
      "source": "SI unit prefix definitions (not physical efficiency assumptions)",
      "description": "Explicit unit conversion; never use unrelated kg/t to convert power."
    },
    "Pa_per_bar": {
      "value": 100000,
      "unit": "Pa/bar",
      "provenance": "ONLINE",
      "source": "SI unit conversion",
      "description": "Used to check external pressure hull analytic stress/buckling bounds"
    },
    "Pa_per_GPa": {
      "value": 1000000000,
      "unit": "Pa/GPa",
      "provenance": "ONLINE",
      "source": "SI unit conversion",
      "description": "Used in conditional shell check"
    },
    "Pa_per_MPa": {
      "value": 1000000,
      "unit": "Pa/MPa",
      "provenance": "ONLINE",
      "source": "SI unit conversion",
      "description": "Used in conditional shell check"
    },
    "millimeters_per_meter": {
      "value": 1000,
      "unit": "mm/m",
      "provenance": "ONLINE",
      "source": "SI conversion",
      "description": "Thin-shell thickness report only"
    },
    "W_per_TW": {
      "value": 1000000000000,
      "unit": "W/TW",
      "provenance": "ONLINE",
      "source": "SI decimal prefixes",
      "description": "Unit conversion only; nominal jet W from TW"
    },
    "MW_per_GW": {
      "value": 1000,
      "unit": "MW/GW",
      "provenance": "ONLINE",
      "source": "SI decimal prefixes",
      "description": "Convert rated gigawatt jet-power reference into megawatt sensitivity"
    }
  },
  "geometry": {
    "hull_length_m": {
      "value": 12.8,
      "unit": "m",
      "provenance": "ASSUMPTION",
      "source": "kT shuttle baseline",
      "description": "Stowed length limit"
    },
    "hull_diameter_m": {
      "value": 4.3,
      "unit": "m",
      "provenance": "ASSUMPTION",
      "source": "kT shuttle baseline",
      "description": "Stowed outer hull diameter"
    },
    "crew_pod_outer_diameter_m": {
      "value": 2.8,
      "unit": "m",
      "provenance": "ASSUMPTION",
      "source": "kT shuttle baseline",
      "description": "Ti sphere OD"
    },
    "crew_pod_pressure_ext_bar": {
      "value": 92,
      "unit": "bar",
      "provenance": "ASSUMPTION",
      "source": "kT shuttle baseline",
      "description": "Venus external rating target"
    },
    "crew_pod_pressure_int_bar": {
      "value": 1,
      "unit": "bar",
      "provenance": "ASSUMPTION",
      "source": "kT shuttle baseline",
      "description": "Human-crew internal rating target"
    },
    "crew_pod_seats": {
      "value": 4,
      "unit": "crew",
      "provenance": "ASSUMPTION",
      "source": "kT shuttle baseline",
      "description": "Optional crew 2 or 4"
    },
    "bay_x_start_m": {
      "value": 18.25,
      "unit": "m",
      "provenance": "CANON",
      "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json",
      "description": "Active derived Wayfarer v0.5.7 bay start, no edits"
    },
    "bay_x_end_m": {
      "value": 32.05,
      "unit": "m",
      "provenance": "CANON",
      "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json",
      "description": "Active derived Wayfarer v0.5.7 bay end"
    },
    "bay_bore_radius_m": {
      "value": 2.4,
      "unit": "m",
      "provenance": "CANON",
      "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json",
      "description": "Derived internal bore radius"
    },
    "g8_min_radial_clearance_m": {
      "value": 0.25,
      "unit": "m",
      "provenance": "CANON",
      "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/docs/CERTIFICATION_BASIS.md",
      "description": "G8 radial clearance"
    },
    "g8_min_axial_clearance_m": {
      "value": 0.5,
      "unit": "m",
      "provenance": "CANON",
      "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/docs/CERTIFICATION_BASIS.md",
      "description": "G8 axial clearance PER END"
    },
    "rotor_diameter_m": {
      "value": 12,
      "unit": "m",
      "provenance": "ASSUMPTION",
      "source": "kT new baseline",
      "description": "Single deployable tip-jet rotor"
    },
    "rotor_blades": {
      "value": 4,
      "unit": "blades",
      "provenance": "ASSUMPTION",
      "source": "kT new baseline",
      "description": "Two fold forward; two fold aft"
    },
    "rotor_blades_fwd": {
      "value": 2,
      "unit": "blades",
      "provenance": "ASSUMPTION",
      "source": "kT new baseline",
      "description": "Fold along spine"
    },
    "rotor_blades_aft": {
      "value": 2,
      "unit": "blades",
      "provenance": "ASSUMPTION",
      "source": "kT new baseline",
      "description": "Fold along spine"
    },
    "mast_stowed_extra_diameter_m": {
      "value": null,
      "unit": "m",
      "provenance": "OPEN",
      "source": "kT baseline; geometry not designed",
      "description": "Additional thickness beyond the 4.3m stowed hull envelope"
    },
    "hub_axial_length_m": {
      "value": null,
      "unit": "m",
      "provenance": "OPEN",
      "source": "kT baseline; hinge geometry not specified",
      "description": "Actual hub/hinge/rotor roots consume nonzero length"
    },
    "mast_retracted_height_m": {
      "value": null,
      "unit": "m",
      "provenance": "OPEN",
      "source": "kT baseline; geometry not designed",
      "description": "Height and recess under 4.3m outer envelope"
    },
    "crew_pod_x_m": {
      "value": null,
      "unit": "m",
      "provenance": "OPEN",
      "source": "kT baseline; mass CG not yet established",
      "description": "Do not place pod within hull by guessing position"
    },
    "rotor_mast_x_m": {
      "value": null,
      "unit": "m",
      "provenance": "OPEN",
      "source": "kT baseline: over CG; CG unknown",
      "description": "No invented CG"
    },
    "rotor_retracted_cg_m": {
      "value": null,
      "unit": "m",
      "provenance": "OPEN",
      "source": "kT baseline; CG unknown",
      "description": "Rotor and boom integration"
    },
    "pod_door_ramp_external_excursion_m": {
      "value": null,
      "unit": "m",
      "provenance": "OPEN",
      "source": "kT baseline",
      "description": "Door/ramp fits while docked? configuration OPEN"
    }
  },
  "mass": {
    "max_docked_dry_t": {
      "value": 34.2,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT approved envelope",
      "description": "Gate A"
    },
    "v1_comparison_dry_t": {
      "value": 35.4,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude v1 hypothesis",
      "description": "Reference only, NOT replacement ledger"
    },
    "pressure_pod_titanium_shell_t": {
      "min": 3.2,
      "max": 7.6,
      "unit": "t",
      "provenance": "PROJECTION",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "Geometric Ti shell research range; NOT buckling/rated, excludes all windows, doors and fittings"
    },
    "hull_thermal_structure_t": {
      "min": 9,
      "max": 14,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. "
    },
    "pressure_pod_fittings_seals_t": {
      "min": 0.5,
      "max": 1.2,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. "
    },
    "folding_rover_chassis_t": {
      "min": 0.6,
      "max": 1.2,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. "
    },
    "single_12m_rotor_blades_hub_mast_t": {
      "min": 0.8,
      "max": 2,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. "
    },
    "tipjet_ducts_compressors_t": {
      "min": 0.3,
      "max": 1,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. "
    },
    "torch_low_high_engine_t": {
      "min": 4,
      "max": 10,
      "unit": "t",
      "provenance": "DECLARED_2226",
      "source": "kT APPROVED 2026-11-03; Wayfarer ledger https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json",
      "description": "Minimum-size floor for shuttle torch in same hypothetical 2226 lineage as Wayfarer. Wayfarer propulsion allocation: 160t = reactor85t + shadow shield45t + nozzle30t. Working jet ceiling 11.361TW gives ~71,006 kW/kg of total propulsion subsystem; at same linear rate 7.7GW corresponds ~0.108t, below a practical minimum-size floor. Keep editable 4–10t; mass/safety/geometry and scaling are an explicit 2226 declaration, NOT evidence of a physically demonstrated 2026 device. Do NOT alter range. This row counts whole 4–10t torch ENGINE floor, and its split is not separately added to another dry-mass row."
    },
    "small_belly_thrusters_t": {
      "min": 0.2,
      "max": 0.6,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. "
    },
    "reactor_power_distribution_t": {
      "min": 0.3,
      "max": 1,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. "
    },
    "crew_habitat_thermal_package_t": {
      "min": 1,
      "max": 2,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. "
    },
    "custody_capsule_dry_t": {
      "min": 0.05,
      "max": 0.2,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. "
    },
    "avionics_controls_yaw_t": {
      "min": 0.5,
      "max": 1.2,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. "
    },
    "entry_tps_t": {
      "min": 3,
      "max": 6,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. "
    },
    "landing_gear_door_ramp_t": {
      "min": 0.8,
      "max": 1.5,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. "
    },
    "water_tank_insulated_t": {
      "min": 1,
      "max": 2,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. "
    },
    "historical_lost_sizer_dry_t": {
      "value": 27.9,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "Historical derived output from lost sizer preserved in PR #453 / current wayfarer_v05_inputs.json",
      "description": "Historical comparison only, excluded from new component sum and gates."
    },
    "venus_hot_loop_thermal_kit_t": {
      "min": 0.5,
      "max": 1.5,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "Analyst screening proposal 2026-11-03, NON-CANON; not independently qualified",
      "description": "Detachable hot-side rejector/heat pipes/hot shroud; not crew pressure pod generic insulation."
    },
    "venus_cooler_t": {
      "min": 0.15,
      "max": 0.8,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "Analyst screening proposal 2026-11-03, NON-CANON; not independently qualified",
      "description": "Detachable Venus hot-environment active heat pump; full system mass remains hypothesis."
    }
  },
  "water": {
    "v1_retained_capacity_t": {
      "value": 23.1,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "Explicit v1 assumption copied from historical LOST-sizer 23.1t; not new validation"
    },
    "v1_venus_touchdown_belly_debit_t": {
      "value": 0.84,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "Original v1 belly touchdown charged already; NOT automatically charged in rotor-only revised mission"
    },
    "v1_after_all_burns_remaining_t": {
      "value": 1.6,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "Original v1 after all burns including 0.84t touchdown; NO extra subtraction"
    },
    "reaction_water_initial_t": {
      "min": 23.1,
      "max": 23.1,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. Separate reaction water store, full initial per kT."
    },
    "crew_thermal_water_initial_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "DERIVED from each sampled water.crew_water_cold_mass_t",
      "description": "Computed from crew_water_cold_mass_t in every sample; no second independent unknown."
    },
    "reaction_water_entry_debit_t": {
      "min": 0,
      "max": 0.3,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. Only entry reaction debit; never double charge rotor."
    },
    "reaction_water_rotor_debit_t": {
      "value": 0,
      "unit": "t",
      "provenance": "PROJECTION",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "Conditional only if tipjet uses ambient CO2 without vehicle water; reactor fuel budget still open"
    },
    "reaction_water_torch_ascent_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "DERIVED rocket equation in each sampled low/high mode",
      "description": "Computed as stage-specific propellant consumption, not an independent assumption."
    },
    "crew_water_heating_delta_T_K": {
      "min": 15,
      "max": 25,
      "unit": "K",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. Usable cold-store sensible temperature window."
    },
    "crew_water_cold_mass_t": {
      "min": 0.3,
      "max": 1,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. Separate cold thermal water inventory, NOT part of reaction 23.1t."
    },
    "crew_water_heat_capacity_J_per_kg_K": {
      "value": 4186,
      "unit": "J/(kg K)",
      "provenance": "ONLINE",
      "source": "https://openstax.org/books/college-physics-ap-courses/pages/14-2-temperature-change-and-heat-capacity",
      "description": "4186 J/kg/K for liquid water at approximately 15 degrees C, OpenStax specific heat table; ONLINE, not constant across every state."
    },
    "crew_water_life_support_consumption_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "No fixed per-crew life support water consumption"
    },
    "water_to_space_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "expenditure ledger",
      "description": "No hidden losses"
    }
  },
  "power": {
    "rotor_figure_of_merit": {
      "min": 0.6,
      "max": 0.8,
      "unit": "fraction",
      "provenance": "ASSUMPTION",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "#453 real rotor screening band; single 12m disk has equal area to 4x6m but NOT equal structure or FM qualification"
    },
    "tipjet_thermal_to_useful_rotor": {
      "min": 0.1,
      "max": 0.35,
      "unit": "fraction",
      "provenance": "ASSUMPTION",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "#453 tipjet conversion sensitivity; no demonstrated 735K device"
    },
    "rotor_usable_input_heat_limit_MW": {
      "min": 30,
      "max": 100,
      "unit": "MW",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. Delivered tipjet thermal limit for phase screen."
    },
    "rotor_safe_tip_speed_mps": {
      "min": 180,
      "max": 250,
      "unit": "m/s",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. Necessary tip-speed screen only; actual aero tip Mach/solidity/torque unqualified."
    },
    "rotor_hot_duty_limit_s": {
      "value": null,
      "unit": "s",
      "provenance": "OPEN",
      "source": "DERIVED from sampled rotor_hot_duty_limit_h × SI seconds_per_hour",
      "description": "One derived representation; do not sample separately."
    },
    "rotor_climb_rate_mps": {
      "min": 5,
      "max": 15,
      "unit": "m/s",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. Assumed net rotor altitude rate, not derived excess power or free of rotor downwash."
    },
    "torch_low_ve_kmps": {
      "min": 10,
      "max": 25,
      "unit": "km/s",
      "provenance": "PROJECTION",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "#453 unearned sensitivity not recovered sizer engine spec"
    },
    "torch_high_ve_kmps": {
      "min": 25,
      "max": 100,
      "unit": "km/s",
      "provenance": "PROJECTION",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "#453 unearned sensitivity"
    },
    "torch_low_thrust_kN": {
      "value": null,
      "unit": "kN",
      "provenance": "OPEN",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "No recovered value"
    },
    "torch_high_thrust_kN": {
      "value": null,
      "unit": "kN",
      "provenance": "OPEN",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "Lost sizer definition remains OPEN; v1 385kN was unqualified illustrative case"
    },
    "torch_power_source_available_GW": {
      "value": null,
      "unit": "GW",
      "provenance": "OPEN",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "7.7GW historical output not certified and not assumed reactor availability"
    },
    "rotor_coupling_efficiency": {
      "value": null,
      "unit": "fraction",
      "provenance": "OPEN",
      "source": "tipjet compressor bleed and nozzle energy partition",
      "description": "Source-to-rotor conversion band does not supply compressor mass or power model"
    },
    "reactor_waste_heat_MW": {
      "value": null,
      "unit": "MW",
      "provenance": "OPEN",
      "source": "source and conversion not selected",
      "description": "No unbounded heat sink"
    },
    "torch_jet_power_GW": {
      "min": 5,
      "max": 8,
      "unit": "GW",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. Jet kinetic power, not electrical production. Thrust 2P/ve each low/high mode."
    },
    "rotor_hot_duty_limit_h": {
      "min": 1,
      "max": 4,
      "unit": "h",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. Powered rotor lifetime, compare ascent climb exposure; not 18h surface dwell."
    }
  },
  "thermal": {
    "venus_external_surface_K": {
      "min": 735,
      "max": 737,
      "unit": "K",
      "provenance": "ONLINE",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "Venus ~735K from VIRA and NASA environment"
    },
    "cabin_target_K": {
      "value": 300,
      "unit": "K",
      "provenance": "ASSUMPTION",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "NASA ALIVE screening interior target"
    },
    "insulation_k_W_per_mK": {
      "min": 0.02,
      "max": 0.1,
      "unit": "W/(m K)",
      "provenance": "ASSUMPTION",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "Unqualified effective insulating screen"
    },
    "insulation_thickness_m": {
      "min": 0.05,
      "max": 0.15,
      "unit": "m",
      "provenance": "ASSUMPTION",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "Unqualified thickness, not fitted inside pod"
    },
    "stay_requested_h": {
      "value": 18,
      "unit": "h",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude v1",
      "description": "Target surface stay, not achieved result"
    },
    "crew_cases": [
      {
        "value": 2,
        "unit": "crew",
        "provenance": "ASSUMPTION",
        "source": "kT",
        "description": "Two crew case"
      },
      {
        "value": 4,
        "unit": "crew",
        "provenance": "ASSUMPTION",
        "source": "kT",
        "description": "Four crew case"
      }
    ],
    "crew_heat_W_each": {
      "min": 100,
      "max": 150,
      "unit": "W",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. Crew heat per crew member; biological/synthetic specifics remain scenario uncertainty."
    },
    "cooler_coefficient_of_performance": {
      "min": 0.07,
      "max": 0.24,
      "unit": "ratio",
      "provenance": "PROJECTION",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "#453 broad Venus cooler COP sensitivity not qualified; no rejection hardware"
    },
    "hot_side_rejection_capacity_kW": {
      "min": 25,
      "max": 300,
      "unit": "kW",
      "provenance": "ASSUMPTION",
      "source": "Analyst screening proposal 2026-11-03, NON-CANON; not independently qualified",
      "description": "Heat dissipated into hot loop at >Venus ambient; rate only, geometry not certified."
    },
    "surface_effective_internal_area_m2": {
      "value": null,
      "unit": "m2",
      "provenance": "OPEN",
      "source": "thermal bridges and cabin geometry",
      "description": "Ideal full sphere surface used only as optimistic bound"
    },
    "cabin_electronics_kW": {
      "min": 1,
      "max": 2,
      "unit": "kW",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. Cabin electronics continuous heat into cold compartment."
    },
    "active_cooler_power_available_kW": {
      "min": 25,
      "max": 200,
      "unit": "kW",
      "provenance": "ASSUMPTION",
      "source": "Analyst screening proposal 2026-11-03, NON-CANON; not independently qualified",
      "description": "Maximum cooler electrical input; not a guaranteed power bus."
    },
    "reactor_aux_electric_power_available_kW": {
      "min": 25,
      "max": 200,
      "unit": "kW",
      "provenance": "ASSUMPTION",
      "source": "Analyst screening proposal 2026-11-03, NON-CANON; not independently qualified",
      "description": "Aux bus available while torch OFF; independent from 5–8 GW jet energy."
    },
    "hot_loop_reject_temperature_K": {
      "min": 780,
      "max": 900,
      "unit": "K",
      "provenance": "ASSUMPTION",
      "source": "Analyst screening proposal 2026-11-03, NON-CANON; not independently qualified",
      "description": "Hot-loop rejection temperature above Venus ambient, unqualified heat exchanger."
    },
    "active_cooler_mass_key": "mass.venus_cooler_t",
    "active_dock_surface_target_h": "thermal.stay_requested_h",
    "passive_pod_target_h": null
  },
  "venus": {
    "gravity_mps2": {
      "value": 8.87,
      "unit": "m/s2",
      "provenance": "ONLINE",
      "source": "https://nssdc.gsfc.nasa.gov/planetary/factsheet/venusfact.html",
      "description": "Near-surface gravity"
    },
    "rotor_mass_screen_t": {
      "min": 58.5,
      "max": 60,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "58.5 v1 dry35.4 + full water23.1, 60t Claude rotor screen; NOT validated dry mass"
    },
    "atmosphere_profile": [
      {
        "altitude_km": 0,
        "temperature_K": 735.3,
        "pressure_bar": 92.1,
        "density_kg_m3": 64.79
      },
      {
        "altitude_km": 5,
        "temperature_K": 696.8,
        "pressure_bar": 66.65,
        "density_kg_m3": 49.87
      },
      {
        "altitude_km": 10,
        "temperature_K": 658.2,
        "pressure_bar": 47.39,
        "density_kg_m3": 37.72
      },
      {
        "altitude_km": 15,
        "temperature_K": 620.8,
        "pressure_bar": 33.04,
        "density_kg_m3": 27.95
      },
      {
        "altitude_km": 20,
        "temperature_K": 580.7,
        "pressure_bar": 22.52,
        "density_kg_m3": 20.39
      },
      {
        "altitude_km": 25,
        "temperature_K": 539.2,
        "pressure_bar": 14.93,
        "density_kg_m3": 14.57
      },
      {
        "altitude_km": 30,
        "temperature_K": 496.9,
        "pressure_bar": 9.581,
        "density_kg_m3": 10.15
      },
      {
        "altitude_km": 35,
        "temperature_K": 455.3,
        "pressure_bar": 5.917,
        "density_kg_m3": 6.831
      },
      {
        "altitude_km": 40,
        "temperature_K": 417.6,
        "pressure_bar": 3.501,
        "density_kg_m3": 4.404
      },
      {
        "altitude_km": 45,
        "temperature_K": 385.4,
        "pressure_bar": 1.979,
        "density_kg_m3": 2.693
      },
      {
        "altitude_km": 50,
        "temperature_K": 350.5,
        "pressure_bar": 1.066,
        "density_kg_m3": 1.594
      },
      {
        "altitude_km": 55,
        "temperature_K": 302.3,
        "pressure_bar": 0.5314,
        "density_kg_m3": 0.9207
      },
      {
        "altitude_km": 60,
        "temperature_K": 262.8,
        "pressure_bar": 0.2357,
        "density_kg_m3": 0.4694
      },
      {
        "altitude_km": 70,
        "temperature_K": 229.8,
        "pressure_bar": 0.0369,
        "density_kg_m3": 0.08393
      }
    ],
    "atmosphere_source": "https://repository.gatech.edu/server/api/core/bitstreams/681dac66-9414-4c40-8f27-9bd92f6a385f/content",
    "atmosphere_provenance": "ONLINE",
    "atmosphere_status": "VIRA-based 2008 IPPW short-course table, representative no latitude/diurnal wind uncertainty",
    "entry_heat_shield_energy_J": {
      "value": null,
      "unit": "J",
      "provenance": "OPEN",
      "source": "entry velocity and shape OPEN",
      "description": "Cannot give safe entry proof"
    },
    "touchdown_mechanics": {
      "value": null,
      "unit": "physical model",
      "provenance": "OPEN",
      "source": "reusable 735K surface hardware OPEN",
      "description": "Need rotor downwash, gear, surface mechanics"
    },
    "handover_altitude_km": {
      "min": 5,
      "max": 25,
      "unit": "km",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. Planning envelope; actual rotor ceiling derived from heat/duty/disk constraints."
    },
    "orbit_injection_delta_v_kmps": {
      "value": null,
      "unit": "km/s",
      "provenance": "OPEN",
      "source": "trajectory/mode transition/aero/gravity losses OPEN",
      "description": "Cannot subtract orbital speed as required delta-v"
    },
    "torch_mode_switch_altitude_km": {
      "value": null,
      "unit": "km",
      "provenance": "OPEN",
      "source": "mode sequencing/open",
      "description": "No invented switch height"
    },
    "torch_ascent_dv_kmps": {
      "min": 9.5,
      "max": 12,
      "unit": "km/s",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. Post rotor handover idealized total demanded delta-v including assumed losses, NOT integrated trajectory."
    },
    "atmosphere_interpolation": "log_density_linear_altitude_between_tabulated_VIRA_points",
    "torch_atmosphere_viability": {
      "value": null,
      "unit": "qualified ability",
      "provenance": "OPEN",
      "source": "No physical magnetic nozzle / 5–25km Venus atmospheric operation evidence",
      "description": "Magnetic nozzle/plume amid dense 1–70bar CO2 OPEN; per-mode rocket equations do NOT prove burn is physically feasible after rotor handover."
    },
    "entry_vehicle_thermal_qualification": {
      "value": null,
      "unit": "qualified TPS",
      "provenance": "OPEN",
      "source": "No entry aerothermal test supplied",
      "description": "Physical entry qualification OPEN but reaction water Gate C still conditional."
    },
    "rotor_extension_levels_km": [
      {
        "value": 30,
        "unit": "km",
        "provenance": "ASSUMPTION",
        "source": "kT 2026-11-03 requested rotor power beyond 25km handover to 30–50km",
        "description": "Output sampling at a VIRA-profile altitude, NOT a new handover approval"
      },
      {
        "value": 40,
        "unit": "km",
        "provenance": "ASSUMPTION",
        "source": "kT 2026-11-03 requested rotor power beyond 25km handover to 30–50km",
        "description": "Output sampling at a VIRA-profile altitude, NOT a new handover approval"
      },
      {
        "value": 50,
        "unit": "km",
        "provenance": "ASSUMPTION",
        "source": "kT 2026-11-03 requested rotor power beyond 25km handover to 30–50km",
        "description": "Output sampling at a VIRA-profile altitude, NOT a new handover approval"
      }
    ]
  },
  "capsule": {
    "dry_mass_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "DERIVED alias to sampled mass.custody_capsule_dry_t",
      "description": "One unique dry-mass entry only; no duplicate addition."
    },
    "content_mass_t": {
      "min": 0.01,
      "max": 0.05,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. Onboard custody payload; separate from capsule dry mass."
    },
    "ejection_consumable_water_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "kT",
      "description": "Not silently charged to main water"
    },
    "custody_state": "ONBOARD_UNTIL_EJECTED",
    "counterpart_mass_key": "mass.custody_capsule_dry_t"
  },
  "sweep": {
    "values_per_interval": {
      "value": 3,
      "unit": "sample points",
      "provenance": "ASSUMPTION",
      "source": "kT research-style sweep sampling",
      "description": "Endpoints and midpoint, not invented engineering point value"
    },
    "round_decimals": {
      "value": 3,
      "unit": "decimal places",
      "provenance": "ASSUMPTION",
      "source": "Report display only",
      "description": "Precision of display, not scientific"
    },
    "svg_pixels_per_meter": {
      "value": 64,
      "unit": "px/m",
      "provenance": "ASSUMPTION",
      "source": "Presentation only",
      "description": "Scale graphic, not vehicle dimension"
    },
    "svg_margin_px": {
      "value": 75,
      "unit": "px",
      "provenance": "ASSUMPTION",
      "source": "Presentation only",
      "description": "Canvas padding"
    },
    "sample_count": {
      "value": 6561,
      "unit": "deterministic orthogonal samples",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02 sampling method choice",
      "description": "3^8 balanced design; each variable visits min/mid/max, not full Cartesian enumeration; report exact sample coverage."
    },
    "sensitivity_count": {
      "value": 81,
      "unit": "one-at-a-time baselines",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "3^4 pairwise-balanced OAT baseline points, per factor min/mid/max; keeps computation bounded and ranking reproducible."
    },
    "report_top_inputs": {
      "value": 3,
      "unit": "top inputs",
      "provenance": "ASSUMPTION",
      "source": "kT",
      "description": "Only report most decisive 3 each gate"
    },
    "report_preview_samples": {
      "value": 9,
      "unit": "samples",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Representative min/mid/max output rows"
    },
    "handover_step_km": {
      "value": 1,
      "unit": "km",
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Grid resolution for altitude screening, density log-interpolated within VIRA tabulation"
    },
    "sample_levels": {
      "value": 3,
      "unit": "levels",
      "provenance": "ASSUMPTION",
      "source": "kT",
      "description": "min/mid/max each uncertain input"
    }
  },
  "run_stage": {
    "value": 2,
    "unit": "stage",
    "provenance": "ASSUMPTION",
    "source": "kT stage 2 Venus round trip screening approval; stacked on Stage 1",
    "description": "Stage 2 hashed input; stage 3 not authorized."
  },
  "kit": {
    "use": "VENUS_TITAN_DETACHABLE_SPECIAL_ENVIRONMENT_KIT",
    "mass_component_keys": [
      "single_12m_rotor_blades_hub_mast_t",
      "tipjet_ducts_compressors_t",
      "entry_tps_t",
      "venus_hot_loop_thermal_kit_t",
      "venus_cooler_t"
    ],
    "mass_rule": "ONE physical part counted ONCE; Gate A full dry includes it, Gate A2 removes it from docked dry and carries it as 50t payload",
    "note": "TPS here is designated Venus/Titan specialized detachable entry TPS as a v1 model assumption; independent Moon/Mars/Mercury heat protection is NOT qualified by its removal.",
    "holds_total_m3": {
      "value": 68,
      "unit": "m3",
      "provenance": "ASSUMPTION",
      "source": "wayfarer/results/out/CERTIFICATION_REPORT_v0.5.md; current main",
      "description": "Two Wayfarer service holds before existing drones"
    },
    "holds_free_m3": {
      "value": 56.1,
      "unit": "m3",
      "provenance": "ASSUMPTION",
      "source": "wayfarer/results/out/CERTIFICATION_REPORT_v0.5.md; current main",
      "description": "Current G8 reported free volume after drones, not reserved for kit alone"
    },
    "payload_allowance_t": {
      "value": 50,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "wayfarer/docs/SPEC.md; current main",
      "description": "Wayfarer nominal total payload allocation; kit competes with 50t missions"
    },
    "service_x_start_m": {
      "value": 14,
      "unit": "m",
      "provenance": "ASSUMPTION",
      "source": "wayfarer/docs/SPEC.md; current main",
      "description": "Wayfarer service region x14–18"
    },
    "service_x_end_m": {
      "value": 18,
      "unit": "m",
      "provenance": "ASSUMPTION",
      "source": "wayfarer/docs/SPEC.md; current main",
      "description": "Wayfarer service region x14–18"
    },
    "packed_effective_density_t_per_m3": {
      "min": 0.18,
      "max": 0.45,
      "unit": "t/m3",
      "provenance": "ASSUMPTION",
      "source": "Analyst screening proposal 2026-11-03, NON-CANON; not independently qualified",
      "description": "Screening packed payload mass divided by usable volume. Enclosures, cradles and service clearance unqualified."
    },
    "rotor_blade_segments_per_blade": {
      "value": 2,
      "unit": "segments/blade",
      "provenance": "ASSUMPTION",
      "source": "Analyst proposed 2026-11-03",
      "description": "Proposed 6m blade split into two 3m modules; fold alone is insufficient for 4m hold"
    },
    "individual_hold_aperture_m": {
      "value": null,
      "unit": "m",
      "provenance": "OPEN",
      "source": "Unqualified geometry or physics; user did not supply numeric value",
      "description": "Need door/opening width and turning clearance; overall 56.1 m3 alone cannot prove individual storage."
    },
    "individual_hold_cross_section_m2": {
      "value": null,
      "unit": "m2",
      "provenance": "OPEN",
      "source": "Unqualified geometry or physics; user did not supply numeric value",
      "description": "Need clearance geometry and actual hold allocation."
    },
    "rotor_blade_joint_qualified": {
      "value": null,
      "unit": "bool",
      "provenance": "OPEN",
      "source": "Unqualified geometry or physics; user did not supply numeric value",
      "description": "Retrievable high-cycle, hot gas ducted joint/coupling not qualified."
    },
    "hot_shuttle_kit_fit_qualified": {
      "value": null,
      "unit": "bool",
      "provenance": "OPEN",
      "source": "Unqualified geometry or physics; user did not supply numeric value",
      "description": "Moving 5 removable items through hold openings, attachment points and deployment clearance not qualified."
    }
  },
  "research": {
    "authority": "RESEARCH / NON-CANON / never automatically upgrades dry mass assumption to ONLINE",
    "torch_source": {
      "wayfarer_repo": "https://github.com/loom-2226/loom-2226/blob/main/src/wayfarer_torch_energy_partition_mass_feasibility.py",
      "dfd_princeton": "https://collaborate.princeton.edu/en/publications/a-direct-fusion-drive-for-rocket-propulsion/",
      "dfd_mars": "https://psatellite.com/going-to-mars-with-direct-fusion-drive/",
      "dfd_present_specific_power_kW_per_kg": {
        "min": 0.3,
        "max": 1.5,
        "unit": "kW/kg",
        "provenance": "ASSUMPTION",
        "source": "LOOM source energy partition mass feasibility file current main; DFD literature",
        "description": "Repo external DFD research analog only, original ONLINE literature; not a shuttle qualification."
      },
      "dfd_ambitious_specific_power_kW_per_kg": {
        "min": 25,
        "max": 100,
        "unit": "kW/kg",
        "provenance": "ASSUMPTION",
        "source": "LOOM source energy partition mass feasibility file current main",
        "description": "Repo's ambitious study, projected diagnostic not hardware engineering guarantee."
      },
      "targeted_shuttle_torch_jet_power_GW": {
        "value": 7.7,
        "unit": "GW",
        "provenance": "ASSUMPTION",
        "source": "wayfarer/config/wayfarer_v05_inputs.json",
        "description": "Historical approximate torch class; 5–8 GW swept active, this constant is comparison only"
      },
      "torch_mass_decision": "KT_DECLARED_2226: retain 4–10t minimum-size torch engine mass; 2026 DFD figures 0.3–1.5 kW/kg and optimistic 25–100kW/kg (>=77t for 7.7GW) are RESEARCH NOTES contrasting 2026 and assumed 2226 technology, not sizer mass constraints or rejections of the 2226 declaration.",
      "no_double_charge": "Component torch mass includes engine-only assumed; separate source mass must be conserved and qualified; do not double count engine into reactor mass.",
      "lineage_mass_basis": {
        "wayfarer_jet_power_TW": {
          "value": 11.361,
          "unit": "TW",
          "provenance": "CANON",
          "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json",
          "description": "Declared current working torch jet ceiling, not measured reactor thermal power"
        },
        "wayfarer_propulsion_allocation_t": {
          "value": 160,
          "unit": "t",
          "provenance": "CANON",
          "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json",
          "description": "Engineering-assumption propulsion ledger total; not hardware validation"
        },
        "wayfarer_reactor_t": {
          "value": 85,
          "unit": "t",
          "provenance": "CANON",
          "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json",
          "description": "Share of propulsion total"
        },
        "wayfarer_shadow_shield_t": {
          "value": 45,
          "unit": "t",
          "provenance": "CANON",
          "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json",
          "description": "Share of propulsion total"
        },
        "wayfarer_magnetic_nozzle_t": {
          "value": 30,
          "unit": "t",
          "provenance": "CANON",
          "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json",
          "description": "Share of propulsion total"
        },
        "shuttle_jet_power_class_GW": {
          "value": 7.7,
          "unit": "GW",
          "provenance": "DECLARED_2226",
          "source": "kT 2026-11-03",
          "description": "Comparison class only; active sensitivity range retains 5–8GW"
        },
        "torch_lineage_classification": "DECLARED_2226_MINIMUM_SIZE_FLOOR",
        "note": "11.361 TW / 160 t -> 71,006 kW/kg derived scaling; 7.7 GW / 71,006 kW/kg -> 0.108t. This does not validate miniaturization, fusion confinement, or idle mode. 4–10t stays unchanged."
      }
    },
    "hull": {
      "nasa_entry_study": "https://science.nasa.gov/wp-content/uploads/2023/10/advents-venus-orbiter-aerobot-and-dropsonde.pdf",
      "comparator": "3.2m single-use aeroshell ~300kg titanium composite structure plus ~373kg HEEET TPS; NOT comparable to reusable 4.3m x12.8m pressurized hot shuttle with rotor and rover.",
      "hull_mass_decision": "NOT_NARROWED: 9–14t still kT ASSUMPTION; 3.2m expendable entry shell provides no credible bound on 12.8m reusable structural pressure paths.",
      "venus_aeroshell_reference_diameter_m": {
        "value": 3.2,
        "unit": "m",
        "provenance": "ONLINE",
        "source": "https://science.nasa.gov/wp-content/uploads/2023/10/advents-venus-orbiter-aerobot-and-dropsonde.pdf",
        "description": "Aeroshell project diameter (not shuttle)"
      },
      "venus_aeroshell_reference_structure_t": {
        "value": 0.3,
        "unit": "t",
        "provenance": "ONLINE",
        "source": "https://science.nasa.gov/wp-content/uploads/2023/10/advents-venus-orbiter-aerobot-and-dropsonde.pdf",
        "description": "Titanium/composite expendable aeroshell structural mass study"
      },
      "venus_aeroshell_reference_TPS_t": {
        "value": 0.373,
        "unit": "t",
        "provenance": "ONLINE",
        "source": "https://science.nasa.gov/wp-content/uploads/2023/10/advents-venus-orbiter-aerobot-and-dropsonde.pdf",
        "description": "Expendable HEEET TPS study"
      }
    },
    "sphere": {
      "material_density_kg_per_m3": {
        "value": 4423,
        "unit": "kg/m3",
        "provenance": "ASSUMPTION",
        "source": "https://mtsociety.memberclicks.net/assets/docs/Journals/JournalMTS2014%20%281%29.pdf",
        "description": "Ti-6Al-4V density representative; alloy/temperature details unresolved"
      },
      "alvin": "https://www.jstage.jst.go.jp/article/jintransnavi/6/1/6_31/_pdf/-char/en",
      "limiting_factor": "https://caladanoceanic.com/home/technology/sub/",
      "buckling": "https://www.sciencedirect.com/science/article/abs/pii/S0951833917300643",
      "knockdown": {
        "min": 0.2,
        "max": 0.5,
        "unit": "ratio",
        "provenance": "ASSUMPTION",
        "source": "Analyst screening proposal 2026-11-03, NON-CANON; not independently qualified",
        "description": "Plausible imperfection knockdown sensitivity ONLY; not code-calibrated or proven at 735K."
      },
      "safety_factor": {
        "min": 1.5,
        "max": 2,
        "unit": "ratio",
        "provenance": "ASSUMPTION",
        "source": "Analyst screening proposal 2026-11-03, NON-CANON; not independently qualified",
        "description": "Design safety factor sensitivity, not third-party pressure qualification."
      },
      "titanium_hot_modulus_GPa": {
        "min": 80,
        "max": 115,
        "unit": "GPa",
        "provenance": "ASSUMPTION",
        "source": "Analyst screening proposal 2026-11-03, NON-CANON; not independently qualified",
        "description": "Sensitivity for hot/cold Ti shell stiffness; hot strength/corrosion/rate unresolved."
      },
      "titanium_allowable_stress_MPa": {
        "min": 180,
        "max": 350,
        "unit": "MPa",
        "provenance": "ASSUMPTION",
        "source": "Analyst screening proposal 2026-11-03, NON-CANON; not independently qualified",
        "description": "Simplified allowable compression including hot strength derating, joints excluded."
      },
      "poisson_ratio": {
        "value": 0.3,
        "unit": "ratio",
        "provenance": "ASSUMPTION",
        "source": "https://mtsociety.memberclicks.net/assets/docs/Journals/JournalMTS2014%20%281%29.pdf",
        "description": "Ti-6Al-4V representative"
      },
      "sphere_mass_decision": "NOT_NARROWED until imperfect hot sphere + penetrations + hatch code proof; 3.2–7.6t remains geometric PROJECTION only.",
      "alvin_wall_mm": {
        "value": 51,
        "unit": "mm",
        "provenance": "ONLINE",
        "source": "https://www.jstage.jst.go.jp/article/jintransnavi/6/1/6_31/_pdf/-char/en",
        "description": "Alvin nominal sphere wall, different diameter and rating"
      },
      "alvin_reference_depth_m": {
        "value": 4500,
        "unit": "m",
        "provenance": "ONLINE",
        "source": "https://www.jstage.jst.go.jp/article/jintransnavi/6/1/6_31/_pdf/-char/en",
        "description": "Deep submersible external-pressure reference"
      },
      "limiting_factor_wall_mm": {
        "value": 90,
        "unit": "mm",
        "provenance": "ONLINE",
        "source": "https://caladanoceanic.com/home/technology/sub/",
        "description": "Full-ocean-depth Ti wall reference"
      },
      "limiting_factor_depth_m": {
        "value": 11000,
        "unit": "m",
        "provenance": "ONLINE",
        "source": "https://caladanoceanic.com/home/technology/sub/",
        "description": "Manufacturer rated depth"
      },
      "limiting_factor_pressure_hull_inner_diameter_m": {
        "value": 1.5,
        "unit": "m",
        "provenance": "ONLINE",
        "source": "https://caladanoceanic.com/home/technology/sub/",
        "description": "Manufacturer pressure sphere ID"
      },
      "hatch_penetration_reinforcement_mass_t": {
        "value": null,
        "unit": "t",
        "provenance": "OPEN",
        "source": "No quantified hatch/stress concentration thermal-seal validation",
        "description": "Not silently credited within geometric Ti-shell mass or fittings"
      }
    },
    "torch_dense_co2": {
      "context": "At 5–25km 14.9–66.65 bar from VIRA table; 30km 9.581 bar; 40km 3.501 bar; 50km 1.066 bar.",
      "magnetic_nozzle_low_density": "https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2022.876684/full",
      "plume_base_heating": "https://ntrs.nasa.gov/citations/20010116591",
      "plume_recirc": "https://link.springer.com/article/10.1007/s12567-020-00306-8",
      "conclusion": "NO published GW fusion magnetic-nozzle proof at 1–70 bar CO2. Magnetic nozzle vacuum PIC/neutrals cannot be extrapolated to dense neutral CO2; collisional momentum/ionization, entrainment, pressure separation, base recirculation, radiation, coil/nozzle heat, bearing and hull heating OPEN. Raising rotor handover to 30–50km increases rotor tipjet heat substantially."
    },
    "idle_tipjet_heat": {
      "classification": "RESEARCH_ONLY_NON_GATE_SENSITIVITY",
      "idle_fraction_of_nominal_jet": {
        "min": 0.005,
        "max": 0.03,
        "unit": "fraction",
        "provenance": "ASSUMPTION",
        "source": "kT 2026-11-03 proposed idle-heat hypothesis",
        "description": "Equivalent to 0.5–3% of 7.7GW jet-power numerical reference, NOT evidence of stable reactor turndown or thermal heat availability"
      },
      "hypothetical_delivered_tipjet_heat_MW": {
        "min": 40,
        "max": 230,
        "unit": "MW",
        "provenance": "ASSUMPTION",
        "source": "kT 2026-11-03 proposed delivered-heat comparison",
        "description": "Independent idealized delivered heat budgets 40/135/230MW, roughly the 0.5–3% nominal comparison. Heat delivery NOT demonstrated; no efficiency debit inferred."
      },
      "heat_transfer_efficiency": {
        "value": null,
        "unit": "fraction",
        "provenance": "OPEN",
        "source": "No neutron/charged-particle-to-CO2 source thermal partition supplied",
        "description": "No lower/upper numerical bound; do not claim 40–230 MW deliverable"
      },
      "minimum_stable_fusion_fraction": {
        "value": null,
        "unit": "fraction",
        "provenance": "OPEN",
        "source": "PFRC/DFD literature through 2026 lacks measured stable GW reactor fractional turndown",
        "description": "Do not infer turndown from PFRC 1–10MW design scale"
      },
      "no_reaction_exhaust_mode_qualified": {
        "value": null,
        "unit": "bool",
        "provenance": "OPEN",
        "source": "DFD magnetic nozzle/exhaust design requires energetic particle confinement or dumping strategy",
        "description": "Zero tank reaction water for tipjets does not prove zero charged-fusion-product reaction exhaust"
      },
      "mast_duct_hotgas_mass_t": {
        "value": null,
        "unit": "t",
        "provenance": "OPEN",
        "source": "NASA NTRS 20230005988 and 20220013111 show challenging hot exchanger and duct structure, no transfer mass mapping",
        "description": "The existing tipjet_ducts_compressors_t remains independently assumed; do not add or subtract unvalidated hardware."
      },
      "allowable_heat_to_mast_MW": {
        "value": null,
        "unit": "MW",
        "provenance": "OPEN",
        "source": "Interface through mast at Venus thermal environment not qualified",
        "description": "Structural thermal, insulation, rotating hot-gas joints, duct pressure drops and bearing/seals OPEN."
      },
      "thermal_rejection_MW": {
        "value": null,
        "unit": "MW",
        "provenance": "OPEN",
        "source": "Reactor heat balance at idle and start/restart transition not qualified",
        "description": "No cooling 'free heat' credit"
      },
      "wayfarer_torch_tap_raw_MW": {
        "value": 63.36,
        "unit": "MW",
        "provenance": "CANON",
        "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/docs/SHIP_POWER_BUDGET_2026_11_01.md",
        "description": "Burn-only source raw extraction, not an idle source"
      },
      "wayfarer_torch_tap_conversion": {
        "value": 0.75,
        "unit": "fraction",
        "provenance": "CANON",
        "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/docs/SHIP_POWER_BUDGET_2026_11_01.md",
        "description": "Burn-only conversion, raw thermal/electromagnetic energy to electrical magnets"
      },
      "wayfarer_torch_tap_net_MWe": {
        "value": 47.52,
        "unit": "MWe",
        "provenance": "CANON",
        "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/docs/SHIP_POWER_BUDGET_2026_11_01.md",
        "description": "Burn-only magnets/cryocooler net, physical tap OPEN"
      },
      "wayfarer_torch_tap_waste_MW": {
        "value": 15.84,
        "unit": "MW",
        "provenance": "CANON",
        "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/docs/SHIP_POWER_BUDGET_2026_11_01.md",
        "description": "Burn-only conversion waste, not an idle rotor heat allocation"
      },
      "case_scope": "Heat-only rotor-disk momentum demand sweep at mass/FM/thermal-to-rotor corners; no safe tip-speed, duty, ascent acceleration, reactor electrical load, 735K mast heat loss, or transport physics certified. DO NOT FEED INTO ANY GATE.",
      "sources": {
        "pss_star_fire": "https://psatellite.com/technology/fusion/",
        "pppl_pfrc": "https://www.pppl.gov/Princeton-Field-Reversed-Configuration",
        "dfd_2023_engineering": "https://doi.org/10.1016/j.actaastro.2023.02.011",
        "field_reversed_fusion_stability": "https://www.nature.com/articles/s41467-025-58849-5",
        "nasa_hot_exchanger": "https://ntrs.nasa.gov/citations/20230005988",
        "nasa_heatpipe_exchanger": "https://ntrs.nasa.gov/citations/20220013111",
        "nasa_heated_gas_interfaces": "https://ntrs.nasa.gov/citations/20210026680"
      },
      "evidence": "PSS/PFRC is conceptual 1–10MW and related 2023 analysis cites RF-recirculation losses and no inherent plasma self-heating. No 0.5–3% GW-class stable off-nominal power or exhaust-free rotor gas heating demonstration. Heat-pipe/NTP exchangers establish real temperature, material, pressure-drop and fatigue constraints, not the ~MW/kg mass of a 2226 hot mast.",
      "venus_cloud_base_km": {
        "value": 48,
        "unit": "km",
        "provenance": "PROJECTION",
        "source": "Venus main cloud deck approximate lower boundary, based on LOOM #453 Venus atmosphere research; no physical torch qualification",
        "description": "Screening dividing line, NOT proven uniform Venus atmosphere transition; cloud base differs with dynamics"
      },
      "venus_cloud_top_km": {
        "value": 65,
        "unit": "km",
        "provenance": "PROJECTION",
        "source": "LOOM #453 approximate Venus cloud layer 48–65km",
        "description": "Chosen upper cloud boundary for altitude screen only; real cloud top estimates vary and extend higher at some locations"
      }
    }
  }
}
```
