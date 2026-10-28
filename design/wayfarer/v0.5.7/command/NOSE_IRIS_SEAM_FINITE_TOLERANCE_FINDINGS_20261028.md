# Wayfarer iris seam: finite tolerance and armour continuity | 28 October 2026

**RESEARCH · NON-CANON · NON-RUNTIME · NON-GOVERNING · NO HYPERVELOCITY CERTIFICATION**

GitHub authority checked live: `loom-2226/loom-2226`, PR #432 head `3485830a56dfead79b2ef8bba031a595b536fbb5`. This is a research-only extension of the +1.2 m/50° angular nose and R1.76 m, 16-leaf, two-tier scarf-lap iris. Original pressure hull, six L1 seats, bow sensors, forward Metric nodes, canon and runtime unchanged.

## Narrow question

Earlier geometry passed **only because the 98 mm + 98 mm half-depth mating edges contacted perfectly**. Does that 27 g/cm² closed shield remain a complete 27 g/cm² shield when the two edges have a finite positional error?

**Result: not under this simple scarf construction.** At any adverse edge retreat, small projected strips are protected by only *one* 98 mm half-lip, even if enough nominal overlap remains elsewhere. Merely widening the scarf postpones a completely open slit but does not eliminate the single-half-thickness strips. This violates the simple uniform nominal areal-protection requirement. This is a geometric failure, **not** a simulated ballistic penetration probability or proof that all finite-tolerance joint constructions are impossible.

## Reproducible model assumptions

- 16 leaves, round aperture radius 1.76 m, fixed armoured centre boss radius 0.12 m.
- Equivalent monolithic leaf thickness 0.19628 m = 27 g/cm² using the *source ledger's effective density* (not a derived material law).
- At each boundary a front 0.09814 m lip and rear 0.09814 m lip are complementary over a nominal 2° total angular lap. Edge retreat `e` is **an illustrative adverse manufactured alignment error on each of the two lips**, constant *millimetres of projected circumferential width*, not an actual Wayfarer process tolerance or assumed thermal expansion.
- Total nominal circumferential lap width at radius `r` = `r × lap_deg × π/180`. Both half-lips remain over the portion `w−2e` when positive. Two thin end strips lack one full half-depth lip. If `2e>w` a direct projected gap appears near the hub.
- The earlier 16-leaf cam is rerun with 2°, 3° and 4° total lap, **without** changing pivots, armour thickness or pressure envelope. All are sampled 0..62°.
- The separate axial-interface-gap sensitivity is an illustrative **additional** nonzero front/rear separation, not a manufactured joint. A rear tongue could in principle keep two full half-depth material lengths with a slightly larger installed depth, but no geometry is qualified.

## Actual numerical results

| Total lap | Lap width at r=.12 m | Full cam with fixed armour/pressure | Fully opens R1.76m within 10 mm | x-placement allowance at open |
|---|---:|---|---|---:|
| 2° | 4.189 mm | Yes, sampled | Yes | +38.25 mm |
| **3°** | **6.283 mm** | **Yes, sampled** | **Yes, narrowly** | **+23.95 mm** |
| 4° | 8.378 mm | Yes, sampled | **No** (clear radius 1.7447 m at 62°) | +9.67 mm |

The 4° layout has more overlap but insufficient clear opening at the previously fixed 62° endpoint. Making the overlap larger reduces free motion and stowage margin; the design has no unlimited geometric slack.

**Adverse lip-edge retreat, near the r=.12 m boss:**

| Lip retreat on *each* half-lip | 2° remaining dual-lip overlap | 3° remaining dual-lip overlap | Worst local nominal column |
|---|---:|---:|---:|
| Exactly 0 mm | 4.189 mm | 6.283 mm | 27 g/cm² nominal (perfect contact) |
| 0.25 mm | 3.689 mm | 5.783 mm | **13.5 g/cm²** in narrow edge strips |
| 0.50 mm | 3.189 mm | 5.283 mm | **13.5 g/cm²** in narrow edge strips |
| 1.00 mm | 2.189 mm | 4.283 mm | **13.5 g/cm²** in narrow edge strips |
| 2.00 mm | 0.189 mm | 2.283 mm | **13.5 g/cm²** in narrow edge strips |
| 3.00 mm | **0 mm: 1.811 mm through-gap** | 0.283 mm | 0 g/cm² locally (2° only) |

In the 0.5 mm edge-retreat thought experiment, all sixteen radial seams together create about **0.02624 m² of half-density strip area** across the r=.12..1.76 m annulus, approximately **0.27% of the central aperture annulus**. That area percentage is not a debris impact-risk estimate; an impact hotspot at a weak seam can be disproportionately important. For the 2° joint, an adverse 3 mm retreat per lip opens a small through-slit near the centre boss, with a total modeled projected gap area about 0.000752 m² over sixteen seams.

