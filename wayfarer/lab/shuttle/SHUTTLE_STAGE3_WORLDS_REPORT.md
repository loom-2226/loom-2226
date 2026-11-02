# LOOM Shuttle v1 Stage 3 — Titan, Moon, Mars, Mercury
ALL bodies. ALL sponsors. 2026–2226.

**Status: RESEARCH / NON-CANON / NON-QUALIFICATION.** This is a deliberately small next-world experiment, not certified flight closure.
Upstream: merged noncanon Stage 2 shuttle JSON, Git blob 32cca54304d8092b57b378fc4e63b0fd12ebb540. Stage 3 source inputs Git blob ceee8ef35ed0c0f987ee73abe7162650b078b93a.
Deterministic 3-level 3^8 scenario design, 6561 per world, 29 swept fields. PASS fractions are balanced-design fractions, NOT probabilities.

## World gate counts
| World | Gate | PASS | FAIL | OPEN | N/A | PASS among resolved |
|---|---|---:|---:|---:|---:|---:|
| Titan | A2 | 4374 | 2187 | 0 | 0 | 66.667% |
| Titan | KIT_VOLUME | 4860 | 1701 | 0 | 0 | 74.074% |
| Titan | LIFT_SCREEN | 6561 | 0 | 0 | 0 | 100.000% |
| Titan | ROTOR_MODEL_TOP | 3645 | 2916 | 0 | 0 | 55.556% |
| Titan | WATER_IDEAL_FLOOR | 6561 | 0 | 0 | 0 | 100.000% |
| Titan | ORBIT_FULL | 0 | 0 | 6561 | 0 | n/a |
| Titan | SURFACE_THERMAL | 0 | 0 | 6561 | 0 | n/a |
| Titan | BAY_FULL | 0 | 0 | 6561 | 0 | n/a |
| Titan | FLIGHT_TOTAL | 0 | 4860 | 1701 | 0 | 0.000% |
| Moon | A2 | 4374 | 2187 | 0 | 0 | 66.667% |
| Moon | KIT_VOLUME | 0 | 0 | 0 | 6561 | n/a |
| Moon | LIFT_SCREEN | 6561 | 0 | 0 | 0 | 100.000% |
| Moon | ROTOR_MODEL_TOP | 0 | 0 | 0 | 6561 | n/a |
| Moon | WATER_IDEAL_FLOOR | 6561 | 0 | 0 | 0 | 100.000% |
| Moon | ORBIT_FULL | 0 | 0 | 6561 | 0 | n/a |
| Moon | SURFACE_THERMAL | 0 | 0 | 6561 | 0 | n/a |
| Moon | BAY_FULL | 0 | 0 | 6561 | 0 | n/a |
| Moon | FLIGHT_TOTAL | 0 | 2187 | 4374 | 0 | 0.000% |
| Mars | A2 | 4374 | 2187 | 0 | 0 | 66.667% |
| Mars | KIT_VOLUME | 0 | 0 | 0 | 6561 | n/a |
| Mars | LIFT_SCREEN | 6561 | 0 | 0 | 0 | 100.000% |
| Mars | ROTOR_MODEL_TOP | 0 | 0 | 0 | 6561 | n/a |
| Mars | WATER_IDEAL_FLOOR | 6561 | 0 | 0 | 0 | 100.000% |
| Mars | ORBIT_FULL | 0 | 0 | 6561 | 0 | n/a |
| Mars | SURFACE_THERMAL | 0 | 0 | 6561 | 0 | n/a |
| Mars | BAY_FULL | 0 | 0 | 6561 | 0 | n/a |
| Mars | FLIGHT_TOTAL | 0 | 2187 | 4374 | 0 | 0.000% |
| Mercury | A2 | 4374 | 2187 | 0 | 0 | 66.667% |
| Mercury | KIT_VOLUME | 0 | 0 | 0 | 6561 | n/a |
| Mercury | LIFT_SCREEN | 6561 | 0 | 0 | 0 | 100.000% |
| Mercury | ROTOR_MODEL_TOP | 0 | 0 | 0 | 6561 | n/a |
| Mercury | WATER_IDEAL_FLOOR | 6561 | 0 | 0 | 0 | 100.000% |
| Mercury | ORBIT_FULL | 0 | 0 | 6561 | 0 | n/a |
| Mercury | SURFACE_THERMAL | 0 | 0 | 6561 | 0 | n/a |
| Mercury | BAY_FULL | 0 | 0 | 6561 | 0 | n/a |
| Mercury | FLIGHT_TOTAL | 0 | 2187 | 4374 | 0 | 0.000% |

