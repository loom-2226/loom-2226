# Wayfarer central iris: finite centre closure and flush-face test | 28 Oct 2026

**RESEARCH ONLY · NON-CANON · NON-RUNTIME · NON-GOVERNING · NOT QUALIFIED**

Source authority checked live: `loom-2226/loom-2226` PR #432, head `3485830a56dfead79b2ef8bba031a595b536fbb5`. Experiment builds upon the separately researched +1.2 m / 50° nose with 1.8 m iris, and preserves the original Rev 7 pressure head, crew, sensors and forward Metric faces.

## Decision

**The exact centre closure has a simple credible geometric answer. A genuinely flush, concealed full-armour iris is still not demonstrated.**

Do not extend the search to a new nose architecture. The observed missing part is an **actual 3D entry throat / backed annular pocket for two levels of thick rotating blades**, with a finite closed lap seam. A flat-space positioning interval is not equivalent to a moving mechanism.

## Experiment A: get rid of the unphysical centre point

Use a **permanently fixed 0.12 m-radius full-armour central boss**, and truncate each of the 16 rigid iris leaves at r≥0.12 m. The fixed boss protects the central circle; the blades cover the remaining annulus to r=1.8 m when closed. A real circumferential lap/gasket and load path remain unmade, but the protection no longer depends on mathematical tips meeting at one dimensionless point.

- Boss projected area π(0.12 m)² = 0.04524 m².
- At the source's 27 g/cm² areal protection, armour-equivalent boss material is **12.21 kg** (not support, attachment, or gasket mass).
- With that boss permanently in place, the *same* source-eye/room/sensor sampled Pilot/NAV forward 60° cone drops only from **100% to 98.66%**; forward hemisphere worst Pilot/NAV changes **32.03% → 31.64%** under the earlier iris + four outside windows.
- Blade tip material sample minimum radius under all 1° opening stages is 0.12 m at closed; the sectors move *away* from the centre. The boss can remain fixed without entering the sampled blade footprint.
- The boss provides a mechanically understandable centre **coverage**, not a proven hypervelocity-impact-qualified seal or a perfectly smooth seam. This is much simpler than a retracting cap and compatible with the image's iris appearance, except for a small central dot.

**Alternative executed:** an entirely retractable **0.10 m-radius / 8.48 kg** equivalent full-depth plug with 0.13 m shallow face lip. After blades are open, a 177-step axial-then-sideways path parks it at r=2.50 m behind the blade stack. It remains ahead of the source pressure head with **minimum sampled 25 mm clearance**, and behind open iris blade backs with **minimum 19.7 mm clearance**. The flange/gasket/ring rail, radius envelope, drag load and simultaneous moving collisions were not modeled. These margins are too small to promote it over the simple fixed boss.

## Experiment B: actual closed-face flushness

The initial protected iris has **two full 196.3 mm material levels separated by 20 mm**. It therefore **closes with a 216.3 mm step** between exposed surfaces. The earlier phrase *flush* was not earned.

A notional way to eliminate the step is to add a raised facing on each of eight recessed leaves only over its visible interior, maintaining edge rebate underneath the neighbouring higher leaf. The extra visible-area face thickness is 216.3 mm. For the 1.8 m iris, reserving ~20.5° of raised face per recessed leaf yields about **4.64 m²** of added facing, or ~**1.38 t** of armour-equivalent material at the current effective reference density (not an independently validated armour construction).

A geometric rotation test shows why that is insufficient:

| Recessed-leaf raised-half angular width | No overlap in fully closed pose? | First upper/lower raised-face overlap during synchronized opening |
|---|---|---|
| 10.25° | Yes | 43° |
| 10.0° | Yes | 43° |
| 8.0° | Yes | 43° |
| 6.0° | Yes | 43° |

The *unmodified* staggered leaves can rotate, but any raised exposed facing that shares the front plane would collide with a rotating neighbour around 43°. Full flushness therefore needs a staged axial separation/cam, retraction or a different true 3D blade construction.

