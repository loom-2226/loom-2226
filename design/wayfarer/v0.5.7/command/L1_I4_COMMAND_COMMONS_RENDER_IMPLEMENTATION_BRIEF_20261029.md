# Wayfarer L1 — I4 Command Commons: exact geometry + render implementation brief
**29 October 2026 | RESEARCH · NON-CANON · NON-RUNTIME · NOT HULL-FITTED OR 4G-QUALIFIED**

## Authority / scope

Bootstrapped the live authoritative `loom-2226/loom-2226` PR #432, OPEN at source head `3485830a56dfead79b2ef8bba031a595b536fbb5`. No changes to PR #432, Rev7, canon, technology timeline or runtime.

User-selected concept: pair **Pilot + Captain** on a raised command terrace, put **Navigator forward and lower**, keep Engineering, Sensors/EW and Mission Operations at their own contoured acceleration seats, and give the crew a separate low-g mission workbench plus shared working/social spaces.

The source for this narrow pass is the existing sandbox `command/L1_THREE_COMPLETE_INTERIOR_CONCEPTS_20261029.json`. Reuse **I1's contiguous low deck and simple command hierarchy**, borrow **I3's open observation and gathering spaces**. No new architecture, evaluation framework, ship subsystem or reoptimization required.

**IMPORTANT FRAME DISTINCTION:** The exact numbers below use the **illustrative 3D viewer coordinates**: `Y` lateral across the room; `Z` toward the forward panorama; `H=4-X` an *illustrative* vertical/tier height. This is NOT the canonical Wayfarer flight/thrust frame. Treat them as **render coordinates in metres** only.

## 1. Station centers — render-ready

Six 1.58m projected-length, approximately 0.70m-wide, contoured Soyuz-inspired **visual seat envelopes**. The form illustrates bent knees, supported feet and head/torso support, but has NOT been anthropometrically fit-tested or mounted/qualified.

| Seat / function | Y (m) | Z (m) | Visual tier H (m) | Heading about plan bow axis |
|---|---:|---:|---:|---:|
| Pilot | -0.93 | -0.46 | **2.09** | -5° |
| Captain / Commander | +0.93 | -0.46 | **2.09** | +5° |
| Navigator | 0.00 | +2.50 | **1.24** | 0° |
| Engineering | -3.04 | -0.95 | 0.69 | -28° |
| Sensors/EW | +3.06 | -0.60 | 0.69 | +28° |
| Mission Operations | +2.48 | -3.06 | 0.69 | +22° |

An independent local display is placed approximately 0.60m from each source-modeled eye, facing toward the operator. The critical control placement and anthropometric reach are **not qualified**.

## 2. Deck surfaces — exact initial model

| Element | Centre (Y,Z,H) m | Width Y × Length Z (m) | Thickness / character |
|---|---|---|---|
| One **continuous main operations deck** | (0, -0.56, 0.68) | **8.15 × 8.05** | 0.16m conceptual floor |
| **Broad paired command terrace** | (0, -0.47, 2.09) | **3.62 × 3.16** | 0.18m open-edged deck |
| **Forward Navigator platform** | (0, +2.48, 1.24) | **2.80 × 2.52** | 0.16m deck |
| Port/Engineering low cabinetry | (-3.85, -1.20, 1.04) | 0.37 × 2.72 | Low side storage |
| Starboard/Sensors low cabinetry | (+3.85, -0.88, 1.04) | 0.37 × 2.45 | Low side storage |
| Aft specialist lockers | (+3.24, -3.78, 1.10) | 1.24 × 0.37 | Low lockers |
| Port/aft mission bay storage | (-3.07, -3.90, 1.02) | 1.62 × 0.38 | Sheltered side storage |

These are **authored room dimensions**, not a claim that an 8.15m rectangular main deck fits the real 8.6m curved pressure vessel. Hull integration is deliberately postponed.

## 3. Three distinct low-g working points

| Work point | Render location | Function | Separation from acceleration seats |
|---|---|---|---|
| **Command stand** | (Y +0.26, Z -2.03), main floor | Anchored standing/leaning authority and briefings | NOT a seventh seat. Vacant during high-g |
| **Shared mission table** | (Y +0.21, Z -3.25), tabletop H≈1.06m | Route/mission discussion, collective planning, informal gathering | Separate from primary personal displays and command controls |
| **Independent mission workbench** | (Y -2.43, Z -3.17), low-g deck | Robotics, EVA, survey/samples and equipment work | Not Mission Ops' acceleration seat, which remains starboard/aft |

A workbench local display sits near the aft/port station; ship-condition display and mission map/plot are kept distinct. The shared table should be **low profile, stowable or secure-able** during acceleration. Its real mechanism has not been selected.

## 4. Access and observation geometry

- Three **low-g hand/foot-rung transfer concepts**: port and starboard command terrace transitions (~0.84→2.04 visual height); one Navigator platform transition (~0.84→1.20). These are rendered as visible handholds, **not ramps and not certified evacuation routes**.
- No intermediate structural mullions in the panorama. The conceptual observation edge is a **low handhold/sill arc** at radius 3.92m and H≈1.09m, roughly ±0.92 radians around bow.
- Perimeter light strips define circulation and deck heights without erecting full-height opaque partitions.
- The previously selected 37 replaceable external transparent panels, two seamless inner pressure domes and adaptive optogel are **NOT modified** by this interior sketch. They are not geometrically fitted to I4 here.

## 5. Smallest implementation order — executed

1. Import **I1’s six stations** and I3’s open-room concept; preserve paired Pilot+Captain and forward/lower Navigator.
2. Create exactly **one continuous working-deck slab**, **one broad command terrace**, **one forward NAV platform**. Do not spawn isolated seat podiums.
3. Install six illustrated acceleration seats, displays and a limited quantity of low cabinetry.
4. Add **three purposeful low-g work points**, minimal built-in equipment, handhold/rung geometry and observation sill.
5. Produce a **single, standalone Android-safe HTML Canvas2D 3D** with orbit/plan/side cameras and crew/display/deck/label toggles. Embed a static preview for script-disabled local Android viewing.
6. Test actual rendered frames on a 412-pixel phone viewport with WebGL/GPU disabled, and verify that the static image loads when JavaScript is disabled.
7. **Stop.** Do not claim structural integration or expand into an interiors platform.

## 6. What the render demonstrates versus what remains unproven

**Demonstrated visually:** coherent central deck; a raised two-person command group; distinct lower forward Navigator; three clearly separated side/aft specialist seats; central command stand; low mission table; separate equipment workbench; open observation direction.

**Not demonstrated:** actual 3D furniture/hull interference, true headroom and routes under acceleration, individual body-size fit, cockpit sightlines through actual canopy and sensors, sustained 4g biological tolerance, mounting or crash loads, accessibility of transfer rungs, final optical/radiative behaviour, or genuine crew-task completion. The illustrations are not scientific qualification.

**Stop condition reached for concept modeling** when one reproducible I4 scene and one phone-viewable, visibly populated interactive rendering exist, and the three working functions (command, shared collaboration, independent mission work) are spatially distinct.

## Reproducibility

- `render/make_l1_i4_command_commons.py` generates the single-file viewer and exact scene data.
- `command/L1_I4_COMMAND_COMMONS_GEOMETRY_20261029.json` records all coordinates and the minimal scene graph.
- `render/out/wayfarer_l1_i4_command_commons_android.html` is self-contained, with Canvas2D draw code and base64 fallback picture.
- `render/out/l1_i4_command_commons_preview.png` is the source image for the embedded fallback; the standalone HTML needs no separate PNG.

**Preserved as isolated research only.**
