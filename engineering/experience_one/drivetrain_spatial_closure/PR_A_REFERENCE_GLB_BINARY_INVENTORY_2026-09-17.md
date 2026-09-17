# PR A — Reference GLB binary inventory (partial audit)

**2026-09-17; status PARTIAL / NON-CANON.** Measured from actual supplied files in the working container, not inferred from filenames. SHA-256 computed over raw file bytes; scene bounds and node/geometry inventories inspected with `trimesh.load(path, force='scene')`. Coordinates are those returned by the scene loader, not an independently validated governing coordinate-frame contract. No geometry modified. Binary files have not been committed to GitHub.

| Reference input | Bytes | SHA-256 | Scene nodes | Geometries | Scene bounds min → max (m, assumed until frame/units audited) |
|---|---:|---|---:|---:|---|
| `WAYFARER_E1_TORCH_STANDALONE.glb` | 49,652 | `e86da58a1cfa9d9b0092c697e8da034d1df5270444b0ea212151e1780f5b41f0` | 17 | 13 | `[37.96000000089407,-3,-3]` → `[58,3,3]` |
| `wayfarer_with_system_rcs.glb` | 111,448 | `0e67b1ee0e09404d7a6ef663b2accd0d5ee1e34d48b4a6672cef0e09dbfd714d` | 40 | 21 | `[0,-5.149999976158142,-5.149999976158142]` → `[57,7.1,5.149999976158142]` |
| `wayfarer_e1_metric_integration_candidate.glb` | 223,116 | `9a9f4d7df97af74a768c9ce53a539194321b314c842934bbed914b6e6f50ab2d` | 372 | 348 | `[0,-5.149999976158142,-5.149999976158142]` → `[58,7.1,5.149999976158142]` |

## Observed identities

- Standalone torch graph: `SYSTEM_PRIMARY_PROPULSION_TORCH`, `TORCH_SPECIFICATIONS`, `PHYSICAL_PLUME_UNRESOLVED`, `PRIMARY_THRUST_AXIS`, `NOZZLE_EXIT_INTERFACE`, `SOURCE_NOZZLE_INTERFACE`, `SHIELD_SOURCE_INTERFACE`, `SHIELD_FORWARD_INTERFACE`, `TORCH_MAGNETIC_NOZZLE_ENVELOPE`, `AFT_THRUST_FRAME_INTERFACE`, four `THRUST_FRAME_CONVERGENCE_*`, `TORCH_REACTOR_SOURCE_ENVELOPE`, `TORCH_SHADOW_SHIELD_ENVELOPE`. Thirteen geometries include shield/source/nozzle candidate envelopes and four struts.
- RCS reference geometry names include `pressure_hull`, `tank_1`–`tank_4`, `longeron_1`–`longeron_4`, `radiator_1`–`radiator_4`, `technical_core`, `launch_bay`, `planetary_launch`, `propulsion_shadow_shield`, `reactor_torch_envelope`, `magnetic_nozzle`, `docking_collar`. `SYSTEM_RCS` and its named RCS groups are graph nodes.
- Metric integration candidate contains the same first 20 listed RCS reference geometry identities plus additional geometry; graph includes `METRIC_RELATIONAL_PLANT`, `STATE_VISUALIZATION`, `SERVICE_ROUTING_CANDIDATE`, `BOUNDARY_METRIC_NODES` and boundary-node instances. Name agreement alone does not prove unchanged meshes/transforms or absence of duplication.

## Discrepancies and holds

**A-EXTENT-01: OPEN.** Torch standalone and metric candidate have maximum X=58 m, while RCS reference has maximum X=57 m and the frozen handoff says 57 m main body. This establishes a measured difference, **not its cause**: inspect the responsible node/mesh and local/world transforms before classifying hull versus marker versus nozzle extension. No rescale, trim, or change to frozen torch permitted.

**A-FRAME-02: OPEN.** Validate glTF units, axis mapping, all node local/world transforms, torch mating and common frame against authoritative geometry producers; `trimesh` scene bounds alone are insufficient.

**A-SOURCE-03: OPEN.** Find governing repository producer paths, exact source commits, prior Shipyard PR diffs and reference export route. The attached handoff is secondary to governing executable sources.

**A-IDENTITY-04: OPEN.** Compare actual tank/torch/RCS/metric geometry and transforms across all three scenes, classify placeholders and any duplicate instances.

**A-FIXTURE-05: OPEN.** Implement a reproducible binary manifest/checker and targeted baseline tests with an approved reference-file acquisition path; this audit records measurements but does not itself close the gate.

PR A gate remains **OPEN**; no PR B/C/D geometry qualification follows from this inventory.
