# FQ11-CALC | Metric Arrival Law v1 inverse-map preview

**LAB TOOLING / NON-CANON / NOT A FLIGHT QUALIFICATION.**

Input: `FQ11_INPUT.json`, main `32a4a45a`, geometry `4d598212…`. The separate `METRIC_LAB_CARD.json` is default off. Run `python wayfarer/lab/flight_qual/fq11_calc_metric_energy_b_20261101/run_fq11_calc.py`.

This solves backwards from Mars' target velocity and selects the exact mathematical pre-jump velocity. Thus arrival matching is an **IDENTITY BY CONSTRUCTION**, not a measured pass. The Sun E/p/L balancing accounts are also defined to close and are **IDENTITIES BY CONSTRUCTION**. The remass-budget calculation is the sole conditional computed check.

The ~4.828 km/s vector burn is ideal impulsive (~498 seconds only if later executed at the nominal CRUISE rate). No flightlab state-machine burn, steering/thermal/gravity integration, transit from a real burn end state, or finite trim is performed. The actual FQ11 must independently measure those behaviours.

**FROZEN-POTENTIAL CAVEAT:** approximate Sun-barycentric frame, Sun-only moving ephemeris and frozen Sun+planet endpoint potentials, not an exact Killing-energy or full N-body law. Sun exchange is the declared Metric miracle, not an independently established coupler. 0.5 Hill is a test boundary, not admissibility canon.

No Navigator, canon, or runtime authority changes.
