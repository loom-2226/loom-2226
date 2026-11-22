ALL bodies. ALL sponsors. 2026-2226.

# Weave shuttle "Tic Tac": build-out v1

**Decisions:**
- kT, 2026-11-22: "Tic tac. It is." Recorded as `shuttle_weave_tictac_hull_2026_11_22`.
- Sol's rulings on 5062961, forwarded by kT, recorded as `shuttle_weave_tictac_rulings_2026_11_22`.

**Status:** NON-CANON lab design. CCR-2026-0005 (PROPOSED) needs a proposal revision: hull text, collar withdrawn. Its physics scope is unchanged.
**Code:** `tictac_v1.py` → `tictac_v1.json`; `tictac_v1_figures.py` → `weave_tictac_v1_vehicle.png`, `weave_tictac_v1_checks.png`.

![Vehicle](weave_tictac_v1_vehicle.png)

## 1. Rulings

| Item | Ruling |
|---|---|
| Diameter | **3.8 m.** That is the F10 exit limit, which already includes 0.5 m each side. Nothing may protrude beyond the diameter. |
| Rover | **Removable mission kit**, about 1.8 t, not in base dry mass. It rides in a combined cargo/rover bay behind a flush side door. |
| Field-off take-off from water | **Limitation accepted.** W3 is recorded as an **EXCEPTION, not a pass**. Field off afloat is a stable wait for a restart or Wayfarer recovery. No extra propulsion is added. |
| Titan | **Tank-level rule plus an optional flotation kit.** No permanent floats. Sea landings stay restricted until equipped. |
| Look | Continuous, smooth, warm-white hull. Flush nose docking interface and cargo door. No visible wings, engines, antenna farms, decorative lights or unnecessary panel lines. Comfortable inside. Empty volume stays empty. |

## 2. The vehicle (12.8 × 3.8 m)

**Mass:** 45.4 t dry, 7.1 t under the 52.5 t ceiling. That includes 2.4 t of parachutes. With the rover kit aboard the margin is 5.2 t.

**Kept from the selected shuttle:** the 8 t module with its flywheel, the 23.1 t tank, the torch, cabin, avionics and custody.

**Power:** a 1.0 t unit for cooling and flywheel recharge (ASSUMPTION).

**Climb water (Earth, with the cushion):** 19.0 t, or 20.6 t with the rover, from the 23.1 t tank.

**Layout, fore to aft:**
- **Nose dome:** the docking hatch sits on the axis, with a 0.8 m passage from the tip. This fixes the B4-S-family nose-passage gap. Avionics and parachutes share the dome.
- **Cabin:** 31 m³, more than the 21 m³ needed. Six couches, 3 abreast × 2 rows, with 2.63 m headroom.
- **Module bay:** the 8 t core cube and the flywheel drum. The rest of the bay is empty.
- **Cargo/rover bay:** 27 m³, 3.45 m long. It holds either the rover kit (3.0 × 1.9 m) or a rigid 6 m³ cargo box.
- **Aft dome:** torch, power unit and RCS.

**Water:** 30 m³ of cells below a continuous deck (z −0.85 m) and in the lower domes. 24.3 m³ is needed.

**Empty space:** 47 m³ after every need, left empty on purpose.

## 3. Sol's checks: what passes and what stays open

![Checks](weave_tictac_v1_checks.png)

| Check | Status | Result |
|---|---|---|
| Floating upright | **OPEN RULE** | **Basis:** every section is a circle about the axis, so roll GM = −z_CG exactly, less free-surface effects. **Full tank:** 0.46 m. **Full tank, rover aboard, dock flooded:** 0.41 m. **Light:** 0.08 m. **Light, rover aboard, dock flooded:** 0.04 m. **Flooding the whole bay** is unstable when light (−0.13 m), so it is rejected. Only a rover-sized **wet dock** (3.4 × 2.1 m) beside the door floods. **Rule:** when afloat light, take on 12–13 t of sea ballast before opening the dock (GM 0.3 m). It is an operating requirement, not yet a demonstrated procedure. |
| Waterborne cargo/rover access | PASS (design) | The deck is 0.5–1.0 m below the waterline, so the dock floods and the rover floats in and out. |
| Field fails in a slow hover | **OPEN (assumption)** | No recovery 5–32 m, then parachutes. With slower inflation the gap is 46–66 m; the selected shuttle's was 5–47 m. The parachutes need about **17,400 m²** of effective drag area (roughly a dozen 50 m canopies) inflating in 2.5 s from a hover. That is a screening assumption, not a demonstrated capability. The torch is not credited, because its axis is horizontal. |
| W3: torch clear of the water | **EXCEPTION** | The axis torch sits at the waterline afloat. Field-off take-off from water is not possible: the accepted state is to wait. |
| Bay exit (exact fit) | PASS | 3.8 m equals the F10 limit; r 1.9 ≤ 2.15 (F8); 12.8 m (F9); any roll; no collar; Wayfarer unchanged. Nothing may protrude. |
| Titan lakes | **RULE** | Landed with ascent water only (50 t): reserve 43% in Ligeia-like liquid (551 kg/m³) and 16% in methane (447 kg/m³). A full tank sinks in methane. The 50% reserve needs a 6 m³ kit (Ligeia) or a 38 m³ kit (methane); landings stay restricted until equipped. |

## 4. Next

- CCR-2026-0005 proposal revision 2 (governance PR).
- Corrected operating card.
- One 3D model for kT's visual approval.
- Then fly her.
