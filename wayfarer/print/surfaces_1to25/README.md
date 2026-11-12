# Wayfarer interior surfaces, 1:25 (swappable)

ALL bodies. ALL sponsors. 2026-2226.

Status: **PLACEHOLDER, best guess, untested.** No printer yet. The surfaces are
drawn to a conservative profile for the stock 0.4 mm nozzle on the Bambu Lab A2L.
They are built to be swapped out once the test sheet has been printed.

## How the swap works

| File | Role |
|---|---|
| `print_profile.json` | Printer limits (min line, groove, slot, hole, relief). `active` selects the profile. |
| `surfaces.py` | Draws 11 surfaces at their **ideal** real-world size, then clamps each feature up to the active profile. |
| `tiles/<ID>.stl` | One 40 x 40 mm tile per surface (1 m x 1 m real). This is the swappable unit. |
| `surface_map.json` | Which wall, floor and ceiling each of the 22 rooms and the corridors use. Deck print files reference IDs only. |
| `surfaces_manifest.json` | Generated: per-tile triangles, volume check, and every feature that was clamped. |
| `wayfarer_1to25_surface_test_sheet.stl` | All 11 tiles plus the L detail ladder on one 175 x 151 mm plate. |

To update after the test print: edit the numbers in `print_profile.json` and run
`python3 surfaces.py`. Every tile, the sheet and the manifest regenerate. Rooms
pick up the change through `surface_map.json`. If a 0.2 mm nozzle is bought, set
`active` to `fine_0p2`. Nothing is clamped on that profile, so every feature
prints at its ideal size.

## Surfaces

| ID | Surface | Used in |
|---|---|---|
| W-A | Habitat lining | Command, wardroom, observation, cabins, shelter/wellness |
| W-B | Service lining | Galley, exercise, washrooms, medical, corridors |
| W-C | Utility wall | ECLSS, suit room, workshop, stores |
| W-D | Bulkhead frame | Airlock, vestibule, custody vault, hatch frames |
| F-1 | Smooth deck | Living rooms, medical, custody |
| F-2 | Ribbed deck | Wet rooms, galley, exercise, suits, workshop |
| F-3 | Grated deck | ECLSS, airlock, stores, vestibule |
| F-4 | Corridor walkway | Ring corridors, all decks |
| C-1 | Living ceiling | All living and wet rooms |
| C-2 | Corridor ceiling | Corridors, medical, vestibule |
| C-3 | Technical ceiling | ECLSS, L5 working rooms |

On `stock_0p4`, five features are clamped above their ideal size (slat grooves,
seams, small fixings; see the manifest). These are the ones to recheck against
ladder tile L.

## Printing the test sheet (once the printer arrives)

Print flat with the detail face up. Use the 0.4 mm nozzle, 0.08 mm layers, matte
light PLA and ironing on; no supports are needed. Report back with a low-angle
photo, plus the narrowest clean raised line and groove on tile L and the
shallowest visible depth step.

## Mass

These are linings, so they come out of `outfit_<deck>`. There is no new mass and
no canon change; the hull and dry mass are untouched.
