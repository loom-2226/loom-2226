# Wayfarer 2226 Drivetrain — Literature Review v0.1

**Status:** EXTERNAL LITERATURE SYNTHESIS / PRE-PROJECTION  
**Purpose:** establish what the existing literature already treats as the relevant technology axes before LOOM chooses any 2226 extrapolation variables or values.  
**Authority:** RESEARCH SYNTHESIS ONLY — NO 2226 NUMERICAL AUTHORITY  
**Cutoff:** public literature reviewed through 2026-09-16

## BLUF

LOOM should not invent a bespoke taxonomy for future drivetrain technology. Existing spacecraft, nuclear-electric, fusion, cryogenic, thermal, power-electronics, energy-storage, magnet, and propulsion literature already converges on a compact set of coupled engineering bottlenecks.

The literature strongly supports treating the Wayfarer drivetrain as a **system-of-systems trade** among field generation, power conversion/distribution, energy buffering, heat rejection, structures/materials, cryogenic/fluid management, propulsion lifetime/performance, and radiation/extreme-environment qualification. It does **not** support treating any one record metric — tesla, Wh/kg, conversion efficiency, radiator kg/m2, material strength, or specific impulse — as an independent future multiplier.

For E2, metric, and LOOM-specific hardware, literature supports extrapolating ordinary enabling technologies only. It does not provide authority for an unknown momentum sink, unknown metric constitutive law, Mc-299m behavior, topology manipulation, or any other unearned mechanism.

## 1. Forecasting methodology literature

Nagy, Farmer, Bui, and Trancik (2013) tested six proposed technological-progress laws against 62 technology datasets using hindcasting. Wright-style experience curves performed best in their comparison, with generalized Moore-style time trends close behind; importantly, forecasting error increased with horizon. Their datasets retained a consistent functional unit and generally covered 10–39 years. This is evidence for empirical forecasting discipline, not evidence that a fitted exponential may be projected safely for two centuries.

NASA's technology-roadmapping practice similarly begins from state of the art and mission capability needs, then identifies enabling technologies and technical challenges. The current NASA Technology Taxonomy deliberately groups like technologies by technical discipline rather than treating every mission as having its own independent technology future.

**Implication for LOOM:** use empirical trend fitting only where like-for-like data genuinely support it. Otherwise use bounded scenarios tied to demonstrated systems, physical constraints, and consumer requirements. Shared technology producers should be reused across consumers.

## 2. Spacecraft system baseline literature

NASA's 2026 State-of-the-Art Small Spacecraft Technology report provides a useful public cross-subsystem survey through April 2026. Its updated chapters cover power, in-space propulsion, structures/materials/mechanisms, thermal control, avionics, and related integration. NASA explicitly describes the report as a survey of public literature rather than an original source and cautions that advertised performance and TRL can be application/environment dependent.

**Implication for LOOM:** retain source hierarchy. NASA's survey is excellent for taxonomy and candidate metrics; primary technical reports, peer-reviewed work, test reports, and demonstrated hardware should anchor quantitative values.

## 3. F1 — fields, superconductors, and magnets

The literature shows immediately why `tesla vs year` is insufficient.

National MagLab's 32 T all-superconducting research magnet uses HTS and exceeded a prior superconducting record around 24 T. The same facility currently reports the 32 T system undergoing HTS-coil repairs, which is direct evidence that achieved field and maintainable lifetime are different metrics.

MIT/CFS demonstrated a full-scale, large-bore REBCO fusion magnet at 20 T, using 267 km of HTS tape. ITER provides still larger system anchors: its toroidal-field coils are designed for 11.8 T, 41 GJ total magnetic energy, and 330 t per coil; its central solenoid reaches 13 T and, with structure/instrumentation, about 1,000 t and 6.4 GJ stored energy.

These systems differ radically in bore, geometry, field duty, mass, stored energy, conductor, structural support, protection, and mission environment.

**Literature-supported axes:** useful field and bore; conductor critical surface `Jc(B,T,strain)`; engineering current density; conductor/reinforcement fraction; structural stress and strain; installed specific mass; stored energy; quench/protection; cryogenic burden; duty/lifetime; radiation/fluence tolerance.

**Do not invent:** one universal field trend or a field value derived from structural strength alone.

