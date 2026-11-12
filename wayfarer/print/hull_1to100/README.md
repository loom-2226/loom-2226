# Wayfarer 1:100 printed hull: etch (print scale)

ALL bodies. ALL sponsors. 2026-2226.

Status: **PLACEHOLDER profile, untested.** This is print-scale geometry only (print
LOD). The canon GLBs keep their true-scale etch and are not touched.

## What's here

| File | What |
|---|---|
| `print_profile_1to100.json` | 1:100 printer limits. Groove 0.5 mm wide (= 50 mm real, per the approved finish table) and 0.24 mm deep; 2.0 mm shell; minimum hole 1.0 mm. `active` selects stock_0p4 or fine_0p2. |
| `hull_etch.py` | Builds the etch spec, the hull development drawing and the test coupon. Run `python3 hull_etch.py`. |
| `etch_spec_1to100.json` | Every approved hull mark in ship metres: 31 rings, 25 longitudinals, 117 outline circles (208-node faces on the cylinder, EVA hatch plug and frame, medical port frames), 17 window openings, 5 viewport bands, plus keep-clear zones. |
| `hull_development_1to100.png` | The whole hull cylinder (x 2.35 to 34.3) unrolled flat: 320 x 283 mm at print scale. |
| `coupon_L4L5_1to100.stl` | Curved test ring, x 8.0 to 14.2: 90 mm across, 62 mm tall. Covers the L4 medical ports (x 9.30) and the L5 EVA hatch. |
| `coupon_preview_1to100.png`, `make_preview.py` | Preview drawn from the same raster the STL is meshed from. |
| `manifest_1to100.json` | Triangles, volume check, watertight check, and the features dropped at this scale. |

## Sources

- **Seam grid:** kT 9 Nov, as encoded in `render/loomgl.js`.
- **Option B joints, EVA hatch frame and medical port frames:** `exterior_surface_2026_11_13`.
- **Groove width:** `canon_finish_2026_11_11`, amendment 4.
- **Windows, node faces, hatch and bands:** geometry `features` and `bands`. The medical ports sit at x 9.30.

The grooves stop at openings, at node faces and inside the hatch and port frames. The
20-degree joints stop at the bay-door edges.

- **Maintenance-panel outlines** (8): the approved 11 Nov canon-finish panels on the service, midship and aft skin.
- **Torch end** (`aft` in the spec, restating the approved 11 Nov canon finish at print scale):
  - Shield rings at x 34.7 and 38.9, plus 4 seams. These are hidden inside the thrust cone.
  - Reactor rings at x 39.7, 43.2 and 45.9, plus 4 access panels.
  - Five nozzle coil bands, 1.5 mm wide.
  - The thrust cone stays plain.
- **Bow shoulder:** clean, with no marks, per `bow_shoulder_surface_2026_11_13`.
- **Dropped at 1:100:** the 20 mm sub-panel lines would print at 0.2 mm. Option B's joints already sit on the same stations.

## Checks (stock_0p4)

- **Coupon:** volume PASS; watertight PASS (0 unmatched edges, conforming mesh, no T-junctions).
- **Dropped at 1:100:** the hatch latches (0.6 mm, below the 1.0 mm minimum hole). They come back with fine_0p2 or at 1:25.

## Printing the coupon (once the printer arrives)

- Stand it on end, bow end up, as exported; no supports.
- Use 0.08 mm layers. Ironing is off, because the outside faces are vertical.
- Look for:
  - ring grooves that stay crisp (these are layer-defined);
  - longitudinal grooves that stay open (these are perimeter-defined);
  - the 15.5 mm port openings, checking how much their tops droop;
  - the node-face circles (3.5 mm).

## Not covered yet

The protruding fixtures (rails,
grapples, RCS, sensors, strakes, fins).

**kT 2026-11-13: the model stays whole until the design is completely finished.** It is
not split into bed-sized print pieces until then. The etch spec is in ship coordinates,
so it applies to the whole model unchanged; splitting is the very last step before
printing.
