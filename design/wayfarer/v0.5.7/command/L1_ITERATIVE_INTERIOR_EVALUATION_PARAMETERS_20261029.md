# LOOM Wayfarer L1 — Iterative Design Evaluation Parameters
**29 October 2026 — RESEARCH / NON-CANON / NON-RUNTIME / NOT CERTIFICATION.** This is a compact evaluation sheet for successive 3D interiors, not a new engineering subsystem.

## Purpose and source authority
Evaluate *actual ship-operating usefulness* of a fully built-out L1 with six individually usable acceleration seats, a **real** low-g standing/anchored command workstation, correctly placed control/display surfaces, and six crew functional domains. LOOM's current Rev7 reference is a **non-governing sandbox**; GitHub PR #432 at head `3485830a56dfead79b2ef8bba031a595b536fbb5` remains the governing source for this branch review.

Source records:
- `design/wayfarer/v0.5.7/SPEC.md`: six crew, five decks, raised Pilot/NAV flight deck, four support stations, two L1 exits, sensor ring; 4g sustained crew doctrine / 5g structural rating; 8.6m pressure vessel.
- `command/l1_study.py` and `command/l1_study_results.json`: Rev7 check criteria with 0.8m accessible paths, 2.1m walkway headroom, >=90% view inside Pilot/NAV's forward 60° cone, eye/display separation >=0.33m and displays outside central cone; source prior crown geometry and ray test differ from the proposed 37-panel canopy and must **not** be conflated.
- `render/out/l1_scene.json`: six original station eye/body/display positions; placeholders are straight 2.1m couches. `STAND` in the prior interactive viewer is only a camera, not a station.
- `command/L1_CREW_FUNCTION_FIRST_INTERIOR_BRIEF_20261029.md`: six work functions, Soyuz/Kazbek-inspired fitted but adjustable *semi-reclined work seats*, and a real low-g anchored command/briefing point.
- LOOM Ship Building and Piloting v0.2: captain/flight, engineering, tactical/mission and damage-control authority; pilot, navigation/Loom, sensors/EW, medical expertise overlap; minimum/normal/surge staffing distinguished.
- Foundational Canon v1.2: crew are persistent agents, not bonuses; judgment, authority and autonomy matter.

Research canopy is fixed for now: **37 replaceable outer panels + two visually seamless independent pressure domes + hypothetical adaptive optogel**. It is a **non-canon visual candidate**, not pressure-qualified technology.

## A. Hard constraints: PASS / FAIL, never weight away
| ID | Requirement | Test |
|---|---|---|
| H1 | Six contoured, adjustable acceleration work seats; no flat coffin-style beds | Six seated digital crew bodies fit, torso/neck/hip/knee/foot supports and harness modeled; >= source 99th-percentile occupant envelope where applicable; model fits differently sized bodies |
| H2 | Every seated operator has a safe supported pose for normal thrust and a full reachable set of *their* emergency controls | Check body load axis relative to principal acceleration; restrained visual/reach envelopes at 4g; retain source structural 5g x 1.5 ultimate checks for changed hardpoints (not a seat qualification) |
| H3 | One actual low-g standing/anchored station with handholds, foot restraints, useful shared work surface and a clear path to captain seat | Build physical geometry and anchored body; at 4g this station is vacant; station does not block any path |
| H4 | Both ladderways and all six seats reachable by continuous unobstructed >=0.8m routes | Geometry path/collision test in realistic parked/occupied positions |
| H5 | >=2.1m standing/walking headroom on routes | Geometry section/path test; same as current L1 source screening |
| H6 | Pilot and NAV retain >=90% unobstructed sightlines inside a 60-degree bow-axis cone **in the SAME held-37-pane optics ray test** | Compare seat+furniture+displays+inner/outer panels with one exact sampler; do not mix with earlier Rev7 framed dome metrics |
| H7 | Essential controls readable and physically usable from the seated, restrained position | Per-role critical-task test; no screen-only emergency single-point dependence; source eye/display distance >=0.33m as a preliminary floor, update only with grounded ergonomic case |
| H8 | No collision with fixed hull, inner pressure boundary, canopy/sensor ring, flight-deck structure, two ladders | Intersection test for station, chair, knee/foot travel, recline and display mounts |
| H9 | Clearly differentiate observed, model-projected, stale and uncertain information; critical command authority remains explicit | Simple task script: operator can correctly tell observation/prediction/age/uncertainty and who may authorize maneuver/abort |
| H10 | Added seats, mounts, shared display and standing fittings have explicit *delta* mass and structural attachment path | Count only actual difference against existing source, don't double-book canopy/outer armour/ship mass |

**No invented threshold:** detailed human reach/visibility comfort, emergency response seconds, leg clearance and display legibility are initially measured and compared. The prior 2.1m couch box is an *occupant accommodation* clue, not a requirement to keep a 2.1m slab seat.