**Axial mating-face clearance** (separate from lateral edge retreat) is also nontrivial. Keeping the total installed joint within the original 196.28 mm external-to-internal depth while introducing a 1 mm axial air gap forces one millimetre less nominal total protective material: **26.86 g/cm² instead of 27**, *if material is simply removed*. Preserving the full material length instead requires an added ~1 mm locally rear-projecting tongue, which would consume about 1 mm of the 38 mm open cam positioning window in an idealised estimate. Such a tongue, gap and support are **not constructed CAD**.

At the r=.12 m boss, 2° lap with 0.5 mm adverse edge retreat leaves 3.19 mm dual-lip overlap. For a hypothetical 1 mm axial void, a straight lateral ray would need approximately 72.6° tangential obliquity to traverse that overlap *entirely within that void*. This is a simple necessary line-of-sight geometry bound, **not a ballistic limit**, safe incidence angle, or a test of shock/spall through a two-piece target. Other impact angles may still damage the seam catastrophically.

## Scientific boundary

NASA ARES HVIT explains why ballistic-limit performance depends on projectile diameter, velocity, density, angle, shield configuration, and failure criterion. ESA explains projectile fragmentation, shock reflections, cracking and spall under hypervelocity impact. A 27 g/cm² **combined normal material column is not equivalent to a monolithic 27 g/cm², impact-qualified shield across a joint.** See:

- [NASA ARES: hypervelocity impact physics and ballistic limits](https://hvit.jsc.nasa.gov/hypervelocity-testing/impact-physics.html)
- [NASA NESC: spacecraft debris risk and empirical ballistic limit models](https://www.nasa.gov/centers-and-facilities/nesc/space-debris-understanding-the-risks-to-nasa-spacecraft/)
- [ESA: hypervelocity impacts and protecting spacecraft](https://www.esa.int/Space_Safety/Space_Debris/Hypervelocity_impacts_and_protecting_spacecraft)

This research **does not** model 2226 ballistic materials, projectile environment/velocity distributions, impact angle populations, spall fragmentation, fatigue, tolerance stackups or qualified structural joint strength. There is no evidentiary basis for declaring a protection pass.

## Decision and stopping condition

**Stop the iris mechanism refinement here for now.** The low-level geometric closing/opening is genuinely interesting; the 1.76 m, 16-leaf, 2°/3° lap designs have executable successful sampled cam paths and remain *research candidates*. But neither is a physically established fully armoured shutter under finite tolerance, and a local lap may have seriously different high-speed failure modes from monolithic nose armour. The iris also sacrifices broad forward-hemisphere visibility (about 33% for Pilot/NAV vs ~69% Rev 7), independent of these seam issues.

No new spacecraft framework, broader nose redesign, materials invention or synthetic ballistic pass is justified by this study. The next step in LOOM **should be to use the existing Wayfarer L1 geometry and viewer** to decide whether the *visible* nose experience justifies retaining this concept. If realism later requires this iris, first obtain a specific protected joint construction/material model and a credible empirical or simulation-backed ballistic-limit basis. The present experiment does not manufacture that evidence.

## Artifacts

- `command/l1_iris_seam_tolerance.py` and `command/l1_iris_seam_tolerance_results.json`: deterministic angular-lap, radial error, understrength-area, axial gap and 16-leaf motion sensitivity.
- `render/make_iris_seam_tolerance_viewer.py` and generated standalone `render/out/nose_iris_seam_tolerance_viewer.html`: 2D mobile-friendly interactive section with lap, radial position and adverse edge-error sliders. Visualises geometric material occupancy only, **not penetration probability**.

Original governing Rev 7, source PR #432, canon and runtime are unchanged.


---

## ERRATUM — 29 October 2026: four-window visibility scoring

The four-window iris figures in this historical report were **overstated** by an angular-mask bug: source research code selected the smallest **signed** angle difference instead of the smallest **absolute** difference from the intended window sector centres. The code and primary result JSONs have since been corrected. For the R1.76 m iris with a fixed R0.12 m centre boss and four genuine 40° sectors, corrected worst Pilot/NAV forward-hemisphere visibility is **26.17%**, not the previously cited ~32–33%. The corresponding corrected 60° forward-cone figure is **98.66%**. A wholly transparent, **unprotected and unqualified**, outer annulus could reach only **32.81%** in the same ray model. The original corrected Rev 7 reference remains **69.14%**. **See** `command/NOSE_IRIS_INTERLOCK_AND_VISIBILITY_CORRECTION_20261029.md` for the source, scope, checks and other aperture radii. This appended erratum supersedes incompatible historical figures above; the original test prose remains as an auditable record.
