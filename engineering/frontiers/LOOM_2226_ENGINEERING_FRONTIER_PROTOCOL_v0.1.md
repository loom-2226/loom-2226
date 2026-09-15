# LOOM 2226 Engineering Frontier Protocol v0.1

**Status:** MVP / HOSTILE-REVIEW CONDITIONS DISPOSITIONED  
**Class:** ENGINEERING METHODOLOGY  
**Authority:** DERIVED DESIGN ENVELOPES ONLY  
**Target epoch:** 2226  
**Prediction claim:** NONE

## Purpose

Provide one repeatable way to answer: **what can two centuries of ordinary engineering plausibly buy LOOM without silently introducing new physics?**

The protocol exists to create bounded engineering design envelopes for technologies consumed by LOOM systems. It does not establish future historical fact, certify components, or repair an unresolved physical mechanism.

## Epistemic firewall

- `INTERESTING_TREND != 2226_FACT`
- `RECORD_MATERIAL_PROPERTY != INSTALLED_SYSTEM_CAPABILITY`
- `EMPIRICAL_EXTRAPOLATION != PHYSICAL_PERMISSION`
- `PHYSICAL_PERMISSION != ENGINEERING_FEASIBILITY`
- `ENGINEERING_ENVELOPE != COMPONENT_CERTIFICATION`
- `BETTER_MATERIALS != NEW_PHYSICS`
- `CONDITIONAL_UPPER_BOUND != DOWNSTREAM_AUTHORITY`

A frontier may narrow or retire a hold only when the hold concerns achievable component/material performance. It may **not** retire a hold for an unknown mechanism, missing conservation closure, unknown momentum partner, or unearned constitutive physics.

## Required pipeline

Every frontier shall preserve this provenance chain:

`OBSERVED -> TREND -> HINDCAST -> EXTRAPOLATED_DISTRIBUTION -> PHYSICS_BOUNDS -> SYSTEM_DERATING -> LOOM_2226_MVP -> AGGRESSIVE_ENVELOPE -> CONSUMER`

### 1. OBSERVED
Use cited real measurements. Prefer demonstrated system performance under stated conditions. Material coupons, record samples, pulsed systems, small-bore systems, hybrid systems, and continuous large systems must not be silently pooled as equivalent observations.

### 2. TREND
Where data permit, fit more than one plausible empirical model. Time-based exponential improvement and experience/production-based learning are candidates, not default truths. A model family must be appropriate to the metric being forecast.

### 3. HINDCAST
Withhold historical observations and test whether the proposed model can predict them. Report errors. A model that cannot survive its own historical record does not earn a 2226 projection.

**Minimum-data rule:** quantitative hindcasting requires at least **6 independent like-for-like historical observations**, leaving enough information for at least 3 fit observations and 3 genuinely withheld validation observations in a simple holdout design. A frontier may use more rigorous time-ordered cross-validation when the dataset supports it. Fewer than 6 like-for-like observations shall be classified `INSUFFICIENT_FOR_QUANTITATIVE_HINDCAST`; the frontier must use bounded scenario construction instead of presenting a fitted long-horizon forecast as validated. Six observations are a minimum admissibility floor, not evidence that a model is strong.

This follows the general discipline demonstrated by Nagy, Farmer, Bui, and Trancik (2013), who compared six technological forecasting laws over 62 technology datasets using hindcasting/cross-validation and found forecast error increases with horizon.

### 4. EXTRAPOLATED DISTRIBUTION
Do not report a 200-year extrapolation as a point prediction. Preserve uncertainty and model disagreement. Raw extrapolations may be retained diagnostically even when absurd; they do not become authority.

**Model-disagreement rule:** after hindcast/admissibility screening and application of physical/system constraints, `loom_2226_mvp` defaults to the **most conservative surviving candidate envelope** for the consumer metric. A less conservative candidate may be selected only with an explicit, reviewable justification tied to evidence or model applicability; convenience or desired consumer performance is not justification. The aggressive envelope must remain separately labeled.

### 5. PHYSICS BOUNDS
Apply relevant known-theory constraints independently of the empirical trend: conservation, thermodynamics, magnetic pressure, stress, Stefan-Boltzmann radiation, electrochemistry, radiation damage, critical surfaces, etc. A bound must state its assumptions.

**All-applicable-bounds rule:** when multiple independent physical bounds apply, all identified applicable bounds must be evaluated. The permitted frontier envelope is constrained by the most restrictive applicable bound or coupled combination of bounds. A frontier may not stop after finding one permissive bound. Any bound not evaluated must be listed as unresolved and prevents claims that the physical constraint set is closed.

A bound derived from a future material assumption is a **conditional engineering bound**, not a fundamental physics limit.

### 6. SYSTEM DERATING
Translate material/device performance into installed-system performance. Include the burdens that make the consumer real: structure, reinforcement, insulation, cooling, shielding, control, protection, margins, geometry, lifetime, duty cycle, radiation/fluence environment where relevant, and balance-of-plant where applicable.

NASA systems-engineering practice provides useful precedent for keeping technology maturity and demonstrated relevant-environment capability separate from aspirational system integration.

### 7. LOOM_2226_MVP
The conservative value or multidimensional envelope permitted for normal downstream LOOM engineering. It is a design scenario, not a prediction of actual 2226 history.

### 8. AGGRESSIVE_ENVELOPE
A more demanding but still known-physics-compatible sensitivity/research case. It must never silently replace the MVP value in a consumer.

### 9. CONSUMER
Each frontier names the LOOM holds/interfaces it informs. Producer capability is derived once and reused. Consumers may not independently invent more favorable versions of the same technology.

