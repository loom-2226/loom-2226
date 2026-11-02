# LOOM Shuttle Sizer v1 — Stage 1
ALL bodies. ALL sponsors. 2026–2226.

**CLASS: Engineering sensitivity / ASSUMPTION / NON-CANON / NOT QUALIFICATION.**
**Run identity:** Git blob SHA-1 of full UTF-8 input JSON incl. stage: `b0ca9cfa68c643c9f28257b0b5e207b00993f262`.
**Run:** `node wayfarer/lab/shuttle/shuttle_sizer.mjs --stage 1`.
**Graphics:** `SHUTTLE_SIDE_VIEW.svg`, `SHUTTLE_MASS_WATERFALL.svg`.

## Computed gates: per-sample status and sample PASS fractions
Design: 6561 balanced, pairwise-stratified min/mid/max samples over 15 independent swept inputs. This is **not** full Cartesian probability; PASS fractions are empirical design fractions, not calibrated probabilities.
| Gate | PASS | FAIL | OPEN | PASS / resolved | Missing required inputs |
|---|---:|---:|---:|---:|---|
| A | 810 | 5751 | 0 | 12.35% | none in numeric screen; physical qualification holds separate |
| B | 0 | 0 | 6561 | n/a | geometry.mast_stowed_extra_diameter_m, geometry.hub_axial_length_m, geometry.mast_retracted_height_m, geometry.crew_pod_x_m, geometry.rotor_mast_x_m, geometry.rotor_retracted_cg_m, geometry.pod_door_ramp_external_excursion_m |

