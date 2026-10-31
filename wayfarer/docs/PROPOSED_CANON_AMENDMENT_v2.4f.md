# LOOM 2226 — CANON II Wayfarer Amendment v2.4f (PROPOSED)

ALL bodies. ALL sponsors. 2026-2226.

**Status: PROPOSED. NOT CANON.** For kT's decision only. Do not place in `canon/current/` until kT approves it in writing.
**Parent authority:** CANON II Engineering, Ships and Operations v2.4; CANON II Wayfarer Schematic Amendment v2.4a.
**Evidence:** Wayfarer v0.5.7 rev 7 (non-governing), report `out/CERTIFICATION_REPORT_v0.5.md`. Supersedes the earlier drafts (v2.4d, v2.4e), which are in git history.
**Preconditions for adoption:** certification basis v0.2 is agreed by Claude and Sol (2026-10-26); every gate PASS or PASS-DECLARED with every declared assumption accepted by kT; Sol signs; loom-gate passes. Accepted by kT: torch heat, 1,750 K fins, plant power, shelter life support, cosmic rays, crown dome, berth viewports, torch thrust-vector control. Awaiting kT: axial RCS plume clearance (`rcs_axial_plumes`), the burn-coast test assumption (`g10_burn_coasts`), and rev 7's `strata_armour`, `node_faces`, `cold_running` and `external_equipment`. Navigator missions (E1, FR-01B-R, MV-01) follow as validation once fixtures and the CANON II §20 solver exist.

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
4 axial longerons (CFRP tubes in an X; the upper pair edge the bay slot) -- now as canon v2.4
1 wrap-around working-fluid tank, C-section, in 4 isolatable cells, around an on-axis launch bay
4 deployable radiator strakes, mirror-symmetric at 40 / 140 / 220 / 320 deg
4 deployable hot fins aft of the shield on the same lines, 1,750 K, torch burns only
1 axial primary fusion torch / magnetic nozzle, pulsed remass-shell burn,
  thrust line offset ~0.2 m from the hull centreline
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

## 4a. Torch architecture and hot fins (new canon detail)

- The torch runs the working card (`src/wayfarer_torch_mode_cards.py`: mass flow and exhaust velocity per mode). Jet power is held to 11.36 TW, the power the heat rejection is sized for, so FAST, HARD and LIMIT run below their card thrust (32.5, 50.5 and 75.7 MN against 34.1, 56.8 and 85.2) and ECON gives 3.4 MN at 5.1 TW. Crew doctrine caps sustained thrust at 4 g.
- The magnetic nozzle steers the thrust line by up to 1 deg, enough to keep it through the centre of mass with trim plus a 0.5 deg thrust error.
- The torch is pulsed. Each pellet of helium-3-rich, spin-polarised D-He3 is wrapped in a shell of remass that soaks up the burn's light and most of its neutrons and leaves as exhaust. The burn sits 6 m aft of the reactor face, inside the nozzle. The heat model needs about 12.6 TW of fusion for an 11.36 TW jet.
- Four hot fins on the strake lines aft of the shield (x 34.3-53.3), 28 m when unfolded, run at 1,750 K and carry about 1.4 GW in torch burns. They fold into 0.6 m stacks otherwise and before big slews. 21 t, paid from the engineering reserve, so dry and wet mass are unchanged.
- In torch burns the strakes open 4 m and carry only the magnet coils' cryo heat; full 24 m span is no longer needed for the torch.
- The slot-side fins stand 1.05 m outside the slot edge lines, so the shuttle keeps a clear lane.

## 4b. Reaction control (new canon detail)

Eight clusters of 25 kN thrusters, four at the bow and four aft: three per cluster for attitude (inward and both tangential) and, new, one axial thruster per cluster (bow ones push aft, aft ones push forward, each canted 10 deg outward) so the ship can translate along its axis for docking. 180 deg slews settle in about a minute in every mass state, also with any one cluster out.

## 5. Habitat (new canon detail)

