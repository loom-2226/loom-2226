# Wayfarer v0.5.6 candidate: full package for Sol's review

ALL bodies. ALL sponsors. 2026-2226.

**NON-GOVERNING SANDBOX.** No canon promotion, no runtime integration. Do not put the amendment in canon/current/. PR #430 stays as is. Geometry sha256 `14bb3c2c3743811e020ba4288b5503392a362e0cc03948fc35bf181b6d629369`.

This release bundles everything since v0.5.1: the torch heat package and hot fins (v0.5.2), Sol's habitat (v0.5.3), and L1 layout D (v0.5.5), closed out in v0.5.6.

## kT's decisions (2026-10-25)

- **L1 layout D adopted.**
- **Torch-heat wording accepted.** Every declared assumption is now ACCEPTED.
- **Couches:** noted, not modelled. The intended shape is knees-up (Soyuz Kazbek-style); the checks keep the flat 2.10 m envelope.

## Gates

G1-G9, G11 and G12 pass (G4 and G6 with accepted declared items). G10 is OPEN until Sol flies the Navigator missions. `certified` stays false until G10 passes and both reviewers sign.

| Figure | Value |
|---|---|
| Dry mass | 867.7 t (unchanged) |
| Departure mass (S1) | 1,167.7 t |
| Worst trim | 0.347 deg (target 0.35, limit 0.5) |
| Engineering reserve | 42.6 t (46.5 t before) |

## What v0.5.6 adds

All new items are paid from the reserve: 3.86 t in total, ledger line `crew_systems_v056_t`. The checks are in `habitat/crew_systems.py` and are reported in G5, G7 and G9.

**L1 command deck**
- **Nose window frame.** A Cupola-style frame carries the 8 nose windows. Each window has four panes and an armour-equivalent shutter.
- **Splayed window openings.** Rendering D showed that the 20 cm armour in front of the panes cuts the pilots' 60 deg view to 89%. Splaying every opening 12 deg restores 99.7% (`command/l1_bore_check.py`). The L1 study now has 12 checks, all passing.
- **Window mass.** All 15 window assemblies now carry their own mass (2.89 t), scaled from the Cupola (1.88 t for 7 windows).
- **Flight-deck columns.** Four aluminium tubes (76 x 3 mm) hold up the flight deck. Buckling margin is 8.5 at 5 g x 1.5. Combined stress with a 0.5 g side load is 114 MPa against a 503 MPa yield.
- **Docking view.** Two cameras with lights at the collar, plus a 0.4 m window in the L5 vestibule. The ship now has 15 windows.

**Habitat**
- **Berths.** Now 2.10 x 0.70 m (were 2.00 x 0.75). This needs a 4 cm partition at r 1.9 m. **Sol to agree.**
- **Bunk loads.** Hard points need at least 3 kN ultimate each. Upper-berth posts have a buckling margin of 10.
- **Floors.** Every floor carries its deck at 5 g x 1.5.
- **Casualties move at 0 g.** The captain orders a coast. The litter goes along the ship's axis, through 2.05 m doors, down the port ladder shaft (rungs on its inboard face) and straight into the medical bay. Under thrust, the casualty is treated in their own couch or berth.
- **Medical opening.** Moved from 210 to 202 deg, which gives a litter 0.24 m clearance at the edge. **Sol to agree.** It is closed by bi-parting doors that seal against air and smoke; they are not a pressure boundary.
- **L4/L5 isolation.** Floor L4 becomes a pressure bulkhead. It needs 1.14 t of the 1.58 t allotted, at a factor of 2.0. Two hatches close the ladderways and a plug seals the trunk, so a depressurised L5 leaves the rest of the habitat pressurised (G9).
- **Storm shelter.** The 72 h stored backup for 10 people needs 0.22 t against 0.3 t allotted (consumption rates from NASA JSC 2015).
- **Berth water collar.** A 12 cm water collar now sits behind the edge of floor L3 (0.95 t, moved from the service tank; protected water total unchanged). Paying for the new items reduced the reserve that is spread over every part, which pushed the bunk radiation screen to 39.91 g/cm2. The collar restores it to 40.24 (minimum 40). **Sol to agree.**

**Crew acceleration doctrine**
- **4 g cap.** Sustained thrust with people aboard is capped at 4 g. NASA's OCHMO brief rates 4 g as tolerable for at least 60 min. 5 g stays the structural rating, for emergencies only. A full-remass HARD burn takes 46 min at 4 g.
- **Time on the back.** Burns longer than 2 h 45 min are split by a 30 min coast break ([V2 6113]; only EXPEDITE, at 183 min).
- **Ship card.** `accel_cap_g` is now 4.0.

## Viewer and images

- **New viewer modes:** Command deck and Habitat decks.
- **New stills:**
  - `cmd_cutaway`, `cmd_pov` and `ext_nose`: L1 layout D;
  - `hab_crew`: berths, the casualty route and the hatch;
  - `ext_docking`: the docking cameras and the vestibule window.
- **Render inputs.** Couches, crew, berths and doors come from `render/out/l1_scene.json` and `render/out/hab_scene.json`. Both are written by the checking scripts.

## For Sol

1. **Agree the four changes to his habitat package:**
   - berths 2.10 x 0.70 m with a 4 cm partition;
   - medical opening at 202 deg;
   - the floor-edge water collar;
   - the G7 rule of a berth per person.
2. **Fly G10:** E1, FR-01B-R and MV-01 in Navigator, using `out/wayfarer_v05_card.json`. The card's acceleration cap is now 4 g.
3. **Review** `habitat/crew_systems.py` and `command/l1_bore_check.py`.

Re-run everything with `./run_all.sh`.
