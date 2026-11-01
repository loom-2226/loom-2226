# Wayfarer L1-I4 completeness repair: 2026-11-01

**ALL bodies. ALL sponsors. 2026–2226.**

Status: ENGINEERING, DRAFT, NON-CANON, NON-RUNTIME, NOT MERGED. Audit source f07354f I4 scene and brief against PR #439. All old snapshots remain in git history.

## Final source and acceptance status
- Geometry SHA256: 702cca4ef985f754b066e4289f3cc63a4d13c87608b40a75fc9520cf67d0cfb3.
- Dry mass: 867.681453 t, S1 dispatch 1167.681453 t. Remaining engineering reserve 17.786216 t.
- G1–G12: G1 PASS, G2 PASS, G3 PASS, G4 PASS-DECLARED, G5 PASS-DECLARED, G6 PASS-DECLARED, G7 PASS-DECLARED, G8 PASS, G9 PASS-DECLARED, G10 PASS-DECLARED, G11 PASS, G12 PASS-DECLARED.
- Machine certified=false, kT declarations accepted 18/22. Pending: crown_dome, crown_monolith_7m, aoi_failure_independence, kT_visual_acceptance.

## I4 source preservation (no silent drops)

- Original source scene f07354f: docs/I4_ORIGINAL_SCENE_2026_10_29.json preserved verbatim. Source implementation brief and README preserved in docs. The historic Canvas2D standalone viewer in render/i4_original_canvas2d_viewer.html, NOT current 3D geometry authority. Original AOI-2226 research from 7240dc21 preserved in docs.
- Integrated original seven interior blocks mapped to terrace platform, NAV platform, five physical work items; all six seats and six displays retained, four rails, two lights, two level transfers, observation rail, common map console, standing mission point and independent workbench accounted.
- No named kT drops. Source item mapping test under lab/test_i4_completeness.py fails on extra unmapped original block, seat/screen, rail, light, transfer, console, phase, missing rendered platform, missing preserved source file or changed pane pattern.
- Original three phases in docs/I4_INTEGRATED_OPERATING_PHASES_2026_11_01.md: coast+standing collaboration; approach+six specialist stations; 4g+six occupied seats; standing stations inactive. Under thrust at 4g, no standing crew; 5g remains structural limit only.

## Crown geometry and visual acceptance

- 37 OUTER nonpressure ceramic protection tiles [1,12,12,12], ring edges EXACT source [0,0.75,2.0,2.75,3.5] m. Final ring stagger π/12 restored. Maximum outer hoop chord 1.812m < previous 1.9m check. No physical constraint was found requiring silent 3.35m cap; original change reverted.
- Old projected glass area 37.516 m2 becomes π·3.5² = 38.485 m2. Additional outer protective ceramic mass 0.036319t is paid from reserve, no new dry mass. The two independent 7m ceramic pressure domes and nonpressure 3.023m3 AOI gel are unchanged from kT Option A.
- Current 3D WebGL renderer now uses independent alpha-blended crown_glass, crown_pane, AOI visual surfaces rather than opaque black window glass. No real optical transmission, NIR modulation or pressure-dome stress proof implied.
- Both independent pressure domes must survive failure of the other with gel present and no coupling; unverified and kT HOLD. Closed Rev7 Strata 16 gores and old operating rule unchanged.

## L1 interior hatches and access

- NAV source platform (x2.76–2.86m, y±1.325m, z1.45–3.65m) now appears in authoritative integrated scene and 3D/GLB. Command terrace appears alongside it; both already in the mass ledger, not duplicated.
- Two L1/L2 ladder holes at y=±1.4m, 0.8m clear, now have visible parked-open hatch leaves in 3D, with no obstruction of shaft or occupied station AABB. They are represented from existing outfitting allowance, no new mass, not a demonstrated pressure seal/closure actuator.
- G7 current SHA 11/11 bounded AABB/route/hatch clearance checks PASS. No 4g moving-body proof, no suited egress hardware certification.

## G6 and G12

- 36 berth points × 600 rays at 2cm in S5: min 40.07 g/cm², failing rays 0. Open node faces sensitivity 14.71 g/cm² unsafe; node faces must stay filled.
- G12 current image manifest 17 items with identical source hash, plus single exterior/interior two-scene GLB: render/out/wayfarer_I4_in_out_702cca4e.glb. Historical I4 Canvas2D is labelled historical, not additional current source authority.

## FQ1–FQ4 recomputation
- 78/78 conventional numerical cases PASS at dt=0.2s, both full and half propellant. Per gate: FQ1 6/6, FQ2 48/48, FQ3 12/12, FQ4 12/12.
- Input fixture derived from the current S4 dry/no-remass source mass, centre of gravity, full inertia tensor, with existing unchanged RCS/torch propulsion equipment and fuel tank source. Reconstructed S1 CG and mass match the current integrated geometry exactly; old PR435 hash cases were not re-labelled.
- Does not certify hardware, FQ5–FQ10, 0 remass operation, Metric arrival or Navigator. Prior FQ5–FQ10 evidence is historical and separate.

## Independent regression checks

- Full pre-existing flight-lab regression: **61/61 PASS**, including old Metric engage HOLD/torch overlap refusal. This is regression only, not new Metric system approval.
- Original-scene source mapping and physical pane-ring checks: **2/2 PASS**.
- GitHub historical viewer, brief, source scene and AOI research copied byte-for-byte from f07354f and 7240dc21; historical README intentionally retains original Markdown hard-break whitespace.

## Remaining kT acceptance / scope

Four outstanding declarations from the unchanged Option A acceptance boundary:
- crown_dome: Rev7 16 closing Strata gores and opening doctrine are retained; their original acceptance applied only to the earlier segmented 2.3m pressure panes, not the new 7m seamless dome.
- crown_monolith_7m: kT Option A 2026-11-01: TWO independent full-pressure ~7m transparent ceramic domes, each 28mm/10.5g/cm2, shaped X(r)=2.35-2.15sqrt(1-(r/4.3)^2), backup shifted 0.12m forward. Both must survive loss of the other; 37 outer segmented nonpressure panes +16 closure gores unchanged. 7m monolithic materials fabrication/pressure/impact and optical radiation behaviour UNSHOWN.
- aoi_failure_independence: AOI-2226 ~3.023m3 (~3t) gel between two separately sealed pressure domes, gap min normal 5.973cm with backup axial offset ~12cm. Neither pressure-bearing nor a pressure seal. Each independent dome MUST withstand full 101.3kPa after other's failure while optogel is present, WITHOUT shock, fracture, crack bridging or fast pressure-pulse coupling. The research has NO measured high-rate response or independent-shell survival test; do not credit impact damping. Rim slip/contact interfaces and >=56L illustrative thermal-expansion compliance still require engineering.
- kT_visual_acceptance: Required before treating rendered representation as accepted design evidence; generated images meet source/hash coverage only

Metric arrival HOLD. Navigator EXCLUDED. Independent ship power budget remains OPEN. PR #439 remains draft and unmerged.