## 4. F2 — power generation, conversion, PMAD, and power electronics

NASA's MW-class Nuclear Electric Propulsion work is particularly useful because it treats the drivetrain as an integrated powertrain. NASA identifies five critical technology elements: reactor, power conversion, power management/distribution, electric propulsion, and primary heat rejection. This is close to the decomposition LOOM needs.

Closed-Brayton studies show that conversion efficiency and radiator area are coupled to turbine/compressor temperatures and heat-exchanger performance. A NASA MW-class model reported minimum-radiator-area solutions around 20% thermal efficiency and radiator areas as low as roughly 650 m2/MWe for the studied assumptions; this is a design-study result, not a universal limit. Near-term lunar fission studies likewise show strong mass/radiator/power coupling rather than an independent conversion-efficiency knob.

NASA's SiC work shows the established direction for power electronics: higher temperature, radiation hardness, high voltage/power capability, faster switching, and reduced converter passive-component mass. NASA reports some demonstrated SiC converter comparisons with more than fivefold reductions in volume/weight relative to corresponding silicon implementations, while also treating reliability and radiation as explicit space concerns.

**Literature-supported axes:** source-independent thermal-to-electric conversion efficiency; conversion specific mass/power; PMAD specific power; voltage/current envelope; switching/conversion loss; operating temperature; radiation tolerance; heat-exchanger/alternator burden; lifetime/reliability.

**Do not invent:** near-100% conversion, zero-mass PMAD, or source power density independent of reactor/fusion physics.

## 5. F3 — energy and pulse-power buffering

NASA's 2026 power survey treats storage as a Ragone trade: energy density and power density are different objectives. Modern spacecraft use Li-ion/Li-polymer broadly; the report cites commercial Li-ion energy cells around 150–270 Wh/kg and advanced demonstrations approaching roughly 450–500 Wh/kg. It also describes supercapacitors as much lower energy density but much higher power density and cycle life, with current/horizon work in solid-state batteries, Li-metal/Li-S, nanomaterials, hybrid battery-capacitor systems, and supercapacitors.

NASA literature also contains spacecraft flywheel and superconducting magnetic energy-storage studies. These establish that mechanical and magnetic buffering are legitimate technology families, but both carry system-specific structural, bearing/control, magnetic-stress, cryogenic, or integration burdens. Spacecraft thermal-storage literature uses phase-change materials to absorb transient heat rather than oversizing radiators for every peak.

**Literature-supported axes:** usable specific energy; specific power; round-trip efficiency; cycle life; discharge duration; thermal operating range; self-discharge; structural/containment burden; radiation tolerance; thermal-buffer specific energy/power. Keep chemical, electrostatic, mechanical, magnetic, and thermal storage classes separate.

**Do not invent:** a single future `battery multiplier` applied to all transient power problems.

## 6. F4 — structures, extreme materials, shielding, and radiation lifetime

NASA's spacecraft structures/materials literature treats material choice together with structural architecture, mechanisms, environmental exposure, qualification, and manufacturability. Fusion literature makes the extreme-environment coupling even clearer.

The 2026 U.S. Fusion Science & Technology Roadmap identifies six challenge areas including structural materials, plasma-facing components, confinement systems, fuel cycle, blankets, and plant engineering/integration. It states that fusion-specific neutron irradiation, heat/particle exhaust, stress, and chemical reactivity can materially alter components over their operational life and identifies fusion-relevant irradiation performance/lifetime as a major knowledge gap.

A 2026 review of plasma-facing materials describes the combined problem of high heat flux, 14.1 MeV neutron irradiation, erosion, thermal conductivity degradation, tritium retention, thermomechanical properties, and radiation resistance; it emphasizes that no single material presently satisfies the full idealized requirement set. UKAEA's Fusion Materials Roadmap likewise separates magnets/shielding, high-temperature materials, radiation-hardened materials, tritium-related materials, and modeling/qualification.

**Literature-supported axes:** temperature-dependent specific strength/stiffness; creep/fatigue; fracture/toughness; radiation/fluence degradation; thermal conductivity after irradiation; erosion/sputtering; chemical compatibility; shielding attenuation per installed mass; lifetime under combined loads.

**Do not invent:** one `future strength` number and apply it unchanged to room-temperature structure, fusion-facing hardware, cryogenic magnet support, and radiation shielding.

