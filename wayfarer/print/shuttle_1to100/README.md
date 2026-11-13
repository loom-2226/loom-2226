# Wayfarer shuttle at 1:100 (PROPOSAL, F4: survey + one decision)

ALL bodies. ALL sponsors. 2026-2226.

Status: **APPROVED by kT 2026-11-14: rotor blades (a), engraved outlines** (decision `shuttle_print_1to100_2026_11_14`). The shuttle is the **NON-CANON** v1 research shuttle
(`wayfarer/lab/shuttle/`; G8 full bay fit still OPEN). It is printed as a separate part, per
`exterior_hardware_1to100_2026_11_13` (2 = a). Survey: `shuttle_1to100_survey.png`, made by
`shuttle_survey.py` from the shuttle_v1 nodes inside the canon stowed/closed exterior GLB.

## What prints

- **As modelled (1 mm or more):** the 128 x 38 mm hull, belly heat shield, belly nozzles, tail magnetic-nozzle ring, rotor hub, stowed mast, intake and ducts.
- **Widened to 0.5 mm grooves:** seams and gullwing door edges, which are 0.17-0.4 mm at scale.
- **Hidden inside the hull, not printed:** crew pod, wheels, custody capsule, water tank and reactors.
- **Needs a decision:** the 4 stowed rotor blades, 56 mm long and 0.1-0.4 mm thick at scale.

## In the bay

- The bay bore is 48 mm across and the shuttle 38 mm, so it lifts out through the open doors.
- It lies on its side, as integrated: nose forward, with the **gullwing crew door up** toward the bay doors, the spine and blades to starboard and the belly heat shield to port. Opening the bay doors shows the crew door.
- How it sits in the bore (cradle or pegs) is drawn with the print files.

## kT decides

Rotor blades:
- (a) engrave as outlines in the spine groove;
- (b) thicken to 0.5 mm raised strips;
- (c) leave the groove empty.

Claude: (a).

## Print file (PLACEHOLDER profile, untested)

- **File:** `parts/shuttle_v1_1to100.stl`, made by `shuttle_print.py` and checked in `shuttle_print_manifest.json`. Preview: `shuttle_print_preview.png`.
- **Size:** 128 x 38 x 38 mm, printed **standing on its tail**, nose up, with no supports.
- **Checks:** watertight (0 unmatched edges); volume 98.8% of the plain lathe hull. The difference is the spine groove and seams.
- **Built from the source numbers** in `shuttle_v1_full_docked_G8.py`: the lathe profile, the door and heat-shield sectors, the spine groove (2.6 mm deep), the seams, the upper blade pair and the belly nozzles. Nothing is traced from the display mesh.
- **Features:**
  - Seams and door outline as 0.5 mm grooves.
  - Heat-shield edge lines.
  - The spine groove, with the two upper blades engraved as outlines.
  - Four belly-nozzle pits, 3.2 mm across.
  - The nozzle-ring band on the tail face.
- **Not yet drawn:** how the shuttle sits in the bay bore (cradle or pegs). It goes with the whole-model sockets at the end.
