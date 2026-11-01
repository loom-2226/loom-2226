# Wayfarer L1: frameless inner transparent pressure dome, mechanics screen
**29 October 2026 — RESEARCH / NON-CANON / NON-RUNTIME / NON-GOVERNING / NOT QUALIFIED**

## Authority / question

Bootstrapped live \`loom-2226/loom-2226\` PR #432: still **open** at governing source head \`3485830a56dfead79b2ef8bba031a595b536fbb5\`. The selected **37 individually replaceable outer protective glass panels** are held exactly as in \`staggered_trapezoids_compact_12\`. This experiment does not edit governing source, runtime, Rev7, or any outer pane geometry.

The question is NOT whether glass can hold pressure in general. It is whether Wayfarer's **existing ellipsoidal pressure-head shape**, within the r=3.5m glazed crown, could plausibly become **one optically continuous transparent shell supported solely at its perimeter** without any internal metal mullions or inner circular-frame ring.

The preceding viewshed test already sampled this **rim-only no-inner-frame upper bound**, with exactly the held 37 outer protective tiles: from actual Pilot and Navigator stations, **78.61% / 78.66%** sampled visible forward hemisphere (4096 rays per station), versus **72.53% / 72.63%** with the 80mm x 8 frame. Those are **straight-ray geometric scores** and not refracted optical image quality. This task assesses mechanical plausibility rather than rerunning the same sky rays.

## Source geometry and assumed loads

- Authoritative input file \`design/wayfarer/v0.5.7/inputs/wayfarer_v05_inputs.json\`: pressure ellipsoid transverse equatorial radius **4.3m**, axial nose depth **2.15m**, forward pressure apex near x=0.20m; outward x(r) = **2.35 − 2.15 sqrt(1 − (r/4.3)^2)**. Inner transparent radius **3.5m** (diameter **7m**), **shape unchanged**.
- True surface area (integrated) **41.3833m²**; projected circular opening area **38.4845m²**.
- Applied uniform pressure **101.3kPa**. This value exists in source **L4/L5 isolation**, NOT as an independently verified L1 pressure design setpoint. Used here as a plausible reference cabin pressure case, not source authority for L1.
- Integrated axial outward pressure resultant on dome **3.89848MN**, entirely transferred through shell/perimeter ring and its connection to the pressure vessel. The ring circumference at r=3.5m is **21.991m**.
- Source pressure-glazing crown subtotal **2.13t panes over ~25m²** of prior crown; naively scaling its **85.2kg/m²** ratio to this 41.383m² means **3.526t nominal transparent material**. This is a budget sensitivity, NOT approved mass for a seven-metre pressure dome or definite count of pressure-pane layers.
- The source crew acceleration doctrine gives **sustained 4g cap**; as a simple normal-direction inertial traction **85.2kg/m² × 4 × 9.80665m/s² ≈ 3.34kPa**, ~3.3% of 101.3kPa cabin pressure. This is *not* a complete vessel acceleration strength case: tangential mass loading, attachment, dynamic and abnormal maneuvers not included.

## Mechanics actually computed

For axisymmetric ellipsoid x(r), define f'=dx/dr and f''=d²x/dr², principal meridional curvature k_s=f''/(1+f'^2)^(3/2), hoop k_h=f'/(r sqrt(1+f'^2)). Balance pressure axial resultant on cap r:

\`N_s = p*r*sqrt(1+f'^2)/(2*f')\`
\`N_h = (p - k_s*N_s)/k_h\`

Those are **membrane forces per length**. Divide by normal dome thickness t to obtain **ideal meridional and hoop tensile stresses**. At the axis the expression is evaluated by limiting behavior. At r=0 the local curvature radius is **8.6m** in both directions, so N_s=N_h≈**435,590 N/m**. Both modeled membrane stresses remain tensile over 0..3.5m and the peak is at the central dome apex. At the r3.5 perimeter the meridional membrane force is ~**308,965 N/m**, hoop force ~**3,820 N/m**; the perimeter absolutely DOES require a load-bearing attachment, despite the optical lack of frame members.

### Same nominal material budget, different real-world material benchmarks

| Reference material | rho kg/m³ | Ideal thickness at 85.2 kg/m² | Dome material mass | Peak ideal cabin-pressure stress | Static pressure-only critical surface flaw a |
|---|---:|---:|---:|---:|---:|
| Fused silica | 2,210 | **38.55mm** | **3.526t** | **11.30MPa** | **1.118mm** |
| Transparent MgAl₂O₄ spinel | 3,580 | **23.80mm** | **3.526t** | **18.30MPa** | **2.735mm** |
| ALON optical ceramic | 3,770 | **22.60mm** | **3.526t** | **19.27MPa** | **1.339mm** |

Density/elasticity/CTE/toughness benchmarks are taken from cited sources below; actual batch and optical processes differ. ALON rho3.77g/cm³ here is from NRL's optical-ceramic table; a previous thickness experiment used a different ALON reference density 3.67g/cm³. This small numerical change is **not new materials physics**.

The flaw number is **not an allowable scratch size**, but merely the static Mode-I size where \`K_I = Y*sigma*sqrt(pi*a) = K_IC\`, with assumed Y=1.12 for a schematic surface flaw under uniform tensile stress. A real 7m ceramic's flaw distributions, surface finishing, manufacturing yield, fatigue / crack-growth lifetime, mounting stresses and proof tests are unmodeled. Measured K_IC for glass ~0.75 MPa sqrt(m) and spinel/ALON 1.9/1.4 are *material property references*, not lifetime acceptance limits.

### Thermal mismatches dominate plausible nuisance cases

To show scale, rather than invent LOOM temperature history, calculate **fully restrained elastic thermal stress proxy** \`sigma_th ≈ E alpha ΔT/(1−nu)\`. This is neither a true thermoelastic stress field nor a guarantee of worst-case magnitude. For **20 K** stress-producing mismatch with no strain relief:

- **Fused silica:** **~0.96 MPa** thermal stress proxy; combined algebraic pressure-plus-thermal fracture flaw length ~**0.95mm**.
- **Spinel:** **~43.2 MPa** proxy; algebraic pressure-plus-thermal flaw length **~0.242mm**.
- **ALON:** **~48.4 MPa** proxy; algebraic pressure-plus-thermal flaw length **~0.108mm**.

Hence material choice matters as much for CTE and boundary design as strength. The one giant ALON shell may be strong in simple static bending benchmarks but becomes *potentially very sensitive* to differential constraint with a dissimilar structural ring. Conversely, silica's thermal expansion is much smaller, but its fracture toughness and flaw growth remain critical. The illustrative fully restrained stress is **not** expected to arise uniformly in an intelligently compliant/perimeter-isolated installation. This is a sensitivity, not proof any candidate fails.

A 4g normal-direction acceleration adds approximately **3.34 kPa per 85.2kg/m² pane**, a useful magnitude check, but pressure + inertial stress requires proper direction-dependent load transfer and local support forces. We have NOT run a stress field, fatigue, shock, thermal cycling, dynamic acceleration or crack propagation model.

## Pressure redundancy and visible seams

The engineering risk is fundamentally **single-event loss of a unique pressure shell**, not the nominal pressure membrane stress alone. An outer replaceable *debris* pane does **not** constitute a backup pressure boundary.

A reasonable **visually identical variant** uses **two nested continuous transparent pressure domes**, each separately capable of bearing cabin differential pressure, with the relevant independent seals and gap/vent failure path. There are still **zero visible inner mullions**, because both nested pressure shells can be optically smooth. This is *not* the same as a monolithic laminate with two chemically bonded layers, whose cracks may propagate through the same structural body.

At **the same per-pane 85.2kg/m² allocation**, two such illustrative full-mass shells cost **~7.05t of pressure glass vs 3.53t single**, *before redundant seals, flange, intermediate clearance, and mount mass*. Each would still have its own single-shell pressure stress when called on. Alternatively, splitting 3.53t equally between two layers doubles the peak nominal pressure stress in each when alone, and no pressure reliability is established either way.

NASA/ESA real spacecraft window practice supports redundant pressure panes: the ESA ISS Cupola contains **two pressure panes** plus separate debris and scratch panes. The 2026-revalidated NASA spacecraft window standard NASA-STD-5018 explicitly expects both pressure and redundant panes to retain atmosphere after failure of either, including dynamic failover. These do not legally govern a fictional 2226 ship, but substantiate why a pressure-seamless visual design can still require two independent pressure-containment elements.

## Bottom line / no invented qualification

**Geometrically and under first-order membrane pressure loading, a continuous seven-metre inner pressure dome is not immediately ruled out.** The same existing mass allocation leads to low-to-moderate *ideal* tensile stress (11–19MPa) relative to short-term flexural-strength measurements of polished coupons. That comparison is NOT a valid margin or lifetime argument at this area: material flaws scale with area, edge stress is unmodeled, and crack growth/lifetime matter.

**What has NOT been demonstrated**: fabrication of reliable **7m** optical-grade fused silica/spinel/ALON structural shell; load-bearing transparent membrane with acceptable strength/reliability; perimeter transfer of ~3.9MN axial resultant without large local thermal and mechanical stresses; tensile/bending stress at rim; true optical transmission through curved 22–39mm material at prior high sightline incidence; thermal cycling, redundant pressure boundaries, failure containment.

**Research preference, not adoption**: retain 37-piece external replaceable shield. Explore a visually frameless **pair of nested transparent pressure domes** as the structurally credible continuation of the user's continuous inner window idea. But **stop here** at the demonstrated missing capabilities: fabrication/reliability of large transparent pressure shells and interface stress, especially if material choice is ALON/spinel. Do not invent additional ship systems/qualification machinery to make the design seem earned. No governing design changed.

## Reproducibility

- \`command/l1_seamless_pressure_dome_screen.py\` → \`command/l1_seamless_pressure_dome_screen_results.json\`, executed on VM \`quantifactus\`. Uses actual source ellipsoid, original pressure panes allocation and held 37 outer panel layout.
- \`render/make_seamless_pressure_dome_viewer.py\` → \`render/out/nose_seamless_inner_pressure_dome_viewer.html\`, offline interactive one/two-shell visualization, material, per-shell thickness and 0..40K fully-restraint stress sensitivity.

## Scientific / engineering references

- NASA Glenn, Jonathan A. Salem (2013), [Transparent Armor Ceramics as Spacecraft Windows](https://doi.org/10.1111/jace.12089). ALON and spinel slow-crack growth relative to fused silica, not proof of 7m pressure shells.
- [NRL 2015 optical ceramics comparative table](https://opg.optica.org/ao/abstract.cfm?uri=ao-54-31-F210): ALON and spinel density, E, Poisson ratio, K_IC and expansion.
- [NASA/Salem, Fracture Mechanics Properties of Fused Silicas Used for ISS Windowpanes](https://ntrs.nasa.gov/citations/20220006236) and [NIST Silica Ceramic Portal](https://srdata.nist.gov/CeramicDataPortal/Silicate/Glss100a): K_IC fused silica ~0.73–0.75 MPa sqrt(m), slow crack growth matters.
- [ESA Cupola spacecraft windows](https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/Node-3_Cupola/Cupola): pressure redundancy and dedicated outer debris pane.
- [NASA-STD-5018, change 1/revalidated 2026](https://standards.nasa.gov/system/files/tmp/NASA-STD-2018_Revalidated%20-%2001-30-2026.pdf): window pressure redundancy and dynamic failover practice. External industry standard for context, **not LOOM authority**.

**Source PR #432, Rev 7, canon and runtime untouched.**
