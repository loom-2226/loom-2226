# Wayfarer 2226 Engineering Frontier Register v0.1

**Status:** WORKING REGISTER / PASS B BOUNDED HORIZON COMPLETE  
**Protocol:** `LOOM_2226_ENGINEERING_FRONTIER_PROTOCOL_v0.1`  
**Authority:** NO NEW DOWNSTREAM NUMERICAL AUTHORITY UNTIL FREEZE  
**Target epoch:** 2226

## BLUF

This register prevents the Frontier program from becoming eight dissertations. It derives a compact shared set of ordinary-engineering capabilities for the Wayfarer drivetrain, once, then lets torch, RCS, E2, metric/LOOM and other consumers pin those producer values.

Target size: **30–50 projected engineering parameters total**. A parameter that cannot be bounded quickly and honestly remains `UNRESOLVED`.

The first bounded horizon pass is preserved in `WAYFARER_2226_ENGINEERING_FRONTIER_HORIZON_PASS_v0.1.md`. It occupies the 42-slot ceiling but deliberately leaves coupled/architecture-dependent quantities unresolved rather than guessing them.

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

**Current status:** evidence pass classifies `INSUFFICIENT_FOR_QUANTITATIVE_HINDCAST`; bounded scenario factors are defined but continuous field remains `UNSET` pending coupled accounting.

### F2 — Power generation, conversion and distribution
**Consumers:** fusion driver/source balance-of-plant, torch auxiliaries, RCS/feed, E2, metric/LOOM, thermal systems.

**Project at most:** continuous source-independent electrical conversion efficiency; converter/distribution specific power; voltage/field/current-density envelope; radiation/high-temperature derating; pulse-power delivery where relevant.

**Current status:** bounded conversion/PMAD efficiency and specific-power scenarios defined; source specific power and generic pulse-power value not invented.

### F3 — Energy storage and transient buffering
**Consumers:** pulse loads, startup/transients, field systems, metric/LOOM support hardware, thermal buffers.

**Project at most:** usable specific energy; specific power; round-trip efficiency; cycle/lifetime envelope; thermal/protection burden.

**Current status:** separate energy/power scenario factors defined with Ragone firewall; chemistry remains unselected.

### F4 — Structures, shielding and extreme-environment materials
**Consumers:** thrust frame, reactor/shield region, magnetic systems, radiators, RCS mounts, pressure/cryogenic systems, metric/LOOM support hardware.

**Project at most:** system-level usable specific strength/stiffness; operating-temperature derating; creep/fatigue/lifetime; radiation/neutron fluence tolerance; erosion/plasma-facing durability; shielding mass-performance where ordinary materials physics supports it.

**Current status:** modest system-level improvement scenarios defined; blanket 8x strength rejected; shielding performance remains spectrum/geometry dependent and `UNRESOLVED`.

### F5 — Thermal transport, buffering and radiators
**Consumers:** essentially the entire drivetrain.

**Project at most:** radiator operating-temperature envelope by material/loop class; effective emissivity; installed radiator specific mass or kg/kW at stated temperature; heat-transport specific capacity; turndown/freeze tolerance; thermal-buffer specific energy.

**Current status:** temperature-conditional radiator/transport scenarios defined. Stefan-Boltzmann remains mandatory accountant; no independent magic heat-rejection multiplier.

### F6 — Fluids, propellants, cryogenics and RCS enabling engineering
**Consumers:** torch remass feed, RCS, fusion auxiliaries, cooling loops and storage.

**Project at most:** tank/system mass fraction by storage class; heat leak/active refrigeration burden; long-duration retention; pump/valve/injector specific power and response class; conventional thruster performance/lifetime envelope; feed-system turndown.

**Current status:** active zero-boiloff-compatible cryogenic scenarios and feed-system improvement factors defined. No universal RCS performance multiplier or working fluid selected.

### F7 — Fusion and torch enabling engineering
**Consumers:** Wayfarer primary torch.

**This is a consumer/integration frontier, not a license to extrapolate fusion physics.**

**Current status:** source specific power, directed fraction and installed nozzle capability remain unresolved; thermal capability inherits F5 only at an earned `P_heat`.

### F8 — E2, metric and LOOM enabling engineering
**Consumers:** E2 momentum-coupled propulsion, metric drive support systems, LOOM-specific hardware.

**Hard firewall:** this frontier projects support technology only. It may not project an unknown momentum-coupling mechanism, momentum sink, metric constitutive law, Mc-299m property, topology manipulation mechanism or other unearned LOOM/RF physics.

**Current status:** support envelopes await integrated accountant; mechanism variables remain outside Frontier authority.

## Dependency graph

`F4 STRUCTURES/MATERIALS -> F1 FIELDS, F5 THERMAL, F6 FLUIDS`

`F2 POWER + F3 BUFFERING + F1 FIELDS + F4 MATERIALS + F5 THERMAL + F6 FLUIDS -> F7 FUSION/TORCH`

`F1 + F2 + F3 + F4 + F5 -> F8 E2/METRIC/LOOM SUPPORT`

RCS primarily consumes F2/F4/F6. No consumer gets to reapply a producer improvement as a second multiplier.

## Parameter budget

The bounded pass uses the maximum initial allocation:

- F1: 6
- F2: 5
- F3: 5
- F4: 6
- F5: 6
- F6: 6
- F7: 4 integration outputs
- F8: 4 integration outputs

Total: **42 slots**. This is a ceiling, not a target for v1.0. The integrated accountant must identify unused/nonbinding slots for deletion before freeze.

## Work plan and exit criteria

### Pass A — evidence cards — COMPLETE ENOUGH FOR BOUNDED PASS
Literature review and F1 evidence pass establish current classes and major constraints. Not every family has enough like-for-like evidence for quantitative forecasting; bounded scenario construction is therefore the default.

### Pass B — bounded 2226 cases — COMPLETE / PROVISIONAL
Preserved in `WAYFARER_2226_ENGINEERING_FRONTIER_HORIZON_PASS_v0.1.md`. Unsupported absolute future quantities remain `UNRESOLVED`; ordinary progress is mostly represented as conservative/MVP/aggressive factors relative to named relevant 2026 system classes.

### Pass C — integrated accountant — NEXT
One model consumes a concrete Wayfarer consumer case and checks efficiency chains, waste heat, mass burdens, field/stored-energy burdens, structural/thermal compatibility, cryogenic loads and cross-frontier double counting. Use Z3 only where coupled constraints make SMT materially useful.

**Exit:** no silent contradiction among proposed producer values; failures identify assumptions rather than invent fixes; unused frontier slots are candidates for deletion.

### Pass D — hostile review and freeze
Give the complete register, evidence cards, equations, assumptions and accountant outputs to an adversarial reviewer. Fix specific defects once. Freeze `WAYFARER_2226_ENGINEERING_FRONTIER_REGISTER_v1.0` with producer version/hash.

## Current authority

- Protocol hostile-review conditions: incorporated.
- Literature review: complete enough for initial horizon pass.
- F1: evidence pass performed; field authority `UNSET`.
- F2–F6: provisional bounded scenarios produced; **not frozen downstream authority**.
- F7/F8: integration/mechanism firewalls preserved.
- Integrated 2226 register: `NOT_YET_FROZEN`.

## Primary-source basis

See the literature review, F1 evidence pass, and horizon-pass references. Principal source families are NASA Small Spacecraft State of the Art, NASA NTRS high-power spacecraft studies, NASA cryogenic-fluid management work, NASA extreme-materials work, National MagLab magnet records, and the U.S. DOE Fusion Science & Technology Roadmap.
