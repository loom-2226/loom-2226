# Wayfarer E1 Primary Propulsion — Torch and Metric-Drive Working Specification

**Status:** WORKING ENGINEERING INTERFACE — ACCUMULATING / NOT CANON  
**Purpose:** Single human-readable working specification for the Wayfarer primary propulsion systems: (1) the remass-consuming axial fusion torch and magnetic nozzle, and (2) the remass-independent metric-drive / metric-effect propulsion lane sometimes informally called the "EM drive" in project discussion. This document is intended to grow as engineering increments earn additional requirements.  
**Authority boundary:** This document consolidates recovered authority, derived engineering requirements, research-supported candidate directions, and explicit open items. It MUST NOT silently promote a candidate, external research analogue, archive value, or numerical sensitivity into canon or hardware certification. Campaign mutation: **ZERO**. LLM calculation authority: **ZERO**.

## 1. Interpretation and authority classes

Every entry belongs to one of these classes:

1. **RECOVERED AUTHORITY** — already governed/requalified Wayfarer vehicle authority.
2. **DERIVED ENGINEERING REQUIREMENT** — follows from governed vehicle state and explicit equations/models.
3. **CANDIDATE** — a packaging, architecture, or technology direction under engineering review.
4. **OPEN** — unresolved and not available for hidden assumptions.
5. **CERTIFIED/FROZEN** — only where an explicit governed artifact has actually earned that status.
6. **EXTERNAL RESEARCH SYNTHESIS** — real scientific/engineering provenance used to constrain or motivate a trade; never canon by citation alone.

Hard firewalls:

- direct kinetic jet power **is not** onboard electrical load;
- direct kinetic jet power **is not** automatically vehicle waste heat;
- successful numerical closure **is not** physical realizability;
- a research analogue **is not** a 2226 component certification;
- an archive value **is not** current authority;
- the remass-consuming torch and remass-independent metric-drive lane are separate propulsion mechanisms and MUST NOT borrow performance assumptions from one another without an explicit governed interface.

## 2. Vehicle propulsion topology

| System | Current role | Remass | Current authority state |
|---|---|---:|---|
| Primary fusion torch / magnetic nozzle | High-thrust conventional momentum-exchange propulsion | **YES** | Vehicle topology recovered; reactor/nozzle hardware open |
| Metric-drive / metric-effect propulsion | Remass-independent propulsion lane | **NO normal remass consumption by definition of this lane** | Separate governed physics/engineering lane; detailed specification to be populated only from its earned authority |
| RCS | Local translation/attitude control | Hardware working fluid OPEN | Vehicle architecture frozen separately; see RCS interface |

Torch operation and high-metric thermal/field operation are currently **mutually exclusive** at the vehicle interface. This document records that interface; it does not infer the microscopic reason.

## 3. Fusion-torch vehicle-level specification

### 3.1 Recovered vehicle interfaces

| Parameter | Current value / specification | Class / interpretation |
|---|---:|---|
| Primary torch count | **1** | RECOVERED AUTHORITY |
| Architecture | `AXIAL_FUSION_TORCH_WITH_MAGNETIC_NOZZLE` | RECOVERED AUTHORITY |
| Reference wet mass | **1,158.5 t** | RECOVERED AUTHORITY |
| Dry mass excluding working fluid/water | **858.5 t** | RECOVERED AUTHORITY |
| Working fluid / water inventory | **300.0 t** | RECOVERED AUTHORITY |
| Normal remass allowance | **250.0 t** | RECOVERED AUTHORITY |
| Protected water reserve | **50.0 t** | RECOVERED AUTHORITY; not normal torch remass |
| Post-normal-remass reference mass | **908.5 t** | RECOVERED AUTHORITY |
| Torch / high-metric simultaneous operation | **PROHIBITED** | RECOVERED vehicle interface |

### 3.2 Working performance cards

These cards are source-recovered **working engineering inputs**, not universal physical constants and not by themselves reactor certification.

| Mode | Acceleration | Exhaust velocity | Initial thrust @ 1,158.5 t | Initial direct kinetic jet power | Full 250 t normal-remass burn time | Ideal constant-a/constant-ve Δv |
|---|---:|---:|---:|---:|---:|---:|
| ECON | 0.30 g | 3,000 km/s | 3.4083 MN | 5.11245 TW | 4,131.32 min | 729.259 km/s |
| CRUISE | 1.00 g | 2,000 km/s | 11.3610 MN | 11.3610 TW | 826.264 min | 486.173 km/s |
| EXPEDITE | 2.00 g | 1,000 km/s | 22.7220 MN | 11.3610 TW | 206.566 min | 243.086 km/s |
| FAST | 3.00 g | 700 km/s | 34.0830 MN | 11.9291 TW | 96.3975 min | 170.161 km/s |
| HARD | 5.00 g | 450 km/s | 56.8050 MN | 12.7811 TW | 37.1819 min | 109.389 km/s |
| LIMIT | 7.50 g | 300 km/s | 85.2075 MN | 12.7811 TW | 16.5253 min | 72.9259 km/s |

