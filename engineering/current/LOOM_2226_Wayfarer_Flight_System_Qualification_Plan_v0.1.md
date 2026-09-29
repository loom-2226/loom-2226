# LOOM 2226 — Wayfarer Flight System Qualification Plan v0.1

**Status:** ACTIVE ENGINEERING QUALIFICATION / NON-CANON  
**Date:** 2026-09-11  
**Target artifact:** `WAYFARER_FLIGHT_SYSTEM_STANDARD_V1.0`  
**Authority boundary:** this plan does not alter governing canon. Current CANON II v2.4 remains authoritative until a later governed promotion.

---

## 0. Purpose

Produce one finalized, internally closed standard thrust and maneuvering package for the reference courier **Wayfarer** that is credible for 2226, machine-readable by Navigator, and explicit about what is canon, what is derived, and what remains optional.

The qualified package must cover:

1. main torch propulsion;
2. torch reaction-mass / working-fluid compatibility and doctrine;
3. optional endurance propulsion that may use negligible or no carried remass;
4. local translation / RCS;
5. attitude control;
6. metric-drive interface states;
7. power and thermal closure;
8. mass closure, reserves, failure states and Navigator integration.

The package shall be derived from mission and conservation requirements rather than selected by aesthetic preference.

---

## 1. Governing baseline preserved during qualification

Until a replacement earns promotion, preserve the current governing baseline:

- TORCH = ordinary momentum exchange;
- METRIC = continuous subluminal relational/metric transport;
- LOOM = discontinuous interstellar relational re-embedding;
- no drive silently performs another drive's conservation work;
- free work / free momentum cycles are HARD KILL;
- Wayfarer current reference wet mass ≈ 1,158.5 t;
- current dry mass ≈ 858.5 t;
- current working-fluid/water inventory ≈ 300 t;
- current normal remass allowance ≈ 250 t within that inventory;
- current protected water reserve ≈ 50 t;
- one primary axial fusion torch / magnetic nozzle;
- current exhaust-velocity cards: ECON 3000 km/s, CRUISE 2000 km/s, EXPEDITE 1000 km/s, FAST 700 km/s, HARD 450 km/s, LIMIT 300 km/s;
- metric and major torch operation remain mutually exclusive thermal/field states unless later evidence changes that rule through governance.

No current canon value is silently overwritten during this project.

---

## 2. Qualification philosophy

Every proposed subsystem or operating card shall carry one of four dispositions:

- `BASELINE` — inherited current canon or current authoritative engineering baseline;
- `CANDIDATE` — engineered proposal undergoing qualification;
- `QUALIFIED` — passes the defined gates and is eligible for canon promotion;
- `REJECTED` — fails a hard gate or is dominated by a better qualified option.

Every numerical value shall also state its provenance class:

- `CANON`
- `MEASURED_OR_PUBLISHED_PHYSICS`
- `DERIVED`
- `ENGINEERING_ASSUMPTION`
- `FICTIONAL_CONSTITUTIVE_LAW`
- `OPEN`

---

# Q1 — Mission and propulsion architecture

## Goal

Define the actual jobs each mobility system must perform before assigning hardware.

## Required mobility layers

### Q1-A Main torch

Role:

- high-thrust ordinary-space acceleration and braking;
- rapid terminal-state matching;
- emergency abort / collision avoidance where high thrust is required;
- gravity-well and local operations where metric is unavailable or uncertified;
- tactical / time-critical ordinary-space maneuver.

The torch remains reaction-mass propulsion unless a future canon change explicitly replaces that foundational rule.

### Q1-B Endurance propulsion slot

Role:

- sustained ordinary-space cruise where high thrust is not required;
- reduce routine torch remass consumption;
- accumulate large delta-v over days/weeks when thermal and power closure permit.

Three implementation states shall be supported:

- `E0_NONE` — no endurance system; current torch baseline remains sufficient;
- `E1_LOW_REMASS` — established or extrapolatable high-power electric/plasma propulsion using small carried working-fluid mass;
- `E2_MOMENTUM_COUPLED` — no/near-zero carried-remass propulsion only if a physical momentum-exchange mechanism and complete conservation ledger are qualified.

