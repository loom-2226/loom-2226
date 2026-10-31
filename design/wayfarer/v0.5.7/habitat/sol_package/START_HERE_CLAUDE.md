# START HERE: Wayfarer v0.5 habitat integration package

**Status:** non-governing, non-canon candidate design. **This is an implementation handoff, not a request to redesign.**

## Claude workflow
1. Bootstrap from live `loom-2226/loom-2226` (GitHub outranks chat). Use archived `design/wayfarer/v0.5/` as baseline; do not overwrite or reinterpret its archived results.
2. Read `HABITAT_DESIGN_DATA.json` as the frozen candidate geometry/requirements. `BASELINE/` contains exact source inputs and code for reproducibility, not an instruction to start over.
3. Apply the changes to a new candidate revision using the existing `build_v05.py`/`certify.py` model. Do not treat this overlay as canon.
4. Reconcile shielding water mass and displacement against the actual parts and S1–S7 fluid states; recalculate CG/trim. Run existing relevant checks. Report only concrete blockers.
5. Stop after updated geometry, ledger, and check results. No architecture work, new framework, unrelated changes or renewed research.

## Decisions already made
- L3 four cabins: captain 1, crew A 2, guests 4, crew B 3. Six footprints: four double and two single berths. Two washrooms and 1m corridor remain.
- Bunks 2.00m radial by 0.75m tangential, span r=2.01..4.01m, angular positions in JSON. 80cm sliding doors. 8cm annular water layer r=4.07..4.15m, x=5.9..8.2m, 4.752t idealized.
- L4 medical, ECLSS and ten-person storm shelter retained. Candidate 2.4m clear medical opening centred at 210 degrees to permit 2.0m x 0.60m rigid stretcher transfer.
- Keep 5g berth-restraint requirement and GCR medical dependency. Do not assert those are qualified.

## Evidence and limits
- Radiation: 600 directions x 36 bunk-centre samples in least protected S5, 2cm steps: 8cm water => minimum 40.92 g/cm², 0/36 under 40. At 5cm: 38.32 and 12/36 failures. This is material-column screening, not dose or full-body certification. Water overlaps existing geometry unless replacement/displacement is reconciled.
- Plan-view bunk outermost corner r=4.02749m, 4.25cm clearance to shield inner boundary. Sector footprints and nominal 80cm door arcs do not overlap; guest/crew B inner-wall door-to-bunk gap only about 11cm, not an aisle clearance proof.
- Axial stacking budget: two x (14cm frame + 12cm mattress + 82cm clearance) = 2.16m in a 2.30m axial deck interval; 14cm remains. Actual usable ceiling, ladder/access and structure unverified.
- L4 stretcher: coarse sampled 5cm/5degree configuration-space search found a path for 2.0x0.60m rigid rectangle through 2.4m clear opening; failed 2.2m and below. Not exact swept path, patient/attendant envelope or structural feasibility.

## Important honesty rule
The design choices are frozen **for implementation**, not physically certified. If pressure boundary, bunk access, water accounting or structural constraints demonstrably fail, report that precise issue; do not silently claim a pass or commission a redesign.

## Contents
- `HABITAT_DESIGN_DATA.json`: complete machine-readable proposed geometry and constraints.
- `EVIDENCE/`: exact exploratory scripts, including the stretcher-turn search.
- `BASELINE/`: archived v0.5 geometry, inputs, specification, and existing builders/certifiers.
- `MANIFEST_SHA256.txt`: file checksums.
