# Wayfarer L1: permanent nanoengineered transparent protective glazing, no shutters | 29 October 2026

**RESEARCH · NON-CANON · NON-RUNTIME · NON-GOVERNING · NOT IMPACT / PRESSURE / OPTICALLY QUALIFIED**

## Authority and purpose

Bootstrapped live `loom-2226/loom-2226` PR #432, still open, head `3485830a56dfead79b2ef8bba031a595b536fbb5`. This experiment uses its original pressure-head geometry, unchanged source L1 station eyes/crew blocking and original bow sensor ring, but an explicitly *hypothetical* +1.2 m, flat-r2 m, 50° angular exterior profile. It is isolated in `research/wayfarer-nose-l1-search-20261028` and changes no source, canon, runtime or PR.

The **specific question** is whether a permanently transparent protective outer skin can replace the 16-leaf shutter and recover a panoramic command deck, without violating the existing *nominal mass allocation* and the original pressure-hull envelope. We do not invent a nanomaterial law.

## Executed no-shutter surface area / visibility screen

The source visibility model traces the same 256 sample directions and forward 60° Pilot/NAV cone from each station, through the original unchanged *shape* of the pressure boundary and a hypothetical wholly transparent outer angular nose. Meridional reference frames, the 2.9 m-inner bow sensor ring and the same crew/furniture occlusions remain in the calculation. Each crown radius is an *aperture-extent change*, not a proven structural pressure pane; material within the original pressure envelope would need to be changed from solid to load-bearing transparent material as the aperture expands.

| 50° angular transparent crown radius | Exterior protection area | Transparent pressure aperture area | Nominal equivalent exterior protection at 270 kg/m² | Worst Pilot/NAV forward hemisphere | Worst support forward hemisphere |
|---|---:|---:|---:|---:|---:|
| 2.8 m | 31.33 m² | 25.53 m² | 8.46 t | 49.61% | 4.30% |
| 3.2 m | 43.07 m² | 33.93 m² | 11.63 t | 63.67% | 7.42% |
| **3.5 m** | **52.89 m²** | **41.38 m²** | **14.28 t** | **72.66%** | **10.94%** |

All three angular profiles have **100% of the sampled Pilot/NAV forward 60° cone clear**. The corrected Rev 7 original ellipsoid/pane reference (not an equal nose profile) is **69.14% forward hemisphere, 5.47% support minimum**. The earlier research two-tier rigid iris with four correctly masked 40° side windows was only **26.17% Pilot/NAV**, corrected in `NOSE_IRIS_INTERLOCK_AND_VISIBILITY_CORRECTION_20261029.md`.

**Geometry verdict:** removing opaque storage and shutters allows the 3.5 m transparent crown to recover and slightly exceed the Rev 7 forward-hemisphere score. This is *directional geometric visibility* with ideal transmission, not evidence that thick real 2226 glazing has flawless optics.

## Mass accounting: do not add the same armour twice

Source design reference: 27 g/cm² = **270 kg/m²** equivalent protection used for the **opaque shutter/armour allocation**. For the 3.5 m fully transparent 50° outer nose, covering **52.89 m²** at that same areal allocation gives **14.28 t**. That number is a *gross protective material allocation* for transparent replacement of the old opaque outer shield. It is **not automatically 14.28 t added to Wayfarer's mass**; the source notes displaced crown protection was already booked in fixed hull armour.

Conversely, it is also **not proof of a zero-net-mass swap**: we do not yet know actual pane shields, frames, structural glazing, attachments, thickness, and which original fixed-armour material can truly be displaced. Further, the larger transparent crown adds pressure-boundary glazing area. The source's ~25 m² original crown assigns **2.13 t pressure panes**, **1.8 t frame**, and **1.0 t brow + tracks/drives** in a 4.93 t crown subtotal. A purely proportional **2.13/25 t/m²** extrapolation to 41.38 m² gives **3.53 t hypothetical pressure panes**, ~1.40 t more than the original. This extrapolation is *not structural sizing*, and the source 1.8 t frame cannot be assumed unchanged. The brow/drives might be removable under a no-shutter design but real mount/frame mass would replace some of them. No complete validated net ledger exists.

The pressure panes and the outer protective layer are **different components**, which cannot be counted as the same 14.28 t simply because both are transparent. A future fully integrated laminate might share jobs, but would require a demonstrated material/strength and impact design.

## Gross fit: use actual candidate material densities only for thickness

The equivalent constant areal **mass** of 270 kg/m² produces the following illustrative *single monolithic* thicknesses, independent of any protection claim:

