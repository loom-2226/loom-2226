# LOOM Wayfarer L1: two independent, visually seamless pressure domes behind HELD 37 exterior protective tiles
**29 October 2026 · RESEARCH · NON-CANON · NON-RUNTIME · NON-GOVERNING · NOT QUALIFIED**

## Authority / scope / stopping condition

Live authority bootstrap: \`loom-2226/loom-2226\` PR #432 remains OPEN at source head \`3485830a56dfead79b2ef8bba031a595b536fbb5\`. This research is isolated on \`research/wayfarer-nose-l1-search-20261028\`. The chosen **37 individually replaceable outer protective glazing panels remain unchanged**, including their r0.75/2.0/2.75/3.5 rings, last staggered band, and nominal 10mm outer seams. No runtime, source Rev 7 design or canon mutation.

After \`NOSE_SEAMLESS_PRESSURE_DOME_MECHANICS_20261029.md\`, the narrow question is: can **two structurally independent, visually uninterrupted** transparent pressure domes fit *inside* the held outer panel shield, preserve the existing source pressure boundary and achieve steady-state **pressure containment after failure of either individual pressure shell**?

This experiment computes geometry, simple gas inventory, and quasi-static failure states, *not* a real window structural qualification.

## Exact model geometry

- Keep original pressure-head ellipsoid \`x_pressure(r)=2.35−2.15 sqrt(1−(r/4.3)²)\` as the mid-surface of the **inner primary** clear pressure shell to r=3.5m (7m aperture).
- Add an independent **outer backup clear pressure shell of exactly the same geometric shape**, shifted axially forward by \`d=0.06…0.25m\`. Its independent perimeter mounting at new x must connect to the same hull, but **not** rely on the other pane for its own structural load path.
- Keep original flat-to-r2m/50° angled **37-part replaceable outer protective skin** with its outside \`x=-1.2+max(0,r−2)tan(50°)\`. This protective skin does **not** hold cabin pressure.
- Reference inside shells use source earlier pressure-glazing mass allowance **85.2kg/m²** and fused-silica benchmark density **2210kg/m³** → each nominal shell normal thickness **38.55mm**; each shell mass **3.526t** over true curved area **41.383m²**. Two shells **7.052t**. These are *same-mass/density* illustrations, NOT qualified panel thicknesses.
- The exterior skin uses reference **270kg/m²** and transparent-ALON density benchmark 3670kg/m³ → **73.57mm** normal illustrative protection layer, which was never impact qualified. Its existing accounting mass is ~**14.28t**, assigned as replacement of opaque armour protection, **not automatically new ship mass**.
- Physical surfaces estimated by local shell-normal thickness converted to axial extent at each r; this is a first-order geometrical shell offset, **not detailed meshed intersections or actually packaged support hardware**.

## Executed spacing screen

| Axial offset of shell mid-surfaces | Minimum approximate *normal* free space between pressure shells | Minimum remaining axial gap from outer pressure shell to protective outer shell | Evacuated clear inter-pane cavity volume |
|---|---:|---:|---:|
| 0.06m | 1.06cm | 31.54cm | 0.714m³ |
| 0.08m | 2.70cm | 29.54cm | 1.483m³ |
| 0.10m | 4.33cm | 27.54cm | 2.253m³ |
| **0.12m reference** | **5.97cm** | **25.54cm** | **3.023m³** |
| 0.15m | 8.43cm | 22.54cm | 4.177m³ |
| 0.20m | 12.53cm | 17.54cm | 6.101m³ |
| 0.25m | 16.62cm | 12.54cm | 8.026m³ |

All have **positive gross cross-sectional axial clearance**, but are NOT proven installable as pressure-contained structural objects: two independently sealed flanges, ring reinforcement, gap access, accelerative deformation, actual protective-layer support and window inspection consume room. More spacing is not free: it puts the outer backup nearer the MMOD-protective 37 tiles. Exact normal clearance to the protective layer was not solved; the table measures sampled same-r axial clearance.

The empty cavity volume is computed from \`V=∫ 2πr [d−t_pressure sqrt(1+f'(r)^2)] dr\`; it is **not** the full mid-surface-to-mid-surface volume \`πr²d\`, since the pane solids occupy part of it. At \`d=0.12m\` volume **3.023m³**, containing **zero gas initially** if evacuated. If it fills quasi-statically to 101.3kPa at *illustrative* 293.15K with air gas constant 287.05J/kg/K, it receives ~**3.64kg** of air from the crew compartment. That is not necessarily lost to space; it moves into the now-pressurized inter-pane cavity. No cabin inventory or pressure transient modeled.

## Pressure logic: the important behavior

**Cavity initially evacuated, sealed and isolated from external vacuum.** A continuously open vent to vacuum would destroy the hoped-for backup after inner failure because cabin air could escape through it. Periodic evacuation via a positively isolated line is a plausible but **not implemented** concept. This aligns with real ISS window practice of evacuating the space between pressure panes (see references).

| Case | Cavity pressure after static settling | Pressure carried by inner primary | Pressure carried by outer backup | Outcome *if other pane+seals survive* |
|---|---:|---:|---:|---|
| Normal | 0kPa | 101.3kPa | 0kPa | Inner carries atmosphere |
| Inner primary fails | ~101.3kPa | failed | 101.3kPa | Outer backup contains cabin pressure |
| Outer backup fails | ~0kPa | 101.3kPa | failed | Inner maintains pressure |
| Both fail | undefined | failed | failed | No containment |

Axial outward resultant **F=pπr²=3.8985MN** per full-pressure shell. With quasi-static cavity gas pressure q, the inner differential is p−q, outer differential is q (external vacuum), so the pressure force splits as **(p−q)A + qA = pA**, NOT 7.8MN simultaneously. However **EACH** independent perimeter attachment must accept the full **3.90MN** axial resultant *alone* when that pane is active. The prior thin-shell membrane screen estimates a meridional force at the 3.5m edge of approximately **309kN per metre of ring**, with corresponding tangential/radial load components and *additional bending not modeled*.

**This is not proof of fail-safe behavior.** It demonstrates only two stable containment endpoints, conditional on each shell's own structural strength and flange/seal integrity. Dynamic fracture, cabin-to-cavity gas shock, flying fragments, failure propagation between close shells, pressure drop during cavity fill, acoustic impulse and event response time can cause *both* to fail, even if static equilibrium looks easy. NASA-STD-5018 (revalidated January 2026) specifically treats backup pane structural response after primary pane failure and discourages failure propagation. The standard is a **real-world reference**, not LOOM authority.

## Important epistemic distinction

The two pressure domes are not one chemically bonded composite of two plies. They must be **independently pressure-retaining assemblies**, with separate perimeter seals and load paths; otherwise they are one structural system with a common failure mode. Both may nonetheless be visually seamless because the supports are confined to their surrounding perimeter outside primary sightline region.

Neither panel is replaceable with the same ease as an outer 37 MMOD tile: replacing a pressure dome may require a temporary pressure cover, deliberate isolation and a large 7m part. This experiment does NOT invent an in-flight primary-window replacement system. The user has only required the **outer protective tiles** to be individually replaceable, which remains true.

## Verdict / stop condition

**Keep the 37 outer transparent protective panes HELD.** Adopt **12cm axial shell offset** as a narrow *research example*, not a proven optimum. It gives ~**6.0cm minimum normal empty gap** between pressure panes, ~**25.5cm sampled axial clearance** to the outer protected skin and a manageable ~**3.02m³** empty interspace, without altering the interior pressure-head shape. Static pressure role-switching after a single failed pane is internally coherent under assumed independent seals and ring supports.

**Do NOT promote to canon or claim pressure redundancy qualified.** We now know the concrete blocker: **a source-backed physical model of post-fracture dynamic failure propagation plus actual independent perimeter attachment/seal design for two large domes**. Anything more complete would need a demonstrated reason. Real-window flaw reliability, thermal gradients, interference, 2226 manufacture, MMOD joint protection and long-term optical transmission also remain unqualified but need not become broad new work here.

Next, if advancing this design again, the smallest worthwhile targeted question is: can the two domes survive the **primary fracture/failover impulse without the shards reaching or destroying the backup**, or is the 6cm normal gap inherently too small? Prefer one bounded fragment/pressure pulse case over a comprehensive window qualification model.

## Files

- \`command/l1_nested_pressure_dome_failover.py\` → \`command/l1_nested_pressure_dome_failover_results.json\`
- \`render/make_nested_pressure_failover_viewer.py\` → \`render/out/nose_nested_pressure_failover_viewer.html\` (offline HTML touchscreen comparison of spacing and normal/failure static cases)

## External references (not canon)

- [ESA, Cupola engineering](https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/Node-3_Cupola/Cupola): two pressure panes + dedicated debris pane, replaceable outer pane.
- [High performance windows for applications in space: Open problems and challenges (2025)](https://doi.org/10.1007/s40940-025-00309-z): ISS evacuated interpressure gap and primary/redundant distribution.
- [NASA-STD-5018 change1, 2026 revalidation](https://standards.nasa.gov/system/files/tmp/NASA-STD-2018_Revalidated%20-%2001-30-2026.pdf): pressure redundancy and dynamic backup load after pane break, failure propagation.

**No governing code, source PR, canon or runtime modifications.**