Derived model used for this envelope:

- `F = m a`
- `mdot = F / ve`
- `Pjet = 0.5 F ve = 0.5 mdot ve^2`
- for constant acceleration and constant exhaust velocity while thrust tracks instantaneous mass: `dm/dt = -m a/ve`
- `delta-v = ve ln(m0/m1)`

The normal-remass integration uses `m0 = 1,158.5 t` and `m1 = 908.5 t`, consuming **250 t normal remass and zero protected-water reserve**.

## 4. Current torch physical architecture direction

### 4.1 Candidate packaging envelope

The following is **NON-GOVERNING CANDIDATE** packaging and may change as physical design closes:

| Region | Candidate envelope |
|---|---|
| Directional shadow shield / isolation | x ≈ 38–43 m; working diameter ≈ 5.5 m |
| Reactor / torch machinery | x ≈ 43–50 m; transverse diameter ≈ 4.25 m |
| Annular thrust-frame convergence | x ≈ 48–50 m |
| Magnetic nozzle / aft torch structure | x ≈ 50–57 m; aperture/support diameter ≈ 6.0 m |

Candidate structural topology: four principal axial longerons converge into an aft thrust frame serving one axial nozzle. This is not yet a detailed structural design.

### 4.2 Reactor/nozzle technology-family trade

Current research direction only:

`D_HE3_OR_RELATED_LOW_NEUTRON_HIGH_BETA_FRC_CLASS_WITH_SEPARATE_REMASS_AUGMENTATION`

**Disposition:** `RESEARCH_DIRECTION_ONLY_NOT_REACTOR_OR_FUEL_CERTIFICATION`

The preferred direction is a linear/high-beta Field-Reversed-Configuration-class fusion source using a low-neutron fuel strategy where practical, with charged fusion-product energy coupled into a separately managed remass stream and exhausted through a magnetic nozzle. The attraction is architectural compatibility with the governed axial torch, direct use of charged-particle energy, variable remass augmentation, and a real research lineage. It does **not** establish that D–3He, an FRC, or any particular nozzle can satisfy Wayfarer scale.

Technology families retained in the trade:

- D–3He FRC / direct-fusion magnetic-nozzle class — leading research analogue, not certified;
- tritium-suppressed D–D FRC class — secondary analogue; neutron/secondary-burn partition open;
- D–T direct-fusion class — neutron/thermal partition is a major hold;
- p–11B direct-fusion class — reactivity/bremsstrahlung/realizability hold;
- pulsed magnetized-target / propellant-liner fusion — useful research reference but requires explicit architecture-change review relative to the current steady axial-torch direction.

Hard trade rule:

> **No family survives by assuming the required deposition ppm or magnetic-nozzle efficiency. Both must be derived or bounded from a physical partition model.**

## 5. Energy, radiation, thermal and shielding interface

The next physical model MUST account separately for:

- primary charged fusion products;
- primary neutrons;
- side-reaction neutrons;
- bremsstrahlung and other prompt photons;
- charged-particle escape/leakage;
- remass coupling fraction;
- directed exhaust fraction;
- magnet/nozzle interception;
- shield absorption and secondary heating;
- activation/decay heat;
- operating-mode dependence.

The current four-radiator vehicle topology and 900 K high-drive reject interface are current authority, but existing metric-drive equivalent radiator areas MUST NOT be repurposed as a torch thermal solution without a governed torch deposition/transient model.

Historical torch deposition figures and historical thermal-buffer/radiator figures may be used only as explicitly labeled **ARCHIVE / NON-GOVERNING SENSITIVITY PROVENANCE** until re-earned.

## 6. Thrust-frame requirement interface

Known quasi-static axial thrust is derived by operating card. At the current wet reference mass, LIMIT provides the largest known initial axial load: **85.2075 MN**.

The eventual four-longeron-to-aft-frame structural design must close:

- LIMIT axial thrust;
- structural design factor — OPEN;
- dynamic amplification — OPEN;
- nozzle side load — OPEN;
- fatigue spectrum / duty history — OPEN;
- local stress, attachment and reinforcement — OPEN;
- thermal and radiation effects on structural life — OPEN.

No structural design factor or local reinforcement value may be invented merely to release installation.

## 7. Physical-realizability kill criteria

A torch technology family cannot advance to component architecture freeze if it cannot demonstrate or credibly bound all applicable items below:

1. required kinetic exhaust power without unbounded or unmodeled source/input power;
2. required thrust and **300–3,000 km/s** exhaust-velocity range within the governed remass envelope;
3. neutron, photon and intercepted-particle deposition;
4. remass entrainment/heating and directed-exhaust energy partition;
5. magnetic-nozzle expansion, detachment and efficiency;
6. candidate packaging or an explicit governed repackaging review;
7. magnet, shield, thermal, structural and lifetime closure;
8. physical plume and external-hardware clearance.

## 8. RCS / torch integration holds

The RCS vehicle architecture remains frozen separately. Torch work carries these five RCS integration holds until physical closure:

1. `PHYSICAL_PLUME_MODEL_AND_CLEARANCE_SWEEP`
2. `WORKING_FLUID_CYCLE_EXHAUST_VELOCITY_AND_THERMAL_LOAD`
3. `MIB_VALVE_RESPONSE_DUTY_TOTAL_IMPULSE_AND_CYCLE_LIFE`
4. `VECTORING_DYNAMIC_RESPONSE_AND_LIFE`
5. `MOUNT_LOAD_PATH_LOCAL_STRUCTURE_AND_REINFORCEMENT`

Torch engineering must not reopen the RCS vehicle architecture solely because these component-level interfaces remain open.

## 9. 2026 research provenance — fusion propulsion lineage

**Classification: EXTERNAL RESEARCH SYNTHESIS — NOT CANON / NOT QUALIFICATION.**

This section records why the current family trade is scientifically motivated rather than invented. Citations establish research lineage only; they do not certify Wayfarer hardware.

### 9.1 Princeton PFRC / Direct Fusion Drive lineage

- Princeton Plasma Physics Laboratory continues to describe the **Princeton Field-Reversed Configuration (PFRC)** as a fusion-reactor research concept using radio-frequency waves/current drive and magnetic mirrors. The experimental program studies energetic electrons, magnetic-field shape and plasma behavior.
- Princeton Direct Fusion Drive mission literature describes a **linear FRC reactor**, D–3He fuel strategy, fusion-product energy transfer to added propellant/remass, and magnetic-nozzle exhaust. A published human-Mars study described an approximately **2 m diameter × 10 m long** PFRC-R concept and multi-engine MW-class mission architecture. These are useful topology/packaging analogues, not evidence for Wayfarer's multi-terawatt scale.
- PPPL intellectual-property descriptions also retain D–3He high-beta FRC reactor and steady fueling concepts as active research/invention lineage.

Key sources:

- Princeton Plasma Physics Laboratory, *Princeton Field-Reversed Configuration (PFRC)*: https://www.pppl.gov/Princeton-Field-Reversed-Configuration
- Princeton/PPPL, *Direct Fusion Drive for a Human Mars Orbital Mission* (PPPL-5064): https://bp-pub.pppl.gov/pub_report/2014/PPPL-5064.pdf
- PPPL, *M-825 — A Small, Clean, Stable Fusion Power Plant*: https://www.pppl.gov/m-825
- PPPL, *M-863 — Fueling method for small, steady-state, aneutronic FRC fusion reactors*: https://www.pppl.gov/m-863

### 9.2 NASA fusion-driven rocket / direct propellant-energy conversion lineage

NASA NIAC work by John Slough/MSNW studied a **Fusion Driven Rocket** in which fusion energy is deposited directly into propellant rather than first converted into electricity. The concept uses magnetized-target/FRC-class fusion, propellant/liner material that absorbs fusion energy, and expansion of the resulting ionized propellant through a magnetically insulated nozzle. NASA records describe exhaust velocity above 30 km/s for that concept and identify driver efficiency and stand-off/protection from fusion energy as central problems.

This is especially relevant to Wayfarer's requirement for a separate remass-energy-coupling path, but the specific liner architecture is not the current Wayfarer baseline.

Key sources:

- NASA, *Nuclear Propulsion Through Direct Conversion of Fusion Energy*: https://www.nasa.gov/general/nuclear-propulsion-through-direct-conversion-of-fusion-energy/
- NASA, *The Fusion Driven Rocket: Nuclear Propulsion through Direct Conversion of Fusion Energy*: https://www.nasa.gov/general/the-fusion-driven-rocket-nuclear-propulsion-through-direct-conversion-of-fusion-energy/
- NASA NTRS, Slough et al., *Nuclear Propulsion through Direct Conversion of Fusion Energy: The Fusion Driven Rocket*, Document 20160010608: https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20160010608.pdf
- NASA TechPort, *The Fusion Driven Rocket*, project 11570 (listed as completed; record updated 2025-12-18): https://techport.nasa.gov/projects/11570

### 9.3 NASA magnetic-nozzle and space-fusion lineage