`E2` is not a prerequisite for completing the Wayfarer standard.

### Q1-C Local translation / RCS

Role:

- docking;
- station keeping;
- formation flight;
- collision avoidance at low relative velocity;
- precise translations;
- main-engine trim;
- metric acquisition / collapse alignment support.

### Q1-D Attitude control

Role:

- nominal orientation control;
- telescope/sensor pointing;
- torch-axis alignment;
- docking alignment;
- momentum unloading;
- emergency slew.

Preferred architecture to test: internal momentum-storage system plus distributed external thrusters.

### Q1-E Metric interface

Metric is not a conventional thruster. Preserve the state sequence:

`ordinary-space maneuver -> metric acquisition -> metric transport -> collapse -> ordinary-space terminal maneuver`

Navigator must keep metric coordinate transport distinct from ordinary velocity and momentum state.

## Q1 exit criteria

PASS when every representative mission phase maps to exactly one qualified mobility layer or an explicit allowed combination, with no hidden momentum reset.

---

# Q2 — Torch remass / feedstock qualification

## Goal

Replace the accidental assumption `REMASS = WATER` with a physically explicit **torch feedstock interface standard**, while separately defining what Wayfarer normally carries.

## Q2-A Required engine-side properties

Derive the allowable envelope for:

- molecular / atomic mass;
- phase at tank and feed conditions;
- ionization / dissociation energy;
- achievable chamber/plasma state;
- magnetic-nozzle compatibility;
- impurity tolerance;
- corrosivity / materials compatibility;
- conductivity / charge-state requirements;
- contamination deposition risk;
- feed-system pressure and temperature;
- storage density;
- thermal conditioning burden;
- nozzle / reactor erosion burden.

## Q2-B Candidate feedstocks

At minimum evaluate:

- H2O / steam / dissociated water plasma;
- H2;
- NH3;
- CH4;
- CO2;
- CO;
- N2;
- Ar;
- O2 / oxygen-rich processed volatile stream.

Additional species may be added only if their Solar-System sourcing or performance makes them materially useful.

## Q2-C Rating system

Each feedstock x torch-mode combination shall receive one rating:

- `CERTIFIED` — normal unrestricted operation within card limits;
- `DERATED` — permitted with reduced thrust, exhaust velocity, duty cycle or maintenance interval;
- `CONTINGENCY` — emergency/frontier use only;
- `PROHIBITED` — incompatible or unacceptable.

For every rating record:

- achievable exhaust velocity;
- thrust at the qualified power point;
- mass flow;
- kg remass per hour;
- delta-v per tonne at representative ship masses;
- conditioning power;
- ship-coupled waste heat;
- storage volume per tonne;
- handling hazards;
- contamination / erosion factor;
- maintenance penalty.

## Q2-D Wayfarer doctrine

Do not conflate engine compatibility with normal logistics. Final standard shall identify:

- `PRIMARY_REMASS`
- `ALTERNATE_REMASS`
- `CONTINGENCY_REMASS`
- `PROTECTED_WATER_RESERVE`

Water may still emerge as the primary because of density, storage simplicity, life-support, shielding and thermal utility, but that conclusion must be earned by Q2 rather than assumed.

## Q2-E Storage architecture

Evaluate whether the four current major tanks can support:

- common certified feed;
- segregated mixed feed;
- tank reconfiguration / cleaning;
- protected potable / life-support reserve isolated from propulsion contamination.

## Q2 exit criteria

PASS when at least one primary and one alternate remass option are qualified and the torch card closes for each without changing foundational torch conservation.

---

# Q3 — Endurance-drive qualification

## Goal

Determine whether 2226 Wayfarer should carry a sustained low-thrust system in addition to the torch.

## Q3-A Performance targets to explore

Do not pre-lock acceleration. Evaluate at least:

- 0.005 g;
- 0.01 g;
- 0.03 g;
- 0.05 g;
- 0.10 g.