## Physical meaning of the gates
**A2:** Same 34.2t docked core dry without detachable kit. Installed Titan mass includes the entire kit; Moon/Mars/Mercury do not carry it.
**KIT_VOLUME:** Titan-only 56.1m3 aggregate hold and 50t total payload necessary check; individual hold openings and hot blade joints remain OPEN.
**LIFT_SCREEN:** Titan conditional near-surface rotor thermal/induced-velocity screen; light worlds peak T/W of #453 Venus belly 760kN array ANALOGUE only, NOT approved small-thruster hardware or sustained lift.
**ROTOR_MODEL_TOP:** Titan-only threshold of reaching the stated 60km ANALYTICAL ATMOSPHERE DOMAIN EDGE. An artificial model-boundary screen, NOT kT required handover altitude. Model altitude censored at 60km.
**WATER_IDEAL_FLOOR:** high-ve torch and finite 23.1t reaction water compared to ideal circular velocity sqrt(g*radius) using rocket equation, with 0–0.84t unqualified belly touchdown debit on light worlds; actual torch burn, gravity losses, guidance, atmospheric drag and continuous thrust NOT credited.
**ORBIT_FULL:** OPEN for ALL because required site/trajectory Δv is not known. A PASS lower-bound is NOT orbital approval.
**SURFACE_THERMAL:** OPEN for all, including Titan heater/cold operations, Mercury day-night, lunar cycles and Mars entry/dust.
**BAY_FULL:** OPEN from G8 stowed geometry. **FLIGHT_TOTAL:** FAIL on demonstrated necessary-gate failure; otherwise OPEN; no certified PASS.

## Per-world vehicle and water comparisons
### Titan
Mode ROTOR_KIT_HOUSE_REACTOR, gravity 1.352m/s², mean radius 2575.000km, necessary ideal orbital speed 1.866km/s.
First sampled vehicle core 21.150t, installed dry 28.075t, Titan/Venus kit 6.925t (carried on Wayfarer payload only when deployed). First sampled wet lift mass 51.485t.
Projected Titan atmosphere: rho0 5.430 kg/m³ × exp(-h/22.000km), only to 60.000km. Observed rotor computed range 18.000–60.000km; 60km results are CENSORED at model edge, NOT true handover.
Reaction water, cabin cold-water and custody inventories are disjoint. Sampled ledger:
| Phase | Reaction water remaining t | phase debit t | cold crew water t | custody content t |
|---|---:|---:|---:|---:|
| entry / atmospheric phase | 23.100 | 0.000 | 0.300 | 0.010 |
| rotor landing (no tank water) | 23.100 | 0.000 | 0.300 | 0.010 |
| ideal circular-speed torch floor only | 19.397 | 3.703 | 0.300 | 0.010 |
Initial reaction water 23.100t; ideal circular floor torch water 3.703t, remaining 19.397t; REQUIRED full orbit Δv OPEN; separate belly liftoff burn OPEN.
**Top three one-at-a-time sensitivity drivers per computed gate (including margin ranking if no PASS flips):**
**A2**
| Input | PASS % min / mid / max | Δ PASS points | Δ physical margin |
|---|---|---:|---:|
| mass.torch_low_high_engine_t | 100.000 / 55.556 / 33.333 | 66.667 | 6.000 |
| mass.hull_thermal_structure_t | 92.593 / 77.778 / 44.444 | 48.148 | 5.000 |
| mass.pressure_pod_titanium_shell_t | 92.593 / 74.074 / 51.852 | 40.741 | 4.400 |
**KIT_VOLUME**
| Input | PASS % min / mid / max | Δ PASS points | Δ physical margin |
|---|---|---:|---:|
| kit.packed_effective_density_t_per_m3 | 22.222 / 100.000 / 100.000 | 77.778 | 39.229 |
| mass.entry_tps_t | 85.185 / 70.370 / 70.370 | 14.815 | 10.952 |
| power.kit_house_reactor_thermal_MW | 77.778 / 77.778 / 70.370 | 7.407 | 8.899 |
**LIFT_SCREEN**
| Input | PASS % min / mid / max | Δ PASS points | Δ physical margin |
|---|---|---:|---:|
| power.kit_house_reactor_thermal_MW | 100.000 / 100.000 / 100.000 | 0.000 | 129.645 |
| power.tipjet_thermal_to_useful_rotor | 100.000 / 100.000 / 100.000 | 0.000 | 8.127 |
| power.rotor_figure_of_merit | 100.000 / 100.000 / 100.000 | 0.000 | 1.885 |
**ROTOR_MODEL_TOP**
| Input | PASS % min / mid / max | Δ PASS points | Δ physical margin |
|---|---|---:|---:|
| power.rotor_hot_duty_limit_h | 0.000 / 66.667 / 100.000 | 100.000 | 24.000 |
| power.rotor_climb_rate_mps | 33.333 / 66.667 / 66.667 | 33.333 | 17.000 |
| capsule.content_mass_t | 55.556 / 55.556 / 55.556 | 0.000 | 0.000 |
**WATER_IDEAL_FLOOR**
| Input | PASS % min / mid / max | Δ PASS points | Δ physical margin |
|---|---|---:|---:|
| power.torch_high_ve_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 3.600 |
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.240 |
| mass.hull_thermal_structure_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.200 |
All OPEN blockers: worlds.Titan.required_ascent_dv_kmps; worlds.Titan.surface_thermal_qualification; worlds.Titan.real_handover_altitude_km; Titan upper-atmosphere model, hot N2/CH4 rotor, torch plume; G8 stowed geometry.

