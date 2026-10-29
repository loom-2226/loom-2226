# Wayfarer L1 — three furnished interior iterations
**2026-10-29 · RESEARCH · NON-CANON · NON-RUNTIME · CONCEPT GEOMETRY**

## Origin and brief

This follows the user-selected F1-R2 tiered command arrangement: **Pilot and Captain/Commander side by side on the elevated tier; Navigator forward/lower; Engineering, Sensors/EW and Mission Ops each retain an acceleration seat; a separate low-g mission workbench replaces the old S4 station location**.

User's requested change is to design a convincing *room*, not merely change chair positions. Freeform room topology is allowed; existing source Rev7 hull, source mezzanine, ladders and canopy need not bound this concept pass. The research source PR #432 was OPEN at head `3485830a56dfead79b2ef8bba031a595b536fbb5` at bootstrap and was not changed.

## Three authored iterations

| Variant | Specific treatment | Most useful advantage | Main issue |
|---|---|---|---|
| **L1-I1 Unified Terraced Commons** | One large connected lower operations floor; raised two-seat Pilot/Captain platform; separate forward Navigator platform; built-in stores, shared status workpoint, perimeter handrails and lighting | Most immediately coherent crew room and easiest-to-understand operational geography | Illustrative tier-transfer connectors need real low-g and acceleration access design |
| **L1-I2 Central Command Spine** | Compact central walkway/information spine flanked by left and right specialist galleries; raised command bridge, forward Navigator and relocated sheltered specialist workbench | Strong differentiation of command, flight and detailed subsystem work | Risks visual separation and obstructive equipment in panoramic cabin |
| **L1-I3 Panoramic Observation Commons** | Wide continuous common floor, extended raised command balcony, peripheral specialist stations, common map table and independent equipment work bay | Best starting point for shared observation, conversation and habitability | Generous open volume still needs restraints/anchoring and emergency flow testing |

All variants have **six independently positioned contoured acceleration seat models, individual screens, a central low-g command workpoint and a distinct mission workbench**. They include visible connected-tier geometry, local lighting strips, handrail elements, built-in cabinets/status furniture and differing floor arrangements. The existing raised Pilot+Captain selection remains visible in each, with small positional adjustments only for the third iteration and specialist wings of the second.

## Viewer and reproduction

- Generator: `render/make_l1_three_interior_iterations.py`
- Complete authored scene state: `command/L1_THREE_COMPLETE_INTERIOR_CONCEPTS_20261029.json`
- Single-file Android-safe interactive 3D: `render/out/wayfarer_l1_three_furnished_interiors_android.html`
- Viewer includes an embedded PNG fallback, generated directly from its I1 scene; needs **no WebGL, no external libraries and no network**.
- Buttons I1/I2/I3 switch actual 3D geometry, not just labels. Orbit / deck plan / side and touch orbit/pinch/zoom remain available; crews, screens, decks, and labels can be toggled.

## Verification

Tested generated HTML in headless Chromium software mode, explicitly **GPU and WebGL disabled**:
- **412 × 915 mobile emulation:** three distinct scene-image SHA hashes; 412 × 493 canvas drawing, all six role seats and separate workbench present.
- **1260 × 940 desktop:** three distinct scene-image SHA hashes.
- JS exceptions / console errors: none in tested run.
- No JavaScript: static preview PNG embedded in HTML still loads and displays; image native dimensions 600 × 404, source screenshot inspected.
- Script compile and extracted JavaScript syntax checks pass.

Not tested in the user's physical Android app/local document viewer. If that environment suppresses scripts, static preview should be visible, but interactive switching may not run. No guarantee for browser-specific device limitations.

## Critical limitations and recommendation

These are lightweight **three-dimensional schematics of inhabited interiors**, not finished or pressure-hull-fitted mechanical designs:
- No 3D swept-crew collision analysis, quantified walkway widths, seat body-size fit, 4g duration tolerance, crashworthiness, mounting loads, environmental thermal/radiation review, or canopy sensor visibility test.
- The sloped deck connectors are *indicative geometry* and cannot be interpreted as safe ramps or ladders.
- Floor and storage mass, support structure, pressure boundary integration, deck levels under gravity/thrust and fire/emergency access are unresolved.
- The three-room comparison is **qualitative and visual**, not simulated task performance.

**Provisional visual preference:** I1 provides the strongest coherent operational foundation; I3 could donate openness and observational/common-space qualities. No measured functional winner yet. A sensible next action is to use I1 with I3's social features and actually rehearse a flight task before further structural detail. Stop rather than expanding into a broad interiors tool framework.

No canon, governing PR, or simulation runtime changes.