NASA has separately studied magnetic-nozzle expansion for fusion propulsion, including experiments/simulations intended to reproduce fusion-grade edge plasma expanding through a diverging magnetic field. Older NASA space-fusion studies explicitly examined D–3He power balance, neutron shielding, direct conversion of plasma enthalpy to thrust through propellant addition, and magnetic nozzles. Historical studies also identified the FRC as attractive for space propulsion because of high beta, compact-toroid properties and linear external-field topology conducive to direct thrust.

Key sources:

- NASA NTRS, *Magnetic-Nozzle Studies for Fusion Propulsion Applications: Gigawatt Plasma Source Operation and Magnetic Nozzle Analysis*, Document 20040008875: https://ntrs.nasa.gov/citations/20040008875
- NASA NTRS, *The NASA-Lewis program on fusion energy for space power and propulsion, 1958–1978*, Document 19910012835: https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19910012835.pdf
- NASA NTRS, *Fuel and Design Options for Space Fusion Reactors*, Document 19920002565: https://ntrs.nasa.gov/api/citations/19920002565/downloads/19920002565.pdf
- NASA NTRS, *High-Energy Space Propulsion Based on Magnetized Target Fusion*, Document 19990080042: https://ntrs.nasa.gov/citations/19990080042

### 9.4 Provenance conclusion

The Wayfarer candidate does **not** claim that a 2026 NASA/PPPL engine can be scaled directly into the ship. The defensible continuity is narrower:

`high-beta/FRC-class fusion` → `charged-product/direct-energy use where possible` → `propellant/remass augmentation` → `magnetic-nozzle expansion`.

Wayfarer's **5–13 TW direct kinetic exhaust power**, **3–85 MN thrust**, **300–3,000 km/s exhaust velocity**, packaging, radiation deposition, thermal rejection and lifetime remain a much more demanding 2226 engineering problem. Those gaps are explicit kill gates, not assumed progress.

## 10. Metric-drive / remass-independent propulsion working section

**Status:** RESERVED WORKING INTERFACE — DO NOT BACKFILL FROM TORCH ASSUMPTIONS.

This section will accumulate the Wayfarer remass-independent propulsion specification as its own governed engineering/research lane is recovered and advanced. The informal project shorthand "EM drive" is retained here only to identify the lane requested for this working document; it MUST NOT be conflated with the historical 21st-century RF-cavity `EMDrive` concept unless an explicit research artifact establishes such a relationship.

Current safe statements:

- this lane is intended to provide propulsion **without consuming normal reaction mass**;
- it is distinct from the fusion torch;
- torch/high-metric thermal/field operation is currently mutually exclusive;
- its physical mechanism, field architecture, energy source, momentum bookkeeping, thrust/power relationship, thermal deposition, operating cards, component geometry and physical-realizability gates MUST be imported from or earned by its own governed RF/metric-drive work rather than invented here.

### 10.1 Metric-drive specification fields to populate

| Field | Current state |
|---|---|
| Governing physical mechanism | OPEN / recover from governed RF authority |
| Remass consumption | NONE by propulsion-lane definition; physical momentum bookkeeping still requires governed explanation |
| Operating cards | OPEN / recover |
| Thrust or acceleration envelope | OPEN / recover |
| Input/source power | OPEN / recover |
| Waste-heat/deposition model | OPEN / recover |
| Field/topology hardware | OPEN / recover |
| Packaging envelope | OPEN / recover |
| Interaction with torch | MUTUALLY EXCLUSIVE at current vehicle interface |
| Interaction with RCS | OPEN |
| Failure/safe-state behavior | OPEN |
| Physical-realizability criteria | OPEN / must follow RF authority |

## 11. Current torch open register

The following remain explicitly OPEN unless a later governed increment updates this document:

- reactor cycle / exact fusion architecture;
- exact fuel cycle;
- fusion gain and specific power;
- reaction-product energy partition;
- side-reaction rates and spectra;
- remass identity, injection, entrainment and heating implementation;
- magnetic-nozzle efficiency and plasma detachment;
- neutron/photon/secondary transport;
- magnetic-coil geometry, stress, cooling and lifetime;
- shadow-shield material stack and streaming paths;
- thermal plumbing and transient heat rejection;
- physical plume envelope and external clearance;
- detailed thrust-frame structure, factors, dynamic/side/fatigue/local stresses;
- physical radiator geometry and torch-clearance closure;
- component installation certification.

## 12. Next governed increment

`BUILD_TORCH_DEPOSITION_PARTITION_MODEL_AND_FAMILY_KILL_CRITERIA`

That increment should bound or expose the energy channels rather than inventing convenient efficiencies. It should distinguish fusion/source power, kinetic jet power and vehicle-deposited heat; enforce partition closure for evaluated candidates; and retain historical ppm values only as non-governing sensitivity provenance.

---

**Maintenance rule:** Update this document as each propulsion engineering increment earns new authority. Preserve superseded values with provenance where useful, but never allow the working specification itself to become an independent source of authority over the governed artifacts it summarizes.
