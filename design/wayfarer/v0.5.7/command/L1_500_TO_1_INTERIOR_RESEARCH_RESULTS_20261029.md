# Wayfarer L1 — 500 → 20 → 5 → 2 → 1 interior design experiment
**29 October 2026 · RESEARCH · NON-CANON · NON-RUNTIME · NOT HUMAN-FACTORS OR STRUCTURAL QUALIFICATION**

## Authority and fixed ship
Live PR #432 source head `3485830a56dfead79b2ef8bba031a595b536fbb5` remains OPEN and unchanged. Source Rev7 L1 crew scene SHA `74e2293894af184a5dc6df0984cc89c3532e907b152daee24ec9d2afdc161271`; six people, 2 front flight crew, 4 support, actual two ladderways, elevated flight deck and sensor ring. Held new non-canon canopy: **37 separate outer tiles / two seamless pressure domes / speculative optogel**.

Physical search variables: support-seat inward displacement 0–42cm, heading ±22° with differential stagger, axial shifts about ±10cm, primary-screen gaze angle 30–54°, a central/aft standing anchor in y,z. Pilot/NAV nominal eye coordinates and source hull/floor/ladder/sensor placements held. Source straight 2.10m slab couches are **replaced only in research renders** by **contoured 1.58m projected head-to-foot, 0.70m-wide prototype shell seats** with supported head/torso/thigh, bent knee/raised feet, harness visual, and restraints/controls indicated. This compact seat **DOES NOT establish fit for the source 99th-percentile occupant**, clinical 4g tolerance or structural hardpoint capacity.

Crew functions as revised: PILOT flight; NAV navigation/Loom; **S1 Captain/command (nearest standing post)**; S2 Sensors/EW; S3 Engineering; S4 Mission operations. Medical/damage control are cross-qualifications. Stand is a **real** low-g/0g anchoring location with dual foot restraint indications, handrails, local controller and shared information surface; never a seventh g-rated seat.

## What was actually executed

| Round | Actual computation | Result |
|---|---|---|
| 500 parameter candidates, fixed seed 2226 | 2D seat OBB collision, simplified hull radius/ladder clearance, geometric dashboard proxies | **476 survive**, **23 rejected for projected hull protrusion**, **1 for ladder clearance** |
| 20 deliberately distinct survivors | Inflated 0.8m 2D floor paths to both ladder openings and support seats; analytic rays through original pressure ellipsoid and hypothesized outer facet shape | **20/20 pass these specified simplified geometric checks** |
| Five visual finalists | Generate one standalone WebGL2 L1 viewer with selectable layout, each with **six custom segmented seats, six mapped displays, hand controls, central standing console, common flight deck and held canopy** | L1-020, L1-002, L1-391, L1-390, L1-155; HTML + generator preserved |
| Two selected operational *proxy* finalists | Four **static** watch/approach/4g/emergency configurations: route availability, canopy geometric sightlines, 6 seat count, display facing, hand reach target proxy, standing evacuated under g | L1-020 and L1-002; **NOT actual piloted simulation, not human response measurements** |
| One recommended research geometry | Choose better 2D egress and support forward sky geometry among finalists with acceptable captain/standing proximity and screen gaze | **L1-020 provisionally preferred**; no structural, ergonomic, dynamic or cognitive qualification claimed |

## Two finalist trade-offs

| Evaluated property | L1-020 selected | L1-002 runner-up | Meaning |
|---|---:|---:|---|
| Support-seat radial inward displacement | **40.2cm** | 9.4cm | L1-020 makes support stations less perimeter-bound |
| Support-seat overall yaw | **-14.6°** | -1.5° | More turned inward |
| Individual screen gaze off bow | 41.6° | **36.1°** | L1-002 lower head/eye redirection; no measured workload |
| Captain-seat centre to anchored standing post | 2.09m | **1.81m** | L1-002 improves captain-to-workstation proximity |
| Two ladder route lengths, **SUM** (0.8m-width 2D floor proxy) | **5.20m** | 6.24m | L1-020 has shorter summed travel |
| Support-seat mean ideal geometric forward hemisphere (four seats) | **~32.2%** | ~28.4% | L1-020 has more theoretical window geometry |
| Ideal geometric Pilot/NAV forward 60° cone | 100% | 100% | **UPPER BOUND**: does not include actual screen, crew, tile seams, sensor volume or refraction |
| Real intact window optical transmission/crew visibility | **UNKNOWN** | **UNKNOWN** | No fully coupled 3D scene ray experiment here |

The 100% modeled Pilot/NAV forward-cone and ~94% geometric hemisphere figures are **optimistic surface-only ray results**. They MUST NOT be substituted for the prior 37-tile nose study (~79% with richer physical obstruction conditions). The source old frame ray test and the new ideal two-shell test are not equivalent. Actual crew-eye WebGL perspectives in the generated viewer are for visual review, not ray-verified optical outputs.

## Four static operational proxy scenes, NOT actual gameplay

1. **Quiet watch:** standing console present, both ladder floor paths pass, captain distance measured. No human motion, fatigue or dialogue model.
2. **Ceres approach:** Pilot and NAV have designed eye-facing screens, sensor + mission roles exist, analytic forward view checked. No Navigator maneuver / spacecraft state was advanced.
3. **4g burn:** all six seated in supported *model shapes*, console unused, hand controls represented at a reference 0.48m arm envelope. **No restraint FEA, 99th-percentile fit, actual reach or acceleration tolerance qualification.**
4. **Fault/Metric/Loom:** unobstructed 2D paths and placeholder command controls. **No live system failure, honest epistemic display runtime or actual crew decision experiment.**

Existing source L1 minimum 2.1m upright-route headroom and current raised flight-deck access are not recalculated. The 2D model deliberately excludes raised Pilot/NAV seats from floor level collision, because naive 2D overlap incorrectly rejected all 500 candidates; these remain **open spatial verification needs**.

## Files and stopping point

- `command/l1_crew_layout_iteration_20261029.py`: deterministic small special-purpose geometry search and comparison
- `command/l1_crew_layout_iteration_20261029_compact.json`: machine-readable 500 summary, 20 detailed results, 5 finalists, 2 operational proxy finalists, provisional choice, caveats
- `render/make_l1_500_search_viewer.py`: generator using existing LOOM WebGL2 engine without changing renderer source
- `render/out/wayfarer_l1_500_search_five_3d_finalists.html`: standalone touchscreen WebGL2, five design buttons, orbit/exterior/cutaway, six eye cameras and standing camera, layer toggles, optogel clear/glare/dark

**Result:** Geometry-only shortlist and provisional concept selected, **not a completed operational design**. Next small action (when continuing) is to physically inspect L1-020 and L1-002 in 3D, verify full swept anthropometric/3D interference and actual controls before declaring a final working L1. A genuine Ceres approach and 4g burn can then be played using the ship's Navigator/existing world model. No canon/Rev7/PR432/runtime mutation.