## 7. F5 — thermal transport, radiators, and heat storage

The literature is unequivocal that high-power spacecraft are often radiator-constrained. NASA's multi-megawatt NEP work identifies main-radiator specific mass as the largest single power-system mass element in studied concepts and shows dependence on loop count, geometry/view factor, heat-pipe temperature limits, and other architecture assumptions.

Closed-Brayton NEP studies show that increasing cycle temperature can both raise conversion efficiency and raise average radiator temperature, reducing required area, but the optimum radiator-area point need not coincide with maximum thermodynamic efficiency. NASA spacecraft thermal-control literature spans passive coatings/MLI, heat pipes, pumped loops, deployable radiators, phase-change thermal storage, and active thermal systems.

The immutable radiative relation remains Stefan-Boltzmann; technology changes allowable temperature, emissivity, areal/system mass, transport losses, deployment architecture, and lifetime — not the fourth-power law itself.

**Literature-supported axes:** reject temperature; effective emissivity/view factor; heat-transport temperature and flux; radiator areal density and system specific mass; loop/pump burden; heat-pipe limits; deployment/stowage burden; survivability; thermal-buffer capacity; lifetime.

**Do not invent:** radiator performance as an arbitrary multiple independent of temperature and geometry.

## 8. F6 — fluids, propellants, cryogenics, RCS, and conventional propulsion

NASA's Cryogenic Fluid Management roadmaps identify long-duration storage, pressure control, transfer/delivery, gauging/acquisition, and heat interception/removal as separate functions. NASA's current zero-boiloff work uses active cooling; `zero boiloff` therefore does not mean zero refrigeration power or perfect insulation.

NASA's 2026 propulsion survey separates chemical, electric, and propellantless/environment-coupled propulsion and treats technology maturity explicitly. Chemical propulsion remains the high-thrust/impulsive family; electric propulsion trades low thrust for high total impulse and long operating duration. A current NASA Transit Habitat RCS concept still studies a pressure-fed hypergolic bipropellant architecture because replenishment and extensive-life requirements drive component/system choices.

For environment-coupled propulsion, NASA explicitly describes solar sails, electrodynamic tethers, electric sails/plasma brakes, and aerodynamic drag devices as exchanging momentum with photons, magnetic/plasma environments, solar wind, or atmosphere. HERTS/electric-sail work explicitly identifies solar-wind protons as the momentum partner.

**Literature-supported axes:** storage duration/boiloff/refrigeration burden; tankage fraction; pressure and feed-system mass; pump/valve/injector response and cycle life; propellant/working-fluid compatibility; thruster specific impulse/exhaust velocity; thrust-to-power; total impulse/lifetime; minimum impulse bit/response where applicable; thermal load; plume/environment interaction; replenishment/transfer.

**Do not invent:** perfect cryogenic storage, zero-mass tankage/feed systems, or reactionless thrust.

## 9. F7 — fusion and torch enabling engineering

The fusion literature already supplies the correct decomposition for LOOM: confinement systems, structural materials, plasma-facing components/exhaust, fuel cycle/tritium, blankets/shielding, and plant engineering/integration. This is much safer than inventing a single `fusion technology level`.

The DOE roadmap and fusion-materials literature emphasize that material lifetime, neutron exposure, plasma exhaust, fuel cycle, and integrated plant engineering remain independent challenges even if confinement physics advances. ITER and HTS fusion-magnet programs show the coupling between field, structure, cryogenics, conductor, stored energy, and protection.

**Literature-supported axes for LOOM projection:** consume F1 field/magnet envelope; consume F2 power-conversion/PMAD envelope; consume F4 extreme-material/radiation envelope; consume F5 thermal envelope; consume F6 fuel/fluid handling envelope. Add only fusion-specific engineering metrics supported by literature, such as plasma-facing heat-flux/lifetime, neutron-material lifetime, tritium/fuel-cycle burden, blanket/shield burden, and balance-of-plant mass.

**Do not invent:** fusion gain, source directed fraction, source specific power, nozzle coupling, or reactor realizability merely by extrapolating materials. Those remain mechanism/component holds until independently earned.

## 10. F8 — E2, metric, and LOOM enabling technology