Every frozen frontier shall expose a machine-checkable `producer_version_hash` identifying the exact governed frontier artifact/version. A consumer claiming use of a frontier value must record that hash. If the producer hash changes, the consumer is stale until explicitly revalidated. This provenance edge does not by itself prove that double counting is absent, but makes producer reuse and dependency drift machine-detectable.

## Mandatory rules

1. **Consumer driven.** Every frontier must name at least one existing LOOM engineering consumer or hold.
2. **Real baseline.** Every quantitative frontier begins with cited observations.
3. **Like with like.** Distinct operating classes are separated unless an explicit normalization justifies comparison.
4. **No preferred curve.** Compare plausible models where the evidence permits.
5. **Hindcast first, or admit insufficiency.** Historical predictive failure blocks long-horizon authority; fewer than 6 independent like-for-like observations blocks quantitative-hindcast claims and triggers bounded scenario construction.
6. **Horizon uncertainty.** Uncertainty must expand rather than disappear over a 200-year horizon.
7. **Physics wins collectively.** All identified applicable physical bounds must be evaluated; the tightest individual or coupled constraint governs.
8. **System performance wins.** Record material/device performance cannot be directly assigned to installed spacecraft hardware.
9. **No perfection.** No 100% efficiency, zero mass, infinite life, perfect insulation, zero entropy production, or similar asymptote may be promoted as an engineering value.
10. **No double counting.** A materials improvement used to derive a subsystem improvement cannot be applied again as an independent multiplier to the same causal benefit.
11. **One producer, many consumers.** Shared technology frontiers are reused across torch, fusion, E2, thermal, RCS, or other consumers.
12. **No mechanism laundering.** Better engineering cannot make an unearned physical mechanism valid.
13. **Provenance survives.** Every downstream value remains traceable to observations, model, bounds, derating, assumptions, and exact `producer_version_hash`.
14. **False precision prohibited.** Output precision shall reflect evidence and model uncertainty.
15. **Conservative disagreement resolution.** Unless a reviewed applicability argument says otherwise, the MVP uses the most conservative surviving candidate after model screening and physical/system filtering.

## Computational roles

### Python / NumPy
Used for datasets, fits, uncertainty propagation, hindcasting, sensitivity sweeps, and deterministic accounting.

### Exact Python / analytic checks
Used where exact identities, dimensional accounting, or simple inequalities are sufficient.

### Z3 / SMT
Z3 is not required to prove that one scalar is below one cap. It becomes useful when multiple independently derived constraints must be simultaneously satisfiable.

For example, a future magnet envelope may require simultaneous satisfaction of field, bore, conductor critical surface, structural stress, installed mass, stored-energy protection, thermal burden, radiation/fluence lifetime, operating margin, geometry, and duty-cycle constraints. `SAT` establishes only that the encoded envelope has at least one mutually consistent state. `UNSAT` identifies incompatible ambitions/assumptions. Neither result certifies hardware or unknown physics.

## Frontier output schema

Each frontier should report at minimum:

- `frontier_id`
- `frontier_version`
- `producer_version_hash`
- `metric_semantics`
- `baseline_year`
- `target_year`
- `observations[]` with source and operating class
- `candidate_models[]`
- `hindcast_status`
- `hindcast_results[]`
- `raw_projection` or distribution
- `physical_constraints[]`
- `unevaluated_physical_constraints[]`
- `conditional_bounds[]`
- `system_derating[]`
- `loom_2226_mvp`
- `mvp_selection_basis`
- `aggressive_envelope`
- `consumers[]`
- `holds_narrowed[]`
- `holds_not_narrowed[]`
- `authority`
- `uncertainties[]`
- `review_status`

## Initial frontier sequence

F1 is superconducting/high-field magnet engineering because the same producer capability informs the Wayfarer torch magnetic nozzle, fusion-confinement engineering, and E2 external-field/plasma momentum-coupling candidates.

Later frontiers may include high-temperature structural materials, heat rejection, power conversion/storage, working-fluid/cryo systems, and radiation-damage-resistant materials. They are not automatically authorized by this protocol; each must earn its own evidence chain.

## Hostile-review disposition — 2026-09-16

External hostile review returned `ACCEPT_WITH_CONDITIONS`. Five conditions were accepted and incorporated: all applicable physical bounds; a protocol-level minimum-N rule for quantitative hindcasting; conservative model-disagreement resolution; radiation/fluence as a relevant system axis; and machine-checkable producer provenance. The reviewer also correctly identified false precision in the exploratory 375 T calculation; that value remains non-authoritative.

## References

1. Nagy, B.; Farmer, J. D.; Bui, Q. M.; Trancik, J. E. (2013), **Statistical Basis for Predicting Technological Progress**, PLOS ONE 8(2): e52669. DOI: 10.1371/journal.pone.0052669. https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0052669
2. NASA, **Systems Engineering Handbook — Appendix**, technology assessment/readiness definitions and relevant-environment maturity guidance. https://www.nasa.gov/reference/system-engineering-handbook-appendix/
3. National High Magnetic Field Laboratory, **Magnet Projects**, demonstrated 32 T all-superconducting, 45 T hybrid, 60 T controlled-waveform, and 100 T nondestructive pulsed systems. https://nationalmaglab.org/magnet-development/magnet-projects/
4. National High Magnetic Field Laboratory, **40-tesla Superconducting Magnet**, 34-mm-bore all-superconducting development target and HTS design context. https://nationalmaglab.org/magnet-development/magnet-projects/40-tesla-superconducting-magnet/
