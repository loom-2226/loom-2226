# Wayfarer two-reactor ship power ledger | 2026-11-01

**ENGINEERING CANDIDATE, NON-CANON, NO HARDWARE CERTIFICATION.** kT decisions on PR #440. No Navigator, Metric arrival or main merge. Previous 7f620c53 G6/G12 certification does not apply to a new geometry source hash.

New physical source hash: `9544a893d711fb9f9c91b145edeb5137728429315e0c852e1e8beab60da46661`.

**House source:** **2×50MW** D–He3 direct-conversion reactors, **5MW minimum per live unit (10%)**, declared 2226 40kW/kg net, 75% conversion. **2.50t** for both inside existing 55t electrical allocation. One unit can independently carry coast/Metric/torch magnet load; 120s RCS uses one unit + flywheel. Surplus from a live reactor charges the store, but **once full it must shut off/cycle**. Never claim 0.389MW continuous plant idle.

**Storage:** 7.00MWh flywheel (deliverable 6.64MWh), 0.70t in existing electrical allocation, declared 2226 10kWh/kg and 800kW/kg, 90% roundtrip. Emergency fast flip 5.771MWh, **7.75 minutes** to refill that used energy from one 50MW reactor. **7.74 theoretical electric recharge cycles/hour**, NOT permission for that manoeuvre rate or unlimited RCS remass.

**Quiet and cold:** BOTH house reactors OFF. Flywheel supplies 0.065MW essentials, 102.2 h energy-only endurance, but existing 50t×15K thermal buffer fills after **11.70h** at ~74.6kW retained. No 200×–4000× speculative reactor throttling.

**Metric authority distinction:** E1 canon supplies cryogenic load and PMAD efficiency, not standalone Metric field-power watts. The extra delivered control/field power is **declared NON-CANON** NORMAL 1MW / FAST 2MW / EXPEDITE 3MW / HARD 5MW. Apply E1 0.98×0.96 PMAD efficiency to cryo + field delivery, and count distribution losses as heat. Environmental-correction load remains explicitly OPEN, not hidden in the 5MW.

