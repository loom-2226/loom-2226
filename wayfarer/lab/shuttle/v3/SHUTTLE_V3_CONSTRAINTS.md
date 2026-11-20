# Shuttle v3: constraints (step 1 of 7)

ALL bodies. ALL sponsors. 2026-2226.

DRAFT for kT, 2026-11-20. Every Wayfarer number below is read from `main` after the B4-S merge (PR #567);
the machine-readable register is `shuttle_constraints.json`, the picture `shuttle_v3_constraints.png`.
The aim: a shuttle that passes these on paper cannot be killed when Sol fits it into Wayfarer.

## 1. Classes

| Class | Meaning |
|---|---|
| HARD | installed Wayfarer geometry, canon, or physics |
| CRITERION | an enforced certification margin (`cert_criteria.json`); changing it is a kT / class:governance decision with a stated basis |
| POLICY | a number kT chose |
| CANDIDATE | an engineering value that can be resized at a mass cost |

## 2. Wayfarer fit and mass (the shuttle's box)

**Fit**

| Id | Class | Constraint | Value |
|---|---|---|---|
| F1 | HARD | bay length | x 18.25–32.05 m (13.8 m) |
| F2 | HARD | bay bore | r 2.4 m about the ship axis |
| F3 | HARD | exit slot | 4.8 m wide on +Z; clamshell doors open to vertical at the slot edges |
| F4 | HARD | upper longerons | d 0.4 m tubes at y ±2.75, z 2.6 |
| F5 | HARD | strake grooves (40°, 140°) | ~2.42 m from the exit-path centre line |
| F6 | HARD | hot fins | x 34.3–53.3 m, 2.25 m aft of the bay, ≥ 1.0 m from the slot edge lines |
| F7 | HARD | docking | pressure-tight transfer tunnel ends at a nose port, x 18.75 m on the bay axis: the shuttle docks nose-first on its long axis |
| F8 | CRITERION | radial clearance | ≥ 0.25 m → stowed section inside r 2.15 m |
| F9 | CRITERION | axial clearance | ≥ 0.5 m each end → stowed length ≤ 12.8 m, nose port included |
| F10 | CRITERION | exit-path clearance | ≥ 0.5 m → width across the slot, stowed, ≤ 3.8 m |
| F11 | HARD | exit | back 0.5 m off the port, rise +Z through the slot; any roll attitude |

**Mass and loads**

| Id | Class | Constraint | Value |
|---|---|---|---|
| M1 | HARD | Wayfarer dry mass and ECON reach fixed | 868.192255 t, 707.845 km/s: every shuttle tonne comes from the reserve |
| M2 | HARD | reserve above the floor today | 31.96 t (shuttle booked at 36.48 t) |
| M3 | POLICY | reserve floor | 16.8 t |
| M4 | POLICY | docked-dry envelope 37 t | kT-approved assumption, **not physics**. Proposed: retire it; M2, M5–M7 set the real ceiling |
| M5 | HARD | ship design ultimate load | 5 g × 1.5 = 7.5 g; the berth holds the shuttle at 7.5 g |
| M6 | CANDIDATE | berth latches | 4 × 0.75 MN → 40.8 t at 7.5 g (lug shear 48.9 t); bigger latches cost reserve |
| M7 | CRITERION | ship thrust trim (G3) | ≤ 0.5°; worst today 0.356° |
| M8 | HARD | shuttle propellant from Wayfarer remass | **−3.25 km/s of Wayfarer ECON reach per tonne** unless refilled (23.1 t = 74 km/s) |
| M9 | HARD | hold space | 56.1 m³ for the 50 t payload and the Venus kit |

**Derived envelope for any v3 design**

- Stowed length ≤ 12.8 m, nose port included.
- Stowed section inside r 2.15 m, and ≤ 3.8 m wide across the slot (it may ride rolled).
- Anything wider than 4.3 m (wings, fins, floats) folds or retracts for stowage.
- Mass ceiling set by M2, M6, M7 (not M4).
- Propellant carried from Wayfarer is expensive (M8): refilling from oceans, ice and ports is a design lever, not an extra.

## 3. Reference missions (physics; kT sets the targets)

| Id | Mission | Physics (standard values) | kT to set |
|---|---|---|---|
| R1 | Earth: sea or land to orbit and back, courier pickup | g 9.81 m/s², 1.01 bar, 288 K, orbital speed 7.8 km/s | passengers, cargo t, max wave height, turnaround |
| R2 | Venus surface stint (Venus kit) | g 8.87, 92 bar, 737 K, orbital speed 7.3 km/s | must it climb back to orbit unaided? stay time |
| R3 | Titan: lake and dune landings | g 1.35, 1.47 bar, 94 K, orbital speed 1.4 km/s | lake ops (float, take off from liquid methane) |
| R4 | Mars | g 3.71, 0.006 bar, ~210 K, orbital speed 3.4 km/s | landing sites, stay |
| R5 | Moon and other airless bodies | g 1.62, vacuum, orbital speed 1.7 km/s | terrain (VTOL only) |
| R6 | Icy moons (Europa class) | g 1.31, vacuum, orbital speed 1.4 km/s | ice landings, water refill |
| R7 | "Get out fast" | from landed to climbing in N minutes, anywhere in R1–R6 | N, and whether abort-to-orbit is required |
| R8 | Passenger leg | 6 seats (kT 2026-11-19) | trip length, comfort level |

Surface-to-orbit Δv with losses, thrust needed, and the propellant each mission eats are computed in step 2, not guessed here.

## 4. kT decisions (2026-11-20, kt_decisions `shuttle_v3_constraints_2026_11_20`)

1. G8 margins F8–F10: **keep**.
2. 37 t envelope (M4): **retired**; ceiling from reserve, berth and trim.
3. Reserve share: **up to 50%** of the reserve above the floor (≈ 16.0 t) on top of 36.48 t → docked-dry ceiling **≈ 52.5 t**, berth latch upgrade included.
4. Ocean/ice refill: **preferably no**. Design on Wayfarer-supplied water and port refills.
5. Venus ascent: **the Venus kit may supply it**.
6. Water (2026-11-20): **option D**. The shuttle lands on, floats on and takes off from water, is watertight to ~10 m (survives swamping or a brief dunk), and **deploys and recovers the rover capsule from the water**. The Venus Ti capsule doubles as a submarine ("deep kit"). The whole shuttle is not a submarine.
7. R1–R8 targets: open.

### 4.1 Water constraints that follow from decision 6

| Id | Class | Constraint | Basis (`water_check.py/.json/.png`) |
|---|---|---|---|
| W1 | POLICY | Watertight to 10 m: every door, hatch, fold and vent seals at ~2 bar outside | kT D |
| W2 | HARD (physics); amended kT 2026-11-21: **hull + pop-out floats ≥ 111 m³, hull alone ≥ ~74 m³** | Floats with **≥ 50% reserve buoyancy** at the heaviest water-landing mass. At the 52.5 t ceiling + 23.1 t water (75.6 t) that is **≥ 111 m³ watertight volume**. B4-S's 82.45 m³ gives only 12% there (42% at 36.5 t + full water) | Archimedes, seawater 1.025 t/m³; 50% is a common small-craft reserve |
| W3 | HARD (physics) | Torch and belly-thruster exits sit **above the floating waterline plus 1 m of wave** at that mass, so it can light up and leave from the water | the torch cannot start submerged |
| W4 | HARD (design) | Capsule leaves and returns **while afloat in 2 m waves**. The side door is in the lower flank (below the waterline), so the rover bay becomes a **floodable well**: bulkhead to the cabin rated for W1, the bay's volume counted out of W2 when flooded | B4-S door x 8.45–11.7 |
| W5 | CANDIDATE | Capsule submarine: rated **~600 m** (92 bar ÷ 1.5 safety factor). Near neutral already: 6.7 m³ displaces 6.9 t of seawater; shell + fittings 4.5 t, so outfit, crew, thrusters and a small trim tank close it to neutral. Tether or acoustic link to the shuttle | kit masses from b4s_mass.json |
| W6 | HARD (physics) | Upright and stable afloat, door side included, with the well flooded and with it empty | step 3/5 hydrostatics |

W2 is the big one: a hull that floats well at full load needs ~111 m³, which feeds straight into the step 3 shape trade and also gives the cabin and water the room B4-S lacks.

## 5. Original questions


1. Keep the G8 margins F8–F10 (0.25 / 0.5 / 0.5 m) as they are? (Recommended: keep. They are enforced; changing them needs a stated basis.)
2. Retire the 37 t envelope (M4) and use the reserve, berth and trim limits instead? (Recommended: yes.)
3. How much of the 31.96 t reserve may the shuttle spend in total?
4. Refuelling: must the shuttle be able to refill water from oceans or ice? (It cuts the M8 cost.)
5. Venus: must the shuttle climb from the surface back to orbit on its own, or may the Venus kit provide that?
6. Set the R1–R8 targets.
