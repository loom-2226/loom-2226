# LOOM 2226 — Wayfarer Q2 Torch Remass Analysis v0.1

**Status:** ENGINEERING STUDY / NON-CANON  
**Date:** 2026-09-11  
**Parent:** `LOOM_2226_Wayfarer_Flight_System_Qualification_Plan_v0.1.md`  
**Purpose:** Quantify the torch/remass interface question before selecting a normal carried feedstock.

---

## 0. Authority boundary

This study does not alter CANON II. The current governing assumption remains a single axial fusion torch using ordinary momentum exchange, with approximately 300 t working-fluid/water inventory and approximately 250 t normal remass allowance. Feedstock identity remains open for qualification.

The goal is to determine whether the torch should be designed around one chemically specific propellant or around a conditioned-plasma feed interface that supports several qualified species.

---

## 1. Governing torch card used for analysis

Reference wet mass: **1,158.5 t**.

| Mode | Acceleration | Exhaust velocity | Reference thrust | Reference mass flow | Reference remass/hour | Ideal jet power |
|---|---:|---:|---:|---:|---:|---:|
| ECON | 0.30 g | 3,000 km/s | 3.408 MN | 1.136 kg/s | 4.09 t/h | 5.11 TW |
| CRUISE | 1.00 g | 2,000 km/s | 11.361 MN | 5.681 kg/s | 20.45 t/h | 11.36 TW |
| EXPEDITE | 2.00 g | 1,000 km/s | 22.722 MN | 22.722 kg/s | 81.80 t/h | 11.36 TW |
| FAST | 3.00 g | 700 km/s | 34.083 MN | 48.690 kg/s | 175.28 t/h | 11.93 TW |
| HARD | 5.00 g | 450 km/s | 56.805 MN | 126.233 kg/s | 454.44 t/h | 12.78 TW |
| LIMIT | 7.50 g | 300 km/s | 85.208 MN | 284.025 kg/s | 1,022.49 t/h | 12.78 TW |

These values are simple momentum/kinetic-power closure at the stated reference wet mass:

`F = m a`

`mdot = F / ve`

`Pjet = 0.5 mdot ve^2 = 0.5 F ve`

They are engineering checks, not a replacement for the governing machine card.

### Immediate consequence

At the current exhaust velocities, directed exhaust kinetic energy is enormous:

- 300 km/s -> **45 GJ/kg**;
- 450 km/s -> **101.25 GJ/kg**;
- 700 km/s -> **245 GJ/kg**;
- 1,000 km/s -> **500 GJ/kg**;
- 2,000 km/s -> **2.0 TJ/kg**;
- 3,000 km/s -> **4.5 TJ/kg**.

Ordinary molecular dissociation and first-ionization energies are therefore a secondary energy term. This does **not** mean chemistry is irrelevant: feed-system compatibility, plasma composition, radiation, recombination, erosion and contamination can still control whether a species is usable.

---

## 2. Physical interpretation of the torch interface

The current torch should not be modeled as a chemical rocket. The working hypothesis to qualify is:

> The reactor supplies energy; remass is a separately supplied working fluid converted to a sufficiently ionized/dissociated plasma and accelerated through a magnetic nozzle.

Under that architecture the engine-side interface cares primarily about:

1. reliable metering at required mass-flow rate;
2. conversion to an electromagnetically controllable plasma;
3. acceptable charge-state / conductivity behavior;
4. acceptable radiative loss and recombination behavior;
5. acceptable interaction with magnetic-nozzle and first-wall materials;
6. low contamination/deposition burden;
7. storage and transfer practicality;
8. compatibility with the ship's thermal architecture.

Molecular identity should be treated as a qualification variable, not automatically as the propulsion-energy source.

---

## 3. Candidate ranking — preliminary

Ratings below are **engineering dispositions for further qualification**, not canon locks and not full per-mode certification.

