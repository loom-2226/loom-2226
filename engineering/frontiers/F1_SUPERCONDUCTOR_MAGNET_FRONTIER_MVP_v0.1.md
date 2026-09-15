# F1 — Superconductor / High-Field Magnet Frontier MVP v0.1

**Status:** HOSTILE-REVIEW SCAFFOLD / NOT FROZEN  
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
May inform field, structural, cryogenic, and specific-mass sensitivity.

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
12. structural stress/strain and protection regime where available.

## 2026 evidence anchors for the first pass

These anchors establish categories, not a fitted 2226 answer.

- National MagLab reports a **32 T all-superconducting magnet**, successfully tested in 2017 and later opened for user science. This is a relevant continuous superconducting-system anchor.
- National MagLab's **45 T hybrid** combines an 11.5 T superconducting outsert with a 33.5 T resistive insert. Its published facility specifications include a 32 mm bore and approximately 30 MW power requirement. It is a continuous-field anchor but **not** like-for-like with an all-superconducting spacecraft magnet.
- National MagLab reports a **100 T nondestructive pulsed magnet**. This is useful for physical/engineering context but must not be pooled with continuous operation.
- National MagLab's all-superconducting **40 T development program** targets a 34 mm bore. Recent large-scale REBCO coil testing is evidence of a development trajectory, not a demonstrated 40 T operational baseline.

## The rejected naive extrapolation

A three-point historical fit using approximately 8.3 T, 11.8 T, and 20 T milestones and naively extending an exponential to 2226 produced roughly 4,776 T in an exploratory calculation.

Disposition: **REJECT AS DOWNSTREAM AUTHORITY.**

Reason: the forecast horizon is many times the fitted observation window; the observations are not demonstrated to be like-for-like system metrics; no hindcast was performed; no uncertainty distribution was retained; and no coupled physical/system constraints were applied.

The absurd raw result is useful only as a regression test: the Frontier Protocol must prevent such a value from silently becoming canon.

## The 375 T conditional-bound experiment

Characteristic magnetic pressure is

`P_B = B^2 / (2 mu0)`.

At 375 T, this characteristic pressure is approximately 56 GPa.

The exploratory calculation assumed a future structural budget of approximately 56 GPa and solved the above expression backward for field. That future strength budget was based on an 8x multiplier over an assumed modern ~7 GPa practical reference.

Disposition: **CONDITIONAL_UPPER_BOUND_EXPERIMENT_ONLY**.

It is not yet accepted because:

- the 8x structural multiplier has not been earned;
- characteristic magnetic pressure is not by itself a complete magnet stress solution;
- bore/geometry matter;
- conductor critical surface and engineering current density matter;
- reinforcement and insulation consume mass/volume;
- stored energy and quench/protection matter;
- cryogenic burden matters;
- radiation/lifetime may matter for Wayfarer consumers;
- the installed system must fit mass and geometry budgets simultaneously.

## Required F1 computational work before freeze

### Data pass
Build a cited dataset with operating-class labels. Do not silently mix all-superconducting, hybrid, resistive, and pulsed systems.

### Forecast pass
Where data support it, fit multiple plausible trends and perform hindcasting. Preserve model disagreement and widening uncertainty. If the data are too sparse for a defensible statistical extrapolation, say so and use bounded scenario construction rather than fake statistics.

### Physics pass
At minimum represent:

- `B` and useful bore/aperture;
- conductor `Jc(B,T,strain)` or a defensible engineering-current-density envelope;
- magnetic stress/structural constraint;
- reinforcement fraction / installed mass;
- stored magnetic energy;
- quench/protection burden;
- operating temperature / cryogenic burden;
- operating margin and duty cycle.

### Joint satisfiability pass
Use exact/analytic checks for simple constraints and Z3 when the multidimensional envelope becomes genuinely coupled.

The relevant SMT question is not `B <= arbitrary_cap`. It is whether there exists at least one state satisfying the required field/bore, conductor, structure, mass, protection, thermal, geometry, margin, and duty constraints simultaneously.

`SAT` means the encoded assumptions admit a solution. It does not certify a component. `UNSAT` means at least one ambition/assumption set is mutually incompatible and should be diagnosed rather than patched with an invented parameter.

## Provisional output fields

Until the work above is complete:

- `loom_2226_mvp_large_continuous_field = UNSET`
- `aggressive_2226_large_continuous_field = UNSET`
- `conditional_upper_bound = 375 T EXPERIMENT / NOT AUTHORITY`
- `component_hardware_certified = false`
- `new_physics_required_by_frontier = false`
- `review_status = HOSTILE_REVIEW_REQUIRED`

No consumer may substitute 50 T, 75 T, 100 T, 375 T, or any other conversational placeholder as F1 authority until the frontier is frozen through governed process.

## Hostile review request for Claude

Review this protocol and F1 scaffold as an adversarial engineering-methodology reviewer.

Find:

- miracle-smuggling;
- category errors;
- unjustified extrapolation;
- double-counting of technological progress;
- inappropriate or incomparable datasets;
- weak or mislabeled physical caps;
- arbitrary system derating;
- false precision;
- hidden preferred outcomes;
- any place where `DERIVED_ENGINEERING_ENVELOPE` can masquerade as `2226_FACT`;
- any place where improved materials could accidentally launder an unknown physical mechanism into validity.

Separately assess whether the protocol is conservative enough for a 200-year horizon while still allowing genuine technological progress.

Do **not** substitute a preferred numerical answer merely because an output looks too high or too low. Identify the failed assumption, dataset, model, bound, or constraint.

For F1 specifically, determine whether the proposed data categories compare like with like, whether a meaningful hindcast can be built from available evidence, what minimum coupled constraints are required before a field value can become downstream authority, and whether the 375 T experiment is correctly demoted to a conditional non-authoritative bound.

Return one disposition: `ACCEPT`, `ACCEPT_WITH_CONDITIONS`, or `REVISE`. Tie every condition to a specific methodological defect and identify the smallest corrective action.

## References

1. Nagy, B.; Farmer, J. D.; Bui, Q. M.; Trancik, J. E. (2013), **Statistical Basis for Predicting Technological Progress**, PLOS ONE 8(2): e52669. https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0052669
2. National High Magnetic Field Laboratory, **Magnet Projects**. https://nationalmaglab.org/magnet-development/magnet-projects/
3. National High Magnetic Field Laboratory, **World's Strongest Superconducting Magnet Open for Science** (32 T all-superconducting system). https://nationalmaglab.org/news-events/news/world-s-strongest-superconducting-magnet-open-for-science/
4. National High Magnetic Field Laboratory, **45 Tesla, 32 mm Bore Hybrid Magnet (Cell 15)**. https://nationalmaglab.org/user-facilities/dc-field/magnets-instruments/hybrid-magnets/45-tesla-cell-15/
5. National High Magnetic Field Laboratory, **40-tesla Superconducting Magnet**. https://nationalmaglab.org/magnet-development/magnet-projects/40-tesla-superconducting-magnet/
6. National High Magnetic Field Laboratory, **Successful Test of Key Superconducting Coil for Future 40-Tesla Magnet**. https://nationalmaglab.org/magnet-development/magnet-science-technology/research/science-highlights/testing-of-a-large-scale-rebco-coil/
7. NASA, **Systems Engineering Handbook — Appendix**. https://www.nasa.gov/reference/system-engineering-handbook-appendix/
