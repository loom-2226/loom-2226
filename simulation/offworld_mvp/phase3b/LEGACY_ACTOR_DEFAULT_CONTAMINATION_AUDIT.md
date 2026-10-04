# Legacy Actor Default Contamination Audit

**Status:** PRE-CONTRACT / DESIGN HYGIENE AUDIT
**Scope:** `simulation/offworld_mvp/`
**Finding:** historical CIVPROP Australia/AUS default identified and quarantined.

## Finding

Current-main historical CIVPROP selected Australia (`AUS`) as the bounded actor for an Earth–Luna prospecting reference experiment. That selection had a legitimate experiment-specific basis: existing Earth identity plus scoped Australian lunar mission/access evidence.

The historical selection propagated into CIVPROP-0 inputs, the later input compiler, actor-state fixtures and regression baselines.

It is **not** authority for the new Offworld MVP to select Australia.

## Search audit

The Offworld MVP tree was searched for:

- Australia
- Australian
- AUS
- Roo-ver / ROO_VER
- Fleet Space
- SPIDER

Before this remediation, none of those legacy actor-specific terms appeared in the Offworld MVP tree. The contamination was conceptual: the historical default was being carried in design discussion rather than encoded in the new branch.

## Remediation

The FRD now declares the participating economy UNSELECTED at architecture level.

The Phase 3B State Model now carries an explicit legacy-actor-default firewall.

Future fixture selection must be deliberate and documented. Country-specific historical CIVPROP assumptions, budgets, capabilities, access evidence and mission evidence do not follow merely because a country is selected.

## Scope boundary

Historical CIVPROP files on main are not deleted or rewritten. They are legitimate archaeology/reference evidence and remain useful for regression lessons. This remediation prevents their experiment-specific actor choice from governing the new architecture.

## Test condition

Until an explicit fixture-selection record exists:

`participating_economy = UNSELECTED`

Any implementation or design artifact that silently substitutes `AUS` or another country fails this design condition.