| Operating state | House MW | Flywheel MW out/in | Battery MW | Loads (MW, components) | Rejected MW | Deficit or closure | House fuel g/h |
|---|---:|---:|---:|---|---:|---|---:|
| docked_one_online_min | 5.000 | 0.000 / 4.601 | 0.0000 | avionics_ECLSS_lighting 0.045, heat_pump 0.324, plant_and_cryo_standby 0.020, docking_control 0.010 | 2.293 | NAMED: FULL_STORE_REQUIRES_REACTOR_CYCLE_OFF | 0.0680 |
| docked_crown_open_worst_sun | 5.000 | 0.000 / 3.904 | 0.0000 | avionics_ECLSS_lighting 0.045, solar_aperture_heat_pump 1.021, standby 0.020, docking_control 0.010 | 3.055 | NAMED: FULL_STORE_REQUIRES_REACTOR_CYCLE_OFF; AOI_OPTICAL_ATTENUATION_NOT_CREDITED | 0.0680 |
| coast_one_online_min | 5.000 | 0.000 / 4.611 | 0.0000 | ordinary_ship_services 0.389 | 2.294 | NAMED: FULL_STORE_REQUIRES_REACTOR_CYCLE_OFF | 0.0680 |
| coast_recharging_fast_flip | 50.000 | 0.000 / 49.611 | 0.0000 | ordinary_ship_services 0.389 | 19.603 | NAMED: CHARGER_BULK_POWER_HARDWARE_UNQUALIFIED | 0.6799 |
| routine_120s_flip | 50.000 | 8.052 / 0.000 | 0.0000 | ordinary_ship_services 0.389, RCS_120s_throttled_proxy 57.663 | 23.259 | NAMED: RCS_THROTTLING_1_OVER_T_SQUARED_NOT_TRACED | 0.6799 |
| fast_40s_flip | 0.000 | 519.358 / 0.000 | 0.0000 | ordinary_ship_services 0.389, RCS_40s_emergency 518.969 | 80.381 | NAMED: FAST_FLIP_BUS_AND_THERMAL_TRANSIENT_UNQUALIFIED | 0.0000 |
| pulsed_torch_burn | 47.909 | 0.000 / 0.000 | 0.0000 | ordinary_ship_services 0.389, magnet_cryocooling_electric 47.520 | 64.360 + 1400 hot-fin | NAMED: PULSED_MAIN_TORCH_NOT_A_HOUSE_GENERATOR | 0.6515 |
| Metric_NORMAL | 6.863 | 0.000 / 0.000 | 0.0000 | ordinary_ship_services 0.389, canon_cryo_scaled_1300K_delivered 5.091, declared_field_and_control_delivered 1.000, E1_PMAD_distribution_losses 0.383 | 9.172 | NAMED: FIELD_CONTROL_NORMAL_NONCANON_DECLARATION; ENVIRONMENTAL_CORRECTION_POWER_STILL_OPEN | 0.0933 |
| Metric_FAST | 12.873 | 0.000 / 0.000 | 0.0000 | ordinary_ship_services 0.389, canon_cryo_scaled_1300K_delivered 9.745, declared_field_and_control_delivered 2.000, E1_PMAD_distribution_losses 0.739 | 17.204 | NAMED: FIELD_CONTROL_FAST_NONCANON_DECLARATION; ENVIRONMENTAL_CORRECTION_POWER_STILL_OPEN | 0.1751 |
| Metric_EXPEDITE | 20.894 | 0.000 / 0.000 | 0.0000 | ordinary_ship_services 0.389, canon_cryo_scaled_1300K_delivered 16.291, declared_field_and_control_delivered 3.000, E1_PMAD_distribution_losses 1.214 | 27.923 | NAMED: FIELD_CONTROL_EXPEDITE_NONCANON_DECLARATION; ENVIRONMENTAL_CORRECTION_POWER_STILL_OPEN | 0.2841 |
| Metric_HARD | 42.655 | 0.000 / 0.000 | 0.0000 | ordinary_ship_services 0.389, canon_cryo_scaled_1300K_delivered 34.764, declared_field_and_control_delivered 5.000, E1_PMAD_distribution_losses 2.502 | 57.010 | NAMED: FIELD_CONTROL_HARD_NONCANON_DECLARATION; ENVIRONMENTAL_CORRECTION_POWER_STILL_OPEN | 0.5800 |
| quiet_reactors_off | 0.000 | 0.065 / 0.000 | 0.0000 | essential_habitat 0.065 | 0.007 passive, 0.075 retained | NAMED: COLD_BUFFER_EXHAUSTED_BEFORE_FLYWHEEL; QUIET_SKIN_EMISSIVITY_DECLARED | 0.0000 |
| cold_running_reactors_off | 0.000 | 0.065 / 0.000 | 0.0000 | essential_habitat 0.065 | 0.007 passive, 0.075 retained | NAMED: COLD_BUFFER_EXHAUSTED_BEFORE_FLYWHEEL; FLYWHEEL_THERMAL_COUPLING_UNQUALIFIED | 0.0000 |
| one_unit_failed_Metric_HARD | 42.655 | 0.000 / 0.000 | 0.0000 | ordinary_ship_services 0.389, canon_cryo_scaled_1300K_delivered 34.764, declared_field_control 5.000, PMAD_loss 2.502 | 57.010 | NAMED: FAILED_REACTOR_ISOLATION_UNQUALIFIED; ENVIRONMENTAL_CORRECTION_POWER_STILL_OPEN | 0.5800 |
| one_unit_failed_torch_magnets | 47.909 | 0.000 / 0.000 | 0.0000 | ordinary_ship_services 0.389, magnet_cryocooling_electric 47.520 | 64.360 + 1400 hot-fin | NAMED: FAILED_REACTOR_ISOLATION_UNQUALIFIED | 0.6515 |
| both_house_reactors_failed_flywheel | 0.000 | 0.389 / 0.000 | 0.0000 | ordinary_ship_services 0.389 | 0.411 | NAMED: FLYWHEEL_EXHAUSTS_AFTER_17.08_H; FAILED_PLANT_ACTIVE_RADIATORS_UNQUALIFIED | 0.0000 |
| torch_emergency_house_unqualified | 0.000 | 0.000 / 0.000 | 0.0000 | ordinary_ship_services 0.389 | 0.000 | NAMED: TORCH_EMERGENCY_HOUSE_OUTPUT_NOT_SIZED; CONTINUOUS_SUPPLY_NOT_AUTHORISED; UNSERVED_ELECTRIC_LOAD | 0.0000 |
| shelter_battery_only | 0.000 | 0.000 / 0.000 | 0.0006 | essential_shelter 0.001 | 0.000 | NAMED: 24_H_BATTERY_EXHAUSTION; NORMAL_SHIP_SERVICES_SHED; 72_H_SHELTER_STORE_NOT_72_H_ELECTRIC_SOURCE | 0.0000 |

**Failure sequence:** one reactor fails → surviving 50MW unit carries known steady loads, HARD Metric and torch magnet electrical, with the flywheel required for routine flips → both house units lost: flywheel supports ordinary ~0.389MW services for **17.08h** energy-only → attempt pulsed main torch **emergency house mode** (UNKNOWN electric output, NOT a certified source) → shed to 0.6kW ×24h shelter battery. Failed-source fallback does not provide an invented continuous torch generator. Full physical power switching, battery isolation, flywheel containment, coolant loops and thermal transfer remain OPEN.

**House fuel inventory:** 5t D–He3 wet consumable, distinct from 250t water remass and 50t protected water; consumption for each reactor-on state is shown in g/h. Main pulsed torch pellet energy is separate. Tank dry 0.5t is paid from engineering reserve. **Dry 867.681t, departure S1 1172.681t, reserve 11.284t (hard floor 5t; headroom 6.284t). Reactor+flywheel 3.20t reallocated WITHIN the 55t electrical line, with no additional dry reserve debit.**

**Engineering gaps:** 2226 reactor 40kW/kg and flywheel 10kWh/kg/800kW/kg unverified; 10% reliable minimum and independent fault isolation untested; RCS 120s throttling is a declared 1/t² assumption, not an FQ trace; electrical bus peaks and radiator integration unqualified; reported thermal rejection is a heat-budget screen; unmodelled environmental Metric correction power remains an explicit named deficit.

**Qualification:** targeted G1/G4 required; G3 inspected for mass movement. New geometry SHA does not automatically inherit G6, G12 or whole-ship certified=true. FQ1–FQ4 only required if physical mass/CG/inertia actually changes; if unchanged, prove parity and retain previous source-stamped FQ (without copying old PASS to the new hash).
