# Wayfarer L1 station design B3 (split halo): proposal

**Status:** PROPOSED. kT approved the concept on 12 Nov 2026, with Nicole's input. Not canon until it is imported into the L1 interior GLB, passes D9 + containment, and its mass is reconciled.
**Class:** research (rule F4 proposal package). No BRep, no D9 claim, no mass booking, no exterior change.

## Source

- Generator: `wayfarer/lab/l1_station_b3_generator.py`. Run it from the repo root. It reads `wayfarer/render/out/interior_L1.glb` and uses the six `i4_seat_*` node transforms unchanged.
- Output: `wayfarer/render/out/proposal_L1_stations_B3.glb`. This is 6 stations in 12 nodes: one shared station mesh, plus role controls per station. Treat the script as the source.

## Design (per station)

- **Couch:** 1.58 × 0.70 m contoured couch, with a five-point harness, a foot restraint, and a base frame on shock-absorbing legs.
- **Split halo:**
  - Two posts behind the head.
  - A curved centre screen about 0.6 m above the eyes. It lifts back (Nicole), so the crown view is clear when it is raised.
  - Two wing screens that swing aside for exit (kT).
- **Armrest role controls:**

| Station | Left | Right |
|---|---|---|
| Pilot | throttle | sidestick |
| Captain (S1) | keypad | backup stick |
| Navigator | keypad | trackball |
| Engineering (S2) | keypad | guarded switches |
| Sensors / EW (S3) | trackball | trackball |
| Mission Ops (S4) | keypad | comms handset |

- **Orientation:** heads to the centre, as already placed by the approved I4 layout. No station is moved.

## Claude's screen (vertex-level, not D9)

- **Clearance to fixtures:** no station vertex enters the bounding box of any L1 fixture.
- **Clearance between stations:** no station enters another station's local 0.70 × 1.58 m envelope. The tightest gap is S3 to S4, about 0.14 m, with the halos closed. Open wings extend beyond the envelope temporarily.
- **Height:** the halo top is 0.98 m above the couch base, against the lowest station headroom of 1.475 m.
- **Mass:** an estimate of about 52 kg per station against 51 kg booked. This must be reconciled from the geometry, and must not be rebooked.
- **Freeze:** dry mass 868.192255 t and ECON Δv 707.845 km/s are unchanged.

## 1:25

Each station is about 63 × 28 mm. The halo, armrest pods and sticks print as geometry. Screens, buttons, labels and buckles are decals.