For each case compute time to 100, 500 and 1000 km/s, energy / power requirements, thermal burden and mission utility.

## Q3-B E1 low-remass lane

Research and model physically conservative high-power electric/plasma architectures that consume small working-fluid quantities.

Required outputs:

- thrust-to-power;
- exhaust velocity;
- propellant species;
- mass flow;
- electrode / grid / magnetic lifetime constraints;
- power conversion architecture;
- heat rejection;
- hardware mass;
- scaling limits.

## Q3-C E2 momentum-coupled lane

Research only unless and until all hard gates close.

Candidate inspirations may include Mach-effect / inertia-coupling / field-coupling concepts, but no historical claim is accepted as evidence of a working drive.

Mandatory hard gates:

1. define the physical momentum exchange partner;
2. close local/global conservation ledger;
3. prohibit hidden shipboard momentum bank;
4. prohibit wake cycle that yields free momentum or work;
5. provide a constitutive scaling law with uncertainty;
6. identify a falsifiable experimental pathway;
7. close power and thermal requirements at Wayfarer scale.

Failure of any gate leaves `E2` as `OPEN_RESEARCH` and blocks canon promotion.

## Q3 exit criteria

PASS when either E1 or E2 demonstrably improves mission performance / remass reserve enough to justify its hardware mass and thermal burden. E0 remains valid if neither earns inclusion.

---

# Q4 — RCS, translation and attitude control

## Goal

Replace MVP maneuver numbers with actuator-derived handling canon.

## Q4-A Rigid-body model

Build a Wayfarer mass-property model covering:

- wet / dry states;
- four-tank depletion;
- launch DOCKED / ABSENT;
- cargo variation;
- radiator state where relevant;
- center of mass;
- principal moments of inertia;
- products of inertia / lateral imbalance where material.

## Q4-B Translation system

Derive:

- station-keeping thrust;
- docking translation acceleration;
- minimum impulse bit;
- plume / dead-zone constraints;
- total RCS working-fluid reserve;
- redundancy after one cluster loss.

## Q4-C Attitude system

Evaluate internal momentum storage plus external unloading / high-authority thrusters.

Derive rather than assume:

- pitch/yaw/roll angular acceleration;
- maximum nominal slew rate;
- emergency slew rate;
- braking / settle time;
- pointing accuracy;
- main-torch alignment tolerance;
- docking alignment tolerance;
- momentum saturation and unload interval.

## Q4 exit criteria

PASS when every attitude / docking number used by Navigator derives from a physical actuator model and current mass properties.

---

# Q5 — Power and thermal closure

## Goal

Make every drive card thermally and energetically self-consistent.

For every propulsion mode record:

- source power;
- directed jet / exhaust / field power;
- power conversion losses;
- electrical-bus demand;
- conditioning power;
- cryogenic demand;
- ship-coupled waste heat;
- radiator reject temperature;
- required equivalent radiator area;
- thermal-buffer use;
- continuous duty limit;
- cool-down / recovery requirement;
- compatibility / exclusion with metric operation.

Torch jet power shall not be treated as automatically interchangeable with electrical output.

## Q5 exit criteria

PASS only when steady-state or explicitly bounded transient thermal closure exists for every certified operating card.

---

# Q6 — Representative mission and regression suite

Run at minimum:

- Earth <-> Ceres;
- Mars <-> Ceres;
- Mars <-> Jupiter system;
- Ceres <-> Neptune;
- outer-system expedition case;
- metric unavailable case;
- endurance drive unavailable case;
- torch unavailable case where survival is still physically possible;
- radiator degradation case;
- one RCS cluster failed;
- low-remass reserve arrival;
- emergency high-g terminal correction.

For each mission compare E0 / E1 / E2 where available and report:

- elapsed time;
- metric path/time;
- ordinary-space delta-v;
- torch burn time;
- endurance burn time;
- remass consumption by species;
- reserve at arrival;
- peak and integrated thermal load;
- energy consumed;
- crew-g exposure;
- subsystem duty cycles;
- hard-gate result.