Existing propulsion literature provides a useful conservation firewall. NASA calls several systems `propellantless`, but the demonstrated/serious concepts still identify an external momentum partner: photons for solar sails; electromagnetic interaction with planetary fields/plasma for tethers; solar-wind ions for electric sails; atmosphere for drag devices. The absence of onboard propellant is not the absence of momentum exchange.

Therefore LOOM can legitimately project the mundane enablers consumed by E2/metric/LOOM systems — magnets, power conversion, pulse power, structures, thermal management, cryogenics, precision control/metrology, radiation tolerance — using F1–F6. It cannot project the unknown mechanism itself by a generic technology-growth factor.

**Do not invent:** undefined vacuum momentum sinks, internally cycled reactionless thrust, free metric velocity reset, Mc-299m constitutive properties, topology manipulation capability, or a field coupling law not earned by the separate physics/research program.

## 11. Cross-literature convergence: the minimal drivetrain frontier set

The review supports the register's broad structure, with one refinement: **radiation/extreme-environment lifetime is not a side metric; it is a cross-cutting derating axis.**

The minimum producer set is:

- F1 fields/magnets;
- F2 power generation/conversion/PMAD;
- F3 electrical/pulse/thermal buffering;
- F4 structures/extreme materials/shielding/radiation lifetime;
- F5 thermal transport/rejection;
- F6 fluids/propellants/cryo/RCS/conventional propulsion.

F7 fusion/torch and F8 E2/metric/LOOM should primarily be **consumer/integration frontiers**, not independent sources of technological multipliers.

This matches the system decomposition repeatedly seen in NASA NEP and DOE fusion work: power source, conversion, distribution, propulsion/confinement, heat rejection, materials, fuel/fluid systems, and integrated lifetime/qualification.

## 12. Projection whitelist produced by the literature review

The next phase may select a bounded subset of the following quantities, staying within the register's total parameter budget:

**F1:** field-at-bore envelope; engineering current density; magnet installed specific mass; stored-energy/protection envelope; cryogenic burden; radiation/lifetime derating.

**F2:** conversion efficiency; conversion specific power/mass; PMAD specific power; allowable operating temperature; distribution/conversion loss; radiation/lifetime derating.

**F3:** electrical specific energy; electrical specific power; pulse-power specific power/energy; cycle life; thermal-buffer specific energy/power; round-trip efficiency.

**F4:** temperature-specific structural performance; creep/fatigue/lifetime; radiation/fluence lifetime; erosion/plasma-facing lifetime; shielding mass effectiveness; thermal-conductivity retention.

**F5:** reject-temperature envelope; effective emissivity; radiator areal/system specific mass; transport heat flux; pumping/loop burden; thermal-storage capability.

**F6:** cryogenic storage/refrigeration burden; tankage/feed fraction; valve/pump/injector response/life; conventional RCS exhaust-velocity/Isp envelope; thrust-to-power where relevant; total-impulse/lifetime envelope.

**F7/F8:** no independent generic future multiplier. Consume F1–F6 plus separately earned mechanism-specific physics.

## 13. What this review changes in the work plan

1. **Do not deepen F1 before the other producer cards exist.** The literature says the same coupled constraints recur across the drivetrain.
2. **Do not search for one historical trend per frontier by default.** Many relevant metrics lack long, like-for-like series; bounded scenario construction will often be the honest method.
3. **Use demonstrated systems as anchors and roadmaps/reviews to identify missing constraints.**
4. **Project system metrics, not record material properties.**
5. **Carry radiation/lifetime explicitly across F1, F2, F4, F5, F6, and F7 consumers.**
6. **Keep F7/F8 as integration consumers.** This prevents duplicate progress multipliers and mechanism laundering.
7. **Stop literature collection when every whitelisted metric has at least one credible 2026 anchor and its major known physical/system deratings are identified.** The goal is not an exhaustive bibliography.

## References

