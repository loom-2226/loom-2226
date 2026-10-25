# Wayfarer v0.5

ALL bodies. ALL sponsors. 2026-2226.

**Status: NON-GOVERNING SANDBOX, submitted for certification.** Nothing here is canon until kT adopts the proposed amendment. Date 2026-10-25.

Wayfarer v0.5 is the v0.4 layout rebuilt around the rover-drop shuttle, with a defined habitat for 6 crew and 4 guests, a full parts model with mass properties, and a certification run against CERTIFICATION_BASIS_v0.1. Every number comes from `inputs/wayfarer_v05_inputs.json` and is recomputed by `build_v05.py` and `certify.py`. The generated report `out/CERTIFICATION_REPORT_v0.5.md` is the authority for figures; this page is a summary.

## The ship

| | |
|---|---|
| Length, hull | 53.3 m, 9.0 m across the armour |
| Dry mass | 867.7 t (canon 858.5 t) |
| Departure mass, full remass, shuttle aboard | 1,167.7 t (canon 1,158.5 t) |
| Water | 300 t: 250 t remass, 50 t protected (16.5 t storm-shelter jacket, 32.5 t service tank, 1.0 t in the tank cells) |
| ECON reach, full remass | 722.8 km/s (canon card 729 at canon mass) |
| Acceleration at cruise thrust | 0.99 g; HARD and LIMIT modes are throttled to the 5 g structural limit when the ship is light |
| People | 6 crew (canon) + 4 guest berths |
| Shuttle | rover-drop shuttle, 27.9 t empty, 12.8 x 3.8 m, on the ship's axis inside the tank |
| Drones | 2 Mars + 2 dense-air drones in pods in the holds |

## Layout, bow to stern

| x (m) | Section |
|---|---|
| 0-14 | Habitat: armour and MMOD shell over an 8.6 m pressure vessel (x 0.2-13.7); five decks |
| 14-18 | Service: fore plant block on the axis; protected-water tank (+Z), two holds (port, starboard), docking collar at x 16 on -Z with the pressure tunnel to the shuttle |
| 18-31.25 | Wrap-around water tank in four isolatable cells, round 4.8 m bore with the shuttle (x 18.75-31.55), 4.8 m slot along the top closed by two doors that open to vertical |
| 31.25-32.3 | Electrical C-ring around the bay's aft end |
| 32.3-34.3 | Aft plant block, radiator manifold |
| 34.3-39.3 | Shadow shield inside the thrust cone |
| 39.3-46.3 | Reactor and thrust frame |
| 46.3-53.3 | Magnetic nozzle |
| 14-32.3 | Four accordion radiator strakes at 40, 140, 220 and 320 deg, up to 24 m span, 1,300 K |

Structure: five longerons (flat planks at 0, 180 and 270 deg between the tank and the skin; round sills beside the slot), ring frames every 2 m. The torch chain's thrust line sits 0.31 m off the hull centreline so it passes through the middle of the centre-of-mass range.

## Decks (aft is down under thrust)

| Deck | x (m) | Rooms | Living volume |
|---|---|---|---|
| L1 Command | 1.0-3.0 (bow sensors ahead) | 6 couch stations, 4 forward windows | 44 m3 |
| L2 Common | 3.3-5.6 | galley, wardroom for 10, observation (2 windows), exercise, washroom | 81 m3 |
| L3 Quarters | 5.9-8.2 | 6 crew and 4 guest cabins (8.2 m3 each, couch-bunk and window), 2 washrooms | 80 m3 |
| L4 Medical, life support, storm shelter | 8.5-10.8 | storm shelter for 10 behind a 20 cm water jacket, medical bay, life support | 57 m3 |
| L5 Mission, EVA, transfer | 11.1-13.4 | airlock, suit room, workshop, custody locker, stores, transfer vestibule with the floor hatch to the tunnel | 57 m3 |

Total 318 m3 (31.8 m3 per person; NASA long-duration minimum 25). Two ladders per deck, a central trunk for lift and utilities, 16 windows, 16 couches.

## Certification (basis v0.1, proposed)

| Gate | Verdict |
|---|---|
| G1 Mass and fluids ledger | PASS |
| G2 Torch and reach | PASS |
| G3 Balance and attitude | PASS (worst trim 0.34 deg; 180 deg slew 33 s) |
| G4 Power and heat | PASS-DECLARED |
| G5 Structure and loads | PASS (longerons 64 MPa at 7.5 g ultimate; first bending mode 8.9 Hz) |
| G6 Radiation | PASS-DECLARED (shelter 56 g/cm2 in every direction) |
| G7 Compartments and crew space | PASS |
| G8 Shuttle, drones and bay exit | PASS |
| G9 Failures and reserves | PASS |
| G10 Mission suite | OPEN, for Sol's Navigator |
| G11 Canon fit | PASS (12 departures listed) |
| G12 Images | PASS |

Declared assumptions for kT: torch heat leak at most 387 MW (34 ppm); plant must supply 34.8 MW for Metric HARD at 1,300 K; shelter life support 72 h; galactic cosmic rays need canon's radiation medicine; torch neutron attenuation is a torch interface requirement.

## Changes made during certification (all in the inputs, with reasons)

- Longerons moved off r 4.1 m, where they ran through the tank and into the slot.
- Strakes moved from 45 to 40 deg: a 2 m groove on the 45 deg diagonal broke 0.28 m into the slot.
- Tank lengthened to 13.25 m: the solid model gives 24.3 m2 of section, not the 25.85 m2 of the v0.4 formula.
- Thrust line offset and protected water moved to +Z to keep the torch pointing through the centre of mass (0.95 deg without them).
- Storm-shelter floor jacketed: an oblique aft ray came out at 39.1 g/cm2 without it.
- Command deck starts behind the bow sensors; one window per cabin (16 in all).

## Images

`render/out/`: exterior stills (hero, torch burn, profile, shuttle departure, Metric HARD), cutaways (axis, habitat, midship section), a plan of every deck plus an overview, and `wayfarer_v05_viewer.html` (phone 3D viewer). All are generated from `out/wayfarer_v05_geometry.json` and stamped with its sha256.
