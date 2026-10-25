# LOOM 2226 — CANON II Wayfarer Amendment v2.4d (PROPOSED)

ALL bodies. ALL sponsors. 2026-2226.

**Status: PROPOSED. NOT CANON.** For kT's decision only. Do not place in `canon/current/` until kT approves it in writing.
**Parent authority:** CANON II Engineering, Ships and Operations v2.4; CANON II Wayfarer Schematic Amendment v2.4a.
**Evidence:** Wayfarer v0.5 certification record (non-governing), report `out/CERTIFICATION_REPORT_v0.5.md`.
**Preconditions for adoption:** Claude and Sol agree the certification basis; Sol runs gate G10 with Navigator; kT accepts each declared assumption in §7.

## 1. Reference courier mass ledger (would replace the §13 values)

| Quantity | Canon v2.4 | Proposed |
|---|---:|---:|
| Main body | ~57 m x 9 m | ~53.3 m x 9 m |
| Normal crew | 6 | 6 (unchanged) |
| Guest berths | not stated | 4 |
| Payload target | 50 t | 50 t (unchanged) |
| Working fluid / water | 300 t | 300 t (unchanged) |
| Normal remass | 250 t | 250 t (unchanged) |
| Dry excl. water | ~858.5 t | ~867.7 t |
| Wet | ~1,158.5 t | ~1,167.7 t |
| Unified relational plant | ~88 t | ~88 t (unchanged), split fore and aft of the bay |

The torch card's exhaust velocities are unchanged. At the new mass the ECON full-remass delta-v is ~723 km/s (the card's ~729 km/s was computed at 1,158.5 t).

## 2. Structural grammar (would replace the §13.2 grammar block)

```text
5 axial longerons
1 wrap-around working-fluid tank, C-section, in 4 isolatable cells, around an on-axis launch bay
4 deployable radiator strakes, mirror-symmetric at 40 / 140 / 220 / 320 deg
1 axial primary fusion torch / magnetic nozzle, thrust line offset ~0.3 m from the hull centreline
```

Reason: the C-tank lets the launch sit on the thrust axis inside the tank instead of in a side blister, which keeps the mothership round and shorter. Four tanks in quadrature cannot clear a centred 4.8 m bay.

## 3. Launch bay (would amend v2.4a §1-2)

- Round bore 4.8 m across, x ~18.25-32.05, on the ship's axis inside the tank. Replaces the x 16-28 reservation.
- Lateral departure through a 4.8 m slot on +Z; two doors that open to vertical. Unchanged in principle: unpressurized, substantially enclosed, lateral departure.
- Pressure-tight crew transfer by tunnel: habitat L5 vestibule, collar node, bay axis, shuttle nose port.
- DOCKED / ABSENT mass state is unchanged and is carried in every mass state.

## 4. Thermal and electrical

- Radiators reject at 1,300 K. Metric HARD then needs ~34.8 MW of cryo-chain electrical power (canon states ~23.9 MW at 900 K). Adoption requires a canon statement that the plant supplies this, or a 900 K loop for the cryo chain.
- The 719 m2 HARD equivalent at 900 K remains the governing requirement and is met with one 2 m pleat per strake (field geometry radius 6.5 m).

## 5. Habitat (new canon detail)

Pressure vessel 8.6 m across inside an armour and MMOD shell, x 0-14. Five decks perpendicular to thrust: command; common; quarters (6 crew, 4 guests); medical, life support and storm shelter; mission, EVA and transfer. ~318 m3 of living volume, 16 windows, 16 acceleration couches, two ladders per deck. Storm shelter behind a 20 cm water jacket drawn from the protected water; the rest of the protected water in a service tank on +Z.

## 6. Planetary launch

Rover-drop shuttle: 27.9 t empty, 12.8 x 3.8 m. The Venus surface is reached by a hardened rover dropped from a cloud city. This replaces the candidate 30-35 t, ~10.5 m launch (candidate, not canon).

## 7. Declared assumptions that adoption would accept

1. Torch interface: non-exhaust torch heat reaching the ship stays at or below ~387 MW (34 ppm of jet power) during burns.
2. Plant electrical: ~34.8 MW available for Metric HARD at a 1,300 K reject temperature.
3. Storm shelter life support: 72 h for 10 people.
4. Galactic cosmic rays: long careers aboard depend on the off-Earth MED-MOD-RADIATION milestone and crew time-in-space rules; the hull alone cannot keep a full-time crew under 600 mSv.
5. Torch neutrons and gammas: the shadow shield attenuation needed for habitat dose limits is a torch interface requirement.

## 8. Unchanged by this amendment

Torch exhaust-velocity card; Metric card and HARD requirement; torch / Metric mutual exclusivity; docking collar at x = 16 m on -Z; habitat at x 0-14 m; four radiator assemblies; no spin ring, wings or landing gear; Loom configuration lock (CANON II §12.1).

---

END — PROPOSED AMENDMENT v2.4d (NOT CANON)
