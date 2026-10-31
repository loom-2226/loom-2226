# Wayfarer I4 carry-over and crown Option B — 2026-11-01

ALL bodies. ALL sponsors. 2026-2226.

Status: ENGINEERING, NON-CANON, DRAFT/HOLD. This is a new geometry requiring kT acceptance of ceramic pressure-dome milestone and new visuals.

## Source and absorption

Base main 20a1106c, predecessor geometry 5d73cdd1. NEW geometry SHA256 9d6f0059c8e6a4ff314b3d58e9c9b52ff7c9100d624c5c1d06d975531c3573c1.
Source candidate: engineering/wayfarer/candidates/l1_i4_20261029/scene.json on historical main f07354f. The candidate folder and REV7_REV8_L1_CANDIDATE_LINKAGE.md were deleted from this branch after carrying content into wayfarer/config and the renderer. Git history remains.
Existing navigator platform and command terrace were retained; not duplicated. 16 added physical/visual objects: engineering + sensor cabinets, map table and console, workbench and display, four rails, two light strips, two transfers, observation perimeter rail and low-g command point.
Corrections vs candidate: NAV light strip +0.45 m forward, observation rail +0.52 m forward, port transfer foot brought to accessible port ladder landing. Source viewport H=4-X mapped to true ship -X bow frame.

## G1 mass from existing engineering reserve

Old pressure-shell aperture mass credit: 3.310664 t. It is reinterpreted as part of ONE monolithic ceramic pressure shell; no second hidden pressure dome.
New interior hardware: 0.528 t; incremental crown: 0.311419 t; net reserve transfer: 0.839419 t.
Dry mass 867.681453466738 t, S1 wet 1167.681453466738 t. The existing I4 table/workbench/cabinet mass proxies remain allocated as mount/understructure; new components are fitting and surface hardware, not an additional room system. Full CG/inertia rebuilt.

## Crown Option B, no backup

37 nonpressure OUTER protective ceramic panes, [1,12,12,12], radius 3.35m; 10mm thick, ~3.75g/cm2, nominal max hoop chord 1.7341 m (corner diagonal approximately 1.9m).
ONE inner monolithic primary pressure dome diameter 7.0m, 28mm transparent ceramic with assumed density 3750kg/m3; X(r)=2.35-2.15 sqrt(1-(r/4.3)^2), 0<=r<=3.50m. No backup dome, no optogel. 16 Rev7 Strata armour-equivalent closing gores and operating rule unchanged.
NEW kT materials milestone is PENDING: ~7m flaw-controlled pressure ceramic versus old accepted maximum 2.3m segmented pressure panes. No full-scale burst/damage/reliability proof.

## G6 comparison, after new source build

Existing shell comparator 8.0g/cm2, inner ceramic 10.5g/cm2, outer 3.75g/cm2. With closed gores 41.25g/cm2 vs former pressure+armour 35.0g/cm2.
S5 shelter screen 36 points x 600 rays at 2cm step: minimum 40.34g/cm2, zero below 40; intentionally open node-face sensitivity 14.78g/cm2 FAIL. No physical pressure, heavy-ion/secondary dose, debris or optics qualification implied. L1 with gores open is not a shelter.

## G7 and G12

G7 10/10 bounded checks PASS. Every new item checked 3D against couches and ladder shafts. Floor walked grid excludes 221 obstacle cells, retaining 715 connected route cells; S2, S3, S4 and both transfer landings accessible. This is not suited-body 4g egress proof.
G12 manifest 17 current-hash entries: {'viewer': 1, 'exterior': 4, 'cutaway': 2, 'command': 4, 'deckplan': 6}. One exterior/interior GLB at wayfarer/render/out/wayfarer_I4_in_out_9d6f0059.glb. Prior GLB removed.

## Gates after certify.py

| Gate | Verdict |
|---|---|
| G1 Mass and fluids ledger | PASS |
| G2 Torch and reach | PASS |
| G3 Balance and attitude | PASS |
| G4 Power and heat | PASS-DECLARED |
| G5 Structure and loads | PASS-DECLARED |
| G6 Radiation | PASS-DECLARED |
| G7 Compartments and crew space | PASS-DECLARED |
| G8 Shuttle, drones and bay exit | PASS |
| G9 Failures and reserves | PASS-DECLARED |
| G10 Flight dynamics: RCS, torch, Metric, Loom | PASS-DECLARED |
| G11 Canon fit | PASS |
| G12 Images | PASS-DECLARED |

certified=false. Earlier acceptance of 2.3m panes and prior 5d73 images does NOT transfer. New source CG/inertia also means old FQ1-FQ10 flight evidence is historical, not fresh qualification.

### Awaiting declarations
- crown_dome: AWAITING — Rev7 16 closing Strata gores and opening doctrine are retained; their original acceptance applied only to the earlier segmented 2.3m pressure panes, not the new 7m seamless dome.
- crown_monolith_7m: AWAITING — NEW kT ACCEPTANCE REQUIRED: ONE ~7m monolithic transparent ceramic primary pressure dome, X(r)=2.35-2.15sqrt(1-(r/4.3)^2), 28mm nominal thickness, ~10.5g/cm2, full-scale proof and flaw control UNSHOWN. 37 independent outer 10mm nonpressure dust/thermal panes at ~3.75g/cm2, 16 Rev7 closing Strata gores restore ~42.25g/cm2 when closed. No secondary pressure dome, no optogel. This is a speculative 2226 materials breakthrough, not a qualified physical pressure enclosure or dose transport.
- kT_visual_acceptance: AWAITING — Required before treating rendered representation as accepted design evidence; generated images meet source/hash coverage only

Metric arrival HOLD. Navigator EXCLUDED. The separate ship-power-budget task remains OPEN and is not claimed by this I4 branch. No new simulator.
