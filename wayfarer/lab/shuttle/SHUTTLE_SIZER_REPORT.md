# LOOM shuttle sizer v1 — Stage 1 result
ALL bodies. ALL sponsors. 2026-2226.

**Status:** NON-CANON / NON-RUNTIME / UNQUALIFIED ENGINEERING SENSITIVITY. No machine constants promoted.
**Input hash / run identity (Git blob SHA-1):** `61d63f2b425be6e261c3180ebc57fe1d0bb22bea`. Raw UTF-8 input identity is SHA-1 of `blob <byte-length>\\0` plus JSON bytes.
**Single source input:** `wayfarer/lab/shuttle/shuttle_inputs.json` (all inputs printed at end).
**Files generated:** `SHUTTLE_SIDE_VIEW.svg`, `SHUTTLE_MASS_WATERFALL.svg`.

## Gate summary
| Gate | Verdict | Finding |
|---|---|---|
| A docked dry ≤ 34.200 t | **OPEN** | Only Ti geometric shell range 3.200–7.600 t; 11 other dry mass entries OPEN; no admissible total. |
| B G8 bay fully fitted | **OPEN** | Necessary hull length 12.800 / available 12.800m, diameter 4.300 / available 4.300m, folded span 12.000m; mast/hub/hinge and actual positioning OPEN. |

## Stage 1 — mass and fit
**Necessary geometry:** G8 bay inner length 13.800m, axial clearance each end 0.500m; bore radius 2.400m, radial clearance 0.250m. Remaining *allowable* diameter and length margins are exactly 0.000m and 0.000m. Any mast or hub exterior to the existing hull is a fit FAILURE.
**Folded rotor:** four blades on one 12.000m tip-jet rotor; two fold forward and two aft. The ideal collinear span is 12.000m, leaving 0.800m for true hinge/root/end geometry. Rotor mount over CG and crew pod station are OPEN; the side view locates neither as engineering authority.
**Dry-mass components (independently conserved):**
| Component | Range / value (t) | Provenance |
|---|---:|---|
| pressure_pod_titanium_shell_t | 3.200–7.600 | PROJECTION |
| hull_thermal_structure_t | OPEN | OPEN |
| pressure_pod_fittings_seals_t | OPEN | OPEN |
| folding_rover_chassis_t | OPEN | OPEN |
| single_12m_rotor_blades_hub_mast_t | OPEN | OPEN |
| tipjet_ducts_compressors_t | OPEN | OPEN |
| torch_low_high_engine_t | OPEN | OPEN |
| small_belly_thrusters_t | OPEN | OPEN |
| reactor_power_distribution_t | OPEN | OPEN |
| crew_habitat_thermal_package_t | OPEN | OPEN |
| custody_capsule_dry_t | OPEN | OPEN |
| avionics_controls_yaw_t | OPEN | OPEN |

**Feasibility map:** 3 shell-projection samples; other masses cannot be assigned without evidence.
| Ti shell assumed (t) | Remaining total budget for ALL other dry components (t) | Gate A | Gate B |
|---:|---:|---|---|
| 3.200 | 31.000 | OPEN | OPEN |
| 5.400 | 28.800 | OPEN | OPEN |
| 7.600 | 26.600 | OPEN | OPEN |

Necessary but insufficient condition: **sum(other component dry masses) ≤ remaining budget**; this is not an earned PASS. Capsule has ONE dry-mass row and may not be counted a second time in the custody ledger.

## Inputs driving the result and provenance boundaries
- A: Ti shell is the only interval-backed dry mass. Single 12m rotor mass is OPEN; #453's 1–10t *four 6m rotor* assumption is **not transferred**.
- B: no dimensional clearance beyond the stated hull; hub thickness, CG, wing/mast stowage geometry unresolved.
- Light-body access and Titan are Stage 3, not evaluated here. No modification to canon/Wayfarer geometry/Navigator.