| Feed | Preliminary disposition | Principal strengths | Principal penalties | Recommended role |
|---|---|---|---|---|
| **H2O** | LEAD CANDIDATE | Dense, non-cryogenic under ship conditions, easy long-duration storage, shielding/life-support/thermal utility, widespread Solar-System resource | Oxygen-bearing plasma may increase materials/radiative burden; potable reserve must be isolated from propulsion contamination | **PRIMARY candidate** |
| **NH3** | STRONG ALTERNATE | High liquid density relative to H2, manageable refrigeration/pressure, hydrogen-rich, found with outer-system volatiles | Toxic, chemically aggressive, dissociation products complicate materials and life-support interfaces | **ALTERNATE candidate** |
| **CO2** | STRONG ALTERNATE / REGIONAL | Dense storage possible as refrigerated liquid or high-pressure/supercritical fluid; common planetary/volatile resource; no ultra-deep cryogenics | Oxygen/carbon plasma chemistry, high molecular mass, pressure/thermal management, possible carbon/oxide contamination pathways | **ALTERNATE / regional candidate** |
| **N2** | GOOD CLEAN PLASMA FEED, STORAGE-PENALIZED | Chemically comparatively inert, simple elemental plasma, abundant in some environments | Cryogenic storage near 77 K if liquid; dedicated tank conditioning; lower multifunction utility than water | **ALTERNATE / depot feed** |
| **Ar** | EXCELLENT PLASMA FEED, LOGISTICS-PENALIZED | Monatomic/inert, excellent magnetic/electric-plasma compatibility precedent, dense liquid relative to H2 | Cryogenic storage near 87 K, limited bulk abundance compared with water/CO2/N2, low multifunction utility | **SPECIALIZED / depot feed** |
| **O2** | PLAUSIBLE CONTINGENCY | Can be produced from water/oxides; dense liquid; simple elemental feed after dissociation | Strong oxidizer before ionization, cryogenic storage, materials/fire-management burden, oxygen-plasma erosion risk | **CONTINGENCY / regional** |
| **CH4** | DERATED CANDIDATE | Useful volatile, moderate cryogenic burden compared with H2, potentially available in outer system | Carbon deposition/soot chemistry during imperfect conditioning, cryogenic storage, contamination concern | **DERATED / contingency** |
| **CO** | WEAK CANDIDATE | Available as volatile/carbon-oxygen feed in some environments | Toxic, deeply cryogenic, little storage advantage, carbon/oxygen contamination with fewer logistics benefits than CO2 | **CONTINGENCY at best** |
| **H2** | PERFORMANCE-SPECIALIZED, POOR BULK DEFAULT | Lowest particle mass; excellent high-specific-impulse plasma working fluid if the hardware benefits from light ions | ~20 K liquid storage, extremely low volumetric density, boiloff/cryogenic complexity, large tankage | **SPECIALIZED high-Isp feed; not normal bulk remass** |

---

## 4. Why water remains the provisional leader

Water does not win because the torch requires H2O. It wins because the **ship** values H2O.

At Wayfarer scale, a tonne of stored water can simultaneously serve as:

- torch reaction mass;
- radiation shielding mass;
- potable/life-support reserve after protected treatment/segregation;
- thermal-buffer working inventory;
- industrial/process feedstock;
- standardized port commodity.

That multifunctionality is unusually valuable aboard a courier where every tonne of deadweight competes with payload and machinery.

A water-primary architecture should therefore be interpreted as **logistics optimization**, not chemical propulsion dependence.

---

## 5. Why hydrogen should not become the default merely because it is light

At a fixed certified exhaust velocity and thrust, the required mass flow is set by `F/ve`, independent of whether that kilogram is H2, H2O, N2 or Ar. A lighter particle species only helps if the engine's attainable exhaust velocity, nozzle efficiency, plasma losses or reactor coupling materially improve with species.

Hydrogen therefore does **not** automatically reduce tonnes of remass at the existing torch card.

Its storage penalty is severe: long-duration liquid-hydrogen storage requires ~20 K-class cryogenic management and very large tank volume per tonne. NASA continues to treat long-duration LH2 storage/transfer as one of the hardest cryogenic-fluid-management problems. This is useful empirical ancestry but does not itself constrain 2226 technology.

Disposition: retain H2 as a **performance-specialized candidate**, not normal Wayfarer bulk remass.

---

## 6. Proposed torch feed interface classes

Instead of a single propellant specification, qualify three interface classes.

### TF-A — Dense molecular volatile

Candidate feeds: `H2O`, `NH3`, `CO2`.

Design emphasis:

- high-density bulk storage;
- moderate-temperature tankage;
- onboard dissociation/ionization conditioner;
- broad logistics availability.

