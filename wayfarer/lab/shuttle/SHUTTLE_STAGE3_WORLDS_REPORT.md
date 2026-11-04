# LOOM Shuttle Stage 3: World-sized belly propulsion (PR #458 correction)
ALL bodies. ALL sponsors. 2026–2226.

**Authority: RESEARCH / NON-CANON / NON-RUNTIME / NON-QUALIFICATION.**
Merged Stage2 baseline JSON blob: a1a8db40fb53ab889fa9bafbe52c299b7a5e529d. Stage3 editable source JSON blob: c75ce80f29dc0113775a122f4c9ede8ac21430f7.
6,561 deterministic min/mid/max coordinate-balanced combinations per world; 38 individually varied input fields. **Design fractions, not engineering reliability probabilities.**
Independent CLI reproduction of earlier Stage3 version reported by Claude through kT. This revision uses reevaluated computational functions; NEW Node CLI reproduction not claimed.

## World gate fractions
| World | Gate | PASS | FAIL | OPEN | N/A | PASS among resolved |
|---|---|---:|---:|---:|---:|---:|
| Titan | A2 | 5103 | 1458 | 0 | 0 | 77.778% |
| Titan | KIT_VOLUME | 5103 | 1458 | 0 | 0 | 77.778% |
| Titan | LIFT_SCREEN | 6561 | 0 | 0 | 0 | 100.000% |
| Titan | ROTOR_MODEL_TOP | 3645 | 2916 | 0 | 0 | 55.556% |
| Titan | WATER_IDEAL_FLOOR | 6561 | 0 | 0 | 0 | 100.000% |
| Titan | ORBIT_FULL | 0 | 0 | 6561 | 0 | n/a |
| Titan | SURFACE_THERMAL | 0 | 0 | 6561 | 0 | n/a |
| Titan | BAY_FULL | 0 | 0 | 6561 | 0 | n/a |
| Titan | FLIGHT_TOTAL | 0 | 2430 | 4131 | 0 | 0.000% |
| Moon | A2 | 5103 | 1458 | 0 | 0 | 77.778% |
| Moon | A2_CHEM | 5103 | 1458 | 0 | 0 | 77.778% |
| Moon | KIT_VOLUME | 0 | 0 | 0 | 6561 | n/a |
| Moon | LIFT_SCREEN | 0 | 0 | 0 | 6561 | n/a |
| Moon | ROTOR_MODEL_TOP | 0 | 0 | 0 | 6561 | n/a |
| Moon | WATER_IDEAL_FLOOR | 0 | 0 | 0 | 6561 | n/a |
| Moon | BELLY_TW_E | 6561 | 0 | 0 | 0 | 100.000% |
| Moon | BELLY_TW_C | 6561 | 0 | 0 | 0 | 100.000% |
| Moon | BELLY_WATER_E | 6561 | 0 | 0 | 0 | 100.000% |
| Moon | BELLY_WATER_C | 6561 | 0 | 0 | 0 | 100.000% |
| Moon | GW_TAP_E | 0 | 0 | 6561 | 0 | n/a |
| Moon | WAYFARER_ELECTROLYSIS | 0 | 0 | 6561 | 0 | n/a |
| Moon | CRYO_PHYSICAL | 0 | 0 | 6561 | 0 | n/a |
| Moon | FLIGHT_E | 0 | 1458 | 5103 | 0 | 0.000% |
| Moon | FLIGHT_C | 0 | 1458 | 5103 | 0 | 0.000% |
| Moon | ORBIT_FULL | 0 | 0 | 6561 | 0 | n/a |
| Moon | SURFACE_THERMAL | 0 | 0 | 6561 | 0 | n/a |
| Moon | BAY_FULL | 0 | 0 | 6561 | 0 | n/a |
| Moon | FLIGHT_TOTAL | 0 | 1458 | 5103 | 0 | 0.000% |
| Mars | A2 | 5103 | 1458 | 0 | 0 | 77.778% |
| Mars | A2_CHEM | 5103 | 1458 | 0 | 0 | 77.778% |
| Mars | KIT_VOLUME | 0 | 0 | 0 | 6561 | n/a |
| Mars | LIFT_SCREEN | 0 | 0 | 0 | 6561 | n/a |
| Mars | ROTOR_MODEL_TOP | 0 | 0 | 0 | 6561 | n/a |
| Mars | WATER_IDEAL_FLOOR | 0 | 0 | 0 | 6561 | n/a |
| Mars | BELLY_TW_E | 6561 | 0 | 0 | 0 | 100.000% |
| Mars | BELLY_TW_C | 6561 | 0 | 0 | 0 | 100.000% |
| Mars | BELLY_WATER_E | 6561 | 0 | 0 | 0 | 100.000% |
| Mars | BELLY_WATER_C | 6561 | 0 | 0 | 0 | 100.000% |
| Mars | GW_TAP_E | 0 | 0 | 6561 | 0 | n/a |
| Mars | WAYFARER_ELECTROLYSIS | 0 | 0 | 6561 | 0 | n/a |
| Mars | CRYO_PHYSICAL | 0 | 0 | 6561 | 0 | n/a |
| Mars | FLIGHT_E | 0 | 1458 | 5103 | 0 | 0.000% |
| Mars | FLIGHT_C | 0 | 1458 | 5103 | 0 | 0.000% |
| Mars | ORBIT_FULL | 0 | 0 | 6561 | 0 | n/a |
| Mars | SURFACE_THERMAL | 0 | 0 | 6561 | 0 | n/a |
| Mars | BAY_FULL | 0 | 0 | 6561 | 0 | n/a |
| Mars | FLIGHT_TOTAL | 0 | 1458 | 5103 | 0 | 0.000% |
| Mercury | A2 | 5103 | 1458 | 0 | 0 | 77.778% |
| Mercury | A2_CHEM | 5103 | 1458 | 0 | 0 | 77.778% |
| Mercury | KIT_VOLUME | 0 | 0 | 0 | 6561 | n/a |
| Mercury | LIFT_SCREEN | 0 | 0 | 0 | 6561 | n/a |
| Mercury | ROTOR_MODEL_TOP | 0 | 0 | 0 | 6561 | n/a |
| Mercury | WATER_IDEAL_FLOOR | 0 | 0 | 0 | 6561 | n/a |
| Mercury | BELLY_TW_E | 6561 | 0 | 0 | 0 | 100.000% |
| Mercury | BELLY_TW_C | 6561 | 0 | 0 | 0 | 100.000% |
| Mercury | BELLY_WATER_E | 6561 | 0 | 0 | 0 | 100.000% |
| Mercury | BELLY_WATER_C | 6561 | 0 | 0 | 0 | 100.000% |
| Mercury | GW_TAP_E | 0 | 0 | 6561 | 0 | n/a |
| Mercury | WAYFARER_ELECTROLYSIS | 0 | 0 | 6561 | 0 | n/a |
| Mercury | CRYO_PHYSICAL | 0 | 0 | 6561 | 0 | n/a |
| Mercury | FLIGHT_E | 0 | 1458 | 5103 | 0 | 0.000% |
| Mercury | FLIGHT_C | 0 | 1458 | 5103 | 0 | 0.000% |
| Mercury | ORBIT_FULL | 0 | 0 | 6561 | 0 | n/a |
| Mercury | SURFACE_THERMAL | 0 | 0 | 6561 | 0 | n/a |
| Mercury | BAY_FULL | 0 | 0 | 6561 | 0 | n/a |
| Mercury | FLIGHT_TOTAL | 0 | 1458 | 5103 | 0 | 0.000% |

