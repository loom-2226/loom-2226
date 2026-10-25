# Wayfarer v0.5.2

ALL bodies. ALL sponsors. 2026-2226.

**Status: NON-GOVERNING SANDBOX.** v0.5.1 plus kT's torch heat package of 2026-10-25 (see `CHANGES_v0.5.2.md`). Nothing here is canon until kT adopts the proposed amendment.

Every number comes from `inputs/wayfarer_v05_inputs.json` and is recomputed by `build_v05.py` and `certify.py`. The generated report `out/CERTIFICATION_REPORT_v0.5.md` is the authority for figures; this page is a summary.

## The ship

| | |
|---|---|
| Length, hull | 53.3 m, 9.0 m across the armour |
| Dry mass | 867.7 t (canon 858.5 t), unchanged from v0.5.1 |
| Departure mass, full remass, shuttle aboard | 1,167.7 t (canon 1,158.5 t) |
| Water | 300 t: 250 t remass, 50 t protected (16.5 t storm-shelter jacket, 32.5 t service tank, 1.0 t in the tank cells) |
| ECON reach, full remass | 722.8 km/s (canon card 729 at canon mass) |
| Acceleration at cruise thrust | 0.99 g; HARD and LIMIT are throttled to the 5 g structural limit when the ship is light |
| Torch | pulsed: each He3-rich, spin-polarised D-He3 pellet is wrapped in a shell of remass that becomes the exhaust; burn 6 m aft of the reactor face (x 52.3 m); same 11.36 TW jet from about 12.6 TW of fusion |
| Torch heat | 1.4 GW reaches hot structure, carried by four hot fins at 1,750 K; 0.48 MW reaches the magnet coils, carried by the strakes |
| People | 6 crew (canon) + 4 guest berths |
| Shuttle | rover-drop shuttle, 27.9 t empty, 12.8 x 3.8 m, on the ship's axis inside the tank |
| Drones | 2 Mars + 2 dense-air drones in pods in the holds |

## Layout, bow to stern

| x (m) | Section |
|---|---|
| 0-14 | Habitat: armour and MMOD shell over an 8.6 m pressure vessel (x 0.2-13.7); five decks |
| 14-18 | Service: fore plant block on the axis; protected-water tank (+Z), two holds, docking collar at x 16 on -Z with the pressure tunnel to the shuttle |
| 18-31.5 | Wrap-around water tank in four isolatable cells around a round 4.8 m bore with the shuttle (x 18.75-31.55); 4.8 m slot along the top closed by two doors that open to vertical |
| 31.5-34.3 | Electrical C-ring, aft plant block, radiator manifold |
| 34.3-39.3 | Shadow shield inside the thrust cone |
| 39.3-46.3 | Reactor and thrust frame |
| 46.3-53.3 | Magnetic nozzle; the pellets burn at x 52.3 |
| 14-32.3 | Four accordion strakes at 40, 140, 220 and 320 deg, 1,300 K: 2 m out for Metric HARD, 4 m in torch burns |
| 34.3-53.3 | **Four hot fins** on the same lines (40, 140, 220, 320 deg), roots at r 4.75 m, 14 pleats of 2 m = 28 m out in torch burns, 1,750 K; folded into 0.6 m stacks otherwise |

The hot fins weigh 21.0 t (17.0 t of fins, 4.0 t of fold-out drive, root trusses and hot loop), paid from the engineering reserve (67.5 to 46.5 t), so the ship's mass and its performance card do not change. The torch chain's thrust line sits 0.20 m off the hull centreline so it passes through the middle of the centre-of-mass range.

## Torch burns

| | v0.5.1 | v0.5.2 |
|---|---|---|
| Heat reaching the ship | declared: at most 387 MW, no mechanism | 1.40 GW to hot structure + 0.48 MW to the magnet coils, from the heat model |
| Carried by | strakes at full 24 m span, 1,300 K | hot fins, 28 m, 1,750 K (capacity 1.49 GW); strakes 4 m for the coils' 48 MW of cryo heat |
| Light on the reactor's aft face | not modelled | 5.0 MW/m2 (ITER divertor class: 10) |
| Declared gap | 34 ppm of the jet reaches the ship | the shell lets out at most ~360 ppm of the burn as light (design 180 ppm); fins at 1,750 K for life |
| One fin lost | n/a | torch throttles to 88% |

Fins out make the ship about 1.5 times harder to roll (12.5 to 19.0 million kg m2 at full load) and about 2% harder to pitch and yaw; the fins fold before big slews.

## Decks (aft is down under thrust)

| Deck | x (m) | Rooms | Living volume |
|---|---|---|---|
| L1 Command | 1.0-3.0 | 6 couch stations, 4 forward windows | 44 m3 |
| L2 Common | 3.3-5.6 | galley, wardroom for 10, observation, exercise, washroom | 81 m3 |
| L3 Quarters | 5.9-8.2 | 6 crew and 4 guest cabins (8.2 m3 each, couch-bunk and window), 2 washrooms | 80 m3 |
| L4 Medical, life support, storm shelter | 8.5-10.8 | storm shelter for 10 behind a 20 cm water jacket, medical bay, life support | 57 m3 |
| L5 Mission, EVA, transfer | 11.1-13.4 | airlock, suit room, workshop, custody locker, stores, transfer vestibule | 57 m3 |

Total 318 m3 (31.8 m3 per person; NASA long-duration minimum 25).

## Certification (basis v0.1, proposed)

| Gate | Verdict |
|---|---|
| G1 Mass and fluids ledger | PASS |
| G2 Torch and reach | PASS |
| G3 Balance and attitude | PASS (worst trim 0.34 deg; 180 deg slew 34 s) |
| G4 Power and heat | PASS-DECLARED |
| G5 Structure and loads | PASS |
| G6 Radiation | PASS-DECLARED (shelter 55 g/cm2 in every direction) |
| G7 Compartments and crew space | PASS |
| G8 Shuttle, drones and bay exit | PASS (fins 1.05 m outside the slot edge lines) |
| G9 Failures and reserves | PASS |
| G10 Mission suite | OPEN, for Sol's Navigator |
| G11 Canon fit | PASS (14 departures listed) |
| G12 Images | PASS |

Declared assumptions: torch heat package (**awaiting kT's acceptance of the narrowed wording**); hot fins at 1,750 K (accepted); plant supplies 34.8 MW for Metric HARD at 1,300 K; shelter life support 72 h; cosmic rays rely on canon's radiation medicine; torch neutron dose is a torch interface requirement.

## Images

`render/out/`: exterior stills (hero, torch burn with fins out, view from aft with the shuttle lane, profile, shuttle departure, Metric HARD), cutaways (axis, habitat, midship), deck plans, and `wayfarer_v05_viewer.html` (phone 3D viewer; the burn mode unfolds the fins). All are generated from `out/wayfarer_v05_geometry.json` and stamped with its sha256.
