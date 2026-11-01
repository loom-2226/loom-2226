# Wayfarer house power, storage and independent slow recovery | 2026-11-01

**ENGINEERING CANDIDATE, NON-CANON. NO HARDWARE QUALIFICATION. PR #440 DRAFT, NO MERGE.**

Geometry SHA256: `4d598212aeb46fab14b326a6023bb6d55e7d584599d91fe821ef8a2f2d837331`; exact current 40s RCS trace: `66a773203d774d3b325c25cd8d09e0d66264036d0e02d8f324d14ff91c2822d3`. Historic FQ/acceptance does not transfer between hashes.

**Reactors:** 2×50MW net D–He3, each 5MW minimum online, 2.50t dry, A aft C-ring/B forward service ring; 40kW/kg and 75% net conversion declared. Must cycle off or store/spill surplus; never throttle to sub-MW.

**Battery:** 3.0MWh nominal / 2.846MWh discharge, 1.50t at declared 2.0kWh/kg; quiet 65kW energy-only 43.8h. Both reactors failed: first 1h normal, then 37.80h 65kW essential energy-only.

**Pulse flywheel:** counter-rotating pairs with burst containment, 1.8MWh nominal / 1.708MWh delivered, 1.8t at 1.0kWh/kg and 150.0kW/kg. Declared 270.0MW maximum. The full 40s current-geometry trace requires 1.302MWh and 202.7MW peak after one steady 50MW reactor. Actual heater/power-switching implementation is OPEN.

**Dock and torch:** docked reactors OFF, external shore power 2MW declared. During pulsed torch BURN ONLY magnets get 47.52MW from internal torch power tap (gross 63.36MW at 75% conversion, heat 15.84MW). Source extraction and jet debit physically OPEN; never count it as house generator. Chain: reactor B, battery, C-lite attitude only.

**C-lite:** 0.25t provisioned (dry 0.10t + wet 0.15t), ~75kg for a 600s recovery, 2 nominal turns. Dynamics still UNQUALIFIED.

**Mass:** dry 867.531453t, loaded S1 1172.681453t. Loaded electrical line 55t = 54.85t dry + 0.15t C-lite wet propellant. Engineering reserve **11.284117t unchanged**; 6.284t above hard floor. C-lite fuel is a consumable, NOT dry ballast.

**Cold-running thermal bound:** 11.70h for the accepted 50t×15K protected-water buffer. Battery energy-only endurance is not a thermal qualification.

**Metric:** E1 cryo and PMAD numbers preserved; separately declared field/control NORMAL 1 / FAST 2 / EXPEDITE 3 / HARD 5MW; environmental correction remains OPEN. 2GJ reversible field bank is not a house source.

