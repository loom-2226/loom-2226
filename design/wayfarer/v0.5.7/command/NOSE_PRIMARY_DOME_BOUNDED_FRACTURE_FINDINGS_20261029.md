# Wayfarer L1: one bounded primary pressure dome fracture challenge
**29 October 2026 | RESEARCH · NON-CANON · NON-RUNTIME · NOT A FRACTURE SIMULATION OR WINDOW QUALIFICATION**

## Authority, objective and strict scope

Bootstrapped live canonical source \`loom-2226/loom-2226\`: PR #432 remains OPEN at source head \`3485830a56dfead79b2ef8bba031a595b536fbb5\`. This report is isolated research branch work; PR432, Rev7, runtime, canon are unchanged.

**HOLD the 37 individually replaceable transparent protective exterior panels**, including their dimensions and angular positions. Keep original r3.5m inner pressure ellipsoid, 12cm axial separation to an independent seamless outer backup pressure dome, original hull/crew/sensors, and the already calculated **5.973cm smallest local normal free gap** between the two pressure shells. Both independently sealed inner pressure domes are still **nonqualified hypothetical 2226 structural glazing**. The sole question is whether this 6cm gap may prevent a failed primary shell piece from striking the backup before pressure redundancy develops.

Do not turn this task into a full fracture mechanics model, CFD, window qualification or ship design expansion.

## One explicit invented test event (not a predicted physical failure)

- Uniform 101.3kPa cabin pressure analogue; 293.15K air; initial cavity evacuated, isolated from exterior vacuum. Cavity ~**3.0227m³** from \`l1_nested_pressure_dome_failover.py\`.
- Sudden inner pressure-pane breach with **0.25m² effective open aperture**; discharge coefficient \`C_d=0.8\` purely assumed for the gas transfer model.
- Separately, a **0.25m² full-thickness slab fragment** from the primary shell, with nominal benchmark areal mass 85.2kg/m² → **21.3kg**, detaches at **zero** launch speed. Zero initial fracture/ejection velocity is an *optimistic* case, not evidence fragments move that slowly.
- The fragment is treated as moving normal toward the backup over the **shortest sampled 0.05973m gap**. This is an ideal hypothetical pane fragment, not a forecast of brittle crack morphology. It is not dynamically coupled to the assumed 0.25m² gas opening, and could in reality impede its flow.
- Cabin treated as a constant-pressure gas reservoir. Cavity is perfectly mixed, isothermal, uniform pressure and fixed volume; in the real first milliseconds it would contain jets, acoustic waves and local shocks.
- Flow follows compressible ideal-gas choked/subcritical isentropic orifice equations with \`γ=1.4, R=287.05J/(kg K)\`, solved at 10µs time steps. The pressure accelerates the intact fragment with \`a=(P_cabin−P_cavity)/85.2kg/m²\` until it touches backup. There is *no physical model for collision, pane reaction, rebound, ongoing fragment velocity or backup damage*.

## Executed numerical result

| Quantity | One-case toy result |
|---|---:|
| Primary fragment area and mass | **0.25 m² / 21.3 kg** |
| Smallest free normal gap | **5.973 cm** |
| Gap divided by air sound speed (NOT an arrival prediction) | **0.174 ms** |
| Initial choked inlet mass flow with assumed Cd and breach | **47.82 kg/s** |
| Contact if full 101.3kPa push remained constant | **10.02 ms**, 11.92m/s, 1,513J |
| Contact with well-mixed rising cavity pressure | **10.26 ms**, **11.37m/s**, **1,378J** |
| Mean mixed cavity pressure at contact | **13.65 kPa**, or ~13.5% of cabin pressure |
| Mixed cavity reaches 10% cabin pressure | **7.61 ms** |
| Mixed cavity reaches 50% cabin pressure | **38.04 ms** |
| Mixed cavity reaches 90% cabin pressure | **72.73 ms** |
| Mixed cavity reaches 99% cabin pressure | **89.08 ms** |

**Causal ordering:** The calculation of gap divided by air sound speed is ~0.17ms, **but the gap starts evacuated and sound does not propagate through vacuum**. The actual initial gas jet/expansion-front arrival requires compressible transient modelling and is NOT computed here. The simplified slab piece reaches the outer pressure dome at ~10ms, well before the globally mixed cavity reaches full differential pressure. Actual local jet impact/pressure waves could be much more intense and faster than the uniform pressure estimate. Equally, the real pane may crumble into smaller, less energetic fragments instead of one 21kg slab. **No meaningful survival probability follows from this model.**

**This is not an impact energy limit.** The ~1.38kJ arises from the one invented zero-launch fragment model with a diminishing ideal differential. Crack propagation, stored elastic energy in the curved shell, ejection velocity, gas-jet acceleration and impact obliquity can raise or lower real impact energy. There is no mechanical backup impact threshold specified, so the model cannot calculate pass/fail or a factor of safety.

Numerical convergence: rerun at 5, 10, 20µs steps; 10.25656, 10.25638, 10.25601ms contact time, and 1,377.58, 1,377.63, 1,377.73J contact energy. This agrees within ~0.0006ms/~0.2J across steps; the dominant uncertainty is **model assumptions**, not timestep.

## A scientific external comparator, not LOOM authority

NASA-STD-5018 with Change 1, real spacecraft window strength design, explicitly demands that a redundant pressure pane account for the dynamic effects of a primary failure and that failures not propagate through the window stack. See requirements **§4.8.1.1(c)** and **§4.8.3**. The standard's §4.4.3 uses a **minimum dynamic amplification factor 2.0** unless explicitly measured, and §4.4.4 adds a separate dynamic safety factor. These are **not direct peak-load predictions** for Wayfarer's unsupported giant transparent shell and are not invoked as governing LOOM rules:

- [NASA-STD-5018 w/Change 1, revalidated NASA standard](https://standards.nasa.gov/sites/default/files/standards/NASA/Baseline-w/CHANGE-1/1/nasa-std-5018_revalidated.pdf)
- [NASA Glenn: Mass Flow Choking](https://www.grc.nasa.gov/www/k-12/BGP/mflchk.html)
- [NASA analysis of compressible isentropic flows through an orifice](https://ntrs.nasa.gov/api/citations/20030007885/downloads/20030007885.pdf)

## Verdict and stopping condition

**The 12cm axial spacing, which yields only ~6cm free normal pressure-pane clearance at its worst location, CANNOT be claimed to protect the outer backup against primary fracture.** Even a deliberately optimistic large slab starting from rest can hit the backup with roughly **1.4kJ** on the bounded assumed event. This does **not** prove the backup fails, only that the **dynamic impact propagation hazard is physically credible** and must be solved before asserting genuine single-pane failure tolerance.

**No increase of gap, sacrificial membrane, hardware grid, mechanics architecture or canon design is automatically authorized.** The sensible next choice is scientific: determine whether some plausible 2226 transparent structural pressure system can avoid large detached shards or withstand their actual impact and transient load with an independently sealed intact backup. That requires a specific credible material/fracture/impact model; the scenario does not supply one. If we cannot ground such a material law, this remains a parked non-canon research constraint.

## Reproducibility

- \`command/l1_primary_fracture_one_case.py\` → \`command/l1_primary_fracture_one_case_results.json\` with exact assumptions, 1ms gas/fragment timeline, contact result, pressure thresholds, force calculations and explicit epistemic limitations.
- \`render/make_primary_fracture_timeline_viewer.py\` → \`render/out/nose_primary_fracture_timeline_viewer.html\`: offline touchscreen timeline of cavity fill and single idealized fragment motion until first contact; nothing beyond impact modeled.

**Source PR432, Rev7, canon and runtime unchanged.**