A hypothetical staged path is geometrically understandable: raise the top eight blades forward by **0.25 m** so their rear face stands ~54 mm ahead of the lower raised front, rotate the top eight, rotate the lower eight, then park each level in turn. At full open, the hypothetical top layer occupies x=−0.309..−0.113 m; lower raised material x=−0.083..+0.330 m, leaving ~30 mm between groups and **~66 mm pressure clearance** at the innermost sampled open radius. The furthest blade remains at r≈2.710 m. **This is necessary geometry only; neither the lift hardware nor real blade-face relief exists.**

## Experiment C: the missing stowage throat

The proposed open-state annulus spans r≈1.80..2.71 m. The local exterior-to-pressure axial geometric gap is at least **1.035 m** over that range, so *volume alone* is not the obstruction. A radially conforming hypothetical assembly of top armour leaf (0.196 m), separator gap (0.020 m), lower raised leaf (0.413 m), and fixed rear ring armour (0.196 m) needs roughly **0.825 m material depth** before real hardware. It could fit locally *if its components actually followed the sloping cavity*.

**But our moving leaves are rigid and flat.** In the explicit 3D open pose, adding 196 mm fixed backing behind the lower blade causes ~**150 mm of pressure intrusion** at the inner annulus, so that apparent gross depth does **not** close the installed mechanism.

More fundamentally, translating a fully rotated blade from its exterior open position into the calculated under-armour slot **intersects the original fixed exterior armour**. The sampled moving sheet hits that material beginning roughly 22.5% through the retreat, so the former analysis assumed that blades could pass through a solid shell. To make an actual recessed iris, one must give the blades a physical entry throat (or relocate part of the armour ring and provide other backing protection). That change has **not** been drawn, massed, or found to preserve the protected hull. The pressure hull itself was not altered.

## Stop here

- **Keep the 16-leaf central iris and small permanent armoured boss** as a useful, non-canon physical concept. The centre is no longer a mathematical unprotected hole.
- **Do not declare flush closure**, because upper and lower leaves still have a 216 mm face step and the proposed raised-face workaround collides.
- **Do not declare concealed stowage**, because a real entrance path through/around the annular fixed armour does not exist in the source geometry.
- **Do not adopt this candidate over Rev 7.** Its earlier tested aperture-plus-ring layout still delivers only ~32% Pilot/NAV forward-hemisphere visibility versus ~69% in the fair Rev 7 geometric baseline.

The next **physical** experiment, if the visual goal warrants one, would be a very small cross-sectional slot and a single staged leaf entering a real *backed* recess. No more visibility searches or unqualified nose redesign. If that cannot be drawn without sacrificing shielding or pressure containment, stop this mechanism.

## Reproducible artifacts

- `command/l1_iris_center_plug.py` and `command/l1_iris_center_plug_results.json`: fixed-centre boss loss and alternative physical plug route.
- `command/l1_iris_flush_hub.py` and `command/l1_iris_flush_hub_results.json`: detailed 16-leaf centre clearance, raised-face overlap, material-depth and outer-armour crossing screen.
- `render/out/nose_armoured_iris_viewer.html`: updated original viewer showing a fixed 0.12 m central boss, truncated rotating leaves, the two-tier front surface and the earlier stowage annulus. Its geometry is research, not CAD qualification. Generated by `render/make_armoured_iris_viewer.py`.


---

## ERRATUM — 29 October 2026: four-window visibility scoring

The four-window iris figures in this historical report were **overstated** by an angular-mask bug: source research code selected the smallest **signed** angle difference instead of the smallest **absolute** difference from the intended window sector centres. The code and primary result JSONs have since been corrected. For the R1.76 m iris with a fixed R0.12 m centre boss and four genuine 40° sectors, corrected worst Pilot/NAV forward-hemisphere visibility is **26.17%**, not the previously cited ~32–33%. The corresponding corrected 60° forward-cone figure is **98.66%**. A wholly transparent, **unprotected and unqualified**, outer annulus could reach only **32.81%** in the same ray model. The original corrected Rev 7 reference remains **69.14%**. **See** `command/NOSE_IRIS_INTERLOCK_AND_VISIBILITY_CORRECTION_20261029.md` for the source, scope, checks and other aperture radii. This appended erratum supersedes incompatible historical figures above; the original test prose remains as an auditable record.
