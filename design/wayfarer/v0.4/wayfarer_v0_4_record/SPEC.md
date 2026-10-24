# Wayfarer v0.4 design record

ALL bodies. ALL sponsors. 2026-2226.

**Status: NON-GOVERNING SANDBOX.** Canon was set aside at kT's request (2026-10-24); physics was kept. This is not canon and not engineering closure. Every number comes from the scripts in this folder; every assumption is authored and visible in the JSON files. Setting: 2226 technology baseline.

Recorded 2026-10-24, from one design session with Claude.

---

## 1. Wayfarer v0.4 (mothership)

Layout `CWRAP_G|SPLIT|STRAKE_QUAD|ACCORDION|1300K|ext0|centre` (run by `wayfarer_v4.py`, reusing `optimize_v3.py` unchanged).

| Item | v0.4 | v0.3 (old shuttle) |
|---|---|---|
| Length | 54.9 m | 54.0 m |
| Dry mass | 872.8 t | 867.7 t |
| Delta-v (ECON, base) | 719.2 km/s | 722.7 km/s |
| Delta-v with Venus kit in hold | 710.6 km/s | n/a |
| Cruise acceleration | 0.988 g | 0.992 g |
| Metric clearance radius, FAST / HARD | 6.5 / 6.5 m | 6.5 / 6.5 m |
| Torch-rated radiator capacity | 422 MW | 403 MW |
| Hull heat load in HARD | 1.11 MW | 1.06 MW |

Arrangement, nose to tail (x in metres):
- 0-14: habitat, radius 4.3 m; hull skin radius 4.5 m to x = 35.9.
- 14-18: service region; fore plant block (x 14-18, radius 2.0 m); docking collar at x = 16.
- 18-30.5: wrap-around (C-shaped) water tanks, r_in 2.45 m, r_out 4.3 m, a slot 4.8 m wide along the top, four 2 m x 0.5 m grooves on the diagonals for the radiator strakes; 25.85 m2 of tank section per metre.
- 18.25-33.65: shuttle bay, a round bore 4.8 m across, on the ship's axis; shuttle at x 18.75-33.15, nose forward toward the docking collar.
- 33.9-35.9: aft plant block (radius 2.0 m). Plant 88 t, split in two blocks.
- 14-33.9: four accordion heat-pipe radiator strakes on the diagonals (45/135/225/315 deg), 2 m pleats, 12 pleats, 1,300 K; stow flush in the grooves.
- 35.9-40.9 shield, 40.9-47.9 reactor, 47.9-54.9 nozzle (torch chain kept from the repo reference).

Mass ledger change: `planetary_launch` 33 t -> 35.3 t (shuttle dry 34.1 t plus two drones of each type in pods, 1.2 t). Venus balloon kit (12.5 t, about 77 m3) is hold payload, loaded only for Venus surface trips.

Why the tanks got shorter: the round shuttle needs only a round bore, which leaves more tank per metre (25.85 vs 21.0 m2/m), so the tanks run 12.5 m instead of 15 m.

## 2. Shuttle v0.2 ("landing shuttle")

Design key `TORCH150 | BICONIC | CABIN_DRIVE | BALLOON`, closes all nine round trips from Wayfarer's parking orbit, everything carried from orbit (`shuttle_final.py`).

- Shape: round Starship-style biconic with flaps, 4.3 m diameter, 14.4 m tall, lands tail-down on four legs. Belly tiles; enters belly-first, flips, lands on the torch.
- Mass: 34.1 t empty (canon had 33 t). Water capacity 28.3 t. Up to 70.0 t fuelled (Venus surface trip).
- Engine: fusion torchlet on water, 10.5 GW jet (150 kW/kg), exhaust 5-20 km/s traded against thrust like Wayfarer's torch modes.
- Crew: 6 normal; 10 for a short evacuation hop.
- Rover: the crew cabin is the rover. Six-seat hardened cabin (titanium pressure hull, 32 mm wall, 3.1 m across with insulation, 5.2 t of hull and insulation) on its own 1.6 t chassis; drives out of a side door on a lift.
- Heat shield: rigid tiles, 1.6 t; flaps and aero surfaces 0.7 t. Peak entry g: Earth 2.8, Venus 2.6, Mars 0.9.
- Bay needed in Wayfarer: 15.4 m long, round bore 4.8 m.

