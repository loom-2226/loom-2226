# Wayfarer v0.5.7 (rev 6)

ALL bodies. ALL sponsors. 2026-2226.

**NON-GOVERNING SANDBOX.** No canon promotion and no runtime integration. Do not put the amendment in `canon/current/`. PR #430 stays as is. Let loom-gate run; no bypass.

This folder holds only the current design. Earlier revisions are in git history; rev 5 is commit `ef1b871`.

| Read | For |
|---|---|
| `SPEC.md` | The ship as it stands |
| `CERTIFICATION_BASIS.md` | What "certified" means (v0.2, agreed by Claude and Sol) |
| `out/CERTIFICATION_REPORT_v0.5.md` | The latest gate results (generated) |
| `PROPOSED_CANON_AMENDMENT_v2.4f.md` | What would change in canon; kT's decision |
| `REVIEW_RECORD.md` | Reviews and decisions, in order |
| `render/out/wayfarer_v05_viewer.html` | Phone 3D viewer, with a toggle back to rev 5 |

## What changed in rev 6

kT's four decisions of 2026-10-26:

1. **Torch card:** main's working card now governs, held to the 11.36 TW the cooling is sized for. FAST, HARD and LIMIT thrust are unchanged. ECON thrust drops to 3.4 MN (burns are longer; Δv is the same).
2. **Torch steering:** 1° of thrust-vector authority, so the torch keeps its thrust line through the centre of mass.
3. **Axial RCS:** one 25 kN axial thruster per cluster (8 in all, 4.0 t from the reserve), so the ship can translate along its axis.
4. **Loom configuration:** declared in the card: strakes stowed, crown gores closed, docking collar free.

Results:
- G10 now passes with two declared items (25/25 checks).
- Every gate is PASS or PASS-DECLARED.
- Two new declared items await kT: axial RCS plume clearance, and the 15-minute burn coasts used in the G10 tests.
- Dry mass is unchanged at 867.7 t. The reserve is 47.6 t.

## Run

From the repository root, so that G10 can import main's `src/` modules:

```sh
sh design/wayfarer/v0.5.7/run_all.sh
```
