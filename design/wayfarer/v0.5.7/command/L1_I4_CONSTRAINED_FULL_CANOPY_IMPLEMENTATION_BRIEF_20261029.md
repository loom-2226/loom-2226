# Wayfarer L1 · I4 constrained-fit rebuild, full dome and 37 trapezoidal tiles
**2026-10-29 · RESEARCH / NON-CANON / NON-RUNTIME · NOT 4g OR STRUCTURAL QUALIFICATION**

## Objective and authority

Rebuild I4 Command Commons **against the existing source L1 geometric envelope first**. Then render **all of L1**, the **complete 37-piece trapezoidal outer protection** and **seamless pressure dome(s)**, with independent user-controlled visibility of the actual ship elements.

Live authority bootstrap: `loom-2226/loom-2226` PR #432, OPEN at `3485830a56dfead79b2ef8bba031a595b536fbb5`. Its current Rev7 geometric source is `design/wayfarer/v0.5.7/out/wayfarer_v05_geometry.json` and original `render/out/l1_scene.json`. Research branch only. No PR/canon/runtime changes.

### Source invariants

- Inner pressure vessel: diameter **8.6 m**, radius **4.3 m**, dome/cylinder transition `X=2.35 m`.
- **True L1 annular floor**: outer radius **4.15 m**, central hole radius **0.90 m**, source axial range `X=3.00–3.30 m`. Do not cover the central hole with a fictitious continuous rectangular deck.
- Two existing vertical ladder footprints: centres `(Y,Z)=(±1.40,0)`, **0.8 m diameter**.
- Shoulder sensor annulus nominally `r=2.9–4.15 m` (no reason to delete it from the viewer).
- Crown clear projected radius **3.5 m**. Held research outer tile pattern: exactly **37** individually delimited trapezoidal/radial modules in **[1,12,12,12]** bands with projected boundaries **[0,0.75,2.0,2.75,3.5] m** and final band angular staggering **π/12**. **10 mm illustrative opaque seam width** is a separate analytical reference, not represented as structural mount qualification by the wireframe.
- Primary seamless structural dome based on `X(r)=2.35−2.15√(1−(r/4.3)²)` (whole pressure shell); speculative backup seamless dome displaced **0.12 m forward axially**. Research optogel previously evaluated conceptually; not mechanically proven or new canon here.
- Exterior research face: flat through `r=2m`, then nominal **50°** radial trapezoidal facet slope with the source `+1.2m` axial nose extension. It is a visual model, not ballistic impact qualification.

## 1. Constrained I4 station placements

All units metres; view axes are the legacy Canvas2D rendering `Y,Z,H=4-X` system. Importantly, **true ship bow is −X, not the old freeform I4 plan's +Z**. The drawing's tier elevation represents source axial X, but human crew seating/head orientation is still research concept geometry, not an approved final flight-coordinate placement.

| Seat | Y | Z | Source X | Plan heading |
|---|---:|---:|---:|---:|
| Pilot | −0.98 | −2.00 | 1.91 | −5° |
| Captain | +0.98 | −2.00 | 1.91 | +5° |
| Navigator | 0.00 | +2.50 | 2.76 | 0° |
| Engineering | −2.85 | −0.70 | 3.31 | −28° |
| Sensors / EW | +2.85 | −0.70 | 3.31 | +28° |
| Mission Operations | +2.45 | −2.00 | 3.31 | +22° |

Pilot and Captain remain raised and paired, Navigator still has a distinct platform, and all six crew functions retain their own contoured workseat.

## 2. Floor, levels and meaningful room furniture

- **Delete** I4's previous `8.15 × 8.05 m` rectangular main deck. **Generate the actual source annulus**, `r=.9..4.15m`, with both ladder holes removed from the drawn floor. A coarse tessellated drawing skips cells within radius **0.49 m** of ladder centre to make the original **0.40 m-radius** shaft visibly clear. Real structural openings and exact edge geometry still require final CAD.
- Command raised terrace: centre **(Y=0,Z=−1.96)**, **3.40 × 2.10 m**, render height **H=2.09m** (concept source `X=1.91m`). It stays away from the 0.9m central opening and the ladder shafts in the 2D envelope.
- Navigator platform: centre **(0,+2.55)**, **2.65 × 2.20m**, `H=1.24m` (concept `X=2.76m`). The true axial sightline and tier transfer remain to be tested.
- Low-g command anchoring point **(−1.35,−3.55)**; mission-planning table **(+0.40,−3.45)**; independent mission workbench **(−2.45,−2.18)**. These are **three distinct working functions**, not three redundant consoles or added high-g crew seats.
- Two compact built-in storage fixtures moved away from occupied specialist envelopes, around `(±3.45,+1.10)`. A redundant locker whose old position obstructed Mission Operations is **deleted**, not relocated for decorative completeness.
- No changed pressure hull, added deck count, arbitrary ladder relocations or seventh acceleration seat.

