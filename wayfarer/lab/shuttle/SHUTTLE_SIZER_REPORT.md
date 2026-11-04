# LOOM Shuttle Sizer v1 — Stage 2 (round 5a)
ALL bodies. ALL sponsors. 2026–2226.

**Authority:** NON-CANON engineering screen, all ranges/provenance from the attached input JSON; numerical PASS is not hardware certification.
**Run identity:** Git-blob SHA-1 of exact input JSON (includes stage): `a1a8db40fb53ab889fa9bafbe52c299b7a5e529d`.
**Reproduce:** `node wayfarer/lab/shuttle/shuttle_sizer.mjs --stage 2`.
**CLI validation record:** CLOSED for previous round-2 Stage 2 commit, confirmed by Claude as reported by kT; this round-5a executable was evaluated in JS against hashed inputs; a new independent Node CLI execution is not claimed.
**Graphics:** SHUTTLE_SIDE_VIEW.svg, SHUTTLE_MASS_WATERFALL.svg.

## Computed gates, same scenario samples
Deterministic coordinate-balanced min/mid/max design: 6561 samples, 46 independent swept inputs. PASS fraction is a **design fraction**, NOT a probability of a flight-ready vehicle.
| Gate | PASS | FAIL | OPEN | PASS / resolved |
|---|---:|---:|---:|---:|
| A | 486 | 6075 | 0 | 7.407% |
| A2 | 5103 | 1458 | 0 | 77.778% |
| KV | 5103 | 1458 | 0 | 77.778% |
| KF | 0 | 1458 | 5103 | 0.000% |
| B | 0 | 0 | 6561 | n/a |
| R | 6561 | 0 | 0 | 100.000% |
| C | 5670 | 891 | 0 | 86.420% |
| C_low | 1296 | 5265 | 0 | 19.753% |
| C_high | 5670 | 891 | 0 | 86.420% |
| DS2 | 2835 | 3726 | 0 | 43.210% |
| DS3 | 2835 | 3726 | 0 | 43.210% |
| DS4 | 2835 | 3726 | 0 | 43.210% |

### Joint closure, same samples
| Combined gates | PASS | FAIL | OPEN | PASS / resolved |
|---|---:|---:|---:|---:|
| A2_and_C | 4536 | 2025 | 0 | 69.136% |
| A2_C_DS2 | 2430 | 4131 | 0 | 37.037% |
| A2_C_DS3 | 2430 | 4131 | 0 | 37.037% |
| A2_C_DS4 | 2430 | 4131 | 0 | 37.037% |
| A2_KF_C_DS2 | 0 | 4617 | 1944 | 0.000% |
| A2_KF_C_DS3 | 0 | 4617 | 1944 | 0.000% |
| A2_KF_C_DS4 | 0 | 4617 | 1944 | 0.000% |

### A vs A2 dry mass (kit separated from shuttle)
Original fully-equipped dry min / mid / max: **25.842 / 40.289 / 54.737 t**.
Detachable Venus/Titan kit min / mid / max: **5.925 / 10.269 / 14.613 t**.
Docked shuttle core dry WITHOUT Venus kit min / mid / max: **19.917 / 30.021 / 40.124 t**. A2 applies the 34.200t G8 docked dry limit to CORE only. A applies the same bound to the fully equipped vehicle as a comparator.
Historical lost-sizer dry 27.900t (not a fit target), current mid minus history 12.389t. Earlier v1 comparison 35.400t.
| Dry component | min t | mid t | max t | Kit? | provenance |
|---|---:|---:|---:|---|---|
| pressure_pod_titanium_shell_t | 2.278 | 3.844 | 5.410 | CORE | ASSUMPTION |
| hull_thermal_structure_t | 7.953 | 10.163 | 12.372 | CORE | ASSUMPTION |
| pressure_pod_fittings_seals_t | 0.399 | 0.678 | 0.957 | CORE | ASSUMPTION |
| folding_rover_chassis_t | 0.530 | 0.795 | 1.060 | CORE | ASSUMPTION |
| single_12m_rotor_blades_hub_mast_t | 0.800 | 1.400 | 2.000 | VENUS/TITAN payload | ASSUMPTION |
| tipjet_ducts_compressors_t | 0.300 | 0.650 | 1.000 | VENUS/TITAN payload | ASSUMPTION |
| torch_low_high_engine_t | 4.000 | 7.000 | 10.000 | CORE | DECLARED_2226 |
| small_belly_thrusters_t | 0.200 | 0.400 | 0.600 | CORE | ASSUMPTION |
| reactor_power_distribution_t | 0.300 | 0.650 | 1.000 | CORE | ASSUMPTION |
| crew_habitat_thermal_package_t | 1.000 | 1.500 | 2.000 | CORE | ASSUMPTION |
| custody_capsule_dry_t | 0.050 | 0.125 | 0.200 | CORE | ASSUMPTION |
| avionics_controls_yaw_t | 0.500 | 0.850 | 1.200 | CORE | ASSUMPTION |
| landing_gear_door_ramp_t | 0.707 | 1.016 | 1.326 | CORE | ASSUMPTION |
| water_tank_insulated_t | 1.000 | 1.500 | 2.000 | CORE | ASSUMPTION |
| venus_hot_loop_thermal_kit_t | 0.500 | 1.000 | 1.500 | VENUS/TITAN payload | ASSUMPTION |
| venus_cooler_t | 0.150 | 0.475 | 0.800 | VENUS/TITAN payload | ASSUMPTION |
| kit_house_reactor_t | 1.875 | 3.094 | 4.313 | VENUS/TITAN payload | DECLARED_2226 |
| kit_house_exchanger_ducts_t | 0.300 | 0.650 | 1.000 | VENUS/TITAN payload | ASSUMPTION |
| base_entry_tps_core_t | 1.000 | 1.500 | 2.000 | CORE | ASSUMPTION |
| extra_venus_entry_tps_t | 2.000 | 3.000 | 4.000 | VENUS/TITAN payload | DERIVED |

