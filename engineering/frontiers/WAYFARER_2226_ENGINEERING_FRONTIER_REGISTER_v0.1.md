# Wayfarer 2226 Engineering Frontier Register v0.1

**Status:** WORKING REGISTER / BOUNDED HORIZON PASS  
**Protocol:** `LOOM_2226_ENGINEERING_FRONTIER_PROTOCOL_v0.1`  
**Authority:** NO NEW DOWNSTREAM NUMERICAL AUTHORITY UNTIL FREEZE  
**Target epoch:** 2226

## BLUF

This register prevents the Frontier program from becoming eight dissertations. It derives a compact shared set of ordinary-engineering capabilities for the Wayfarer drivetrain, once, then lets torch, RCS, E2, metric/LOOM and other consumers pin those producer values.

Target size: **30–50 projected engineering parameters total**. A parameter that cannot be bounded quickly and honestly remains `UNRESOLVED`.

## Hard scope rules

1. Short evidence cards, not component design studies.
2. Prefer demonstrated 2026 system anchors; separate laboratory/material records from installed capability.
3. Quantitative hindcasting only where the protocol's like-for-like evidence floor is met. Otherwise use bounded scenario construction.
4. Project ordinary engineering enablers only. Unknown E2, metric, LOOM, fusion-source or nozzle mechanisms are not extrapolated into existence.
5. Known physics remains the accountant: conservation, thermodynamics, radiation, stress, critical surfaces, Stefan-Boltzmann, electrochemistry and relevant constitutive limits.
6. Shared producer capability is derived once and reused; consumers do not receive independent favorable multipliers.
7. One integrated accountant after the cards; Z3 only for genuinely coupled satisfiability.
8. One hostile review of the integrated register, then freeze. Reopen only for a downstream contradiction or materially new evidence.

## Frontier families

### F1 — Fields, superconductors and magnets
**Consumers:** fusion/confinement, torch magnetic nozzle, E2 external-field/plasma candidates, metric/LOOM hardware where earned physics requires fields.

**Project at most:** continuous field vs useful bore/scale; engineering current-density envelope; installed magnet specific mass; operating-temperature/cryogenic burden; stored-energy/protection burden; radiation/fluence lifetime.

**Current status:** evidence pass complete enough to classify `INSUFFICIENT_FOR_QUANTITATIVE_HINDCAST`; bounded scenario + coupled system accounting required. No field value frozen.

### F2 — Power generation, conversion and distribution
**Consumers:** fusion driver/source balance-of-plant, torch auxiliaries, RCS/feed, E2, metric/LOOM, thermal systems.

**Project at most:** continuous source-independent electrical conversion efficiency; converter/distribution specific power; voltage/field/current-density envelope; radiation/high-temperature derating; pulse-power delivery where relevant.

**2026 anchors:** NASA identifies SiC as enabling smaller/lighter and higher-efficiency spacecraft power conversion, while current radiation testing shows heavy-ion degradation/single-event burnout can force substantial voltage derating. NASA's 2026 small-spacecraft state-of-art report provides a current power baseline. Space fission remains at tens-of-kW demonstration scale, so source specific power for a Wayfarer fusion source is NOT to be inferred from fission progress.

### F3 — Energy storage and transient buffering
**Consumers:** pulse loads, startup/transients, field systems, metric/LOOM support hardware, thermal buffers.

**Project at most:** usable specific energy; specific power; round-trip efficiency; cycle/lifetime envelope; thermal/protection burden.

**Firewall:** do not choose a chemistry merely to hit a desired ship number. Separate electrochemical, capacitor, flywheel/SMES and thermal-buffer regimes where their metric semantics differ.

### F4 — Structures, shielding and extreme-environment materials
**Consumers:** thrust frame, reactor/shield region, magnetic systems, radiators, RCS mounts, pressure/cryogenic systems, metric/LOOM support hardware.

**Project at most:** system-level usable specific strength/stiffness; operating-temperature derating; creep/fatigue/lifetime; radiation/neutron fluence tolerance; erosion/plasma-facing durability; shielding mass-performance where ordinary materials physics supports it.