No historical route result is promoted as a machine constant.

---

# Q7 — Failure, reserve and dispatch doctrine

Define operational behavior for:

- torch unavailable;
- endurance drive unavailable;
- metric unavailable / uncertified;
- degraded radiator capacity;
- reduced reactor / bus power;
- one major tank isolated;
- primary remass unavailable at destination;
- alternate feed only;
- RCS cluster loss;
- attitude momentum system degraded;
- launch absent / docked mass asymmetry.

Final doctrine shall specify:

- normal dispatch remass;
- minimum legal/safe dispatch remass;
- protected reserve;
- reserve not available to routine optimization;
- contingency-feed reserve if carried;
- abort / diversion triggers.

---

# Q8 — Final mass closure and Navigator integration

## Goal

Produce one machine-readable authority object consumed by geometry, Navigator and later simulation systems.

Target schema concept:

```text
WAYFARER_FLIGHT_SYSTEM_STANDARD_V1.0
  identity
  mass_states
  torch
    hardware
    mode_cards
    feedstock_interface
    feedstock_ratings
    reserve_doctrine
  endurance
    implementation_class
    cards
  rcs
  attitude
  metric_interface
  power_thermal
  configuration_states
  failure_modes
  provenance
  qualification_status
```

Navigator shall not own duplicated machine constants that belong to this standard.

Integration must use typed/adapted access rather than scattering new hard-coded field names through routing logic.

## Q8 exit criteria

PASS when:

1. all standard fields validate;
2. mass ledger closes;
3. each certified mode closes energy, momentum and thermal ledgers;
4. Navigator regression suite passes;
5. geometry / mass-property model reads the same authority object;
6. no current canon is silently changed;
7. canon-promotion patch is separately reviewable.

---

## 9. Work order

Execute in this order:

1. **Baseline capture** — machine-readable snapshot of current authoritative Wayfarer flight constants and open items.
2. **Q2 feedstock study** — because remass identity and storage affect ship mass, tanks and torch cards.
3. **Q4 mass properties + RCS/attitude model** — needed for real maneuver performance.
4. **Q5 torch power/thermal closure** — revalidate existing cards against final mass/feed assumptions.
5. **Q3 endurance-drive lanes** — E1 engineering first; E2 research in separate research authority.
6. **Q6 mission suite** — derive actual remass requirement rather than retaining 250 t by inertia.
7. **Q7 reserve doctrine**.
8. **Q8 integrated standard + Navigator adapter**.
9. Independent hostile review.
10. Separate governance action for canon promotion.

---

## 10. Immediate no-regret decisions

The following are adopted for this engineering project but are **not** canon changes:

- Preserve current 250 t normal remass + 50 t protected water reserve as the comparison baseline.
- Do not freeze H2O as the only permissible torch remass.
- Treat torch compatibility and Wayfarer carried-remass doctrine as separate decisions.
- Preserve optionality for multiple certified feedstocks.
- Preserve an endurance-drive slot with E0/E1/E2 implementation states.
- Do not require E2 propellantless physics for Wayfarer qualification.
- Do not reduce remass capacity until representative mission analysis demonstrates the reserve is unnecessary.
- Do not promote RCS angular-rate placeholders into actuator canon.
- Keep TORCH / METRIC / LOOM physically distinct unless changed through governed physics/canon process.

---

## 11. Required final outputs

The project is not complete until it produces:

1. `WAYFARER_FLIGHT_SYSTEM_STANDARD_V1.0` machine-readable artifact;
2. human-readable engineering qualification report;
3. torch feedstock compatibility matrix;
4. final torch mode card;
5. endurance-drive disposition (`E0`, `E1`, or qualified `E2`);
6. RCS / attitude actuator card;
7. mass-property envelope;
8. power / thermal closure report;
9. mission-regression report;
10. reserve / dispatch doctrine;
11. Navigator adapter + regression tests;
12. separately reviewable canon-promotion patch.

Until item 12 is approved and merged through governance, this project remains engineering authority only.