## B. Design variables to change (narrow initial search)
- **Couches (6):** centre x/y/z, bow/radial rotation and recline, pelvis/shoulder/head placement, bent knee and supported foot positions, chair outside envelope, brace and side-controls. Pilot/NAV start at source positions; first vary support chairs before front positions.
- **Local displays:** per-role display centre x/y/z, panel footprint/angle, head-to-screen angular distance, physical/perceptual occlusion, mounted versus adjustable, one important fixed/physical fallback control.
- **Standing station:** x/y/z, low-g body anchor and grip geometry, lean/perch surface, shared mission/ship display position, passage clearance and proximity to Pilot/NAV/Captain.
- **Shared information and lighting:** two or three possible shared display placements; clear/glare/dark canopy states; task-based visualization of route/uncertainty, ship state, contacts, and crew communications.
- **Roles:** functional map to six seats (Pilot, NAV, Captain, Engineering, Sensors/EW, Mission Operations) may change **without** assuming the same crew member is always seated there. Medical, damage-control and life-support response are cross-qualified.
- **Fixed at first:** pressure-vessel envelope, ladderways, flight deck elevation, shoulder sensor ring, 37 outer tiles and both inner domes. No new passageway, seventh g seat or new subsystems.

First exploratory variations, explicitly **not authoritative standards**: support station radial offsets 0 to 0.4m inward, yaw +/-25deg, axial relocation 0 to 0.25m; local screen offsets up to ~0.2m vertical/axial and orientation toward the eye; Pilot/NAV move only after these tests. Run a small authored set, not thousands of unexplained candidate combinations.

## C. Comparative metrics: report raw numbers and failure symptoms

| Metric | Quantified output / how scored | Improvement direction |
|---|---|---|
| M1. Critical-task completion | Per-role task completed/blocked in each scenario; wrong/ambiguous actions recorded | All critical tasks possible; no misleading UI |
| M2. Retained restrained reach | Fraction of *required* controls reachable at supported seat posture under nominal 4g; worst operator fit | 100% for critical controls |
| M3. External sky | Same-ray Pilot/NAV 60° clear fraction; forward hemisphere visible solid-angle fraction by each role; canopy obstruction by screen mount | Better where visibility helps that role |
| M4. Display usability | Eye-to-screen distance, angular gaze shift outside-vs-screen, screen occlusion, tiny text angular size; readable from actual eye for individual and shared panels | Reduce work and head movement without occluding panorama |
| M5. L1 movement/egress | 0.8m route continuous, shortest obstruction-free path from seats/standing to each ladder; stuck-point count | Fewer obstructions; both exits reachable |
| M6. Crew collaboration | Count pairs who can see each other/shared information; ability to conduct a captain/Pilot/NAV briefing and hand off between stations | Higher functional awareness; no compulsory all-on-one-display |
| M7. Seat loading and fatigue | Relative acceleration/body axes; supported back/head, bent legs, actual anchored reach in multi-minute burns; adjustments for crew size | Lower unsupported loads and prolonged strain |
| M8. Watch and standing usability | One/two-person quiet watch can run ship, anchored standing station allows briefing and retreat to seat without blocking egress | Normal watch with minimum clutter |
| M9. Environmental quality | Reflections, glare at displays under exterior illumination, blackout ability, lit handholds, view quality; subjective crew review | Comfortable/legible in clear/glare/dark |
| M10. Physical cost | Added mass and volume displacement; screen/seat mount burden; percentage clear floor free for access | Smaller justified penalty |
| M11. Failure legibility | Identify stale track, estimated future trajectory, uncertain Metric/Loom condition, degradation and manual fallback; count operator mistakes | No unknown fact presented as known |
| M12. Human experience | Crew-eye walkthrough: plausibility, comfort, autonomy, ability to observe and use ship, visual identity without spectacle blocking work | Clear reason to prefer design in simulation |

**Avoid a single arbitrary weighted "bridge score"** in early rounds. Each candidate gets PASS/FAIL hard gates + the table of raw metrics + one paragraph identifying the meaningful trade-offs. Compare the Pareto improvements, then *play* with the two strongest arrangements.

## D. Exactly four test scenes
1. **Quiet coast/watch:** one/two active operators + captain at standing workstation; ship status, local adjustment, normal conversation.
2. **Precision Ceres approach/docking:** Pilot+NAV+Sensors/Mission; uncertain contacts, changing guidance, shared route and manual controls.
3. **Torch burn:** 4g sustained, all six L1 occupants restrained, critical controls operable, quiet but necessary comms; standing post inactive.
4. **Metric/Loom transition or single fault:** cross-check forecasts/observations, engineering readiness, command authorization, abort, access to exits.

Each scene produces the same raw metrics. No invented reaction-time thresholds; observe actual issues before assigning limits.

## E. Iteration order and stopping rule
- **R0**: current source Rev7 baseline measured on the same metrics (note source uses old framed crown).
- **R1**: fit six contoured Kazbek-inspired seats, **without** rearranging the hull/flight deck.
- **R2**: correct role-specific screens and restrained controls.
- **R3**: place a real central/aft low-g standing workstation with hand/foot anchors and one shared display.
- **R4 only if warranted**: move/reorient four support seats; Pilot/NAV positions last.
- Play one Ceres approach and one 4g burn at the strongest candidate. Stop when hard gates pass, each role has its essential interface, standing work is real and low-g only, and the next geometry change shows no demonstrable operational benefit.

**Do not author a new qualification engine, giant scoring optimizer or spaceship UI system.** Extend the existing 3D viewer and small ray/collision calculations only as necessary to answer an observed design question.

**All this is research. No canon, governing Rev7 geometry, PR432, Technology Timeline or runtime mutation.**