### Moon
Mode BELLY_NO_KIT, gravity 1.620m/s², mean radius 1737.400km, necessary ideal orbital speed 1.678km/s.
First sampled vehicle core 21.150t, installed dry 21.150t, Titan/Venus kit 6.925t (carried on Wayfarer payload only when deployed). First sampled wet lift mass 44.560t.
Unqualified 760kN #453 belly array used as hypothetical upper-bound peak; sustained duty and real small belly-nozzle installation OPEN.
Reaction water, cabin cold-water and custody inventories are disjoint. Sampled ledger:
| Phase | Reaction water remaining t | phase debit t | cold crew water t | custody content t |
|---|---:|---:|---:|---:|
| entry / atmospheric phase | 23.100 | 0.000 | 0.300 | 0.010 |
| belly touchdown (illustrative) | 23.100 | 0.000 | 0.300 | 0.010 |
| ideal circular-speed torch floor only | 20.208 | 2.892 | 0.300 | 0.010 |
Initial reaction water 23.100t; ideal circular floor torch water 2.892t, remaining 20.208t; REQUIRED full orbit Δv OPEN; separate belly liftoff burn OPEN.
**Top three one-at-a-time sensitivity drivers per computed gate (including margin ranking if no PASS flips):**
**A2**
| Input | PASS % min / mid / max | Δ PASS points | Δ physical margin |
|---|---|---:|---:|
| mass.torch_low_high_engine_t | 100.000 / 55.556 / 33.333 | 66.667 | 6.000 |
| mass.hull_thermal_structure_t | 92.593 / 77.778 / 44.444 | 48.148 | 5.000 |
| mass.pressure_pod_titanium_shell_t | 92.593 / 74.074 / 51.852 | 40.741 | 4.400 |
**LIFT_SCREEN**
| Input | PASS % min / mid / max | Δ PASS points | Δ physical margin |
|---|---|---:|---:|
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.925 |
| mass.hull_thermal_structure_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.768 |
| mass.pressure_pod_titanium_shell_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.676 |
**WATER_IDEAL_FLOOR**
| Input | PASS % min / mid / max | Δ PASS points | Δ physical margin |
|---|---|---:|---:|
| power.torch_high_ve_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 2.664 |
| world.belly.touchdown_water_debit_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.810 |
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.216 |
All OPEN blockers: worlds.Moon.required_ascent_dv_kmps; worlds.Moon.surface_thermal_qualification; worlds.Moon.belly_sustained_burn_and_ramp; belly.liftoff_water_debit_t; G8 stowed geometry.

