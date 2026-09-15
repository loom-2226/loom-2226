# F1 — Superconductor / High-Field Magnet Frontier MVP v0.1

**Status:** HOSTILE REVIEW CONDITIONS INCORPORATED / NUMERICAL ENVELOPE NOT FROZEN  
**Protocol:** `LOOM_2226_ENGINEERING_FRONTIER_PROTOCOL_v0.1`  
**Authority:** DERIVED ENGINEERING ENVELOPE — PENDING DATA/FIT/COUPLED-CONSTRAINT PASS  
**Target epoch:** 2226

## BLUF

LOOM does **not** currently authorize a 375 T Wayfarer magnet.

The previously explored ~375 T value is retained only as a **conditional single-constraint stress-bound experiment**. It resulted from equating characteristic magnetic pressure `B^2/(2 mu0)` to an assumed future ~56 GPa structural-strength budget. The ~56 GPa value itself came from an unearned 8x multiplier on an assumed ~7 GPa modern practical reference. Therefore 375 T is not a physics constant, not a forecast, and not downstream engineering authority.

F1 exists to replace that shortcut with a multidimensional system envelope.

## Consumers

### Wayfarer E1 torch
May inform magnetic-nozzle field/mass sensitivity and related integration requirements.

**May not close:** magnetic-nozzle plasma physics, detachment, divergence, interception, erosion, or lifetime merely because a stronger magnet becomes feasible.

### Fusion source / confinement
May inform field, structural, cryogenic, radiation-lifetime, and specific-mass sensitivity.

**May not close:** `SOURCE_REACTOR_REALIZABILITY` or fusion gain/source physics by materials extrapolation alone.

### E2 momentum-coupled propulsion
May inform field/mass ceilings for candidates with an explicit external momentum partner, such as external plasma/charged-particle interaction.

**May not close:** momentum conservation, coupling mechanism, environmental availability, thrust scaling, or an undefined momentum sink.

## Metric semantics

F1 must not collapse all magnet records into a single `tesla vs year` series. At minimum distinguish:

1. continuous all-superconducting system field;
2. continuous hybrid/resistive field;
3. pulsed nondestructive field;
4. bore/aperture;
5. operating temperature;
6. conductor/material class;
7. engineering current density vs conductor-layer/material critical-current density;
8. stored energy;
9. installed magnet/system mass where available;
10. cryogenic/electrical burden;
11. duty cycle;
12. structural stress/strain and protection regime where available;
13. radiation/fluence tolerance and lifetime in the relevant consumer environment.

## 2026 evidence anchors for the first pass

These anchors establish categories, not a fitted 2226 answer.

- National MagLab reports a **32 T all-superconducting magnet**, successfully tested in 2017 and later opened for user science. This is a relevant continuous superconducting-system anchor.
- National MagLab's **45 T hybrid** combines an 11.5 T superconducting outsert with a 33.5 T resistive insert. Its published facility specifications include a 32 mm bore and approximately 30 MW power requirement. It is a continuous-field anchor but **not** like-for-like with an all-superconducting spacecraft magnet.
- National MagLab reports a **100 T nondestructive pulsed magnet**. This is useful for physical/engineering context but must not be pooled with continuous operation.
- National MagLab's all-superconducting **40 T development program** targets a 34 mm bore. Recent large-scale REBCO coil testing is evidence of a development trajectory, not a demonstrated 40 T operational baseline.

## The rejected naive extrapolation

A three-point historical fit using approximately 8.3 T, 11.8 T, and 20 T milestones and naively extending an exponential to 2226 produced roughly 4,776 T in an exploratory calculation.

Disposition: **REJECT AS DOWNSTREAM AUTHORITY.**

Reason: the forecast horizon is many times the fitted observation window; the observations are not demonstrated to be like-for-like system metrics; three points fail the protocol's minimum-N rule for quantitative hindcasting; no uncertainty distribution was retained; and no coupled physical/system constraints were applied.

The absurd raw result is useful only as a regression test: the Frontier Protocol must prevent such a value from silently becoming canon.

## The 375 T conditional-bound experiment

Characteristic magnetic pressure is

`P_B = B^2 / (2 mu0)`.

At roughly 375 T, this characteristic pressure is roughly 56 GPa. Precision beyond that is unsupported by the assumptions.

The exploratory calculation assumed a future structural budget of approximately 56 GPa and solved the above expression backward for field. That future strength budget was based on an unearned 8x multiplier over an assumed modern ~7 GPa practical reference.

Disposition: **CONDITIONAL_UPPER_BOUND_EXPERIMENT_ONLY**.

It is not accepted because:

- the 8x structural multiplier has not been earned;
- characteristic magnetic pressure is not by itself a complete magnet stress solution;
- it is only one candidate constraint and the protocol now requires all applicable bounds;
- bore/geometry matter;
- conductor critical surface and engineering current density matter;
- reinforcement and insulation consume mass/volume;
- stored energy and quench/protection matter;
- cryogenic burden matters;
- radiation/fluence lifetime matters for relevant Wayfarer consumers;
- the installed system must fit mass and geometry budgets simultaneously.