### B stowed shuttle and Wayfarer G8 clearance
Necessary hull fit PASS. Hull length 12.800m vs allowed 12.800m, hull diameter 3.800m vs allowed 4.300m. Remaining allocated axial and radial margins: 0.000m / 0.500m. Ideal folded span 12.000m.
Full B remains OPEN owing to explicit nulls: geometry.mast_stowed_extra_diameter_m, geometry.hub_axial_length_m, geometry.mast_retracted_height_m, geometry.crew_pod_x_m, geometry.rotor_mast_x_m, geometry.rotor_retracted_cg_m, geometry.pod_door_ramp_external_excursion_m.
### Detachable kit and service holds
Kit components: single_12m_rotor_blades_hub_mast_t, tipjet_ducts_compressors_t, extra_venus_entry_tps_t, venus_hot_loop_thermal_kit_t, venus_cooler_t, kit_house_reactor_t, kit_house_exchanger_ducts_t. Thermal pod core insulation/habitat remains in shuttle; detachable hot-loop and active cooler are kit mass and must not be added again.
Kit mass min/mid/max 5.925 / 10.269 / 14.613 t against total Wayfarer payload allowance 50.000t. Thus remaining allowance for other cargo at those three cases: 44.075 / 39.731 / 35.388 t.
G8 certified hold inventory: two service holds 68.000m³ gross; 56.100m³ free after drones. Service x 14.000–18.000m. Packed effective density 0.18–0.45 t/m³ is ASSUMPTION, not a container design.
Four 6.000m blades hypothetically split into 2.000 segments per blade; segment length 3.000m versus 4.000m service length, necessary-only PASS. Full blade connector integrity and stow/reassemble geometry still OPEN.
Kit packed-volume gate KV is computed PASS/FAIL per sample. Full kit physical fit KF is OPEN if total volume passes but **kit.individual_hold_aperture_m, kit.individual_hold_cross_section_m2, kit.rotor_blade_joint_qualified, kit.hot_shuttle_kit_fit_qualified** remain null; a sample exceeding total volume is a determinate FAIL. Free volume does not prove two separate holds can accept the pieces.
First sample: kit mass 5.925t, estimated packed volume 32.917m³, KV=PASS, KF=OPEN.

## Three strongest input sensitivities per computable gate
Each input is set to min / mid / max across 81 deterministic OAT baselines; rank by change in PASS fraction, then physical margin if PASS never changes.
B and full KF have no honest min/mid/max influence ranking until required individual geometry/qualification inputs exist.
**A**
| Input | PASS % min / mid / max | Δ PASS percentage points | Δ margin when no flip |
|---|---|---:|---:|
| mass.torch_low_high_engine_t | 14.815 / 3.704 / 3.704 | 11.111 | 6.000 |
| mass.hull_thermal_structure_t | 11.111 / 3.704 / 3.704 | 7.407 | 4.419 |
| mass.entry_tps_t | 11.111 / 7.407 / 3.704 | 7.407 | 3.000 |

**A2**
| Input | PASS % min / mid / max | Δ PASS percentage points | Δ margin when no flip |
|---|---|---:|---:|
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 40.741 | 59.259 | 6.000 |
| mass.hull_thermal_structure_t | 100.000 / 88.889 / 70.370 | 29.630 | 4.419 |
| mass.pressure_pod_titanium_shell_t | 100.000 / 88.889 / 74.074 | 25.926 | 3.132 |

**KV**
| Input | PASS % min / mid / max | Δ PASS percentage points | Δ margin when no flip |
|---|---|---:|---:|
| kit.packed_effective_density_t_per_m3 | 40.741 / 100.000 / 100.000 | 59.259 | 34.229 |
| mass.entry_tps_t | 92.593 / 81.481 / 70.370 | 22.222 | 10.952 |
| power.kit_house_reactor_thermal_MW | 92.593 / 81.481 / 70.370 | 22.222 | 8.899 |

**R**
| Input | PASS % min / mid / max | Δ PASS percentage points | Δ margin when no flip |
|---|---|---:|---:|
| power.tipjet_thermal_to_useful_rotor | 100.000 / 100.000 / 100.000 | 0.000 | 17.222 |
| power.rotor_hot_duty_limit_h | 100.000 / 100.000 / 100.000 | 0.000 | 14.901 |
| power.rotor_climb_rate_mps | 100.000 / 100.000 / 100.000 | 0.000 | 11.247 |

**C**
| Input | PASS % min / mid / max | Δ PASS percentage points | Δ margin when no flip |
|---|---|---:|---:|
| power.torch_high_ve_kmps | 60.494 / 100.000 / 100.000 | 39.506 | 15.148 |
| venus.torch_ascent_dv_kmps | 100.000 / 88.889 / 70.370 | 29.630 | 2.035 |
| mass.torch_low_high_engine_t | 92.593 / 86.420 / 81.481 | 11.111 | 0.906 |

**DS2**
| Input | PASS % min / mid / max | Δ PASS percentage points | Δ margin when no flip |
|---|---|---:|---:|
| thermal.insulation_k_W_per_mK | 62.963 / 39.506 / 24.691 | 38.272 | 1.579 |
| thermal.reactor_aux_electric_power_available_kW | 16.049 / 48.148 / 53.086 | 37.037 | 1.188 |
| thermal.active_cooler_power_available_kW | 16.049 / 50.617 / 53.086 | 37.037 | 1.185 |

**DS4**
| Input | PASS % min / mid / max | Δ PASS percentage points | Δ margin when no flip |
|---|---|---:|---:|
| thermal.insulation_k_W_per_mK | 62.963 / 39.506 / 24.691 | 38.272 | 1.595 |
| thermal.reactor_aux_electric_power_available_kW | 14.815 / 48.148 / 53.086 | 38.272 | 1.236 |
| thermal.active_cooler_power_available_kW | 14.815 / 50.617 / 53.086 | 38.272 | 1.233 |

