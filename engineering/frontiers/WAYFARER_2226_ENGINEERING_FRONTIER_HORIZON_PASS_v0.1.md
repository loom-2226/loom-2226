# Wayfarer 2226 Engineering Frontier — Bounded Horizon Pass v0.1

**Status:** PASS B / PROVISIONAL SCENARIO ENVELOPES  
**Protocol:** `LOOM_2226_ENGINEERING_FRONTIER_PROTOCOL_v0.1`  
**Authority:** NOT FROZEN / NOT DOWNSTREAM AUTHORITY  
**Target epoch:** 2226

## Purpose

Convert the literature review into a deliberately shallow set of ordinary-engineering 2226 scenario envelopes for the Wayfarer drivetrain. This is not a prediction and does not certify components. Where the evidence does not justify a future number, the output remains `UNRESOLVED` or is expressed as a dimensionless improvement factor relative to a named 2026 system baseline.

The pass deliberately avoids detailed component design. It uses three scenario labels:

- `CONSERVATIVE_2226`: modest improvement that should remain comfortably inside known physics;
- `MVP_2226`: working LOOM ordinary-engineering scenario;
- `AGGRESSIVE_2226`: sensitivity case that remains known-physics-compatible but needs substantially better engineering.

These are scenario bounds, not probabilities.

## Cross-cutting rules

1. No unknown mechanism is projected into existence.
2. No efficiency is set to 100%.
3. Temperature-dependent and environment-dependent properties stay conditional on their operating point.
4. Record material/device values are not installed-system values.
5. Improvements are derived once in F1–F6 and inherited by F7/F8.
6. Where a future absolute number would require arbitrary architecture choices, use a bounded improvement factor or leave it unresolved.
7. The integrated accountant must reject combinations that violate mass, heat, stored-energy, stress, radiation/lifetime, or efficiency constraints.

# F1 — Fields / superconductors / magnets

Evidence status: `INSUFFICIENT_FOR_QUANTITATIVE_HINDCAST` for a like-for-like Wayfarer-scale continuous magnet class.

2026 evidence classes include demonstrated 20 T full-scale large-bore REBCO fusion magnet work, 32 T all-superconducting research magnet, ITER-scale 11.8–13 T very-large magnet systems, and separate hybrid/pulsed records. These are not one statistical series.

| Parameter | Conservative 2226 | MVP 2226 | Aggressive 2226 | Status |
|---|---:|---:|---:|---|
| Large-system continuous useful field | UNSET | UNSET | UNSET | coupled scenario/accountant required |
| Engineering current density at required B,T,strain | 1.5× relevant 2026 system baseline | 2× | 3× | scenario factor, must survive critical-surface check |
| Installed magnet specific mass at like field/bore | 0.75× 2026 like-for-like system burden | 0.5× | 0.33× | scenario factor, not independent of structure/J_e |
| Cryogenic parasitic burden at like cold load | 0.7× | 0.5× | 0.33× | scenario factor; thermodynamics still applies |
| Protection/stored-energy capability | 1.5× admissible energy per installed protection mass | 2× | 3× | scenario factor; no free quench protection |
| Radiation/fluence lifetime | 2× relevant qualified exposure | 3× | 5× | scenario factor; consumer environment required |

**Reason for leaving field UNSET:** field is an emergent coupled output, not an independent multiplier. The accountant must solve it from bore, J_e, structure, stored energy, protection, thermal and radiation constraints.

# F2 — Power conversion / PMAD

Literature anchors establish that PMAD is a real spacecraft mass and efficiency subsystem; SiC-class wide-bandgap devices enable higher-temperature/high-power conversion but radiation and voltage derating remain binding engineering concerns. Historical high-power concepts already separate source, conversion, PMAD and radiator burdens rather than treating electrical power as free.

| Parameter | Conservative 2226 | MVP 2226 | Aggressive 2226 | Status |
|---|---:|---:|---:|---|
| High-power conversion efficiency, per major stage | 97% | 98% | 99% | scenario envelope; never 100% |
| PMAD end-to-end efficiency across a representative high-power path | 94% | 96% | 98% | scenario envelope; topology dependent |
| Converter/PMAD specific power at like voltage/isolation/radiation duty | 3× 2026 relevant system baseline | 5× | 10× | factor; system baseline must be selected by accountant |
| Radiation/high-temperature voltage derating | >=20% headroom retained | >=15% | >=10% | engineering margin, not device physics claim |
| Pulse-power delivery | UNRESOLVED | UNRESOLVED | UNRESOLVED | architecture belongs with F3 load duration |

**Firewall:** no fusion-source specific power is inferred here. F2 begins at an available source output interface and accounts for conversion/distribution.

# F3 — Energy storage / transient buffering

NASA treats high-energy and high-power cells as different designs; spacecraft battery packs carry BMS/interconnect/thermal burdens, and capacitors are used for repeated short high-power pulses. Therefore one universal future `Wh/kg` is rejected.