| Operating state | House MW | Shore MW | Torch self MW | Flywheel out / charge MW | Battery MW | Loads MW | Heat rejected MW | State deficits |
|---|---:|---:|---:|---:|---:|---|---:|---|
| docked_shore_power | 0.000 | 0.399 | 0.000 | 0.000 / 0.000 | 0.000 | ordinary_ship_services 0.389, docking_control 0.010 | 0.390 | SHORE_PLUG_AND_SUPPLY_INTERFACE_UNQUALIFIED |
| docked_crown_open_worst_sun | 0.000 | 1.096 | 0.000 | 0.000 / 0.000 | 0.000 | avionics_ECLSS 0.045, standby 0.020, heat_pump 1.021, docking 0.010 | 1.188 | AOI_OPTICAL_ATTENUATION_UNCREDITED; SHORE_PLUG_AND_SUPPLY_INTERFACE_UNQUALIFIED |
| coast_one_online_min | 5.000 | 0.000 | 0.000 | 0.000 / 4.611 | 0.000 | ordinary_ship_services 0.389 | 2.294 | FULL_PULSE_STORE_REACTOR_OFF_OR_BATTERY_CHARGE |
| coast_recharging_fast_flip | 50.000 | 0.000 | 0.000 | 0.000 / 49.611 | 0.000 | ordinary_ship_services 0.389 | 19.603 | CHARGER_BULK_POWER_UNQUALIFIED |
| routine_120s_flip | 50.000 | 0.000 | 0.000 | 8.052 / 0.000 | 0.000 | ordinary_ship_services 0.389, RCS_120s_UNTRACED_proxy 57.663 | 23.259 | RCS_ROUTINE_THROTTLE_PROXY_UNTRACED |
| fast_40s_flip | 50.000 | 0.000 | 0.000 | 202.653 / 0.000 | 0.000 | ordinary_ship_services 0.389, RCS_40s_TRACE_PEAK 252.264 | 53.246 | FAST_FLIP_REACTOR_DISPATCH_BUS_HEAT_HARDWARE_UNQUALIFIED |
| pulsed_torch_burn | 5.000 | 0.000 | 47.520 | 0.000 / 4.611 | 0.000 | ordinary_ship_services 0.389, magnet_cryocooling 47.520 | 66.134 | TORCH_BURN_ONLY_POWER_TAP_UNQUALIFIED; TORCH_TAP_NOT_DEBITED_FROM_FLIGHT_THRUST |
| Metric_NORMAL | 6.863 | 0.000 | 0.000 | 0.000 / 0.000 | 0.000 | ordinary 0.389, scaled_cryo 5.091, declared_field 1.000, PMAD_loss 0.383 | 9.172 | FIELD_POWER_NONCANON_DECLARED; ENVIRONMENTAL_CORRECTION_POWER_OPEN |
| Metric_FAST | 12.873 | 0.000 | 0.000 | 0.000 / 0.000 | 0.000 | ordinary 0.389, scaled_cryo 9.745, declared_field 2.000, PMAD_loss 0.739 | 17.204 | FIELD_POWER_NONCANON_DECLARED; ENVIRONMENTAL_CORRECTION_POWER_OPEN |
| Metric_EXPEDITE | 20.894 | 0.000 | 0.000 | 0.000 / 0.000 | 0.000 | ordinary 0.389, scaled_cryo 16.291, declared_field 3.000, PMAD_loss 1.214 | 27.923 | FIELD_POWER_NONCANON_DECLARED; ENVIRONMENTAL_CORRECTION_POWER_OPEN |
| Metric_HARD | 42.655 | 0.000 | 0.000 | 0.000 / 0.000 | 0.000 | ordinary 0.389, scaled_cryo 34.764, declared_field 5.000, PMAD_loss 2.502 | 57.010 | FIELD_POWER_NONCANON_DECLARED; ENVIRONMENTAL_CORRECTION_POWER_OPEN |
| quiet_reactors_off | 0.000 | 0.000 | 0.000 | 0.000 / 0.000 | 0.065 | essential_habitat 0.065 | 0.075 retained | THERMAL_BUFFER_LIMIT; BATTERY_THERMAL_COUPLING_UNQUALIFIED |
| cold_running_reactors_off | 0.000 | 0.000 | 0.000 | 0.000 / 0.000 | 0.065 | essential_habitat 0.065 | 0.075 retained | THERMAL_BUFFER_LIMIT; BATTERY_THERMAL_COUPLING_UNQUALIFIED |
| one_unit_failed_Metric_HARD | 42.655 | 0.000 | 0.000 | 0.000 / 0.000 | 0.000 | ordinary 0.389, cryo 34.764, field 5.000, PMAD_loss 2.502 | 57.010 | FAILED_REACTOR_ISOLATION_UNQUALIFIED; METRIC_ENVIRONMENTAL_CORRECTION_OPEN |
| one_unit_failed_torch_magnets | 5.000 | 0.000 | 47.520 | 0.000 / 4.611 | 0.000 | ordinary 0.389, magnet_cryocooling 47.520 | 66.134 | FAILED_REACTOR_ISOLATION_UNQUALIFIED; TORCH_BURN_ONLY_POWER_TAP_UNQUALIFIED; TORCH_TAP_NOT_DEBITED_FROM_FLIGHT_THRUST |
| degraded_60s_flip | 50.000 | 0.000 | 0.000 | 62.508 / 0.000 | 0.000 | ordinary_ship_services 0.389, RCS_60s_trace_peak 112.119 | 31.650 | DEGRADED_FLIP_REAL_BUS_AND_HEAT_UNQUALIFIED |
| both_house_reactors_failed_hour1 | 0.000 | 0.000 | 0.000 | 0.000 / 0.000 | 0.389 | ordinary_services 0.389 | 0.411 | FAILED_REACTORS_ACTIVE_COOLING_UNQUALIFIED |
| both_house_reactors_failed_essentials | 0.000 | 0.000 | 0.000 | 0.000 / 0.000 | 0.065 | essential_services 0.065 | 0.394 | NONESSENTIAL_LOADS_SHED; BOTH_FAILED_COOLING_UNQUALIFIED |
| c_lite_slow_attitude_recovery | 0.000 | 0.000 | 0.000 | 0.000 / 0.000 | 0.000 |  | 0.000 retained | CHEMICAL_THRUSTER_GEOMETRY_AND_TORQUE_UNQUALIFIED |
| shelter_battery_only | 0.000 | 0.000 | 0.000 | 0.000 / 0.000 | 0.001 | shelter_essential 0.001 | 0.000 | DEDICATED_SHELTER_BATTERY_ONLY; 24H_ENDURANCE_LIMIT |