## Interpretation and accounting
**BASELINE SELECTED (kT):** chemical H2/O2 belly is authoritative for Moon, Mars and Mercury polar noncanon screening; electric/thermal water is RESEARCH ALTERNATIVE only. FLIGHT_TOTAL for those worlds mirrors FLIGHT_C (baseline), not the union of architectures. Titan remains rotor + house kit.
**A2:** The original 34.2t G8 docked-core dry cap. Electric/core uses the existing small-belly-thruster dry part. Chemical also charges its **additional cryo tank 0.3–0.8t**; no Venus/Titan kit on Moon, Mars or Mercury.
**BELLY_TW_E / BELLY_TW_C:** chosen thrust-to-weight target 1.2–1.5 at each world's local g, applied to the initial sampled wet mass, not the abandoned Venus fixed-thrust array. Because thrust is being **sized** by this formula, these gates mechanically PASS by construction. They do NOT certify installed thrust, combustion, motor mass, duty, exhaust plume or structure.
**BELLY_WATER_E / BELLY_WATER_C:** finite 23.1t reaction-water stock charged once for belly sortie Δv 0.3–0.6km/s (touchdown + hover + lift to torch pitch-up) **AND** main torch ideal circular-speed lower bound at world g/radius, with cryo boil-off also debited for chemical. PASS means this lower-bound water ledger closes. Actual required orbit Δv and thrust/duty remain OPEN.
**Electric/thermal architecture (a), RESEARCH ALTERNATIVE:** water exhaust 6–12km/s, directed jet power P=F×ve/2, reactor input=P/(0.30–0.70 efficiency). The GW tap from the shuttle's torch reactor is OPEN. Wayfarer only declares a 63.36MW RAW **burn-only** torch tap, not a GW supply. Water-gate PASS does not imply a viable input power system.
**Chemical architecture (b), kT BASELINE for Moon/Mars/Mercury:** H2/O2 exhaust 4.0–4.4km/s from conventional high-performance engine analogues, whole propellant from water electrolysed **on Wayfarer before sortie**, 2×50MW net house reactors (DECLARED_2226), then shipped in a **0.3–0.8t** cryogenic tank. LOX+LH2 and water are mutually exclusive accounting forms; never double-count propellant mass. Boil-off 0.5–2%/day; an explicit **0–1day ASSUMPTION** is swept because no actual hold-time was supplied. The plant/liquefier, tanks, engine packaging and oxygen/hydrogen interfaces remain OPEN.
**Electrolysis evidence:** source-backed electrolysis input **5.000–6.200 kWh per kg of stoichiometric WATER**, tagged ONLINE (DERIVED from US DOE reported hydrogen-electricity figures and H₂/H₂O mass ratio 0.112). This is **electrolysis only**; Wayfarer oxygen/hydrogen liquefaction, delivery, insulation, plant hardware and additional energy remain OPEN, not silently included.
**Titan:** rotor + previously defined detachable reactor kit, no belly architecture. The 60km upper atmosphere model boundary is NOT a needed handover height; the rocket plume and actual Titan upper atmosphere remain OPEN.
**Full orbit and thermal gates:** remain OPEN even for selected chemical baseline, including cryogenic hardware integration, Mercury polar-site thermal environment and G8 hold clearance; GW electrical tap remains an alternative-only OPEN. No convenient numerical lower-bound PASS promotes these to mission certification.

## Planetary outputs and sensitivity
### Titan
**Mode:** ROTOR_KIT_HOUSE_REACTOR. g=1.352 m/s², mean radius=2575.000km, ideal circular-speed lower bound=1.866km/s.
Core docked dry first sample 19.917t; removable kit first sample 5.925t. No kit is carried on Moon/Mars/Mercury, and chemical cryo tank is counted in A2_CHEM.
Kit reactor, rotor and existing water accounting unchanged from earlier Stage3, apart from joint sampling. Rotor altitude model 18.000–60.000km, with 60.000km a **domain boundary only**, not a flight requirement.
First scenario ideal torch water floor 3.542t, remaining 19.558t from separate reaction-water stock. Pod cold water and custody payload are not propellant.
| Titan phase | reaction water t | phase debit t | cold cabin water t | custody payload t |
|---|---:|---:|---:|---:|
| entry/rotor (no reaction-water debit) | 23.100 | 0.000 | 0.300 | 0.010 |
| ideal circular-speed torch floor | 19.558 | 3.542 | 0.300 | 0.010 |
#### Three strongest one-at-a-time drivers per computable gate
Each variable is varied min/mid/max over 81 baseline configurations. For T/W-sizing gates that pass by construction, the physical *required thrust* variation ranks drivers, rather than fabricating certification sensitivity.
**A2**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 40.741 | 59.259 | 6.000 |
| mass.hull_thermal_structure_t | 100.000 / 88.889 / 70.370 | 29.630 | 4.419 |
| mass.pressure_pod_titanium_shell_t | 100.000 / 88.889 / 74.074 | 25.926 | 3.132 |
**KIT_VOLUME**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| kit.packed_effective_density_t_per_m3 | 40.741 / 100.000 / 100.000 | 59.259 | 34.229 |
| mass.entry_tps_t | 92.593 / 81.481 / 70.370 | 22.222 | 10.952 |
| power.kit_house_reactor_thermal_MW | 92.593 / 81.481 / 70.370 | 22.222 | 8.899 |
**LIFT_SCREEN**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| power.kit_house_reactor_thermal_MW | 100.000 / 100.000 / 100.000 | 0.000 | 129.654 |
| power.tipjet_thermal_to_useful_rotor | 100.000 / 100.000 / 100.000 | 0.000 | 7.537 |
| power.rotor_figure_of_merit | 100.000 / 100.000 / 100.000 | 0.000 | 1.745 |
**ROTOR_MODEL_TOP**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| power.rotor_hot_duty_limit_h | 0.000 / 66.667 / 100.000 | 100.000 | 24.000 |
| power.rotor_climb_rate_mps | 33.333 / 66.667 / 66.667 | 33.333 | 17.000 |
| capsule.content_mass_t | 55.556 / 55.556 / 55.556 | 0.000 | 0.000 |
**WATER_IDEAL_FLOOR**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| power.torch_high_ve_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 3.423 |
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.240 |
| mass.hull_thermal_structure_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.176 |
**Required physical OPENs:** worlds.Titan.required_ascent_dv_kmps; worlds.Titan.surface_thermal_qualification; worlds.Titan.real_handover_altitude_km; Titan upper-atmosphere model, hot N2/CH4 rotor, torch plume; G8 stowed geometry.