### Mars
Mode BELLY_NO_KIT, gravity 3.730m/s², mean radius 3389.500km, necessary ideal orbital speed 3.556km/s.
First sampled vehicle core 21.150t, installed dry 21.150t, Titan/Venus kit 6.925t (carried on Wayfarer payload only when deployed). First sampled wet lift mass 44.560t.
Unqualified 760kN #453 belly array used as hypothetical upper-bound peak; sustained duty and real small belly-nozzle installation OPEN.
Reaction water, cabin cold-water and custody inventories are disjoint. Sampled ledger:
| Phase | Reaction water remaining t | phase debit t | cold crew water t | custody content t |
|---|---:|---:|---:|---:|
| entry / atmospheric phase | 23.100 | 0.000 | 0.300 | 0.010 |
| belly touchdown (illustrative) | 23.100 | 0.000 | 0.300 | 0.010 |
| ideal circular-speed torch floor only | 17.192 | 5.908 | 0.300 | 0.010 |
Initial reaction water 23.100t; ideal circular floor torch water 5.908t, remaining 17.192t; REQUIRED full orbit Δv OPEN; separate belly liftoff burn OPEN.
**Top three one-at-a-time sensitivity drivers per computed gate (including margin ranking if no PASS flips):**
**A2**
| Input | PASS % min / mid / max | Δ PASS points | Δ physical margin |
|---|---|---:|---:|
| mass.torch_low_high_engine_t | 100.000 / 55.556 / 33.333 | 66.667 | 6.000 |
| mass.hull_thermal_structure_t | 92.593 / 77.778 / 44.444 | 48.148 | 5.000 |
| mass.pressure_pod_titanium_shell_t | 92.593 / 74.074 / 51.852 | 40.741 | 4.400 |
**LIFT_SCREEN**
| Input | PASS % min / mid / max | Δ PASS points | Δ physical margin |
|---|---|---:|---:|
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.402 |
| mass.hull_thermal_structure_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.334 |
| mass.pressure_pod_titanium_shell_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.294 |
**WATER_IDEAL_FLOOR**
| Input | PASS % min / mid / max | Δ PASS points | Δ physical margin |
|---|---|---:|---:|
| power.torch_high_ve_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 5.388 |
| world.belly.touchdown_water_debit_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.778 |
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.446 |
All OPEN blockers: worlds.Mars.required_ascent_dv_kmps; worlds.Mars.surface_thermal_qualification; worlds.Mars.belly_sustained_burn_and_ramp; belly.liftoff_water_debit_t; G8 stowed geometry.

### Mercury
Mode BELLY_NO_KIT, gravity 3.700m/s², mean radius 2439.400km, necessary ideal orbital speed 3.004km/s.
First sampled vehicle core 21.150t, installed dry 21.150t, Titan/Venus kit 6.925t (carried on Wayfarer payload only when deployed). First sampled wet lift mass 44.560t.
Unqualified 760kN #453 belly array used as hypothetical upper-bound peak; sustained duty and real small belly-nozzle installation OPEN.
Reaction water, cabin cold-water and custody inventories are disjoint. Sampled ledger:
| Phase | Reaction water remaining t | phase debit t | cold crew water t | custody content t |
|---|---:|---:|---:|---:|
| entry / atmospheric phase | 23.100 | 0.000 | 0.300 | 0.010 |
| belly touchdown (illustrative) | 23.100 | 0.000 | 0.300 | 0.010 |
| ideal circular-speed torch floor only | 18.054 | 5.046 | 0.300 | 0.010 |
Initial reaction water 23.100t; ideal circular floor torch water 5.046t, remaining 18.054t; REQUIRED full orbit Δv OPEN; separate belly liftoff burn OPEN.
**Top three one-at-a-time sensitivity drivers per computed gate (including margin ranking if no PASS flips):**
**A2**
| Input | PASS % min / mid / max | Δ PASS points | Δ physical margin |
|---|---|---:|---:|
| mass.torch_low_high_engine_t | 100.000 / 55.556 / 33.333 | 66.667 | 6.000 |
| mass.hull_thermal_structure_t | 92.593 / 77.778 / 44.444 | 48.148 | 5.000 |
| mass.pressure_pod_titanium_shell_t | 92.593 / 74.074 / 51.852 | 40.741 | 4.400 |
**LIFT_SCREEN**
| Input | PASS % min / mid / max | Δ PASS points | Δ physical margin |
|---|---|---:|---:|
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.405 |
| mass.hull_thermal_structure_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.336 |
| mass.pressure_pod_titanium_shell_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.296 |
**WATER_IDEAL_FLOOR**
| Input | PASS % min / mid / max | Δ PASS points | Δ physical margin |
|---|---|---:|---:|
| power.torch_high_ve_kmps | 100.000 / 100.000 / 100.000 | 0.000 | 4.615 |
| world.belly.touchdown_water_debit_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.787 |
| mass.torch_low_high_engine_t | 100.000 / 100.000 / 100.000 | 0.000 | 0.380 |
All OPEN blockers: worlds.Mercury.required_ascent_dv_kmps; worlds.Mercury.surface_thermal_qualification; worlds.Mercury.belly_sustained_burn_and_ramp; belly.liftoff_water_debit_t; G8 stowed geometry.

