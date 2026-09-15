# Wayfarer 2226 Engineering Frontier Accountant v0.1

**Status:** PASS C / PROVISIONAL ACCOUNTANT  
**Authority:** NOT FROZEN / NOT DOWNSTREAM AUTHORITY  
**Inputs:** `WAYFARER_2226_ENGINEERING_FRONTIER_HORIZON_PASS_v0.1.md` plus existing earned E1 interfaces

## Purpose

Make the frontier scenarios pay their ordinary engineering bills without turning the frontier program into detailed component design. The accountant consumes producer assumptions once and exposes heat, efficiency, mass-factor and unresolved-physics dependencies.

## Implemented now

`src/wayfarer_2226_frontier_accountant.py` implements the three Pass-B scenarios and checks:

- conversion efficiency and PMAD efficiency as separate stages;
- conservation of electrical power across delivered load plus conversion/PMAD losses;
- conversion/PMAD losses as heat rather than disappearing them;
- Stefan-Boltzmann radiator flux at explicit temperature and scenario emissivity;
- radiator area required for those ordinary electrical losses;
- shared F1/F4/F5/F6 improvement factors without reapplying them in F7/F8;
- explicit unresolved outputs for large-system magnet field, fusion source specific power, RCS exhaust velocity, E2 momentum partner and metric constitutive law.

The default 900 K radiator temperature is inherited from the existing E1 `HIGH_DRIVE_REJECT_INTERFACE_K`; it is not a new 2226 technology projection.

## Deliberately not implemented yet

The accountant does **not** invent baselines merely so every Pass-B factor can produce an absolute number. Therefore these remain holds until a real consumer supplies a relevant class/baseline:

- F1 field/bore/mass/stored-energy coupled magnet solution;
- F3 storage mass without load energy, duration and storage class;
- F4 shielding mass without radiation spectrum, material and geometry;
- F5 installed radiator mass without a like-for-like installed baseline;
- F6 RCS performance without cycle and working fluid;
- F7 fusion source/nozzle quantities that depend on unresolved source/plasma physics;
- F8 E2 momentum partner and metric constitutive physics.

This is intentional. A factor such as `5x specific power` is not allowed to become an absolute component capability until the consumer names the 2026 system class to which it applies.

## First dependency reduction

The 42 Pass-B slots are not 42 independent ship knobs. The first accountant pass shows several can be treated as subordinate variables rather than top-level frontier authority:

1. F2 conversion efficiency + PMAD efficiency jointly determine ordinary electrical distribution heat.
2. F5 emissivity + explicit radiator temperature determine ideal radiative flux; heat rejection is not an independent multiplier.
3. F3 energy and power capability cannot be selected independently without a load-duration/storage-class decision.
4. F1 field cannot be selected independently from bore, current density, structure, stored energy/protection, cryogenics and radiation lifetime.
5. F6 RCS performance cannot be selected independently from physical propulsion cycle and working fluid.
6. F7/F8 must consume F1-F6 rather than receive duplicate future-tech multipliers.

These dependencies are candidates for reducing the final frozen register below 42 top-level quantities.

## Test contract

`tests/test_wayfarer_2226_frontier_accountant.py` requires:

- all three scenarios exist;
- no efficiency/emissivity reaches perfection;
- source electrical power equals delivered load plus accounted losses;
- radiator flux obeys the fourth-power temperature law;
- unearned mechanism-dependent values remain `None`;
- the integrated case exposes F2/F5 dependencies and unresolved F1/F3/F4/F6/F7/F8 holds.

## Next bounded increment

Do **not** broaden the literature search or add more frontier parameters. The next useful step is to exercise this accountant against the actual Wayfarer consumers already in Git:

1. ordinary ship electrical/thermal support case if an earned load exists;
2. E1 torch only where `P_heat` or another input is already earned;
3. RCS only where its frozen interface supplies a physical requirement;
4. E2/metric only as support-technology envelopes, leaving mechanism physics unresolved.

Where a required absolute baseline does not exist, report `UNRESOLVED` and move on. This is the anti-rabbit-hole stopping rule.