### Moon
**Mode:** BELLY_NO_KIT. g=1.620 m/s², mean radius=1737.400km, ideal circular-speed lower bound=1.678km/s.
Core docked dry first sample 19.917t; removable kit first sample 5.925t. No kit is carried on Moon/Mars/Mercury, and chemical cryo tank is counted in A2_CHEM.
**World-specific belly requirements, min / mean / max over 6,561 samples. H2/O2 is the kT BASELINE, electric water a RESEARCH ALTERNATIVE:**
| Quantity | (a) Electric/thermal water (RESEARCH) | (b) Wayfarer H2/O2 (BASELINE) |
|---|---:|---:|
| Initial wet mass | 43.327 / 53.801 / 59.538 t | 43.627 / 54.351 / 60.088 t |
| Target thrust-to-weight | OPEN | OPEN |
| Required thrust | 84.228 / 117.662 / 143.924 kN | 84.811 / 118.865 / 144.653 kN |
| Belly sortie Δv | 0.300 / 0.450 / 0.600 km/s | 0.300 / 0.450 / 0.600 km/s |
| Belly exhaust velocity | 6.000 / 9.000 / 12.000 km/s | 4.000 / 4.200 / 4.400 km/s |
| Directed jet power | 0.253 / 0.529 / 0.786 GW | OPEN |
| Required onboard electric power | 0.415 / 1.193 / 2.619 GW | OPEN |
| Water committed/cryogenic loaded | 1.294 / 2.832 / 5.601 t | 3.152 / 5.540 / 8.029 t |
| Belly fuel actually consumed | 1.294 / 2.832 / 5.601 t | 3.152 / 5.505 / 7.948 t |
| Cryogenic boil-off | 0.000 / 0.000 / 0.000 t | 0.000 / 0.034 / 0.154 t |
| Cryo tank dry mass | 0.000 / 0.000 / 0.000 t | 0.300 / 0.550 / 0.800 t |
| Water remaining after belly | 17.499 / 20.268 / 21.806 t | 15.071 / 17.560 / 19.948 t |
| Ideal remaining torch water requirement | 0.697 / 1.836 / 3.718 t | 0.650 / 1.758 / 3.606 t |
| Water remaining after belly + ideal torch | 14.851 / 18.433 / 20.956 t | 12.070 / 15.803 / 18.786 t |
| Wayfarer electrolysis + cryo preparation budget | OPEN | 15761.672 / 31021.054 / 49346.353 kWh |
| Production hours @ 100MW net | OPEN | 0.158 / 0.310 / 0.493 h |
Both architectures calculate **thrust required** from sampled T/W and the respective actual wet vehicle mass. A1/A2 engine actuator specific thrust and installed hardware capability are still OPEN; the chemical dry tank is included once.
The full water debit includes belly touchdown, hover and liftoff to pitch-up **once per sortie**, followed by the ideal circular-speed torch lower-bound. In chemical mode, the generated 1kg of combined H2/O2 *replaces* 1kg water; loaded propellant and reaction water are not additional to the 23.1t initial stock.
#### First sampled phase ledgers
**(b) Wayfarer-manufactured H2/O2 — BASELINE**
Required 84.811 kN at T/W 1.200, belly Δv 0.300km/s; ideal circular-speed torch floor 2.627t.
| Phase | remaining reaction-water equivalent t | charged to phase t | cryo subset on board after phase t | cold cabin water t | custody t |
|---|---:|---:|---:|---:|---:|
| Wayfarer load before sortie | 23.100 | 0.000 | 3.152 | 0.300 | 0.010 |
| Cryogenic boil-off and belly burn | 19.948 | 3.152 | 0.000 | 0.300 | 0.010 |
| Main torch ideal-circular-speed floor (NOT full ascent) | 17.321 | 2.627 | 0.000 | 0.300 | 0.010 |
On Wayfarer: water converted to cryo 3.152t (including expected 0.000t boil-off); electrolysis/handling energy 15761.672kWh requiring 0.158h at both declared house reactors' full 100MW output. Plant, processing and full charging schedule remain OPEN.
**(a) Electric/thermal water — research alternative**
Required 84.228 kN at T/W 1.200, belly Δv 0.300km/s; ideal circular-speed torch floor 2.675t.
| Phase | remaining reaction-water equivalent t | charged to phase t | cryo subset on board after phase t | cold cabin water t | custody t |
|---|---:|---:|---:|---:|---:|
| Wayfarer load before sortie | 23.100 | 0.000 | OPEN | 0.300 | 0.010 |
| Thermal/electric water belly burn | 20.987 | 2.113 | OPEN | 0.300 | 0.010 |
| Main torch ideal-circular-speed floor (NOT full ascent) | 18.312 | 2.675 | 0.000 | 0.300 | 0.010 |
Jet 0.253GW; required conversion input 0.842GW; torch reactor high-power feed **OPEN**.
#### Three strongest one-at-a-time drivers per computable gate
Each variable is varied min/mid/max over 81 baseline configurations. For T/W-sizing gates that pass by construction, the physical *required thrust* variation ranks drivers, rather than fabricating certification sensitivity.
**A2**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 40.741 | 59.259 | 6.000 |
| mass.hull_thermal_structure_t | 100.000 / 88.889 / 70.370 | 29.630 | 4.419 |
| mass.pressure_pod_titanium_shell_t | 100.000 / 88.889 / 74.074 | 25.926 | 3.132 |
**A2_CHEM**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 39.506 | 60.494 | 6.000 |
| mass.hull_thermal_structure_t | 100.000 / 88.889 / 66.667 | 33.333 | 4.419 |
| mass.pressure_pod_titanium_shell_t | 96.296 / 88.889 / 74.074 | 22.222 | 3.132 |
**BELLY_TW_E**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| world.belly.thrust_to_weight | 100.000 / 100.000 / 100.000 | 0.000 | 26.147 |
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 100.000 | 0.000 | 13.122 |
| mass.hull_thermal_structure_t | 100.000 / 100.000 / 100.000 | 0.000 | 9.663 |
**BELLY_TW_C**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| world.belly.thrust_to_weight | 100.000 / 100.000 / 100.000 | 0.000 | 26.414 |
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 100.000 | 0.000 | 13.122 |
| mass.hull_thermal_structure_t | 100.000 / 100.000 / 100.000 | 0.000 | 9.663 |
**BELLY_WATER_E**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| power.torch_high_ve_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 2.460 |
| world.belly.electric.ve_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 1.831 |
| world.belly.sortie_dv_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 1.767 |
**BELLY_WATER_C**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| world.belly.sortie_dv_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 3.384 |
| power.torch_high_ve_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 2.356 |
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.806 |
**Required physical OPENs:** worlds.Moon.required_ascent_dv_kmps; worlds.Moon.surface_thermal_qualification; belly.electric.torch_reactor_GW_tap; belly.chemical.electrolysis_plant_and_liquefaction_qualified; belly.chemical.cryo_joint_storage_qualified; worlds.Moon.belly_sustained_burn_and_ramp; G8 stowed geometry.

