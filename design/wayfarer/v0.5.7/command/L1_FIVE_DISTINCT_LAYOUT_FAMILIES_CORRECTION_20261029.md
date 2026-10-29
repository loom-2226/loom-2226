# L1 corrected comparison: five visibly distinct arrangement families
**2026-10-29 · NON-CANON / NON-RUNTIME / RESEARCH**

## Why the previous viewer failed as a design comparison
The first 500 candidates were minor perturbations of **one** same support-seat ring arrangement. The five so-called finalists differed by tens of centimetres or modest rotations, so they looked essentially identical at normal 3D zoom. It was not an inactive UI control: a headless browser run confirmed all five buttons changed the crew coordinates and rebuilt the 3D mesh without JS/WebGL errors. **But five parameter tuples did not constitute five design concepts.**

The viewer also defaulted to an exterior-facing angle with the canopy and opaque rim over the chairs, obscuring differences. The cutaway removed half the floor and visually stranded support seats. Both errors are corrected below.

## Corrective, bounded second search
Five **explicitly different support-station plan forms**, with 100 small variations per family; fixed same 8.6m pressure hull, 6 crews (2 front, 4 support), source flight deck and two ladders, the separate 37 outer tiles / two pressure domes / speculative optogel.

| ID | Family | Operating idea | 2D-route proxy, sum to both ladders (m) | Ideal mean support forward hemisphere |
|---|---|---|---:|---:|
| L1-A | Inboard panoramic ring | Four seats closer to inner shoulder, improved sky | 5.20 | 34.1% |
| L1-B | Perimeter free core | Keep workstations outboard, large central floor | 5.46 | 28.0% |
| L1-C | Paired mission pods | Two adjacent pairs, team collaboration and shared displays | 4.94 | 32.2% |
| L1-D | Staggered specialist stations | Alternate inner/outer workstations for differentiated roles | 5.20 | 31.9% |
| L1-E | Command fan and mission wings | Bring Captain and mission closer to central station, others outward | 5.46 | 32.3% |

Valid 2D floorplan/layout candidates by family: A 100/100, B 100/100, C 6/100 (mostly blocked 2D paths or standing console), D 94/100, E 78/100. Total 378/500 on this revised, explicitly structured search. All five selected family representatives pass the **simplified** floor plan and analytical window geometry filters, NOT full 3D collision, 4g seat ergonomics or genuine human workload.

Previous numerical 'L1-020 winner' belongs to the **narrow ring-only search** and cannot legitimately be called better than these five new conceptual arrangements. There is **no proven winner** among the five full interior options yet. Do NOT reinterpret 100% ideal Pilot/NAV forward-surface rays as actual window throughput or crew sightlines.

## Browser-verified corrected viewer
`render/out/wayfarer_l1_five_distinct_layouts_corrected.html`:
- Switches between these FIVE family layouts, not slight variations of one.
- Shows five same-scale plan thumbnails, with seat orientation, ladder openings and real low-g command station (orange C).
- Hides the non-canon canopy and ring by default **in the interior comparison only**, with switches still allowing the user to inspect every layer.
- Uses raised view to show actual seat positions; does not clip away floor unless the exterior canopy layers are enabled.
- Maintains six segmented Kazbek-inspired concept work seats, role screens, crew figures and physical standing console. These remain concept meshes, not structural model.
- Tested in actual headless Chromium with WebGL software fallback: clicking each family changed its active button/labels, support-seat coordinates and geometry; browser showed no page errors and `gl.getError()=0`.

The first 3D comparison is superseded; keep it in git as reproducible *failed design-space lesson*, do not delete history. This corrected viewer is the usable comparison.

## Next action and stop
Visually compare A–E in actual crew views, with 3D seated-body and control reach checks and the fixed source envelope before selecting a new 'winner'. Flight/deck/ladder/pressure geometry is retained; no source PR #432, Rev7, main, canonical Technology Timeline or runtime edits. **No qualification claim.**