**Firewall:** material coupon strength is not installed structure; no blanket 8x multiplier. The prior ~56 GPa/375 T experiment remains an example of what this frontier must prevent.

### F5 — Thermal transport, buffering and radiators
**Consumers:** essentially the entire drivetrain.

**Project at most:** radiator operating-temperature envelope by material/loop class; effective emissivity; installed radiator specific mass or kg/kW at stated temperature; heat-transport specific capacity; turndown/freeze tolerance; thermal-buffer specific energy.

**2026 anchors:** NASA treats radiator mass as a major limiting term for multi-megawatt nuclear-electric systems; older carbon-carbon heat-pipe prototypes demonstrated the possibility of ~1.45 kg/m^2 element-level specific mass, while modern work continues on lightweight, damage/freeze-tolerant and high-turndown radiators. Stefan-Boltzmann remains immutable: higher rejection temperature earns area reduction only if materials and loops survive it.

### F6 — Fluids, propellants, cryogenics and RCS enabling engineering
**Consumers:** torch remass feed, RCS, fusion auxiliaries, cooling loops and storage.

**Project at most:** tank/system mass fraction by storage class; heat leak/active refrigeration burden; long-duration retention; pump/valve/injector specific power and response class; conventional thruster performance/lifetime envelope; feed-system turndown.

**2026 anchors:** NASA is actively demonstrating two-stage active cooling aimed at zero-boiloff liquid-hydrogen storage, while current in-space cryogenic storage/transfer remains an acknowledged technology gap. Zero boiloff is therefore an energy-accounted active capability, never perfect insulation. NASA's 2026 propulsion state-of-art provides conventional/electric thruster anchors.

**RCS firewall:** this frontier may bound ordinary component capability but does not silently select Wayfarer RCS working fluid, exhaust velocity, hardware MIB, valve response, cycle life, plume or mount design.

### F7 — Fusion and torch enabling engineering
**Consumers:** Wayfarer primary torch.

**This is a consumer/integration frontier, not a license to extrapolate fusion physics.**

**Project at most:** only shared enabling quantities inherited from F1/F2/F4/F5/F6 plus evidence-supported plasma-facing lifetime, driver/conversion burden and balance-of-plant specific mass ranges where ordinary engineering permits.

**Must remain unresolved unless separately earned:** fusion gain/source physics, `SOURCE_REACTOR_REALIZABILITY`, source directed fraction, neutron/photon/particle deposition, remass species, nozzle plasma coupling/detachment/divergence/interception/erosion and certified source/nozzle hardware.

### F8 — E2, metric and LOOM enabling engineering
**Consumers:** E2 momentum-coupled propulsion, metric drive support systems, LOOM-specific hardware.

**Project at most:** inherited fields/magnets, electrical/pulse power, thermal rejection, structures, energy storage, radiation tolerance, switching/control precision, metrology and fabrication tolerance where these are ordinary engineering quantities.

**Hard firewall:** this frontier projects **support technology only**. It may not project an unknown momentum-coupling mechanism, momentum sink, metric constitutive law, Mc-299m property, topology manipulation mechanism or other unearned LOOM/RF physics. Research-derived exotic properties enter through their own governed physics authority, not through a 200-year engineering multiplier.

## Dependency graph

`F4 STRUCTURES/MATERIALS -> F1 FIELDS, F5 THERMAL, F6 FLUIDS`

`F2 POWER + F3 BUFFERING + F1 FIELDS + F4 MATERIALS + F5 THERMAL + F6 FLUIDS -> F7 FUSION/TORCH`

`F1 + F2 + F3 + F4 + F5 -> F8 E2/METRIC/LOOM SUPPORT`

RCS primarily consumes F2/F4/F6. No consumer gets to reapply a producer improvement as a second multiplier.

## Parameter budget

The first frozen register should remain within approximately 30–50 total projected quantities. Initial allocation ceiling:

- F1: 6
- F2: 5
- F3: 5
- F4: 6
- F5: 6
- F6: 6
- F7: 4 integration outputs beyond inherited producer values
- F8: 4 integration outputs beyond inherited producer values