### Mars
**Mode:** BELLY_NO_KIT. g=3.730 m/s², mean radius=3389.500km, ideal circular-speed lower bound=3.556km/s.
Core docked dry first sample 19.917t; removable kit first sample 5.925t. No kit is carried on Moon/Mars/Mercury, and chemical cryo tank is counted in A2_CHEM.
**World-specific belly requirements, min / mean / max over 6,561 samples. H2/O2 is the kT BASELINE, electric water a RESEARCH ALTERNATIVE:**
| Quantity | (a) Electric/thermal water (RESEARCH) | (b) Wayfarer H2/O2 (BASELINE) |
|---|---:|---:|
| Initial wet mass | 43.327 / 53.801 / 59.538 t | 43.627 / 54.351 / 60.088 t |
| Target thrust-to-weight | OPEN | OPEN |
| Required thrust | 193.932 / 270.913 / 331.382 kN | 195.274 / 273.683 / 333.060 kN |
| Belly sortie Δv | 0.300 / 0.450 / 0.600 km/s | 0.300 / 0.450 / 0.600 km/s |
| Belly exhaust velocity | 6.000 / 9.000 / 12.000 km/s | 4.000 / 4.200 / 4.400 km/s |
| Directed jet power | 0.582 / 1.218 / 1.809 GW | OPEN |
| Required onboard electric power | 0.955 / 2.747 / 6.030 GW | OPEN |
| Water committed/cryogenic loaded | 1.294 / 2.832 / 5.601 t | 3.152 / 5.540 / 8.029 t |
| Belly fuel actually consumed | 1.294 / 2.832 / 5.601 t | 3.152 / 5.505 / 7.948 t |
| Cryogenic boil-off | 0.000 / 0.000 / 0.000 t | 0.000 / 0.034 / 0.154 t |
| Cryo tank dry mass | 0.000 / 0.000 / 0.000 t | 0.300 / 0.550 / 0.800 t |
| Water remaining after belly | 17.499 / 20.268 / 21.806 t | 15.071 / 17.560 / 19.948 t |
| Ideal remaining torch water requirement | 1.464 / 3.786 / 7.595 t | 1.364 / 3.625 / 7.366 t |
| Water remaining after belly + ideal torch | 11.569 / 16.482 / 20.020 t | 8.558 / 13.935 / 17.881 t |
| Wayfarer electrolysis + cryo preparation budget | OPEN | 15761.672 / 31021.054 / 49346.353 kWh |
| Production hours @ 100MW net | OPEN | 0.158 / 0.310 / 0.493 h |
Both architectures calculate **thrust required** from sampled T/W and the respective actual wet vehicle mass. A1/A2 engine actuator specific thrust and installed hardware capability are still OPEN; the chemical dry tank is included once.
The full water debit includes belly touchdown, hover and liftoff to pitch-up **once per sortie**, followed by the ideal circular-speed torch lower-bound. In chemical mode, the generated 1kg of combined H2/O2 *replaces* 1kg water; loaded propellant and reaction water are not additional to the 23.1t initial stock.
#### First sampled phase ledgers
**(b) Wayfarer-manufactured H2/O2 — BASELINE**
Required 195.274 kN at T/W 1.200, belly Δv 0.300km/s; ideal circular-speed torch floor 5.366t.
| Phase | remaining reaction-water equivalent t | charged to phase t | cryo subset on board after phase t | cold cabin water t | custody t |
|---|---:|---:|---:|---:|---:|
| Wayfarer load before sortie | 23.100 | 0.000 | 3.152 | 0.300 | 0.010 |
| Cryogenic boil-off and belly burn | 19.948 | 3.152 | 0.000 | 0.300 | 0.010 |
| Main torch ideal-circular-speed floor (NOT full ascent) | 14.582 | 5.366 | 0.000 | 0.300 | 0.010 |
On Wayfarer: water converted to cryo 3.152t (including expected 0.000t boil-off); electrolysis/handling energy 15761.672kWh requiring 0.158h at both declared house reactors' full 100MW output. Plant, processing and full charging schedule remain OPEN.
**(a) Electric/thermal water — research alternative**
Required 193.932 kN at T/W 1.200, belly Δv 0.300km/s; ideal circular-speed torch floor 5.464t.
| Phase | remaining reaction-water equivalent t | charged to phase t | cryo subset on board after phase t | cold cabin water t | custody t |
|---|---:|---:|---:|---:|---:|
| Wayfarer load before sortie | 23.100 | 0.000 | OPEN | 0.300 | 0.010 |
| Thermal/electric water belly burn | 20.987 | 2.113 | OPEN | 0.300 | 0.010 |
| Main torch ideal-circular-speed floor (NOT full ascent) | 15.523 | 5.464 | 0.000 | 0.300 | 0.010 |
Jet 0.582GW; required conversion input 1.939GW; torch reactor high-power feed **OPEN**.
#### Three strongest one-at-a-time drivers per computable gate
Each variable is varied min/mid/max over 81 baseline configurations. For T/W-sizing gates that pass by construction, the physical *required thrust* variation ranks drivers, rather than fabricating certification sensitivity.
**A2**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 40.741 | 59.259 | 6.000 |
| mass.hull_thermal_structure_t | 100.000 / 88.889 / 70.370 | 29.630 | 4.419 |
| mass.pressure_pod_titanium_shell_t | 100.000 / 88.889 / 74.074 | 25.926 | 3.132 |
**A2_CHEM**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 39.506 | 60.494 | 6.000 |
| mass.hull_thermal_structure_t | 100.000 / 88.889 / 66.667 | 33.333 | 4.419 |
| mass.pressure_pod_titanium_shell_t | 96.296 / 88.889 / 74.074 | 22.222 | 3.132 |
**BELLY_TW_E**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| world.belly.thrust_to_weight | 100.000 / 100.000 / 100.000 | 0.000 | 60.203 |
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 100.000 | 0.000 | 30.213 |
| mass.hull_thermal_structure_t | 100.000 / 100.000 / 100.000 | 0.000 | 22.250 |
**BELLY_TW_C**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| world.belly.thrust_to_weight | 100.000 / 100.000 / 100.000 | 0.000 | 60.818 |
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 100.000 | 0.000 | 30.213 |
| mass.hull_thermal_structure_t | 100.000 / 100.000 / 100.000 | 0.000 | 22.250 |
**BELLY_WATER_E**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| power.torch_high_ve_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 4.977 |
| world.belly.electric.ve_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 1.758 |
| world.belly.sortie_dv_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 1.697 |
**BELLY_WATER_C**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| power.torch_high_ve_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 4.766 |
| world.belly.sortie_dv_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 3.250 |
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 100.000 | 0.000 | 1.012 |
**Required physical OPENs:** worlds.Mars.required_ascent_dv_kmps; worlds.Mars.surface_thermal_qualification; belly.electric.torch_reactor_GW_tap; belly.chemical.electrolysis_plant_and_liquefaction_qualified; belly.chemical.cryo_joint_storage_qualified; worlds.Mars.belly_sustained_burn_and_ramp; G8 stowed geometry.