Mass breakdown, empty (t): cabin, crew kit and systems 7.1; cabin chassis 1.6; hardened cabin hull and insulation 5.18; tanks 0.85; torchlet 7.25; legs 2.07; flaps 0.74; heat shield 1.64; Venus-proofing of the rest 0.08; structure 3.18; growth margin 4.45. Venus balloon kit 10.4 t (+20% margin = 12.5 t) carried only on Venus surface trips.

Trips (start mass in orbit; ascent delta-v):

| Trip | Start mass | Water used | Ascent delta-v |
|---|---|---|---|
| Ceres | 36.1 t | 1.9 t | 0.47 km/s |
| Moon | 41.4 t | 7.2 t | 1.79 km/s |
| Callisto | 41.6 t | 7.4 t | 1.83 km/s |
| Titan | 43.7 t | 9.5 t | 4.11 km/s |
| Mars | 46.2 t | 12.0 t | 3.96 km/s |
| Mercury | 48.3 t | 14.1 t | 3.24 km/s |
| Venus clouds (cloud city) | 55.7 t | 21.5 t | 9.11 km/s |
| Earth | 62.5 t | 28.3 t | 10.73 km/s |
| Venus surface | 70.0 t | 23.2 t | 9.11 km/s from 55 km |

Decks, bottom to top (concept layout): torchlet 0-1.4 m; water 1.4-3.8 m (fuel, neutron shield between torch and crew, Venus heat sink); cabin deck 3.8-7.4 m; drone bay and avionics 7.4-8.2 m; Venus kit or ~75 m3 cargo 8.2-13.0 m; docking nose and hatch 13.0-14.4 m. Volume budget is tight: 148 m3 needed of about 150 m3 usable.

The shuttle fuels from Wayfarer's water before each trip. An Earth trip (28 t) taken from torch remass costs Wayfarer about 73 km/s of reach; otherwise it uses most of the 50 t protected reserve. Canon makes Venus water-poor, so arrive full.

## 3. Venus surface trip (the landing version)

1. Undock in a 250 km orbit; small deorbit burn.
2. Enter belly-first; peak about 2.6 g.
3. Fall through the cloud deck (55 km, 0.5 bar, 27 C).
4. Touch down at 92 bar, 462 C; air so thick it arrives at about 18 m/s; short torch burn.
5. Cabin drives off for about 12 h; about 9 kW of heat leaks in; the water tanks soak it up.
6. Cabin back aboard; a hydrogen balloon (radius 26.7 m, about 54 m across; 3.5 t gas, 5.4 t envelope, 0.5 t rigging, 1.0 t dewar) lifts the whole shuttle to 55 km over several hours. Hydrogen is safe there: no free oxygen.
7. Drop the balloon, fall clear, light the torch.
8. About 9.1 km/s back to orbit, about 4 minutes of burn.

Why not rocket straight off the surface: computed 23-29 km/s, half drag and half gravity, so it never closes. Chemical exhaust slows from 3.6 to 1.7 km/s at 92 bar; nuclear thermal cannot fire at all.

Alternative kept on file: rover-drop plan (shuttle docks at a cloud city; a 4.6 t two-seat hardened rover drops and floats back on its own balloon): 51 t on the 2226 baseline.

## 4. Drones v0.1 (two types)

| | Mars drone | Dense-air drone (Titan, Venus clouds, Earth) |
|---|---|---|
| Mass | 80 kg | 60 kg |
| Rotors | 3 coaxial pairs, 3.0 m | 3 coaxial pairs, 2.5 m |
| Power | 4.9 kWh battery, 3.9 m2 fold-out solar, laser receiver | 4.6 kWh battery, 55 W nuclear battery |
| Range per charge | 43 km | 158 km (Titan 2,560 km) |
| On station | 18 min alone; unlimited under the shuttle's laser | 1.2 h (Titan 38 h) |
| Carries | 6 kg | 5 kg |
| Folded | 2.4 x 2.1 x 0.7 m | 2.1 x 1.8 x 0.7 m |
| Drop pod from Wayfarer | 395 kg: 3.5 m umbrella + small rocket pack, mid-air release | 204 kg: 3.1 m umbrella + parachute, mid-air release |
| Per Wayfarer drone berth (1.75 t) | 4 | 8 |
| Shuttle mass added to carry one | +0.38 t | +0.28 t |

Roles: scout ahead (40 km out and back), overwatch and relay (1 h), fetch a 5 kg sample case (10 km loaded), survey alone for 30 days at 20 km/day. At Venus the drone works at cloud level only and cannot hold station against 60 m/s winds: scout and survey there, not overwatch. One-drone-for-all alternative: 190 kg winged hybrid, 4.65 m rotors, 10 m wing, too big for a side bay.