### Half battery and flywheel performance at unchanged installation mass

Battery delivers 1.423MWh; flywheel delivers 0.854MWh and at most 135.0MW. Reactor/chemical states unchanged. Half-energy battery carries 1h ordinary followed by 15.91h essentials energy-only; cold thermal limit remains. Actual 60s one-reactor store event 0.497MWh, peak 62.5MW.

| State | Half-performance electrical envelope | Basis |
|---|---|---|
| docked_shore_power | CLOSES | electric ledger unchanged; named hardware/physics holds retained |
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
| degraded_60s_flip | CLOSES | 60s source-recomputed half-performance, one 50MW reactor |
| both_house_reactors_failed_hour1 | CLOSES | one hour ordinary services on half-energy battery |
| both_house_reactors_failed_essentials | CLOSES | >=1 hour essentials after 1 hour ordinary; full nominal-hours are reduced |
| c_lite_slow_attitude_recovery | CLOSES | electric ledger unchanged; named hardware/physics holds retained |
| shelter_battery_only | CLOSES | electric ledger unchanged; named hardware/physics holds retained |

### Explicit 2226 engineering declarations and outstanding kT choices

- ACCEPTED BY kT FOR THIS DRAFT: 1.8MWh / 1.8t flywheel, 1kWh/kg, 150kW/kg (270MW max), 90% round trip and counter-rotating contained assembly. Engineering tests of actual rotor packing/containment still OPEN.
- ACCEPTED BY kT FOR THIS DRAFT: reactor A aft C-ring, reactor B forward service ring as separate physical mass envelopes. Independent vessel shielding, reactor-failure isolation and switching NOT QUALIFIED.
- ACCEPTED BY kT FOR THIS DRAFT: if electrical storage half-performance, stretch 40s emergency pitch flip to 60s, using one surviving 50MW house reactor. Source-derived event passes the specified ideal power screen; hardware and other attitude axes OPEN.
- NEW DECLARATION FOR kT: dock external electrical interface rated 2.0MW (current worst solar crown-open dock load ~1.096MW), reactors OFF. Shore-side source/connector, isolation, and thermal fit OPEN.
- NEW DECLARATION FOR kT: pulsed torch supplies 47.52MW net magnet/cryocooling ONLY WHILE BURNING via conversion at 75%: 63.36MW raw torch energy diversion, 15.84MW rejected conversion heat. Not charged to house, but this diversion is NOT YET reflected in the propulsion flight model and real tap/conditioning is OPEN.
- EXISTING UNQUALIFIED DECLARATIONS RETAINED: 2×50MW reactors at 40kW/kg net and 10% minimum; battery 2kWh/kg 90% round trip; C-lite 75kg/600s slow chemical turns and independent torque; Metric field watts NORMAL/FAST/EXPEDITE/HARD 1/2/3/5MW delivered, environment correction HOLD.
- INDEPENDENT CABIN REFUGE: the 0.6kW×24h shelter battery remains isolated; not a replacement for reactor B/battery/C-lite failure chain.

**Source event scope:** 40s and 60s are full-remass pitch diagnostics with current rigid-body inertia and ideal water heating/jet energy. They do not establish all axes, zero-house-power rescue or actual rotor/chemical hardware.


**Qualification holds:** flywheel strength, discharge electronics, containment and counter-rotation; battery thermal/isolation; chemical wet containment/nozzle placement and torque; trace-derived ideal RCS power not demonstrated supply; one-reactor 50MW dynamic dispatch; metric correction; full electrical isolation/heat flow. A closed ledger is not a physical flight certificate.

**Do not merge; preserve full certify verdicts, not inherited historical passes.**