1. Nagy, B.; Farmer, J. D.; Bui, Q. M.; Trancik, J. E. (2013), *Statistical Basis for Predicting Technological Progress*, PLOS ONE 8(2): e52669. https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0052669
2. NASA, *2024 NASA Technology Taxonomy*. https://www.nasa.gov/otps/2024-nasa-technology-taxonomy/
3. NASA, *2026 State-of-the-Art Small Spacecraft Technology*. https://www.nasa.gov/smallsat-institute/sst-soa/
4. NASA, *2026 State-of-the-Art — Power*. https://www.nasa.gov/smallsat-institute/sst-soa/power-subsystems/
5. NASA, *2026 State-of-the-Art — In-Space Propulsion*. https://www.nasa.gov/smallsat-institute/sst-soa/in-space_propulsion/
6. NASA, *2026 State-of-the-Art — Structures, Materials, and Mechanisms*. https://www.nasa.gov/smallsat-institute/sst-soa/structures-materials-and-mechanisms/
7. NASA, *2026 State-of-the-Art — Thermal Control*. https://www.nasa.gov/smallsat-institute/sst-soa/thermal-control/
8. National High Magnetic Field Laboratory, *32 Tesla Superconducting Magnet*. https://nationalmaglab.org/user-facilities/dc-field/magnets-instruments/superconducting-magnets/scm-32-t/
9. MIT News, *MIT-designed project achieves major advance toward fusion energy* (20 T full-scale HTS fusion magnet). https://news.mit.edu/2021/MIT-CFS-major-advance-toward-fusion-energy-0908
10. ITER, *Superconducting Magnets*. https://www.iter.org/machine/magnets
11. ITER, *Standing tall* (2026 central-solenoid completion milestone). https://www.iter.org/node/20687/standing-tall
12. NASA NTRS, *A Technology Maturation Plan for the Development of Nuclear Electric Propulsion*. https://ntrs.nasa.gov/citations/20220017771
13. NASA NTRS, *Brayton Cycle Power Conversion Model for MW-Class Nuclear Electric Propulsion Mars Missions*. https://ntrs.nasa.gov/citations/20220002047
14. NASA Glenn, *Benefits and Collaborations — Silicon Carbide Electronics and Sensors*. https://www.nasa.gov/glenn/research/silicon-carbide-electronics-sensors/benefits-collaborations/
15. NASA NTRS, *Considerations for Radiator Design in Multi-Megawatt Nuclear Electric Propulsion Applications*. https://ntrs.nasa.gov/citations/20220017479
16. NASA, *Cryogenic Fluid Management*. https://www.nasa.gov/space-technology-mission-directorate/tdm/cryogenic-fluid-management-cfm/
17. NASA, *Zero Boil-Off Tank*. https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/fluid-science/zero-boil-off-tank-zbot/
18. NASA, *Stay Cool: NASA Tests Innovative Technique for Super Cold Fuel Storage*. https://www.nasa.gov/directorates/stmd/tech-demo-missions-program/cryogenic-fluid-management-cfm/stay-cool-nasa-tests-innovative-technique-for-super-cold-fuel-storage/
19. NASA NTRS, *Transit Habitat Government-Reference Conceptual Design Reaction Control System Propulsion Concept Design Data Book*. https://ntrs.nasa.gov/citations/20240015687
20. U.S. Department of Energy, *Fusion Science and Technology Roadmap* (2026 final roadmap and challenge areas). https://www.energy.gov/documents/fusion-science-and-technology-roadmap
21. UKAEA, *UK Fusion Materials Roadmap*. https://www.ukaea.org/about-ukaea/publications/uk-fusion-materials-roadmap/
22. Li, F. et al. (2026), *Plasma-facing materials for fusion energy: Historical review, challenges and future directions*, Extreme Materials 2(3), 100044. https://doi.org/10.1016/j.exm.2026.100044
23. NASA, *Heliopause Electrostatic Rapid Transit System (HERTS)*. https://www.nasa.gov/general/heliopause-electrostatic-rapid-transit-system-herts-2/
24. NASA NTRS, *Electrostatic Solar Sail: A Propellantless Propulsion Concept for an Interstellar Probe Mission*. https://ntrs.nasa.gov/search.jsp?R=20200001008
25. NASA NTRS, *Lunar Superconducting Magnetic Energy Storage*. https://ntrs.nasa.gov/citations/20190001255
26. NASA Science/JPL, *Energy Storage Technologies for Future Planetary Science Missions*. https://science.nasa.gov/resource/energy-storage-technologies-for-future-planetary-science-missions/
27. NASA TFAWS 2026, *Development and Testing of Additively Manufactured Phase Change Material Thermal Storage Units*. https://tfaws.nasa.gov/tfaws-2026/paper-proceedings/
