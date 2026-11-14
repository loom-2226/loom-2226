# Metric node faces: conflict map and proposed fixes (2026-11-15)

ALL bodies. ALL sponsors. 2026-2226.

NON-CANON proposal by Claude for kT. It places the 208 node faces (13 rings x 16, the PR #184 baseline, `wayfarer_v05_geometry.json`) against the hull and exterior hardware.

- `node_map.py` produces `node_conflict_map.png`.
- `node_data.py` produces `nodes_before_after.json`, which the review viewer uses for its Metric nodes: Off / Now / Fixed overlay.

**Now:**

- 80 are on the torch chain.
- 20 are under stowed strakes, over the longerons.
- 12 are on the bay-door leaves.
- 8 are on or next to hardware.
- 16 are on the bow shoulder.
- 72 are clear.

**Fixed (proposal):**

- 80 move into the four hot-fin root trusses (20 per fin), inside the existing outline, so nothing new is added outside the hull.
- 20 move into the strake root fittings.
- The 4 bay rings are re-spaced to clear the door leaves (48 nodes).
- 16 move to the bow shoulder ring frame at x 2.35.
- For 7, the hardware moves instead of the node.
- 37 are unchanged.

No mass is booked and nothing is placed in canon. The placement decision is kT's, and is then executed against PR #184.
