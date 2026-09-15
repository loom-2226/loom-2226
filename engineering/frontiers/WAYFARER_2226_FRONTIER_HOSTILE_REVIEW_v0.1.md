# Wayfarer 2226 Engineering Frontier — Hostile Review v0.1

**Disposition:** ACCEPT WITH REQUIRED CORRECTIONS / NOT YET FREEZE-READY  
**Scope:** protocol + bounded horizon + accountant + actual Canon II / E1 RCS / E1 torch consumers

## Review question

Does the frontier package provide a compact, reusable ordinary-engineering floor for the actual Wayfarer without double counting progress, rewriting canon, erasing E1 evidence, or smuggling unresolved mechanisms into existence?

## Finding H1 — FIXED: consumer-load direction was backwards

**Severity: HIGH.** The first canon-metric consumer exercise passed the certified cryogenic electrical load into a forward efficiency chain as though it were upstream source power. That reduced delivered power below the canon requirement.

A certified consumer load is fixed. Conversion and PMAD losses must be paid upstream:

`P_upstream = P_load / (eta_conversion * eta_PMAD)`

and ordinary distribution heat is:

`P_heat = P_upstream - P_load`.

Tests were changed first to require this invariant, then the consumer exercise was corrected. Canon load is no longer derated by the frontier scenario.

## Finding H2 — REQUIRED: prune the 42-slot ceiling before freeze

The initial 42 slots are useful research bookkeeping but too many deserve producer-authority status. Several are architecture-dependent outputs, not reusable producer parameters.

### KEEP as producer/frontier quantities

F1: engineering current-density/field capability by stated scale; installed magnet burden; cryogenic burden; stored-energy/protection burden; radiation lifetime.

F2: conversion efficiency; PMAD efficiency; installed specific power; environment/radiation derating.

F3: technology-class usable specific energy; specific power; round-trip efficiency/lifetime only when a real load-duration case selects the class.

F4: installed structural specific-load capability; high-temperature derating; fatigue/lifetime; radiation/fluence lifetime; plasma/erosion lifetime where actually consumed.

F5: radiator temperature class; emissivity; installed areal/specific mass; heat-transport capacity; freeze/turndown capability.

F6: tankage burden by storage class; active cryogenic burden; retention; feed-system burden/turndown/response; RCS component performance only after working-fluid/cycle selection.

### DEMOTE from producer authority to consumer-derived/output

- F7 source mass, source electrical power, torch radiator area and nozzle installed performance: these depend on unresolved source/nozzle/deposition physics.
- F8 E2 thrust/power performance and metric/LOOM mechanism performance: these depend on separate earned physics.
- generic shielding mass-performance without a spectrum/geometry/material stack.
- generic pulse-power capability without a defined pulse/load case.
- generic thermal-buffer capability without a defined transient.
- a universal RCS Isp/exhaust-velocity multiplier.

**Result:** the frozen producer register should target roughly **24–30 genuinely reusable quantities**, not preserve 42 merely because slots exist.

## Finding H3 — KEEP UNRESOLVED: F1 field number

No defensible like-for-like historical hindcast exists for a Wayfarer-scale continuous superconducting magnet. A single stress bound or material record cannot authorize 50 T, 75 T, 100 T or ~375 T as the ship field.

F1 should expose a coupled design interface and bounded material/system improvements while `large_system_continuous_field_t = UNSET` until bore, conductor critical surface, structure, stored energy, quench/protection, cryogenics and radiation lifetime are jointly solved.

## Finding H4 — KEEP UNRESOLVED: fusion-source closure

The ordinary-engineering frontiers can make a future fusion system lighter, tougher, colder/hotter, better switched and better cooled. They cannot earn fusion gain, source directed fraction, source specific power, radiation/deposition partition or magnetic-nozzle plasma physics.

Therefore the E1 torch remains exactly what T5 says: vehicle interface closed with technology holds, not component hardware certified.

## Finding H5 — KEEP UNRESOLVED: RCS physical cycle

E1 gives enough force/torque/demand evidence to constrain a future component selection but not enough to select propellant, exhaust velocity, MIB, valve response, cycle life or plume. F6 must not collapse these into one generic future-thruster factor.

## Finding H6 — CANON/E1 coexistence is correct

Canon contributes governing relational-plant, metric, packaging and operating requirements. E1 contributes later, independently earned vehicle-interface engineering detail. The accountant must preserve both and report conflicts rather than resolving them by authority erasure.

No contradiction requiring canon or E1 mutation was found in this pass. Candidate torch packaging remains non-governing and therefore cannot displace frozen RCS hardpoints.

## Finding H7 — operational diversity must be explicit

Torch and high-metric operation are mutually exclusive. Full torch and full metric peak loads therefore must not be summed as a simultaneous design case. However transition, shutdown, residual heat, standby, RCS and emergency loads are not thereby zero. A future integrated load schedule should distinguish mutually exclusive peak modes from transition/coincident loads.

## Finding H8 — the 2 GJ bank is a requirement, not a trend target

Canon already fixes the shared relational bank at 2 GJ. F3 should not project a larger 2226 bank simply because storage technology improves. F3's role is to determine the plausible installed mass, power, efficiency, lifetime and thermal consequences of satisfying that 2 GJ requirement once an appropriate storage architecture is selected.

## Finding H9 — no current reason for Z3

The current accountant is exact arithmetic plus explicit unresolved variables. There is not yet a sufficiently specified coupled magnet/source/thermal/RCS physical design to make SMT useful. Adding Z3 now would create proof theater. Use it later when real inequalities and mutually dependent design variables exist.

## Freeze gate

Before v1.0:
1. prune producer parameter set to reusable quantities only;
2. preserve consumer-derived quantities outside producer authority;
3. run Python regression for accountant + consumer exercise;
4. record exact producer version/hash;
5. mark every downstream consumer as requiring explicit revalidation before frozen frontier values can become load-bearing authority;
6. do not fill unresolved mechanism-dependent values merely to obtain a complete table.

**Current disposition:** the architecture is sound after H1 correction, but numerical frontier scenarios remain provisional and the register is **NOT_YET_FROZEN**.