## Research notes and explicit non-transfer
Source facts: NASA Planetary Fact Sheets, JPL planetary physical parameters, NASA Titan thermal/environment and the merged #453 shuttle research. Each data field retains a URL and ONLINE/PROJECTION/ASSUMPTION/OPEN status in the attached JSON.
Do not apply Venus atmospheric temperature, Venus entry TPS performance, Venus ascent Δv, reactor-to-rotor coupling qualification or any Torch dense atmosphere ignition assumption to Titan or the light worlds. No new propellant is created or shared between thermal water and reaction water.
The 2226 kT lineage declarations, unresolved M1/M2/M3, physical validity and all canon remain untouched.

## Full Stage 3 input JSON (source and provenance)
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
        "description": "Peak touchdown belly array not qualified for continuous ascent or lunar pad blast"
      },
      "surface_thermal_qualification": {
        "value": null,
        "unit": "status",
        "provenance": "OPEN",
        "source": "No mission-specific physical envelope supplied in kT Stage 3 brief or #453 research",
        "description": "Solar illumination, regolith plume/dust and night survival depend on site/epoch"
      }
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
        "description": "Peak belly thrust has no continuous Mars ascent qualification"
      },
      "surface_thermal_qualification": {
        "value": null,
        "unit": "status",
        "provenance": "OPEN",
        "source": "No mission-specific physical envelope supplied in kT Stage 3 brief or #453 research",
        "description": "Mars thermal/dust/reentry TPS depends on site and use case"
      }
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
        "description": "Hot/cold surface, thruster sustained burn and plume/ground hazard not qualified"
      },
      "surface_thermal_qualification": {
        "value": null,
        "unit": "status",
        "provenance": "OPEN",
        "source": "No mission-specific physical envelope supplied in kT Stage 3 brief or #453 research",
        "description": "Terminator/site illumination and vacuum thermal protection unknown"
      }
    }
  },
  "belly": {
    "peak_thrust_kN": {
      "value": 760,
      "unit": "kN",
      "provenance": "ASSUMPTION",
      "source": "https://github.com/loom-2226/loom-2226/blob/main/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "#453 UNQUALIFIED Venus v1 belly-array peak **analogue only**. Not evidence of identical 'small belly thrusters' on Moon/Mars/Mercury. Only necessary peak T/W screen; true installed small-thruster rating remains OPEN."
    },
    "exhaust_velocity_kmps": {
      "value": 9,
      "unit": "km/s",
      "provenance": "ASSUMPTION",
      "source": "https://github.com/loom-2226/loom-2226/blob/main/research/engineering/SHUTTLE_RESEARCH_INPUTS.json",
      "description": "#453 Venus v1 belly thruster exhaust-speed hypothesis. Not transferred as qualified hardware."
    },
    "touchdown_water_debit_t": {
      "min": 0,
      "max": 0.84,
      "unit": "t",
      "provenance": "ASSUMPTION",
      "source": "kT 2026-11-03 Stage3 screen inspired by #453 already-accounted 0.84t Venus touchdown, NOT actual per-world landing burn",
      "description": "Illustrative single touchdown debit sensitivity 0–0.84t. Separate liftoff small-thruster water demand and duration remain OPEN."
    },
    "liftoff_water_debit_t": {
      "value": null,
      "unit": "t",
      "provenance": "OPEN",
      "source": "No mission-specific physical envelope supplied in kT Stage 3 brief or #453 research",
      "description": "No actual belly liftoff impulse/schedule specified; ideal torch lower bound omits it and cannot certify an ascent."
    }
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
    "Peak belly thrust uses old 760kN Venus v1 unqualified analogue only; cannot count as qualified small-thruster sustained ascent.",
    "Titan atmosphere beyond near surface represented only by explicitly projected scale height; altitude at 60km is model-boundary censoring, not handover proof.",
    "Titan ambient N2 heat feed from reactor is an assumed 2226 thermal conversion; real methane/nitrogen reactivity, exchanger/cold rotor materials and Torch dense atmosphere stay OPEN.",
    "Plume design and surface survival are not certified; G8 B full fit remains OPEN."
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
