# Wayfarer MASS CAMPAIGN — Track 1, ledger to physics

ALL bodies. ALL sponsors. 2026–2226.

**RESEARCH / DRAFT / NON-CANON / NON-RUNTIME / NO MERGE. kT decides.**

**Geometry SHA** `274e94fb43cfe549a3d2087abbdff4d65499ce6f5055ad2d7ade790414fbaaf9`. **Dry mass 867.531453t**, 292 individual parts. Ledger-to-parts sum **867.531453t**, discrepancy +0.000000015t.

**Critical distinction:** source builder spreads **18.656156t** of still-uncommitted engineering/released-structure growth mass into the non-`from_reserve` dry parts with factor **1.023704**. The booked pre-spread baseline for each line EXCLUDES that spread, but it is NOT a physically qualified mass. **Do not count those tonnes as already earned weight savings and then use them again to fund Halo.**

ECON local sensitivity for 1t near S1: **~0.693km/s recovered per tonne truly removed** (exact small-perturbation derivative, not route optimization). The shorthand 0.69km/s/t is sound near the current S1.

## Three independent source sizing calculations (others remain stated allocations)

| Governing calculation | Direct mass t | Ledger before spread t | Delta t | Status |
|---|---:|---:|---:|---|
| longeron CFRP source tube solids, before spread reserves/joint loads | 10.8530 | 11.9270 | -1.0740 | Independent geometric material screen; longeron joints/ring growth are distinct, G5 stress separate |
| radiator 1300K deployed panel areal basis | 8.7840 | 8.7840 | -0.0000 | Matches one-sided kg/m2 panel material, not full 90t thermal manifold |
| 1750K hotfin panel + folding support | 21.0240 | 21.0240 | +0.0000 | Two radiating faces per fin and 4t deployment/support allocation; lifetime unqualified |

These are direct **mass sizing** arithmetic checks, not a substitute for pressure, stress, radiation or heat rejection qualification. Reevaluate all critical G1–G12 physics for any accepted part change.

## Ranked source allocations before uncommitted reserve spread

| Rank | Part | Booked pre-spread t | Embedded uncommitted reserve t | Current geometry total t | Sizing status | Protected/canon? |
|---:|---|---:|---:|---:|---|---|
| 1 | `armor` | 105.000 | 2.489 | 107.489 | REQUIRED_NOT_REDESIGNED | YES |
| 2 | `manifold` | 90.000 | 2.133 | 92.133 | UNSIZED_ALLOCATION | review |
| 3 | `reactor` | 85.000 | 2.015 | 87.015 | UNSIZED_ALLOCATION | review |
| 4 | `shield` | 45.000 | 1.067 | 46.067 | REQUIRED_NOT_REDESIGNED | YES |
| 5 | `plant_fore` | 44.000 | 1.043 | 45.043 | UNSIZED_ALLOCATION | YES |
| 6 | `plant_aft` | 44.000 | 1.043 | 45.043 | UNSIZED_ALLOCATION | YES |
| 7 | `shuttle` | 30.021 | 0.712 | 30.732 | UNSIZED_OR_ASSUMED | YES |
| 8 | `nozzle` | 30.000 | 0.711 | 30.711 | UNSIZED_OR_ASSUMED | review |
| 9 | `electrical` | 26.950 | 0.639 | 27.589 | UNSIZED_OR_ASSUMED | review |
| 10 | `electrical_fwd` | 22.000 | 0.521 | 22.521 | UNSIZED_OR_ASSUMED | review |
| 11 | `courier_systems` | 19.000 | 0.450 | 19.450 | UNSIZED_OR_ASSUMED | review |
| 12 | `tank_shell_out` | 17.600 | 0.417 | 18.017 | ALLOCATION_PENDING_SIZING | review |
| 13 | `thrust_cone` | 16.300 | 0.386 | 16.686 | UNSIZED_OR_ASSUMED | review |
| 14 | `pressure_vessel` | 15.000 | 0.356 | 15.356 | ALLOCATION_PENDING_SIZING | YES |
| 15 | `tank_shell_in` | 14.400 | 0.341 | 14.741 | ALLOCATION_PENDING_SIZING | review |
| 16 | `room_L4-eclss` | 13.980 | 0.331 | 14.311 | UNSIZED_OR_ASSUMED | review |
| 17 | `core_racks` | 11.400 | 0.270 | 11.670 | UNSIZED_OR_ASSUMED | review |
| 18 | `skin_midship` | 9.862 | 0.234 | 10.096 | ALLOCATION_PENDING_SIZING | review |
| 19 | `bow_sensors` | 7.960 | 0.189 | 8.149 | UNSIZED_OR_ASSUMED | review |
| 20 | `service_arm` | 7.401 | 0.175 | 7.576 | UNSIZED_OR_ASSUMED | review |
| 21 | `crown_dome` | 6.202 | 0.000 | 6.202 | PARTIAL_GEOMETRY | review |
| 22 | `aft_bulkhead` | 5.500 | 0.130 | 5.630 | ALLOCATION_PENDING_SIZING | review |
| 23 | `crown_backup_pressure_dome` | 4.729 | 0.000 | 4.729 | PARTIAL_GEOMETRY | YES |
| 24 | `hotfin_40` | 4.256 | 0.000 | 4.256 | MIXED_SIZED | YES |
| 25 | `hotfin_140` | 4.256 | 0.000 | 4.256 | MIXED_SIZED | YES |
| 26 | `hotfin_220` | 4.256 | 0.000 | 4.256 | MIXED_SIZED | YES |
| 27 | `hotfin_320` | 4.256 | 0.000 | 4.256 | MIXED_SIZED | YES |
| 28 | `bay_liner` | 4.000 | 0.095 | 4.095 | UNSIZED_OR_ASSUMED | review |
| 29 | `docking_collar` | 3.980 | 0.094 | 4.074 | UNSIZED_OR_ASSUMED | review |
| 30 | `crown_c_additional_strata_gore` | 3.889 | 0.000 | 3.889 | REQUIRED_NOT_REDESIGNED | YES |
| 31 | `crown_adaptive_optogel` | 3.041 | 0.000 | 3.041 | DESIGN_INTERPOLATION | YES |
| 32 | `room_L4-medical` | 3.000 | 0.071 | 3.071 | UNSIZED_OR_ASSUMED | review |

