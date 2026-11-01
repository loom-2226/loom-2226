# Wayfarer central iris: flush scarf-lap seam experiment | 28 Oct 2026

**RESEARCH · NON-CANON · NON-RUNTIME · NON-GOVERNING · NOT MANUFACTURED OR QUALIFIED**

Live authority verified: `loom-2226/loom-2226` PR #432 open, head `3485830a56dfead79b2ef8bba031a595b536fbb5`. Uses unchanged Rev 7 pressure ellipsoid, retained crew and original sensor/node locations, and the previously tested +1.2 m / 50° angular nose. Work confined to research branch `research/wayfarer-nose-l1-search-20261028`.

## Exact question

Can the previous **R1.76 m / 16-blade / two-tier** iris close as a **flat protected front face**, rather than retaining the unacceptable 216 mm exposed step between staggered leaves, while still following the sampled collision-free cam?

**Answer: Yes, as an ideal exact-fit geometric construction. No, not yet as a mechanically credible, dust-impact-qualified seal.**

## Smallest geometry that works on paper

The earlier model gave each sector 22.5° angular pitch plus 1° overlap on each side, with every overlapping lip full thickness. For a flat close, replace just the overlap-zone geometry:

- Each **upper** leaf's full-thickness main body is unchanged over its central **20.5°** angular region. On each edge it has a **front half-thickness (98.14 mm)** projecting lap over the 2° seam.
- Each adjacent **lower** leaf has an equivalent full-thickness main body, but carries the **rear half-thickness (98.14 mm)** mating lip in that same seam.
- Both main bodies start at the **same forward x = −1.200 m** when closed. The two mating half-lips occupy adjoining x intervals; their sum is one nominal **196.28 mm** armour-equivalent thickness. There is **no face step** in the ideal closed geometry.
- The original **0.12 m-radius central armour boss** remains necessary for the finite centre. Its circular joint is not qualified.
- Before any iris rotation, retreat the lower eight blades axially by **216.28 mm**. The lower mating lips move *away from* the upper front lips, avoiding the previous raised-face collision. Next withdraw both tiers behind the central round aperture, then rotate all 16 together through the prior 0–62° cam trajectory.

The result uses the original 27 g/cm² effective protection and 20 mm tier spacing, **without adding an extra full blade layer or relocating the pressure hull**. Material continuity is an exact mathematical idealisation, not evidence that an actual half-depth rabbet has the strength and impact resistance of a seamless plate.

## Executed checks

| Screen | Result |
|---|---:|
| Tested closed angular positions | **72,001** |
| Angular/axial cells lacking nominal armour depth | **0** |
| Angular/axial cells double-occupied by rigid material | **0** |
| Nominal full material depth at all tested angles | **0.19628 m** |
| Difference between upper and lower *visible* main front planes when closed | **0.000 m** |
| Sampled stages (lower peel, common withdrawal, cam) | **123** |
| Sampled leaf-to-fixed-armour contacts | **0** |
| Sampled blade-lip intersection along staged path | **0** |
| Sampled same-tier collisions | **0** |
| Smallest pressure-head clearance in inherited cam geometry | **0.06225 m** |
| Smallest fixed-armour axial separation in inherited cam geometry | **0.026 m** |
| Inter-tier air separation after staged peel | **0.020 m** |
| Prior common-cam endpoint x-positioning allowance | **0.0383 m** |

For this test, source pressure and modelled armour collision checks use the previous **hypothetical** local 20 cm normal armour on the faceted 50° nose. These are discrete point-cloud and polygon tests, not continuous solid CAD or structural/dynamic qualification.

The fully-open iris reaches r≈2.651 m, inside the prior modelled bow sensor inner radius r=2.90 m; new bearings or field-of-regard clearance remain unproved. The earlier source-eye result still stands: the permanent 0.12 m boss preserves about **98.66%** of the sampled Pilot/NAV 60° forward cone, but the opaque parking annulus leaves only about **32.81%** of the forward hemisphere visible (versus corrected Rev 7 **69.14%**).

## Where this mechanism is physically weak

**The lap is extremely narrow near the centre.** With an angular seam of 2°, its circumferential projected width is just **4.19 mm at the central boss radius r=0.12 m**, increasing to about **61.4 mm at r=1.76 m**. These are *not* two overlapping full-length armour blocks with a generous shielded joint. The exact model presumes perfectly contacting, sharp, mutually complementary tongues, **zero assembly clearance**, no manufacturing tolerance, no gasket and no fasteners. Real dust-impact or blast loading could split/open the joint; current areal-mass bookkeeping alone does not establish protection.

A sensitivity screen was also executed on seam angle while retaining the same 16-leaf pivot. Two-tier same-level polygon collisions remain absent at 62° for **2°, 3° and 4°** total lap widths, but at **5° or more** collisions appear around 62°. Increasing to 4° approximately doubles inner lap width to **8.38 mm**, yet makes the opening radius only ~1.745 m by 62°, short of the nominal 1.76 m target. Wider lips are not free.

**The moving mechanism remains incomplete:** a 360° reinforced rim throat, actual cam bearings, edge seals, bearing loads, pressure/armour retention and closure under thermal/mechanical strain are unmodelled. The stationary upper and lower panels could be cut into scarfed edges, but **the assembled physical gap and manufacturing solution have not been demonstrated**.

During the opening sequence, the seam temporarily has less than the nominal 27 g/cm² protection after the rear lip withdraws. This may be consistent with an explicit low-speed/viewing-only shutter operating doctrine, but it is *not* suitable for claiming continuous armour protection during motion. No new doctrine is adopted.

## Decision

**Retain as the first ideal flush-shut iris *geometry*, not an adopted mechanical design.** This directly answers the 216 mm stepped-face defect without making more room inside the crew cabin. All moving armour is still intended to remain outside the original pressure head.

Do **not** announce a finished iris or modify Rev 7, canon or runtime. A further test is only justified if the centre lap can be made a **finite-tolerance, load-bearing impact seam** without consuming the existing 38 mm cam margin. The broader panoramic visibility deficit remains a separate unsolved design compromise and should not be forgotten.

## Reproduce and visualize

- `command/l1_iris_flush_scarf.py` produces `command/l1_iris_flush_scarf_results.json`: closed material-depth angular coverage and 123-stage peel/withdraw/cam path.
- `render/make_flush_scarf_viewer.py` produces self-contained offline `render/out/nose_iris_flush_scarf_viewer.html`: actual 16 moving main blade faces, mobile rotation and motion slider, plus a schematic of the mating seam cross-section.

The code uses the isolated research geometry and does not change any qualified or authoritative spacecraft structure.


---

## ERRATUM — 29 October 2026: four-window visibility scoring

The four-window iris figures in this historical report were **overstated** by an angular-mask bug: source research code selected the smallest **signed** angle difference instead of the smallest **absolute** difference from the intended window sector centres. The code and primary result JSONs have since been corrected. For the R1.76 m iris with a fixed R0.12 m centre boss and four genuine 40° sectors, corrected worst Pilot/NAV forward-hemisphere visibility is **26.17%**, not the previously cited ~32–33%. The corresponding corrected 60° forward-cone figure is **98.66%**. A wholly transparent, **unprotected and unqualified**, outer annulus could reach only **32.81%** in the same ray model. The original corrected Rev 7 reference remains **69.14%**. **See** `command/NOSE_IRIS_INTERLOCK_AND_VISIBILITY_CORRECTION_20261029.md` for the source, scope, checks and other aperture radii. This appended erratum supersedes incompatible historical figures above; the original test prose remains as an auditable record.