### Gate A mass envelope and historical comparison
Component sums min / midpoint / max: **25.250 / 38.375 / 51.500 t**. Gate A limit 34.200 t.
Historical LOST-sizer empty mass 35.400 t is the **v1 comparison** while LOST historical output is **27.900t** in PR #453; neither is an equality target or an input mass offset.
Actual midpoint versus **27.9t** historical output: **10.475 t** difference (27.900t historical anchored in #453 and should not be mistaken for a constraint).
| Distinct dry component | min | mid | max | provenance |
|---|---:|---:|---:|---|
| pressure_pod_titanium_shell_t | 3.200 | 5.400 | 7.600 | PROJECTION |
| hull_thermal_structure_t | 9.000 | 11.500 | 14.000 | ASSUMPTION |
| pressure_pod_fittings_seals_t | 0.500 | 0.850 | 1.200 | ASSUMPTION |
| folding_rover_chassis_t | 0.600 | 0.900 | 1.200 | ASSUMPTION |
| single_12m_rotor_blades_hub_mast_t | 0.800 | 1.400 | 2.000 | ASSUMPTION |
| tipjet_ducts_compressors_t | 0.300 | 0.650 | 1.000 | ASSUMPTION |
| torch_low_high_engine_t | 4.000 | 7.000 | 10.000 | ASSUMPTION |
| small_belly_thrusters_t | 0.200 | 0.400 | 0.600 | ASSUMPTION |
| reactor_power_distribution_t | 0.300 | 0.650 | 1.000 | ASSUMPTION |
| crew_habitat_thermal_package_t | 1.000 | 1.500 | 2.000 | ASSUMPTION |
| custody_capsule_dry_t | 0.050 | 0.125 | 0.200 | ASSUMPTION |
| avionics_controls_yaw_t | 0.500 | 0.850 | 1.200 | ASSUMPTION |
| entry_tps_t | 3.000 | 4.500 | 6.000 | ASSUMPTION |
| landing_gear_door_ramp_t | 0.800 | 1.150 | 1.500 | ASSUMPTION |
| water_tank_insulated_t | 1.000 | 1.500 | 2.000 | ASSUMPTION |

### Gate B G8 stowed fit
Necessary-dimensional result: **PASS**. G8 allowable L 12.800 m, diameter 4.300 m; hull 12.800 × 4.300 m, folded theoretical blade span 12.000m. Real margins: L 0.000m, D 0.000m.
Full fit verdict OPEN; explicit REQUIRED nulls: geometry.mast_stowed_extra_diameter_m, geometry.hub_axial_length_m, geometry.mast_retracted_height_m, geometry.crew_pod_x_m, geometry.rotor_mast_x_m, geometry.rotor_retracted_cg_m, geometry.pod_door_ramp_external_excursion_m. No arbitrary hub or mast geometry credited.

## Three most influential inputs per gate (one-at-a-time)
Each factor is set to **min / mid / max** while 81 balanced baselines hold all other inputs. Rank by change in PASS fraction; if no boundary crosses, rank by change in physical margin.
**Gate A**
| Input | PASS % at min/mid/max | Δ PASS | Δ margin if no flip |
|---|---|---:|---:|
| mass.torch_low_high_engine_t | 33.3 / 6.2 / 3.7 | 29.6 pp | 6.000 |
| mass.hull_thermal_structure_t | 25.9 / 11.1 / 3.7 | 22.2 pp | 5.000 |
| mass.pressure_pod_titanium_shell_t | 27.2 / 8.6 / 4.9 | 22.2 pp | 4.400 |

## Representative sample outcomes
| # | Dry t | A | B |  |
|---:|---:|---|---||
| 0 | 25.250 | PASS | OPEN | 
| 1 | 31.850 | PASS | OPEN | 
| 2 | 38.450 | FAIL | OPEN | 
| 3 | 36.025 | FAIL | OPEN | 
| 4 | 36.175 | FAIL | OPEN | 
| 5 | 40.075 | FAIL | OPEN | 
| 6 | 40.350 | FAIL | OPEN | 
| 7 | 44.250 | FAIL | OPEN | 
| 8 | 44.400 | FAIL | OPEN | 

## Full input JSON: exact bytes determine run identity
```json
{
  "header": "ALL bodies. ALL sponsors. 2026-2226.",
  "schema": "LOOM.SHUTTLE_SIZER_INPUTS_V1",
  "status": "NON_CANON_ENGINEERING_SCREEN_STAGE1_STAGE2_UNQUALIFIED",
  "authority": "kT approved fresh sizer; no edits to canon, Wayfarer, Navigator or historical research",
  "origin": {
    "source_453": "https://github.com/loom-2226/loom-2226/pull/453",
    "bay": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/config/wayfarer_v05_inputs.json",
    "qualification": "https://github.com/loom-2226/loom-2226/blob/main/wayfarer/docs/CERTIFICATION_BASIS.md",
    "atmosphere": "https://repository.gatech.edu/server/api/core/bitstreams/681dac66-9414-4c40-8f27-9bd92f6a385f/content",
    "atmosphere_reference": "Seiff et al. VIRA (1985), IPPW-6 (2008) JPL/T. Balint adaptation",
    "declared_assumptions": "kT/Claude 2026-11-02; kT-approved explicit model sensitivities, all labeled ASSUMPTION"
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
      "provenance": "ASSUMPTION",
      "source": "kT/Claude 2026-11-02",
      "description": "Editable three-level min/mid/max sizing sensitivity. Not qualified hardware. "
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
      "value": null,
      "unit": "kW",
      "provenance": "OPEN",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "Warm heat rejection to 735K atmosphere unqualified"
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
      "value": null,
      "unit": "kW",
      "provenance": "OPEN",
      "source": "No kT declared installed cooler and hot-side sink available",
      "description": "Passive sensible cold-water Gate D computed. Additional active cooling not credited."
    }
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
      "description": "Required for physical orbit mission but NOT required for conditional Gate C rocket-equation water balance. Physical closure remains OPEN."
    },
    "entry_vehicle_thermal_qualification": {
      "value": null,
      "unit": "qualified TPS",
      "provenance": "OPEN",
      "source": "No entry aerothermal test supplied",
      "description": "Physical entry qualification OPEN but reaction water Gate C still conditional."
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
    "value": 1,
    "unit": "stage",
    "provenance": "ASSUMPTION",
    "source": "kT stage 1 approved mass and fit workflow",
    "description": "Hashed input state. Stage 2 uses its own JSON revision; CLI stage must agree."
  }
}
```
