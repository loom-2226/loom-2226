# Wayfarer 1:100 exterior hardware (PROPOSAL, F4: sketch + numbers)

ALL bodies. ALL sponsors. 2026-2226.

Status: **APPROVED by kT 2026-11-13: 1 = a (exaggerate thin hardware), 2 = a (swappable bay doors + separate shuttle model)** (decision `exterior_hardware_1to100_2026_11_13`). `hardware_inventory.json` lists 61 exterior items, with
positions taken from the canon stowed/closed exterior GLB. `hardware_map_1to100.png` shows
them on the 1:100 hull development. This is print LOD only, with no canon, geometry or mass
change.

## Classes at 1:100 (stock 0.4 nozzle)

| Class | Items | Treatment |
|---|---|---|
| A: print as part of the hull | 8 RCS clusters, 2 sensor turrets, 2 laser terminals, 3 service ports, docking collar, stowed service arm, bow sensors | Printed as part of the hull, each 1 mm or more proud. Each gets a 45 deg chamfered underside so it prints on the upright hull with no supports. |
| B: engraved outline | 4 grapple plates (4 mm), docking target (3 mm), 4 RF arrays (14 x 10 mm), 4 vents | 0.5 mm groove outline. These are flush plates, 0.04-0.27 mm thick at scale. |
| C: too thin | 4 EVA rails (0.1-0.4 mm section), 24 crawler points (1.2 mm, 0.23 mm proud), 2 docking cameras (2 mm) | See decision 1. |

## kT decides

1. **Thin hardware (class C).**
   - (a) Exaggerate to the print minimum: rails become 0.5 x 0.5 mm ridges (50 mm real), crawler points become 1.2 mm pads 0.24 mm proud, cameras become 2 mm bumps.
   - (b) Engrave them as outlines.
   - (c) Leave them off at 1:100.
   - Claude: (a). They give the model its sense of scale, and ridges along the hull print cleanly on the upright hull.
2. **Shuttle and bay doors.** The shuttle sits behind the bay doors. The doors open to vertical in canon.
   - (a) Swappable door leaves (closed / open to vertical) plus the shuttle as a separate 1:100 model, about 130 mm, which sits in the bay. This is the same plug-in idea as the fins.
   - (b) Doors closed only; the shuttle becomes its own display model.
   - Claude: (a). The shuttle is the most detailed thing you've built, and open doors are how anyone would see it.
