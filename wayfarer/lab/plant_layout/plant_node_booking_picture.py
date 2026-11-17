"""Picture for plant_node_booking.json. NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import json, os, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, 'plant_node_booking.json')))
N = np.array(json.load(open(os.path.join(HERE, '..', 'metric_nodes', 'nacelle_fit', 'node_coverage_fit.json')))['nodes'])
INK, MUTE, BG = '#0b0b0b', '#52514e', '#fcfcfb'
fig = plt.figure(figsize=(11, 7.4), dpi=150); fig.patch.set_facecolor(BG)
fig.text(.03, .955, 'Booking the nodes and their cabling out of the plant boxes', fontsize=14, weight='bold', color=INK)
fig.text(.03, .92, 'NON-CANON proposal for Sol. 16.5 t leaves the two boxes; the plant total stays 88 t. No node sits on a bay door.', fontsize=9.5, color=MUTE)
ax = fig.add_axes([.04, .42, .93, .45]); ax.set_facecolor(BG)
hull = np.array([[-.3, 0], [.2, 2.6], [1.2, 3.8], [3, 4.5], [34.3, 4.5], [39.3, 2.95], [39.3, 2.125], [46.3, 2.125], [53.3, 3.0]])
for s in (1, -1): ax.plot(hull[:, 0], s * hull[:, 1], color='#9aa0a6', lw=1)
ax.add_patch(Rectangle((18.25, 4.5), 13.8, .25, color='#d8dbe0')); ax.text(25.1, 4.95, 'bay doors: no nodes', ha='center', fontsize=8, color=MUTE)
for x0, L, lab in ((14, 3, 'fore box'), (32.3, 2, 'aft box')):
    ax.add_patch(Rectangle((x0, -2), L, 4, fc='#eef0f3', ec=MUTE)); ax.text(x0 + L / 2, 0, lab + '\n−8.25 t', ha='center', va='center', fontsize=8)
for s in (1, -1): ax.add_patch(Rectangle((39.5, s * 4.6 - .6), 14.8, 1.2, fc='none', ec='#2a78d6', lw=1))
ax.plot([53.9, 53.9], [-4.6, 4.6], color='#1baf7a', lw=2, alpha=.5)
cols = plt.cm.viridis(np.linspace(.05, .9, 8))
y_side = N[:, 1]   # side view: y up
for it, c in zip(d['items'][:8], cols):
    a, b = it['x_range']; m = (N[:, 0] >= a - .01) & (N[:, 0] <= b + .01)
for i, it in enumerate(d['items']):
    pass
x, y, z = N.T; r = np.hypot(y, z)
kind = np.where(x > 39.4, 2, np.where(x >= 34.3, 1, 0))
ax.scatter(x[kind == 0], y[kind == 0], s=14, c='#6250d6', zorder=3, label='hull nodes (bands)')
ax.scatter(x[kind == 1], y[kind == 1], s=14, c='#eb6834', zorder=3, label='cone ring')
ax.scatter(x[kind == 2], y[kind == 2], s=14, c='#2a78d6', zorder=3, label='on nacelles + ring (move with them)')
for b in (5, 10, 15, 20, 25, 30): ax.axvline(b, color='#e4e3df', lw=.8, zorder=0)
ax.legend(loc='lower left', fontsize=8, frameon=False, ncol=3, bbox_to_anchor=(0, -.02))
ax.set_xlim(-1, 56); ax.set_ylim(-6.2, 6.2); ax.set_aspect('equal'); ax.axis('off')
ax.text(-1, 5.6, 'side view (all nodes projected)', fontsize=8.5, color=MUTE)
t = fig.add_axes([.04, .04, .93, .33]); t.axis('off'); t.set_xlim(0, 1); t.set_ylim(0, 1)
hdr = ['booking item', 'nodes', 'node t', 'cabling t', 'total t', 'centre x, m']
xs = [0, .42, .52, .63, .75, .87]
for xx, h in zip(xs, hdr): t.text(xx, .97, h, fontsize=9, color=MUTE, ha='left' if xx == 0 else 'right' if xx < .87 else 'left', va='top')
yy = .88
for it in d['items']:
    nm = it['id'].replace('node_band_x', 'hull band x ').replace('_', '–', 1) if it['id'].startswith('node_band') else it['id'].replace('node_ring_cone', 'thrust-cone ring').replace('node_set_nacelle_', 'nacelle set ') + ('°' if 'nacelle' in it['id'] else '')
    vals = [nm, it['nodes'], f"{it['node_t']:.2f}", f"{it['trunk_t']:.2f}", f"{it['total_t']:.2f}", f"{it['cg_deployed'][0]:.1f}"]
    for xx, v in zip(xs, vals): t.text(xx, yy, str(v), fontsize=8.6, ha='left' if xx in (0, .87) else 'right', va='top')
    yy -= .067
t.text(0, yy - .01, f"Total {d['total_t']:.1f} t. Ship centre of mass moves {d['dry_cg_shift_m']['deployed'][0] * 100:.1f} cm aft (the decision estimated ~1 cm): G3 must check it.",
       fontsize=9, weight='bold', color='#c8432f', va='top')
fig.savefig(os.path.join(HERE, 'plant_node_booking.png'), facecolor=BG)