## 5. 2226 technology baseline (authored)

- Torchlet: 2 GW of jet power per tonne plus 2 t fixed; 5-20 km/s exhaust; magnetic nozzle treated as ~400 bar against ambient air.
- Batteries 600 Wh/kg; nuclear batteries 8 W/kg; fold-out solar 1.5 kg/m2 at 35%.
- Heat shields: areal model from the Laub & Venkatapathy correlation, calibrated to a Shuttle-orbiter-like entry (~10%).
- Venus hardening: titanium spheres sized against buckling (knockdown 0.25, safety 1.5, hot modulus 90 GPa); insulation 0.05 W/m K, 0.1 m.
- Growth margin 15%; structure 12%; dry mass cap 100 t for a shuttle.

## 6. Checks run

- Ascent model vs known figures: Earth 9.9 km/s (reference 9.3-10), Mars 4.0 (NASA Mars ascent vehicle 3.9), Moon 1.8 (1.87).
- Winner re-flown at its own mass: tables slightly pessimistic.
- Drone rotor model vs the Mars Science Helicopter: power per kg within about 10%.

## 7. Open items

- Lift to lower the 12 t cabin to the ground; crew path from the nose hatch through the kit bay.
- Mars landing burn from about 1.2 km/s: big plume near ports.
- Torchlet power density is the biggest lever (0.5 GW/t gives a 131 t shuttle in the v0.1 runs).
- Torch heat deposition (inherited from Wayfarer's torch).
- Venus drone recovery and relay in 60 m/s winds; rover pickup timing for the rover-drop plan.
- Radiative entry heating not modelled; Titan atmosphere is a fit.

## 8. Sources

- Venus atmosphere (VIRA): https://en.wikipedia.org/wiki/Atmosphere_of_Venus
- Venera 9: https://en.wikipedia.org/wiki/Venera_9
- NASA Venus sample return, ASCEND 2024: https://ntrs.nasa.gov/api/citations/20240000426/downloads/Venus%20sample%20return_ASCEND-2024.pdf
- HAVOC: https://ntrs.nasa.gov/api/citations/20160006580/downloads/20160006580.pdf
- ADEPT: https://websites.isae-supaero.fr/IMG/pdf/adept_presentation_raj_final_6_14_12.pdf
- HIAD applications: https://ntrs.nasa.gov/api/citations/20240015418/downloads/AIAA_SciTech_2025_HIAD_Applications_Dutta_v2p1.pdf
- HIAD scaling: https://ntrs.nasa.gov/api/citations/20260007785/downloads/260901%20AFOSR%20HIAD%20Developments%20v2.pdf
- Heat shield mass correlation: https://arxiv.org/pdf/2308.07005
- Mars ascent vehicle: https://ntrs.nasa.gov/api/citations/20170003404/downloads/20170003404.pdf
- Delta-v budget: https://en.wikipedia.org/wiki/Delta-v_budget
- Space Exploration Vehicle: https://en.wikipedia.org/wiki/Space_Exploration_Vehicle
- Venus-condition electronics: https://science.nasa.gov/technology/technology-highlights/electronics-demonstrate-operability-in-simulated-venus-conditions
- Venus lander cooling: https://www.1-act.com/wp-content/uploads/2019/08/24-Hour-Consumable-based-Cooling-System-for-Venus-Lander.pdf
- Direct Fusion Drive: https://w3.pppl.gov/ppst/docs/paluszek2014iac.pdf
- VAMP: https://en.wikipedia.org/wiki/Venus_Atmospheric_Maneuverable_Platform
- Ingenuity: https://en.wikipedia.org/wiki/Ingenuity_(helicopter)
- Mars helicopter capabilities: https://rotorcraft.arc.nasa.gov/Publications/files/MarsHeliCapabilities_Final_Update.pdf
- Mid-Air Helicopter Delivery: https://arxiv.org/pdf/2203.03704
- Dragonfly: https://en.wikipedia.org/wiki/Dragonfly_(Titan_space_probe)
- ARES Mars airplane: https://ntrs.nasa.gov/api/citations/20040034201/downloads/20040034201.pdf
- Venus winds (Venus Express): https://sci.esa.int/web/venus-express/-/43391-a-3d-view-of-variable-winds-in-venus-s-cloud-layers
- Laser-powered UAV: https://www.militaryaerospace.com/uncrewed/article/16720247/lockheed-martin-and-lasermotive-use-laser-to-power-uav-for-48-hours
- Radiator sources: see radiators_v3.json