## Full hashed input JSON (verbatim)
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
    "atmosphere_reference": "Seiff et al. VIRA (1985), IPPW-6 (2008) JPL/T. Balint adaptation"
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
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "No qualified structural sizing"
    },
    "pressure_pod_fittings_seals_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "No rated door/windows/pressure shell fit-out"
    },
    "folding_rover_chassis_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "Wheeled kneeling chassis mass OPEN"
    },
    "single_12m_rotor_blades_hub_mast_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "#453 four 6m rotor 1-10t assumption cannot be transferred to one 12m rotor"
    },
    "tipjet_ducts_compressors_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "Hot CO2 tip-jet mass"
    },
    "torch_low_high_engine_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "LOST sizer, no replacement engine mass"
    },
    "small_belly_thrusters_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "kT baseline",
      "description": "Moon Mars Mercury thrusters"
    },
    "reactor_power_distribution_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "No credible compact source mass for rotor/torch"
    },
    "crew_habitat_thermal_package_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "Cooling, insulation, crew thermal mass"
    },
    "custody_capsule_dry_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "kT baseline",
      "description": "Ejectable secure packet capsule, unique dry ledger"
    },
    "avionics_controls_yaw_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "kT baseline",
      "description": "Yaw control, avionics, electronics"
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
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "phase-specific actual mission manifest not yet selected",
      "description": "Conserved ledger, cannot assume entire 23.1t usable"
    },
    "crew_thermal_water_initial_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "separate tank or marked inventory needed",
      "description": "Separate from reaction water, no double use"
    },
    "reaction_water_entry_debit_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "entry physics missing",
      "description": "Cannot infer entry delta-v"
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
      "source": "trajectory and torch model missing",
      "description": "Mission total not predicted"
    },
    "crew_water_heating_delta_T_K": {
      "value": null,
      "unit": "K",
      "provenance": "OPEN",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "Without cold-water reservoir window, cannot compute usable stored cold"
    },
    "crew_water_cold_mass_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "May be subset of crew thermal inventory; no double use"
    },
    "crew_water_heat_capacity_J_per_kg_K": {
      "value": null,
      "unit": "J/(kg K)",
      "provenance": "OPEN",
      "source": "https://github.com/loom-2226/loom-2226/blob/research/shuttle-tech-opportunities-20261102/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "Real water heat capacity vs state and high-temperature system boundary OPEN"
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
      "unit": "MW",
      "provenance": "OPEN",
      "source": "hot source-to-blade heat delivery not demonstrated",
      "description": "Necessary to choose physical handover altitude"
    },
    "rotor_safe_tip_speed_mps": {
      "value": null,
      "unit": "m/s",
      "provenance": "OPEN",
      "source": "material/blade Mach not qualified",
      "description": "Blade stress and compressibility ceiling"
    },
    "rotor_hot_duty_limit_s": {
      "value": null,
      "unit": "s",
      "provenance": "OPEN",
      "source": "bearings and seals life unknown",
      "description": "Altitude duty and surface hold"
    },
    "rotor_climb_rate_mps": {
      "value": null,
      "unit": "m/s",
      "provenance": "OPEN",
      "source": "net climb from available excess power unknown",
      "description": "Cannot integrate phase time"
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
      "value": null,
      "unit": "W",
      "provenance": "OPEN",
      "source": "metabolic/embodiment power requirements unqualified",
      "description": "Separate human/synthetic capabilities; no arbitrary heat constant"
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
      "value": null,
      "unit": "km",
      "provenance": "OPEN",
      "source": "OUTPUT_UNRESOLVED_UNTIL_ROTOR_LIMITS_AVAILABLE",
      "description": "Never select arbitrary cloud altitude"
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
    }
  },
  "capsule": {
    "dry_mass_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "kT",
      "description": "Also mass.custody_capsule_dry_t; same physical inventory, not double counted"
    },
    "content_mass_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "kT",
      "description": "Unknown secure data carrier contents"
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
    }
  }
}
```
