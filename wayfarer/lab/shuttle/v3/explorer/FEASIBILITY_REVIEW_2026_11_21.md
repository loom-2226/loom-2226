# Explorer: feasibility answer to the 2026-11-21 review
ALL bodies. ALL sponsors. 2026-2226. Research/design exploration only; no canon, booking or requirement changes.

## The four questions

1. **Recompute one modified configuration without a sweep?** Yes. `engine.evaluate(params)` is self-contained: it rebuilds the geometry and runs every model for one design in ~0.42 s natively (measured on B5; the 3-D entry run is ~0.35 s of it).
2. **What is independently editable?** All 16 inputs (`ridge, shoulder_z, shoulder_y, keel, chine_z, belly_w, nose, base, wing, span, chord, fan_m2, floats_m3, water_t, seats, rover`). Geometry, mass, fan power, payload and every metric are derived inside `evaluate`, so nothing has to be regenerated outside it. Coupled rules: `wing=none` forces span 4.26 m and chord 0; `fold` caps span at 9 m; fan power is sized inside from landing mass; payload is set from couches.
3. **Smallest edit → recompute → compare loop:** run the *same* Python files in the page with Pyodide. The page's content-security policy allows `cdn.jsdelivr.net/pyodide`, and the model chain is pure numpy (engine, aero_test, build_v2b, variants, step2_propulsion, plus shuttle_inputs.json and b4s_mass.json as data). No server, no lookup table and no JavaScript rewrite of the physics. Expect a ~10–20 s first load on a phone and ~1–4 s per edit (estimate, to be measured). The precomputed population stays as the backdrop.
4. **Unsupported or weak metrics** (genuine findings, below).

## What the current numbers do not support

| Item | Status | What is wrong or missing |
|---|---|---|
| Bay fit | **Partial** | Checks only the stowed hull against r ≤ 2.15 m. Folded wings, fans, floats, the 3.8 m slot, the 90° roll and the G8 exit path are not checked. |
| Interior closure | Accounting only | One total-volume sum with assumed allocations (4.5 m³/couch, rover 11.5, door 5, aft 7, avionics 3, 0.04 m³/MW). There is no layout, and the 5 m³ door allowance is charged even with no rover. |
| Buoyancy | Volume only | No upright-stability (W6) check; floats are assumed 100% effective. |
| Fan power | Over-sized by assumption | Every fan design carries Venus-hover power whether or not it goes to Venus. |
| Water touchdown | **Assumed coefficient** | Blown-flap CL = min(4, CL₂₀ + 2.6 × MW/28): a straight line through one QSRA-class point. |
| Max turn | **Bug** | Above 272 m/s the formula drops the √(n²−1) term. Affects only fast cases. |
| Capability thresholds | Partly arbitrary | "Heavy ≤ 55 m/s" is not kT's rule (~50 m/s, 1 m waves); Venus "tank + 13 t" is an earlier estimate; "Titan hover" is just fans > 0; "Rover in core" is a configuration, not a capability. |
| Moon (vacuum kit) | Crude | Dry = core − wings − floats − fans − ½ TPS + 1.5 t, all assumed. |
| Pareto set | Mixed objectives | It includes the capability *count*, which the review rightly says should not rank designs. |
| Reproducibility | Missing | Results carry id and params but no model version or input hash. |
| Side effect | Bug | Importing step2_propulsion rewrites step2_propulsion.json in the current folder. |

## Kits and new families: what the existing models can carry

| Wanted | Can the v3 models do it? |
|---|---|
| Passenger, cargo, medical, survey, rover kits | Yes, as mass/volume/power accounting plus mission legs (`step2.water`). Kit masses and volumes would be **labelled assumptions**; there is no source data for them. Off-board storage goes against Wayfarer's hold (56.1 m³) and payload allowance, so the mass never disappears. |
| Orbital courier (no atmosphere gear) | Yes: drop wings, fans, floats and TPS from the accounting and run orbital legs. |
| Detachable wings or surfaces | Yes for aero (change wing area/span); attachment mass is an assumption. |
| Other hull families (lens, D-section, waverider, flying boat) | Yes: `shape_families.py` already uses the same aero functions. They need adding as a `family` input. |
| Fan, engine or RCS **placement** trades | **Blocked.** No centre-of-gravity, trim or stability model exists yet (planned for step 6). Placement cannot be judged without one. |
| Float arrangements | Volume only; stability blocked as above. |
| Split / two-body shuttle | **Blocked** for aero of the mated and separated shapes; needs new geometry and new entry cases. |

## Proposed next iteration (only after kT agrees)
1. `evaluate` returns margins: value, threshold, headroom, unit and evidence class (geometry/accounting, physics model, assumed coefficient, threshold), plus the first limiting constraint, a model version (git commit) and an input hash. Fix the two bugs.
2. Run `evaluate` in the page with Pyodide: select B5, edit any input, recompute, show margins.
3. Mission profiles as an editable assumptions file (passengers including crew, payload, legs, thresholds), defaulting to ASSUMPTION, never requirements; pin B5 + two designs and generate plain-language comparisons from the deltas.
4. Then kits as an accounting layer, and the `family` input. Placement trades wait for the step 6 balance model.
