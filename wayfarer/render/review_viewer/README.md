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