Pressure vessel 8.6 m across inside an armour and MMOD shell, x 0-14. Five decks perpendicular to thrust: command (pilot and navigator on a flight deck 1.78 m up in the nose, supine facing the bow, under a 25 m2 crown dome (ceramic panes on an Osteon frame, closed by tambour gores that stow in a brow ring; open only at low speed or with the bow out of the dust flow); bow sensors in a ring at the dome shoulder; four support couches along the rim); common; quarters (four shared cabins: captain 1, crew 2 and 3, guests 4; ten berths with 5 g restraints, behind an 8 cm water ring); medical, life support and storm shelter; mission, EVA and transfer. ~315 m3 of living volume. Glazing for livability, about 48 m2: the crown dome over L1; a panoramic viewport band round the L2 common deck (19 m2, 1.6 m tall in the lounge, on Osteon titanium mullions between titanium edge rings; ceramic plate panes on the crown's materials milestone); and 22 round viewports: 4 L1 shoulder, 10 berth (0.5 m), 2 medical, 2 storm shelter, 1 suit room, 2 workshop, 1 vestibule. Every opening below the crown has an acrylic shield plug (berths and shelter keep their screens with the shutters open) and a flush Strata shutter, closed at cruise speed, in storms and in burns. This goes beyond the canon candidate's 10-16 windows: kT's call. 16 acceleration couches and berths, two ladders per deck. Storm shelter behind a 20 cm water jacket drawn from the protected water; the rest of the protected water in a service tank on +Z.

## 5a. Hull skin (rev 7; kT decisions 2026-10-26, Sol agreed)

Low signature is a skin criterion: an operational constraint, not a promise of invisibility. The habitat armour (x 0-14) is faced in **Strata laminate** (Builder-derived, MHL-22) over its whole area, not only in the gores and shutters; the bow (x 0-2.6) is bare Strata, the erosion face that meets the dust flow. Naming the material implies no new shielding performance: the armour keeps its 105 t ledger line, and Strata's density, properties and appearance stay open. Aft of the bow the flanks carry a **tunable-emissivity layer** (proposed Frontier item F5-TE-01) with two modes: normal (emissivity 0.85, light in sunlight) and cold running (0.10), which holds heat for a finite time. The hull shows **208 metric node faces** (13 rings x 16), flush or recessed; each must carry at least the armour's g/cm2, and their placement is held against PR #184. External equipment (passive sensor turrets, flush RF arrays, laser terminals, star trackers, service ports, vents, hull-crawler docks and grip points, grapple fixtures, EVA rails) is part of the geometry; drone bays are held.

## 6. Planetary launch

Rover-drop shuttle: 27.9 t empty, 12.8 x 3.8 m. The Venus surface is reached by a hardened rover dropped from a cloud city. This replaces the candidate 30-35 t, ~10.5 m launch (candidate, not canon).

## 7. Declared assumptions (kT's acceptances recorded in `inputs/kt_decisions.json`)

1. **Torch heat, a narrowed declared gap (accepted 2026-10-25).** The remass shell lets no more than about 360 ppm of the burn's energy escape as light, counting its own glow; the design value is 180 ppm. With the heat model's other assumptions, 1.4 GW reaches hot structure and under 1 MW the magnet coils. Whether a shell this hot can glow this little is a physics unknown that nobody has shown; it replaces v0.5.1's 387 MW (34 ppm) gap, which had no mechanism. The same gap covers neutron and gamma leakage: the torch and shadow shield keep habitat dose within crew limits during burns.
1a. **Hot fins at 1,750 K (accepted 2026-10-25).** An engineering extrapolation, not new physics: heat pipes have run in labs at about 1,500 K for long periods and briefly near 1,800 K. Fallback: 1,500 K fins, about 49 m and 30 t, still inside the reserve.
2. **Plant electrical.** The relational plant supplies ~34.8 MW for Metric HARD at a 1,300 K reject temperature.
3. **Storm shelter life support.** 72 h for 10 people, as a design provision.
4. **Galactic cosmic rays.** Long careers aboard rely on the off-Earth MED-MOD-RADIATION milestone plus crew time-in-space limits; the hull alone cannot keep a full-time crew under 600 mSv.
5. **Torch thrust-vector control (accepted 2026-10-26).** Up to 1 deg of steering by the magnetic nozzle, against an assumed 0.5 deg thrust error; not yet a qualified nozzle capability.
6. **Axial RCS plumes (awaiting kT).** The canted axial thrusters' plumes clear the crown, hull, hot fins and torch chain; not yet modelled.
7. **Strata habitat armour (rev 7, awaiting kT's wording).** Strata faces the whole habitat armour; no new shielding performance is implied; density, properties and appearance open.
8. **Node faces (rev 7, awaiting kT; placement HOLD).** 208 faces, each carrying at least the armour's g/cm2. If they were open bores through the armour the worst berth screen would fall from 40.4 to 14.8 g/cm2. Materials, covers, seals and mounts open; PR #184 open.
9. **Cold running (rev 7, awaiting kT; F5-TE-01 provisional).** Low emissivity holds heat, it does not remove it: about 17 h on the protected water before the strakes must open. The metallic look is a proposed optical property.
10. **External equipment (rev 7, awaiting kT).** 2026-analogue mass allowances; most items located inside existing ledger lines, 1.4 t of new hardware from the reserve.

## 8. Unchanged by this amendment

Torch exhaust-velocity card (jet power per mode now follows the working card, held to 11.36 TW); Metric card and HARD requirement; torch / Metric mutual exclusivity; docking collar at x = 16 m on -Z; habitat at x 0-14 m; four radiator assemblies (the strakes; the hot fins are additional torch hardware); no spin ring, wings or landing gear; Loom configuration lock (CANON II §12.1), now declared in the ship card: shuttle DOCKED, docking collar FREE, strakes and hot fins STOWED, crown gores closed.

---

END — PROPOSED AMENDMENT v2.4f (NOT CANON)
