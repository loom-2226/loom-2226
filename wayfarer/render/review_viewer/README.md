# Wayfarer v2.5.14 review viewer (artifact source)

ALL bodies. ALL sponsors. 2026-2226.

This is the source of kT's review viewer artifact ("Wayfarer v2.5.14 Review"). It is a
visual-reference tool only: it is not canon and does not govern anything.

- `index.html` is the viewer. It uses Three.js 0.160 from a CDN. The first-person
  **Walk** and **Fly** modes, full screen and landscape, and **Walter's patrol** were
  added 14 Nov 2026.
- `meta.json` holds the part descriptions and mass table the viewer reads.
- The viewer loads `glb/<name>.json` files, each `{"glb_base64": ...}` wrapping a GLB
  already in the repo: the six exterior detail states (radiators stowed / Metric / torch,
  crown gores stowed / closed), `interior_L1`..`L5`, `interior_deck_hatches` and
  `walter_L1`. These are not stored twice; regenerate them from `wayfarer/render/out/`.

## Walter's patrol (first person)

- **Walk.** Thrust gravity points aft, so "up" is toward the bow. Walter's eye is 0.6 m
  (a human's 1.6 m). Collision uses horizontal rays plus the r 4.05 m lining. Climb at
  the ladderways at 0 and 180 deg, r 1.45.
- **Light.** The nearest 8 emissive fittings (warm / task / screen / graphic) become
  point lights. There is bloom in first person, and a Day/Night switch.
- **Sound.** Synthesised: hull hum, the L4 life-support whir, the L5 airlock pump pulse,
  L1 console blips, paw clicks and a ladder clank.
- **Readout.** The current deck and room, plus the name of any tapped part.
- **Coast, 0 g (15 Nov 2026).** The `1g` / `0g` chip (or `G`) switches the torch off.
  The hull hum fades and dust motes hang in the air. Walter floats on his own momentum:
  - **Move:** the joystick pushes off with his paw jets (0.55 m/s2, slow air drag, 2.2 m/s cap).
    ▲ / ▼ (E / Q) float up and down.
  - **Turn:** drag turns any way up; Z / C roll.
  - **Walls:** he bounces softly off walls and the r 4.05 m lining (restitution 0.3), with a
    bump sound.
  - **Between decks:** he can drift up and down the ladderways.
  - **Torch back on:** he settles to the nearest deck, feet aft.

## Surface etch (14 Nov 2026)

- **What it shows:** the approved 1:25 surface library as relief on walls, floors and ceilings. `tex/surface_atlas.png` is built by `make_surface_atlas.py` from `wayfarer/print/surfaces_1to25/surfaces.py`, the same generator as the print tiles.
- **How it works:** in the shader, each fragment classifies itself by its normal: floor, ceiling, curved hull lining or radial partition. It takes its room from position (the room sectors in the geometry) and its tiles from `surface_map.json`. Corridors use W-B / F-4 / C-2.
- **Where it applies:** linings, partitions, the deck floors `floor_L1`-`L4` and the aft bulkhead (the L5 floor).

## Nacelles and selected node layout (19 Nov 2026)

- **Nacelles:** the viewer overlays the four nacelles, links and tail arms (PR #561, two-state D9 PASS) on the
  88ce19fc exterior: tucked in the torch radiator mode, out with the ring locked in Metric and Loom.
  `glb/nacelles_tucked.json` and `glb/nacelles_deployed.json` are built by `tools/nacelle_overlay.py` from
  `wayfarer/render/candidates/` (not stored twice). Layer: "Metric nacelles and aft ring (new)".
- **Nodes → Selected:** the 208 selected node faces booked in PR #563 (120 hull, 20 cone, 68 nacelles and ring),
  tucked or deployed with the radiator mode. Geometric proxy only, not PR #356 qualified.
- The released canon exterior GLBs are unchanged until kT signs off; the aft RCS cant (25 deg) is not yet in them.
- **Shuttle B4-S (20 Nov 2026):** the stowed B4-S (PR #567, rolled 90°) replaces the v1 shuttle in the bay view.
  `glb/shuttle_b4s.json` is built by `tools/shuttle_overlay.py` from `render/out/b4s_candidates/`.
- **Ship / Shuttle B4-S tabs (20 Nov 2026):** `shuttle.html` is the solo B4-S viewer, built by `tools/shuttle_tab.py` (not stored twice).