## Required F1 computational work before freeze

### Data pass
Build a cited dataset with operating-class labels. Do not silently mix all-superconducting, hybrid, resistive, and pulsed systems.

### Forecast pass
Where data support it, fit multiple plausible trends and perform hindcasting. Quantitative hindcasting requires at least 6 independent like-for-like observations under the protocol. If F1 cannot assemble that minimum for a given operating class, classify it `INSUFFICIENT_FOR_QUANTITATIVE_HINDCAST` and use bounded scenario construction instead of fake statistical validation.

Preserve model disagreement and widening uncertainty. After admissibility/hindcast and physical/system filtering, the MVP defaults to the most conservative surviving candidate unless a reviewed applicability argument supports another choice.

### Physics pass
At minimum represent and evaluate every applicable constraint among:

- `B` and useful bore/aperture;
- conductor `Jc(B,T,strain)` or a defensible engineering-current-density envelope;
- magnetic stress/structural constraint;
- reinforcement fraction / installed mass;
- stored magnetic energy;
- quench/protection burden and thermal-runaway constraints;
- operating temperature / cryogenic power burden;
- radiation/fluence tolerance and lifetime for the consumer environment;
- operating margin and duty cycle.

The most restrictive applicable individual or coupled bound governs. Any identified bound that cannot yet be evaluated must remain explicit and prevents the physical constraint set from being called closed.

### Joint satisfiability pass
Use exact/analytic checks for simple constraints and Z3 when the multidimensional envelope becomes genuinely coupled.

The relevant SMT question is not `B <= arbitrary_cap`. It is whether there exists at least one state satisfying the required field/bore, conductor, structure, mass, protection, thermal, radiation/lifetime, geometry, margin, and duty constraints simultaneously.

`SAT` means the encoded assumptions admit a solution. It does not certify a component. `UNSAT` means at least one ambition/assumption set is mutually incompatible and should be diagnosed rather than patched with an invented parameter.

## Provisional output fields

Until the work above is complete:

- `frontier_version = v0.1`
- `producer_version_hash = PENDING_FREEZE`
- `hindcast_status = PENDING_DATA`
- `loom_2226_mvp_large_continuous_field = UNSET`
- `mvp_selection_basis = UNSET`
- `aggressive_2226_large_continuous_field = UNSET`
- `conditional_upper_bound = ~375 T EXPERIMENT / NOT AUTHORITY`
- `component_hardware_certified = false`
- `new_physics_required_by_frontier = false`
- `review_status = ACCEPT_WITH_CONDITIONS / CONDITIONS INCORPORATED`

On freeze, `producer_version_hash` must identify the exact governed F1 artifact/version. Any consumer using F1 must pin that hash and revalidate if it changes.

No consumer may substitute 50 T, 75 T, 100 T, ~375 T, or any other conversational placeholder as F1 authority until the frontier is frozen through governed process.

## Hostile review disposition — 2026-09-16

Review disposition: **ACCEPT_WITH_CONDITIONS**.

All five requested corrections are incorporated in this revision:

1. all applicable independent physics bounds must be evaluated, with the tightest individual/coupled constraint governing;
2. quantitative hindcasting now has a protocol-level minimum of 6 independent like-for-like observations; sparse classes fall back to bounded scenario construction;
3. model disagreement resolves conservatively by default after screening/filtering;
4. radiation/fluence tolerance is a required F1 metric and physics/system consideration for relevant consumers;
5. frozen producer artifacts expose `producer_version_hash`, which consumers must pin for machine-detectable provenance and revalidation.

The reviewer's false-precision criticism is also incorporated: the stress-only experiment is expressed only as approximately 375 T / approximately 56 GPa, and remains non-authoritative.

## References

1. Nagy, B.; Farmer, J. D.; Bui, Q. M.; Trancik, J. E. (2013), **Statistical Basis for Predicting Technological Progress**, PLOS ONE 8(2): e52669. https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0052669
2. National High Magnetic Field Laboratory, **Magnet Projects**. https://nationalmaglab.org/magnet-development/magnet-projects/
3. National High Magnetic Field Laboratory, **World's Strongest Superconducting Magnet Open for Science** (32 T all-superconducting system). https://nationalmaglab.org/news-events/news/world-s-strongest-superconducting-magnet-open-for-science/
4. National High Magnetic Field Laboratory, **45 Tesla, 32 mm Bore Hybrid Magnet (Cell 15)**. https://nationalmaglab.org/user-facilities/dc-field/magnets-instruments/hybrid-magnets/45-tesla-cell-15/
5. National High Magnetic Field Laboratory, **40-tesla Superconducting Magnet**. https://nationalmaglab.org/magnet-development/magnet-projects/40-tesla-superconducting-magnet/
6. National High Magnetic Field Laboratory, **Successful Test of Key Superconducting Coil for Future 40-Tesla Magnet**. https://nationalmaglab.org/magnet-development/magnet-science-technology/research/science-highlights/testing-of-a-large-scale-rebco-coil/
7. NASA, **Systems Engineering Handbook — Appendix**. https://www.nasa.gov/reference/system-engineering-handbook-appendix/
