# Wayfarer v0.5.7 candidate (for Sol's review, side by side with v0.5.6)

ALL bodies. ALL sponsors. 2026-2226.

**NON-GOVERNING SANDBOX.** v0.5.1 (Sol's review fixes) plus kT's torch heat package of 2026-10-25: remass-shell torch, cleaner fuel, burn moved aft, four 1,750 K hot fins. No canon promotion, no runtime integration. v0.5 in PR #430 stays as archived.

v0.5.7 (rev 4) makes the crown dome the main design, replacing the 8 nose windows, and maximises viewports for livability: a panoramic band round the L2 common deck and 22 round viewports, all shielded by acrylic plugs and closed by flush Strata shutters. Rev 4 closes the band's load path with titanium edge rings, a lounge transom and plate-sized panes (`habitat/VIEWPORT_BAND_STUDY.md`). It also adds four sized longerons (matching canon) with their joints, shielded viewports (10 berths plus 6 in the habitat, with acrylic plugs) and a service shield band. The spine and visor sketches stay concepts. The accepted v0.5.6 files are in `compare/v0.5.6/`, and the viewer toggles between the two versions.

Read in this order:
1. `CHANGES_v0.5.7.md`: what v0.5.7 changes, the v0.5.6 comparison table, and what Sol is asked to review.
1. `structure/LONGERON_STUDY.md` and `habitat/berth_viewports.png`: the two studies behind v0.5.7.
1. `command/BOW_OPTIONS_STUDY.md`: the crown dome (option C, now adopted). `docs/concepts/`: the bow and spine sketches.
1. `CHANGES_v0.5.6.md`: the full package, kT's decisions, and what Sol is asked to agree and run.
1. `CLOSEOUT_PLAN_v0.5.6.md`: the close-out list (all items done except Sol's steps).
1. `command/L1_OPTIONS_v0.5.5.md`: the L1 command level, five options scored against NASA-STD-3001-derived criteria, and the built flight-deck design.
1. `command/L1_COMMAND_REPORT_v0.5.4.md`: the first L1 candidate (option A) and the builder volume fix.
1. `habitat/HABITAT_INTEGRATION_REPORT_v0.5.3.md`: Sol's habitat package integrated on top of v0.5.2, and the concrete issues found.
1. `CHANGES_v0.5.2.md`: the torch heat package and what Sol should re-check.
1. `REVIEW_RESPONSE_v0.5.1.md`: what changed after Sol's review, finding by finding.
2. `CERTIFICATION_BASIS_v0.1.md`: what "certified" means (proposed; Sol to agree).
3. `out/CERTIFICATION_REPORT_v0.5.md`: the generated verdicts and every check.
4. `SPEC_v0.5.2.md`: the ship in one page (v0.5.2; the habitat delta is in the integration report).
5. `PROPOSED_CANON_AMENDMENT_v2.4e.md`: what canon would change if kT adopts it (v2.4d, for v0.5.6, kept for comparison).

## Re-run

| Step | Command | Needs |
|---|---|---|
| Geometry and mass properties | `python3 build_v05.py` (about 1 min) | Python 3, standard library |
| Gates G1-G12 | `python3 certify.py` | Python 3, standard library |
| Everything, including images | `./run_all.sh` | adds Node and Playwright's Chromium |

`build_v05.py` is deterministic: a clean re-run reproduces `out/wayfarer_v05_geometry.json` byte for byte. `certify.py` checks images only by their manifest and geometry hash, so it runs without a browser.

## Files

| Path | What |
|---|---|
| `inputs/wayfarer_v05_inputs.json` | every design input, each with its provenance |
| `inputs/cert_criteria_v0.1.json` | every pass threshold (A = authored, open to challenge); v0.5.2 adds three for the new hardware |
| `inputs/kt_decisions.json` | kT's decisions on declared assumptions (read by `certify.py` only) |
| `build_v05.py` | parts, rooms, features, protected-water split, thrust-line offset, mass properties for S1-S7 |
| `certify.py` | the twelve gates; writes the report, its JSON and the Navigator card |
| `out/wayfarer_v05_geometry.json` | the hashed geometry everything else is made from |
| `out/certification_report.json`, `out/CERTIFICATION_REPORT_v0.5.md` | verdicts |
| `out/wayfarer_v05_card.json` | machine-readable ship card for Navigator (gate G10) |
| `torch/torch_heat_budget.py`, `torch/torch_heat_inputs.json` | torch heat model (non-governing; standard library; `certify.py` imports step S4) |
| `torch/fin_layout.py`, `torch/fin_layout_inputs.json` | hot-fin layout search, 3 to 8 fins (exploration; needs numpy) |
| `render/loomgl.js` | small WebGL2 renderer (no libraries) that builds meshes from the part shapes |
| `render/render.html`, `render/render.js`, `render/views.json` | still renders |
| `render/deckplans.py` | deck plans from the room data |
| `render/make_viewer.py` | the phone 3D viewer |
| `render/out/` | the images, `manifest.json` (each with the geometry hash) and `wayfarer_v05_viewer.html` |