Full 292-part record, explicit material classification, governing sizing requirement, provenance/source, identified canon lines and reserve distribution are in [mass_basis.json](../config/mass_basis.json). Rows without a quantitative sizing law are marked as **unsized allocations**, not material facts.

## How much actual strip-down buys 10–20Tm Halo?

| Halo case at Je1000 | Optimistic installed mass | Already free above 16.8t floor | **Verified additional mass saving required** | ECON reach cost if simply added |
|---:|---:|---:|---:|---:|
| 10Tm | 16.115t | 1.856t | **14.258t** | 11.00km/s |
| 15Tm | 24.103t | 1.856t | **22.247t** | 16.33km/s |
| 20Tm | 32.547t | 1.856t | **30.691t** | 21.87km/s |

### One testable **allocation target**, not an asserted saving

| Suspect ledger source | Hypothetical requested saving | Fraction of present pre-spread booked allocation | What must be shown |
|---|---:|---:|---|
| `manifold` | 10.00t | 11.1% | G4: thermal loop/pump/coolant mass from heat transfer and pressure, not bare radiators |
| `reactor` | 8.00t | 9.4% | G2/G4/G5: torch reactor actual mass from specific power and shield interfaces |
| `tank_shell_out` | 2.00t | 11.4% | G5: tank/carrying-shell pressure, 5g buckling and double-duty |
| `tank_shell_in` | 2.00t | 13.9% | G5/G6: internal tank shell and radiation-water preservation |

This **22.00t counterfactual package** falls **8.691t short** of the 20Tm Halo funding gap, even on paper. **ZERO t verified or credited**. Paired relational plant sections are **88t CANON HOLD**, not a candidate for the earlier hypothetical 9t discount. No requested saving changes ship mass until actual sizing laws and G1–G12 are satisfied.

The most valuable first experiment is **manifold ~90t pre-spread:** reconstruct coolant duty, pressure drop, line length/radius, pump and material mass. If it genuinely requires ~90t, eliminate its alleged 10t saving and move on. The Mc plant is not discountable merely because it is futuristic.

## Parked Track 2 material/thermal handoff (research-lab #151; zero credit)

- **Pressure vessel:** current 15.000t pre-spread / 15.356t geometry stays intact. Old strength-only 9.000/12.825/14.025t shell savings are inadmissible without fatigue, crack growth, leak-before-burst, puncture and pressure-life sizing. Lower/mid/upper *non-vessel* material sensitivities 20.347/35.152/44.737t are unqualified; credited saving **0t**.
- **Thermal manifold:** 90t source, ~92.133t geometry; heavy/reference/optimistic pumped-loop hypotheses 356.58/88.75/26.61t do not qualify mass credits. Compare pumped liquid circuits, heat pipes, liquid-metal options and hybrid layouts; the already-booked **4t hot-fin deployment/loop allowance** must not be counted twice. Credited saving **0t**.
- **Next sizing lines:** 5kg/m² strake radiator panel basis 8.784t and 1750K hot-fin panel/support basis 21.024t; ~46t torch shield, ~87t reactor, ~31t nozzle, ~57t electrical remain physical sizing questions. No arbitrary mass cuts.
- **Halo funding:** 10/15/20Tm at Je1000 need 14.258/22.247/30.691t of additional *verified* savings above the floor; presently **0t** qualified. Bobber v0.6 composites/Halo 15–20Tm remains a parked, non-canon paper option, not a live Wayfarer branch.
- **Relational plant:** two 44t source allocations are CANON-HOLD; **0t** plant savings eligible. No radiation-dose credit for OG-3, Halo or Lightfold.

## Hard holds

- No passive armour removal; no GCR dose discount for OG-3 or Halo; maintain shelter ZERO windows and 208 Metric faces.
- No cuts to habitat volume or 50t protected water; no new pressure-body, thermal, bay clearance or payload loss.
- Engineering reserve >=5t, combined uncommitted >=16.8t after any mass reallocation; WWS 12t NEW draw stays tracked separately.
- **No part has an earned saving yet.** This is an inventory plus first physically testable design question, not a canon redesign.
- Keep historical and proposed materials separate; kT decides merges.