| Material-density benchmark | Density | Physical thickness at 270 kg/m² | 3.5 m crown tightest remaining x-gap to original pressure head after illustrative exterior layer |
|---|---:|---:|---:|
| Fused silica | 2,210 kg/m³ | 12.22 cm | ~0.325 m |
| Magnesium aluminate spinel | 3,581 kg/m³ | 7.54 cm | ~0.396 m |
| Aluminium oxynitride (AlON) | 3,670 kg/m³ | 7.36 cm | ~0.399 m |

The angular facet shell uses normal physical thickness and axial allowance = normal thickness / cos(50°); the central flat face uses normal thickness directly. The minimum is sampled across the actual original Rev 7 pressure ellipsoid inside r≤3.5. **All three fit the gross envelopes** without placing material inside the pressurised cabin. However, that gap is not a certified open structural bay and has not been allocated to frames, spacers, pressure-pane layers or impact debris-cloud stand-off.

These benchmark densities are *not* an actual composition or performance specification for a 2226 multilayer. In particular, a nanostructured shield with internal stand-off could be physically much thicker than a dense equal-mass monolith. No assumption of equal protection based on areal density is permitted.

## Empirical material evidence and the missing physics

- **NASA Glenn, Salem (2012/13), _Transparent Armor Ceramics as Spacecraft Windows_**, [DOI 10.1111/jace.12089](https://doi.org/10.1111/jace.12089). ALON and spinel have better slow-crack-growth resistance than fused silica, and were investigated to improve window mass/lifetime. *This is not evidence that any 7.4 cm ALON plate survives Wayfarer's 2226 impact environment.*
- **NASA Glenn, Salem (2017), _Applying Fused Silica and Other Transparent Window Materials in Aerospace Applications_**, [NASA NTRS](https://ntrs.nasa.gov/citations/20170005664). Better fracture resistance does not automatically produce better thermal shock behavior; impact morphology/residual strength are separate questions.
- **NASA 2014/15, _HVI Ballistic Limit Characterization of Fused Silica Thermal Pane_**, [NASA NTRS](https://ntrs.nasa.gov/citations/20140006471). Hypervelocity tests on Orion fused silica window configurations reached ~10 km/s, using hydrocode alongside empirical impacts. A specific impact environment and configuration are required.
- **NASA Glenn, Salem (2024), _Residual Strength of Hypervelocity Impacted Silica_**, [NASA NTRS](https://ntrs.nasa.gov/citations/20230017129). The residual strength after craters and microcracking matters to lifetime and crew safety.
- **National Academies transparent materials overview**, [Protection Materials Science](https://www.nationalacademies.org/read/13157/chapter/7) gives AlON density ~3.67 g/cm³, but is mainly ballistic-ceramic context, **not equivalent MMOD protection**.
- **NIST Structural Ceramics Database**, [spinel density ~3.581 g/cm³](https://srdata.nist.gov/CeramicDataPortal/Scd/Z00738). This is single-crystal reference material and processing may change properties.

Required physics *not supplied*: validated 2226 material law, damage tolerance under particles at relevant velocities/angles, optical transmission and scattering through 7–12 cm or a realistic laminate, laminated window fracture/thermal response, pressure differential/redundancy, abrasion/pitting over ship life, replaceability. The 27 g/cm² existing opaque allocation is an accounting starting point, **not a scientifically demonstrated universal ballistic protection threshold**.

No transparent candidate **passes** the actual protection requirement, because it has not been defined in terms of particle environment and assessed against the material performance. Equally, nothing in the available evidence establishes that no transparent 2226 candidate could work.

## Decision / stop condition

**Promote the 3.5 m no-shutter crown as the LEADING NON-CANON EXPERIENCE / GEOMETRY CANDIDATE**, not as adopted Wayfarer design. It restores the best forward panorama of the tested profiles while dispensing with a complex iris that consumed the field of view. It also eliminates mechanical shutters and their failure modes, without assuming that nanoengineering is magical.

**Stop at a clear epistemic boundary:** we have geometry, gross thickness/space and mass-allocation calculations; **we do not have a qualified transparent-impact material**. Do not expand this work into an invented materials science subsystem or a certification framework. The next genuinely useful activity is to **view the 3.5 m nose from the actual Pilot/NAV and support positions** using the existing Wayfarer viewer, and assess whether the visibility experience justifies the larger pressure-panel structure. Only then consider a narrow sourced material-property assumption for the fictional 2226 laminate.

## Artifacts

- `command/l1_transparent_nose_screen.py` → `command/l1_transparent_nose_results.json`: reproducible no-shutter 2.8 / 3.2 / 3.5 m area, visibility, gross mass, physical density/thickness and pressure/exterior clearance.
- `render/make_transparent_nose_viewer.py` → `render/out/nose_transparent_noshutter_viewer.html`: standalone, offline, Android-friendly cross-sectional nose browser. It switches crown radius and illustrative material density without claiming armour or optical certification.

**Rev 7, source PR #432, canon and runtime unchanged.**
