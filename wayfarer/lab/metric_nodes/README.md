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

## Creative options (2026-11-16)

`node_options.py` produces `node_options.json`, and `node_options_picture.py` produces `node_options.png`.

| Option | Evenness | Ship length | Notes |
|---|---|---|---|
| 1 Compact torch + nozzle-coil ring | 0.26 | 48.2 m | Reactor 7 → 4 m, burn point 6 → 4 m; rear nodes on the cold coil frame |
| 2 Telescoping nozzle | 0.27 | 46.3 m in Loom config | Nozzle coils park as a collar round the reactor |
| 3 Shuttle completes the hull (+ 1) | **0.25** | 48.2 m | No bay doors: the docked shuttle's back is the hull and carries 12 nodes |
| 4 End-cap lens, no aft hardware | geometrically fails | 53.3 m | Worst gap 14.8 m |

All options are NON-CANON sketches.

## Retractable nacelles (kT idea, 2026-11-16)

`node_nacelles.py` produces `node_nacelles.json`, and `node_nacelles_picture.py` produces `node_nacelles.png`.

Two 14 m nacelles (x 39.5-53.5, az 0 and 180):

- **Burning:** tucked against the torch at r 3.4.
- **Metric / Loom:** swung out to r 4.6, with the torch cold (Canon II s14).

Results:

| Layout | Worst gap | Evenness | Skin in reach |
|---|---|---|---|
| Two nacelles | 5.0 m | 0.27 | 85% |
| Three nacelles (+ keel) | 4.7 m | 0.28 | 87% |

The network stays in one piece. NON-CANON sketch.

## Two nacelles vs four + aft ring (2026-11-16)

`node_ring.py` produces `node_ring.json`, and `node_ring_picture.py` produces `node_ring.png`.

B is four nacelles plus a White-style hoop (x 52.6, R 4.4).

| Option | Worst gap | Gap covering 95% of the skin | Evenness | Rear nodes per quarter |
|---|---|---|---|---|
| A two nacelles | 5.0 m | 3.8 m | 0.27 | 30/7/22/8 |
| B four + ring | 4.3 m | 2.6 m | 0.26 | 21/19/21/20 |

NON-CANON.
