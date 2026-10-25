# Wayfarer v0.5 certification record

ALL bodies. ALL sponsors. 2026-2226.

**NON-GOVERNING SANDBOX.** Successor to the v0.4 and v0.4.1 records. No canon promotion, no runtime integration.

Read in this order:
1. `CERTIFICATION_BASIS_v0.1.md`: what "certified" means (proposed; Sol to agree).
2. `out/CERTIFICATION_REPORT_v0.5.md`: the generated verdicts and every check.
3. `SPEC_v0.5.md`: the ship in one page.
4. `PROPOSED_CANON_AMENDMENT_v2.4d.md`: what canon would change if kT adopts it.

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
| `inputs/cert_criteria_v0.1.json` | every pass threshold (A = authored, open to challenge) |
| `build_v05.py` | parts, rooms, features, protected-water split, thrust-line offset, mass properties for S1-S7 |
| `certify.py` | the twelve gates; writes the report, its JSON and the Navigator card |
| `out/wayfarer_v05_geometry.json` | the hashed geometry everything else is made from |
| `out/certification_report.json`, `out/CERTIFICATION_REPORT_v0.5.md` | verdicts |
| `out/wayfarer_v05_card.json` | machine-readable ship card for Navigator (gate G10) |
| `render/loomgl.js` | small WebGL2 renderer (no libraries) that builds meshes from the part shapes |
| `render/render.html`, `render/render.js`, `render/views.json` | still renders |
| `render/deckplans.py` | deck plans from the room data |
| `render/make_viewer.py` | the phone 3D viewer |
| `render/out/` | the images, `manifest.json` (each with the geometry hash) and `wayfarer_v05_viewer.html` |
