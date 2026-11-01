# Wayfarer house power, storage and independent slow recovery | 2026-11-01

**ENGINEERING CANDIDATE, NON-CANON. NO HARDWARE QUALIFICATION. PR #440 DRAFT, NO MERGE.**

Geometry SHA256: `f7dc6b8c69cf56f48a55eeaa1a5daa7779fce3e06474157c960ef2f08cac95f7`; exact current 40s RCS trace: `4e53d93684edab5a07320b3116e4f3873c26589dec513de6263b74932cdc6014`. Historic FQ/acceptance does not transfer between hashes.

**Reactors:** 2×50MW net D–He3, each 5MW minimum online, 2.50t dry declared at 40kW/kg and 75% net conversion. Must cycle off or store/spill surplus; never throttle to sub-MW.

**Battery:** 3.0MWh nominal / 2.846MWh discharge, 1.50t at declared 2.0kWh/kg; quiet 65kW energy-only 43.8h. Both reactors failed: first 1h normal, then 37.80h 65kW essential energy-only.

**Pulse flywheel:** counter-rotating pairs with burst containment, 1.5MWh nominal / 1.423MWh delivered, 1.5t at 1.0kWh/kg and 150.0kW/kg. Declared 225.0MW maximum. The full 40s current-geometry trace requires 1.302MWh and 202.6MW peak after one steady 50MW reactor. Actual heater/power-switching implementation is OPEN.

**C-lite:** 0.25t provisioned (dry 0.10t + **wet** 0.15t), ~75kg for a 600s recovery, 2 nominal turns. No current dynamics/propulsion qualification.

**Mass:** dry 867.531453t, loaded S1 1172.681453t. Loaded electrical line 55t = 54.85t dry + 0.15t C-lite wet propellant. Engineering reserve **11.284117t unchanged**; 6.284t above hard floor. C-lite fuel is a consumable, NOT dry ballast.

**Cold-running thermal bound:** 11.70h for the accepted 50t×15K protected-water buffer. Battery energy-only endurance is not a thermal qualification.

**Metric:** E1 cryo and PMAD numbers preserved; separately declared field/control NORMAL 1 / FAST 2 / EXPEDITE 3 / HARD 5MW; environmental correction remains OPEN. 2GJ reversible field bank is not a house source.

| Operating state | House MW | Flywheel out / charge MW | Battery MW | Loads MW | Heat rejected MW | State deficits |
|---|---:|---:|---:|---|---:|---|
| docked_one_online_min | 5.000 | 0.000 / 4.601 | 0.000 | ordinary_ship_services 0.389, docking_control 0.010 | 2.293 | FULL_PULSE_STORE_REQUIRES_REACTOR_OFF_OR_BATTERY_CHARGE |
| docked_crown_open_worst_sun | 5.000 | 0.000 / 3.904 | 0.000 | avionics_ECLSS 0.045, standby 0.020, heat_pump 1.021, docking 0.010 | 3.055 | AOI_OPTICAL_ATTENUATION_UNCREDITED; FULL_PULSE_STORE_REACTOR_OFF_OR_BATTERY_CHARGE |
| coast_one_online_min | 5.000 | 0.000 / 4.611 | 0.000 | ordinary_ship_services 0.389 | 2.294 | FULL_PULSE_STORE_REACTOR_OFF_OR_BATTERY_CHARGE |
| coast_recharging_fast_flip | 50.000 | 0.000 / 49.611 | 0.000 | ordinary_ship_services 0.389 | 19.603 | CHARGER_BULK_POWER_UNQUALIFIED |
| routine_120s_flip | 50.000 | 8.052 / 0.000 | 0.000 | ordinary_ship_services 0.389, RCS_120s_UNTRACED_proxy 57.663 | 23.259 | RCS_ROUTINE_THROTTLE_PROXY_UNTRACED |
| fast_40s_flip | 50.000 | 202.623 / 0.000 | 0.000 | ordinary_ship_services 0.389, RCS_40s_TRACE_PEAK 252.234 | 53.241 | FAST_FLIP_REACTOR_DISPATCH_BUS_HEAT_HARDWARE_UNQUALIFIED |
| pulsed_torch_burn | 47.909 | 0.000 / 0.000 | 0.000 | ordinary_ship_services 0.389, magnet_cryocooling 47.520 | 64.360 | PULSED_TORCH_NOT_CONTINUOUS_HOUSE_GENERATOR |
| Metric_NORMAL | 6.863 | 0.000 / 0.000 | 0.000 | ordinary 0.389, scaled_cryo 5.091, declared_field 1.000, PMAD_loss 0.383 | 9.172 | FIELD_POWER_NONCANON_DECLARED; ENVIRONMENTAL_CORRECTION_POWER_OPEN |
| Metric_FAST | 12.873 | 0.000 / 0.000 | 0.000 | ordinary 0.389, scaled_cryo 9.745, declared_field 2.000, PMAD_loss 0.739 | 17.204 | FIELD_POWER_NONCANON_DECLARED; ENVIRONMENTAL_CORRECTION_POWER_OPEN |
| Metric_EXPEDITE | 20.894 | 0.000 / 0.000 | 0.000 | ordinary 0.389, scaled_cryo 16.291, declared_field 3.000, PMAD_loss 1.214 | 27.923 | FIELD_POWER_NONCANON_DECLARED; ENVIRONMENTAL_CORRECTION_POWER_OPEN |
| Metric_HARD | 42.655 | 0.000 / 0.000 | 0.000 | ordinary 0.389, scaled_cryo 34.764, declared_field 5.000, PMAD_loss 2.502 | 57.010 | FIELD_POWER_NONCANON_DECLARED; ENVIRONMENTAL_CORRECTION_POWER_OPEN |
| quiet_reactors_off | 0.000 | 0.000 / 0.000 | 0.065 | essential_habitat 0.065 | 0.075 retained | THERMAL_BUFFER_LIMIT; BATTERY_THERMAL_COUPLING_UNQUALIFIED |
| cold_running_reactors_off | 0.000 | 0.000 / 0.000 | 0.065 | essential_habitat 0.065 | 0.075 retained | THERMAL_BUFFER_LIMIT; BATTERY_THERMAL_COUPLING_UNQUALIFIED |
| one_unit_failed_Metric_HARD | 42.655 | 0.000 / 0.000 | 0.000 | ordinary 0.389, cryo 34.764, field 5.000, PMAD_loss 2.502 | 57.010 | FAILED_REACTOR_ISOLATION_UNQUALIFIED; METRIC_ENVIRONMENTAL_CORRECTION_OPEN |
| one_unit_failed_torch_magnets | 47.909 | 0.000 / 0.000 | 0.000 | ordinary 0.389, magnet_cryocooling 47.520 | 64.360 | FAILED_REACTOR_ISOLATION_UNQUALIFIED |
| both_house_reactors_failed_hour1 | 0.000 | 0.000 / 0.000 | 0.389 | ordinary_services 0.389 | 0.411 | FAILED_REACTORS_ACTIVE_COOLING_UNQUALIFIED |
| both_house_reactors_failed_essentials | 0.000 | 0.000 / 0.000 | 0.065 | essential_services 0.065 | 0.394 | NONESSENTIAL_LOADS_SHED; BOTH_FAILED_COOLING_UNQUALIFIED |
| c_lite_slow_attitude_recovery | 0.000 | 0.000 / 0.000 | 0.000 |  | 0.000 retained | CHEMICAL_THRUSTER_GEOMETRY_AND_TORQUE_UNQUALIFIED |
| torch_emergency_house_unqualified | 0.000 | 0.000 / 0.000 | 0.000 | ordinary_ship_services 0.389 | 0.000 | TORCH_HOUSE_OUTPUT_UNSIZED; CONTINUOUS_GENERATION_NOT_AUTHORIZED; UNSERVED_LOAD |
| shelter_battery_only | 0.000 | 0.000 / 0.000 | 0.001 | shelter_essential 0.001 | 0.000 | DEDICATED_SHELTER_BATTERY_ONLY; 24H_ENDURANCE_LIMIT |