### Mercury
**Mode:** BELLY_NO_KIT. g=3.700 m/s², mean radius=2439.400km, ideal circular-speed lower bound=3.004km/s.
Core docked dry first sample 19.917t; removable kit first sample 5.925t. No kit is carried on Moon/Mars/Mercury, and chemical cryo tank is counted in A2_CHEM.
**World-specific belly requirements, min / mean / max over 6,561 samples. H2/O2 is the kT BASELINE, electric water a RESEARCH ALTERNATIVE:**
| Quantity | (a) Electric/thermal water (RESEARCH) | (b) Wayfarer H2/O2 (BASELINE) |
|---|---:|---:|
| Initial wet mass | 43.327 / 53.801 / 59.538 t | 43.627 / 54.351 / 60.088 t |
| Target thrust-to-weight | OPEN | OPEN |
| Required thrust | 192.372 / 268.734 / 328.716 kN | 193.704 / 271.481 / 330.381 kN |
| Belly sortie Δv | 0.300 / 0.450 / 0.600 km/s | 0.300 / 0.450 / 0.600 km/s |
| Belly exhaust velocity | 6.000 / 9.000 / 12.000 km/s | 4.000 / 4.200 / 4.400 km/s |
| Directed jet power | 0.577 / 1.208 / 1.794 GW | OPEN |
| Required onboard electric power | 0.948 / 2.725 / 5.981 GW | OPEN |
| Water committed/cryogenic loaded | 1.294 / 2.832 / 5.601 t | 3.152 / 5.540 / 8.029 t |
| Belly fuel actually consumed | 1.294 / 2.832 / 5.601 t | 3.152 / 5.505 / 7.948 t |
| Cryogenic boil-off | 0.000 / 0.000 / 0.000 t | 0.000 / 0.034 / 0.154 t |
| Cryo tank dry mass | 0.000 / 0.000 / 0.000 t | 0.300 / 0.550 / 0.800 t |
| Water remaining after belly | 17.499 / 20.268 / 21.806 t | 15.071 / 17.560 / 19.948 t |
| Ideal remaining torch water requirement | 1.241 / 3.225 / 6.487 t | 1.156 / 3.087 / 6.291 t |
| Water remaining after belly + ideal torch | 12.507 / 17.044 / 20.293 t | 9.562 / 14.473 / 18.145 t |
| Wayfarer electrolysis + cryo preparation budget | OPEN | 15761.672 / 31021.054 / 49346.353 kWh |
| Production hours @ 100MW net | OPEN | 0.158 / 0.310 / 0.493 h |
Both architectures calculate **thrust required** from sampled T/W and the respective actual wet vehicle mass. A1/A2 engine actuator specific thrust and installed hardware capability are still OPEN; the chemical dry tank is included once.
The full water debit includes belly touchdown, hover and liftoff to pitch-up **once per sortie**, followed by the ideal circular-speed torch lower-bound. In chemical mode, the generated 1kg of combined H2/O2 *replaces* 1kg water; loaded propellant and reaction water are not additional to the 23.1t initial stock.
#### First sampled phase ledgers
**(b) Wayfarer-manufactured H2/O2 — BASELINE**
Required 193.704 kN at T/W 1.200, belly Δv 0.300km/s; ideal circular-speed torch floor 4.583t.
| Phase | remaining reaction-water equivalent t | charged to phase t | cryo subset on board after phase t | cold cabin water t | custody t |
|---|---:|---:|---:|---:|---:|
| Wayfarer load before sortie | 23.100 | 0.000 | 3.152 | 0.300 | 0.010 |
| Cryogenic boil-off and belly burn | 19.948 | 3.152 | 0.000 | 0.300 | 0.010 |
| Main torch ideal-circular-speed floor (NOT full ascent) | 15.365 | 4.583 | 0.000 | 0.300 | 0.010 |
On Wayfarer: water converted to cryo 3.152t (including expected 0.000t boil-off); electrolysis/handling energy 15761.672kWh requiring 0.158h at both declared house reactors' full 100MW output. Plant, processing and full charging schedule remain OPEN.
**(a) Electric/thermal water — research alternative**
Required 192.372 kN at T/W 1.200, belly Δv 0.300km/s; ideal circular-speed torch floor 4.667t.
| Phase | remaining reaction-water equivalent t | charged to phase t | cryo subset on board after phase t | cold cabin water t | custody t |
|---|---:|---:|---:|---:|---:|
| Wayfarer load before sortie | 23.100 | 0.000 | OPEN | 0.300 | 0.010 |
| Thermal/electric water belly burn | 20.987 | 2.113 | OPEN | 0.300 | 0.010 |
| Main torch ideal-circular-speed floor (NOT full ascent) | 16.320 | 4.667 | 0.000 | 0.300 | 0.010 |
Jet 0.577GW; required conversion input 1.924GW; torch reactor high-power feed **OPEN**.
#### Mercury locality sensitivity (NOT a gate)
| Scenario | Site/thermal setting | Thermal extra mass | Effect on gate fractions |
|---|---|---|---|
| **DEFAULT: POLAR settlement** | Atlas polar water industrial niche; site heat load OPEN | **No dayside kit** | Default fractions above |
| **Separate dayside comparison** | Surface 650.000–705.000K representative day-exposed range | **OPEN**, no qualified package | **NOT credited / unchanged** |
Canon Atlas supports Mercury's polar water/industrial niche; it does **not** identify a unique shade, launch pad thermal boundary, or imply every polar city is permanently shadowed.
#### Three strongest one-at-a-time drivers per computable gate
Each variable is varied min/mid/max over 81 baseline configurations. For T/W-sizing gates that pass by construction, the physical *required thrust* variation ranks drivers, rather than fabricating certification sensitivity.
**A2**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 40.741 | 59.259 | 6.000 |
| mass.hull_thermal_structure_t | 100.000 / 88.889 / 70.370 | 29.630 | 4.419 |
| mass.pressure_pod_titanium_shell_t | 100.000 / 88.889 / 74.074 | 25.926 | 3.132 |
**A2_CHEM**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 39.506 | 60.494 | 6.000 |
| mass.hull_thermal_structure_t | 100.000 / 88.889 / 66.667 | 33.333 | 4.419 |
| mass.pressure_pod_titanium_shell_t | 96.296 / 88.889 / 74.074 | 22.222 | 3.132 |
**BELLY_TW_E**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| world.belly.thrust_to_weight | 100.000 / 100.000 / 100.000 | 0.000 | 59.719 |
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 100.000 | 0.000 | 29.970 |
| mass.hull_thermal_structure_t | 100.000 / 100.000 / 100.000 | 0.000 | 22.071 |
**BELLY_TW_C**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| world.belly.thrust_to_weight | 100.000 / 100.000 / 100.000 | 0.000 | 60.329 |
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 100.000 | 0.000 | 29.970 |
| mass.hull_thermal_structure_t | 100.000 / 100.000 / 100.000 | 0.000 | 22.071 |
**BELLY_WATER_E**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| power.torch_high_ve_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 4.263 |
| world.belly.electric.ve_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 1.779 |
| world.belly.sortie_dv_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 1.717 |
**BELLY_WATER_C**
| Input | PASS % at min / mid / max | Δ PASS points | Δ margin or sized requirement |
|---|---|---:|---:|
| power.torch_high_ve_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 4.082 |
| world.belly.sortie_dv_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 3.288 |
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.952 |
**Required physical OPENs:** worlds.Mercury.required_ascent_dv_kmps; worlds.Mercury.surface_thermal_qualification; belly.electric.torch_reactor_GW_tap; belly.chemical.electrolysis_plant_and_liquefaction_qualified; belly.chemical.cryo_joint_storage_qualified; worlds.Mercury.belly_sustained_burn_and_ramp; G8 stowed geometry.

