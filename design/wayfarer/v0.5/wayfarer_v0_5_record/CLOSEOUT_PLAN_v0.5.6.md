# Wayfarer v0.5.6: close-out plan

**Status 2026-10-25: K1 and K2 decided by kT; sections 2 and 3 done (see CHANGES_v0.5.6.md). Changes from plan: casualty moves use the port ladder shaft at 0 g, not the trunk lift (a 2.0 m litter does not fit the 1.8 m trunk, and the flight deck sits over its L1 stop); crew thrust is capped at 4 g. Section 4 remains.**

ALL bodies. ALL sponsors. 2026-2226.

**NON-GOVERNING.** Written 2026-10-25 at kT's request: what remains before the full package (fins, torch, tanks, habitat, L1) goes to Sol for review with everything shown in the 3D viewer. Starting point is the v0.5.5 candidate, geometry sha256 `8002b4df904d354b9590f768cd5162008292f0bb13c7085cb10a2d323e2f8e56`.

## 1. kT's calls

| # | Call | Why it blocks |
|---|---|---|
| K1 | Adopt L1 layout D | The L1 work below builds on it |
| K2 | Accept the torch-heat wording (declared item `torch_heat`, PENDING) | Certification needs every declared item ACCEPTED |

Noted by kT on 2026-10-25, not modelled: the couches are meant to be knees-up, Kazbek-style (`command/L1_OPTIONS_v0.5.5.md`, item 8). In v0.5.6 this goes into the inputs as a note.

## 2. Claude's design pass (one pass, after K1 and K2)

**L1 command**
- Nose window frame: a Cupola-style frame carrying the 8 panes, with debris and pressure panes and external shutters. It must fix the armour-bore finding (`command/l1_bore_check.py`). Mass comes from the reserve.
- Flight-deck supports and the 5 g load path.
- Flight-deck access, and lowering an injured pilot.
- Time on the back: EXPEDITE (about 2 g, up to about 3.1 h) against [V2 6113]'s 3 h 15 min limit, and HARD duration at 5 g against the +Gx curve.
- Docking view: cameras, plus a window in the L5 vestibule.

**Habitat**
- Berths from 2.00 to 2.10 m. This is Sol's package, so it gets flagged to Sol.
- 5 g load paths for the bunks.
- Casualty route through the trunk goods lift, with the turn into each deck tested.
- An isolation hatch between L4 and L5, and a closure for the L4 medical opening.
- Size the 72 h shelter life support (accepted as a provision; it now gets numbers).
- Fix the stale `windows_note` in the inputs (it still says 4 forward and 2 in the lounge; the ship has 14).

**Fins, torch, tanks**
- No new design; carried forward as is.
- New masses (window frame, flight-deck structure, life support) come out of the 46.476 t reserve. Rerun mass, trim, tank-structure and fin checks.

## 3. Integration

- One build at v0.5.6. Run all 12 gates. Record the new hashes. Build one zip.
- Viewer: one page with everything.
  - Existing modes: Coasting, Metric HARD, Torch burn (fins), Shuttle out, Command deck.
  - New modes: a Habitat deck mode (bunks, doors, berth water ring, lift, ladders, medical opening) and a pilot's-eye view.
  - Refresh all stills.
- Docs: one `CHANGES_v0.5.6.md`; updated spec, canon amendment v2.4d, certification basis and README.
- One note for Sol.

## 4. After the release

1. kT looks at the image set. This is the human half of G12.
2. Sol reviews as second reviewer:
   - agrees the G7 change (a 5 g berth per person, no private cabins);
   - flies E1, FR-01B-R and MV-01 in Navigator for G10. His integration steps are the CIVSTATE database in the run context, a ship-card import, and mission fixtures.
3. Both reviewers sign and loom-gate passes. Only then does `certified` become true.
