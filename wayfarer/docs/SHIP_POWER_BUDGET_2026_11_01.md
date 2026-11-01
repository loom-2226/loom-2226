# Wayfarer ship power budget (kT 2026-11-01)

**ENGINEERING SCREEN / NOT HARDWARE FLIGHT CERTIFICATION.** No new simulation, Navigator, Metric arrival or canon mutation. Main base ce9ee081.

Geometry sha256: `49cc20e70f5ad2b39280fa460cec07874a1053ca2a6fed48dda38ca4527d7c6b`.

**Source:** dedicated 80 MW net D–He3 reactor and direct converter at declared 2226 **40 kW/kg** net, 75% electric efficiency. Reactor dry 2.00t is reallocated WITHIN the existing 55t electrical ledger; not a fresh reserve draw. Relational plant is a consumer, Metric bank is never a power source.

**Peak store:** flywheel, 6.50MWh nominal, 6.17MWh delivered at 94.9% charge and discharge; 5.77MWh for ~519MW×40s. 10kWh/kg and 800kW/kg declared 2226 **NOT DEMONSTRATED**; 0.65t dry also reallocated within 55t. At rated 80MW on the coast, **5.16min recharge, ≈11.6 energy-only recharge cycles/hour** when the house reactor can maintain net output and the thermal system is available. This is **not** an operational manoeuvre rate: actual fast flips consume finite RCS remass (5t ring-fenced) and require nozzle, thermal and control readiness. No back-to-back charged peaks.

**Mass:** 5.000t D–He3 separately counted wet; 0.500t dry fuel tank from reserve. Current S1 1172.681t, dry 867.681t, reserve 11.284t (5t mandatory floor, 6.284t free). Fuel location is a mass/CG envelope and actual tank packing, containment and cryo support unqualified.

| State | House MW | Charged store MW | Battery MW | Loads (MW each) | Heat rejected MW / capacity | Outcome | Fuel g/h |
|---|---:|---:|---:|---|---|---|---:|
| docked | 0.399 | 0.000 | 0.0000 | avionics_ECLSS_lighting: 0.045, habitat_heat_pump: 0.324, plant_and_cryo_standby: 0.020, docking_control: 0.010 | 0.523 / 387.212 | **CLOSED (declared basis)** | 0.0054 |
| coast | 0.389 | 0.000 | 0.0000 | avionics_ECLSS_lighting: 0.045, habitat_heat_pump: 0.324, plant_and_cryo_standby: 0.020 | 0.520 / 387.212 | **CLOSED (declared basis)** | 0.0053 |
| coast_recharging_store | 80.000 | 0.000 | 0.0000 | ordinary_ship_services: 0.389, flywheel_charger_DC: 79.611 | 31.142 / 387.212 | **NAMED DEFICIT:** CHARGER_ELECTRONICS_NOT_PHYSICALLY_QUALIFIED | 1.0878 |
| routine_120s_flip | 58.052 | 0.000 | 0.0000 | ordinary_ship_services: 0.389, RCS_120s_throttled_proxy: 57.663 | 25.507 / 387.212 | **NAMED DEFICIT:** RCS_120S_THROTTLING_LAW_DECLARED_NOT_TRACED | 0.7894 |
| fast_40s_flip | 0.389 | 518.969 | 0.0000 | ordinary_ship_services: 0.389, RCS_40s_emergency: 518.969 | 80.489 / 387.212 | **NAMED DEFICIT:** FAST_FLIP_TRANSIENT_POWER_BUS_AND_WASTE_HEAT_UNQUALIFIED | 0.0053 |
| pulsed_torch_burn | 47.909 | 0.000 | 0.0000 | ordinary_ship_services: 0.389, magnet_cryocooling_electric: 47.520 | 64.360 / 73.019; +1400 MW hot-fin rejection | **NAMED DEFICIT:** TORCH_1_TO_10_HZ_PULSES_NOT_HOUSE_POWER_SOURCE | 0.6515 |
| Metric_HARD | 35.153 | 0.000 | 0.0000 | ordinary_ship_services: 0.389, Metric_cryo_chain_at_1300K: 34.764 | 47.008 / 387.212 | **NAMED DEFICIT:** METRIC_FIELD_DRIVE_ELECTRIC_DRAW_UNQUANTIFIED | 0.4780 |
| cold_running | 0.065 | 0.000 | 0.0000 | basic_habitat_electrical: 0.045, plant_and_cryo_standby: 0.020 | 0.007 / passive_skin_and_water_heat_buffer | **NAMED DEFICIT:** BUFFER_FULL_AFTER_9.41_H; REACTOR_DEEP_THROTTLE_UNQUALIFIED | 0.0009 |
| shelter_emergency | 0.021 | 0.000 | 0.0000 | minimal_shelter_24h_backup: 0.001, plant_cryo_and_safety_watch: 0.020 | 0.029 / 387.212 | **NAMED DEFICIT:** SHELTER_72H_LIFE_SUPPORT_DECLARED_BUT_ONLY_24H_BATTERY_IF_HOUSE_LOST | 0.0003 |
| house_reactor_failed | 0.000 | 0.000 | 0.0006 | essential_shelter: 0.001, ordinary_ship_services_unavailable: 0.388 | 0.000 / passive_crown_closed_skin | **NAMED DEFICIT:** NORMAL_LOADS_UNPOWERED_0.388_MW; ESSENTIAL_BATTERY_EXHAUSTED_AFTER_24_H; PULSED_TORCH_HOUSE_MODE_EMERGENCY_ONLY_NOT_CREDITED | 0.0000 |

**Heat accounting:** house fusion heat not converted to electricity is rejected at the reactor efficiency; cryogenic cooling, habitat heat-pump load, declared local RCS nozzle waste (10%), and flywheel charge/discharge inefficiency are separately tracked. The water-jet kinetic/conditioning energy leaves in exhaust except declared 10% onboard loss. Hot fins handle the pulsed torch GW-class heat separately; the electric house reactor does **not** generate those pulses. Cold running shuts active rejection: thermal energy accumulates in existing 50t protected water, without withdrawing or moving its shield mass.

**Cold running:** only ~9.41 h before the existing 50t ×15K heat buffer is filled under this new reactor-waste estimate; cold-running deep turndown and actual thermal coupling remain OPEN. This replaces the earlier ~17h screen based on 10+10kW standby alone.

**Fuel draw:** D–He3 assumed 18.35MeV per D+He3 reaction / 3.53×10^14J/kg released. This is fuel energy, not electric output; at 75% direct conversion, mode-specific g/h are shown above. Five tonnes is a kT inventory allowance, not a calculated mission fuel requirement. The separately pulsed main torch has its own pellet/fuel basis and is NEVER silently an ordinary house generator. On house failure it is emergency-only and not counted in continuous availability.

**Named limits (explicit):** routine RCS power 519MW/9 assumes identical 180° angle, thruster throttlability and 40→120s time scaling of required acceleration; it is not a 120s trace. Electric bus/nozzle transient and real flywheel containment are unqualified. Metric field-load beyond mapped 34.8MW cryo is unknown, so HARD cannot be claimed fully closed. House failure has only 0.6kW×24h battery essential backup: unserved normal loads immediately and emergency battery ends after 24h. The proposed 2226 efficiencies and densities are design assumptions, not extant hardware or accepted canon.

**Acceptance boundary:** G1/G3/G4 targeted reruns and fresh FQ1–FQ4 are required after any wet-mass change. Previous 7f620c53 visual/radiation/FQ certificates do NOT automatically transfer to this new geometry; no main merge authorised by this engineering study.