## Provenance and limits
Physics identities: T/W thrust from loaded mass and local gravity, Pjet=F×ve/2, Tsiolkovsky rocket equation, mass conservation H2O→H2+½O2, ideal circular speed sqrt(g×R). Nothing about a numerical PASS proves continuous real-world thrust, orbital Δv, pressure vessel, heat rejection or plasma operation.
Sources for stage 3: merged Stage 2 repository, current Atlas Mercury polar niche, NASA 2024 propulsion H2/O2 performance, NASA/JPL planetary facts, Wayfarer 2026-11-01 house reactor declaration, and published electrolyser energy per kg H2. All claims tagged in source input JSON.
No changes to canon, Wayfarer geometry or the merged Stage2 input ledger. Research conclusions do not mutate authority.

## Full editable Stage 3 input JSON and provenance
~~~json
{
  "schema": "LOOM_SHUTTLE_STAGE3_NONCANON_2026_11_03",
  "classification": "RESEARCH/NON_CANON/NON_QUALIFICATION/NON_RUNTIME",
  "authority": "kT APPROVED Stage3, ALL bodies ALL sponsors 2026–2226",
  "baseline": "wayfarer/lab/shuttle/shuttle_inputs.json (MERGED Stage2 research baseline), physical ranges/provenance reused unchanged",
  "worlds": {
    "Titan": {
      "mode": "ROTOR_KIT_HOUSE_REACTOR",
      "surface_gravity_mps2": {
        "value": 1.352,
        "unit": "m/s2",
        "provenance": "ONLINE",
        "source": "https://ntrs.nasa.gov/citations/20220016292",
        "description": "Titan surface gravity"
      },
      "mean_radius_km": {
        "value": 2575,
        "unit": "km",
        "provenance": "ONLINE",
        "source": "https://ntrs.nasa.gov/citations/20220016292",
        "description": "Titan approximate radius"
      },
      "surface_density_kg_m3": {
        "value": 5.43,
        "unit": "kg/m3",
        "provenance": "ONLINE",
        "source": "https://ntrs.nasa.gov/citations/20220016292",
        "description": "Near-surface N2 atmosphere"
      },
      "surface_temperature_K": {
        "value": 94,
        "unit": "K",
        "provenance": "ONLINE",
        "source": "https://ntrs.nasa.gov/citations/20220016292",
        "description": "Approximate surface temperature; heating, cold duty OPEN"
      },
      "density_scale_height_km": {
        "value": 22,
        "unit": "km",
        "provenance": "PROJECTION",
        "source": "https://ntrs.nasa.gov/citations/20220016292",
        "description": "Approximate lower-atmosphere scale height, applied as exponential proxy over 0–60km for sensitivity, NOT validated Huygens upper-atmosphere profile"
      },
      "atmosphere_model_ceiling_km": {
        "value": 60,
        "unit": "km",
        "provenance": "ASSUMPTION",
        "source": "kT Stage 3 limited demonstration screen 2026-11-03",
        "description": "Numerical stopping boundary for an explicitly provisional exponential atmosphere model. NOT a mission handover target."
      },
      "real_handover_altitude_km": {
        "value": null,
        "unit": "km",
        "provenance": "OPEN",
        "source": "No mission-specific physical envelope supplied in kT Stage 3 brief or #453 research",
        "description": "Real Titan torch ignition/handover altitude and dense N2/CH4 plume effects unqualified"
      },
      "required_ascent_dv_kmps": {
        "value": null,
        "unit": "km/s",
        "provenance": "OPEN",
        "source": "No mission-specific physical envelope supplied in kT Stage 3 brief or #453 research",
        "description": "No site-specific ascent losses, atmospheric drag, hover/surface trajectory or actual target orbit supplied"
      },
      "surface_thermal_qualification": {
        "value": null,
        "unit": "status",
        "provenance": "OPEN",
        "source": "No mission-specific physical envelope supplied in kT Stage 3 brief or #453 research",
        "description": "Cold Titan habitat heater and methane/nitrogen operations unqualified"
      }
    },
    "Moon": {
      "mode": "BELLY_NO_KIT",
      "surface_gravity_mps2": {
        "value": 1.62,
        "unit": "m/s2",
        "provenance": "ONLINE",
        "source": "https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html",
        "description": "Moon surface gravity"
      },
      "mean_radius_km": {
        "value": 1737.4,
        "unit": "km",
        "provenance": "ONLINE",
        "source": "https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html",
        "description": "Mean Moon radius"
      },
      "required_ascent_dv_kmps": {
        "value": null,
        "unit": "km/s",
        "provenance": "OPEN",
        "source": "No mission-specific physical envelope supplied in kT Stage 3 brief or #453 research",
        "description": "Ideal circular speed is a LOWER bound; full Δv including gravity/steering losses and target orbit unspecified"
      },
      "belly_sustained_burn_and_ramp": {
        "value": null,
        "unit": "status",
        "provenance": "OPEN",
        "source": "No mission-specific physical envelope supplied in kT Stage 3 brief or #453 research",
        "description": "Sized thrust = 1.2–1.5× local weight, using actual sampled vehicle mass. Two electric/thermal-water and chemical H2/O2 alternatives each separately screened; delivered-engine mass, sustained torque, plume impingement and hardware qualification OPEN."
      },
      "surface_thermal_qualification": {
        "value": null,
        "unit": "status",
        "provenance": "OPEN",
        "source": "No mission-specific physical envelope supplied in kT Stage 3 brief or #453 research",
        "description": "Solar illumination, regolith plume/dust and night survival depend on site/epoch"
      },
      "baseline_belly_architecture": "CHEMICAL_H2_O2",
      "research_alternative_belly_architecture": "ELECTRIC_THERMAL_WATER"
    },
    "Mars": {
      "mode": "BELLY_NO_KIT",
      "surface_gravity_mps2": {
        "value": 3.73,
        "unit": "m/s2",
        "provenance": "ONLINE",
        "source": "https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html",
        "description": "Mean Mars surface gravity"
      },
      "mean_radius_km": {
        "value": 3389.5,
        "unit": "km",
        "provenance": "ONLINE",
        "source": "https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html",
        "description": "Mean Mars radius"
      },
      "required_ascent_dv_kmps": {
        "value": null,
        "unit": "km/s",
        "provenance": "OPEN",
        "source": "No mission-specific physical envelope supplied in kT Stage 3 brief or #453 research",
        "description": "Mars atmospheric drag, trajectory and orbital insertion losses not supplied"
      },
      "belly_sustained_burn_and_ramp": {
        "value": null,
        "unit": "status",
        "provenance": "OPEN",
        "source": "No mission-specific physical envelope supplied in kT Stage 3 brief or #453 research",
        "description": "Sized thrust = 1.2–1.5× local weight, using actual sampled vehicle mass. Two electric/thermal-water and chemical H2/O2 alternatives each separately screened; delivered-engine mass, sustained torque, plume impingement and hardware qualification OPEN."
      },
      "surface_thermal_qualification": {
        "value": null,
        "unit": "status",
        "provenance": "OPEN",
        "source": "No mission-specific physical envelope supplied in kT Stage 3 brief or #453 research",
        "description": "Mars thermal/dust/reentry TPS depends on site and use case"
      },
      "baseline_belly_architecture": "CHEMICAL_H2_O2",
      "research_alternative_belly_architecture": "ELECTRIC_THERMAL_WATER"
    },
    "Mercury": {
      "mode": "BELLY_NO_KIT",
      "surface_gravity_mps2": {
        "value": 3.7,
        "unit": "m/s2",
        "provenance": "ONLINE",
        "source": "https://ssd.jpl.nasa.gov/planets/phys_par.html",
        "description": "Mercury gravity"
      },
      "mean_radius_km": {
        "value": 2439.4,
        "unit": "km",
        "provenance": "ONLINE",
        "source": "https://ssd.jpl.nasa.gov/planets/phys_par.html",
        "description": "Mean Mercury radius"
      },
      "required_ascent_dv_kmps": {
        "value": null,
        "unit": "km/s",
        "provenance": "OPEN",
        "source": "No mission-specific physical envelope supplied in kT Stage 3 brief or #453 research",
        "description": "Target orbit, ascent control and loss budget not supplied"
      },
      "belly_sustained_burn_and_ramp": {
        "value": null,
        "unit": "status",
        "provenance": "OPEN",
        "source": "No mission-specific physical envelope supplied in kT Stage 3 brief or #453 research",
        "description": "Sized thrust = 1.2–1.5× local weight, using actual sampled vehicle mass. Two electric/thermal-water and chemical H2/O2 alternatives each separately screened; delivered-engine mass, sustained torque, plume impingement and hardware qualification OPEN."
      },
      "surface_thermal_qualification": {
        "value": null,
        "unit": "status",
        "provenance": "OPEN",
        "source": "No mission-specific physical envelope supplied in kT Stage 3 brief or #453 research",
        "description": "Terminator/site illumination and vacuum thermal protection unknown"
      },
      "default_sortie": "POLAR_SETTLEMENT",
      "default_polar_canon": {
        "value": "POLAR_SETTLEMENT",
        "unit": "sortie scenario",
        "provenance": "CANON_REFERENCE",
        "source": "canon/current/LOOM_2226_Earth_Solar_System_Canon_Atlas_v3.2.md (Mercury polar water industrial niche)",
        "description": "Canonical Mercury includes polar water niche; default landing/access sortie is a polar settlement per kT. NOT a claim every settlement is permanently shadowed."
      },
      "default_polar_thermal_load": {
        "value": null,
        "unit": "W",
        "provenance": "OPEN",
        "source": "Local landing-site shadow, surface radiation and actual polar infrastructure unprovided",
        "description": "Do not impose dayside thermal kit or ungrounded polar temperature on default."
      },
      "dayside_sensitivity": {
        "classification": "RESEARCH_ONLY / NON_GATE / NOT DEFAULT",
        "surface_temperature_K": {
          "min": 650,
          "max": 705,
          "unit": "K",
          "provenance": "PROJECTION",
          "source": "https://www.esa.int/content/view/full/487435 ; NASA Mercury upper day ~430°C",
          "description": "Illustrative 650–705K insolation sensitivity bracket derived from ESA's maximum ~430°C upper bound; source does not establish uniform lower 650K threshold. Non-gate."
        },
        "thermal_kit_mass_t": {
          "value": null,
          "unit": "t",
          "provenance": "OPEN",
          "source": "No Mercury dayside entry/habitat thermal kit accepted",
          "description": "Report as unqualified sensitivity row, no fabricated mass or gate change."
        },
        "note": "High insolation and hot surface may impose dayside thermal structure, radiator and shelter loads; this comparison never changes polar gate fractions."
      },
      "baseline_belly_architecture": "CHEMICAL_H2_O2",
      "research_alternative_belly_architecture": "ELECTRIC_THERMAL_WATER"
    }
  },
  "belly": {
    "thrust_to_weight": {
      "min": 1.2,
      "max": 1.5,
      "unit": "ratio",
      "provenance": "ASSUMPTION",
      "source": "kT APPROVED Stage3 PR #458 correction 2026-11-03, NONCANON",
      "description": "Required world-specific peak belly thrust = T/W × initial loaded landing/ascent mass × local surface gravity; mechanical sizing result, NOT installed thrust qualification."
    },
    "sortie_dv_kmps": {
      "min": 0.3,
      "max": 0.6,
      "unit": "km/s",
      "provenance": "ASSUMPTION",
      "source": "kT APPROVED Stage3 PR #458 correction 2026-11-03, NONCANON",
      "description": "Total combined belly touchdown + hover + lift to torch pitch-up, once per sortie. Do not apply same debit multiple times."
    },
    "electric": {
      "ve_kmps": {
        "min": 6,
        "max": 12,
        "unit": "km/s",
        "provenance": "ASSUMPTION",
        "source": "kT APPROVED Stage3 PR #458 correction 2026-11-03, NONCANON",
        "description": "High exhaust speed for thermal/electric water belly; separate from 2226 high-mode main torch."
      },
      "jet_efficiency": {
        "min": 0.3,
        "max": 0.7,
        "unit": "fraction",
        "provenance": "ASSUMPTION",
        "source": "kT APPROVED Stage3 PR #458 correction 2026-11-03, NONCANON",
        "description": "Electric-to-directed-water-jet efficiency: Pjet=F×ve/2, Pinput=Pjet/eta. Does not establish reactor-to-belly GW tap."
      },
      "torch_reactor_GW_tap": {
        "value": null,
        "unit": "GW",
        "provenance": "OPEN",
        "source": "Wayfarer: only 63.36 MW raw burn-only torch tap, 75% conversion; no GW feeder declared",
        "description": "GW-class on-shuttle belly energy from torch-lineage reactor remains unqualified; user explicitly forbids crediting source feasibility in numerical water gate."
      },
      "peak_GW_tap_qualified": {
        "value": null,
        "unit": "status",
        "provenance": "OPEN",
        "source": "kT APPROVED Stage3 PR #458 correction 2026-11-03, NONCANON",
        "description": "Physical high-power feeder, direct nozzle conversion and 18h duty architecture missing"
      }
    },
    "chemical": {
      "ve_kmps": {
        "min": 4,
        "max": 4.4,
        "unit": "km/s",
        "provenance": "ONLINE",
        "source": "NASA rocket propulsion H2/O2 Isp ~410–450s; https://www.nasa.gov/wp-content/uploads/2023/09/nasa-sl-2024-arw-propulsion-systems-508.pdf ; https://www.l3harris.com/en-au/all-capabilities/rs-25-engine",
        "description": "Conventional H2/O2 effective exhaust speed bracket, compatible with typical high-performance vacuum LOX/LH2; pressure/altitude dependence not modeled."
      },
      "cryo_tank_t": {
        "min": 0.3,
        "max": 0.8,
        "unit": "t",
        "provenance": "ASSUMPTION",
        "source": "kT APPROVED Stage3 PR #458 correction 2026-11-03, NONCANON",
        "description": "Additional onboard LOX/LH2 cryogenic tank + plumbing dry mass, added ONCE to nonkit shuttle core for chemical architecture and docked A2; vessel dry qualifications OPEN."
      },
      "boiloff_fraction_per_day": {
        "min": 0.005,
        "max": 0.02,
        "unit": "per day",
        "provenance": "ASSUMPTION",
        "source": "kT APPROVED Stage3 PR #458 correction 2026-11-03, NONCANON",
        "description": "Loss of combined stoichiometric H2+O2 propellant water-equivalent per elapsed day; user provided range; high, not a NASA-qualified mission loss rate."
      },
      "storage_days": {
        "min": 0,
        "max": 1,
        "unit": "days",
        "provenance": "ASSUMPTION",
        "source": "Analyst Stage3 bounded sensitivity 2026-11-03, NON-CANON",
        "description": "Explicit illustrative zero-to-one-day interval because user gave a per-day loss but no actual transport/storage time; change if itinerary known. Charged to initial water, never ignored."
      },
      "electrolysis_kWh_per_kg_water": {
        "min": 5,
        "max": 6.2,
        "unit": "kWh/kg H2O",
        "provenance": "ONLINE",
        "source": "US DOE Hydrogen Program Record 24005 representative PEM 55.2kWh/kg H2: https://www.hydrogen.energy.gov/docs/hydrogenprogramlibraries/pdfs/24005-clean-hydrogen-production-cost-pem-electrolyzer.pdf ; DOE alkaline system 48–55 kWh/kg H2: https://www.energy.gov/cmei/fuels/technical-targets-liquid-alkaline-electrolysis ; stoichiometric H2 fraction in H2O=2.016/18.015≈0.1119",
        "description": "Equivalent electrolysis-only electricity per kg stoichiometric WATER converted to H2+O2, ~45–55kWh/kg H2 ×0.112 =5.04–6.16 kWh/kg H2O; bounded to 5.0–6.2 for source-backed sensitivity. ONLINE DERIVED from published H2-unit efficiency and chemical stoichiometry; not a measured per-kg-water system metric. NOT a claim to include cryogenic liquefaction, cooling, plant construction, or handling; those remain OPEN."
      },
      "molecular_water_to_stoich_h2o2": {
        "value": 1,
        "unit": "kg combined H2/O2 per kg water",
        "provenance": "ONLINE",
        "source": "H2O → H2 + 1/2 O2, conserved mass; https://www.arei.info/docs/rub83/Introduction_to_GREEN_HYDROGEN___AREI_CD___Dr_Maged_Mahmoud_July_2022_Finalcalb115236.pdf",
        "description": "The available water mass is converted into H2+O2 mass, no duplicated reaction water and propellant inventories."
      },
      "house_reactors_net_MW": {
        "value": 100,
        "unit": "MW net electric",
        "provenance": "DECLARED_2226",
        "source": "wayfarer/docs/SHIP_POWER_BUDGET_2026_11_01.md (merged main), kT accepted 2026-11-01",
        "description": "2×50 MW net onboard Wayfarer, consumed to prepare electrolysis propellant before shuttle departure. No shuttle GW belly tap."
      },
      "electrolysis_plant_and_liquefaction_qualified": {
        "value": null,
        "unit": "status",
        "provenance": "OPEN",
        "source": "kT APPROVED Stage3 PR #458 correction 2026-11-03, NONCANON",
        "description": "Available electrical generation does not prove that a high-throughput electrolysis plant/LOX-LH2 liquefier exists; no plant mass charged to shuttle; Wayfarer capacity and storage remain OPEN."
      },
      "cryo_joint_storage_qualified": {
        "value": null,
        "unit": "status",
        "provenance": "OPEN",
        "source": "kT APPROVED Stage3 PR #458 correction 2026-11-03, NONCANON",
        "description": "Boiloff and 0.3–0.8t tank declared but actual cold-line valves, oxygen compatibility, landing pad duty and vehicle packaging OPEN"
      }
    },
    "orbit_torch_basis": "same high-ve torch and ideal circular-speed lower bound as Stage3 first draft; actual full ascent delta-v remains OPEN",
    "baseline_architecture": "chemical",
    "research_alternative_architecture": "electric",
    "selection_authority": "kT APPROVED 2026-11-03: chemical H2/O2 belly BASELINE on Moon, Mars, Mercury polar; electric/thermal water research alternative only. Does not certify full flight."
  },
  "pilot": {
    "sweep_count": {
      "value": 6561,
      "unit": "scenarios",
      "provenance": "ASSUMPTION",
      "source": "Reuse Stage 2 3^8 sample design",
      "description": "Deterministic balanced min/mid/max coverage, not probability"
    },
    "oat_count": {
      "value": 81,
      "unit": "baseline scenarios",
      "provenance": "ASSUMPTION",
      "source": "Reuse Stage2 one-at-a-time sensitivity count",
      "description": "3^4 baselines per input"
    },
    "top": {
      "value": 3,
      "unit": "drivers",
      "provenance": "ASSUMPTION",
      "source": "kT Stage 3",
      "description": "Three strongest variation/margins per computed gate"
    }
  },
  "cautions": [
    "A2 core excludes detachable Titan/Venus kit in Wayfarer dock; Titan installed mass includes kit in wet and thrust analysis.",
    "No kit on Moon/Mars/Mercury; crew cold water, reaction water and custody capsule remain distinct.",
    "Necessary ideal-circular-orbit water floor is not full orbital ascent Δv. C_FULL stays OPEN for each world.",
    "Titan atmosphere beyond near surface represented only by explicitly projected scale height; altitude at 60km is model-boundary censoring, not handover proof.",
    "Titan ambient N2 heat feed from reactor is an assumed 2226 thermal conversion; real methane/nitrogen reactivity, exchanger/cold rotor materials and Torch dense atmosphere stay OPEN.",
    "Plume design and surface survival are not certified; G8 B full fit remains OPEN.",
    "Removed abandoned Venus fixed-peak belly-array analogue; World-specific F=T/W×wetmass×gravity at sampled 1.2–1.5 T/W.",
    "Electric water belly requires GW source tap from torch reactor: OPEN; Wayfarer 63.36MW torch tap is burn-only and no GW feeder proved.",
    "H2/O2 uses shared water by electrolysis aboard Wayfarer, with 100MW net declared house-power, cryogenic tank and time-swept boiloff. Plant/liquefier and fill logistics OPEN.",
    "Electrolysis electricity is ONLINE-derived ~5.0–6.2kWh per kg stoichiometric water, based on published ~45–55kWh/kg hydrogen and 0.112 mass fraction; cryogenic liquefaction extra power and plant remain OPEN.",
    "Mercury polar settlement default supported by Atlas polar water niche; dayside surface thermal only separate uncredited sensitivity.",
    "Moon, Mars, Mercury polar: chemical H2/O2 belly is the baseline; electric/thermal water is a research alternative (GW electrical power tap OPEN); full orbital ascent remains OPEN."
  ],
  "si": {
    "N_per_kN": {
      "value": 1000,
      "unit": "N/kN",
      "provenance": "ONLINE",
      "source": "SI decimal prefixes",
      "description": "Explicit mechanical force unit conversion"
    }
  }
}
~~~