| Parameter | Conservative 2226 | MVP 2226 | Aggressive 2226 | Status |
|---|---:|---:|---:|---|
| Electrochemical pack usable specific energy | 2× 2026 flight-relevant pack baseline | 3× | 5× | scenario factor, chemistry not selected |
| Electrochemical pack specific power | 2× | 4× | 8× | scenario factor, cannot be combined freely with max specific energy |
| Short-duration capacitor/pulse specific power | 3× relevant 2026 system baseline | 5× | 10× | scenario factor |
| Round-trip efficiency | 90% | 95% | 98% | system scenario; technology-class dependent |
| Cycle/lifetime at fixed depth-of-discharge and environment | 2× | 4× | 8× | scenario factor; mission conditions required |

**Ragone firewall:** maximum energy-density and maximum power-density factors cannot automatically be applied to the same device state. The accountant must choose a consistent storage class/load duration.

# F4 — Structures / shielding / extreme materials

Current NASA and DOE literature already supports C/C and SiC/SiC families for high-temperature structural service and treats fusion radiation damage, swelling, embrittlement, creep-fatigue, joints, coolant compatibility and transmutation as coupled lifetime limits. This pass therefore avoids a universal future strength number.

| Parameter | Conservative 2226 | MVP 2226 | Aggressive 2226 | Status |
|---|---:|---:|---:|---|
| Installed specific load capability at same temperature/environment | 1.5× 2026 qualified structural system | 2× | 3× | scenario factor |
| High-temperature structural service capability | +100 K over relevant qualified class | +200 K | +400 K | conditional scenario, never beyond material stability/chemistry |
| Creep/fatigue service life at fixed load/T/environment | 2× | 3× | 5× | scenario factor |
| Fusion-relevant radiation/fluence lifetime | 2× qualified relevant baseline | 3× | 5× | scenario factor; no extrapolation from ion-only exposure as equivalent to fusion spectrum |
| Plasma/erosion-facing service life at fixed flux/T | 1.5× | 2× | 3× | scenario factor |
| Shielding mass per required attenuation | UNRESOLVED | UNRESOLVED | UNRESOLVED | depends on spectrum/material/geometry; no magic shielding multiplier |

**Explicit rejection:** the prior blanket 8× structural-strength assumption is not used.

# F5 — Thermal transport / radiators

Space radiator literature shows large differences by operating temperature and architecture. Demonstrated/tested carbon-carbon heat-pipe elements have reached roughly 1.5–2.1 kg/m² class two-sided element mass, while complete radiators carry headers, deployment, protection and controls. High-temperature conceptual fusion radiators can achieve low kg/kW only because Stefan–Boltzmann flux rises strongly with temperature. Therefore the frontier is temperature-conditional.

| Parameter | Conservative 2226 | MVP 2226 | Aggressive 2226 | Status |
|---|---:|---:|---:|---|
| Effective radiator emissivity | 0.85 | 0.90 | 0.95 | bounded surface/system scenario |
| Installed radiator areal mass at like T/survivability | 0.75× relevant 2026 system baseline | 0.5× | 0.33× | scenario factor; element records are not system baseline |
| Heat-transport hardware specific capacity | 2× 2026 relevant loop/heat-pipe baseline | 3× | 5× | scenario factor |
| High-temperature radiator/loop operating capability | +100 K over qualified class | +200 K | +400 K | conditional on F4/material compatibility |
| Turndown/freeze/restart envelope | 2× present qualified operating range | 3× | 5× | scenario factor, architecture dependent |
| Thermal-buffer usable specific energy | 2× relevant 2026 buffer baseline | 3× | 5× | scenario factor, material/temperature dependent |

The accountant shall always recompute radiative flux from `q = epsilon sigma (T^4 - T_sink^4)` rather than multiplying heat rejection independently of temperature.

# F6 — Fluids / cryogenics / RCS enabling engineering

NASA's cryogenic-fluid work supports long-duration zero-boiloff as an active refrigeration/storage capability, not perfect insulation. Current spacecraft propulsion establishes mature chemical and electric propulsion classes; e.g. hydrazine-class thrusters remain roughly 200–235 s Isp, while NASA's 12.5 kW HERMeS Hall thruster demonstrated ~2,820 s and 68% total thrust efficiency. Those are class anchors, not Wayfarer RCS selections.

| Parameter | Conservative 2226 | MVP 2226 | Aggressive 2226 | Status |
|---|---:|---:|---:|---|
| Cryogenic storage parasitic power at same tank/heat-leak/T | 0.7× 2026 active-storage burden | 0.5× | 0.33× | scenario factor; Carnot/refrigerator accounting required |
| Cryogenic tank+insulation specific mass at same stored-fluid class | 0.8× | 0.6× | 0.5× | scenario factor |
| Long-duration retention | zero-boiloff feasible when active cooling closes | same | same | capability condition, not zero power |
| Pump/valve/feed specific power at like pressure/flow | 0.7× 2026 burden | 0.5× | 0.33× | scenario factor |
| Feed-system controllable turndown | 2× relevant 2026 qualified range | 5× | 10× | scenario factor; response/stability must close |
| Conventional RCS performance | NO UNIVERSAL MULTIPLIER | NO UNIVERSAL MULTIPLIER | NO UNIVERSAL MULTIPLIER | select physical cycle/working fluid first |