## Three mass-driver research checks (not automatic certification)
### Torch 7.7 GW-class source and approved 2226 lineage
**KT DECISION — DECLARED_2226:** Shuttle 4–10 t engine minimum-size floor is unchanged. Wayfarer working ledger total 160.000 t = 85.000 reactor + 45.000 shield + 30.000 nozzle, for 11.361 TW jet. The derived specific jet-power per aggregate propulsion kilogram is 71006.250 kW/kg, so a 7.700 GW-class ideal proportional engine would be 0.108 t. This is **not** physical miniaturization proof; kT declares a larger 4–10t minimum-size floor. No canon changed.
**RESEARCH NOTE — 2026 DFD gap is real and applies equally to Wayfarer.** Repo [torch energy partition / specific power](https://github.com/loom-2226/loom-2226/blob/main/src/wayfarer_torch_energy_partition_mass_feasibility.py) leaves directed fraction and source specific power OPEN. [Jain and Kakade 2023](https://doi.org/10.1016/j.actaastro.2023.02.011) and [Princeton DFD](https://psatellite.com/technology/fusion/) discuss MW-class conceptual systems, not compact GW hardware. The 2026 research bands below diagnose the 200-year technological extrapolation, not an override of DECLARED_2226.
At 7.700 GW ideal jet power, even optimistic study source specific power 25–100 kW/kg implies **77.000–308.000 t** SOURCE-ONLY, before power partition and shielding. Consequently 4.000–10.000t torch engine remains DECLARED_2226 at the approved 4–10 t floor. The `>=77t` 2026 research comparison is a technology-gap diagnostic, not a constraint on the fictional 2226 assumption; 2026 scaling limitations apply to Wayfarer as well.
### Biconic hull and thermal structure
NASA [Venus aeroshell](https://science.nasa.gov/wp-content/uploads/2023/10/advents-venus-orbiter-aerobot-and-dropsonde.pdf) models 3.200m expendable entry body, 0.300t Ti-composite structure and 0.373t HEEET, excluding the 3.800m × 12.800m reusable shuttle with hot rotor mount, keel and rover loads. The 7.953–12.372t kT range cannot be credibly narrowed from that analog. It stays ASSUMPTION.
### 2.8m OD titanium pressure sphere
[Alvin classification comparison](https://www.jstage.jst.go.jp/article/jintransnavi/6/1/6_31/_pdf/-char/en): 51.000mm wall for 4500.000m ocean depth; [Limiting Factor](https://caladanoceanic.com/home/technology/sub/): 90.000mm at 11000.000m, smaller 1.500m inside diameter. [Elastic-plastic buckling](https://doi.org/10.1016/j.marstruc.2017.09.007) flags shape imperfections. Neither qualifies a hot 4-crew Venus vessel; hatch reinforcement remains OPEN.
Analytic perfect-sphere elastic buckling with independent **assumed knockdown and safety factor**, plus simple membrane compression, against 91.000 bar differential. This is a screen, **not** real-hatch, penetration or thermal-cycle buckling qualification.
| Shell mass t | Nominal wall thickness mm | allowable differential pressure bar | required bar | screen |
|---:|---:|---:|---:|---|
| 2.278 | 26.797 | 38.588 | 91.000 | FAIL ANALYTIC |
| 3.844 | 45.925 | 111.269 | 91.000 | PASS ANALYTIC ONLY |
| 5.410 | 65.680 | 245.205 | 91.000 | PASS ANALYTIC ONLY |
Knockdown 0.200–0.500, SF 1.500–2.000, modulus 80.000–115.000GPa, allowable compressive stress 180.000–350.000MPa are all ASSUMPTION; hatch/penetration stress concentrations and Venus hot material strength OPEN. Do not narrow the shell mass until these are resolved.

## Round 4 research sensitivity: torch IDLE, heated CO2 tip jets (NEVER credited to gates)
**kT hypothesis:** reactor no-thrust idle at 0.500–3.000% of 7.700GW working jet reference = 38.500–231.000MW numerical comparison. The independently **ASSUMED delivered** thermal budgets 40.000/135.000/230.000MW are **NOT** a derived heat-transfer efficiency, guaranteed fusion output, or actual reactor availability. No physical model maps 7.7GW jet to idle thermal power; that mapping is OPEN.
**Wayfarer authority is NOT idle:** raw 63.360MW × 0.750 during the BURN ONLY gives 47.520MWe magnet supply and 15.840MW conversion waste. A burn-only energy tap does not establish a stationary reactor heater.
**Minimum stable fusion / turndown:** [PSS Starfire/PFRC](https://psatellite.com/technology/fusion/) projects MW-scale steady-power capability; [PPPL PFRC](https://www.pppl.gov/Princeton-Field-Reversed-Configuration) studies RF-driven FRCs; [Jain & Kakade](https://doi.org/10.1016/j.actaastro.2023.02.011) identify RF recirculation and sustained-plasma challenges; [Nature FRC demonstration](https://www.nature.com/articles/s41467-025-58849-5) validates limited experimental FRC formation, not a GW fusion powerplant. **No published qualified minimum stable fusion power, 0.5–3% turndown, or exhaustless operation for this reactor lineage was found.** These are OPEN, not failed gate inputs.
**Heat path:** a 2226 source-to-hot-loop exchanger → high-temperature duct manifold → retracted mast/rotating union → four hollow rotor blades → CO₂ tip jets. The source must transfer charged-particle/radiative energy without a main plume, hold the FRC operating point, avoid net reaction exhaust, and dissipate unrecovered thermal power. [NASA exchanger material-interface research](https://ntrs.nasa.gov/citations/20230005988) and [NEP heat-pipe sizing](https://ntrs.nasa.gov/citations/20220013111) establish substantial temperature, fatigue, duct-pressure and exchanger-mass concerns but no validated GW-specific 2226 mass range. Exchanger mass, flow, insulation, rotating union and hot-mast heat leak remain OPEN; no credits or new dry-mass guesses.
**Conditional rotor demand at 30/40/50 km**, using original VIRA table and min/mid/max total wet mass, figure of merit and tip-jet efficiency. The *mass and aerodynamic assumptions are the sizer's existing ranges*, not invented reactor performance.
| Rotor case | Wet t | FM | source→rotor | altitude km | ambient bar | shaft MW | required hot-gas input MW |
|---|---:|---:|---:|---:|---:|---:|---:|
| OPTIMISTIC | 49.252 | 0.800 | 0.350 | 30.000 | 9.581 | 7.533 | 21.522 |
| OPTIMISTIC | 49.252 | 0.800 | 0.350 | 40.000 | 3.501 | 11.436 | 32.674 |
| OPTIMISTIC | 49.252 | 0.800 | 0.350 | 50.000 | 1.066 | 19.008 | 54.310 |
| MIDPOINT | 64.069 | 0.700 | 0.225 | 30.000 | 9.581 | 12.773 | 56.768 |
| MIDPOINT | 64.069 | 0.700 | 0.225 | 40.000 | 3.501 | 19.391 | 86.182 |
| MIDPOINT | 64.069 | 0.700 | 0.225 | 50.000 | 1.066 | 32.231 | 143.250 |
| PESSIMISTIC | 78.887 | 0.600 | 0.100 | 30.000 | 9.581 | 20.359 | 203.595 |
| PESSIMISTIC | 78.887 | 0.600 | 0.100 | 40.000 | 3.501 | 30.908 | 309.084 |
| PESSIMISTIC | 78.887 | 0.600 | 0.100 | 50.000 | 1.066 | 51.375 | 513.754 |

**Heat-only ceiling, VIRA profile, no atmospheric/nozzle qualification.** At each independently assumed delivered heat level, climb only while required tip-jet input is no larger than budget. This ignores rotor safe-tip-speed, hot duty, mast/exchanger loss and reactor start/restart, so reported ceilings are optimistic *heat-only* bounds, NOT Gate R or C.
| Rotor case | hypothetical delivered heat MW | thermal rotor ceiling km | cloud-base reached? | **above cloud TOP?** |
|---|---:|---:|---|---|
| OPTIMISTIC | 40.000 | 44.000 | no | no |
| OPTIMISTIC | 135.000 | 63.000 | yes | no |
| OPTIMISTIC | 230.000 | 69.000 | yes | yes |
| MIDPOINT | 40.000 | 19.000 | no | no |
| MIDPOINT | 135.000 | 48.000 | yes | no |
| MIDPOINT | 230.000 | 57.000 | yes | no |
| PESSIMISTIC | 40.000 | OPEN | no | no |
| PESSIMISTIC | 135.000 | 18.000 | no | no |
| PESSIMISTIC | 230.000 | 33.000 | no | no |

Cloud-base 48.000km; cloud-top 65.000km, screen references only. **Entering the clouds is NOT lighting the torch above the clouds.** An ABOVE-CLOUD-TOP result would still not certify magnetic-nozzle plume operation at local density or guarantee reactor idle mode. Jet-power throttling and thermal routing are not demonstrated.
**STOP / HOLDS:** idle fusion power stability, extraction efficiency, exhaust-free containment, rotating joint, heat exchanger/duct mass, and heat transfer to tipjets are all OPEN. Existing A/A2/B/C/D and existing statistical sensitivity ranking are not altered by this isolated calculation.

## Stage 2: Venus rotor and torch, D-shuttle vs D-pod
**Rotor:** one 12.000m disk, VIRA atmosphere, sampled rotor FM and hot-gas conversion, kT-approved 100–230MW independent kit house reactor plus active cabin electrical debits and rotor hot-duty/tip-speed screens. Handover is an OUTPUT (no imposed 25km ceiling) with 5.000km necessary minimum screening height; actual aerodynamic climb not certified.
**Torch:** thrust per mode = 2 × Pjet / ve and propellant rate = 2 × Pjet / ve². Required Δv and resulting water-at-orbit are calculated per sample, with separate reaction/crew water and custody payload; never negative reaction-water stock. C is conditional on the rotor arithmetic gate, not dense-CO₂ plume viability.
**D-shuttle Round 5a:** 18.000h on Venus, pod docked and rotor parked. Existing kit tip-jet CO2 exchanger runs in GROUND-VENT mode (compressor-fed atmosphere, hot gas exits hub). No additional hardware or mass. Capacity = existing kit thermal rating × 0.300–1.000 ground factor; compressor electric draw = 1.000–5.000% of rejected heat. The SAME house reactor pays cooler+compressor. With Qcold cabin load, Pcool=Qcold/COP and f=compressor fraction, solve Qreactor=max(10% rated, (Pcool+f×Qcold)/(0.75−f)). Qvent=Qreactor+Qcold. Check Qvent≤derate×rated, reactor ≤rating, Pcool+fQvent≤0.75×Qreactor, cooler installed drive/bus, and A2+kit mass. The old 25–300kW hot-loop rejector is NOT the only heat sink. No fictitious mass or second reactor credited; unqualified CO2 flow, heat transfer, compressor and plume physics remain OPEN.
**D-pod:** detached pod, cold-water sensible storage only; **maximum passive hours are OUTPUT** without an invented survival-duration target. No D-pod PASS/FAIL criterion. Passive pod heat load includes electronics and actual crew count.
| Crew | minimum detached pod hours | maximum detached pod hours |
|---:|---:|---:|
| 2 | 0.449 | 7.840 |
| 3 | 0.446 | 7.523 |
| 4 | 0.442 | 7.231 |

**Independent best/worst parameter corners (not contained in every balanced sample):**
- 2 crew passive pod: mathematical parameter corner **0.269–12.429 hours**. Balanced-sample observed maximum 7.840 hours. No minimum required stay time.
- 3 crew passive pod: mathematical parameter corner **0.267–11.919 hours**. Balanced-sample observed maximum 7.523 hours. No minimum required stay time.
- 4 crew passive pod: mathematical parameter corner **0.265–11.450 hours**. Balanced-sample observed maximum 7.231 hours. No minimum required stay time.

### Kit house-reactor power and computed handover
Wayfarer-lineage kit reactor thermal output 100.000–230.000 MW; derived net specific power 40.000kW/kg @ 75.000% conversion, reactor mass 1.875–4.313t plus 0.300–1.000t additional exchanger/ducts. BOTH included once in kit payload and wet-ascent mass, never A2 core mass.
Simultaneous rotor+cooler budget per scenario: **rotor raw heat max = reactor gross thermal − (four-crew cooler electrical / 0.75)**. This is a raw heat upper bound with a DECLARED_2226 perfect heat-transfer interface, NOT independently qualified CO2 exchanger or mast. At 18h surface stay, rotor OFF; 10% min-stable thermal reactor power must be transferred/rejected, producing large heat-disposal demand.
Computed rotor handover (not supplied input): **min 18.000km / median 43.000km / max 67.000km** across 6561 resolved samples. Reach approximate cloud base 48.000km: 2349; reach approximate cloud top 65.000km: 162. These are the *joint hot-duty + induced-speed + heat* screens, not the earlier torch-idle research-only heat ceilings.
**Ground-vent heat dump uses EXISTING KIT tipjet exchanger:** rotor parked, ambient CO2 drawn through compressor and heated via the source hot exchanger, vented through hub. kT ground derate 0.300–1.000 and compressor-power fraction 1.000–5.000% are ASSUMPTION. Reactor cannot go below 10% rated while ON. Heat/energy are conserved in the raw reactor-to-gas and cabin-to-gas ledger. No extra mass.
**Design rule only, NOT gate:** plume points UP, away from pod, door, and ramp. Plume impingement and CO2 hot-gas materials remain physically OPEN.
### Reactor-OFF and 18h battery comparison, NOT gate
Battery energy must power cabin cooler AND the ground vent compressor when the reactor is OFF. Battery density 0.300–1.000 kWh/kg ASSUMPTION, cooler draw over 18h; no battery conversion loss, container, cooling or life credit.
| Crew | cooler kW | ground compressor kW | battery energy kWh | battery mass at high kWh/kg t | battery mass at low kWh/kg t |
|---:|---:|---:|---:|---:|---:|
| 2 | 65.950 | 0.713 | 1199.926 | 1.200 | 4.000 |
| 3 | 67.378 | 0.728 | 1225.918 | 1.226 | 4.086 |
| 4 | 68.807 | 0.744 | 1251.910 | 1.252 | 4.173 |

### Representative reactor and cooling power
| Crew | Load W | cooler electric kW | installed cooler bus kW | reactor run MW | ground vent MW | capacity MW | compressor electric MW | D-shuttle | D-pod hours |
|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 2 | 4616.482 | 65.950 | 25.000 | 10.000 | 10.005 | 30.000 | 0.100 | FAIL | 1.133 |
| 3 | 4716.482 | 67.378 | 25.000 | 10.000 | 10.005 | 30.000 | 0.100 | FAIL | 1.109 |
| 4 | 4816.482 | 68.807 | 25.000 | 10.000 | 10.005 | 30.000 | 0.100 | FAIL | 1.086 |

### Phase-by-phase conserved inventories (first scenario, mode comparisons)
**Mode low**
| Phase | reaction water before → after t | reaction debit t | reserved pod water t | pod cold energy 2/4 crew kWh | cooler input 2/4 crew kW | ground-vent rejection 2/4 crew kW | custody |
|---|---|---:|---:|---|---|---|---|
| entry | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232/5.232 | — | — | ONBOARD |
| rotor deploy | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232/5.232 | — | — | ONBOARD |
| rotor descent | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232/5.232 | — | — | ONBOARD |
| touchdown | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232/5.232 | — | — | ONBOARD |
| surface stay | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232/5.232 | 65.950/67.378/68.807 | 10004.616/10004.716/10004.816 | ONBOARD |
| rotor climb | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232/5.232 | — | — | ONBOARD |
| rotor-to-torch handover | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232/5.232 | — | — | ONBOARD |
| torch ascent to orbit | 23.100 → 0.000 | 23.100 | 0.300 | 5.232/5.232/5.232 | — | — | ONBOARD |
Water to orbit 0.000t; unmet demand 7.104t; achievable ideal Δv 6.330km/s; thrust 1000000.000N.
**Mode high**
| Phase | reaction water before → after t | reaction debit t | reserved pod water t | pod cold energy 2/4 crew kWh | cooler input 2/4 crew kW | ground-vent rejection 2/4 crew kW | custody |
|---|---|---:|---:|---|---|---|---|
| entry | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232/5.232 | — | — | ONBOARD |
| rotor deploy | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232/5.232 | — | — | ONBOARD |
| rotor descent | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232/5.232 | — | — | ONBOARD |
| touchdown | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232/5.232 | — | — | ONBOARD |
| surface stay | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232/5.232 | 65.950/67.378/68.807 | 10004.616/10004.716/10004.816 | ONBOARD |
| rotor climb | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232/5.232 | — | — | ONBOARD |
| rotor-to-torch handover | 23.100 → 23.100 | 0.000 | 0.300 | 5.232/5.232/5.232 | — | — | ONBOARD |
| torch ascent to orbit | 23.100 → 7.530 | 15.570 | 0.300 | 5.232/5.232/5.232 | — | — | ONBOARD |
Water to orbit 7.530t; unmet demand 0.000t; achievable ideal Δv 9.500km/s; thrust 400000.000N.

### Dense-CO₂ torch light-up research and rotor extension
A [magnetic nozzle PIC study](https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2022.876684/full) operates under near-vacuum backgrounds, not Venus 1–70bar CO₂. [NASA rocket base heating](https://ntrs.nasa.gov/citations/20010116591) and [plume recirculation work](https://link.springer.com/article/10.1007/s12567-020-00306-8) show atmosphere/exhaust shear, entrainment and structural heating matter even for conventional jets. There is **no source** validating a multi-GW magnetically driven plume at Venus pressure; plasma neutralization, CO₂ ingestion, magnetic field confinement, base recirculation, induced hot-loop/hull loads, nozzle erosion and restart remain OPEN.
The **5–25km prescribed handover interval has been removed**. For each sample the sizer computes the highest feasible altitude within the VIRA table and declared rotor duty/thermal/speed bounds. Rotor-only flight to 30–50km increases MW demand; these values are **demand**, not reactor-specific output or blade certification.
| Altitude km | ambient bar | rotor shaft MW min–max | tip-jet heat MW min–max |
|---:|---:|---:|---:|
| 30.000 | 9.581 | 9.339–17.139 | 26.682–157.851 |
| 40.000 | 3.501 | 14.177–26.019 | 40.507–239.639 |
| 50.000 | 1.066 | 23.566–43.248 | 67.330–398.325 |
At 30–50km the new reactor 100–230MW raw thermal is drawn from the kit. Its actual gas-side delivered heat is a DECLARED_2226 model assumption; exchanger efficiency, ducting, rotor life, and light-up physics remain unqualified. Moving handover upward helps ambient backpressure but does NOT certify a fusion plasma nozzle even near 1bar. Torch dense-atmosphere viability remains OPEN.
### Physical holds after conditional gate results
The following declared required physics is still OPEN: venus.torch_atmosphere_viability, venus.entry_vehicle_thermal_qualification, kit individual hold geometry and hot blade joints, research.sphere hot pressurization and actual hatch/seal, power.reactor_waste_heat_MW. No PASS from this sizer overrides those holds.

## Representative sampled outcomes
| Sample | Dry with kit t | A | Docked core t | A2 | packed kit m³ | KV | KF | B | Rotor | Water C | D-shuttle 2 | D-shuttle 4 |
|---:|---:|---|---:|---|---:|---|---|---|---|---|---|---||
| 0 | 25.842 | PASS | 19.917 | PASS | 32.917 | PASS | OPEN | OPEN | PASS | PASS | FAIL | FAIL | 
| 1 | 43.048 | FAIL | 31.335 | PASS | 65.069 | FAIL | FAIL | OPEN | PASS | PASS | PASS | PASS | 
| 2 | 45.441 | FAIL | 34.373 | FAIL | 61.493 | FAIL | FAIL | OPEN | PASS | PASS | FAIL | FAIL | 
| 3 | 38.895 | FAIL | 28.520 | PASS | 32.937 | PASS | OPEN | OPEN | PASS | PASS | PASS | PASS | 
| 4 | 41.298 | FAIL | 29.411 | PASS | 37.738 | PASS | OPEN | OPEN | PASS | PASS | PASS | PASS | 
| 5 | 41.124 | FAIL | 32.581 | PASS | 27.123 | PASS | OPEN | OPEN | PASS | PASS | FAIL | FAIL | 
| 6 | 37.324 | FAIL | 26.024 | PASS | 25.111 | PASS | OPEN | OPEN | PASS | PASS | PASS | PASS | 
| 7 | 44.931 | FAIL | 35.119 | FAIL | 21.806 | PASS | OPEN | OPEN | PASS | PASS | FAIL | FAIL | 
| 8 | 38.400 | FAIL | 29.756 | PASS | 19.208 | PASS | OPEN | OPEN | PASS | PASS | PASS | PASS | 

## Full hashed input JSON (verbatim fields and provenance)
```json
{
  "header": "ALL bodies. ALL sponsors. 2026-2226.",
  "schema": "LOOM.SHUTTLE_SIZER_INPUTS_V1",
  "status": "NON_CANON_ENGINEERING_SENSITIVITY_RESIZE_R1_R5_20261103",
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
    "round_4": "kT approved 2026-11-03; same draft branches; all gate inputs frozen; idle heat research only",
    "round_5": "kT APPROVED 2026-11-03; HOUSE REACTOR kit, bounded 100–230MW heat and derived kit mass; review before merge; stage 3 after merge; torch idle unchanged research only",
    "round_5a": "kT APPROVED 2026-11-03: existing kit tipjet heat exchanger runs ground-vent mode, rotor parked; merge after report per user's direct approval. Stage 3 afterwards.",
    "resize": "kT APPROVED 2026-11-03 R1-R5; 3.8m hull, 2.5m/3crew pod, TPS 1-2t base ASSUMPTION, original total conserved"
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
      "value": 3.8,
      "unit": "m",
      "provenance": "ASSUMPTION",
      "source": "kT APPROVED R2/R3 2026-11-03",
      "description": "Stowed outer hull diameter; revised shuttle 3.8m/2.5m/3crew"
    },
    "crew_pod_outer_diameter_m": {
      "value": 2.5,
      "unit": "m",
      "provenance": "ASSUMPTION",
      "source": "kT APPROVED R2/R3 2026-11-03",
      "description": "Ti sphere OD; revised shuttle 3.8m/2.5m/3crew"
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
      "value": 3,
      "unit": "crew",
      "provenance": "ASSUMPTION",
      "source": "kT APPROVED R2/R3 2026-11-03",
      "description": "Optional crew 2 or 4; revised shuttle 3.8m/2.5m/3crew"
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
      "min": 2.277696793,
      "max": 5.409529883,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "R2/R3 2026-11-03; scaled original bounds by 0.711780248; constant relative wall thickness, R^3 geometric mass only; buckling NOT qualified",
      "description": "constant relative wall thickness, R^3 geometric mass only; buckling NOT qualified"
    },
    "hull_thermal_structure_t": {
      "min": 7.953488372,
      "max": 12.372093023,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "R2/R3 2026-11-03; scaled original bounds by 0.883720930; constant hull length, lateral skin-area proxy; internal structure NOT qualified",
      "description": "constant hull length, lateral skin-area proxy; internal structure NOT qualified"
    },
    "pressure_pod_fittings_seals_t": {
      "min": 0.398596939,
      "max": 0.956632653,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "R2/R3 2026-11-03; scaled original bounds by 0.797193878; pod surface-area proxy, not qualified hatch/seal load",
      "description": "pod surface-area proxy, not qualified hatch/seal load"
    },
    "folding_rover_chassis_t": {
      "min": 0.530232558,
      "max": 1.060465116,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "R2/R3 2026-11-03; scaled original bounds by 0.883720930; available transverse packaging proxy; suspension/track NOT qualified",
      "description": "available transverse packaging proxy; suspension/track NOT qualified"
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
      "description": "TOTAL existing entry TPS 3-6t; dynamically split into core base_entry_tps_core_t and kit-only extra, with mass conservation; never double-count."
    },
    "landing_gear_door_ramp_t": {
      "min": 0.706976744,
      "max": 1.325581395,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "R2/R3 2026-11-03; scaled original bounds by 0.883720930; door/ramp width proxy; actual hinges/loads NOT qualified",
      "description": "door/ramp width proxy; actual hinges/loads NOT qualified"
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
    },
    "kit_house_reactor_t": {
      "min": 1.875,
      "max": 4.3125,
      "unit": "t",
      "provenance": "DECLARED_2226",
      "source": "DERIVED from power.kit_house_reactor_thermal_MW, power.kit_house_reactor_net_specific_kW_per_kg and conversion efficiency; kT 2026-11-03",
      "description": "DEPENDENT, NEVER independently sampled: thermal MW × 0.75×1000kW/MW ÷40kW/kg ÷1000kg/t = 1.875–4.3125t; excluded from independent sample fields; included exactly once in dry and kit payload ledgers."
    },
    "kit_house_exchanger_ducts_t": {
      "min": 0.3,
      "max": 1,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT 2026-11-03 additional kit house-reactor heat exchanger / high-temperature transfer duct sensitivity",
      "description": "Additional dedicated kit house-reactor heat exchanger/duct mass above existing tipjet_ducts_compressors_t and venus_hot_loop_thermal_kit_t. Disjoint machinery ledger; actual gas-mast thermal/pressure qualification OPEN."
    },
    "base_entry_tps_core_t": {
      "min": 1,
      "max": 2,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "2026-11-03 sensitivity hypothesis; NASA 1997 Mars reference mission uses 15% entry aeroshell mass as coarse reference, NOT a vehicle-specific TPS design; NASA PICA heritage; https://nss.org/wp-content/uploads/1997-NASA-Human-Exploration-Of-Mars-Reference-Mission.pdf ; https://science.nasa.gov/science-research/science-enabling-technology/technology-highlights/protecting-future-planetary-missions-from-extreme-heat/",
      "description": "Base Mars TPS assumed 1-2t inside CORE; existing 3-6t total entry TPS is conserved; extra Venus kit TPS = total minus this value. Range is deliberately tentative, NOT NASA-derived or qualified."
    },
    "extra_venus_entry_tps_t": {
      "value": null,
      "unit": "t",
      "provenance": "DERIVED",
      "source": "mass.entry_tps_t - mass.base_entry_tps_core_t",
      "description": "Derived kit TPS only; total entry_tps_t is not independently included in dry mass."
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
      "value": null,
      "unit": "MW thermal",
      "provenance": "OPEN",
      "source": "DERIVED OUTPUT: kit house-reactor thermal raw output minus concurrent four-crew cooler electric divided by direct conversion efficiency. Not independent input or missing parameter.",
      "description": "Derived per sample, not sampled/credited from torch idle. Actual exchanger transfer efficacy to heated CO2 remains unqualified."
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
    },
    "kit_house_reactor_thermal_MW": {
      "min": 100,
      "max": 230,
      "unit": "MW thermal (raw)",
      "provenance": "DECLARED_2226",
      "source": "kT 2026-11-03; https://github.com/loom-2226/loom-2226/blob/main/wayfarer/docs/SHIP_POWER_BUDGET_2026_11_01.md",
      "description": "Independent dedicated Venus/Titan kit house-reactor thermal power interval. NOT torch idle heat. Switched between thermal-to-tipjet and 75% direct conversion to cooler electric, with raw thermal allocation conserved. Unqualified direct gas exchanger and radiator geometry."
    },
    "kit_house_reactor_net_specific_kW_per_kg": {
      "value": 40,
      "unit": "kW/kg net electric",
      "provenance": "DECLARED_2226",
      "source": "kT 2026-11-03 Round 5, same Wayfarer house-reactor lineage; https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json ; https://github.com/loom-2226/loom-2226/blob/main/wayfarer/docs/SHIP_POWER_BUDGET_2026_11_01.md",
      "description": "Same Wayfarer twin D-He3 house units: 2×50 MW net each, 1.25t each at 40kW/kg NET."
    },
    "kit_house_reactor_direct_conversion_efficiency": {
      "value": 0.75,
      "unit": "fraction",
      "provenance": "DECLARED_2226",
      "source": "kT 2026-11-03 Round 5, same Wayfarer house-reactor lineage; https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json ; https://github.com/loom-2226/loom-2226/blob/main/wayfarer/docs/SHIP_POWER_BUDGET_2026_11_01.md",
      "description": "75% direct converter electrical efficiency; thermal raw drawn for cooler electricity = cooler electrical/0.75."
    },
    "kit_house_reactor_min_stable_fraction": {
      "value": 0.1,
      "unit": "fraction",
      "provenance": "DECLARED_2226",
      "source": "kT 2026-11-03 Round 5, same Wayfarer house-reactor lineage; https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json ; https://github.com/loom-2226/loom-2226/blob/main/wayfarer/docs/SHIP_POWER_BUDGET_2026_11_01.md",
      "description": "10% minimum online output each from Wayfarer house-reactor declarations; NOT main torch idle."
    },
    "kit_house_reactor_source_net_MW_at_100thermal": {
      "value": 75,
      "unit": "MW electric",
      "provenance": "DECLARED_2226",
      "source": "kT 2026-11-03 Round 5, same Wayfarer house-reactor lineage; https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json ; https://github.com/loom-2226/loom-2226/blob/main/wayfarer/docs/SHIP_POWER_BUDGET_2026_11_01.md",
      "description": "Derived 100MW thermal *75% for comparison, electrical distribution may be lower."
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
        "source": "legacy sensitivity only; resized pod rated for 3 not 4",
        "description": "Comparison only; not new pod crew capacity"
      },
      {
        "value": 3,
        "unit": "crew",
        "provenance": "KT_DECISION",
        "source": "R3 2026-11-03",
        "description": "Authoritative three-crew case"
      },
      {
        "value": 4,
        "unit": "crew",
        "provenance": "ASSUMPTION",
        "source": "legacy sensitivity only; resized pod rated for 3 not 4",
        "description": "Comparison only; not new pod crew capacity"
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
      "description": "Heat dissipated into hot loop at >Venus ambient; rate only, geometry not certified. Round 5a ground-vent rejects main reactor surplus via existing KIT heat exchanger, not this old coolant-only cap; retained as historical comparison and ignored by D-shuttle gate."
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
      "description": "Installed cooler drive/power handling limit, separate from house reactor net output and electrical interface cap."
    },
    "reactor_aux_electric_power_available_kW": {
      "min": 25,
      "max": 200,
      "unit": "kW",
      "provenance": "ASSUMPTION",
      "source": "Analyst screening proposal 2026-11-03, NON-CANON; not independently qualified",
      "description": "Installed cooler auxiliary electrical interface/bus limit only (25–200kW), NOT separate reactor source. House reactor electrical available = thermal MW×0.75×1000; take min of bus, cooler input limit and reactor output."
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
    "passive_pod_target_h": null,
    "ground_vent_derate": {
      "min": 0.3,
      "max": 1,
      "unit": "fraction",
      "provenance": "ASSUMPTION",
      "source": "kT APPROVED 2026-11-03 Round 5a (non-canon)",
      "description": "No ram air; compressor-fed ground CO2 mass flow. Actual hub vent physics not qualified. No new exchanger hardware or mass."
    },
    "ground_vent_compressor_fraction": {
      "min": 0.01,
      "max": 0.05,
      "unit": "fraction of vented heat",
      "provenance": "ASSUMPTION",
      "source": "kT APPROVED 2026-11-03 Round 5a (non-canon)",
      "description": "Ground CO2 compressor electric load relative to total hot-gas vent heat; powered by SAME house reactor net output, allocated from thermal budget. No invented extra compressor mass (existing tipjet ducts/compressors)."
    },
    "ground_vent_plume_orientation": {
      "value": null,
      "unit": "design only",
      "provenance": "OPEN",
      "source": "kT 2026-11-03 Round 5a design rule, NON-GATE",
      "description": "Plume must point UP, away from pod, door and ramp; actual directional clearance and thermochemistry not demonstrated; not scored as gate."
    },
    "reactor_off_18h_battery_specific_energy_kWh_kg": {
      "min": 0.3,
      "max": 1,
      "unit": "kWh/kg",
      "provenance": "ASSUMPTION",
      "source": "kT APPROVED 2026-11-03 Round 5a (non-canon)",
      "description": "Reactor-OFF and 18h battery-only electric COOLER, plus 18h cold storage not credited. Comparison output only, no gate; ignores cooling battery self-heat and actual physical packaging."
    },
    "ground_vent_accounting": "Thermal reactor >=10% rated; house raw thermal Q; ventilated heat equals Q + cabin cold heat; compressor electricity = f*Qvent, cooler electric = Qcold/COP, raw reactor required for both electric draws >=(Pcool+Pcomp)/0.75; run power Qrun=max(10%*Prated,(Pcool+f*Qcold)/(.75-f)), Qrun<=Prated; vent capacity=derate*Prated; no double count of compressor/cooler electricity in Qvent because extracted from Qrun and returned as heat. No external separate 25–300kW sink required in ground-vent mode. Existing installed cooler electric and aux bus caps still apply ONLY to cooler electrical draw, compressor is a separate already-existing tipjet compressor bus; new compressor power tap geometry remains unqualified."
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
      "value": null,
      "unit": "km",
      "provenance": "OPEN",
      "source": "PER-SAMPLE DERIVED OUTPUT",
      "description": "Computed from climb until rotor heat, available reactor power after simultaneous cooling, tip speed, hot duty or VIRA model ceiling; no arbitrary 5–25km cap. Torch-in-dense-CO2 physical feasibility remains OPEN below computed altitude."
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
      "description": "Full torch ignition in CO2 remains physically OPEN independent of rotor's newly computed handover altitude, even above cloud top; magnetic nozzle/reentry plume not qualified."
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
    ],
    "minimum_rotor_handover_screen_km": {
      "value": 5,
      "unit": "km",
      "provenance": "ASSUMPTION",
      "source": "Carry forward original kT 5–25km handover screen LOWER bound; upper input cap deleted for Round 5",
      "description": "Necessary minimum ascent height for rotor screen, NOT a fixed or desired handover altitude. Handover is computed per sample."
    }
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
      "extra_venus_entry_tps_t",
      "venus_hot_loop_thermal_kit_t",
      "venus_cooler_t",
      "kit_house_reactor_t",
      "kit_house_exchanger_ducts_t"
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
    },
    "house_reactor_power_source": "power.kit_house_reactor_thermal_MW",
    "house_reactor_mass_ledger": "mass.kit_house_reactor_t (DERIVED, includes converter at net specific power), mass.kit_house_exchanger_ducts_t (added) both in payload",
    "house_reactor_thermal_partition": "Rotor phase: tipjet raw heat ≤ reactor thermal output - 4-crew cabin cooler electric/(direct conversion). Surface phase: rotor OFF, cooler supplied via reactor direct electrical conversion; never count both full outputs simultaneously.",
    "ground_vent_reuse": "existing tipjet heat exchanger and compressor reused while rotor parked; no new dry-part mass, no duplication. All ventilation occurs while on surface; rotor-gas thermodynamics and plume impingement remain OPEN."
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
          "provenance": "DECLARED_2226",
          "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json",
          "description": "Declared current working torch jet ceiling, not measured reactor thermal power Source ledger labels this engineering-assumption or derived, not experimentally qualified."
        },
        "wayfarer_propulsion_allocation_t": {
          "value": 160,
          "unit": "t",
          "provenance": "DECLARED_2226",
          "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json",
          "description": "Engineering-assumption propulsion ledger total; not hardware validation Source ledger labels this engineering-assumption or derived, not experimentally qualified."
        },
        "wayfarer_reactor_t": {
          "value": 85,
          "unit": "t",
          "provenance": "DECLARED_2226",
          "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json",
          "description": "Share of propulsion total Source ledger labels this engineering-assumption or derived, not experimentally qualified."
        },
        "wayfarer_shadow_shield_t": {
          "value": 45,
          "unit": "t",
          "provenance": "DECLARED_2226",
          "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json",
          "description": "Share of propulsion total Source ledger labels this engineering-assumption or derived, not experimentally qualified."
        },
        "wayfarer_magnetic_nozzle_t": {
          "value": 30,
          "unit": "t",
          "provenance": "DECLARED_2226",
          "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json",
          "description": "Share of propulsion total Source ledger labels this engineering-assumption or derived, not experimentally qualified."
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
        "provenance": "DECLARED_2226",
        "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/docs/SHIP_POWER_BUDGET_2026_11_01.md",
        "description": "Burn-only source raw extraction, not an idle source kT accepted Wayfarer engineering declaration; tap hardware remains unqualified."
      },
      "wayfarer_torch_tap_conversion": {
        "value": 0.75,
        "unit": "fraction",
        "provenance": "DECLARED_2226",
        "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/docs/SHIP_POWER_BUDGET_2026_11_01.md",
        "description": "Burn-only conversion, raw thermal/electromagnetic energy to electrical magnets kT accepted Wayfarer engineering declaration; tap hardware remains unqualified."
      },
      "wayfarer_torch_tap_net_MWe": {
        "value": 47.52,
        "unit": "MWe",
        "provenance": "DECLARED_2226",
        "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/docs/SHIP_POWER_BUDGET_2026_11_01.md",
        "description": "Burn-only magnets/cryocooler net, physical tap OPEN kT accepted Wayfarer engineering declaration; tap hardware remains unqualified."
      },
      "wayfarer_torch_tap_waste_MW": {
        "value": 15.84,
        "unit": "MW",
        "provenance": "DECLARED_2226",
        "source": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/docs/SHIP_POWER_BUDGET_2026_11_01.md",
        "description": "Burn-only conversion waste, not an idle rotor heat allocation kT accepted Wayfarer engineering declaration; tap hardware remains unqualified."
      },
      "case_scope": "Heat-only rotor-disk momentum demand sweep at mass/FM/thermal-to-rotor corners; no safe tip-speed, duty, ascent acceleration, reactor electrical load, 735K mast heat loss, or transport physics certified. DO NOT FEED INTO ANY GATE. Round 5 explicitly sources rotor heat from a SEPARATE Venus-kit 100–230MW D–He3 house reactor, NOT from this idle torch hypothesis; do not credit this sensitivity in gates.",
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
