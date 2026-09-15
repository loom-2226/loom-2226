# Wayfarer 2226 Frontier — Canon + E1 Consumer Exercise v0.1

**Status:** PASS C CONSUMER EXERCISE / PROVISIONAL  
**Authority:** NO CANON MUTATION / NO E1 MUTATION / NO NEW-PHYSICS AUTHORITY

## BLUF

The integrated frontier accountant is exercised against both governing current canon and the independently earned Experience One RCS/torch engineering interfaces. Canon is not used as a filter that discards E1 engineering evidence; E1 is not allowed to overwrite canon. The exercise preserves both authority classes and exposes the seams that the future-engineering register must actually serve.

## Authority inputs

### Governing current canon
- `canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md`
- `canon/current/LOOM_2226_CANON_II_Wayfarer_Schematic_Amendment_v2.4a.md`

Important consumed facts include the ~88 t shared relational plant, 10 kg Mc-299m, 208 distributed nodes, 2 GJ reversible bank, 150 kW-class/20 K cryoplant, 900 K high-drive reject interface, certified metric cards and their cryogenic electrical/radiator-equivalent loads, metric/Loom shared hardware, four axial longerons, four quadrature working-fluid/remass tanks, four deployable radiators, one axial fusion torch, and the x=16–28 m integrated launch-bay reservation.

### Experience One engineering authority
- `engineering/experience_one/WAYFARER_E1_RCS_FLIGHT_DYNAMICS_GEOMETRY_INTERFACE.md`
- T1–T5 executable torch closure in `src/wayfarer_e1_torch_*`
- detailed torch handoff currently preserved in PR #237: `engineering/experience_one/WAYFARER_E1_TORCH_PROPULSION_INTEGRATION_GEOMETRY_INTERFACE.md`

Important consumed facts include the 1,158.5 t wet / 858.5 t dry mass state, 250 t normal remass + protected 50 t water, six torch cards, 250:1 feed turndown, 900 K/four-radiator interface, 85.207530 MN known LIMIT axial load, 16 frozen RCS hardpoints, 25 kN allocator cap, 100/75 kN nominal/degraded translation requirements, 1 MN m nominal pitch/yaw authority, and sampled actuator-demand evidence.

## What the exercise found

### 1. Canon adds real frontier consumers that the first accountant did not yet exercise

The shared relational plant is not merely narrative context. Its certified metric cards impose real electrical and thermal loads. The consumer exercise now sends the canon cryogenic electrical demand through the provisional F2 conversion/PMAD chain and computes the *additional distribution/conversion heat* through F5 at the canon 900 K interface.

The canon-reported 900 K radiator-equivalent areas are retained separately. They are not replaced by the frontier calculation, because they represent an already-certified metric card while the frontier calculation represents only incremental ordinary-engineering PMAD/conversion burden. This prevents double counting and prevents the future-tech register from silently rewriting canon.

### 2. E1 torch turns several frontier slots into genuine requirements

The 250:1 feed turndown, 1.1361004025–284.025100625 kg/s mass-flow range, four-radiator topology, 900 K interface and 85.207530 MN known axial load are real consumers of F4/F5/F6.

But the exercise still cannot honestly compute source mass, source electrical power, torch deposition heat, radiator area or magnetic-nozzle field because E1 deliberately leaves source directed fraction, Q/source realizability, source specific power, vehicle deposition fraction, working-fluid species and nozzle physics open.

Therefore F1/F2/F4/F5/F6 can narrow component holds later, but they cannot close the torch by themselves.

### 3. E1 RCS makes F6 materially more specific without choosing a thruster

The frozen architecture requires 16 compound coarse/fine vectored mounts, 25 kN per-mount allocation cap, 100 kN nominal translation, 75 kN one-cluster-out translation, and the qualified torque envelope. Sampled traces reached ~20.845 kN mount thrust and provide a ~9.281 N s exact-trace MIB upper-bound witness, but the latter is explicitly not hardware MIB.

This means F6 needs to support a future physical cycle against *actual force, response, lifetime, thermal and packaging requirements*. A generic 2226 Isp multiplier remains the wrong abstraction. Working fluid, exhaust velocity, hardware MIB, valve response, cycle life and plume remain open.

### 4. Packaging creates cross-frontier constraints

Canon preserves four longerons, four remass tanks, four radiators and the integrated launch bay at approximately x=16–28 m. E1 preserves RCS hardpoints including the aft band at x=44.5 m and torch candidate aft envelopes from x=38–57 m. These facts must coexist.

The frontier register therefore cannot optimize magnet mass, shielding, radiator mass or RCS hardware in isolation. Installed-system mass and geometry are the relevant quantities. Candidate torch envelopes remain non-governing and cannot erase the frozen RCS hardpoints.

### 5. Torch/metric exclusion is a major simplifier

Current E1 requires torch operation and high-metric thermal/field operation to be mutually exclusive. The frontier accountant should therefore avoid summing full torch and full metric peak loads as though simultaneous operation were required. Transition, standby and residual thermal loads remain open and must be handled separately.

This is an example of why exercising actual consumers is more valuable than inventing a universal 2226 power number.

## Frontier parameters that are clearly high-value after consumer exercise

Retain with high priority:
- F1 installed field-at-bore capability, magnet mass, cryogenic burden, protection/stored-energy burden, radiation lifetime;
- F2 conversion efficiency, PMAD path efficiency, PMAD specific power and radiation/temperature margin;
- F4 installed structural load capability, high-T capability, fatigue/lifetime and radiation lifetime;
- F5 emissivity, installed radiator mass at stated T, heat-transport capability and high-T loop capability;
- F6 cryogenic burden, tankage burden, feed-system burden/turndown and physical RCS-cycle capability once selected.

F3 storage remains relevant for the canon 2 GJ relational bank and transients, but the current consumer exercise does not justify selecting one universal storage technology or multiplying the canon bank energy. The bank requirement is already 2 GJ; F3 should answer installed mass/power/lifetime implications when a technology class is selected.

## Parameters still correctly unresolved

- Wayfarer large-system continuous magnet field;
- fusion-source specific power;
- source directed fraction / fusion gain / energy-deposition partition;
- magnetic-nozzle field/topology/efficiency/lifetime;
- physical torch plume;
- RCS working fluid, exhaust velocity, hardware MIB, valve response and cycle life;
- shielding mass for actual spectra/geometry;
- installed torch radiator mass/area before deposition is earned;
- E2 momentum partner/mechanism;
- any new metric constitutive law or Mc-299m property beyond canon/research authority.

## Accountant implementation

`src/wayfarer_2226_frontier_consumers.py` provides a deterministic integration witness. It carries canon and E1 inputs side-by-side and uses the existing frontier accountant only where ordinary-engineering arithmetic is legitimate.

`tests/test_wayfarer_2226_frontier_consumers.py` protects the main authority boundaries: canon metric loads must not disappear; E1 torch/RCS requirements must not disappear; unresolved hardware remains `None`; packaging and torch/metric exclusion remain explicit.

## Disposition

The frontier register is now connected to the ship we are actually building rather than a generic future spacecraft.

The next useful step is **parameter pruning + hostile review**, not more technology research. The review should specifically attack whether any frontier factor is unused, duplicated, inconsistent with canon/E1, or capable of silently granting closure to an unresolved mechanism.
