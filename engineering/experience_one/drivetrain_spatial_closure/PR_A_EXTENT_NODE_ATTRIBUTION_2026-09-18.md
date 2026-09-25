# PR A — 57/58 m extent: responsible nodes (partial resolution)

**2026-09-18 · NON-CANON · reference binaries only.** Inspected the three byte-identified GLBs in `PR_A_REFERENCE_GLB_BINARY_INVENTORY_2026-09-17.md` with `trimesh.load(path, force='scene')`; for every geometry node inspected `scene.graph[node]` and its geometry-local bounds, applying the returned world transform. The numbers below are observed scene-coordinate results, not an independently certified metre/unit or coordinate-frame contract. No GLB changed.

| Reference | Responsible node / mesh | Geometry-local X bounds | Node world X translation | Observed world X max |
|---|---|---|---:|---:|
| Torch standalone | `PRIMARY_THRUST_AXIS` / `primary_thrust_axis` | -10 to +10 | 48 | **58.00** |
| Torch standalone | `NOZZLE_EXIT_INTERFACE` / `nozzle_exit_interface` | -0.04 to +0.04 | 57 | 57.04 |
| Torch standalone | `TORCH_MAGNETIC_NOZZLE_ENVELOPE` / `magnetic_nozzle_candidate_envelope` | -3.5 to +3.5 | 53.5 | **57.00** |
| RCS reference | `magnetic_nozzle` / `magnetic_nozzle` | -3.5 to +3.5 | 53.5 | **57.00** |
| Metric integration candidate | `PRIMARY_THRUST_AXIS` / `primary_thrust_axis` | -10 to +10 | 48 | **58.00** |
| Metric integration candidate | `NOZZLE_EXIT_INTERFACE` / `nozzle_exit_interface` | -0.04 to +0.04 | 57 | 57.04 |
| Metric integration candidate | `TORCH_MAGNETIC_NOZZLE_ENVELOPE` / `magnetic_nozzle_candidate_envelope` | -3.5 to +3.5 | 53.5 | **57.00** |

**A-EXTENT-01 finding:** The scene maximum X=58 in both torch-containing files is attributable to the named `PRIMARY_THRUST_AXIS` geometry (a 20-unit-long axis object centred at X=48), **not** the magnetic nozzle envelope. The exit-interface geometry reaches X=57.04; it is a separate interface primitive, not evidence of a one-metre hull stretch. The RCS reference's nozzle reaches X=57. This resolves the *identity of the responsible extent-producing node*, but does not independently establish its intended semantics or authorize excluding markers from every spatial check. Do not rescale, trim, or modify frozen torch geometry.

**Remaining PR A holds:** A-FRAME-02 verify actual glTF unit/axis contract, transforms and mating against governing producer; A-SOURCE-03 identify authoritative source/export and commits; A-IDENTITY-04 compare actual meshes/transforms and duplication across scenes; A-FIXTURE-05 implement repeatable binary manifest/checker with reference acquisition. A-EXTENT-01 may be marked **node-attributed, pending governing-source confirmation**; PR A gate remains OPEN. The scene's overall AABB must not be misrepresented as hull length.
