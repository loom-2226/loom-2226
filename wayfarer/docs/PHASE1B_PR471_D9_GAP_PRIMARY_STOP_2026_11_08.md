# Phase 1b PR #471: approved research packing port and D9 primary-integrity STOP

ALL bodies. ALL sponsors. 2026–2226.

**DRAFT / kT REVIEW / NO MERGE / ZERO QUALIFICATION CREDIT / NO PERFORMANCE TUNING.**

Source main: ea50354e222e77d145a6bbbf49227506d2b560fd (unchanged). Current geometry SHA-256: 88ce19fc8bc4c487b1ad96e2edb1bed17f36188a445070af238afdffada181c1. Complete kT D9 instruction recorded VERBATIM in upstream PR #471.

## Why research 0 vs first upstream 73: one part-set and checker comparison

| Dimension | Approved research #157 | First upstream #471 | Port / consequence |
|---|---|---|---|
| Geometry | Final physical B-rep after **93** explicit cut operations; primary structure never cut | Sector/tube/panel source envelopes largely untrimmed | Original 73 are missing approved D8 geometry operations, not a thrust or ECON problem |
| Inventories | 315 named STEP components (292+17 original, 4 wet lobes+4 caps replace single fuel/wet representations) | 316 source entries (296 dry, 20 S1 fluids): 194 installed + 122 no_render/unlocated | The extra upstream no_render part is the unlocated 0.660802t D8 doubler; no physical fit credit |
| Names | Four indexed fuel lobes/caps; C-lite fluid index 16; STEP exports 32_3 and 34_3 instead of decimal point | Four named fore/aft-port/starboard lobes/caps; C-lite fluid index 19; 32.3 and 34.3 labels | Exact aliases reconciled to match upstream set before any collision check |
| Tunnel and collar | Arm physically relieved about tunnel_0/tunnel_1 and docking_collar, retaining 98.073% envelope; courier collar notch | Arm intersects tunnel_0 2.940531m3, tunnel_1 0.455316m3, collar 1.369856m3 | Approved arm/courier cuts, NOT moving primary tunnel/collar |
| Manifold and floor | Manifold cut around ring frame and longerons; L2–L4 floors relieve racks | Frame_34/manifold 1.536427m3; each L2–L4 floor/rack 0.618360m3 | Equipment and secondary floor yield; no primary frame movement |
| Water jacket | Actual B-rep overlaps subtracted before 1.931t service reservoir transfer | Mass debited without corresponding installed jacket Boolean cuts | Original jacket_outer/ceiling and floor each had 0.424115m3 intersection |
| Fin and equipment solids | Four deployed thin membranes, secondary notches and satellite equipment clearances in final B-rep | Stowed proxy panel envelopes and untrimmed equipment represented | First upstream category-d scan cannot inherit lab zero |
| Part-set handling | #157 originally scanned all 315 including 121 no_render representation objects | First D9 omitted 122 no_render objects: 194 installed solids | Revised same-rule replay selects **the SAME 194 installed objects** on both sides, excluding the same 121 proxies and upstream's one extra unlocated D8 placeholder |
| Checker rule | #156 OpenCascade/build123d 0.13.0 triage, category d, threshold >0.01m3 after reliefs; 49,455 pairs (315 choose 2) | Same triage and threshold but 18,721 pairs (194 choose 2) with NO reliefs | The failure was not a threshold change; shared 194-item replay, 18,721 pairs each, found 0 category-d conflicts once the approved STEP and units were used |
| CAD STEP units | Source reference authored in metres; STEP export Unit.M | Import reads numeric mm; initial raw volume had 1e9 scaling error | Explicit 0.001 linear conversion is checked against the unchanged core-trunk span; **no threshold relaxation** |

## CAD port and newly found primary-integrity STOP

Port is the actual approved named #157 STEP (stored losslessly as frozen_research_3p8_forward.step.gz), not a recreated outer sector. Its D8 notches, true 4-lobe fuel and protective water geometry remain traceable. The four core water B-reps were reduced at the forward settled boundary to match kT's 245.390431711t physical upstream remass, down by 0.080959521t from the lab B-rep 245.471391232t. No new fuel, propulsion or structural mass.

After unit and name reconciliation, the shared D9 replay on 194 installed parts has **0 category-(d)** and **0 CAD errors**, both lab reference and initial migrated water check (GitHub run https://github.com/loom-2226/loom-2226/actions/runs/42431225602). That numerical intersection result is NOT sufficient for physical integrity.

The independent stricter protected-primary audit checks both no_render and installed G5 members against native source geometry, including bounding geometry and B-rep symmetric difference. It STOPPED at **dry:nozzle**: original/native and ported volumes both 16.41090264m3, but bounding-box delta **229.74m** and symmetric difference **32.821805284m3**. Volume-only checks in the earlier replay had missed the displacement. It might be a STEP import/export transform issue, but no cause is verified. It does NOT justify moving/rebuilding the physical nozzle. The evidence file records D8_primary_shape_unchanged=false and pass=false. The approved CAD is **NOT source-verified**.

Strict failure evidence: https://github.com/loom-2226/loom-2226/actions/runs/42431893588 . Source data: wayfarer/results/out/D9_BREP_CLASH_REPORT.json. The D9 checker rejects any future upstream geometry hash different from its pinned source until the geometry is independently reconstructed. No one may override this by citing the frozen research zero-conflict STEP.

## Evidence regeneration and full certify

- G7 I4 human factors: 16/16 current-hash bounded checks pass. Pressure seal, occupant motion, 4g loads and true swept egress remain OPEN.
- G12: 37 current-source-hash files (13 exterior, 4 cutaway, 12 command, 7 deckplan, 1 viewer), two-scene GLB, 4 x 0.95t wet lobe and 4 x 0.125t dry cap labels, separate C-lite labels. Render evidence generated by full Actions run https://github.com/loom-2226/loom-2226/actions/runs/42431463430 . These pictures derive from the analytic source representation, NOT a claim that every exact CAD notch is depicted in the renderer.
- Full upstream G1–G12 plus D9: G1 PASS; G2 PASS (ideal ECON 707.845km/s); G3 PASS; G4 PASS-DECLARED; G5 PASS-DECLARED; G6 PASS-DECLARED (node-face design 41.67g/cm2; open-bore sensitivity 18.89); G7 PASS-DECLARED; G8 PASS; G9 PASS-DECLARED; G10 PASS-DECLARED; G11 PASS; G12 PASS-DECLARED; **D9 FAIL**.
- Full CI run: https://github.com/loom-2226/loom-2226/actions/runs/42432092114 . Source report: wayfarer/results/out/certification_report.json . certified=false. Legacy certify.py CLI exits 0 even if gates fail; strict CI correctly exits FAIL.

## Outstanding physical issues and decision boundary

Immediate BLOCKER: reconcile imported approved nozzle B-rep pose against the immutable current source nozzle, with an independent CAD transform/placement audit, before any new installed fit PASS. If any genuine primary movement is required, STOP and return to kT; do not repair by changing nozzle, primary frame/tunnel, or the 0.01m3 threshold.

Other OPEN items: fitted D8 physical doublers (0.660802t bookkeeping only); unlocated tank webs/baffles; actual cryogenic tank walls/lines/insulation and boiloff; G8 zero margin dynamic sweeps; courier external mount, strake heat and MMOD; physical flight/RCS trials and radiation transport beyond areal column; D9 representation for 122 no_render/unlocated items. No credit for them.

**Disposition:** PR #471 remains DRAFT, OPEN, UNMERGED. Main and frozen research PRs unchanged. No performance tuning. kT reviews all evidence before any additional geometry authority or merge.