Maximum initial budget: **42 quantities**. Reducing this count is preferred. Exceeding it requires explicit justification that a downstream drivetrain decision cannot be made without the added parameter.

## Work plan and exit criteria

### Pass A — evidence cards
For F2–F6, collect only enough primary-source evidence to establish current demonstrated classes, major binding physics/system constraints, and whether quantitative hindcasting is admissible. F1 already has its first evidence pass. F7/F8 mostly consume producer frontiers rather than repeat research.

**Exit:** every parameter is `EARNED_2026_ANCHOR`, `SCENARIO_REQUIRED`, or `UNRESOLVED`; no unclassified gaps.

### Pass B — bounded 2226 cases
For each producer parameter create conservative/MVP/aggressive bounded scenarios. A scenario must identify the mundane improvement mechanism and known-physics/system constraint. No raw 200-year exponential becomes authority.

**Exit:** all proposed numbers/ranges have provenance and uncertainty; unsupported parameters remain `UNRESOLVED`.

### Pass C — integrated accountant
One Python model consumes the register and checks efficiency chains, waste heat, mass burdens, field/stored-energy burdens, structural/thermal compatibility, cryogenic loads and obvious cross-frontier double counting. Use Z3 only where coupled constraints make SMT materially useful.

**Exit:** no silent contradiction among frozen producer values; failures identify the offending assumptions rather than invent fixes.

### Pass D — hostile review and freeze
Give the complete register, evidence cards, equations, assumptions and accountant outputs to an adversarial reviewer. Fix specific defects once. Freeze `WAYFARER_2226_ENGINEERING_FRONTIER_REGISTER_v1.0` with a producer version/hash.

**Exit:** downstream consumers can cite one governed 2226 ordinary-engineering baseline. Further frontier research stops unless a consumer exposes a contradiction or materially new evidence warrants reopening.

## Current authority

- Protocol hostile-review conditions: incorporated.
- F1: evidence pass performed; numerical authority `UNSET`.
- F2–F6: scoped; evidence passes pending.
- F7/F8: consumer/integration scope defined; mechanism authority explicitly excluded.
- Integrated 2226 register: `NOT_YET_FROZEN`.

## Initial primary-source anchors

- NASA, 2026 State-of-the-Art of Small Spacecraft Technology: power, propulsion, structures/materials and thermal-control baseline. https://www.nasa.gov/smallsat-institute/sst-soa/
- NASA Glenn, Silicon Carbide Electronics and Sensors: high-temperature/high-power/radiation context and spacecraft power-conversion benefits. https://www.nasa.gov/glenn/research/silicon-carbide-electronics-sensors/
- NASA TechPort, Silicon Carbide Power Components for NASA Lunar Surface Applications: radiation degradation and single-event-burnout limitations. https://techport.nasa.gov/projects/118469
- NASA, Cryogenic Fluid Management / two-stage liquid-hydrogen zero-boiloff testing (2025). https://www.nasa.gov/directorates/stmd/tech-demo-missions-program/cryogenic-fluid-management-cfm/stay-cool-nasa-tests-innovative-technique-for-super-cold-fuel-storage/
- NASA, Zero-Boil-Off Tank experiments: long-duration cryogenic storage/transfer physics and technology gap. https://science.nasa.gov/science-research/science-enabling-technology/zero-boil-off-tank-experiments-to-enable-long-duration-space-exploration/
- NASA NTRS, Considerations for Radiator Design in Multi-Megawatt Nuclear Electric Propulsion Applications. https://ntrs.nasa.gov/citations/20220019167
- NASA NTRS, carbon-carbon composite prototype heat-pipe radiator, derived ~1.45 kg/m^2 element-level specific mass. https://ntrs.nasa.gov/citations/20020082957
- NASA, 2026 Small Spacecraft In-Space Propulsion state of art. https://www.nasa.gov/smallsat-institute/sst-soa/in-space_propulsion/
- National High Magnetic Field Laboratory sources are retained in the F1 evidence card.