**RCS firewall:** F6 does not select Wayfarer working fluid, exhaust velocity, MIB, valve response, plume, cycle life or mount hardware. Once a cycle is selected, it may consume these ordinary engineering envelopes.

# F7 — Fusion / torch integration

F7 receives F1/F2/F4/F5/F6. It receives no independent 200-year multiplier.

Provisional integration outputs:

1. `fusion_source_specific_power = UNRESOLVED` — reactor/source mechanism and balance-of-plant not earned.
2. `source_to_remass_directed_fraction = UNRESOLVED` — physical coupling mechanism not earned.
3. `installed_magnetic_nozzle_capability = UNRESOLVED` — must emerge from F1 plus nozzle/plasma physics.
4. `thermal_rejection_capability = DERIVED_FROM_F5_AT_EARNED_P_HEAT_ONLY`.

This preserves the existing E1 technology holds.

# F8 — E2 / metric / LOOM support integration

F8 receives F1–F5 ordinary support capabilities. It receives no propulsion or metric mechanism from this register.

Provisional integration outputs:

1. `e2_available_field_mass_power_envelope = PENDING_INTEGRATED_ACCOUNTANT`.
2. `e2_momentum_partner_or_sink = UNRESOLVED_BY_FRONTIER / MUST_BE_EARNED_BY_E2_RESEARCH`.
3. `metric_support_power_thermal_field_envelope = PENDING_INTEGRATED_ACCOUNTANT`.
4. `metric_constitutive_law_and_mc299m_properties = OUT_OF_SCOPE / PHYSICS_AUTHORITY_ONLY`.

# Parameter count

This pass uses 6 + 5 + 5 + 6 + 6 + 6 + 4 + 4 = **42 slots**, exactly the register ceiling. Several slots remain `UNRESOLVED`; this is intentional and preferable to invented precision.

# Pass-B disposition

- No new-physics mechanism has been created.
- No 2226 magnet field has been guessed.
- No fusion source specific power has been guessed.
- No universal RCS exhaust velocity has been guessed.
- No magic shielding factor has been guessed.
- The ordinary engineering scenarios are predominantly bounded factors relative to a relevant 2026 system class, reducing category errors and false precision.
- Absolute efficiencies/emissivity values are capped below perfection and must still survive integrated accounting.

**Next required artifact:** one integrated drivetrain accountant that selects a consumer case and applies these factors without double counting. Its first purpose is to expose which of the 42 slots actually matter; unused slots should be deleted before v1.0 freeze.

## Primary literature anchors

- NASA Small Spacecraft Technology State of the Art 2026, Power and Propulsion chapters: https://www.nasa.gov/smallsat-institute/sst-soa/
- NASA, 2022 State of the Art Small Spacecraft Technology, battery system/cell distinction and energy-storage metrics: https://www.nasa.gov/wp-content/uploads/2023/05/2022-soa-full.pdf
- NASA NTRS, HERMeS 12.5 kW performance: https://ntrs.nasa.gov/citations/20170001283
- NASA, Solar Electric Propulsion / AEPS: https://www.nasa.gov/space-technology-mission-directorate/tdm/solar-electric-propulsion/
- NASA, liquid-hydrogen two-stage active zero-boiloff testing: https://www.nasa.gov/directorates/stmd/tech-demo-missions-program/cryogenic-fluid-management-cfm/stay-cool-nasa-tests-innovative-technique-for-super-cold-fuel-storage/
- NASA NTRS, cryogenic zero-boiloff system sizing: https://ntrs.nasa.gov/citations/20160000337
- NASA Technology Transfer, SiC/SiC CMCs for high-temperature structural service: https://technology.nasa.gov/patent/LEW-TOPS-25
- U.S. DOE Fusion Science & Technology Roadmap, structural materials and nuclear-effects testing: https://www.energy.gov/documents/fusion-science-and-technology-roadmap
- NASA NTRS, carbon-carbon heat-pipe radiator specific mass: https://ntrs.nasa.gov/citations/19980236936
- NASA NTRS, intermediate-temperature ceramic heat pipe example: https://ntrs.nasa.gov/citations/20240009802
- NASA NTRS, multimegawatt heat-pipe radiator design: https://ntrs.nasa.gov/citations/19890065892
- F1 magnet evidence sources are preserved separately in `F1_SUPERCONDUCTOR_MAGNET_EVIDENCE_PASS_v0.1.md`.
