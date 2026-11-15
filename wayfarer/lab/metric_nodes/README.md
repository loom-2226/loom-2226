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