### Half battery and flywheel performance at unchanged installation mass

Battery delivers 1.423MWh; flywheel delivers 0.712MWh and at most 112.5MW. Reactor/chemical states unchanged. Half-energy battery still carries 1h ordinary followed by 15.91h of 65kW essentials (energy-only); cold thermal limit still bounds.

| State | Half-performance electrical envelope | Basis |
|---|---|---|
| docked_one_online_min | CLOSES | electric ledger unchanged; named hardware/physics holds retained |
| docked_crown_open_worst_sun | CLOSES | electric ledger unchanged; named hardware/physics holds retained |
| coast_one_online_min | CLOSES | electric ledger unchanged; named hardware/physics holds retained |
| coast_recharging_fast_flip | CLOSES | electric ledger unchanged; named hardware/physics holds retained |
| routine_120s_flip | CLOSES | routine untraced throttle proxy, energy and power only |
| fast_40s_flip | FAILS | fast trace supplemental energy and peak power |
| pulsed_torch_burn | CLOSES | electric ledger unchanged; named hardware/physics holds retained |
| Metric_NORMAL | CLOSES | electric ledger unchanged; named hardware/physics holds retained |
| Metric_FAST | CLOSES | electric ledger unchanged; named hardware/physics holds retained |
| Metric_EXPEDITE | CLOSES | electric ledger unchanged; named hardware/physics holds retained |
| Metric_HARD | CLOSES | electric ledger unchanged; named hardware/physics holds retained |
| quiet_reactors_off | CLOSES | battery covers existing cold thermal-buffer limit |
| cold_running_reactors_off | CLOSES | battery covers existing cold thermal-buffer limit |
| one_unit_failed_Metric_HARD | CLOSES | electric ledger unchanged; named hardware/physics holds retained |
| one_unit_failed_torch_magnets | CLOSES | electric ledger unchanged; named hardware/physics holds retained |
| both_house_reactors_failed_hour1 | CLOSES | one hour ordinary services on half-energy battery |
| both_house_reactors_failed_essentials | CLOSES | >=1 hour essentials after 1 hour ordinary; full nominal-hours are reduced |
| c_lite_slow_attitude_recovery | CLOSES | electric ledger unchanged; named hardware/physics holds retained |
| torch_emergency_house_unqualified | FAILS | electric ledger unchanged; named hardware/physics holds retained |
| shelter_battery_only | CLOSES | electric ledger unchanged; named hardware/physics holds retained |

**Qualification holds:** flywheel strength, discharge electronics, containment and counter-rotation; battery thermal/isolation; chemical wet containment/nozzle placement and torque; trace-derived ideal RCS power not demonstrated supply; one-reactor 50MW dynamic dispatch; metric correction; full electrical isolation/heat flow. A closed ledger is not a physical flight certificate.

**Do not merge; preserve full certify verdicts, not inherited historical passes.**