This should be the primary Wayfarer class.

### TF-B — Cryogenic simple/elemental feed

Candidate feeds: `N2`, `Ar`, `O2`, optionally `H2`.

Design emphasis:

- clean or simple plasma behavior;
- dedicated cryogenic handling;
- depot/special-mission loading;
- performance or regional-availability optimization.

### TF-C — Carbon-bearing contingency feed

Candidate feeds: `CH4`, `CO`, impure CO2-rich process streams if separately qualified.

Design emphasis:

- frontier availability;
- reduced duty cycle;
- aggressive conditioning;
- explicit contamination/maintenance penalties.

No raw-regolith or arbitrary-dirt mode is proposed. The torch receives a **conditioned fluid/plasma precursor**, not mined rubble.

---

## 7. Preliminary per-mode rule

Until plasma/material modeling says otherwise, do **not** assign different nominal exhaust velocities merely because molecular species differs. The current velocity card remains the target interface.

Species qualification should first determine whether each feed can support the target card with acceptable:

- ionization fraction;
- radiative loss;
- magnetic coupling;
- nozzle efficiency;
- chamber/nozzle erosion;
- continuous duty cycle.

Only then apply a mode-specific `CERTIFIED`, `DERATED`, `CONTINGENCY`, or `PROHIBITED` rating.

This prevents a common modeling error: using molecular mass alone to invent a different rocket performance card without a defined plasma/nozzle constitutive model.

---

## 8. Storage implication for the four-tank architecture

Preferred architecture for Q2-E testing:

- four major structural working-fluid tanks remain;
- normal dispatch configuration loads primarily TF-A feed, likely water;
- tanks are **feed-compatible but not necessarily potable-compatible** after propulsion service;
- the protected life-support water reserve is physically isolated behind dedicated cleanliness boundaries;
- one or more tanks may be configured for alternate feed on special missions;
- cryogenic TF-B service requires explicit insulation/refrigeration modules and should not be assumed to be free merely because the relational plant already contains a 20 K cryogenic chain.

The relational plant's precision cryogenic system must not be silently repurposed as a hundreds-of-tonnes propellant refrigerator.

---

## 9. External empirical anchors

These are ancestry/engineering references, not direct proof of the fictional torch architecture.

1. NASA describes electric propulsion as ionizing inert-gas propellants such as xenon and krypton and accelerating them with electric/magnetic or electrostatic fields, demonstrating the general principle that propulsion energy can be externally supplied while propellant acts primarily as accelerated working mass: https://www.nasa.gov/humans-in-space/the-propulsion-were-supplying-its-electrifying/
2. NASA's solar-electric-propulsion overview likewise distinguishes onboard electrical energy from ionized propellant flow and emphasizes high propellant economy: https://www.nasa.gov/space-technology-mission-directorate/tdm/solar-electric-propulsion/
3. NASA cryogenic-fluid-management work identifies hydrogen, methane and oxygen as cryogenic fluids with significant storage/transfer challenges and identifies hydrogen as particularly difficult: https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/fluid-science/zero-boil-off-tank-zbot/
4. NASA's current Integrated Flight Demonstration specifically describes LH2 transfer and long-duration storage as the most challenging cryogenic propellant case: https://techport.nasa.gov/projects/116762

---

## 10. Q2 v0.1 recommendation

### Provisional hierarchy

`PRIMARY CANDIDATE = H2O`

`ALTERNATE CANDIDATES = NH3, CO2, N2, Ar`

`SPECIALIZED = H2`

`CONTINGENCY / DERATED = O2, CH4, CO`

This hierarchy is **not yet QUALIFIED**.

### Required next pass

Q2 v0.2 must quantify:

1. storage density / tank-volume implications for each feed;
2. tank temperature/pressure class;
3. estimated dissociation + first-ionization energy per kg;
4. conditioning-energy fraction relative to jet energy by torch mode;
5. likely plasma-radiation/material-risk class;
6. Solar-System sourcing/logistics class;
7. whether a single conditioner/nozzle architecture plausibly covers TF-A and TF-B;
8. which combinations deserve full per-mode certification testing.

### Current disposition

**Q2 remains OPEN.**

However, v0.1 supports continuing the multi-feed architecture and gives no reason to freeze the torch to a chemically unique remass species.