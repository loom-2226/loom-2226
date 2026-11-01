# FQ11 | Earth → Mars Metric Arrival Law v1 | 2026-11-01

**LAB ONLY, NON-CANON, NOT NAVIGATOR.** Baseline main `32a4a45a4f55007bbc5162d19438cd2ffd8300fe`; Wayfarer geometry `4d598212aeb46fab14b326a6023bb6d55e7d584599d91fe821ef8a2f2d837331`.

Input snapshot: `FQ11_INPUT.json`, JPL J2000 source epoch 2226-08-29. `METRIC_LAB_CARD.json` is **default off** and inherits the existing canonical NORMAL timing card. `run_fq11.py` invokes the existing `flightlab.run` through the explicit `enable_metric_arrival_law_v1=true` option. It never changes the canonical HOLD or other cases. Output: `FQ11_RESULT.json`.

Sequence: paid ideal impulsive CRUISE vector preburn; NORMAL Metric transit with **moving Mars** (Sun-only two-body propagation, no ordinary-space metric path); orbit-relative B arrival with ENERGY speed; match Mars' arrival velocity within **1 m/s**. Wayfarer remass floor **5 t**.

The output checks remass closure, velocity matching, and separate **E/p/L algebraic ledgers** for ideal torch and Metric. The Sun receives the opposing Metric impulse and the complete angular change, split into `−r_depart×Δp` and `−(r_arrive−r_depart)×p_arrive`. The large split terms partly cancel; the output gives each and the resulting magnitude. Reference lever arms are **planet-center Sun vectors**, not a resolved collapse location/torque-distribution geometry. The solar spin/orbit and field-work accounts are **declared Metric-miracle bookkeeping**, not independent physical derivation or qualification. Torch source-energy accounting is likewise idealized.

**FROZEN-POTENTIAL CAVEAT:** there is no exact global Killing energy for moving planets; Sun-only motion, approximate Sun-barycentric speeds and static endpoint potentials are assumptions. **MONITOR:** Step 4's ~1.5 m/s equivalent return residual at 30 km/s follows a ~264 MJ/kg paid seed; later test phase-sweep **sign and bound** (not part of FQ11).

### Repeat

```bash
PYTHONDONTWRITEBYTECODE=1 python wayfarer/lab/flight_qual/fq11_metric_energy_b_20261101/run_fq11.py
```

Original FQ1–FQ10 source and results are untouched. No Navigator or canon changes. FQ11's numeric PASS does **not** qualify the Metric miracle, real torch burn, actual mission trajectory, orbital capture, or a real Sun E/p/L interaction.