## 3. Spatial screening completed

`command/l1_i4_constrained_fit_screen.py` is a small reproducible checker against the actual source floor radial envelope, central opening, and ladder shaft centres with an additional **0.12m** clearance margin around the original 0.4m ladder radius.

**Results**: all six new seat bounding rectangles and retained work surfaces/storage objects pass the **plan-view source floor outer radius / central hole / ladder** gates. A separate rectangle-overlap pass showed that the only remaining shared plan footprint is the **intentional workbench with its mounted local display**, at different height. The previous I4 rectangular floor's **13.783m²** outside the original floor ring and **2.545m²** covering the central opening are not merely shaded: **the old rectangular floor has been replaced** by the source annulus.

These are **not** finished clearance or engineering results. Not yet checked: entire seated human swept volume, 0.8m circulation paths, actual full-height ladder routes between decks, room/head support and restrained reach, thrust-axis alignment, 4g biological and structural loads, dome/window refraction, attachment and damage tolerance. The correct next blocker for physically qualifying I4 is a **true X/Y/Z body-and-hull/egress check**. Do not claim all spatial conflicts are solved.

## 4. Full L1 research visualization

`render/out/wayfarer_l1_i4_full_trapezoid_dome_constrained_android.html` shows the **complete L1 round floor and all six stations**, source shell, primary/backup seamless dome visuals, 37 separate trapezoidal outer projected panels, seam outlines, shoulder sensor ring, central shaft and both ladders, station screens/people, terraced platforms, work areas and support/handhold elements. No floating cutaway of a rectangular floor.

Independent controls for:
- structural pressure hull
- primary pressure dome
- backup pressure dome
- 37 outer trapezoidal panes
- tile seams
- sensor shoulder annulus
- rings and illustrative supports
- ladder openings
- source floor reference outlines
- crew
- personal/shared displays
- mission furniture
- rails and lighting
- decks
- station labels

Cameras: orbit, deck-plan, side/tier. Defaults show the full 37-pane exterior and primary/backup dome with transparency. Individual elements can be hidden to inspect the interior. All exterior panes are authored as real separate parametric sectors in 3D with distinct boundaries, not one painted circular disk.

**Render engine:** Offline, no WebGL, no external assets; source geometry plus non-canon panes interpreted by the existing Canvas2D software projection. The HTML has its own embedded actual screenshot fallback if Android disables scripting.

## 5. Reproduction and tests actually run

- `command/l1_i4_constrained_fit_screen.py` → `command/L1_I4_CONSTRAINED_FIT_SCREEN_20261029.json`.
- `render/make_l1_i4_full_fit_and_canopy.py` → `command/L1_I4_CONSTRAINED_FULL_CANOPY_SCENE_20261029.json` and the self-contained HTML.
- HTML tested in Chromium at **412×915** mobile and **1260×940** desktop viewports with GPU/WebGL disabled. Orbit, plan and side generated different rendered images without reported JS errors.
- JS disabled: embedded static screenshot loads, 600×404 pixels.
- Each independent display control was clicked in a mobile browser and verified to change the **actual canvas image** (including dome/backup/outer/seams/shoulder/hull/ladder/interior layers). No reported page errors.
- No test on the user's actual Pixel/Android `content://` browser. A previous black screen on that platform is why this continues to use Canvas2D with a static fallback.

## Stopping condition

**Current research pass stops when** source annular floor, openings and six seats pass the bounded screen; complete 37-pane layered dome + structural shell are visible and independently switchable; mobile browser actually renders the scene. **That condition is met.**

**No claim of final fit or crew operations** until a real 3D occupied-body/ladder-access test is run on the selected source-coordinate layout. Complexity does not earn a new optimizer or CAD/qualification platform here.

Preserved as non-authoritative LOOM design research only.
