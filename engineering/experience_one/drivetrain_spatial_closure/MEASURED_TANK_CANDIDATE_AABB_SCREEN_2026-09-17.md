# Measured tank candidate screening against E1 system/RCS GLB

Date: 2026-09-17. Status: NON-CANON MEASURED SCREEN, NOT COLLISION CERTIFICATION. Source: locally supplied `wayfarer_with_system_rcs.glb` loaded with trimesh; world-space AABBs of named GLB nodes. No GLB or seed mutated. Tank candidates are analytic X-axis circular cylinders, X18–32 m, at four 45-degree quadrature positions. 250 t normal inventory, separate 50 t reserve remains unallocated. Density 800 kg/m3 and usable fraction 0.8 are **illustrative inputs only**, not chosen fluid/storage physics. Shell radius 4.5 m nominal. Tests use nearest 2D circle-to-world-AABB separation where X intervals overlap; a negative value means cylinder intersects the conservative AABB, NOT proven physical mesh collision; positive value is clearance from that AABB under the modeled geometry, NOT full swept/operational clearance. Local script executed against supplied GLB; not GitHub CI.

| Tank diameter / centre radius m | Gross four-tank m3 | Illustrative usable capacity t | Required density kg/m3 at 80% | Radius beyond 4.5 m shell | Adjacent tank gap m | Longer-on-2 AABB gap m | Fore-mid RCS-1 AABB gap m | Launch-bay AABB gap m |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 3.0 / 2.7 baseline | 395.84 | 253.34 | 789.5 | 0 | 0.818 | +0.314 | +0.100 | +0.191 |
| 3.2 / 2.8 | 450.38 | 288.24 | 693.9 | 0 | 0.760 | +0.269 | **-0.100** | +0.020 |
| 3.4 / 2.9 | 508.44 | 325.40 | 614.6 | 0.100 | 0.701 | +0.228 | **-0.300** | **-0.151** |
| 3.6 / 3.0 | 570.01 | 364.81 | 548.2 | 0.300 | 0.643 | +0.190 | **-0.500** | **-0.321** |

Measured GLB node bounds: fore-mid RCS at X18.3–18.7, positive-Y/negative-Z AABB Y3.04–3.78, Z-3.78–-3.04; launch_bay X16–27.5, Y3.6–7.1, Z-2.2–2.2; pressure_hull X0–14, transverse +/-4.3; tank X18–32. Longeron_2 X14–50, Y2.31–2.59, Z +/-0.14. Note earlier suggestion that baseline longerons necessarily intersect tank cylinders is **not supported** by this measured conservative AABB screen: the illustrated baseline has +0.314 m separation from longeron_2 AABB, though all components and true load paths need checking.

**Substantive finding:** Naively enlarging all four circular tanks radially creates a fore-mid RCS conservative-envelope conflict starting at the 3.2 m candidate. At 3.4 m it also conflicts with the launch-bay AABB, contrary to the explicit priority to protect shuttle space. Widening the shell alone cannot cure internal RCS/launch interference. Do not select these candidate geometries or claim 325 t validated capacity.

**Next design direction within user authorization:** preserve baseline cabin, shuttle and RCS; investigate axial extension or noncircular/outboard lobes that avoid the X18.3–18.7 RCS station and the launch-bay Y/Z envelope. If a longer tank extends toward X33+, screen radiator roots and metric/torch boundaries. Investigate moving tank forward X start beyond RCS only if it remains clear of shuttle extraction; reserve allocation, fluid choice, real meshes, structural supports, centre-of-mass/inertia and metric fields remain HOLD. No frozen interface or canonical hull dimension changed.
