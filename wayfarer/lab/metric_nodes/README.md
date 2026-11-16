# Metric node faces: conflict map and fix options (2026-11-15, revised 2026-11-16)

ALL bodies. ALL sponsors. 2026-2226.

**NON-CANON proposal by Claude for kT.** This lab places the 208 node faces (13 rings x 16, the
PR #184 revisable baseline, taken from `wayfarer_v05_geometry.json`) against the hull and the
exterior hardware.

- `node_map.py` produces `node_conflict_map.png`.
- `node_data.py` produces `nodes_before_after.json`. The review viewer uses it for its
  Metric nodes overlay (Off / Now / Proposal).

## Now (screening counts, reproduced by Sol)

| Nodes | Where |
|---|---|
| 80 | On the torch chain |
| 20 | Under the stowed strakes, over the longerons |
| 12 | On the bay-door leaves |
| 8 | On or next to hardware |
| 16 | On the bow shoulder |
| 72 | Clear |

These are screening counts, not solid-body interference results.

## Proposal (revised after Sol's PR #552 review)

| Nodes | Treatment | Status |
|---|---|---|
| 16 | Ring 0 stays exactly where it is | Settled by kt_decisions `bow_shoulder_surface_2026_11_13` |
| 80 | Into the four hot-fin root trusses, 20 per fin | **Option only, unresolved** |
| 20 | Into the strake root fittings | Proposal |
| 48 | The 4 bay rings, re-spaced clear of the door leaves | Proposal |
| 7 | The hardware moves instead of the node | Proposal |
| 37 | Unchanged | - |

The hot-fin option has two problems:

- **Thermal:** the roots run at 1,750 K in Torch against the 20 K cryoplant, with no isolation or
  heat budget.
- **Domain coverage:** clustering the aft nodes on four lines cannot be qualified while PR #356
  has no operator that maps node placement to the translation-domain boundary.

No mass is booked and nothing is placed in canon. Placement is kT's decision, carried out against
the PR #184 baseline.

## Even layouts that fit around everything (2026-11-16)

`node_optimize.py` produces `node_layouts_even.json`, and `node_layouts_picture.py` produces `node_layouts_even.png`.

**Method:** weighted k-means snapped to allowed mount sites, best of 4 restarts.

**Allowed sites:**

- Hull skin, excluding:
  - the bay-door leaves
  - the stowed strake bands (the strake root line is allowed)
  - the longerons
  - hardware, windows, hatches and cameras
- Optionally the thrust-cone skin.
- Optionally both faces of the hot-fin root trusses.
- Ring 0 stays fixed.

**Result:** the best layout uses the cone and the fin roots.

| Metric | Today | Best layout |
|---|---|---|
| Nodes on a no-go zone | 120 | 0 |
| Network in one piece | No | Yes |
| Worst gap | 5.0 m | 4.3 m |
| Gap covering 95% of the skin | 3.0 m | 2.5 m |
| Load spread (CV) | 0.29 | 0.28 |

The best layout places 133 nodes on the hull, 20 on the cone, 39 on the fin roots and 16 on ring 0.

Hull-only and cone-only layouts leave the reactor and nozzle 12 to 20 m from the nearest node.

**Open:**

- The fin-root heat soak.
- The strake-root line is still a kT decision.
- This measures geometric evenness only. It is not a domain certification (PR #356).
